from bot_common.utils.utils import catch_exception
from bot_common.utils.logging_conf import logger
from pydantic import BaseModel
import mysql.connector


class DbConfig(BaseModel):
    db_user: str
    db_password: str
    db_host: str
    db_port: int
    db_name: str


@catch_exception
def db_connect(conf: DbConfig, dict_query=False):
    db = mysql.connector.connect(
        host=conf.db_host,
        port=conf.db_port,
        user=conf.db_user,
        password=conf.db_password,
        database=conf.db_name,
        charset='utf8')
    cursor = db.cursor(dictionary=dict_query)
    return db, cursor


@catch_exception
def create_table_if_not_exists(db, cursor, tab_name, headers):
    show_table_query = f"SHOW TABLES LIKE '{tab_name}';"
    cursor.execute(show_table_query)
    matched_tables = cursor.fetchall()

    if len(matched_tables) == 0:
        unique_index_flag = '<U_IDX>'
        index_flag = '<IDX>'
        tab_field_ls = ["pk BIGINT PRIMARY KEY AUTO_INCREMENT"]
        u_idx_field_ls = []
        idx_field_ls = []
        for h, dtype in headers.items():
            if unique_index_flag in dtype:
                u_idx_field_ls.append(h)
                dtype = dtype.replace(unique_index_flag, '').strip()
            if index_flag in dtype:
                idx_field_ls.append(f"INDEX ({h})")
                dtype = dtype.replace(index_flag, '').strip()
            tab_field_ls.append(f"{h} {dtype}")

        u_idx_fields = 'UNIQUE INDEX (' + ', '.join(u_idx_field_ls) + ')' if u_idx_field_ls else ''
        idx_fields = ', '.join(idx_field_ls)
        tab_field_ls.append(u_idx_fields)
        tab_field_ls.append(idx_fields)
        tab_field_ls = [el for el in tab_field_ls if el]
        create_table_query = f"CREATE TABLE IF NOT EXISTS {tab_name} ({', '.join(tab_field_ls)});"
        cursor.execute(create_table_query)
        db.commit()
        logger.info(f'created table: {tab_name}')
    return


@catch_exception
def insert_into_table(db, cursor, data_dict, tab_name):
    # data_dict = {k: v for k, v in data_dict.items() if v != ''}
    tab_field_ls = data_dict.keys()
    tab_value_ls = [f"'{val}'" for val in data_dict.values()]
    # compose query
    insert_into_table_query = f"INSERT INTO {tab_name} ({', '.join(tab_field_ls)}) VALUES ({', '.join(tab_value_ls)});"
    cursor.execute(insert_into_table_query)
    db.commit()
    return


@catch_exception
def update_table(db, cursor, data_dict, tab_name):
    # data_dict = {k: v for k, v in data_dict.items() if v != ''}
    # update the record
    overwrite_value_ls = [f"{h}='{val}'" for h, val in data_dict.items()]
    tab_field_ls = data_dict.keys()
    tab_value_ls = [f"'{val}'" for val in data_dict.values()]
    # compose query
    update_table_query = f"INSERT INTO {tab_name} ({', '.join(tab_field_ls)}) VALUES ({', '.join(tab_value_ls)}) ON DUPLICATE KEY UPDATE {', '.join(overwrite_value_ls)};"
    cursor.execute(update_table_query)
    db.commit()
    return

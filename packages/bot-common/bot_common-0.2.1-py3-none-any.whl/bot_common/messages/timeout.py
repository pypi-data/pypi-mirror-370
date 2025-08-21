from bot_common.messages.timeout_model import TimeoutObj
from bot_common.utils.db_utils import DbConfig, create_table_if_not_exists, db_connect, update_table
from bot_common.utils.utils import catch_exception, get_time_now, clean_string
from bot_common.utils.logging_conf import logger
from bot_common.lib_conf import table_name_timeout

mysql_headers = {k: v.field_info.description for k, v in TimeoutObj.__fields__.items()}

int_fields = ['timeout_sec']
clean_str_fields = ['company_contact', 'user_contact']


# TimeoutMessageManager class is only used by the message.py classes

class TimeoutMessageManager:
    def __init__(self, db, cursor, new_timeout: TimeoutObj = None):
        self.db, self.cursor = db, cursor
        self.tab_name = table_name_timeout
        self.new_timeout = new_timeout
        create_table_if_not_exists(self.db, self.cursor, self.tab_name, mysql_headers)

    @catch_exception
    def get(self, required_elapsed_seconds_default):
        get_timeout_query = f"SELECT * FROM {self.tab_name} WHERE company_contact = '{self.new_timeout.company_contact}' AND user_contact = '{self.new_timeout.user_contact}';"
        self.cursor.execute(get_timeout_query)
        new_timeout_ls = self.cursor.fetchall()
        if new_timeout_ls:
            return new_timeout_ls[0].get('timeout_sec')
        return required_elapsed_seconds_default

    @catch_exception
    def delete(self):
        delete_timeout_query = f"DELETE FROM {self.tab_name} WHERE company_contact = '{self.new_timeout.company_contact}' AND user_contact = '{self.new_timeout.user_contact}';"
        self.cursor.execute(delete_timeout_query)
        self.db.commit()

    @catch_exception
    def delete_older_mins(self, delete_timeout_before_tmp):
        delete_expired_query = f"DELETE FROM {self.tab_name} WHERE timestamp < '{delete_timeout_before_tmp}';"
        self.cursor.execute(delete_expired_query)
        self.db.commit()


@catch_exception
def set_timeout(new_timeout: TimeoutObj, db_config: DbConfig):
    db, cursor = db_connect(db_config)
    tab_name = table_name_timeout
    create_table_if_not_exists(db, cursor, tab_name, mysql_headers)

    data = new_timeout.__dict__.copy()
    data['timestamp'] = get_time_now()
    for field in int_fields:
        data[field] = int(data[field])
    for field in clean_str_fields:
        data[field] = clean_string(data[field])

    update_table(db, cursor, data, tab_name)
    logger.info(f'set new_timeout {data} success')
    db.close()

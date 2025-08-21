from bot_common.companies.company_model import ConfigObject, FlowObject, ResponsesObject, ConfigPaths
from bot_common.utils.utils import catch_exception, get_time_now
from bot_common.utils.db_utils import DbConfig, db_connect, insert_into_table, create_table_if_not_exists, update_table
from bot_common.utils.logging_conf import logger
import pandas as pd
import yaml
import json
from bot_common.lib_conf import table_name_company_configurations, flow_csv_subflow_identifier, \
    flow_csv_subflow_delimiter, flow_csv_multiple_response_ids_join, max_subflow_iterations, \
    table_prefix_conversational_flow, table_prefix_responses

flow_mysql_headers = {k: v.field_info.description for k, v in FlowObject.__fields__.items()}
responses_mysql_headers = {k: v.field_info.description for k, v in ResponsesObject.__fields__.items()}


# ALLOWED UP TO max_subflow_iterations LEVELS INDENTED SUBFLOWS
class FlowCsvParser:
    def __init__(self, csv_path):
        self.subflow_identifier = flow_csv_subflow_identifier.strip().lower()
        self.subflow_delimiter = flow_csv_subflow_delimiter.strip().lower()
        self.responses_separator = flow_csv_multiple_response_ids_join.strip().lower()
        self.df = pd.read_csv(csv_path, index_col=False, delimiter=';', encoding='latin-1', header=0)
        self.subflows_df = None
        self.current_row = None
        self.current_required_subflow_dict = {}
        self.current_subflow_name = ''
        self.current_in_ctx = ''
        self.other_iteration_needed = True
        self.n_iterations = 0

    @catch_exception
    def get_current_subflow_dict(self):
        try:
            self.current_required_subflow_dict = json.loads(self.current_row['out_ctx'])
        except json.decoder.JSONDecodeError:
            self.current_required_subflow_dict = {}
        except TypeError:
            self.current_required_subflow_dict = {}
        self.current_required_subflow_dict = dict(
            (k.strip().lower(), v) for k, v in self.current_required_subflow_dict.items())

    @catch_exception
    def process_current_subflow_slice(self, r):
        out_ctx = str(r['out_ctx']).strip().lower()
        r['in_ctx'] = str(r['in_ctx']).strip().lower().replace(self.current_subflow_name, self.current_in_ctx)

        if out_ctx in self.current_required_subflow_dict.keys():
            out_ls = self.current_required_subflow_dict.get(out_ctx)
            r['out_ctx'] = out_ls[0].strip().lower()
            if len(out_ls) > 1 and out_ls[1].strip():
                rid = r['response_id'] if pd.notna(r['response_id']) else ''
                r['response_id'] = rid + self.responses_separator + out_ls[1].strip()
        else:
            r['out_ctx'] = out_ctx.replace(self.current_subflow_name, self.current_in_ctx)
        return r

    @catch_exception
    def attach_subflows(self, df):
        drop_idx_all = []
        for idx, row in df.iterrows():
            self.current_row = row
            self.get_current_subflow_dict()

            if self.current_required_subflow_dict:
                idx_max = max(list(df.index))
                self.current_in_ctx = self.current_row['in_ctx'].strip().lower()
                self.current_subflow_name = self.subflow_identifier + self.subflow_delimiter + self.current_required_subflow_dict.get(self.subflow_identifier)

                subflow_df_tmp_bool = self.subflows_df['in_ctx'].apply(lambda x: str(x).strip().lower().startswith(self.current_subflow_name))
                subflow_df_tmp = self.subflows_df[subflow_df_tmp_bool]
                subflow_df_tmp_out = subflow_df_tmp.copy()
                subflow_df_tmp_out['in_ctx'] = subflow_df_tmp['in_ctx'].apply(lambda x: str(x).strip().lower().replace(self.current_subflow_name, self.current_in_ctx))
                subflow_df_tmp_out = subflow_df_tmp_out.apply(lambda r: self.process_current_subflow_slice(r), axis=1)
                drop_idx_all.append(idx)
                idx_new = list(range(idx_max + 1, idx_max + len(subflow_df_tmp_out) + 1))
                subflow_df_tmp_out.index = idx_new
                df = pd.concat([df.loc[:idx], subflow_df_tmp_out, df.loc[idx:]])

        df = df.drop(drop_idx_all, errors="ignore")
        return df.reset_index(drop=True)

    @catch_exception
    def check_other_iteration_needed(self):
        required_subflow = False
        for idx, row in self.subflows_df.iterrows():
            self.current_row = row
            self.get_current_subflow_dict()
            if self.current_required_subflow_dict:
                required_subflow = True
                break
        self.other_iteration_needed = False if not required_subflow else True
        self.n_iterations = self.n_iterations + 1 if required_subflow else self.n_iterations

    @catch_exception
    def get_subflows_df(self):
        subflow_bool = self.df['in_ctx'].apply(lambda x: str(x).strip().lower().startswith(self.subflow_identifier))
        self.subflows_df = self.df[subflow_bool]
        self.df = self.df.drop(list(self.subflows_df.index), errors="ignore").reset_index(drop=True)

        while self.other_iteration_needed:
            self.subflows_df = self.attach_subflows(self.subflows_df)
            self.check_other_iteration_needed()

            if self.n_iterations > max_subflow_iterations:
                raise Exception('Invalid fsa: infinite loop occurred due to nested subflows')

    @catch_exception
    def to_pd(self):
        non_comment_rows = self.df.iloc[:, 0].apply(lambda x: not str(x).strip().startswith('#'))
        self.df = self.df[non_comment_rows]
        self.df = self.df.dropna(axis=0, how='all')
        self.get_subflows_df()
        self.df = self.attach_subflows(self.df)
        return self.df


@catch_exception
def csv_to_pd(csv_path):
    df = pd.read_csv(csv_path, index_col=False, delimiter=';', encoding='latin-1', header=0)
    non_comment_rows = df.iloc[:, 0].apply(lambda x: not str(x).strip().startswith('#'))
    non_comment_idx = non_comment_rows[non_comment_rows].index
    df_clean = df.loc[non_comment_idx].reset_index(drop=True)
    return df_clean


@catch_exception
def parse_yaml(yaml_path):
    with open(yaml_path, 'r') as stream:
        try:
            parsed_yaml = yaml.safe_load(stream)
            return parsed_yaml
        except yaml.YAMLError as e:
            raise Exception(f"Failed to parse config file yaml {yaml_path}: {str(e)}")


class ConfigurationSetup:
    def __init__(self, company: str, db_config: DbConfig, paths: ConfigPaths):
        self.conversational_flow_table_name = table_prefix_conversational_flow + company
        self.responses_table_name = table_prefix_responses + company
        self.company_conf_table_name = table_name_company_configurations
        self.paths = paths
        self.file_path = ''
        self.tab_name = ''
        self.headers = None
        self.df = None
        self.new_pk = 1
        self.db, self.cursor = db_connect(db_config)

    @catch_exception
    def write_rows(self):
        for cnt, row in self.df.iterrows():
            row = row.dropna()
            row_data_dict = dict(zip(list(row.index), list(row.values)))
            insert_into_table(self.db, self.cursor, row_data_dict, self.tab_name)

    @catch_exception
    def drop_table_if_exists(self):
        drop_table_query = f"DROP TABLE IF EXISTS {self.tab_name};"
        self.cursor.execute(drop_table_query)
        self.db.commit()

    @catch_exception
    def setup_csv_table(self, flow=False):
        logger.info(f'setup table {self.tab_name}')
        self.drop_table_if_exists()
        create_table_if_not_exists(self.db, self.cursor, self.tab_name, self.headers)
        self.df = FlowCsvParser(self.file_path).to_pd() if flow else csv_to_pd(self.file_path)
        self.df = self.df.applymap(lambda x: x.replace("\\", "\\\\").replace("'", "\\'") if isinstance(x, str) else x)
        self.write_rows()

    @catch_exception
    def get_new_pk(self):
        get_pks_query = f"SELECT pk FROM {self.tab_name}"
        self.cursor.execute(get_pks_query)
        pks = self.cursor.fetchall()
        self.new_pk = max([el[0] for el in pks]) + 1 if pks else 1

    @catch_exception
    def setup_yaml_config(self):
        logger.info(f'setup table {self.tab_name}')
        create_table_if_not_exists(self.db, self.cursor, self.tab_name, self.headers)
        data_dict_var = parse_yaml(self.file_path).get('Variables')
        data_dict = {}
        field_other = {}
        for k, v in data_dict_var.items():
            v = json.dumps(v) if (isinstance(v, list) or isinstance(v, dict)) else v
            v = v.replace("\\", "\\\\").replace("'", "\\'") if isinstance(v, str) else v
            if k in self.headers.keys():
                data_dict[k] = v
            else:
                field_other[k] = v
        self.get_new_pk()
        data_dict['pk'] = self.new_pk
        data_dict['is_active'] = 1
        data_dict['is_active_switch_tmp'] = get_time_now()
        data_dict['other'] = json.dumps(field_other)
        update_table(self.db, self.cursor, data_dict, self.tab_name)

    # --- MAIN ---

    @catch_exception
    def setup(self):
        self.file_path = self.paths.flow_path
        self.tab_name = self.conversational_flow_table_name
        self.headers = flow_mysql_headers
        self.setup_csv_table(flow=True)

        self.file_path = self.paths.responses_path
        self.tab_name = self.responses_table_name
        self.headers = responses_mysql_headers
        self.setup_csv_table(flow=False)

        self.file_path = self.paths.config_file_path
        self.tab_name = self.company_conf_table_name
        self.headers = {k: v.field_info.description for k, v in ConfigObject.__fields__.items()}
        self.setup_yaml_config()
        self.db.close()

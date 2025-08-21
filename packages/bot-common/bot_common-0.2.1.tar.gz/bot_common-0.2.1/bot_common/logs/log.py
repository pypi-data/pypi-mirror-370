from bot_common.utils.utils import catch_exception, get_time_now, clean_string, str_to_datetime, datetime_to_str
from bot_common.utils.db_utils import DbConfig, create_table_if_not_exists, db_connect, insert_into_table
from bot_common.logs.log_model import LogObject
from bot_common.utils.logging_conf import logger
from bot_common.lib_conf import table_prefix_logs, table_prefix_logs_end_conversation
from datetime import timedelta
import json

# - In "other_logs" we store some indicators about the performed
#   conversational flow path.
# - In "extracted_data" we store the main features extracted
#   during the conversation.

mysql_headers = {k: v.field_info.description for k, v in LogObject.__fields__.items()}

str_special_char_fields = []
float_fields = ['intent_confidence']
dump_fields = ['other_logs', 'extracted_data']
clean_str_fields = ['bot_message', 'current_user_utterance', 'log_transcript']
int_fields = ['conv_duration_sec', 'fallback', 'handover', 'handover_incomprehension',
              'conv_step_num', 'closed', 'expired', 'redirect', 'closed_formality',
              'hangup', 'unclosed_success', 'solicit', 'platform_exception']


class Log(LogObject):
    @catch_exception
    def extract_data(self):
        data = self.__dict__.copy()
        data['timestamp'] = get_time_now()
        for field in dump_fields:
            data[field] = clean_string(json.dumps(data[field])).replace('\\', '\\\\')
        for field in str_special_char_fields:
            data[field] = data[field].replace("\\", "\\\\").replace("'", "\\'")
        for field in int_fields:
            data[field] = int(data[field])
        for field in clean_str_fields:
            data[field] = clean_string(data[field])
        for field in float_fields:
            data[field] = round(float(data[field]), 2)
        return data

    @catch_exception
    def write(self, db_config: DbConfig, end_conversation=False):
        prefix = table_prefix_logs_end_conversation if end_conversation else table_prefix_logs
        tab_name = prefix + self.company
        logs_db, logs_cursor = db_connect(db_config)
        create_table_if_not_exists(logs_db, logs_cursor, tab_name, mysql_headers)
        data_dict = self.extract_data()
        try:
            insert_into_table(logs_db, logs_cursor, data_dict, tab_name)
            logger.info(f'writing logs success')
        except Exception as err:
            try:
                time_new = datetime_to_str(str_to_datetime(get_time_now()) + timedelta(seconds=1))
                data_dict['timestamp'] = time_new
                insert_into_table(logs_db, logs_cursor, data_dict, tab_name)
                logger.info(f'writing logs success (at second try) - {err}')
            except Exception as e:
                raise Exception(f'Exception in writing logs: {e}')
        finally:
            logs_db.close()

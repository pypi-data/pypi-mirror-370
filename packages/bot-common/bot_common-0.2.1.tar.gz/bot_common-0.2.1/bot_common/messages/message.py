from bot_common.utils.db_utils import DbConfig, create_table_if_not_exists, db_connect, update_table, insert_into_table
from bot_common.utils.utils import catch_exception, get_time_now, clean_string, str_to_datetime
from bot_common.messages.message_model import MessageDbObj, NewMessageDbObj, DmMessageLightObj
from bot_common.messages.timeout_model import TimeoutObj
from bot_common.messages.timeout import TimeoutMessageManager
from bot_common.utils.logging_conf import logger
from bot_common.lib_conf import void_response, table_name_messages
from datetime import timedelta
from typing import List
import itertools

mysql_headers = {k: v.field_info.description for k, v in MessageDbObj.__fields__.items()}

int_fields = []
clean_str_fields = ['company_contact', 'user_contact', 'user_message']


class NewMessages:
    def __init__(self, db_config: DbConfig):
        self.db, self.cursor = db_connect(db_config, dict_query=True)
        self.tab_name = table_name_messages
        self.current_tmp = str_to_datetime(get_time_now())
        self.required_elapsed_seconds_default = 0
        self.single_user_parsed_messages = []
        self.single_user_messages = []
        self.company_user_key = ()
        self.new_messages_dict = {}
        create_table_if_not_exists(self.db, self.cursor, self.tab_name, mysql_headers)

    @catch_exception
    def set_processed_and_parse(self, message_dict):
        message_dict['processed'] = 1
        message_obj = MessageDbObj.parse_obj(message_dict)
        # set processed=1 for the extracted messages
        update_table(self.db, self.cursor, message_dict, self.tab_name)
        return message_obj

    @catch_exception
    def check_single_user_messages(self):
        user_last_received_tmp = str_to_datetime(self.single_user_messages[0].get('timestamp'))
        # time_elapsed_sec is the time elapsed from the given user's last message
        time_elapsed_sec = (self.current_tmp - user_last_received_tmp).total_seconds()
        # if it is passed a given amount of time since the user's last message,
        # we add the user messages between the processable ones, otherwise we wait for it
        to = TimeoutObj(company_contact=self.company_user_key[0], user_contact=self.company_user_key[1])
        required_elapsed_seconds = TimeoutMessageManager(self.db, self.cursor, to).get(self.required_elapsed_seconds_default)

        logger.info(f'required_elapsed_seconds: {required_elapsed_seconds}')
        if time_elapsed_sec > required_elapsed_seconds:
            TimeoutMessageManager(self.db, self.cursor, to).delete()
            self.single_user_parsed_messages = [self.set_processed_and_parse(m) for m in self.single_user_messages]
            self.new_messages_dict[self.company_user_key] = self.single_user_parsed_messages

    @catch_exception
    def get(self, required_elapsed_seconds_default: int):
        self.required_elapsed_seconds_default = required_elapsed_seconds_default
        # query for the unprocessed messages:
        # ORDER BY company, user_contact --> in order to allow the grouping by user_contact for different companies
        # ORDER BY timestamp DESC (per each user_contact) --> in order to have the last received message as first record
        get_new_messages_query = f"SELECT * FROM {self.tab_name} WHERE processed = '0' ORDER BY company_contact, user_contact, timestamp DESC;"
        self.cursor.execute(get_new_messages_query)
        new_messages_ls = self.cursor.fetchall()
        # group by different user_contacts
        grouper = itertools.groupby(new_messages_ls, key=lambda x: (x.get('company_contact'), x.get('user_contact')))
        # cu_key = (company_contact, user_contact) tuple
        for cu_key, user_messages in grouper:
            logger.info(f'get_new_messages - (company_contact, user_contact): {cu_key}')
            self.company_user_key = cu_key
            self.single_user_messages = list(user_messages)
            self.check_single_user_messages()
        self.db.close()
        return self.new_messages_dict

    @catch_exception
    def set(self, new_message: NewMessageDbObj):
        data = new_message.__dict__.copy()
        data['timestamp'] = get_time_now()
        data['processed'] = 0
        del data['token']
        for field in int_fields:
            data[field] = int(data[field])
        for field in clean_str_fields:
            data[field] = clean_string(data[field])

        void_message_content = not bool(data.get('user_message')) and not bool(data.get('start_context'))
        data['user_message'] = list(void_response.values())[0] if void_message_content else data.get('user_message')
        insert_into_table(self.db, self.cursor, data, self.tab_name)
        logger.info(f'set_new_message {data} success')
        self.db.close()


# --------------- DELETE MESSAGES CLASS

class DeleteMessages:
    def __init__(self, db_config: DbConfig):
        self.db, self.cursor = db_connect(db_config)
        self.tab_name = table_name_messages
        self.company_contact = ''
        self.user_contact = ''
        self.current_tmp = str_to_datetime(get_time_now())
        create_table_if_not_exists(self.db, self.cursor, self.tab_name, mysql_headers)

    @catch_exception
    def expired(self, expired_ls: List[DmMessageLightObj]):
        for exp in expired_ls:
            self.company_contact = exp.company_contact
            self.user_contact = exp.session_id
            delete_expired_query = f"DELETE FROM {self.tab_name} WHERE company_contact = '{self.company_contact}' AND user_contact = '{self.user_contact}';"
            self.cursor.execute(delete_expired_query)
            self.db.commit()
            to = TimeoutObj(company_contact=self.company_contact, user_contact=self.user_contact)
            TimeoutMessageManager(self.db, self.cursor, to).delete()
            logger.info(f'deleted expired messages/timeouts ({self.company_contact}, {self.user_contact}) success')
        self.db.close()

    @catch_exception
    def older_mins(self, delete_older_messages_mins):
        timedelta_mins = timedelta(minutes=delete_older_messages_mins)
        delete_messages_before_tmp = self.current_tmp - timedelta_mins
        delete_expired_query = f"DELETE FROM {self.tab_name} WHERE timestamp < '{delete_messages_before_tmp}';"
        self.cursor.execute(delete_expired_query)
        self.db.commit()
        TimeoutMessageManager(self.db, self.cursor).delete_older_mins(delete_messages_before_tmp)
        logger.info('deleted older messages/timeouts')
        self.db.close()

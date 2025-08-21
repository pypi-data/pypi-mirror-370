from pydantic import BaseModel, Field

# '<U_IDX>' flags all the fields that cannot be simultaneously duplicated,
# '<IDX>' flags all the fields that are used in the queries


class SessionObject(BaseModel):
    id_session: str =                       Field(description="VARCHAR(250) NOT NULL <U_IDX>")
    is_closed: int =                        Field(default=0, description="TINYINT NOT NULL <IDX>")
    company: str =                          Field(description="TEXT NOT NULL")
    company_contact: str =                  Field(description="TEXT NOT NULL")
    start_conversation_timestamp: str =     Field(description="VARCHAR(50)")
    unique_id: str =                        Field(default="", description="VARCHAR(30) NOT NULL <IDX>")
    user_key: str =                         Field(default="", description="TEXT")
    start_context: str =                    Field(default="", description="TEXT")
    current_context: str =                  Field(default="", description="TEXT")
    state: str =                            Field(default="", description="TEXT")
    timestamp: str =                        Field(default="", description="VARCHAR(50)")
    timeout_sec: int =                      Field(default=0, description="TINYINT")
    bot_message_contains_buttons: bool =    Field(default=False, description="TINYINT")
    unclosed_success: bool =                Field(default=False, description="TINYINT")
    solicited_times: int =                  Field(default=0, description="TINYINT")
    message_id: str =                       Field(default="", description="TEXT")
    bot_message: str =                      Field(default="", description="TEXT")
    other_logs: dict =                      Field(default={}, description="TEXT")
    extracted_data: dict =                  Field(default={}, description="TEXT")
    cache: dict =                           Field(default={}, description="TEXT")
    entities: dict =                        Field(default={}, description="TEXT")

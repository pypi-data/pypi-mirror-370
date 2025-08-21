from pydantic import BaseModel, Field

# '<U_IDX>' flags all the fields that cannot be simultaneously duplicated,
# '<IDX>' flags all the fields that are used in the queries


class LogObject(BaseModel):
    timestamp: str =                    Field(default="", description="DATETIME(6) NOT NULL <U_IDX>")
    id_session: str =                   Field(description="VARCHAR(250) NOT NULL <U_IDX>")
    company: str =                      Field(description="VARCHAR(250) NOT NULL <IDX>")
    company_contact: str =              Field(description="VARCHAR(250) NOT NULL <IDX>")
    user_key: str =                     Field(default="", description="VARCHAR(250) <IDX>")
    unique_id: str =                    Field(default="", description="VARCHAR(30) NOT NULL <IDX>")
    start_context: str =                Field(default="", description="VARCHAR(250) <IDX>")
    current_context: str =              Field(default="", description="TEXT")
    conversation_platform: str =        Field(default="", description="VARCHAR(50)")
    start_conversation_timestamp: str = Field(default="", description="DATETIME(6) NOT NULL <IDX>")
    conv_duration_sec: int =            Field(default=0, description="INT")
    detected_intent: str =              Field(default="", description="TEXT")
    intent_confidence: float =          Field(default=0, description="DOUBLE(3,2)")
    conv_step_num: int =                Field(default=0, description="TINYINT <IDX>")
    closed_formality: bool =            Field(default=False, description="TINYINT <IDX>")
    unclosed_success: bool =            Field(default=False, description="TINYINT <IDX>")
    platform_exception: bool =          Field(default=False, description="TINYINT <IDX>")
    solicit: bool =                     Field(default=False, description="TINYINT <IDX>")
    fallback: bool =                    Field(default=False, description="TINYINT <IDX>")
    handover: bool =                    Field(default=False, description="TINYINT <IDX>")
    handover_incomprehension: bool =    Field(default=False, description="TINYINT <IDX>")
    closed: bool =                      Field(default=False, description="TINYINT <IDX>")
    hangup: bool =                      Field(default=False, description="TINYINT <IDX>")
    redirect: bool =                    Field(default=False, description="TINYINT <IDX>")
    expired: bool =                     Field(default=False, description="TINYINT <IDX>")
    state: str =                        Field(default="", description="VARCHAR(250)")
    message_id: str =                   Field(default="", description="TEXT")
    bot_message: str =                  Field(default="", description="TEXT")
    current_user_utterance: str =       Field(default="", description="TEXT")
    log_transcript: str =               Field(default="", description="TEXT")
    other_logs: dict =                  Field(default={}, description="TEXT")
    extracted_data: dict =              Field(default={}, description="TEXT")

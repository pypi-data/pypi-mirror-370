from pathlib import Path
from pydantic import BaseModel, Field

# '<U_IDX>' flags all the fields that cannot be simultaneously duplicated,
# '<IDX>' flags all the fields that are used in the queries


class ConfigPaths(BaseModel):
    config_file_path: Path
    flow_path: Path
    responses_path: Path


class ConfigObject(BaseModel):
    company: str =                                      Field(description="VARCHAR(180) NOT NULL <U_IDX> <IDX>")
    is_active: int =                                    Field(description="TINYINT NOT NULL <IDX>")
    is_active_switch_tmp: str =                         Field(description="VARCHAR(50)")
    company_port: int =                                 Field(description="INT NOT NULL")
    company_contact: list =                             Field(description="VARCHAR(500) NOT NULL <IDX>")
    used_conversation_platform: str =                   Field(description="TEXT")
    redirect_contacts: list =                           Field(description="TEXT")
    nlu_port: int =                                     Field(description="INT NOT NULL")
    sessions_expiration_mins: dict =                    Field(description="TEXT")
    unexisting_session_start_ctx: str =                 Field(description="TEXT")
    preferred_nlu_extractor: str =                      Field(description="TEXT")
    default_timeout_sec: int =                          Field(description="INT")
    fallback_counter_max: int =                         Field(description="INT")
    technical_issue_response_id: str =                  Field(description="TEXT")
    session_expired_response_id_by_start_ctx: dict =    Field(default={}, description="TEXT")
    handover_incomprehension_response_id: str =         Field(description="TEXT")
    end_conversation_formalities_intents: list =        Field(default=[], description="TEXT")
    preprocessing_messages_contexts: dict =             Field(default={}, description="TEXT")
    preprocessing_messages_bodies: dict =               Field(default={}, description="TEXT")
    hints_mapping: dict =                               Field(default={}, description="TEXT")
    solicit_after_mins: dict =                          Field(default={}, description="TEXT")
    solicit_action_ls: dict =                           Field(default={}, description="TEXT")
    success_other_logs: dict =                          Field(default={}, description="TEXT")
    other: dict =                                       Field(default={}, description="TEXT")


class FlowObject(BaseModel):
    in_ctx: str =               Field(description="VARCHAR(180) NOT NULL <U_IDX> <IDX>")
    intent: str =               Field(description="VARCHAR(180) <U_IDX>")
    entity: str =               Field(description="VARCHAR(180) <U_IDX>")
    action: str =               Field(description="TEXT")
    action_out: str =           Field(description="VARCHAR(180) <U_IDX>")
    out_ctx: str =              Field(description="TEXT NOT NULL")
    response_id: str =          Field(description="TEXT NOT NULL")
    response_id_fallback: str = Field(description="TEXT")
    hints: str =                Field(description="TEXT")
    timeout_sec: int =          Field(description="INT")
    call_reason: str =          Field(description="TEXT")


class ResponsesObject(BaseModel):
    id: str =       Field(description="VARCHAR(180) NOT NULL <U_IDX> <IDX>")
    body1: str =    Field(description="TEXT")
    body2: str =    Field(description="TEXT")
    body3: str =    Field(description="TEXT")
    body4: str =    Field(description="TEXT")
    body5: str =    Field(description="TEXT")

from pydantic import BaseModel, Field

# '<U_IDX>' flags all the fields that cannot be simultaneously duplicated,
# '<IDX>' flags all the fields that are used in the queries


class MessageDbObj(BaseModel):
    company_contact: str =  Field(description="VARCHAR(250) NOT NULL <U_IDX>")
    user_contact: str =     Field(description="VARCHAR(250) NOT NULL <U_IDX>")
    timestamp: str =        Field(description="VARCHAR(50) NOT NULL <U_IDX>")
    processed: int =        Field(description="TINYINT NOT NULL <IDX>")
    user_message: str =     Field(description="TEXT")
    start_context: str =    Field(description="TEXT")
    user_key: str =         Field(description="TEXT")


class DmMessageLightObj(BaseModel):
    session_id: str
    company_contact: str


class NewMessageDbObj(BaseModel):
    company_contact: str
    user_contact: str
    user_key: str = ''
    user_message: str = ''
    start_context: str = ''
    token: str = ''

from pydantic import BaseModel, Field

# '<U_IDX>' flags all the fields that cannot be simultaneously duplicated,
# '<IDX>' flags all the fields that are used in the queries


class TimeoutObj(BaseModel):
    company_contact: str =  Field(description="VARCHAR(250) NOT NULL <U_IDX>")
    user_contact: str =     Field(description="VARCHAR(250) NOT NULL <U_IDX>")
    timestamp: str =        Field(default="", description="VARCHAR(50)")
    timeout_sec: int =      Field(default=0, description="INT")

from pydantic import BaseModel, Field

# '<U_IDX>' flags all the fields that cannot be simultaneously duplicated,
# '<IDX>' flags all the fields that are used in the queries


class ExceptionObj(BaseModel):
    timestamp: str =        Field(default='', description="DATETIME(6) NOT NULL <IDX>")
    state: str =            Field(default='', description="TEXT")
    error_message: str =    Field(default='', description="TEXT")

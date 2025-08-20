from pydantic import BaseModel

class SingularBaseModel(BaseModel):
    class Config:
        populate_by_name = True

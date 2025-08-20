from pydantic import BaseModel, ConfigDict

class SingularBaseModel(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
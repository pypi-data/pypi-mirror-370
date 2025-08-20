from pydantic import Field
from ..base import SingularBaseModel
from typing import List, Literal, Optional
from datetime import datetime

class InternalError(SingularBaseModel):
    context: List[Literal["https://w3id.org/dspace/2025/1/context.jsonld"]] = Field(alias="@context")
    type: Literal["InternalError"] = Field(alias="@type")
    code: Optional[str] = None
    reason: Optional[List] = None

class Asset(SingularBaseModel):
    id: str
    name: str
    offer_id: Optional[List[str]]= None
    description: Optional[str] = None
    organization: Optional[str] = None
    tags: Optional[List[str]] = None
    created: Optional[datetime] = None
    modified: Optional[datetime] = None
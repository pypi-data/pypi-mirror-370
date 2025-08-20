from pydantic import Field
from ...base import SingularBaseModel
from typing import List, Literal, Optional
from .low_level import Catalog, Dataset, DataService

class CatalogRequestMessage(SingularBaseModel):
    context: List[Literal["https://w3id.org/dspace/2025/1/context.jsonld"]] = Field(alias="@context")
    type: Literal["CatalogRequestMessage"]= Field(alias="@type")
    filter: Optional[List] = None

class DatasetRequestMessage(SingularBaseModel):
    context: List[Literal["https://w3id.org/dspace/2025/1/context.jsonld"]] = Field(alias="@context")
    type: Literal["DatasetRequestMessage"]= Field(alias="@type")
    dataset: str

class RootCatalog(SingularBaseModel):
    id: str = Field(alias="@id")
    context: List[Literal["https://w3id.org/dspace/2025/1/context.jsonld"]] = Field(alias="@context")
    type: str = Field(alias="@type")
    participantId: str
    catalog: Optional[List[Catalog]] = None
    dataset: Optional[List[Dataset]] = None
    service: Optional[List[DataService]] = None

class CatalogError(SingularBaseModel):
    context: List[Literal["https://w3id.org/dspace/2025/1/context.jsonld"]] = Field(alias="@context")
    type: Literal["CatalogError"] = Field(alias="@type")
    code: Optional[str] = None
    reason: Optional[List] = None
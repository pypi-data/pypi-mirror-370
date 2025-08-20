from pydantic import Field
from ..base import SingularBaseModel
from typing import List, Literal, Optional
from .low_level import Catalog, Dataset, DataService

class CatalogRequestMessage(SingularBaseModel):
    context: List[Literal["https://w3id.org/dspace/2025/1/context.jsonld"]] = Field(alias="@context")
    type: Literal["CatalogRequestMessage"]= Field(alias="@type")
    filter: Optional[List]

class DatasetRequestMessage(SingularBaseModel):
    context: List[Literal["https://w3id.org/dspace/2025/1/context.jsonld"]] = Field(alias="@context")
    type: Literal["DatasetRequestMessage"]= Field(alias="@type")
    dataset: str

class RootCatalog(SingularBaseModel):
    id: List[str] = Field(alias="@id")
    context: List[Literal["https://w3id.org/dspace/2025/1/context.jsonld"]] = Field(alias="@context")
    type: str = Field(alias="@type")
    participantId: str
    catalog: Optional[List[Catalog]]
    dataset: Optional[List[Dataset]]
    service: Optional[List[DataService]]

class CatalogError(SingularBaseModel):
    context: List[Literal["https://w3id.org/dspace/2025/1/context.jsonld"]] = Field(alias="@context")
    type: Literal["CatalogError"] = Field(alias="@type")
    code: Optional[str]
    reason: Optional[List]
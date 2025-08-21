from pydantic import Field
from ...base import SingularBaseModel
from typing import List, Literal, Optional, Union, ForwardRef

# Forward references
DatasetRef = ForwardRef("Dataset")
DataServiceRef = ForwardRef("DataService")


class Constraint(SingularBaseModel):
    leftOperand: str
    operator: str
    rightOperand: str

class Duty(SingularBaseModel):
    action: Optional[str] = None
    constraint: Optional[List[Constraint]] = None

class Rule(SingularBaseModel):
    action: str
    constraint: Optional[List[Constraint]] = None
    duty: Optional[List[Duty]] = None

class Agreement(SingularBaseModel):
    id: str = Field(alias='@id')
    type: Literal["Agreement"] = Field(alias='@type')
    assignee: str
    assigner: str
    target: str
    obligation: Optional[List[Duty]] = None
    permission: Optional[List[Rule]] = None
    profile: Optional[List[str]] = None
    prohibition: Optional[List[Rule]] = None
    timestamp: Optional[str] = None

class Offer(SingularBaseModel):
    id: str = Field(alias='@id')
    type: Optional[Literal["Offer"]] = Field(alias='@type')
    obligation: Optional[List[Duty]] = None
    permission: Optional[List[Rule]] = None
    profile: Optional[List[str]] = None
    prohibition: Optional[List[Rule]] = None


class Distribution(SingularBaseModel):
    accessService: Union[DataServiceRef, str]
    format: str
    hasPolicy: Optional[List[Offer]] = None

class Dataset(SingularBaseModel):
    id: str = Field(alias='@id')
    type: Optional[Literal["Dataset"]] = Field(alias='@type')
    context: List[Literal["https://w3id.org/dspace/2025/1/context.jsonld"]] = Field(alias="@context", default=None)
    distribution: List[Distribution]
    hasPolicy: List[Offer]

class DataService(SingularBaseModel):
    id: str = Field(alias='@id')
    type: Optional[Literal["DataService"]] = Field(alias='@type')
    endpointURL: Optional[str] = None
    servesDataset: Optional[List[DatasetRef]] = None

class Catalog(SingularBaseModel):
    id: str = Field(alias='@id')
    type: Literal["Catalog"] = Field(alias='@type')
    catalog: Optional[List["Catalog"]] = None  # Recursive self-reference
    dataset: Optional[List[Dataset]] = None
    service: Optional[List[DataService]] = None

class EndpointProperty(SingularBaseModel):
    type: Literal["EndpointProperty"] = Field(alias='@type')
    name: str
    value: str

class DataAddress(SingularBaseModel):
    type: Literal["DataAddress"] = Field(alias='@type')
    endpointType: str
    endpoint: Optional[str] = None
    endpointProperties: Optional[List[EndpointProperty]] = None


Distribution.model_rebuild()
DataService.model_rebuild()
Catalog.model_rebuild()

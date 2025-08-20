from pydantic import Field
from ..base import SingularBaseModel
from typing import List, Literal, Optional, Union, ForwardRef

# Forward references
DatasetRef = ForwardRef("Dataset")
DataServiceRef = ForwardRef("DataService")


class Action(SingularBaseModel): str

class Constraint(SingularBaseModel):
    leftOperand: str
    operator: str
    rightOperand: str

class Duty(SingularBaseModel):
    action: Optional[Action]
    constraint: Optional[List[Constraint]]

class Rule(SingularBaseModel):
    action: Action
    constraint: Optional[List[Constraint]]
    duty: Optional[List[Duty]]

class Agreement(SingularBaseModel):
    id: str = Field(alias='@id')
    type: Literal["Agreement"] = Field(alias='@type')
    assignee: str
    assigner: str
    target: str
    obligation: Optional[List[Duty]]
    permission: Optional[List[Rule]]
    profile: Optional[List[str]]
    prohibition: Optional[List[Rule]]
    timestamp: Optional[str]

class Offer(SingularBaseModel):
    id: str = Field(alias='@id')
    type: Optional[Literal["Offer"]] = Field(alias='@type')
    obligation: Optional[List[Duty]]
    permission: Optional[List[Rule]]
    profile: Optional[List[str]]
    prohibition: Optional[List[Rule]]


class Distribution(SingularBaseModel):
    accessService: Union[DataServiceRef, str]
    format: str
    hasPolicy: Optional[List[Offer]]

class Dataset(SingularBaseModel):
    id: str = Field(alias='@id')
    distribution: List[Distribution]
    hasPolicy: List[Offer]

class DataService(SingularBaseModel):
    id: str = Field(alias='@id')
    type: Optional[Literal["DataService"]] = Field(alias='@type')
    endpointURL: Optional[str]
    servesDataset: Optional[List[DatasetRef]]

class Catalog(SingularBaseModel):
    id: str = Field(alias='@id')
    type: Literal["Catalog"] = Field(alias='@type')
    catalog: Optional[List["Catalog"]]  # Recursive self-reference
    dataset: Optional[List[Dataset]]
    service: Optional[List[DataService]]

class EndpointProperty(SingularBaseModel):
    type: Literal["EndpointProperty"] = Field(alias='@type')
    name: str
    value: str

class DataAddress(SingularBaseModel):
    type: Literal["DataAddress"] = Field(alias='@type')
    endpointType: str
    endpoint: Optional[str]
    endpointProperties: Optional[List[EndpointProperty]]

class MessageOffer(Offer):
    target: Optional[str]

Distribution.model_rebuild()
DataService.model_rebuild()
Catalog.model_rebuild()

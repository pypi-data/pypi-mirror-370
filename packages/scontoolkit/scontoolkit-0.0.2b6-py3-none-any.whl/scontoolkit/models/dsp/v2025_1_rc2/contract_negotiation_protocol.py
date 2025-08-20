from pydantic import Field
from ...base import SingularBaseModel
from typing import List, Literal, Optional
from .low_level import Offer

# Forward references
# DatasetRef = ForwardRef("Dataset")
# DataServiceRef = ForwardRef("DataService")


class MessageOffer(Offer):
    target: Optional[str]

class ContractRequestMessage(SingularBaseModel):
    context: List[Literal["https://w3id.org/dspace/2025/1/context.jsonld"]] = Field(alias="@context")
    type: Literal["ContractRequestMessage"]= Field(alias="@type")
    callbackAddress: str
    consumerPid: str
    offer: MessageOffer
    providerPid: Optional[str] = None

class ContractOfferMessage(SingularBaseModel):
    context: List[Literal["https://w3id.org/dspace/2025/1/context.jsonld"]] = Field(alias="@context")
    type: Literal["ContractOfferMessage"]= Field(alias="@type")
    callbackAddress: str
    consumerPid: str
    offer: MessageOffer
    providerPid: Optional[str] = None


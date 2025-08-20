from pydantic import Field, HttpUrl
from ..base import SingularBaseModel
from typing import List, Literal, Optional, Any, Union


class Auth(SingularBaseModel):
    protocol: str
    version: str
    profile: Optional[List]

class Version(SingularBaseModel):
    binding: Literal["HTTPS"]
    path: str
    version: Any
    auth: Optional[Auth] = None
    identifierType: Optional[str] = None
    serviceId: Optional[str] = None

class VersionResponse(SingularBaseModel):
    protocolVersions: List[Version]

class DiDService(SingularBaseModel):
    context: List[Union[
        Literal["https://w3id.org/dspace/2025/1/context.jsonld"],
        Literal["https://www.w3.org/ns/did/v1"]
    ]] = Field(alias="@context")
    type: Literal["DataService", "CatalogService"]
    id: str
    serviceEndpoint: HttpUrl
#
#
#
# class SelfDescriptionResponse(SingularBaseModel):
#     model_config = ConfigDict(populate_by_name=True)
#
#     context: Literal["https://w3id.org/dspace/2024/1/context.json"] = Field(
#         alias="@context"
#     )
#     type: Literal["ConnectorDescription"] = Field(alias="@type")
#     id: HttpUrl = Field(alias="@id")
#
#     title: str
#     description: str
#     version: str
#     securityProfile: HttpUrl
#     maintainer: HttpUrl
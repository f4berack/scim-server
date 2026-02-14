from typing import List, Optional, Literal
from pydantic import BaseModel, Field, field_validator
from schema import SCIM_USER_SCHEMA, SCIM_ERROR_SCHEMA

class Name(BaseModel):
    formatted: Optional[str]
    familyName: Optional[str]
    givenName: Optional[str]

class Meta(BaseModel):
    resourceType: Optional[str]
    created: Optional[str]
    lastModified: Optional[str]
    location: Optional[str]
    version: Optional[str]

class ScimCreateUserRequest(BaseModel):
    schemas: List[str]
    userName: str
    externalId: str
    name: Name

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "schemas": [
                        "urn:ietf:params:scim:schemas:core:2.0:User"
                    ],
                    "userName": "testUserName",
                    "externalId": "testExternalId",
                    "name": {
                        "formatted": "Dr. Luke Skywalker",
                        "familyName": "Luke Skywalker",
                        "givenName": "Luke"
                    }
                }
            ]
        }
    }

class ScimUser(BaseModel):
    schemas: List[str]
    id: str
    externalId: str
    meta: Meta
    name: Name
    userName: str
    

ScimType = Literal[
    "invalidFilter",
    "tooMany",
    "uniqueness",
    "mutability",
    "invalidSyntax",
    "invalidPath",
    "noTarget",
    "invalidValue",
    "invalidVers",
    "sensitive",
]

class ScimErrorResponse(BaseModel):
    schemas: List[str] = Field(
        default_factory=lambda: [SCIM_ERROR_SCHEMA],
        description="SCIM error schema identifier",
    )

    status: str = Field(
        ...,
        description="HTTP status code expressed as a JSON string",
        examples=["400", "404", "409"],
    )

    scimType: Optional[ScimType] = Field(
        default=None,
        description="SCIM detail error keyword (Table 9)",
    )

    detail: Optional[str] = Field(
        default=None,
        description="Human-readable error description",
    )

    @field_validator("schemas")
    @classmethod
    def validate_schema(cls, v: List[str]) -> List[str]:
        if SCIM_ERROR_SCHEMA not in v:
            raise ValueError(
                f"schemas must include '{SCIM_ERROR_SCHEMA}'"
            )
        return v

    @field_validator("status")
    @classmethod
    def validate_status_is_numeric_string(cls, v: str) -> str:
        if not v.isdigit():
            raise ValueError("status must be a numeric HTTP status code as a string")
        return v
from datetime import datetime
from typing import Any, Callable, List, Optional

from pydantic import Base64Str, BaseModel, Field, GetJsonSchemaHandler, HttpUrl
from pydantic.json_schema import JsonSchemaValue
from pydantic_core import core_schema
from semver import Version
from typing_extensions import Annotated


class _VersionPydanticAnnotation:
    """
    Recommended way to use the `Version` class from the `semver` package with Pydantic,
    according to the documentation here:
    https://python-semver.readthedocs.io/en/3.0.2/advanced/combine-pydantic-and-semver.html
    """

    @classmethod
    def __get_pydantic_core_schema__(
        cls,
        _source_type: Any,
        _handler: Callable[[Any], core_schema.CoreSchema],
    ) -> core_schema.CoreSchema:
        def validate_from_str(value: str) -> Version:
            return Version.parse(value)

        from_str_schema = core_schema.chain_schema(
            [
                core_schema.str_schema(),
                core_schema.no_info_plain_validator_function(validate_from_str),
            ]
        )

        return core_schema.json_or_python_schema(
            json_schema=from_str_schema,
            python_schema=core_schema.union_schema(
                [
                    core_schema.is_instance_schema(Version),
                    from_str_schema,
                ]
            ),
            serialization=core_schema.to_string_ser_schema(),
        )

    @classmethod
    def __get_pydantic_json_schema__(
        cls, _core_schema: core_schema.CoreSchema, handler: GetJsonSchemaHandler
    ) -> JsonSchemaValue:
        return handler(core_schema.str_schema())


SemVer = Annotated[Version, _VersionPydanticAnnotation]


class ModelAuthor(BaseModel):
    email: Optional[str] = None
    orgId: Optional[str] = None
    orgName: Optional[str] = None
    givenName: Optional[str] = None
    familyName: Optional[str] = None

    def __str__(self) -> str:
        if self.givenName and self.familyName:
            s = f"{self.givenName} {self.familyName}"
        elif self.email:
            s = f"{self.email}"
        elif self.familyName:
            s = f"{self.familyName}"
        elif self.givenName:
            s = f"{self.givenName}"
        else:
            s = ""

        if self.orgName:
            s += f" ({self.orgName})"

        return s


class ModelVersion(BaseModel):
    tag: SemVer
    digest: str
    commitHash: str
    engineVersion: Optional[str] = None
    createdAt: Optional[datetime] = None
    createdBy: Optional[ModelAuthor] = None


class AddModel(BaseModel):
    id: str
    name: str
    description: str
    source_repository_url: HttpUrl = Field(serialization_alias="sourceRepositoryURL")
    logo_url: Optional[Base64Str] = Field(default=None, serialization_alias="logoURL")


class ModelDetails(BaseModel):
    id: str
    name: str
    createdAt: Optional[datetime] = None
    updatedAt: Optional[datetime] = None
    ociRepository: str
    sourceRepositoryURL: str
    card: dict
    createdBy: ModelAuthor
    versions: Optional[List[ModelVersion]] = Field(default_factory=list)


class RobotDetails(BaseModel):
    name: str
    token: str


__all__ = ["AddModel", "ModelAuthor", "ModelVersion", "ModelDetails", "RobotDetails"]

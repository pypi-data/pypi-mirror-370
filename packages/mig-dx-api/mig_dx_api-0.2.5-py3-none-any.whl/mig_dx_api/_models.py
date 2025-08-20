from typing import Annotated, AsyncGenerator, Literal, Optional, Generic, TypeVar
import datetime
from uuid import UUID
from pydantic import (
    BaseModel,
    Field,
    create_model,
    validate_call,
    ConfigDict,
    computed_field,
)
import warnings


class _BaseModel(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
    )


class ResponseMetadata(_BaseModel):
    count: int


class Workspace(_BaseModel):
    workspace_id: Annotated[int, Field(alias="workspaceId")]
    workspace_key: Annotated[str, Field(alias="workspaceKey")] = None
    display_name: Annotated[str, Field(alias="displayName")]
    type: Annotated[str, Field(alias="type")]


class CreatedBy(_BaseModel):
    user_id: Annotated[int, Field(alias="userId")]
    display_name: Annotated[str, Field(alias="displayName")]
    email: Annotated[str | None, Field(default=None)] = None


class WhoAmI(_BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
    )

    user_id: Annotated[int, Field(alias="userId")]
    workspace: Annotated[Workspace, Field(alias="workspace")]
    app_id: Annotated[UUID | None, Field(alias="appId")] = None
    display_name: Annotated[str, Field(alias="displayName")]
    email: Annotated[str | None, Field(alias="email")] = None
    date_terms_accepted: Annotated[str | None, Field(alias="dateTermsAccepted")] = None
    permissions: Annotated[list[str], Field(alias="permissions")]


# Schema property supporting multiple data types
class SchemaProperty(_BaseModel):
    type: str = "string"
    required: bool  # Removed exclude=True so it gets included in model_dump()
    name: str
    
    def model_post_init(self, __context):
        # Normalize type to lowercase and validate
        if hasattr(self, 'type'):
            self.type = self.type.lower()
            if self.type not in ["string", "integer", "boolean"]:
                raise ValueError(f"Invalid type '{self.type}'. Must be one of: string, integer, boolean")


class DatasetSchema(_BaseModel):
    dataset_schema_id: Annotated[int | None, Field(alias="datasetSchemaId")] = None
    properties: list[SchemaProperty]
    primary_key: Annotated[
        list[str], Field(alias="primaryKey", default_factory=list)
    ] = []


class CreateDataset(_BaseModel):
    name: str = Field(
        ..., title="Name of the dataset", description="Name of the dataset"
    )
    description: str = Field(
        ...,
        title="Description of the dataset",
        description="Description of the dataset",
    )
    schema_: DatasetSchema = Field(
        ...,
        alias="schema",
        title="Schema of the dataset",
        description="Schema of the dataset",
    )
    tagIds: Optional[list[dict]] = Field(
        ...,
        alias="tag_ids",
        title="List of tag IDs",
        description="List of tag IDs to associate with the dataset",
    )


class DatasetTag(_BaseModel):
    dataset_tag_id: Annotated[UUID, Field(alias="datasetTagId")]
    name: str
    movement_app_id: Annotated[UUID, Field(alias="movementAppId")]


class Dataset(_BaseModel):
    dataset_id: Annotated[UUID, Field(alias="datasetId")]
    name: str
    description: str
    date_created: Annotated[datetime.datetime, Field(alias="dateCreated")]
    record_count: Annotated[int, Field(alias="recordCount")]
    created_by: Annotated[CreatedBy, Field(alias="createdBy")]
    created_by_workspace: Annotated[Workspace, Field(alias="createdByWorkspace")]
    dataset_tags: Annotated[list[DatasetTag], Field(alias="datasetTags")] = []
    dataset_schema: Annotated[DatasetSchema, Field(alias="datasetSchema")]


class Installation(_BaseModel):
    installation_id: Annotated[int, Field(alias="installationId")]

    @property
    def movement_app_installation_id(self) -> str:
        warnings.warn("This field is deprecated. Use `installation_id` instead.")
        return self.installation_id

    movement_app_id: Annotated[UUID, Field(alias="movementAppId")]
    workspace_key: Annotated[str, Field(alias="workspaceKey")]
    workspace_id: Annotated[int, Field(alias="workspaceId")]
    created_by: Annotated[CreatedBy, Field(alias="createdBy")]
    date_created: Annotated[datetime.datetime, Field(alias="dateCreated")]
    name: str


class ClientToken(_BaseModel):
    token: str
    token_type: Annotated[Literal["Bearer"], Field(alias="tokenType")] = "Bearer"
    expires_at: Annotated[datetime.datetime, Field(alias="expiresAt")]


T = TypeVar("T", bound=BaseModel)


class PaginatedResponse(_BaseModel, Generic[T]):
    metadata: ResponseMetadata
    data: list[T]


class ExceptionDetails(_BaseModel):
    details: str
    headers: dict[str, str] = Field(
        ...,
        title="Request headers",
        description="Request headers",
        default_factory=dict,
    )
    path: str
    endpoint: str
    routeValues: dict[str, str]


class ErrorResponse(_BaseModel):
    model_config = ConfigDict(extra="allow")

    type: str
    title: str
    status: int
    detail: str
    exception: ExceptionDetails
    source: str

    def __repr__(self):
        return f"<Error {self.title} ({self.status}): {self.detail} />"


class DXException(Exception):
    def __init__(self, error: ErrorResponse):
        self.error = error
        super().__init__()

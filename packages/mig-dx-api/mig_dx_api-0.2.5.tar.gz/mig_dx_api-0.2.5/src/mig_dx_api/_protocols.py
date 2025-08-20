from typing import Protocol, AsyncGenerator, List, Dict, Any
from datetime import datetime
from uuid import UUID
import httpx


class WhoAmIProtocol(Protocol):
    user_id: int
    workspace_id: int
    app_id: UUID
    user_name: str | None
    email: str | None
    date_terms_accepted: datetime | None


class CreatedByProtocol(Protocol):
    user_id: int
    display_name: str
    email: str | None


class WorkspaceProtocol(Protocol):
    workspace_id: int
    display_name: str


class SchemaPropertyProtocol(Protocol):
    type: str
    required: bool
    name: str


class DatasetSchemaProtocol(Protocol):
    dataset_schema_id: int | None
    properties: List[SchemaPropertyProtocol]
    primary_key: List[str]


class CreateDatasetProtocol(Protocol):
    name: str
    description: str
    schema_: DatasetSchemaProtocol


class DatasetProtocol(Protocol):
    dataset_id: UUID
    name: str
    description: str
    date_created: datetime
    record_count: int
    created_by: CreatedByProtocol
    created_by_workspace: WorkspaceProtocol
    dataset_tags: List[str]
    dataset_schema: DatasetSchemaProtocol


class InstallationProtocol(Protocol):
    movement_app_installation_id: int
    movement_app_id: UUID
    workspace_id: int
    created_by: CreatedByProtocol
    date_created: datetime
    name: str


class ClientTokenProtocol(Protocol):
    token: str
    token_type: str
    expires_at: datetime


class DXProtocol(Protocol):
    app_id: str
    private_key_path: str
    auth_token: str

    @property
    def session(self) -> httpx.Client: ...

    @property
    def asession(self) -> httpx.AsyncClient: ...

    def create_auth_token(self) -> str: ...

    def whoami(self) -> WhoAmIProtocol: ...

    async def whoami_async(self) -> WhoAmIProtocol: ...

    def get_installations(self) -> List[InstallationProtocol]: ...

    async def get_installations_async(self) -> List[InstallationProtocol]: ...

    def get_client_token(self, installation_id: str, workspace_key: str) -> ClientTokenProtocol: ...

    async def get_client_token_async(
        self, installation_id: str, workspace_key: str
    ) -> ClientTokenProtocol: ...


class InstallationManagerProtocol(Protocol):
    def __iter__(self) -> List[InstallationProtocol]: ...

    async def __aiter__(self) -> AsyncGenerator[InstallationProtocol, None]: ...

    def find(
        self, name: str | None = None, install_id: int | None = None
    ) -> InstallationProtocol: ...

    async def find_async(
        self, name: str | None = None, install_id: int | None = None
    ) -> InstallationProtocol: ...


class SyncInstallationContextProtocol(Protocol):
    client: DXProtocol
    installation: InstallationProtocol

    def __enter__(self): ...

    def __exit__(self, exc_type, exc_value, traceback): ...


class AsyncInstallationContextProtocol(Protocol):
    client: DXProtocol
    installation: InstallationProtocol

    async def __aenter__(self): ...

    async def __aexit__(self, exc_type, exc_value, traceback): ...


class DatasetManagerProtocol(Protocol):
    def __iter__(self) -> List[DatasetProtocol]: ...

    def find(self, name: str) -> "DatasetOperationsProtocol": ...

    def create(
        self, name: str, description: str, schema: Dict[str, Any]
    ) -> "DatasetOperationsProtocol": ...


class AsyncDatasetManagerProtocol(Protocol):
    async def __aiter__(
        self,
    ) -> AsyncGenerator["AsyncDatasetOperationsProtocol", None]: ...

    async def list_datasets(self) -> AsyncGenerator[DatasetProtocol, None]: ...

    async def find(self, name: str) -> "AsyncDatasetOperationsProtocol": ...

    async def get(self, dataset_id: str) -> DatasetProtocol: ...

    async def create(
        self, name: str, description: str, schema: Dict[str, Any]
    ) -> "AsyncDatasetOperationsProtocol": ...


class DatasetOperationsProtocol(Protocol):
    dataset_id: str
    name: str
    description: str
    date_created: datetime
    record_count: int
    created_by: CreatedByProtocol
    created_by_workspace: WorkspaceProtocol
    dataset_tags: List[str]
    dataset_schema: DatasetSchemaProtocol

    def records(self) -> List[Dict[str, Any]]: ...

    def load(self, data: List[Dict[str, Any]]): ...

    def load_from_file(self, file_path: str): ...

    def load_from_url(self, data_url: str): ...

    def get_upload_url(self) -> Dict[str, str]: ...

    def upload_data_to_url(self, upload_url: str, data: List[Dict[str, Any]]): ...

    def upload_file_to_url(self, upload_url: str, file_path: str): ...

    def get_download_url(self) -> Dict[str, str]: ...

    def download_data_from_url(self, download_url: str) -> List[Dict[str, Any]]: ...


class AsyncDatasetOperationsProtocol(Protocol):
    dataset_id: str
    name: str
    description: str
    date_created: datetime
    record_count: int
    created_by: CreatedByProtocol
    created_by_workspace: WorkspaceProtocol
    dataset_tags: List[str]
    dataset_schema: DatasetSchemaProtocol

    async def load(
        self, data: List[Dict[str, Any]], validate_records: bool = True
    ) -> bool: ...

    async def get_upload_url(self) -> Dict[str, str]: ...

    async def upload_data_to_url(self, upload_url: str, data: List[Dict[str, Any]]): ...

    async def load_data_from_public_url(self, url: str) -> Dict[str, Any]: ...

    async def records(self) -> AsyncGenerator[Dict[str, Any], None]: ...

    async def get_download_url(self) -> Dict[str, str]: ...

    async def download_data_from_url(
        self, download_url: str
    ) -> List[Dict[str, Any]]: ...

    async def load_from_file(self, file_path: str): ...

    async def upload_file_to_url(self, upload_url: str, file_path: str): ...

    async def load_from_url(self, data_url: str) -> Dict[str, Any]: ...

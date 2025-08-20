# test_dx.py

import pytest
import pytest_asyncio
import respx
import datetime
from httpx import Response
from unittest.mock import patch, MagicMock
from mig_dx_api import (
    DX,
    WhoAmI,
    Installation,
    Dataset,
    DatasetSchema,
    SchemaProperty,
    CreateDataset,
    ClientToken,
    CreatedBy,
    Workspace,
)
from uuid import UUID, uuid4
from mig_dx_api._client import InstallationManager
from mig_dx_api._dataset import DatasetOperations, AsyncDatasetOperations


# Mock constants
BASE_URL = "https://app.movementinfrastructure.org/api/v1/{}"
TEST_APP_ID = str(uuid4())
TEST_PRIVATE_KEY_PATH = "path/to/private/key.pem"
TEST_PRIVATE_KEY = "private_key_contents"
FAKE_JWT_TOKEN = "fake_jwt_token"


@pytest.fixture
def client_response_token():
    return ClientToken.model_validate(
        {
            "token": "client_token",
            "tokenType": "Bearer",
            "expiresAt": "2023-10-10T13:00:00Z",
        }
    )


# Fixtures
@pytest.fixture
def dx_client(mocker, client_response_token: ClientToken):
    # Mock file opening and JWT encoding
    mocker.patch("builtins.open", mocker.mock_open(read_data=TEST_PRIVATE_KEY))
    mocker.patch("jwt.encode", return_value=FAKE_JWT_TOKEN)

    with patch("builtins.open", mocker.mock_open(read_data=TEST_PRIVATE_KEY)), patch(
        "jwt.encode", return_value=FAKE_JWT_TOKEN
    ):
        client = DX(app_id=TEST_APP_ID, private_key_path=TEST_PRIVATE_KEY_PATH)

        # Mock common endpoints
        respx.post(BASE_URL.format("auth/clientToken")).mock(
            return_value=Response(
                200, json=client_response_token.model_dump(mode="json")
            )
        )

        yield client


@pytest_asyncio.fixture
async def dx_client_async(mocker, client_response_token: ClientToken):
    # Mock file opening and JWT encoding
    mocker.patch("builtins.open", mocker.mock_open(read_data=TEST_PRIVATE_KEY))
    mocker.patch("jwt.encode", return_value=FAKE_JWT_TOKEN)
    # Initialize the DX client
    with patch("builtins.open", mocker.mock_open(read_data=TEST_PRIVATE_KEY)), patch(
        "jwt.encode", return_value=FAKE_JWT_TOKEN
    ):
        client = DX(app_id=TEST_APP_ID, private_key_path=TEST_PRIVATE_KEY_PATH)

        # Mock common endpoints
        respx.post(BASE_URL.format("auth/clientToken")).mock(
            return_value=Response(
                200, json=client_response_token.model_dump(mode="json")
            )
        )

        yield client


@pytest.fixture
def installation():
    return Installation.model_validate(
        {
            "installationId": 1,
            "movementAppId": str(uuid4()),
            "workspaceId": 100,
            "createdBy": {
                "userId": 123,
                "displayName": "Test User",
                "email": "test@example.com",
            },
            "dateCreated": "2023-10-10T12:00:00Z",
            "name": "Test Installation",
        }
    )


# Helper function to create mock responses
def create_mock_response(status_code=200, json_data=None):
    response = Response(status_code)
    response.json = lambda: json_data
    response.raise_for_status = MagicMock()
    return response


# Test DX client initialization
def test_dx_initialization(dx_client: DX):
    assert dx_client.app_id == TEST_APP_ID
    assert dx_client._private_key == TEST_PRIVATE_KEY
    assert dx_client.auth_token == FAKE_JWT_TOKEN
    assert dx_client.auth_header == f"Bearer {FAKE_JWT_TOKEN}"
    assert dx_client.mode == "sync"


# Test whoami method (sync)
@respx.mock
def test_dx_whoami(dx_client: DX):
    whoami_response = {
        "userId": 123,
        "workspaceId": 456,
        "appId": str(uuid4()),
        "userName": "testuser",
        "email": "test@example.com",
        "dateTermsAccepted": None,
    }
    respx.get(BASE_URL.format("auth/me")).mock(
        return_value=Response(200, json=whoami_response)
    )
    whoami = dx_client.whoami()

    assert whoami.user_id == 123
    assert whoami.email == "test@example.com"


# Test whoami method (async)
@pytest.mark.asyncio
@respx.mock
async def test_dx_whoami_async(dx_client_async: DX):
    whoami_response = {
        "userId": 123,
        "workspaceId": 456,
        "appId": str(uuid4()),
        "userName": "testuser",
        "email": "test@example.com",
        "dateTermsAccepted": None,
    }
    respx.get(BASE_URL.format("auth/me")).mock(
        return_value=Response(200, json=whoami_response)
    )
    whoami = await dx_client_async.whoami_async()
    assert whoami.user_id == 123
    assert whoami.email == "test@example.com"


# Test get_installations method (sync)
@respx.mock
def test_dx_get_installations(dx_client: DX):
    installations_response = {
        "data": [
            {
                "installationId": 1,
                "movementAppId": str(uuid4()),
                "workspaceId": 100,
                "createdBy": {
                    "userId": 123,
                    "displayName": "Test User",
                    "email": "test@example.com",
                },
                "dateCreated": "2023-10-10T12:00:00Z",
                "name": "Test Installation",
            }
        ]
    }
    respx.get(BASE_URL.format("apps/me/installations")).mock(
        return_value=Response(200, json=installations_response)
    )
    installations = dx_client.get_installations()
    assert len(installations) == 1
    installation = installations[0]
    assert installation.installation_id == 1
    assert installation.name == "Test Installation"


# Test get_installations method (async)
@pytest.mark.asyncio
@respx.mock
async def test_dx_get_installations_async(dx_client_async: DX):
    installations_response = {
        "data": [
            {
                "installationId": 1,
                "movementAppId": str(uuid4()),
                "workspaceId": 100,
                "createdBy": {
                    "userId": 123,
                    "displayName": "Test User",
                    "email": "test@example.com",
                },
                "dateCreated": "2023-10-10T12:00:00Z",
                "name": "Test Installation",
            }
        ]
    }
    respx.get(BASE_URL.format("apps/me/installations")).mock(
        return_value=Response(200, json=installations_response)
    )
    installations = await dx_client_async.get_installations_async()
    assert len(installations) == 1
    installation = installations[0]
    assert installation.installation_id == 1
    assert installation.name == "Test Installation"


# Test get_client_token method (sync)
@respx.mock
def test_dx_get_client_token(dx_client: DX, client_response_token: ClientToken):
    respx.post(BASE_URL.format("auth/clientToken")).mock(
        return_value=Response(200, json=client_response_token.model_dump(mode="json"))
    )
    client_token = dx_client.get_client_token(installation_id="1")
    assert client_token.token == "client_token"
    assert client_token.token_type == "Bearer"


# Test get_client_token method (async)
@pytest.mark.asyncio
@respx.mock
async def test_dx_get_client_token_async(
    dx_client_async: DX, client_response_token: ClientToken
):
    # respx.post(BASE_URL.format("auth/clientToken")).mock(
    #     return_value=Response(200, json=client_response_token.model_dump(mode="json"))
    # )
    client_token = await dx_client_async.get_client_token_async(installation_id="1")
    assert client_token.token == "client_token"
    assert client_token.token_type == "Bearer"


# Test InstallationManager find method (sync)
@respx.mock
def test_installation_manager_find(dx_client: DX):
    installations_response = {
        "data": [
            {
                "installationId": 1,
                "movementAppId": str(uuid4()),
                "workspaceId": 100,
                "createdBy": {
                    "userId": 123,
                    "displayName": "Test User",
                    "email": "test@example.com",
                },
                "dateCreated": "2023-10-10T12:00:00Z",
                "name": "Test Installation",
            }
        ]
    }
    respx.get(BASE_URL.format("apps/me/installations")).mock(
        return_value=Response(200, json=installations_response)
    )
    installation_manager = dx_client.installations
    installation = installation_manager.find(name="Test Installation")
    assert installation.installation_id == 1
    assert installation.name == "Test Installation"


# Test InstallationManager find method (async)
@pytest.mark.asyncio
@respx.mock
async def test_installation_manager_find_async(dx_client_async: DX):
    installations_response = {
        "data": [
            {
                "installationId": 1,
                "movementAppId": str(uuid4()),
                "workspaceId": 100,
                "createdBy": {
                    "userId": 123,
                    "displayName": "Test User",
                    "email": "test@example.com",
                },
                "dateCreated": "2023-10-10T12:00:00Z",
                "name": "Test Installation",
            }
        ]
    }
    respx.get(BASE_URL.format("apps/me/installations")).mock(
        return_value=Response(200, json=installations_response)
    )
    installation_manager = dx_client_async.installations
    installation = await installation_manager.find_async(name="Test Installation")
    assert installation.installation_id == 1
    assert installation.name == "Test Installation"


# Test Installation context manager (sync)
@respx.mock
def test_installation_context(dx_client: DX, client_response_token: ClientToken):
    installations_response = {
        "data": [
            {
                "installationId": 1,
                "movementAppId": str(uuid4()),
                "workspaceId": 100,
                "createdBy": {
                    "userId": 123,
                    "displayName": "Test User",
                    "email": "test@example.com",
                },
                "dateCreated": "2023-10-10T12:00:00Z",
                "name": "Test Installation",
            }
        ]
    }

    respx.get(BASE_URL.format("apps/me/installations")).mock(
        return_value=Response(200, json=installations_response)
    )
    # respx.post(BASE_URL.format("auth/clientToken")).mock(
    #     return_value=Response(200, json=client_response_token.model_dump(mode="json"))
    # )
    installation = dx_client.installations.find(name="Test Installation")
    with dx_client.installation(installation=installation) as install_ctx:
        assert dx_client.auth_header == "Bearer client_token"
        assert install_ctx.datasets is not None
        # Mock datasets endpoint
        datasets_response = {
            "data": [
                {
                    "datasetId": str(uuid4()),
                    "name": "Test Dataset",
                    "description": "Test Description",
                    "dateCreated": "2023-10-10T12:00:00Z",
                    "recordCount": 100,
                    "createdBy": {
                        "userId": 123,
                        "displayName": "Test User",
                        "email": "test@example.com",
                    },
                    "createdByWorkspace": {
                        "workspaceId": 100,
                        "displayName": "Test Workspace",
                    },
                    "datasetTags": [],
                    "datasetSchema": {
                        "datasetSchemaId": 1,
                        "properties": [],
                        "primaryKey": [],
                    },
                }
            ]
        }
        respx.get(BASE_URL.format("datasets")).mock(
            return_value=Response(200, json=datasets_response)
        )
        datasets = list(install_ctx.datasets)
        assert len(datasets) == 1
        dataset = datasets[0]
        assert dataset.name == "Test Dataset"


# Test Installation context manager (async)
@pytest.mark.asyncio
@respx.mock
async def test_installation_context_async(
    dx_client_async: DX, client_response_token: ClientToken
):
    installations_response = {
        "data": [
            {
                "installationId": 1,
                "movementAppId": str(uuid4()),
                "workspaceId": 100,
                "createdBy": {
                    "userId": 123,
                    "displayName": "Test User",
                    "email": "test@example.com",
                },
                "dateCreated": "2023-10-10T12:00:00Z",
                "name": "Test Installation",
            }
        ]
    }

    respx.get(BASE_URL.format("apps/me/installations")).mock(
        return_value=Response(200, json=installations_response)
    )
    # respx.post(BASE_URL.format("auth/clientToken")).mock(
    #     return_value=Response(200, json=client_response_token.model_dump(mode="json"))
    # )
    installation = await dx_client_async.installations.find_async(
        name="Test Installation"
    )
    async with dx_client_async.installation(installation=installation) as install_ctx:
        assert dx_client_async.auth_header == "Bearer client_token"
        assert install_ctx.datasets is not None
        # Mock datasets endpoint
        datasets_response = {
            "data": [
                {
                    "datasetId": str(uuid4()),
                    "name": "Test Dataset",
                    "description": "Test Description",
                    "dateCreated": "2023-10-10T12:00:00Z",
                    "recordCount": 100,
                    "createdBy": {
                        "userId": 123,
                        "displayName": "Test User",
                        "email": "test@example.com",
                    },
                    "createdByWorkspace": {
                        "workspaceId": 100,
                        "displayName": "Test Workspace",
                    },
                    "datasetTags": [],
                    "datasetSchema": {
                        "datasetSchemaId": 1,
                        "properties": [],
                        "primaryKey": [],
                    },
                }
            ]
        }
        respx.get(BASE_URL.format("datasets")).mock(
            return_value=Response(200, json=datasets_response)
        )
        datasets = []
        async for dataset in install_ctx.datasets:
            datasets.append(dataset)
        assert len(datasets) == 1
        dataset = datasets[0]
        assert dataset.name == "Test Dataset"


# Test DatasetManager create method (sync)
@respx.mock
def test_dataset_manager_create(
    dx_client: DX, client_response_token: ClientToken, installation: Installation
):
    # respx.post(BASE_URL.format("auth/clientToken")).mock(
    #     return_value=Response(200, json=client_response_token.model_dump(mode="json"))
    # )

    with dx_client.installation(installation=installation) as install_ctx:
        dataset_response = {
            "datasetId": str(uuid4()),
            "name": "New Dataset",
            "description": "New Description",
            "dateCreated": "2023-10-10T12:00:00Z",
            "recordCount": 0,
            "createdBy": {
                "userId": 123,
                "displayName": "Test User",
                "email": "test@example.com",
            },
            "createdByWorkspace": {
                "workspaceId": 100,
                "displayName": "Test Workspace",
            },
            "datasetTags": [],
            "datasetSchema": {
                "datasetSchemaId": 1,
                "properties": [
                    {
                        "type": "string",
                        "required": True,
                        "name": "id",
                    },
                    {
                        "type": "string",
                        "required": True,
                        "name": "value",
                    },
                ],
                "primaryKey": ["id"],
            },
        }
        respx.post(BASE_URL.format("datasets")).mock(
            return_value=Response(200, json=dataset_response)
        )
        dataset_ops = install_ctx.datasets.create(
            name="New Dataset",
            description="New Description",
            schema=DatasetSchema(
                primary_key=["id"],
                properties=[
                    SchemaProperty(name="id", type="string", required=True),
                    SchemaProperty(name="value", type="string", required=True),
                ],
            ),
        )
        assert dataset_ops.name == "New Dataset"


# Test DatasetManager create method (async)
@pytest.mark.asyncio
@respx.mock
async def test_dataset_manager_create_async(
    dx_client_async: DX, installation: Installation
):
    # client_token_response = {
    #     "token": "client_token",
    #     "tokenType": "Bearer",
    #     "expiresAt": "2023-10-10T13:00:00Z",
    # }
    # respx.post(BASE_URL.format("auth/clientToken")).mock(
    #     return_value=Response(200, json=client_token_response)
    # )

    async with dx_client_async.installation(installation=installation) as install_ctx:
        dataset_response = {
            "datasetId": str(uuid4()),
            "name": "New Dataset",
            "description": "New Description",
            "dateCreated": "2023-10-10T12:00:00Z",
            "recordCount": 0,
            "createdBy": {
                "userId": 123,
                "displayName": "Test User",
                "email": "test@example.com",
            },
            "createdByWorkspace": {
                "workspaceId": 100,
                "displayName": "Test Workspace",
            },
            "datasetTags": [],
            "datasetSchema": {
                "datasetSchemaId": 1,
                "properties": [
                    {
                        "type": "string",
                        "required": True,
                        "name": "id",
                    },
                    {
                        "type": "string",
                        "required": True,
                        "name": "value",
                    },
                ],
                "primaryKey": ["id"],
            },
        }
        respx.post(BASE_URL.format("datasets")).mock(
            return_value=Response(200, json=dataset_response)
        )
        dataset_ops = await install_ctx.datasets.create(
            name="New Dataset",
            description="New Description",
            schema=DatasetSchema(
                properties=[
                    SchemaProperty(name="id", type="string", required=True),
                    SchemaProperty(name="value", type="string", required=True),
                ],
                primary_key=["id"],
            ),
        )
        assert dataset_ops.name == "New Dataset"


# Test DatasetOperations load method (sync)
@respx.mock
def test_dataset_operations_load(
    dx_client: DX, client_response_token: ClientToken, installation: Installation
):
    with dx_client.installation(installation=installation) as install_ctx:
        dataset = Dataset(
            dataset_id=str(uuid4()),
            name="Test Dataset",
            description="Test Description",
            date_created=datetime.datetime.now(),
            record_count=0,
            created_by=CreatedBy(
                user_id=123, display_name="Test User", email="test@example.com"
            ),
            created_by_workspace=Workspace(
                workspace_id=100, display_name="Test Workspace"
            ),
            dataset_tags=[],
            dataset_schema=DatasetSchema(
                dataset_schema_id=1,
                properties=[
                    SchemaProperty(type="string", required=False, name="field1")
                ],
                primary_key=[],
            ),
        )
        dataset_ops = DatasetOperations(dataset, install_ctx)
        # Mock get_upload_url
        upload_url_response = {"url": "http://fake-upload-url.com"}
        respx.post(BASE_URL.format(f"datasets/{dataset.dataset_id}/uploadUrl")).mock(
            return_value=Response(200, json=upload_url_response)
        )
        # Mock upload_data_to_url
        respx.put("http://fake-upload-url.com").mock(
            return_value=Response(200, text="OK")
        )
        dataset_ops.load(data=[{"field1": "value1"}])


# Test DatasetOperations load method (async)
@pytest.mark.asyncio
@respx.mock
async def test_dataset_operations_load_async(
    dx_client_async: DX,
    client_response_token: ClientToken,
    installation: Installation,
):
    respx.post(BASE_URL.format("auth/clientToken")).mock(
        return_value=Response(200, json=client_response_token.model_dump(mode="json"))
    )

    async with dx_client_async.installation(installation=installation) as install_ctx:
        dataset = Dataset(
            dataset_id=str(uuid4()),
            name="Test Dataset",
            description="Test Description",
            date_created=datetime.datetime.now(),
            record_count=0,
            created_by=CreatedBy(
                user_id=123, display_name="Test User", email="test@example.com"
            ),
            created_by_workspace=Workspace(
                workspace_id=100, display_name="Test Workspace"
            ),
            dataset_tags=[],
            dataset_schema=DatasetSchema(
                dataset_schema_id=1,
                properties=[
                    SchemaProperty(type="string", required=False, name="field1")
                ],
                primary_key=[],
            ),
        )
        dataset_ops = AsyncDatasetOperations(dataset, install_ctx)
        # Mock get_upload_url
        upload_url_response = {"url": "http://fake-upload-url.com"}
        respx.post(BASE_URL.format(f"datasets/{dataset.dataset_id}/uploadUrl")).mock(
            return_value=Response(200, json=upload_url_response)
        )
        # Mock upload_data_to_url
        respx.put("http://fake-upload-url.com").mock(
            return_value=Response(200, text="OK")
        )
        await dataset_ops.load(data=[{"field1": "value1"}])


# Test DatasetOperations records method (sync)
@respx.mock
def test_dataset_operations_records(
    dx_client: DX, client_response_token: ClientToken, installation: Installation
):
    respx.post(BASE_URL.format("auth/clientToken")).mock(
        return_value=Response(200, json=client_response_token.model_dump(mode="json"))
    )

    with dx_client.installation(installation=installation) as install_ctx:
        dataset = Dataset(
            dataset_id=str(uuid4()),
            name="Test Dataset",
            description="Test Description",
            date_created=datetime.datetime.now(),
            record_count=0,
            created_by=CreatedBy(
                user_id=123, display_name="Test User", email="test@example.com"
            ),
            created_by_workspace=Workspace(
                workspace_id=100, display_name="Test Workspace"
            ),
            dataset_tags=[],
            dataset_schema=DatasetSchema(
                dataset_schema_id=1,
                properties=[
                    SchemaProperty(type="string", required=False, name="field1")
                ],
                primary_key=[],
            ),
        )
        dataset_ops = DatasetOperations(dataset, install_ctx)
        # Mock get_download_url
        download_url_response = {"url": "http://fake-download-url.com"}
        respx.post(
            BASE_URL.format(f"datasets/{dataset.dataset_id}/records:retrieve")
        ).mock(return_value=Response(200, json=download_url_response))
        # Mock download_data_from_url
        csv_data = "field1\nvalue1\n"
        respx.get("http://fake-download-url.com").mock(
            return_value=Response(200, text=csv_data)
        )
        records = dataset_ops.records()
        assert len(records) == 1
        assert records[0]["field1"] == "value1"


# Test DatasetOperations records method (async)
@pytest.mark.asyncio
@respx.mock
async def test_dataset_operations_records_async(
    dx_client_async: DX,
    client_response_token: ClientToken,
    installation: Installation,
):
    respx.post(BASE_URL.format("auth/clientToken")).mock(
        return_value=Response(200, json=client_response_token.model_dump(mode="json"))
    )

    async with dx_client_async.installation(installation=installation) as install_ctx:
        dataset = Dataset(
            dataset_id=str(uuid4()),
            name="Test Dataset",
            description="Test Description",
            date_created=datetime.datetime.now(),
            record_count=0,
            created_by=CreatedBy(
                user_id=123, display_name="Test User", email="test@example.com"
            ),
            created_by_workspace=Workspace(
                workspace_id=100, display_name="Test Workspace"
            ),
            dataset_tags=[],
            dataset_schema=DatasetSchema(
                dataset_schema_id=1,
                properties=[
                    SchemaProperty(type="string", required=False, name="field1")
                ],
                primary_key=[],
            ),
        )
        dataset_ops = AsyncDatasetOperations(dataset, install_ctx)
        # Mock get_download_url
        download_url_response = {"url": "http://fake-download-url.com"}
        respx.post(
            BASE_URL.format(f"datasets/{dataset.dataset_id}/records:retrieve")
        ).mock(return_value=Response(200, json=download_url_response))
        # Mock download_data_from_url
        csv_data = "field1\nvalue1\n"
        respx.get("http://fake-download-url.com").mock(
            return_value=Response(200, text=csv_data)
        )
        records = []
        async for record in dataset_ops.records():
            records.append(record)
        assert len(records) == 1
        assert records[0]["field1"] == "value1"

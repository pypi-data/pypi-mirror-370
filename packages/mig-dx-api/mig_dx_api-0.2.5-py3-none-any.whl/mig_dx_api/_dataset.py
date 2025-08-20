import contextvars
import csv
import datetime
import io
import os
from abc import ABC, abstractmethod
from typing import Annotated, AsyncGenerator, Literal, Optional
from uuid import UUID
from pydantic import validate_call
import aiofiles
import httpx
import jwt
from loguru import logger

from ._models import Dataset, Field, create_model, SchemaProperty, DatasetSchema

from ._protocols import (
    SyncInstallationContextProtocol,
    AsyncInstallationContextProtocol,
)

APPROVED_CONTENT_TYPES = ["csv", "json", "tsv"]

class DatasetManager:
    def __init__(self, installation_context: SyncInstallationContextProtocol):
        self.installation_context = installation_context
        self.client = installation_context.client
        self.session = installation_context.session
        self.datasets = None

    def __iter__(self):
        response = self.session.get(self.client.base_url.format("datasets"))
        response.raise_for_status()
        data = response.json()
        return iter([Dataset(**item) for item in data.get("data", [])])

    def find(self, name: str):
        for dataset in self:
            if dataset.name == name:
                return DatasetOperations(dataset, self.installation_context)
        raise KeyError(f"Dataset with name '{name}' not found")

    @validate_call(validate_return=True)
    def get(self, dataset_id: str | UUID) -> Dataset:
        response = self.session.get(
            self.client.base_url.format(f"datasets/{dataset_id}")
        )
        response.raise_for_status()
        return response.json()
    
    def get_tags(self):
        response = self.session.get(
            self.client.base_url.format("datasets/tags")
        )
        response.raise_for_status()
        return response.json()
        
    def create(
        self,
        name: str,
        description: str,
        schema: dict | DatasetSchema,
        tag_ids: Optional[list[str]] = None,
    ) -> "DatasetOperations":
        if isinstance(schema, dict):
            schema = DatasetSchema(**schema)
        jsonBody = {
                "name": name,
                "description": description,
                "schema": schema.model_dump(
                    mode="json",
                    exclude_none=True,
                    by_alias=True,
                ),
            }
        if tag_ids:
            jsonBody["tagIds"] = [{"movementAppId": tag} for tag in tag_ids]

        response = self.session.post(
            self.client.base_url.format("datasets"),
            json=jsonBody,
        )
        response.raise_for_status()
        data = response.json()
        dataset = Dataset(**data)
        if self.datasets is not None:
            self.datasets.append(dataset)
        return DatasetOperations(dataset, self.installation_context)
    
    def get_dataset_job(self, job_id: str):
        response = self.session.get(
            self.client.base_url.format(f"datasets/jobs/{job_id}")
        )
        response.raise_for_status()
        return response.json()
    
    def get_dataset_job_logs(self, job_id: str):
        response = self.session.get(
            self.client.base_url.format(f"datasets/jobs/{job_id}/logs")
        )
        response.raise_for_status()
        return response.json()
    
    def get_current_dataset_logs(self, job_id: str):
        response = self.session.get(
            self.client.base_url.format(f"datasets/jobs/{job_id}/logs:current")
        )
        response.raise_for_status()
        return response.json()
            


class AsyncDatasetManager:
    def __init__(self, installation_context: AsyncInstallationContextProtocol):
        self.installation_context = installation_context
        self.client = installation_context.client
        self.session = installation_context.session
        self.datasets = None

    async def __aiter__(self) -> AsyncGenerator["AsyncDatasetOperations", None]:
        async for dataset in self.list_datasets():
            yield AsyncDatasetOperations(dataset, self.installation_context)

    async def list_datasets(self) -> AsyncGenerator[Dataset, None]:
        response = await self.session.get(self.client.base_url.format("datasets"))
        response.raise_for_status()
        data = response.json()
        for item in data.get("data", []):
            yield Dataset(**item)
        # return [Dataset(**item) for item in data.get("data", [])]

    async def find(self, name: str) -> "AsyncDatasetOperations":
        async for dataset in self:
            if dataset.name == name:
                return AsyncDatasetOperations(dataset, self.installation_context)
        raise KeyError(f"Dataset with name '{name}' not found")

    @validate_call(validate_return=True)
    async def get(self, dataset_id: str) -> Dataset:
        response = await self.session.get(
            self.client.base_url.format(f"datasets/{dataset_id}")
        )
        response.raise_for_status()
        return response.json()
    
    async def get_tags(self):
        response = await self.session.get(
            self.client.base_url.format("datasets/tags")
        )
        response.raise_for_status()
        return response.json()

    async def create(
        self,
        name: str,
        description: str,
        schema: dict | DatasetSchema,
        tag_ids: Optional[list[str]] = None,
    ) -> "DatasetOperations":
        if isinstance(schema, dict):
            schema = DatasetSchema(**schema)

        jsonBody = {
                "name": name,
                "description": description,
                "schema": schema.model_dump(
                    mode="json",
                    exclude_none=True,
                    by_alias=True,
                ),
            }
        if tag_ids:
            jsonBody["tag_ids"] = [{"movementAppId": tag} for tag in tag_ids]

        response = await self.session.post(
            self.client.base_url.format("datasets"),
            json=jsonBody
        )
               
        response.raise_for_status()
        data = response.json()
        dataset = Dataset(**data)
        if self.datasets is not None:
            self.datasets.append(dataset)
        return AsyncDatasetOperations(dataset, self.installation_context)
    
    async def get_dataset_job(self, job_id: str):
        response = await self.session.get(
            self.client.base_url.format(f"datasets/jobs/{job_id}")
        )
        response.raise_for_status()
        return response.json()
    
    async def get_dataset_job_logs(self, job_id: str):
        response = await self.session.get(
            self.client.base_url.format(f"datasets/jobs/{job_id}/logs")
        )
        response.raise_for_status()
        return response.json()
    
    async def get_current_dataset_logs(self, job_id: str):
        response = await self.session.get(
            self.client.base_url.format(f"datasets/jobs/{job_id}/logs:current")
        )
        response.raise_for_status()
        return response.json()

class ABCDatasetOperations(ABC):
    _dataset: Dataset

    @property
    def dataset_id(self) -> str:
        return self._dataset.dataset_id

    @property
    def name(self) -> str:
        return self._dataset.name

    @property
    def description(self):
        return self._dataset.description

    @property
    def date_created(self):
        return self._dataset.date_created

    @property
    def record_count(self):
        return self._dataset.record_count

    @property
    def created_by(self):
        return self._dataset.created_by

    @property
    def created_by_workspace(self):
        return self._dataset.created_by_workspace

    @property
    def dataset_tags(self):
        return self._dataset.dataset_tags

    @property
    def dataset_schema(self):
        return self._dataset.dataset_schema

    def _create_record_model(self):
        # Map schema types to Python types
        type_mapping = {
            'string': str,
            'integer': int,
            'boolean': bool,
        }
        
        _schema = []
        for prop in self.dataset_schema.properties:
            python_type = type_mapping.get(prop.type, str)  # Default to str if type not found
            _schema.append((prop.name, (python_type, Field(default=None))))
        return create_model("Record", **dict(_schema))

    @abstractmethod
    def records(self) -> list[dict]:
        raise NotImplementedError

    @abstractmethod
    def load(
        self,
        data: list[dict],
        validate_records: bool = True,
        upload_mode: Literal["replace", "create"] | None = None,
    ):
        raise NotImplementedError

    @abstractmethod
    def load_from_file(
        self,
        file_path: str,
        upload_mode: Literal["replace", "create"] | None = None,
    ):
        raise NotImplementedError

    @abstractmethod
    def load_from_url(self, data_url: str, mode: Literal["replace", "create"] | None):
        raise NotImplementedError

    @abstractmethod
    def get_upload_url(
        self,
        mode: Literal["replace", "create"] | None = None,
        upload_type: Literal["resumable", "singlerequest"] | None = None,
    ):
        raise NotImplementedError

    @abstractmethod
    def upload_data_to_url(self, upload_url: str, data: list[dict]):
        raise NotImplementedError

    @abstractmethod
    def upload_file_to_url(self, upload_url: str, file_path: str):
        raise NotImplementedError

    @abstractmethod
    def get_download_url(self, content_type: str = "csv"):
        raise NotImplementedError

    @abstractmethod
    def download_data_from_url(self, download_url: str) -> list[dict]:
        raise NotImplementedError

    def __repr__(self):
        return f"Operations[Dataset(dataset_id={self.dataset_id}, name={self.name})]"


class DatasetOperations(ABCDatasetOperations):
    def __init__(
        self, dataset: Dataset, installation_context: SyncInstallationContextProtocol
    ):
        self._dataset = dataset
        self._install_ctx = installation_context

    @property
    def client(self):
        return self._install_ctx.client

    @property
    def session(self):
        return self.client.session

    def load(
        self,
        data: list[dict],
        validate_records: bool = True,
        upload_mode: Literal["replace", "create"] | None = None,
    ):
        try:
            _model = self._create_record_model()
            if validate_records:
                _data = [_model(**record).model_dump(mode="json") for record in data]
            else:
                _data = data
        except Exception as e:
            raise ValueError(f"Data does not match schema: {e}")

        upload_info = self.get_upload_url(mode=upload_mode)

        upload_url = upload_info["url"]
        r = self.upload_data_to_url(upload_url, _data)
        
        assert r.status_code == 200
        return {"jobId": upload_info["jobId"]}

    def get_upload_url(
        self,
        mode: Literal["replace", "create"] | None = None,
        upload_type: Literal["resumable", "singlerequest"] | None = None,
    ):
        _params = {"mode": mode, "type": upload_type}

        response = self.session.post(
            self.client.base_url.format(f"datasets/{self.dataset_id}/uploadUrl"),
            params={k: v for k, v in _params.items() if v is not None},
            json={"contentType": "csv"},
        )
        response.raise_for_status()
        return response.json()

    def upload_data_to_url(self, upload_url: str, data: list[dict]):
        _buffer = io.StringIO()
        writer = csv.DictWriter(_buffer, fieldnames=data[0].keys())
        writer.writeheader()
        writer.writerows(data)
        _buffer.seek(0)
        response = self.session.put(
            upload_url, data=_buffer.getvalue(), headers={"Content-Type": "text/csv"}
        )
        response.raise_for_status()      
        return response

    def records(self, content_type: str = "csv"): 
        download_info = self.get_download_url(content_type=content_type)
        download_url = download_info["url"]
        return self.download_data_from_url(download_url)

    def get_download_url(self, content_type: str):
        if content_type not in APPROVED_CONTENT_TYPES:
            raise ValueError(f"content_type '{content_type}' is not currently supported.")
        response = self.session.post(
            self.client.base_url.format(f"datasets/{self.dataset_id}/records:retrieve"),
            json={"contentType": content_type},
        )
        response.raise_for_status()
        return response.json()

    def download_data_from_url(self, download_url: str) -> list[dict]:
        response = self.session.get(download_url)
        response.raise_for_status()
        with io.StringIO(response.text) as f:
            return list(csv.DictReader(f))

    def load_from_file(
        self,
        file_path: str,
        upload_mode: Literal["replace", "create"] | None = None,
    ):
        upload_info = self.get_upload_url(mode=upload_mode)
        upload_url = upload_info["url"]
        self.upload_file_to_url(upload_url, file_path)
        return {"jobId": upload_info["jobId"]}

    def upload_file_to_url(self, upload_url: str, file_path: str):
        with open(file_path, "rb") as f:
            response = self.session.put(upload_url, data=f, headers={"Content-Type": "text/csv"})
        response.raise_for_status()

    def load_from_url(self, data_url: str, mode: Literal["replace", "create"] | None):
        _params = {"mode": mode}
        response = self.session.post(
            self.client.base_url.format(f"datasets/{self.dataset_id}/records:load"),
            json={"url": data_url},
            params={k: v for k, v in _params.items() if v is not None},
        )
        response.raise_for_status()
        return response.json()


class AsyncDatasetOperations(ABCDatasetOperations):
    def __init__(
        self,
        dataset: Dataset,
        installation_context: AsyncInstallationContextProtocol,
    ):
        self._dataset = dataset
        self._install_ctx = installation_context

    @property
    def client(self):
        return self._install_ctx.client

    @property
    def session(self):
        return self.client.asession

    async def load(
        self,
        data: list[dict],
        validate_records: bool = True,
        upload_mode: Literal["replace", "create"] | None = None,
    ):
        try:
            _model = self._create_record_model()
            if validate_records:
                _data = [_model(**record).model_dump(mode="json") for record in data]
            else:
                _data = data
        except Exception as e:
            raise ValueError(f"Data does not match schema: {e}")

        upload_info = await self.get_upload_url(mode=upload_mode)
        upload_url = upload_info["url"]
        r = await self.upload_data_to_url(upload_url, _data)
        assert r.status_code == 200
        return {"jobId": upload_info["jobId"]}

    async def get_upload_url(
        self,
        mode: Literal["replace", "create"] | None = None,
        upload_type: Literal["resumable", "singlerequest"] | None = None,
    ):
        _params = {"mode": mode, "type": upload_type}
        response = await self.session.post(
            self.client.base_url.format(f"datasets/{self.dataset_id}/uploadUrl"),
            params={k: v for k, v in _params.items() if v is not None},
            json={"contentType": "csv"},
        )
        response.raise_for_status()
        return response.json()

    async def upload_data_to_url(self, upload_url: str, data: list[dict]):
        _buffer = io.StringIO()
        writer = csv.DictWriter(_buffer, fieldnames=data[0].keys())
        writer.writeheader()
        writer.writerows(data)
        _buffer.seek(0)
        response = await self.session.put(
            upload_url, data=_buffer.getvalue(), headers={"Content-Type": "text/csv"}
        )
        response.raise_for_status()
        return response

    async def records(self, content_type: str = "csv") -> AsyncGenerator[dict, None]:
        download_info = await self.get_download_url(content_type=content_type)
        logger.info(download_info)
        download_url = download_info["url"]
        logger.info(download_url)
        r = await self.download_data_from_url(download_url)
        for record in r:
            yield record

    async def get_download_url(self, content_type: str = "csv"):
        if content_type not in APPROVED_CONTENT_TYPES:
            raise ValueError(f"content_type '{content_type}' is not currently supportted.")
        response = await self.session.post(
            self.client.base_url.format(f"datasets/{self.dataset_id}/records:retrieve"),
            json={"contentType": content_type},
        )
        response.raise_for_status()
        return response.json()

    async def download_data_from_url(self, download_url: str) -> list[dict]:
        response = await self.session.get(download_url)
        response.raise_for_status()
        with io.StringIO(response.text) as f:
            return list(csv.DictReader(f))

    async def load_from_file(
        self,
        file_path: str,
        upload_mode: Literal["replace", "create"] | None = None,
    ):
        upload_info = await self.get_upload_url(mode=upload_mode)
        upload_url = upload_info["url"]
        await self.upload_file_to_url(upload_url, file_path)
        return {"jobId": upload_info["jobId"]}

    async def upload_file_to_url(self, upload_url: str, file_path: str):
        async with aiofiles.open(file_path, "rb") as f:
            file_data = await f.read()
            response = await self.session.put(upload_url, data=file_data, headers={"Content-Type": "text/csv"})
        response.raise_for_status()

    async def load_from_url(
        self, data_url: str, mode: Literal["replace", "create"] | None
    ):
        _params = {"mode": mode}
        response = await self.session.post(
            self.client.base_url.format(f"datasets/{self.dataset_id}/records:load"),
            json={"url": data_url},
            params={k: v for k, v in _params.items() if v is not None},
        )
        response.raise_for_status()
        return response.json()

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

from ._models import WhoAmI, Installation, ClientToken
from ._installation import SyncInstallationContext, AsyncInstallationContext


class DX:
    __version__ = "0.1.0"

    @classmethod
    def useragent(cls):
        return f"DX API Client v{cls.__version__}"

    def __init__(
        self,
        app_id: Optional[str] = None,
        private_key_path: Optional[str] = None,
        private_key: Optional[str] = None,
        base_url: Optional[str] = None,
    ):
        if app_id is None:
            app_id = os.environ.get("DX_CONFIG_APP_ID")

        if private_key_path is None:
            private_key_path = os.environ.get("DX_CONFIG_PRIVATE_KEY_PATH")

        if private_key is None:
            private_key = os.environ.get("DX_CONFIG_PRIVATE_KEY")

        if base_url is None:
            base_url = "https://app.movementinfrastructure.org/api/v1/{}"

        self.app_id = app_id
        self.base_url = base_url

        if private_key is not None:
            self._private_key = private_key
        elif private_key_path is not None:
            with open(private_key_path, "rb") as f:
                self._private_key = f.read()
        else:
            raise ValueError("Must provide either private_key or private_key_path")

        self.auth_token = self.create_auth_token()
        # logger.info(f"created token {self.auth_token}")
        self.auth_header = f"Bearer {self.auth_token}"

        self.mode = "sync"

        self._session = None
        self._asession = None
        self._installations = None

    def session_config(self):
        return dict(
            headers={
                "Authorization": self.auth_header,
                "Content-Type": "application/json",
                "User-Agent": self.useragent(),
            },
            timeout=30,
        )

    @property
    def session(self):
        if self._session:
            # logger.info(self._session.headers.get("Authorization"))
            if self._session.headers.get("Authorization") != self.auth_header:
                self._session.headers["Authorization"] = self.auth_header

        if not self._session or self._session.is_closed:
            self._session = httpx.Client(**self.session_config())
        return self._session

    @property
    def asession(self):
        if self._asession:
            if self._asession.headers.get("Authorization") != self.auth_header:
                self._asession.headers["Authorization"] = self.auth_header
        if not self._asession or self._asession.is_closed:
            self._asession = httpx.AsyncClient(**self.session_config())
        return self._asession

    def create_auth_token(self):
        issued_time = datetime.datetime.now(tz=datetime.timezone.utc)

        token = jwt.encode(
            {
                "iss": self.app_id,
                "aud": "movementconsole",
                "MovementAppId": self.app_id,
                "exp": issued_time + datetime.timedelta(hours=1),
                "iat": issued_time,
                "nbf": issued_time,
            },
            self._private_key,
            algorithm="RS256",
        )

        # logger.info(f"created token {token}")

        return token

    @validate_call(validate_return=True)
    def whoami(self) -> WhoAmI:
        response = self.session.get(self.base_url.format("auth/me"))
        response.raise_for_status()
        return response.json()

    @validate_call(validate_return=True)
    async def whoami_async(self) -> WhoAmI:
        async with self.asession as session:
            response = await session.get(self.base_url.format("auth/me"))
            response.raise_for_status()
            return response.json()

    @property
    def installations(self):
        if not self._installations:
            self._installations = InstallationManager(client=self)
        return self._installations

    def installation(
        self,
        installation: Installation | None = None,
        name: str | None = None,
        install_id: int | None = None,
        workspace_key: str | None = None,
    ):
        if not installation:
            installation = self.installations.find(name=name, install_id=install_id)

        return _InstallationContext(client=self, installation=installation)

    @validate_call(validate_return=True)
    def get_installations(self) -> list[Installation]:
        response = self.session.get(self.base_url.format("apps/me/installations"))
        response.raise_for_status()
        data = response.json()
        return data.get("data", [])

    @validate_call(validate_return=True)
    async def get_installations_async(self) -> list[Installation]:
        async with self.asession as session:
            response = await session.get(self.base_url.format("apps/me/installations"))
            response.raise_for_status()
            data = response.json()
            return data.get("data", [])

    @validate_call(validate_return=True)
    def get_client_token(self, installation_id: str, workspace_key: str) -> ClientToken:
        resp = self.session.post(
            self.base_url.format("auth/clientToken"),
            json={
                "tokenType": "appInstallation",
                "workspaceKey": workspace_key,
                "installationId": installation_id,
                "permissions": [],
            },
        )
        resp.raise_for_status()
        return resp.json()

    @validate_call(validate_return=True)
    async def get_client_token_async(self, installation_id: str, workspace_key: str) -> ClientToken:
        async with self.asession as session:
            resp = await session.post(
                self.base_url.format("auth/clientToken"),
                json={
                    "tokenType": "appInstallation",
                    "workspaceKey": workspace_key,
                    "installationId": installation_id,
                    "permissions": [],
                },
            )
            resp.raise_for_status()
            return resp.json()


class InstallationManager:
    def __init__(self, client: DX):
        self.client = client
        self._installations = None

    def __iter__(self):
        if self._installations is None:
            self._installations = self.client.get_installations()
        return iter(self._installations)

    async def __aiter__(self):
        if self._installations is None:
            self._installations = await self.client.get_installations_async()
        for installation in self._installations:
            yield installation

    @validate_call
    def find(
        self,
        name: str | None = None,
        install_id: int | None = None,
    ) -> Installation:
        if not any([name, install_id]):
            raise ValueError(
                "Must provide one of the following: name, install_id, app_id"
            )
        for installation in self:
            if any(
                [
                    name and installation.name == name,
                    install_id and installation.installation_id == install_id,
                ]
            ):
                return installation
        raise KeyError("Installation not found")

    @validate_call
    async def find_async(
        self, name: str | None = None, install_id: int | None = None
    ) -> Installation:
        async for installation in self:
            if any(
                [
                    name and installation.name == name,
                    install_id and installation.installation_id == install_id,
                ]
            ):
                return installation
        raise KeyError("Installation not found")

    def get(self, id: int) -> Installation:
        for installation in self:
            if installation.installation_id == id:
                return installation
        raise KeyError("Installation not found")

    async def get_async(self, id: int) -> Installation:
        async for installation in self:
            if installation.installation_id == id:
                return installation
        raise KeyError("Installation not found")


class _InstallationContext:
    def __init__(self, client: DX, installation: Installation):
        self.client = client
        self.installation = installation
        self.ctx = None
        self._ctx_token = None

    def __enter__(self):
        self.client.mode = "sync"
        self.ctx = SyncInstallationContext(self.client, self.installation)
        result = self.ctx.__enter__()
        return result

    def __exit__(self, exc_type, exc_value, traceback):
        result = None
        if self.ctx:
            result = self.ctx.__exit__(exc_type, exc_value, traceback)
        return result

    async def __aenter__(self):
        self.client.mode = "async"
        self.ctx = AsyncInstallationContext(self.client, self.installation)
        result = await self.ctx.__aenter__()
        return result

    async def __aexit__(self, exc_type, exc_value, traceback):
        if self.ctx:
            await self.ctx.__aexit__(exc_type, exc_value, traceback)

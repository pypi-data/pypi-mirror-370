import contextvars
import csv
import datetime
import io
import os
from abc import ABC, abstractmethod
from typing import Annotated, AsyncGenerator, Literal, Optional
from uuid import UUID

import aiofiles
import httpx
import jwt
from loguru import logger

from ._models import WhoAmI, Installation, ClientToken
from ._protocols import DXProtocol
from ._dataset import DatasetManager, AsyncDatasetManager


class SyncInstallationContext:
    _client_token: ClientToken
    client: DXProtocol
    installation: Installation
    session: httpx.Client

    def __init__(self, client: DXProtocol, installation: Installation):
        self.client = client
        self.installation = installation
        self._previous_auth_header = None
        self._client_token = None
        self._datasets = None

    @property
    def session(self):
        return self.client.session

    @property
    def datasets(self):
        if self._datasets is None:
            raise ValueError("Must enter context manager first")
        return self._datasets

    def _authenticate_installation(self):
        self._client_token = self.client.get_client_token(
            str(self.installation.installation_id),
            self.installation.workspace_key
        )
        self._previous_auth_header = self.client.auth_header
        self.client.auth_header = f"Bearer {self._client_token.token}"

    def _authentication_reset(self):
        self.client.auth_header = self._previous_auth_header

    def __enter__(self):
        self._authenticate_installation()
        self._datasets = DatasetManager(self)
        if self.session._state == httpx._client.ClientState.UNOPENED:
            self.session.__enter__()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self._authentication_reset()
        self.session.__exit__(exc_type, exc_value, traceback)


class AsyncInstallationContext:
    _client_token: ClientToken
    client: DXProtocol
    installation: Installation
    session: httpx.AsyncClient

    def __init__(self, client: DXProtocol, installation: Installation):
        self.client = client
        self.installation = installation
        self._client_token = None
        self._datasets = None

    @property
    def session(self):
        return self.client.asession

    @property
    def datasets(self):
        if self._datasets is None:
            raise ValueError("Must enter context manager first")
        return self._datasets

    async def __aenter__(self):
        await self._authenticate_installation()
        if self.session._state == httpx._client.ClientState.UNOPENED:
            await self.session.__aenter__()
        self._datasets = AsyncDatasetManager(self)
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        self._authentication_reset()
        await self.session.__aexit__(exc_type, exc_value, traceback)

    async def _authenticate_installation(self):
        self._client_token = await self.client.get_client_token_async(
            str(self.installation.movement_app_installation_id),
            self.installation.workspace_key
        )
        self._previous_auth_header = self.client.auth_header
        self.client.auth_header = f"Bearer {self._client_token.token}"

    def _authentication_reset(self):
        self.client.auth_header = self._previous_auth_header

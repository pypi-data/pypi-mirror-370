import typing

from pydantic import (
    Field,
    computed_field,
    model_validator,
    SecretStr,
    # AliasChoices,
    # AmqpDsn,
    # BaseModel,
    # Field,
    # ImportString,
    # PostgresDsn,
    # RedisDsn,
)

from pydantic_settings import BaseSettings, SettingsConfigDict


class DXConfig(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="DX_CONFIG_")

    app_id: typing.Annotated[
        str | None, Field(..., title="App ID", description="App ID", env="APP_ID")
    ] = None

    token_aud: typing.Annotated[
        typing.Literal["movementconsole"], Field(repr=False)
    ] = "movementconsole"

    application_token: typing.Annotated[
        str | None,
        Field(
            ...,
            title="Application Token",
            description="Application Token",
            repr=False,
        ),
    ] = None

    private_key_path: typing.Annotated[
        str | None,
        Field(
            ...,
            title="Private Key Path",
            description="Private Key Path",
            env="PRIVATE_KEY_PATH",
            repr=False,
        ),
    ] = None

    private_key_str: typing.Annotated[
        SecretStr | None,
        Field(
            ...,
            title="Private Key",
            description="Private Key",
            env="PRIVATE_KEY",
            repr=False,
        ),
    ] = None

    @model_validator(mode="after")
    def _validate_private_key(self):
        if not self.private_key_str and not self.private_key_path:
            raise ValueError("Either private_key_path or private_key_str must be set")
        if not self.app_id:
            raise ValueError("app_id must be set")
        return self
        # if not data.get("private_key_str") or data.get("private_key_path"):
        #     raise ValueError("Either private_key_path or private_key_str must be set")
        # return data

    def get_private_key(self) -> str:
        if self.private_key_str:
            return self.private_key_str.get_secret_value()
        if self.private_key_path:
            with open(self.private_key_path) as f:
                self.private_key_str = f.read()
                return self.private_key_str
        raise ValueError("Either private_key_path or private_key_str must be set")

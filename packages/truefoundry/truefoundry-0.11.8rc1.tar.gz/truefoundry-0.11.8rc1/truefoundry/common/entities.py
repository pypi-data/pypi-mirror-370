import time
from typing import Optional

import jwt
from typing_extensions import NotRequired, TypedDict

from truefoundry.pydantic_v1 import BaseModel, Field, NonEmptyStr, validator


class UserInfo(BaseModel):
    class Config:
        allow_population_by_field_name = True
        allow_mutation = False

    user_id: NonEmptyStr
    email: Optional[str] = None
    tenant_name: NonEmptyStr = Field(alias="tenantName")


class _DecodedToken(TypedDict):
    tenantName: str
    exp: int
    username: NotRequired[str]
    email: NotRequired[str]


def _user_slug(decoded_token: _DecodedToken) -> str:
    return (
        decoded_token.get("username")
        or decoded_token.get("email")
        or "--user-slug-missing--"
    )


class Token(BaseModel):
    access_token: NonEmptyStr = Field(alias="accessToken", repr=False)
    refresh_token: Optional[NonEmptyStr] = Field(alias="refreshToken", repr=False)
    decoded_value: Optional[_DecodedToken] = Field(exclude=True, repr=False)

    class Config:
        allow_population_by_field_name = True
        allow_mutation = False

    @validator("decoded_value", always=True, pre=True)
    def _decode_jwt(cls, v, values, **kwargs) -> _DecodedToken:
        access_token = values["access_token"]
        return jwt.decode(
            access_token,
            options={
                "verify_signature": False,
                "verify_aud": False,
                "verify_exp": False,
            },
        )

    @property
    def tenant_name(self) -> str:
        assert self.decoded_value is not None
        return self.decoded_value["tenantName"]

    @property
    def exp(self) -> int:
        assert self.decoded_value is not None
        return self.decoded_value["exp"]

    def is_going_to_be_expired(self, buffer_in_seconds: int = 120) -> bool:
        assert self.decoded_value is not None
        return (self.exp - time.time()) < buffer_in_seconds

    def to_user_info(self) -> UserInfo:
        assert self.decoded_value is not None
        return UserInfo(
            user_id=_user_slug(self.decoded_value),
            email=self.decoded_value["email"]
            if "email" in self.decoded_value
            else None,
            tenant_name=self.tenant_name,
        )


class CredentialsFileContent(BaseModel):
    class Config:
        allow_mutation = False

    access_token: NonEmptyStr = Field(repr=False)
    refresh_token: Optional[NonEmptyStr] = Field(repr=False)
    host: NonEmptyStr

    def to_token(self) -> Token:
        return Token(access_token=self.access_token, refresh_token=self.refresh_token)


class TenantInfo(BaseModel):
    class Config:
        allow_population_by_field_name = True
        allow_mutation = False

    tenant_name: NonEmptyStr = Field(alias="tenantName")
    auth_server_url: str


class PythonSDKConfig(BaseModel):
    class Config:
        allow_population_by_field_name = True
        allow_mutation = False

    min_version: str = Field(alias="minVersion")
    truefoundry_cli_min_version: str = Field(alias="truefoundryCliMinVersion")
    use_sfy_server_auth_apis: Optional[bool] = Field(
        alias="useSFYServerAuthAPIs", default=False
    )
    python_build_default_image_tag: str = Field(
        alias="pythonBuildDefaultImageTag", default="3.11"
    )


class DeviceCode(BaseModel):
    class Config:
        allow_population_by_field_name = True
        allow_mutation = False

    user_code: str = Field(alias="userCode")
    device_code: str = Field(alias="deviceCode")
    verification_url: Optional[str] = Field(alias="verificationURI")
    complete_verification_url: Optional[str] = Field(alias="verificationURIComplete")
    expires_in_seconds: int = Field(alias="expiresInSeconds", default=60)
    interval_in_seconds: int = Field(alias="intervalInSeconds", default=1)
    message: Optional[str] = Field(alias="message")

    def get_user_clickable_url(self, auth_host: str) -> str:
        return f"{auth_host}/authorize/device?userCode={self.user_code}"

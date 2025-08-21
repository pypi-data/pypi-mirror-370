import enum
import os
from pathlib import Path
from typing import Any, Dict, Optional

from truefoundry.pydantic_v1 import BaseSettings, Field, SecretStr

TFY_CONFIG_DIR = Path.home() / ".truefoundry"
CREDENTIAL_FILEPATH = TFY_CONFIG_DIR / "credentials.json"

# These keys are kept separately because we use them in error messages and some checks
TFY_HOST_ENV_KEY = "TFY_HOST"
TFY_API_KEY_ENV_KEY = "TFY_API_KEY"
TFY_DEBUG_ENV_KEY = "TFY_DEBUG"
TFY_INTERNAL_ENV_KEY = "TFY_INTERNAL"

TFY_INTERNAL_SIGNED_URL_SERVER_HOST_ENV_KEY = "TFY_INTERNAL_SIGNED_URL_SERVER_HOST"
TFY_INTERNAL_SIGNED_URL_SERVER_TOKEN_ENV_KEY = "TFY_INTERNAL_SIGNED_URL_SERVER_TOKEN"

# === Global Constants for OpenAI Integration ===
OPENAI_API_KEY_KEY = "OPENAI_API_KEY"
OPENAI_MODEL_KEY = "OPENAI_MODEL"

# === Ask Command Specific Environment Variables for TrueFoundry ===
TFY_ASK_OPENAI_API_KEY_KEY = "TFY_ASK_OPENAI_API_KEY"
TFY_ASK_OPENAI_BASE_URL_KEY = "TFY_ASK_OPENAI_BASE_URL"
TFY_ASK_MODEL_NAME_KEY = "TFY_ASK_OPENAI_MODEL"


class PythonPackageManager(str, enum.Enum):
    PIP = "pip"
    UV = "uv"


class TrueFoundrySdkEnv(BaseSettings):
    # Note: Every field in this class should have a default value
    # Never expect the user to set these values

    # These two are not meant to be used directly. See the TFY_HOST and TFY_API_KEY properties below
    TFY_HOST_: Optional[str] = Field(default=None, env=TFY_HOST_ENV_KEY)
    TFY_API_KEY_: Optional[SecretStr] = Field(default=None, env=TFY_API_KEY_ENV_KEY)

    # Internal Signed URL Server
    TFY_INTERNAL_SIGNED_URL_SERVER_HOST: Optional[str] = Field(
        default=None, env=TFY_INTERNAL_SIGNED_URL_SERVER_HOST_ENV_KEY
    )
    TFY_INTERNAL_SIGNED_URL_SERVER_TOKEN: Optional[str] = Field(
        default=None, env=TFY_INTERNAL_SIGNED_URL_SERVER_TOKEN_ENV_KEY
    )
    TFY_INTERNAL_SIGNED_URL_SERVER_MAX_TIMEOUT: int = 5  # default: 5 seconds
    TFY_INTERNAL_SIGNED_URL_SERVER_DEFAULT_TTL: int = 3600  # default: 1 hour
    TFY_INTERNAL_MULTIPART_UPLOAD_FINALIZE_SIGNED_URL_TIMEOUT: int = (
        24 * 60 * 60
    )  # default: 24 hour
    TFY_INTERNAL_SIGNED_URL_REQUEST_TIMEOUT: int = 3600  # default: 1 hour
    TFY_INTERNAL_SIGNED_URL_CLIENT_LOG_LEVEL: str = "WARNING"

    # Artifacts
    TFY_ARTIFACTS_DOWNLOAD_CHUNK_SIZE_BYTES: int = 100 * 1000 * 1000
    TFY_ARTIFACTS_DOWNLOAD_MAX_WORKERS: int = max(min(32, (os.cpu_count() or 2) * 2), 4)
    TFY_ARTIFACTS_UPLOAD_MAX_WORKERS: int = max(min(32, (os.cpu_count() or 2) * 2), 4)
    TFY_ARTIFACTS_DISABLE_MULTIPART_UPLOAD: bool = False
    TFY_ARTIFACTS_DOWNLOAD_FSYNC_CHUNKS: bool = False

    # Fo customizing the python image used for building via PythonBuild
    TFY_PYTHONBUILD_PYTHON_IMAGE_REPO: str = "public.ecr.aws/docker/library/python"

    # TODO(gw): Use another image with more linient rate limits
    TFY_SPARK_BUILD_SPARK_IMAGE_REPO: str = "public.ecr.aws/bitnami/spark"

    TFY_TASK_PYSPARK_BUILD_SPARK_IMAGE_REPO: str = "public.ecr.aws/bitnami/spark"

    # For local development, this enables futher configuration via _TFYServersConfig
    TFY_CLI_LOCAL_DEV_MODE: bool = False

    TFY_PYTHON_BUILD_PACKAGE_MANAGER: PythonPackageManager = PythonPackageManager.UV
    TFY_PYTHON_BUILD_UV_IMAGE_URI: str = "ghcr.io/astral-sh/uv:latest"

    # Global Constants for OpenAI Integration
    OPENAI_API_KEY: Optional[str] = Field(default=None, env=OPENAI_API_KEY_KEY)
    OPENAI_MODEL: Optional[str] = Field(default=None, env=OPENAI_MODEL_KEY)

    # Ask Command Specific Environment Variables for TrueFoundry
    TFY_ASK_OPENAI_API_KEY: Optional[str] = Field(
        default=None, env=TFY_ASK_OPENAI_API_KEY_KEY
    )
    TFY_ASK_OPENAI_BASE_URL: Optional[str] = Field(
        default=None, env=TFY_ASK_OPENAI_BASE_URL_KEY
    )
    TFY_ASK_MODEL_NAME: Optional[str] = Field(default=None, env=TFY_ASK_MODEL_NAME_KEY)
    TFY_ASK_GENERATION_PARAMS: Dict[str, Any] = Field(
        default_factory=lambda: {"temperature": 0.0, "top_p": 1, "max_tokens": 4096}
    )
    TFY_ASK_SYSTEM_PROMPT_NAME: str = Field(default="tfy-ask-k8s-prompt")
    TFY_INTERNAL_ASK_CONFIG_OVERRIDE_FILE: Optional[str] = Field(default=None)

    # This is a hack to fresh read the env vars because people can end up importing this file
    # before setting the correct env vars. E.g. in notebook environments.
    @property
    def TFY_HOST(self) -> Optional[str]:
        self.__init__()
        return self.TFY_HOST_

    @property
    def TFY_API_KEY(self) -> Optional[SecretStr]:
        self.__init__()
        return self.TFY_API_KEY_


ENV_VARS = TrueFoundrySdkEnv()
API_SERVER_RELATIVE_PATH = "api/svc"
MLFOUNDRY_SERVER_RELATIVE_PATH = "api/ml"
VERSION_PREFIX = "v1"
SERVICEFOUNDRY_CLIENT_MAX_RETRIES = 2

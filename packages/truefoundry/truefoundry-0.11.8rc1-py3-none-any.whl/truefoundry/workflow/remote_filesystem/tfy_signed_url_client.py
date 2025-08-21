# file: client.py
import io
import os
from enum import Enum
from typing import Any, Dict, List, Optional, Union
from urllib.parse import urlencode, urljoin

from requests.exceptions import RequestException

from truefoundry.common.constants import (
    ENV_VARS,
    TFY_INTERNAL_SIGNED_URL_SERVER_HOST_ENV_KEY,
    TFY_INTERNAL_SIGNED_URL_SERVER_TOKEN_ENV_KEY,
)
from truefoundry.common.request_utils import requests_retry_session
from truefoundry.common.storage_provider_utils import MultiPartUploadStorageProvider
from truefoundry.pydantic_v1 import BaseModel, Field
from truefoundry.workflow.remote_filesystem.logger import log_time, logger

LOG_PREFIX = "[tfy][fs]"
DEFAULT_TTL = ENV_VARS.TFY_INTERNAL_SIGNED_URL_SERVER_DEFAULT_TTL
MAX_TIMEOUT = ENV_VARS.TFY_INTERNAL_SIGNED_URL_SERVER_MAX_TIMEOUT
REQUEST_TIMEOUT = ENV_VARS.TFY_INTERNAL_SIGNED_URL_REQUEST_TIMEOUT
MULTIPART_UPLOAD_FINALIZE_SIGNED_URL_TIMEOUT = (
    ENV_VARS.TFY_INTERNAL_MULTIPART_UPLOAD_FINALIZE_SIGNED_URL_TIMEOUT
)


class SignedURLAPIResponseDto(BaseModel):
    uri: str
    signed_url: str
    headers: Optional[Dict[str, Any]] = None


class SignedURLIsDirectoryAPIResponseDto(BaseModel):
    is_directory: bool = Field(..., alias="isDirectory")


class SignedURLExistsAPIResponseDto(BaseModel):
    exists: bool


class PartSignedUrl(BaseModel):
    partNumber: int
    signedUrl: str


class SignedURLMultipartUploadAPIResponseDto(BaseModel):
    uploadId: str
    partSignedUrls: List[PartSignedUrl]
    finalizeSignedUrl: str
    storageProvider: MultiPartUploadStorageProvider


class FileInfo(BaseModel):
    path: str
    is_directory: bool = Field(..., alias="isDirectory")
    bytes: Optional[int] = None
    signed_url: Optional[str] = None


class PagedList(BaseModel):
    items: List[FileInfo]
    token: Optional[str] = None


class SignedURLServerEndpoint(str, Enum):
    """Enumeration for Signed URL Server endpoints."""

    READ = "/v1/signed-uri/read"
    WRITE = "/v1/signed-uri/write"
    EXISTS = "/v1/exists"
    IS_DIRECTORY = "/v1/is-dir"
    LIST_FILES = "/v1/list-files"
    CREATE_MUTLIPART_UPLOAD = "/v1/multipart-upload"


class SignedURLClient:
    """Client to interact with the Signed URL Server for file operations."""

    def __init__(
        self,
        base_url: Optional[str] = None,
        token: Optional[str] = None,
        ttl: int = DEFAULT_TTL,
        max_retries: int = 3,
        retry_backoff_factor: float = 0.3,
    ):
        """Initialize the SignedURLClient."""
        # Set the base URL and token from the environment variables
        self.base_url = base_url or ENV_VARS.TFY_INTERNAL_SIGNED_URL_SERVER_HOST
        self.token = token or ENV_VARS.TFY_INTERNAL_SIGNED_URL_SERVER_TOKEN
        self.signed_url_server_headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
        }

        if not self.base_url or not self.token:
            raise ValueError(
                f"Set `base_url` and `token` or define env vars "
                f"{TFY_INTERNAL_SIGNED_URL_SERVER_HOST_ENV_KEY} and "
                f"{TFY_INTERNAL_SIGNED_URL_SERVER_TOKEN_ENV_KEY}"
            )

        # Set the TTL, max retries, and backoff factor
        self.ttl = ttl
        self.max_retries: int = max_retries
        self.retry_backoff_factor: float = retry_backoff_factor
        self.session = requests_retry_session(
            retries=self.max_retries, backoff_factor=self.retry_backoff_factor
        )

    @log_time(prefix=LOG_PREFIX)
    def _make_request(
        self,
        endpoint: str,
        method: str = "GET",
        payload: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Internal method to handle requests to the signed URL server."""
        url = urljoin(self.base_url, endpoint)
        try:
            response = self.session.request(
                method, url, headers=headers, json=payload, timeout=MAX_TIMEOUT
            )
            response.raise_for_status()
            return response.json()
        except RequestException as e:
            raise RuntimeError(f"Error during request to {url}: {e}") from e

    @log_time(prefix=LOG_PREFIX)
    def _make_server_api_call(
        self,
        endpoint: SignedURLServerEndpoint,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Get a signed URL for the specified operation and URI."""
        query_string = urlencode(params or {})
        endpoint_with_params = f"{endpoint.value}?{query_string}"
        return self._make_request(
            endpoint=endpoint_with_params, method="GET", payload=None, headers=headers
        )

    @log_time(prefix=LOG_PREFIX)
    def _upload_data(
        self,
        signed_url: str,
        data: Union[bytes, io.BufferedReader],
        headers: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Upload data to the specified storage path using a signed URL.

        Args:
            signed_url: str: The signed URL to upload the data to.
            data: Bytes or IO: The data to upload.
        """
        if isinstance(data, io.BufferedReader):
            if os.fstat(data.fileno()).st_size == 0:
                data = b""
        try:
            headers = headers or {}
            headers["Content-Type"] = "application/octet-stream"
            response = self.session.put(
                url=signed_url,
                headers=headers,
                data=data,
                timeout=REQUEST_TIMEOUT,
            )
            response.raise_for_status()
        except Exception as e:
            raise RuntimeError(f"Failed to upload data: {e}") from e

    @log_time(prefix=LOG_PREFIX)
    def upload_from_bytes(self, data: bytes, storage_uri: str) -> str:
        """Upload bytes to the specified storage path using a signed URL."""
        signed_object = self._make_server_api_call(
            endpoint=SignedURLServerEndpoint.WRITE,
            params={"uri": storage_uri, "expiryInSeconds": self.ttl},
            headers=self.signed_url_server_headers,
        )
        pre_signed_object_dto = SignedURLAPIResponseDto.parse_obj(signed_object)
        self._upload_data(
            signed_url=pre_signed_object_dto.signed_url,
            data=data,
            headers=pre_signed_object_dto.headers,
        )
        return storage_uri

    @log_time(prefix=LOG_PREFIX)
    def upload(self, file_path: str, storage_uri: str) -> str:
        """Upload a file to the specified storage path using a signed URL."""
        logger.info(f"{LOG_PREFIX} Uploading {file_path} to {storage_uri}")
        response = self._make_server_api_call(
            endpoint=SignedURLServerEndpoint.WRITE,
            params={"uri": storage_uri, "expiryInSeconds": self.ttl},
            headers=self.signed_url_server_headers,
        )
        pre_signed_object_dto = SignedURLAPIResponseDto.parse_obj(response)
        with open(file_path, "rb") as file:
            self._upload_data(
                signed_url=pre_signed_object_dto.signed_url,
                data=file,
                headers=pre_signed_object_dto.headers,
            )
        return storage_uri

    def create_multipart_upload(
        self, storage_uri: str, num_parts: int
    ) -> SignedURLMultipartUploadAPIResponseDto:
        response = self._make_server_api_call(
            endpoint=SignedURLServerEndpoint.CREATE_MUTLIPART_UPLOAD,
            params={
                "path": storage_uri,
                "numParts": num_parts,
                "partExpiryInSeconds": self.ttl,
                "finalizationExpiryInSeconds": MULTIPART_UPLOAD_FINALIZE_SIGNED_URL_TIMEOUT,
            },
            headers=self.signed_url_server_headers,
        )

        return SignedURLMultipartUploadAPIResponseDto.parse_obj(response)

    @log_time(prefix=LOG_PREFIX)
    def _download_file(
        self,
        signed_url: str,
        local_path: Optional[str] = None,
        headers: Optional[Dict[str, Any]] = None,
    ) -> Optional[bytes]:
        """Common method to download a file using a signed URL."""
        try:
            if headers is None:
                headers = {"Content-Type": "application/octet-stream"}
            else:
                headers["Content-Type"] = "application/octet-stream"
            response = self.session.get(
                signed_url,
                stream=True,
                headers=headers,
                timeout=REQUEST_TIMEOUT,
            )
            response.raise_for_status()
            if local_path:
                with open(local_path, "wb") as file:
                    for chunk in response.iter_content(chunk_size=8192):
                        file.write(chunk)
                return None
            return response.content
        except RequestException as e:
            raise RuntimeError(f"Failed to download file from {signed_url}: {e}") from e

    @log_time(prefix=LOG_PREFIX)
    def download(self, storage_uri: str, local_path: str) -> Optional[str]:
        """Download a file from the specified storage path to a local path using a signed URL."""
        logger.info(f"{LOG_PREFIX} Downloading {storage_uri} to {local_path}")
        response = self._make_server_api_call(
            endpoint=SignedURLServerEndpoint.READ,
            params={"uri": storage_uri, "expiryInSeconds": self.ttl},
            headers=self.signed_url_server_headers,
        )
        presigned_object = SignedURLAPIResponseDto.parse_obj(response)
        self._download_file(
            signed_url=presigned_object.signed_url,
            local_path=local_path,
            headers=presigned_object.headers,
        )
        return local_path

    @log_time(prefix=LOG_PREFIX)
    def download_to_bytes(self, storage_uri: str) -> Optional[bytes]:
        """Download a file from the specified storage path and return it as bytes."""
        response = self._make_server_api_call(
            endpoint=SignedURLServerEndpoint.READ,
            params={"uri": storage_uri, "expiryInSeconds": self.ttl},
            headers=self.signed_url_server_headers,
        )
        presigned_object = SignedURLAPIResponseDto.parse_obj(response)
        return self._download_file(
            signed_url=presigned_object.signed_url, headers=presigned_object.headers
        )

    @log_time(prefix=LOG_PREFIX)
    def exists(self, uri: str) -> bool:
        """Check if a file exists at the specified path."""
        response = self._make_server_api_call(
            endpoint=SignedURLServerEndpoint.EXISTS,
            params={"uri": uri},
            headers=self.signed_url_server_headers,
        )
        return SignedURLExistsAPIResponseDto.parse_obj(response).exists

    @log_time(prefix=LOG_PREFIX)
    def is_directory(self, uri: str) -> bool:
        """Check if the specified URI is a directory."""
        response = self._make_server_api_call(
            endpoint=SignedURLServerEndpoint.IS_DIRECTORY,
            params={"path": uri},
            headers=self.signed_url_server_headers,
        )
        is_directory = SignedURLIsDirectoryAPIResponseDto.parse_obj(
            response
        ).is_directory
        logger.info(f"{LOG_PREFIX} Path {uri} is a directory: {is_directory}")
        return is_directory

    @log_time(prefix=LOG_PREFIX)
    def list_files(
        self, path: str, detail: bool = False, max_results: int = 1000
    ) -> Union[List[FileInfo], List[str]]:
        """List files in the specified directory."""
        token = ""
        items: List[FileInfo] = []
        # Fetch all files in the specified path, in pages of max_results
        while True:
            response = self._make_server_api_call(
                endpoint=SignedURLServerEndpoint.LIST_FILES,
                params={"path": path, "maxResults": max_results, "pageToken": token},
                headers=self.signed_url_server_headers,
            )
            response_obj = PagedList.parse_obj(response)
            items.extend(response_obj.items)
            token = response_obj.token
            if not token:
                break

        # Return the items or paths based on the detail flag
        return items if detail else [item.path for item in items]

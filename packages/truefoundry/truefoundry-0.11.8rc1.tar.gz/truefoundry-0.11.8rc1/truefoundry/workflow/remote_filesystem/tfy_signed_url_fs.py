# file: tfy_signed_url_fs.py
# pylint: disable=W0223
import io
import os
from concurrent.futures import FIRST_EXCEPTION, Future, ThreadPoolExecutor, wait
from pathlib import Path
from threading import Event
from typing import List, Optional, Tuple

from fsspec.spec import DEFAULT_CALLBACK, AbstractBufferedFile, AbstractFileSystem

from truefoundry.common.constants import ENV_VARS
from truefoundry.common.storage_provider_utils import (
    MultiPartUpload,
    SignedURL,
    _FileMultiPartInfo,
    decide_file_parts,
    s3_compatible_multipart_upload,
)
from truefoundry.workflow.remote_filesystem.logger import log_time, logger
from truefoundry.workflow.remote_filesystem.tfy_signed_url_client import (
    LOG_PREFIX,
    SignedURLClient,
    SignedURLMultipartUploadAPIResponseDto,
)

MULTIPART_SUPPORTED_PROVIDERS = ["s3"]


def _add_file_for_upload(
    local_file: str,
    remote_path: str,
    files_for_normal_upload: List[Tuple[str, str, _FileMultiPartInfo]],
    files_for_multipart_upload: List[Tuple[str, str, _FileMultiPartInfo]],
    multipart_upload_allowed: bool,
):
    multipart_info = decide_file_parts(local_file, multipart_upload_allowed)
    if multipart_info.num_parts == 1:
        files_for_normal_upload.append((remote_path, local_file, multipart_info))
    else:
        files_for_multipart_upload.append((remote_path, local_file, multipart_info))


class SignedURLFileSystem(AbstractFileSystem):
    def __init__(
        self, base_url: Optional[str] = None, token: Optional[str] = None, **kwargs
    ):
        super().__init__()
        base_url = base_url or ENV_VARS.TFY_INTERNAL_SIGNED_URL_SERVER_HOST
        token = token or ENV_VARS.TFY_INTERNAL_SIGNED_URL_SERVER_TOKEN
        self.client = SignedURLClient(base_url, token)

    @log_time(prefix=LOG_PREFIX)
    def exists(self, path, **kwargs):
        """Check if a file exists at the given path."""
        return self.client.exists(path)

    @log_time(prefix=LOG_PREFIX)
    def get(
        self,
        rpath,
        lpath,
        recursive=False,
        callback=DEFAULT_CALLBACK,
        maxdepth=None,
        **kwargs,
    ):
        """Get file(s) to local"""
        # TODO: Add support for ThreadPoolExecutor here
        # TODO: Add support for async download
        # TODO: Do a proper error handling here
        if self.isdir(rpath):
            if not recursive:
                raise ValueError(
                    f"{rpath} is a directory, but recursive is not enabled."
                )

            # Handle recursive download
            files = self.ls(rpath, detail=True)

            for file_info in files:
                file_path = file_info.path.rstrip("/").rsplit("/")[-1]

                is_directory = file_info.is_directory
                # Construct the relative path for local download
                relative_path = rpath.rstrip("/") + "/" + file_path
                target_local_path = lpath.rstrip("/") + "/" + file_path

                if is_directory:
                    # If it's a directory, create the directory locally
                    Path(target_local_path).mkdir(parents=True, exist_ok=True)
                    relative_path = relative_path + "/"
                    if recursive:
                        # Recursively download the contents of the directory
                        self.get(
                            relative_path,
                            target_local_path,
                            recursive=True,
                            maxdepth=maxdepth,
                            **kwargs,
                        )
                else:
                    self.client.download(
                        storage_uri=relative_path, local_path=target_local_path
                    )

        else:
            # Ensure the directory exists first
            target_local_path = lpath
            if target_local_path.endswith("/"):
                # If it ends with "/", it's a directory, so create the directory first
                target_local_path = os.path.join(
                    target_local_path, rpath.rsplit("/", 1)[-1]
                )
            # Create the directory for the target file path (common for both cases)
            Path(os.path.dirname(target_local_path)).mkdir(parents=True, exist_ok=True)
            self.client.download(storage_uri=rpath, local_path=target_local_path)

    @log_time(prefix=LOG_PREFIX)
    def put(
        self,
        lpath,
        rpath,
        recursive=False,
        callback=DEFAULT_CALLBACK,
        maxdepth=None,
        **kwargs,
    ):
        files_for_normal_upload: List[Tuple[str, str, _FileMultiPartInfo]] = []
        files_for_multipart_upload: List[Tuple[str, str, _FileMultiPartInfo]] = []
        local_path = Path(lpath)
        multipart_upload_allowed = (
            self.protocol in MULTIPART_SUPPORTED_PROVIDERS
            and not ENV_VARS.TFY_ARTIFACTS_DISABLE_MULTIPART_UPLOAD
        )
        if local_path.is_dir():
            if not recursive:
                raise ValueError(
                    f"{lpath} is a directory, but recursive is set to False."
                )

            # Optionally limit recursion depth
            max_depth = maxdepth if maxdepth is not None else float("inf")

            # Walk through the directory structure
            for root, _, files in os.walk(lpath):
                current_depth = Path(root).relative_to(local_path).parts
                if len(current_depth) > max_depth:
                    continue  # Skip files deeper than the max depth

                rel_dir = Path(root).relative_to(local_path)
                remote_dir = (
                    rpath.rstrip("/")
                    if rel_dir == Path(".")
                    else rpath.rstrip("/") + "/" + str(rel_dir)
                )

                # Upload each file
                for file in files:
                    local_file_path = Path(root) / file
                    remote_file_path = f"{remote_dir}/{file}"
                    _add_file_for_upload(
                        local_file=str(local_file_path),
                        remote_path=str(remote_file_path),
                        files_for_normal_upload=files_for_normal_upload,
                        files_for_multipart_upload=files_for_multipart_upload,
                        multipart_upload_allowed=multipart_upload_allowed,
                    )
        else:
            if rpath.endswith("/"):
                rpath = os.path.join(rpath, local_path.name)
            _add_file_for_upload(
                local_file=str(lpath),
                remote_path=str(rpath),
                files_for_normal_upload=files_for_normal_upload,
                files_for_multipart_upload=files_for_multipart_upload,
                multipart_upload_allowed=multipart_upload_allowed,
            )
        return self._upload(
            files_for_normal_upload=files_for_normal_upload,
            files_for_multipart_upload=files_for_multipart_upload,
        )

    def _upload(
        self,
        files_for_normal_upload: List[Tuple[str, str, _FileMultiPartInfo]],
        files_for_multipart_upload: List[Tuple[str, str, _FileMultiPartInfo]],
    ):
        abort_event = Event()
        with ThreadPoolExecutor(
            max_workers=ENV_VARS.TFY_ARTIFACTS_UPLOAD_MAX_WORKERS
        ) as executor:
            futures: List[Future] = []
            for remote_path, local_path, _ in files_for_normal_upload:
                futures.append(
                    executor.submit(
                        self.client.upload,
                        file_path=local_path,
                        storage_uri=remote_path,
                    )
                )

            done, not_done = wait(futures, return_when=FIRST_EXCEPTION)
            if len(not_done) > 0:
                abort_event.set()
            for future in not_done:
                future.cancel()
            for future in done:
                if future.exception() is not None:
                    raise future.exception()

            for remote_path, local_path, multipart_info in files_for_multipart_upload:
                self._multipart_upload(
                    local_file=local_path,
                    artifact_path=remote_path,
                    multipart_info=multipart_info,
                    executor=executor,
                    abort_event=abort_event,
                )

    def _multipart_upload(
        self,
        local_file: str,
        artifact_path: str,
        multipart_info: _FileMultiPartInfo,
        executor: ThreadPoolExecutor,
        abort_event: Optional[Event] = None,
    ):
        logger.info(
            "Uploading %s to %s using multipart upload",
            local_file,
            artifact_path,
        )

        multipart_upload: SignedURLMultipartUploadAPIResponseDto = (
            self.client.create_multipart_upload(
                storage_uri=artifact_path,
                num_parts=multipart_info.num_parts,
            )
        )
        s3_compatible_multipart_upload(
            multipart_upload=MultiPartUpload(
                storage_provider=multipart_upload.storageProvider,
                part_signed_urls=[
                    SignedURL(signed_url=url.signedUrl)
                    for url in multipart_upload.partSignedUrls
                ],
                s3_compatible_upload_id=multipart_upload.uploadId,
                finalize_signed_url=SignedURL(
                    signed_url=multipart_upload.finalizeSignedUrl
                ),
            ),
            local_file=local_file,
            executor=executor,
            multipart_info=multipart_info,
            abort_event=abort_event,
        )

    @log_time(prefix=LOG_PREFIX)
    def isdir(self, path):
        """Is this entry directory-like?"""
        return self.client.is_directory(path)

    def open(
        self,
        path,
        mode="rb",
        block_size=None,
        cache_options=None,
        compression=None,
        **kwargs,
    ):
        """
        Open a file for reading or writing.
        """
        if "r" in mode:
            # Reading mode
            file_content = self.client.download_to_bytes(path)
            return io.BytesIO(file_content)
        elif "w" in mode or "a" in mode:
            # Writing mode (appending treated as writing)
            buffer = io.BytesIO()
            buffer.seek(0)

            def on_close(buffer=buffer, path=path):
                """
                Callback when file is closed, automatically upload the content.
                """
                buffer.seek(0)
                self.client.upload_from_bytes(buffer.read(), storage_uri=path)

            # Wrapping the buffer to automatically upload on close
            return io.BufferedWriter(buffer, on_close)

    @log_time(prefix=LOG_PREFIX)
    def write(self, path, data, **kwargs):
        """
        Write data to the file at the specified path (this could be tied to open's close).
        """
        if isinstance(data, io.BytesIO):
            data.seek(0)
            content = data.read()
        elif isinstance(data, str):
            content = data.encode()  # Encode to bytes
        else:
            raise ValueError("Unsupported data type for writing")

        # Upload the content to the remote file system
        self.client.upload_from_bytes(content, storage_uri=path)

    @log_time(prefix=LOG_PREFIX)
    def ls(self, path, detail=True, **kwargs):
        """List objects at path."""
        return self.client.list_files(path, detail=detail)


class SignedURLBufferedFile(AbstractBufferedFile):
    """
    Buffered file implementation for Signed URL-based file system.
    # TODO: Need to test this implementation
    """

    def __init__(
        self, fs: SignedURLFileSystem, path: str, mode: str, block_size: int, **kwargs
    ):
        """
        Initialize the buffered file, determining the mode (read/write).
        """
        super().__init__(fs, path, mode, block_size, **kwargs)
        self.buffer = io.BytesIO()
        self.client = fs.client

        if "r" in mode:
            # Download the file content for reading
            file_content = fs.client.download_to_bytes(path)
            self.buffer.write(file_content)
            self.buffer.seek(0)  # Reset buffer after writing content

    def _upload_on_close(self):
        """
        Upload content back to the remote store when the file is closed.
        """
        self.buffer.seek(0)
        self.client.upload_from_bytes(self.buffer.read(), storage_uri=self.path)

    def close(self):
        """
        Close the file, ensuring the content is uploaded for write/append modes.
        """
        if self.writable():
            self._upload_on_close()
        self.buffer.close()
        super().close()

    def _fetch_range(self, start, end):
        """
        Fetch a specific byte range from the file. Useful for large files and range reads.
        """
        self.buffer.seek(start)
        return self.buffer.read(end - start)

    def _upload_chunk(self, final=False):
        """
        Upload a chunk of the file. For larger files, data may be uploaded in chunks.
        """
        if final:
            self._upload_on_close()

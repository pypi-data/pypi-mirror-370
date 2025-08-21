import logging
import math
import mmap
import os
from concurrent.futures import FIRST_EXCEPTION, Future, ThreadPoolExecutor, wait
from enum import Enum
from threading import Event
from typing import List, NamedTuple, Optional

import requests
from rich.progress import Progress
from tqdm.utils import CallbackIOWrapper

from truefoundry.common.constants import ENV_VARS
from truefoundry.common.exceptions import HttpRequestException
from truefoundry.common.request_utils import (
    augmented_raise_for_status,
    cloud_storage_http_request,
)
from truefoundry.pydantic_v1 import BaseModel

logger = logging.getLogger("truefoundry")


class MultiPartUploadStorageProvider(str, Enum):
    S3_COMPATIBLE = "S3_COMPATIBLE"
    AZURE_BLOB = "AZURE_BLOB"


class SignedURL(BaseModel):
    signed_url: str
    path: Optional[str] = None


class MultiPartUpload(BaseModel):
    storage_provider: MultiPartUploadStorageProvider
    part_signed_urls: List[SignedURL]
    s3_compatible_upload_id: Optional[str] = None
    azure_blob_block_ids: Optional[List[str]] = None
    finalize_signed_url: SignedURL


class _FileMultiPartInfo(NamedTuple):
    num_parts: int
    part_size: int
    file_size: int


class _PartNumberEtag(NamedTuple):
    part_number: int
    etag: str


_MIN_BYTES_REQUIRED_FOR_MULTIPART = 100 * 1024 * 1024
# GCP/S3 Maximum number of parts per upload	10,000
# Maximum number of blocks in a block blob 50,000 blocks
# TODO: This number is artificially limited now. Later
# we will ask for parts signed URI in batches rather than in a single
# API Calls:
# Create Multipart Upload (Returns maximum number of parts, size limit of
#                            a single part, upload id for s3 etc )
#   Get me signed uris for first 500 parts
#     Upload 500 parts
#   Get me signed uris for the next 500 parts
#     Upload 500 parts
#   ...
# Finalize the Multipart upload using the finalize signed url returned
# by Create Multipart Upload or get a new one.
_MAX_NUM_PARTS_FOR_MULTIPART = 1000
# Azure Maximum size of a block in a block blob	4000 MiB
# GCP/S3 Maximum size of an individual part in a multipart upload 5 GiB
_MAX_PART_SIZE_BYTES_FOR_MULTIPART = 4 * 1024 * 1024 * 1000


class _CallbackIOWrapperForMultiPartUpload(CallbackIOWrapper):
    def __init__(self, callback, stream, method, length: int):
        self.wrapper_setattr("_length", length)
        super().__init__(callback, stream, method)

    def __len__(self):
        return self.wrapper_getattr("_length")


def _align_part_size_with_mmap_allocation_granularity(part_size: int) -> int:
    modulo = part_size % mmap.ALLOCATIONGRANULARITY
    if modulo == 0:
        return part_size

    part_size += mmap.ALLOCATIONGRANULARITY - modulo
    return part_size


# Can not be less than 5 * 1024 * 1024
_PART_SIZE_BYTES_FOR_MULTIPART = _align_part_size_with_mmap_allocation_granularity(
    10 * 1024 * 1024
)


def decide_file_parts(
    file_path: str,
    multipart_upload_allowed: bool = not ENV_VARS.TFY_ARTIFACTS_DISABLE_MULTIPART_UPLOAD,
    min_file_size_bytes_for_multipart: int = _MIN_BYTES_REQUIRED_FOR_MULTIPART,
) -> _FileMultiPartInfo:
    file_size = os.path.getsize(file_path)
    if not multipart_upload_allowed or file_size < min_file_size_bytes_for_multipart:
        return _FileMultiPartInfo(1, part_size=file_size, file_size=file_size)

    ideal_num_parts = math.ceil(file_size / _PART_SIZE_BYTES_FOR_MULTIPART)
    if ideal_num_parts <= _MAX_NUM_PARTS_FOR_MULTIPART:
        return _FileMultiPartInfo(
            ideal_num_parts,
            part_size=_PART_SIZE_BYTES_FOR_MULTIPART,
            file_size=file_size,
        )

    part_size_when_using_max_parts = math.ceil(file_size / _MAX_NUM_PARTS_FOR_MULTIPART)
    part_size_when_using_max_parts = _align_part_size_with_mmap_allocation_granularity(
        part_size_when_using_max_parts
    )
    if part_size_when_using_max_parts > _MAX_PART_SIZE_BYTES_FOR_MULTIPART:
        raise ValueError(
            f"file {file_path!r} is too big for upload. Multipart chunk"
            f" size {part_size_when_using_max_parts} is higher"
            f" than {_MAX_PART_SIZE_BYTES_FOR_MULTIPART}"
        )
    num_parts = math.ceil(file_size / part_size_when_using_max_parts)
    return _FileMultiPartInfo(
        num_parts, part_size=part_size_when_using_max_parts, file_size=file_size
    )


def _get_s3_compatible_completion_body(multi_parts: List[_PartNumberEtag]) -> str:
    body = "<CompleteMultipartUpload>\n"
    for part in multi_parts:
        body += "  <Part>\n"
        body += f"    <PartNumber>{part.part_number}</PartNumber>\n"
        body += f"    <ETag>{part.etag}</ETag>\n"
        body += "  </Part>\n"
    body += "</CompleteMultipartUpload>"
    return body


def _get_azure_blob_completion_body(block_ids: List[str]) -> str:
    body = "<BlockList>\n"
    for block_id in block_ids:
        body += f"<Uncommitted>{block_id}</Uncommitted> "
    body += "</BlockList>"
    return body


def _file_part_upload(
    url: str,
    file_path: str,
    seek: int,
    length: int,
    file_size: int,
    abort_event: Optional[Event] = None,
    method: str = "put",
    exception_class=HttpRequestException,
):
    def callback(*_, **__):
        if abort_event and abort_event.is_set():
            raise Exception("aborting upload")

    with open(file_path, "rb") as file:
        with mmap.mmap(
            file.fileno(),
            length=min(file_size - seek, length),
            offset=seek,
            access=mmap.ACCESS_READ,
        ) as mapped_file:
            wrapped_file = _CallbackIOWrapperForMultiPartUpload(
                callback, mapped_file, "read", len(mapped_file)
            )
            with cloud_storage_http_request(
                method=method,
                url=url,
                data=wrapped_file,
                exception_class=exception_class,
            ) as response:
                augmented_raise_for_status(response, exception_class=exception_class)
                return response


def s3_compatible_multipart_upload(
    multipart_upload: MultiPartUpload,
    local_file: str,
    multipart_info: _FileMultiPartInfo,
    executor: ThreadPoolExecutor,
    progress_bar: Optional[Progress] = None,
    abort_event: Optional[Event] = None,
    exception_class=HttpRequestException,
):
    abort_event = abort_event or Event()
    parts = []

    if progress_bar:
        multi_part_upload_progress = progress_bar.add_task(
            f"[green]Uploading {local_file}:", start=True
        )

    def upload(part_number: int, seek: int) -> None:
        logger.debug(
            "Uploading part %d/%d of %s",
            part_number,
            multipart_info.num_parts,
            local_file,
        )
        response = _file_part_upload(
            url=multipart_upload.part_signed_urls[part_number].signed_url,
            file_path=local_file,
            seek=seek,
            length=multipart_info.part_size,
            file_size=multipart_info.file_size,
            abort_event=abort_event,
            exception_class=exception_class,
        )
        logger.debug(
            "Uploaded part %d/%d of %s",
            part_number,
            multipart_info.num_parts,
            local_file,
        )
        if progress_bar:
            progress_bar.update(
                multi_part_upload_progress,
                advance=multipart_info.part_size,
                total=multipart_info.file_size,
            )
        etag = response.headers["ETag"]
        parts.append(_PartNumberEtag(etag=etag, part_number=part_number + 1))

    futures: List[Future] = []
    for part_number, seek in enumerate(
        range(0, multipart_info.file_size, multipart_info.part_size)
    ):
        future = executor.submit(upload, part_number=part_number, seek=seek)
        futures.append(future)

    done, not_done = wait(futures, return_when=FIRST_EXCEPTION)
    if len(not_done) > 0:
        abort_event.set()
    for future in not_done:
        future.cancel()
    for future in done:
        if future.exception() is not None:
            raise future.exception()

    logger.debug("Finalizing multipart upload of %s", local_file)
    parts = sorted(parts, key=lambda part: part.part_number)
    response = requests.post(
        multipart_upload.finalize_signed_url.signed_url,
        data=_get_s3_compatible_completion_body(parts),
        timeout=2 * 60,
    )
    response.raise_for_status()
    logger.debug("Multipart upload of %s completed", local_file)


def azure_multi_part_upload(
    multipart_upload: MultiPartUpload,
    local_file: str,
    multipart_info: _FileMultiPartInfo,
    executor: ThreadPoolExecutor,
    progress_bar: Optional[Progress] = None,
    abort_event: Optional[Event] = None,
    exception_class=HttpRequestException,
):
    abort_event = abort_event or Event()

    if progress_bar:
        multi_part_upload_progress = progress_bar.add_task(
            f"[green]Uploading {local_file}:", start=True
        )

    def upload(part_number: int, seek: int):
        logger.debug(
            "Uploading part %d/%d of %s",
            part_number,
            multipart_info.num_parts,
            local_file,
        )
        _file_part_upload(
            url=multipart_upload.part_signed_urls[part_number].signed_url,
            file_path=local_file,
            seek=seek,
            length=multipart_info.part_size,
            file_size=multipart_info.file_size,
            abort_event=abort_event,
            exception_class=exception_class,
        )
        if progress_bar:
            progress_bar.update(
                multi_part_upload_progress,
                advance=multipart_info.part_size,
                total=multipart_info.file_size,
            )
        logger.debug(
            "Uploaded part %d/%d of %s",
            part_number,
            multipart_info.num_parts,
            local_file,
        )

    futures: List[Future] = []
    for part_number, seek in enumerate(
        range(0, multipart_info.file_size, multipart_info.part_size)
    ):
        future = executor.submit(upload, part_number=part_number, seek=seek)
        futures.append(future)

    done, not_done = wait(futures, return_when=FIRST_EXCEPTION)
    if len(not_done) > 0:
        abort_event.set()
    for future in not_done:
        future.cancel()
    for future in done:
        if future.exception() is not None:
            raise future.exception()

    logger.debug("Finalizing multipart upload of %s", local_file)
    if multipart_upload.azure_blob_block_ids:
        response = requests.put(
            multipart_upload.finalize_signed_url.signed_url,
            data=_get_azure_blob_completion_body(
                block_ids=multipart_upload.azure_blob_block_ids
            ),
            timeout=2 * 60,
        )
        response.raise_for_status()
    logger.debug("Multipart upload of %s completed", local_file)

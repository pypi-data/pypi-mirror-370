"""
Utilities for validating user inputs such as metric names and parameter names.
"""

import json
import numbers
import posixpath
import re
from operator import xor
from typing import List, Optional, Union

from truefoundry.ml import MlFoundryException
from truefoundry.ml._autogen.client import (  # type: ignore[attr-defined]
    MetricDto,
    ParamDto,
    RunTagDto,
)

_VALID_PARAM_AND_METRIC_NAMES = re.compile(r"^[/\w.\- ]*$")

# Regex for valid run IDs: must be an alphanumeric string of length 1 to 256.
_BAD_CHARACTERS_MESSAGE = (
    "Names may only contain alphanumerics, underscores (_), dashes (-), periods (.),"
    " spaces ( ), and slashes (/)."
)
_RUN_ID_REGEX = re.compile(r"^[a-zA-Z0-9][\w\-]{0,255}$")
_ML_REPO_ID_REGEX = re.compile(r"^[a-zA-Z0-9][\w\-]{0,63}$")
_ML_REPO_NAME_REGEX = re.compile(r"^[a-zA-Z][a-zA-Z0-9\-]{1,98}[a-zA-Z0-9]$")
_RUN_NAME_REGEX = re.compile(r"^[a-zA-Z0-9-]*$")
_RUN_LOG_LOG_TYPE_REGEX = re.compile(r"^[a-zA-Z0-9-/]*$")
_RUN_LOG_KEY_REGEX = re.compile(r"^[a-zA-Z0-9-_]*$")
_APP_NAME_REGEX = re.compile(r"^[a-z][a-z0-9\\-]{1,30}[a-z0-9]$")


MAX_PARAMS_TAGS_PER_BATCH = 100
MAX_METRICS_PER_BATCH = 1000
MAX_ENTITIES_PER_BATCH = 1000
MAX_BATCH_LOG_REQUEST_SIZE = int(1e6)
MAX_PARAM_VAL_LENGTH = 1000
MAX_TAG_VAL_LENGTH = 5000
MAX_ML_REPO_TAG_KEY_LENGTH = 250
MAX_ML_REPO_TAG_VAL_LENGTH = 5000
MAX_ENTITY_KEY_LENGTH = 250
MAX_RUN_LOG_KEY_NAME_LENGTH = 128
MAX_RUN_LOG_LOG_TYPE_LENGTH = 128
MAX_ML_REPO_DESCRIPTION_LENGTH = 512
MAX_RUN_DESCRIPTION_LENGTH = 512
MAX_ML_REPOS_LISTED_PER_PAGE = 100


def is_string_type(item):
    return isinstance(item, str)


def bad_path_message(name: str):
    return (
        f"Names may be treated as files in certain cases, "
        f"and must not resolve to other names when treated as such. "
        f"This name would resolve to {posixpath.normpath(name)!r}"
    )


def path_not_unique(name: str):
    norm = posixpath.normpath(name)
    return norm != name or norm == "." or norm.startswith("..") or norm.startswith("/")


def _validate_metric_name(name: str):
    """Check that `name` is a valid metric name and raise an exception if it isn't."""
    if name is None or not _VALID_PARAM_AND_METRIC_NAMES.match(name):
        raise MlFoundryException(
            f"Invalid metric name: {name!r}. {_BAD_CHARACTERS_MESSAGE}",
        )
    if path_not_unique(name):
        raise MlFoundryException(
            f"Invalid metric name: {name!r}. {bad_path_message(name)}",
        )


def _validate_run_name(name: Optional[str]):
    if not name or not _RUN_NAME_REGEX.match(name):
        raise MlFoundryException(
            f"Invalid run name {name!r}. Name should not empty string "
            f"and may only contain alphanumerics or dashes (-)",
        )
    _validate_length_limit("Run name", MAX_ENTITY_KEY_LENGTH, name)


def _is_numeric(value):
    """
    Returns True if the passed-in value is numeric.
    """
    # Note that `isinstance(bool_value, numbers.Number)` returns `True` because `bool` is a
    # subclass of `int`.
    return not isinstance(value, bool) and isinstance(value, numbers.Number)


def _validate_metric(
    key: str,
    value: Optional[Union[int, float]],
    timestamp: Optional[int],
    step: Optional[int],
):
    """
    Check that a param with the specified key, value, timestamp is valid and raise an exception if
    it isn't.
    """
    _validate_metric_name(key)
    _validate_length_limit("Metric name", MAX_ENTITY_KEY_LENGTH, key)
    # value must be a Number
    # since bool is an instance of Number check for bool additionally
    if not _is_numeric(value):
        raise MlFoundryException(
            f"Got invalid value {value} for metric {key!r} (step={step}). "
            f"Please specify value as a valid double (64-bit floating point)",
        )

    if not isinstance(timestamp, int) or timestamp < 0:
        raise MlFoundryException(
            f"Got invalid timestamp {timestamp} for metric {key!r} (value={value}). "
            f"Timestamp must be a non-negative long (64-bit integer)",
        )

    if not isinstance(step, int):
        raise MlFoundryException(
            f"Got invalid step {step} for metric {key!r} (value={value}). "
            f"Step must be a valid long (64-bit integer).",
        )


def _validate_run_log_input(
    key: str,
    timestamp: int,
    step: int,
    log_type: str,
    value: Optional[str],
    artifact_path: Optional[str],
):
    # reusing the validation defined for metric: str
    _validate_metric(key=key, value=0, timestamp=timestamp, step=step)
    _validate_length_limit("RunLog log type", MAX_RUN_LOG_LOG_TYPE_LENGTH, log_type)
    _validate_length_limit("RunLog log key", MAX_RUN_LOG_KEY_NAME_LENGTH, key)
    if not log_type or not _RUN_LOG_LOG_TYPE_REGEX.match(log_type):
        raise MlFoundryException(
            f"Invalid run log_type: {log_type}",
        )

    if not key or not _RUN_LOG_KEY_REGEX.match(key):
        raise MlFoundryException(
            f"Invalid run log key: {key!r} should only contain alphanumeric, hyphen or underscore"
        )

    if not xor(bool(artifact_path), bool(value)):
        raise MlFoundryException(
            "Either artifact_path or value should be empty. "
            f"artifact_path={artifact_path!r}, value={value!r}",
        )
    if value is not None:
        try:
            json.loads(value)
        except ValueError as e:
            raise MlFoundryException(
                f"Key {key!r} does not contain a valid json: {e}",
            ) from e


def _validate_param(key: str, value: str):
    """
    Check that a param with the specified key & value is valid and raise an exception if it
    isn't.
    """
    _validate_param_name(key)
    _validate_length_limit("Param key", MAX_ENTITY_KEY_LENGTH, key)
    _validate_length_limit("Param value", MAX_PARAM_VAL_LENGTH, value)


def _validate_tag(key: str, value: str):
    """
    Check that a tag with the specified key & value is valid and raise an exception if it isn't.
    """
    _validate_tag_name(key)
    _validate_length_limit("Tag key", MAX_ENTITY_KEY_LENGTH, key)
    _validate_length_limit("Tag value", MAX_TAG_VAL_LENGTH, value)


def _validate_ml_repo_tag(key: str, value: str):
    """
    Check that a tag with the specified key & value is valid and raise an exception if it isn't.
    """
    _validate_tag_name(key)
    _validate_length_limit("Tag key", MAX_ML_REPO_TAG_KEY_LENGTH, key)
    _validate_length_limit("Tag value", MAX_ML_REPO_TAG_VAL_LENGTH, value)


def _validate_list_ml_repos_max_results(max_results):
    """
    Check that `max_results` is within an acceptable range and raise an exception if it isn't.
    """
    if max_results is None:
        return

    if max_results < 1:
        raise MlFoundryException(
            f"Invalid value for request parameter max_results. "
            f"It must be at least 1, but got value {max_results}",
        )

    if max_results > MAX_ML_REPOS_LISTED_PER_PAGE:
        raise MlFoundryException(
            f"Invalid value for request parameter max_results. "
            f"It must be at most {MAX_ML_REPOS_LISTED_PER_PAGE}, but got value {max_results}",
        )


def _validate_param_keys_unique(params: List[ParamDto]):
    """Ensures that duplicate param keys are not present in the `log_batch()` params argument"""
    unique_keys = []
    dupe_keys = []
    for param in params:
        if param.key not in unique_keys:
            unique_keys.append(param.key)
        else:
            dupe_keys.append(param.key)

    if dupe_keys:
        raise MlFoundryException(
            f"Duplicate parameter keys have been submitted: {dupe_keys}. Please ensure "
            f"the request contains only one param value per param key.",
        )


def _validate_param_name(name: str):
    """Check that `name` is a valid parameter name and raise an exception if it isn't."""
    if name is None or not _VALID_PARAM_AND_METRIC_NAMES.match(name):
        raise MlFoundryException(
            f"Invalid parameter name: {name!r}. {_BAD_CHARACTERS_MESSAGE}",
        )
    if path_not_unique(name):
        raise MlFoundryException(
            f"Invalid parameter name: {name!r}. {bad_path_message(name)}",
        )


def _validate_tag_name(name: str):
    """Check that `name` is a valid tag name and raise an exception if it isn't."""
    # Reuse param & metric check.
    if name is None or not _VALID_PARAM_AND_METRIC_NAMES.match(name):
        raise MlFoundryException(
            f"Invalid tag name: {name!r}. {_BAD_CHARACTERS_MESSAGE}",
        )
    if path_not_unique(name):
        raise MlFoundryException(
            f"Invalid tag name: {name!r}. {bad_path_message(name)}",
        )


def _validate_length_limit(entity_name: str, limit: int, value: str):
    if len(value) > limit:
        raise MlFoundryException(
            f"{entity_name} {value!r} had length {len(value)} which exceeded length limit of {limit}",
        )


def _validate_run_id(run_id: str):
    """Check that `run_id` is a valid run ID and raise an exception if it isn't."""
    if _RUN_ID_REGEX.match(run_id) is None:
        raise MlFoundryException(
            f"Invalid run ID: {run_id!r}",
        )


def _validate_ml_repo_id(ml_repo_id: str):
    """Check that `ml_repo_id`is a valid string or None, raise an exception if it isn't."""
    if ml_repo_id is not None and _ML_REPO_ID_REGEX.match(ml_repo_id) is None:
        raise MlFoundryException(
            f"Invalid ml_repo ID: {ml_repo_id!r}",
        )


def _validate_batch_limit(entity_name: str, limit: int, length: int):
    if length > limit:
        error_msg = (
            f"A batch logging request can contain at most {limit} {entity_name}. "
            f"Got {length} {entity_name}. "
            f"Please split up {entity_name} across multiple requests and try again."
        )
        raise MlFoundryException(error_msg)


def _validate_batch_log_limits(
    metrics: List[MetricDto], params: List[ParamDto], tags: List[RunTagDto]
):
    """Validate that the provided batched logging arguments are within expected limits."""
    _validate_batch_limit(
        entity_name="metrics", limit=MAX_METRICS_PER_BATCH, length=len(metrics)
    )
    _validate_batch_limit(
        entity_name="params", limit=MAX_PARAMS_TAGS_PER_BATCH, length=len(params)
    )
    _validate_batch_limit(
        entity_name="tags", limit=MAX_PARAMS_TAGS_PER_BATCH, length=len(tags)
    )
    total_length = len(metrics) + len(params) + len(tags)
    _validate_batch_limit(
        entity_name="metrics, params, and tags",
        limit=MAX_ENTITIES_PER_BATCH,
        length=total_length,
    )


def _validate_batch_log_data(
    metrics: List[MetricDto], params: List[ParamDto], tags: List[RunTagDto]
):
    if len(metrics) == 0 and len(params) == 0 and len(tags) == 0:
        return
    _validate_batch_log_limits(metrics=metrics, params=params, tags=tags)
    for metric in metrics:
        _validate_metric(metric.key, metric.value, metric.timestamp, metric.step)
    if len(params) > 1:
        _validate_param_keys_unique(params)
    for param in params:
        _validate_param(param.key, param.value)
    for tag in tags:
        _validate_tag(tag.key, tag.value)


def _validate_ml_repo_name(ml_repo_name: str):
    """Check that `ml_repo_name` is a valid string and raise an exception if it isn't."""
    if ml_repo_name == "" or ml_repo_name is None or not is_string_type(ml_repo_name):
        raise MlFoundryException(
            f"ml_repo must be string type and not empty. "
            f"Got {type(ml_repo_name)} type with value {ml_repo_name!r}"
        )

    if not _ML_REPO_NAME_REGEX.match(ml_repo_name):
        raise MlFoundryException(
            f"Invalid ML Repo name {ml_repo_name!r}. Name may only contain alphanumerics or dashes (-)",
        )


def _validate_ml_repo_description(description: str):
    _validate_length_limit(
        "ML Repo Description", MAX_ML_REPO_DESCRIPTION_LENGTH, description
    )


def _validate_run_description(description: str):
    _validate_length_limit("Run Description", MAX_RUN_DESCRIPTION_LENGTH, description)

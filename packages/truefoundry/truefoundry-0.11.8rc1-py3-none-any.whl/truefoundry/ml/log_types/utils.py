import re

from truefoundry.ml.exceptions import MlFoundryException

KEY_REGEX = re.compile(r"^[a-zA-Z0-9-_]+$")


def validate_key_name(key: str):
    if not key or not KEY_REGEX.match(key):
        raise MlFoundryException(
            f"Invalid run image key: {key} should only contain alphanumeric, hyphen or underscore"
        )

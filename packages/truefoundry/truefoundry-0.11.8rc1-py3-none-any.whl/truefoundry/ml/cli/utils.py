import rich_click as click

from truefoundry.ml import MlFoundryException
from truefoundry.ml.validation_utils import (
    _APP_NAME_REGEX,
)


class AppName(click.ParamType):
    """
    Custom ParamType to validate application names.
    """

    name = "application-name"

    def convert(self, value, param, ctx):
        try:
            if not value or not _APP_NAME_REGEX.match(value):
                raise MlFoundryException(
                    f"{value!r} must be lowercase and cannot contain spaces. It can only contain alphanumeric characters and hyphens. "
                    f"Length must be between 1 and 30 characters."
                )
        except MlFoundryException as e:
            self.fail(str(e), param, ctx)
        return value


class NonEmptyString(click.ParamType):
    name = "non-empty-string"

    def convert(self, value, param, ctx):
        if isinstance(value, str) and not value.strip():
            self.fail("Value cannot be empty or contain only spaces.", param, ctx)
        return value

import os
import typing

from truefoundry.ml.exceptions import MlFoundryException


class _InternalNamespace:
    NAMESPACE = "mlf"
    DELIMITER = "."
    NAMESPACE_VIOLATION_MESSAGE = """
        {name} cannot start with {prefix}
    """

    def __call__(self, name: str, delimiter: str = DELIMITER):
        if not name:
            raise MlFoundryException("name should be a non empty string")
        return _InternalNamespace.NAMESPACE + delimiter + name

    def __truediv__(self, path: str):
        return os.path.join(_InternalNamespace.NAMESPACE, path)

    @staticmethod
    def _validate_name_not_using_namespace(name: typing.Optional[str], delimiter: str):
        if name and name.startswith(_InternalNamespace.NAMESPACE + delimiter):
            raise MlFoundryException(
                _InternalNamespace.NAMESPACE_VIOLATION_MESSAGE.format(
                    name=name, prefix=_InternalNamespace.NAMESPACE + delimiter
                )
            )

    def validate_namespace_not_used(
        self,
        names: typing.Optional[typing.Union[str, typing.Iterable[str]]] = None,
        delimiter: str = DELIMITER,
        path: typing.Optional[str] = None,
    ):
        if isinstance(names, str):
            names = [names]
        if names is not None:
            for name_ in names:
                self._validate_name_not_using_namespace(name_, delimiter)
        if path:
            prefix = os.path.normpath(os.path.join(_InternalNamespace.NAMESPACE, ""))
            if os.path.normpath(path).startswith(prefix):
                raise MlFoundryException(
                    _InternalNamespace.NAMESPACE_VIOLATION_MESSAGE.format(
                        name=path, prefix=prefix
                    )
                )


NAMESPACE = _InternalNamespace()

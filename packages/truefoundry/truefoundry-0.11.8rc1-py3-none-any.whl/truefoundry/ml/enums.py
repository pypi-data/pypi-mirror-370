import enum

from truefoundry.ml.exceptions import MlFoundryException


class EnumMissingMixin:
    @classmethod
    def _missing_(cls, value):
        raise MlFoundryException(
            "%r is not a valid %s.  Valid types: %s"
            % (
                value,
                cls.__name__,
                ", ".join([repr(m.value) for m in cls]),  # type: ignore
            )
        )


class ViewType(str, EnumMissingMixin, enum.Enum):
    # TODO (chiragjn): This should come from autogen! And also be exported in __init__.py
    ACTIVE_ONLY = "ACTIVE_ONLY"
    DELETED_ONLY = "DELETED_ONLY"
    HARD_DELETED_ONLY = "HARD_DELETED_ONLY"
    ALL = "ALL"


class RunStatus(str, EnumMissingMixin, enum.Enum):
    # TODO (chiragjn): This should come from autogen! And also be exported in __init__.py
    RUNNING = "RUNNING"
    SCHEDULED = "SCHEDULED"
    FINISHED = "FINISHED"
    FAILED = "FAILED"
    KILLED = "KILLED"


class FileFormat(EnumMissingMixin, enum.Enum):
    CSV = "csv"
    PARQUET = "parquet"


class ModelFramework(EnumMissingMixin, enum.Enum):
    SKLEARN = "sklearn"
    TENSORFLOW = "tensorflow"
    PYTORCH = "pytorch"
    KERAS = "keras"
    XGBOOST = "xgboost"
    LIGHTGBM = "lightgbm"
    FASTAI = "fastai"
    H2O = "h2o"
    ONNX = "onnx"
    SPACY = "spacy"
    STATSMODELS = "statsmodels"
    GLUON = "gluon"
    PADDLE = "paddle"
    TRANSFORMERS = "transformers"
    UNKNOWN = "unknown"


class DataSlice(EnumMissingMixin, enum.Enum):
    TRAIN = "train"
    VALIDATE = "validate"
    TEST = "test"
    PREDICTION = "prediction"


class ModelType(EnumMissingMixin, enum.Enum):
    BINARY_CLASSIFICATION = "binary_classification"
    MULTICLASS_CLASSIFICATION = "multiclass_classification"
    REGRESSION = "regression"
    TIMESERIES = "timeseries"

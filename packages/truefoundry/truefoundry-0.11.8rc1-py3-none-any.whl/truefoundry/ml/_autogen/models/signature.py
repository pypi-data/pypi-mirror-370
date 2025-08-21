from dataclasses import dataclass, is_dataclass
from typing import TYPE_CHECKING, Any, Dict, Optional, Union

import numpy as np

if TYPE_CHECKING:
    import pandas as pd


from .schema import ParamSchema, Schema, convert_dataclass_to_schema
from .utils import infer_param_schema, infer_schema

MlflowInferableDataset = Union["pd.DataFrame", "np.ndarray", Dict[str, "np.ndarray"]]


class ModelSignature:
    """
    ModelSignature specifies schema of model's inputs, outputs and params.

    ModelSignature can be :py:func:`inferred <mlflow.models.infer_signature>` from training
    dataset, model predictions using and params for inference, or constructed by hand by
    passing an input and output :py:class:`Schema <mlflow.types.Schema>`, and params
    :py:class:`ParamSchema <mlflow.types.ParamSchema>`.
    """

    def __init__(
        self,
        inputs: Union[Schema, dataclass] = None,
        outputs: Union[Schema, dataclass] = None,
        params: ParamSchema = None,
    ):
        if inputs and not isinstance(inputs, Schema) and not is_dataclass(inputs):
            raise TypeError(
                "inputs must be either None, mlflow.models.signature.Schema, or a dataclass,"
                f"got '{type(inputs).__name__}'"
            )
        if outputs and not isinstance(outputs, Schema) and not is_dataclass(outputs):
            raise TypeError(
                "outputs must be either None, mlflow.models.signature.Schema, or a dataclass,"
                f"got '{type(outputs).__name__}'"
            )
        if params and not isinstance(params, ParamSchema):
            raise TypeError(
                "If params are provided, they must by of type mlflow.models.signature.ParamSchema, "
                f"got '{type(params).__name__}'"
            )
        if all(x is None for x in [inputs, outputs, params]):
            raise ValueError(
                "At least one of inputs, outputs or params must be provided"
            )
        if is_dataclass(inputs):
            self.inputs = convert_dataclass_to_schema(inputs)
        else:
            self.inputs = inputs
        if is_dataclass(outputs):
            self.outputs = convert_dataclass_to_schema(outputs)
        else:
            self.outputs = outputs
        self.params = params

    def to_dict(self) -> Dict[str, Any]:
        """
        Serialize into a 'jsonable' dictionary.

        Input and output schema are represented as json strings. This is so that the
        representation is compact when embedded in an MLmodel yaml file.

        Returns:
            dictionary representation with input and output schema represented as json strings.
        """

        return {
            "inputs": self.inputs.to_json() if self.inputs else None,
            "outputs": self.outputs.to_json() if self.outputs else None,
            "params": self.params.to_json() if self.params else None,
        }

    @classmethod
    def from_dict(cls, signature_dict: Dict[str, Any]):
        """
        Deserialize from dictionary representation.

        Args:
            signature_dict: Dictionary representation of model signature.
                Expected dictionary format:
                `{'inputs': <json string>,
                'outputs': <json string>,
                'params': <json string>" }`

        Returns:
            ModelSignature populated with the data form the dictionary.
        """
        inputs = Schema.from_json(x) if (x := signature_dict.get("inputs")) else None
        outputs = Schema.from_json(x) if (x := signature_dict.get("outputs")) else None
        params = (
            ParamSchema.from_json(x) if (x := signature_dict.get("params")) else None
        )

        return cls(inputs, outputs, params)

    def __eq__(self, other) -> bool:
        return (
            isinstance(other, ModelSignature)
            and self.inputs == other.inputs
            and self.outputs == other.outputs
            and self.params == other.params
        )

    def __repr__(self) -> str:
        return (
            "inputs: \n"
            f"  {self.inputs!r}\n"
            "outputs: \n"
            f"  {self.outputs!r}\n"
            "params: \n"
            f"  {self.params!r}\n"
        )


def infer_signature(
    model_input: Any = None,
    model_output: "MlflowInferableDataset" = None,
    params: Optional[Dict[str, Any]] = None,
) -> ModelSignature:
    if model_input is not None:
        inputs = (
            convert_dataclass_to_schema(model_input)
            if is_dataclass(model_input)
            else infer_schema(model_input)
        )
    else:
        inputs = None
    if model_output is not None:
        outputs = (
            convert_dataclass_to_schema(model_output)
            if is_dataclass(model_output)
            else infer_schema(model_output)
        )
    else:
        outputs = None
    params = infer_param_schema(params) if params else None
    return ModelSignature(inputs, outputs, params)

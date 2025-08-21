import argparse
import importlib
import json
from typing import Any, Dict, List, Mapping, Optional, Tuple, Union

import numpy as np

from truefoundry.ml.exceptions import MlFoundryException


def get_module(
    module_name: str, error_message: Optional[str] = None, required: bool = False
):
    try:
        return importlib.import_module(module_name)
    except Exception as ex:
        msg = error_message or f"Error importing module {module_name}"
        if required:
            raise MlFoundryException(msg) from ex


class NumpyEncoder(json.JSONEncoder):
    """Special json encoder for numpy types"""

    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        return json.JSONEncoder.default(self, obj)


ParamsType = Union[Mapping[str, Any], argparse.Namespace]


def process_params(params: ParamsType) -> Mapping[str, Any]:
    if isinstance(params, Mapping):
        return params
    if isinstance(params, argparse.Namespace):
        return vars(params)
    # TODO: add absl support if required
    # move to a different file then
    raise MlFoundryException(
        "params should be either argparse.Namespace or a Mapping (dict) type"
    )


def flatten_dict(
    input_dict: Mapping[Any, Any], parent_key: str = "", sep: str = "."
) -> Dict[str, Any]:
    """Flatten hierarchical dict, e.g. ``{'a': {'b': 'c'}} -> {'a.b': 'c'}``.
    All the keys will be converted to str.

    Args:
        input_dict: Dictionary containing the keys
        parent_key: Prefix to add to the keys. Defaults to ``''``.
        sep: Delimiter to express the hierarchy. Defaults to ``'.'``.

    Returns:
        Flattened dict.

    Examples:
        >>> flatten_dict({'a': {'b': 'c'}})
        {'a.b': 'c'}
        >>> flatten_dict({'a': {'b': 123}})
        {'a.b': 123}
        >>> flatten_dict({'a': {'b': 'c'}}, parent_key="param")
        {'param.a.b': 'c'}
    """
    new_dict_items: List[Tuple[str, Any]] = []
    for k, v in input_dict.items():
        new_key = parent_key + sep + str(k) if parent_key else k
        if isinstance(v, Mapping):
            new_dict_items.extend(flatten_dict(v, new_key, sep=sep).items())
        else:
            new_dict_items.append((new_key, v))
    return dict(new_dict_items)

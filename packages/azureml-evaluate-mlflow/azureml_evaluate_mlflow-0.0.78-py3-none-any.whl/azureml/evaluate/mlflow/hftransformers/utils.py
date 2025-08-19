# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import importlib
import logging
from collections import UserDict

import numpy as np
import pandas as pd
import torch

from azureml.evaluate.mlflow.hftransformers import constants
from azureml.evaluate.mlflow.exceptions import AzureMLMLFlowTypeException
from azureml.evaluate.mlflow.constants import ErrorStrings

_logger = logging.getLogger(__name__)


def _ensure_tensor_on_device(inputs, device):
    if isinstance(inputs, dict):
        return {name: _ensure_tensor_on_device(tensor, device) for name, tensor in inputs.items()}
    elif isinstance(inputs, UserDict):
        return UserDict({name: _ensure_tensor_on_device(tensor, device) for name, tensor in inputs.items()})
    elif isinstance(inputs, list):
        return [_ensure_tensor_on_device(item, device) for item in inputs]
    elif isinstance(inputs, tuple):
        return tuple([_ensure_tensor_on_device(item, device) for item in inputs])
    elif isinstance(inputs, torch.Tensor):
        if device == torch.device("cpu") and inputs.dtype in {torch.float16, torch.bfloat16}:
            inputs = inputs.float()
        return inputs.to(device)
    else:
        return inputs


def concat_data_columns(data, seperator):
    """
    Concatenating data
    Todo: Add more datatypes and handle series
    :param data: Incoming data to be processed
    :type data:  DF/Numpy
    :param seperator: separator to concat
    :type seperator: str
    :return: Processed data
    :rtype: list
    """
    if isinstance(data, pd.DataFrame):
        data = data.apply(lambda x: x.astype(str).str.cat(sep=seperator), axis=1).to_list()
    elif isinstance(data, pd.Series):
        data = data.to_list()
    elif isinstance(data, np.ndarray):
        data = list(map(lambda x: seperator.join(x), data))
    else:
        raise AzureMLMLFlowTypeException(ErrorStrings.UnsupportedDataType)
    return data


def process_text_pairs(data, keys):
    """
    Preprocess Text Pairs
    """
    if isinstance(data, pd.DataFrame):
        if len(keys) != 2:
            _logger.warning("Number of columns should be two. Using default processor")
            return None
        data.rename(columns={keys[0]: 'text', keys[1]: 'text_pair'}, inplace=True)
        data = data.to_dict(orient='records')
    elif isinstance(data, np.ndarray):
        if data.ndim != 2 or data.shape[1] != 2:
            _logger.warning("Array dimension not of required size. Using default processor")
            return None
        data = [{'text': val[0], 'text_pair': val[1]} for val in data]
    else:
        _logger.warning("Datatype not supported by TextProcessor. Using default processor")
        return None
    return data


def sanitize_load_args(items):
    for item in items:
        if isinstance(items[item], str) and items[item].startswith("torch."):
            items[item] = eval(items[item])
    return items


def get_custom_pipeline(**kwargs):
    custom_pipeline_module = kwargs.get("custom_pipeline_module", None)
    custom_pipeline_class = kwargs.get("custom_pipeline_class", None)
    if custom_pipeline_module is not None:
        try:
            imported_module = importlib.import_module(custom_pipeline_module)
            return getattr(imported_module, custom_pipeline_class, None)
        except ImportError as e:
            _logger.warning(f"custom_pipeline_module script not found: {e.msg}")
        except Exception as e:
            _logger.error(f"Error while loading custom pipeline: {repr(e)}")
    return None


def get_pipeline_parameters(**kwargs):
    """
    Extract relevant kwargs to set in pipeline
    @param kwargs:
    @return:
    """
    pipeline_init_args = kwargs.pop("pipeline_init_args", {})
    parameters = {"device": kwargs.get("device", None),
                  "batch_size": kwargs.get("batch_size", None),
                  "model_kwargs": sanitize_load_args(
                      {**kwargs.pop("model_hf_load_kwargs", {}), **kwargs.pop("model_kwargs", {})}),
                  "pipeline_class": get_custom_pipeline(**kwargs),
                  "trust_remote_code": kwargs.pop("trust_remote_code", True),
                  **sanitize_load_args(pipeline_init_args)}
    return parameters


def get_task_type_for_pipeline(task_type):
    if task_type in [constants.TaskTypes.MULTILABEL, constants.TaskTypes.MULTICLASS]:
        return constants.TaskTypes.TEXT_CLASSIFICATION
    return task_type

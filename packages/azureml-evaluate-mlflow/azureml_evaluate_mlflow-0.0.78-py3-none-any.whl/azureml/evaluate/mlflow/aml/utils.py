# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from typing import Union

import pandas as pd
import numpy as np
from azureml.evaluate.mlflow.aml.model import AzureMLInput
from scipy.sparse import csc_matrix, csr_matrix
from mlflow.types import DataType, Schema, TensorSpec
from mlflow.types.utils import clean_tensor_type
from azureml.evaluate.mlflow.exceptions import AzureMLMLFlowUserException


def _enforce_mlflow_datatype(name, values: pd.Series, t: DataType):
    """
    Enforce the input column type matches the declared in model input schema.

    The following type conversions are allowed:

    1. object -> string
    2. int -> long (upcast)
    3. float -> double (upcast)
    4. int -> double (safe conversion)
    5. np.datetime64[x] -> datetime (any precision)
    6. object -> datetime

    Any other type mismatch will raise error.
    """
    if values.dtype == object and t not in (DataType.binary, DataType.string):
        values = values.infer_objects()

    if t == DataType.string and values.dtype == object:
        # NB: the object can contain any type and we currently cannot cast to pd Strings
        # due to how None is cast
        return values

    # NB: Comparison of pd and numpy data type fails when numpy data type is on the left hand
    # side of the comparison operator. It works, however, if pd type is on the left hand side.
    # That is because pd is aware of numpy.
    if t.to_pandas() == values.dtype or t.to_numpy() == values.dtype:
        # The types are already compatible => conversion is not necessary.
        return values

    if t == DataType.binary and values.dtype.kind == t.binary.to_numpy().kind:
        # NB: bytes in numpy have variable itemsize depending on the length of the longest
        # element in the array (column). Since MLflow binary type is length agnostic, we ignore
        # itemsize when matching binary columns.
        return values

    if t == DataType.datetime and values.dtype.kind == t.to_numpy().kind:
        # NB: datetime values have variable precision denoted by brackets, e.g. datetime64[ns]
        # denotes nanosecond precision. Since MLflow datetime type is precision agnostic, we
        # ignore precision when matching datetime columns.
        return values

    if t == DataType.datetime and values.dtype == object:
        # NB: Pyspark date columns get converted to object when converted to a pd
        # DataFrame. To respect the original typing, we convert the column to datetime.
        try:
            return values.astype(np.datetime64, errors="raise")
        except ValueError:
            raise AzureMLMLFlowUserException(
                "Failed to convert column {0} from type {1} to {2}.".format(name, values.dtype, t)
            )

    numpy_type = t.to_numpy()
    if values.dtype.kind == numpy_type.kind:
        is_upcast = values.dtype.itemsize <= numpy_type.itemsize
    elif values.dtype.kind == "u" and numpy_type.kind == "i":
        is_upcast = values.dtype.itemsize < numpy_type.itemsize
    elif values.dtype.kind in ("i", "u") and numpy_type == np.float64:
        # allow (u)int => double conversion
        is_upcast = values.dtype.itemsize <= 6
    else:
        is_upcast = False

    if is_upcast:
        return values.astype(numpy_type, errors="raise")
    else:
        # NB: conversion between incompatible types (e.g. floats -> ints or
        # double -> float) are not allowed. While supported by pd and numpy,
        # these conversions alter the values significantly.
        def all_ints(xs):
            return all(pd.isnull(x) or int(x) == x for x in xs)

        hint = ""
        if (
            values.dtype == np.float64
            and numpy_type.kind in ("i", "u")
            and values.hasnans
            and all_ints(values)
        ):
            hint = (
                " Hint: the type mismatch is likely caused by missing values. "
                "Integer columns in python can not represent missing values and are therefore "
                "encoded as floats. The best way to avoid this problem is to infer the model "
                "schema based on a realistic data sample (training dataset) that includes missing "
                "values. Alternatively, you can declare integer columns as doubles (float64) "
                "whenever these columns may have missing values. See `Handling Integers With "
                "Missing Values <https://www.mlflow.org/docs/latest/models.html#"
                "handling-integers-with-missing-values>`_ for more details."
            )

        raise AzureMLMLFlowUserException(
            "Incompatible input types for column {0}. "
            "Can not safely convert {1} to {2}.{3}".format(name, values.dtype, numpy_type, hint)
        )


def _enforce_tensor_spec(
    values: Union[np.ndarray, csc_matrix, csr_matrix], tensor_spec: TensorSpec
):
    """
    Enforce the input tensor shape and type matches the provided tensor spec.
    """
    expected_shape = tensor_spec.shape
    actual_shape = values.shape

    actual_type = values.dtype if isinstance(values, np.ndarray) else values.data.dtype

    if len(expected_shape) != len(actual_shape):
        raise AzureMLMLFlowUserException(
            "Shape of input {0} does not match expected shape {1}.".format(
                actual_shape, expected_shape
            )
        )
    for expected, actual in zip(expected_shape, actual_shape):
        if expected == -1:
            continue
        if expected != actual:
            raise AzureMLMLFlowUserException(
                "Shape of input {0} does not match expected shape {1}.".format(
                    actual_shape, expected_shape
                )
            )
    if clean_tensor_type(actual_type) != tensor_spec.type:
        raise AzureMLMLFlowUserException(
            "dtype of input {0} does not match expected dtype {1}".format(
                values.dtype, tensor_spec.type
            )
        )
    return values


def _enforce_col_schema(aml_input: AzureMLInput, input_schema: Schema):
    """Enforce the input columns conform to the model's column-based signature."""
    if input_schema.has_input_names():
        input_names = input_schema.input_names()
    else:
        input_names = aml_input.columns[: len(input_schema.inputs)]
    input_types = input_schema.input_types()
    new_aml_input = pd.DataFrame()
    for i, x in enumerate(input_names):
        new_aml_input[x] = _enforce_mlflow_datatype(x, aml_input[x], input_types[i])
    return new_aml_input


def _enforce_tensor_schema(aml_input: AzureMLInput, input_schema: Schema):
    """Enforce the input tensor(s) conforms to the model's tensor-based signature."""
    if input_schema.has_input_names():
        if isinstance(aml_input, dict):
            new_aml_input = dict()
            for col_name, tensor_spec in zip(input_schema.input_names(), input_schema.inputs):
                if not isinstance(aml_input[col_name], np.ndarray):
                    raise AzureMLMLFlowUserException(
                        "This model contains a tensor-based model signature with input names,"
                        " which suggests a dictionary input mapping input name to a numpy"
                        " array, but a dict with value type {0} was found.".format(
                            type(aml_input[col_name])
                        )
                    )
                new_aml_input[col_name] = _enforce_tensor_spec(aml_input[col_name], tensor_spec)
        elif isinstance(aml_input, pd.DataFrame):
            new_aml_input = dict()
            for col_name, tensor_spec in zip(input_schema.input_names(), input_schema.inputs):
                new_aml_input[col_name] = _enforce_tensor_spec(
                    np.array(aml_input[col_name], dtype=tensor_spec.type), tensor_spec
                )
        else:
            raise AzureMLMLFlowUserException(
                "This model contains a tensor-based model signature with input names, which"
                " suggests a dictionary input mapping input name to tensor, but an input of"
                " type {0} was found.".format(type(aml_input))
            )
    else:
        if isinstance(aml_input, pd.DataFrame):
            new_aml_input = _enforce_tensor_spec(aml_input.to_numpy(), input_schema.inputs[0])
        elif isinstance(aml_input, (np.ndarray, csc_matrix, csr_matrix)):
            new_aml_input = _enforce_tensor_spec(aml_input, input_schema.inputs[0])
        else:
            raise AzureMLMLFlowUserException(
                "This model contains a tensor-based model signature with no input names,"
                " which suggests a numpy array input, but an input of type {0} was"
                " found.".format(type(aml_input))
            )
    return new_aml_input


def _enforce_schema(aml_input: AzureMLInput, input_schema: Schema):
    """
    Enforces the provided input matches the model's input schema,

    For signatures with input names, we check there are no missing inputs and reorder the inputs to
    match the ordering declared in schema if necessary. Any extra columns are ignored.

    For column-based signatures, we make sure the types of the input match the type specified in
    the schema or if it can be safely converted to match the input schema.

    For tensor-based signatures, we make sure the shape and type of the input matches the shape
    and type specified in model's input schema.
    """
    if not input_schema.is_tensor_spec():
        if isinstance(aml_input, (list, np.ndarray, dict)):
            try:
                aml_input = pd.DataFrame(aml_input)
            except Exception as e:
                raise AzureMLMLFlowUserException(
                    "This model contains a column-based signature, which suggests a DataFrame"
                    " input. There was an error casting the input data to a DataFrame:"
                    " {0}".format(str(e))
                )
        if not isinstance(aml_input, pd.DataFrame):
            raise AzureMLMLFlowUserException(
                "Expected input to be DataFrame or list. Found: %s" % type(aml_input).__name__
            )

    if input_schema.has_input_names():
        # make sure there are no missing columns
        input_names = input_schema.input_names()
        expected_cols = set(input_names)
        actual_cols = set()
        if len(expected_cols) == 1 and isinstance(aml_input, np.ndarray):
            # for schemas with a single column, match input with column
            aml_input = {input_names[0]: aml_input}
            actual_cols = expected_cols
        elif isinstance(aml_input, pd.DataFrame):
            actual_cols = set(aml_input.columns)
        elif isinstance(aml_input, dict):
            actual_cols = set(aml_input.keys())
        missing_cols = expected_cols - actual_cols
        extra_cols = actual_cols - expected_cols
        # Preserve order from the original columns, since missing/extra columns are likely to
        # be in same order.
        missing_cols = [c for c in input_names if c in missing_cols]
        extra_cols = [c for c in actual_cols if c in extra_cols]
        if missing_cols:
            raise AzureMLMLFlowUserException(
                "Model is missing inputs {0}."
                " Note that there were extra inputs: {1}".format(missing_cols, extra_cols)
            )
    elif not input_schema.is_tensor_spec():
        # The model signature does not specify column names => we can only verify column count.
        num_actual_columns = len(aml_input.columns)
        if num_actual_columns < len(input_schema.inputs):
            raise AzureMLMLFlowUserException(
                "Model inference is missing inputs. The model signature declares "
                "{0} inputs  but the provided value only has "
                "{1} inputs. Note: the inputs were not named in the signature so we can "
                "only verify their count.".format(len(input_schema.inputs), num_actual_columns)
            )

    return (
        _enforce_tensor_schema(aml_input, input_schema)
        if input_schema.is_tensor_spec()
        else _enforce_col_schema(aml_input, input_schema)
    )

# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Constants for azureml-evaluate-mlflow"""


class ForecastFlavors:
    """The constants for forecast flavors."""

    # The parameter name
    FLAVOUR = "forecast_flavour"
    # Flavors
    RECURSIVE_FORECAST = "forecast"
    ROLLING_FORECAST = "rolling_forecast"

    ALL = {RECURSIVE_FORECAST, ROLLING_FORECAST}


class ForecastColumns:
    """The columns, returned in the forecast data frame."""

    _ACTUAL_COLUMN_NAME = '_automl_actual'
    _FORECAST_COLUMN_NAME = '_automl_forecast'


class ErrorStrings:
    """Error Strings."""

    GenericEvaluateMlflowError = "Evaluate Mlflow failed due to [{error}]."
    InvalidModel = "Invalid model. Model should be of type [{type}]."
    UnsupportedModelType = "Unsupported model type [{type}]."
    UnsupportedTaskType = "Unsupported task type [{task}]."
    UnsupportedDataType = "Unsupported data type."
    UnknownArtifact = "Unknown artifact [{artifact}]."
    InvalidBinaryClassifierLabels = "Binary classifier evaluation dataset positive class label must be 1 or True, " + \
                                    "negative class label must be 0 or -1 or False, and dataset must contains " + \
                                    "both positive and negative examples."
    InvalidModelEvaluator = "The model could not be evaluated by any of the registered evaluators, please " + \
                            "verify that the model type and other configs are set correctly."
    InvalidEvaluatorName = "`evaluators` argument must be None, an evaluator name string, or a list of " + \
                           "evaluator names."
    InvalidModelURI = "The model argument must be a string URI referring to an MLflow model or " + \
                      "an instance of `[{instance}]`."
    InvalidData = "The data argument must be a numpy array, a list or a Pandas DataFrame, or " + \
                  "spark DataFrame if pyspark package installed."
    InvalidDatasetTemplate = "Dataset [{type}] cannot include a double quote (\") but got [{value}]."
    MethodDoesNotExist = "Unable to use [{predict_module}] module. [{method}] method does not exist."
    MissingMetadata = "Model is missing metadata."
    MissingMethod = "Model implementation is missing required [{method}] method."

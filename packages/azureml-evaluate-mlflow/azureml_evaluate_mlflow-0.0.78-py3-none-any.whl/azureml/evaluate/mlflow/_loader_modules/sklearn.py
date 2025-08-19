# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import mlflow


def _load_azureml(path):
    """
        Load Azureml implementation. Called by ``azureml.load_model``.

        :param path: Local filesystem path to the MLflow Model with the ``sklearn`` flavor.
    """
    return mlflow.sklearn.load_model(path)


def _load_pyfunc(path):
    """
        Load Azureml implementation. Called by ``azureml.load_model``.

        :param path: Local filesystem path to the MLflow Model with the ``sklearn`` flavor.
    """
    return mlflow.sklearn.load_model(path)

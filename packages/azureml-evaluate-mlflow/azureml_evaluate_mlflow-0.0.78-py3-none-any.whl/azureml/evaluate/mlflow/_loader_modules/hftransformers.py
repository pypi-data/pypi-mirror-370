# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import logging
import os

from mlflow import MlflowException
from transformers import pipeline

import azureml.evaluate.mlflow as mlflow
from mlflow.utils.model_utils import _get_flavor_configuration
from azureml.evaluate.mlflow.hftransformers.utils import get_task_type_for_pipeline
from azureml.evaluate.mlflow.hftransformers import HFMODEL_PATH, is_experimental

_logger = logging.getLogger(__name__)


class _AzureMLTransformersWrapper(mlflow.hftransformers._HFTransformersWrapper):
    def predict(self, data, **kwargs):
        if hasattr(self.hf_model, 'eval'):
            self.hf_model.eval()
        data, addn_args = self._validate_data(data)
        from azureml.evaluate.mlflow.hftransformers._task_based_predictors import get_predictor
        if "task_type" in addn_args:
            self.misc_conf["task_type"] = addn_args.pop("task_type")
        predictor_kwargs = {**self.misc_conf, **kwargs, **addn_args.pop("dev_args", {}), "addn_args": addn_args}
        problem_type = self._get_problem_type(**predictor_kwargs)
        if hasattr(self.config, 'custom_pipelines'):
            setattr(self.config, 'custom_pipelines', self.custom_pipelines)
        if "task_type" in predictor_kwargs:
            self.task_type = predictor_kwargs.pop("task_type")
            self.pipeline = pipeline(get_task_type_for_pipeline(self.task_type), model=self.path_to_model,
                                     tokenizer=self.tokenizer,
                                     **self.pipeline_args) if is_experimental() else None
        predictor = get_predictor(self.task_type, problem_type)(task_type=self.task_type, model=self.hf_model,
                                                                tokenizer=self.tokenizer,
                                                                config=self.config,
                                                                pipeline=self.pipeline)
        return predictor.predict(data, **predictor_kwargs)

    def predict_proba(self, data, **kwargs):
        if hasattr(self.hf_model, 'eval'):
            self.hf_model.eval()
        data, addn_args = self._validate_data(data)
        if "task_type" in addn_args:
            self.misc_conf["task_type"] = addn_args.pop("task_type")
        from azureml.evaluate.mlflow.hftransformers._task_based_predictors import get_predictor
        predictor_kwargs = {**self.misc_conf, **kwargs, **addn_args.pop("dev_args", {}), "addn_args": addn_args}
        problem_type = self._get_problem_type(**predictor_kwargs)
        if hasattr(self.config, 'custom_pipelines'):
            setattr(self.config, 'custom_pipelines', self.custom_pipelines)
        if "task_type" in predictor_kwargs:
            self.task_type = predictor_kwargs.pop("task_type")
            self.pipeline = pipeline(get_task_type_for_pipeline(self.task_type), model=self.path_to_model,
                                     tokenizer=self.tokenizer,
                                     **self.pipeline_args) if is_experimental() else None
        predictor = get_predictor(self.task_type, problem_type)(task_type=self.task_type, model=self.hf_model,
                                                                tokenizer=self.tokenizer,
                                                                config=self.config,
                                                                pipeline=self.pipeline)
        return predictor.predict_proba(data, **predictor_kwargs)


def _load_azureml(path, **kwargs):
    """
    Load PyFunc implementation. Called by ``pyfunc.load_model``.

    :param path: Local filesystem path to the MLflow Model with the ``pytorch`` flavor.
    """
    path1 = os.sep.join(path.split(os.sep)[:-1])
    try:
        hf_conf = _get_flavor_configuration(path1, mlflow.hftransformers.FLAVOR_NAME_MLMODEL_LOGGING)
    except MlflowException as e:
        hf_conf = _get_flavor_configuration(path1, mlflow.hftransformers.FLAVOR_NAME)
    hf_conf = {**hf_conf, **kwargs, "path": path1}
    task_type, hf_model, tokenizer, config = mlflow.hftransformers._load_model(path, hf_conf)
    return _AzureMLTransformersWrapper(task_type, hf_model, tokenizer, config, hf_conf,
                                       path_to_model=os.path.join(path, HFMODEL_PATH))

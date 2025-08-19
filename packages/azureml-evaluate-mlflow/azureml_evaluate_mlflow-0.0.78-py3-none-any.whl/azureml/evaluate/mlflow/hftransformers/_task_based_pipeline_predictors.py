# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
""" Predictors for different tasks for HFTransformers Mlflow flavor"""
import logging
import numpy as np
import pandas as pd

from transformers import PreTrainedModel, PreTrainedTokenizer, PretrainedConfig
from typing import Any

from ._task_based_predictors import BasePredictor
from azureml.evaluate.mlflow.exceptions import AzureMLMLFlowTypeException
from azureml.evaluate.mlflow.constants import ErrorStrings

_logger = logging.getLogger(__name__)


def get_pipeline_predictor(task_type: str, problem_type: str):
    """
    Helper function to return Predictor class based on task_type
    @param task_type: HuggingFace task type
    @param problem_type: multilabel or not
    @return: Return BasePredictor
    """
    if task_type == 'question-answering':
        return QnAPipelinePredictor
    return GenericPipelinePredictor


class PipelineBasedPredictor(BasePredictor):

    def __init__(self, task_type: str, model: PreTrainedModel, tokenizer: PreTrainedTokenizer,
                 config: PretrainedConfig, pipeline_obj):
        super().__init__(task_type, model, tokenizer, config, pipeline_obj)

    def get_pipeline_results(self, data_orig, **kwargs):
        data, _ = self._preprocess(data_orig, **kwargs)
        pipeline_call_kwargs = self._get_tokenizer_config(**kwargs)
        return self.pipeline(data, **pipeline_call_kwargs)


class GenericPipelinePredictor(PipelineBasedPredictor):

    def predict(self, data: Any, **kwargs: Any):
        return self.get_pipeline_results(data, **kwargs)


class QnAPipelinePredictor(PipelineBasedPredictor):
    # ToDO: Add data validations
    def _parse_data(self, data, **kwargs):
        """
        Helper to parse Data
        @param data: Numpy.NDarray, DataFrame
        @return: context, question
        """
        keys = kwargs.get("keys", None)
        if keys is not None and len(keys) < 2:
            raise AzureMLMLFlowTypeException(
                "Extractive QnA must have at least two columns set as keys in preprocessing_config corresponding to "
                "'context' and 'question'."
            )
        if isinstance(data, pd.DataFrame):
            columns = data.columns.to_list()
            if keys is None and "context" in columns and "question" in columns:
                keys = ["context", "question"]
            elif keys is None:
                _logger.warning("Assuming first column to be context and the second column to be question")
                keys = columns
            if len(columns) < 2 or keys[0] not in columns or keys[1] not in columns:
                raise AzureMLMLFlowTypeException(
                    "Extractive QnA must have at least two columns in Dataframe. The columns must match "
                    "the preprocessing_config keys if set."
                )
            question = data[keys[1]].to_list()
            context = data[keys[0]].to_list()
        elif isinstance(data, pd.Series):
            raise AzureMLMLFlowTypeException("For Extractive QnA at least two columns are required")
        elif isinstance(data, np.ndarray):
            if data.ndim != 2:
                raise AzureMLMLFlowTypeException(
                    "The second dimension must be of size 2 corresponding to 'context' and 'question'."
                )
            context, question = np.hsplit(data, 2)
            context, question = list(context.ravel()), list(question.ravel())
        else:
            raise AzureMLMLFlowTypeException(ErrorStrings.UnsupportedDataType)
        return context, question

    def get_pipeline_results(self, data_orig, **kwargs):
        context, question = self._parse_data(data_orig)
        pipeline_call_kwargs = self._get_tokenizer_config(**kwargs)
        return self.pipeline(context=context, question=question, **pipeline_call_kwargs)

    def predict(self, data: Any, **kwargs: Any):
        return self.get_pipeline_results(data, **kwargs)

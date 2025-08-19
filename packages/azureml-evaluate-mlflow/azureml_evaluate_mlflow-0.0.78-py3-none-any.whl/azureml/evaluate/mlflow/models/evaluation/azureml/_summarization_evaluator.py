# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import numpy as np

from azureml.evaluate.mlflow.aml import AMLGenericModel, AzureMLInput
from azureml.evaluate.mlflow.models.evaluation.azureml._task_evaluator import TaskEvaluator

from azureml.evaluate.mlflow.exceptions import AzureMLMLFlowInvalidModelException
from azureml.evaluate.mlflow.constants import ErrorStrings
from azureml.metrics import compute_metrics, constants


class SummarizationEvaluator(TaskEvaluator):
    def evaluate(self,
                 model: AMLGenericModel,
                 X_test: AzureMLInput,
                 y_test: AzureMLInput,
                 **kwargs):
        if not isinstance(model, AMLGenericModel):
            exception_message = ErrorStrings.InvalidModel.format(type="AMLGenericModel")
            raise AzureMLMLFlowInvalidModelException(exception_message)
        y_pred = self._convert_predictions(model.predict(X_test, **kwargs))
        y_test = self._convert_predictions(y_test)
        if y_test.ndim == 1:
            y_test = np.reshape(y_test, (-1, 1))
        metrics = compute_metrics(task_type=constants.Tasks.SUMMARIZATION, y_test=y_test.tolist(),
                                  y_pred=y_pred.tolist(), **kwargs)
        return metrics, y_pred

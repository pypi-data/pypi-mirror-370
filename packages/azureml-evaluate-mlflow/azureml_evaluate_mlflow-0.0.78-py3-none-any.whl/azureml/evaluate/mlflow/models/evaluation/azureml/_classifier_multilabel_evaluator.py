# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from azureml.evaluate.mlflow.aml import AMLClassifierModel, AzureMLInput
from azureml.evaluate.mlflow.models.evaluation.azureml._task_evaluator import TaskEvaluator

from azureml.evaluate.mlflow.exceptions import AzureMLMLFlowInvalidModelException
from azureml.evaluate.mlflow.constants import ErrorStrings
from azureml.metrics import compute_metrics, constants
import ast
import logging
import numpy as np

_logger = logging.getLogger(__name__)


class ClassifierMultilabelEvaluator(TaskEvaluator):

    def evaluate(self,
                 model: AMLClassifierModel,
                 X_test: AzureMLInput,
                 y_test: AzureMLInput,
                 **kwargs):
        if not isinstance(model, AMLClassifierModel):
            exception_message = ErrorStrings.InvalidModel.format(type="AzureMLClassifierModel")
            raise AzureMLMLFlowInvalidModelException(exception_message)

        y_pred = self._convert_predictions(model.predict(X_test, **kwargs))
        y_pred_proba = self._convert_predictions(model.predict_proba(X_test, **kwargs))

        y_test = np.array(list(map(lambda x: ast.literal_eval(x), y_test)))
        y_pred = np.array(list(map(lambda x: ast.literal_eval(x), y_pred)))

        formatted_outputs = []
        for y_pred_val, y_pred_proba_val in zip(y_pred, y_pred_proba):
            formatted_outputs.append(
                [",".join(y_pred_val), ",".join(list(map(lambda x: f"{x:.4f}", y_pred_proba_val)))])

        if "multilabel" not in kwargs:
            kwargs["multilabel"] = True
        metrics = compute_metrics(task_type=constants.Tasks.CLASSIFICATION, y_test=y_test,
                                  y_pred=y_pred, y_pred_proba=y_pred_proba, **kwargs)
        return metrics, formatted_outputs

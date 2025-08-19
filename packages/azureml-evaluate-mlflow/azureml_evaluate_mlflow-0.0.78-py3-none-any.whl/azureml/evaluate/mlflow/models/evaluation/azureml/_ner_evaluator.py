# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import ast

from azureml.evaluate.mlflow.aml import AMLGenericModel, AzureMLInput
from azureml.evaluate.mlflow.models.evaluation.azureml._task_evaluator import TaskEvaluator

from azureml.evaluate.mlflow.exceptions import AzureMLMLFlowInvalidModelException
from azureml.evaluate.mlflow.constants import ErrorStrings
from azureml.metrics import compute_metrics, constants


class NerEvaluator(TaskEvaluator):

    def evaluate(self,
                 model: AMLGenericModel,
                 X_test: AzureMLInput,
                 y_test: AzureMLInput,
                 **kwargs):
        if not isinstance(model, AMLGenericModel):
            exception_message = ErrorStrings.InvalidModel.format(type="AMLGenericModel")
            raise AzureMLMLFlowInvalidModelException(exception_message)
        y_pred = list(self._convert_predictions(model.predict(X_test, **kwargs)))
        y_pred = list(map(lambda x: ast.literal_eval(x), y_pred))
        y_test = list(map(lambda x: ast.literal_eval(x), y_test))
        metrics = compute_metrics(task_type=constants.Tasks.TEXT_NER, y_test=y_test, y_pred=y_pred, **kwargs)
        return metrics, y_pred

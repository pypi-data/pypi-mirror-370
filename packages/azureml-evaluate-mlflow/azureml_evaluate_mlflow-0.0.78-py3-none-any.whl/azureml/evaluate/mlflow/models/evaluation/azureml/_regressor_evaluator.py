# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from azureml.evaluate.mlflow.aml import AMLGenericModel, AzureMLInput
from azureml.evaluate.mlflow.models.evaluation.azureml._task_evaluator import TaskEvaluator

from azureml.evaluate.mlflow.exceptions import AzureMLMLFlowInvalidModelException
from azureml.evaluate.mlflow.constants import ErrorStrings
from azureml.metrics import compute_metrics, constants


class RegressorEvaluator(TaskEvaluator):
    def evaluate(self,
                 model: AMLGenericModel,
                 X_test: AzureMLInput,
                 y_test: AzureMLInput,
                 **kwargs):
        if not isinstance(model, AMLGenericModel):
            exception_message = ErrorStrings.InvalidModel.format(type="AMLGenericModel")
            raise AzureMLMLFlowInvalidModelException(exception_message)
        y_pred = self._convert_predictions(model.predict(X_test, **kwargs))

        metrics = compute_metrics(task_type=constants.Tasks.REGRESSION, y_test=y_test, y_pred=y_pred, **kwargs)
        return metrics, y_pred

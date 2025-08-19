# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from azureml.evaluate.mlflow.aml import AMLClassifierModel, AzureMLInput
from azureml.evaluate.mlflow.models.evaluation.azureml._task_evaluator import TaskEvaluator

from azureml.evaluate.mlflow.exceptions import AzureMLMLFlowInvalidModelException
from azureml.evaluate.mlflow.constants import ErrorStrings
from azureml.metrics import compute_metrics, constants


class ClassifierEvaluator(TaskEvaluator):

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

        y_test = self._convert_predictions(y_test)
        metrics = compute_metrics(task_type=constants.Tasks.CLASSIFICATION, y_test=y_test, y_pred=y_pred,
                                  y_pred_proba=y_pred_proba, **kwargs)
        return metrics, y_pred

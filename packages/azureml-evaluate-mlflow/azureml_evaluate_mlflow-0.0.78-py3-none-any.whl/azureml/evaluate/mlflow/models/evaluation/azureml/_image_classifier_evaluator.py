# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from azureml.evaluate.mlflow.aml import AMLClassifierModel, AzureMLInput
from azureml.evaluate.mlflow.models.evaluation.azureml._task_evaluator import TaskEvaluator
from azureml.evaluate.mlflow.models.evaluation.constants import (
    EvaluationSettingLiterals,
    EvaluationMiscLiterals,
    EvaluationDefaultSetting,
)

from azureml.evaluate.mlflow.exceptions import AzureMLMLFlowInvalidModelException
from azureml.evaluate.mlflow.constants import ErrorStrings
from azureml.metrics import compute_metrics, constants

import ast
import numpy as np


class ImageClassifierEvaluator(TaskEvaluator):
    def evaluate(self, model: AMLClassifierModel, X_test: AzureMLInput, y_test: AzureMLInput, **kwargs):
        """Evaluate the image classifier model on the given test data.

        :param model: The model to evaluate.
        :param X_test: The test data.
        :param y_test: The test labels.
        :param kwargs: Additional arguments to evaluate model ["multi_label", "batch_size", "threshold"]
        :return: The metrics and predictions.
        :rtype: Tuple of Dict[str, Dict[str, Any]] and List[List]
        """
        if not isinstance(model, AMLClassifierModel):
            exception_message = ErrorStrings.InvalidModel.format(type="AzureMLClassifierModel")
            raise AzureMLMLFlowInvalidModelException(exception_message)

        y_pred = model.predict(X_test, **kwargs)
        y_pred_probs = y_pred[EvaluationMiscLiterals.IMAGE_OUTPUT_PROBS_COLUMN].to_list()
        y_labels = y_pred[EvaluationMiscLiterals.IMAGE_OUTPUT_LABEL_COLUMN].to_list()
        multilabel = kwargs.get(EvaluationSettingLiterals.MULTI_LABEL)
        if multilabel:
            # Prepare labels name from prediction probabilities. If probability is greater than threshold, then it's
            # considered as a predicted label.
            threshold = kwargs.get(
                EvaluationMiscLiterals.THRESHOLD, EvaluationDefaultSetting.MULTI_LABEL_PRED_THRESHOLD
            )

            predicted_labels = []
            for probs, labels in zip(y_pred_probs, y_labels):
                # Iterate through each image's predicted probabilities.
                image_labels = []
                for index, pred in enumerate(probs):
                    if pred >= threshold:
                        image_labels.append(labels[index])
                predicted_labels.append(image_labels)

            y_test = np.array(list(map(lambda x: ast.literal_eval(x), y_test)))
        else:
            y_pred_probs = np.array(y_pred_probs)
            label_indexes = np.argmax(y_pred_probs, axis=1)
            predicted_labels = [label_list[index] for index, label_list in zip(label_indexes, y_labels)]
            predicted_labels = self._convert_predictions(predicted_labels)
            y_test = self._convert_predictions(y_test)

        metrics = compute_metrics(
            task_type=constants.Tasks.CLASSIFICATION, y_test=y_test, y_pred=predicted_labels, **kwargs
        )
        return metrics, predicted_labels

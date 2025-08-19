# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from azureml.core.run import Run, _OfflineRun
from azureml.core.workspace import Workspace
from azureml.metrics import constants, _scoring_utilities
from mlflow.models.evaluation.artifacts import JsonEvaluationArtifact
from azureml.evaluate.mlflow.constants import ForecastColumns
from azureml.evaluate.mlflow.models.evaluation.azureml._task_evaluator_factory import EvaluatorFactory
from azureml.evaluate.mlflow.models.evaluation.base import ModelEvaluator, EvaluationResult
from azureml.evaluate.mlflow.exceptions import AzureMLMLFlowException, AzureMLMLFlowValueException
from azureml.evaluate.mlflow.constants import ErrorStrings

import pandas as pd
import os
import logging
import azureml.evaluate.mlflow as azureml_mlflow
import numpy as np

_logger = logging.getLogger(__name__)
DEFAULT_OUTPUT_FOLDER = "evaluation_result"
PREDICTION_COLUMN_NAME = "predictions"


class AzureMLEvaluator(ModelEvaluator):
    def __init__(self) -> None:
        super().__init__()
        self.supported_model_types = EvaluatorFactory().supported_tasks
        self.list_metrics = [constants.Metric.FMPerplexity]

    def can_evaluate(self, *, model_type, evaluator_config, **kwargs) -> bool:
        """
        Helper Function to check if model type supported by AzureMLEvaluator
        @param model_type:
        @param evaluator_config:
        @param kwargs:
        @return:
        """
        return model_type in self.supported_model_types

    def load_model(self, model, model_type=""):
        """
        Load Model using AML Flavor
        @param model: MLFLOW model
        @param model_type: optional (can be deprecated; apt model_type can be inferred from methods
        @return: AMLModel
        """
        from azureml.evaluate.mlflow.aml import AMLModel
        import azureml.evaluate.mlflow as mlflow_azureml
        if isinstance(model, str):
            model = mlflow_azureml.aml.load_model(model, model_type)
        elif isinstance(model, AMLModel):
            pass
        else:
            raise AzureMLMLFlowValueException(ErrorStrings.InvalidModelURI.format(instance="mlflow.aml.AMLModel"))
        return model

    def _log_predictions(self):
        """
        Logs predictions in csv file and upload it to AzureMLRun
        """
        pred_df = pd.DataFrame(self.X.copy())
        pred_df[self.label_columns] = self.y
        pred_df[PREDICTION_COLUMN_NAME] = self.predictions
        pred_df.to_csv(os.path.join(self.output_path, "predictions.csv"))
        self.run.upload_file(
            name="predictions.csv", path_or_stream=os.path.join(self.output_path, "predictions.csv"),
            datastore_name="workspaceblobstore"
        )
        if self.parent_run is not None:
            self.parent_run.upload_file(
                name="predictions.csv", path_or_stream=os.path.join(self.output_path, "predictions.csv"),
                datastore_name="workspaceblobstore"
            )

    def _log_metrics(self):
        """
        Log metrices in the run
        """
        table_scores = {}
        nonscalar_scores = {}
        classwise_scores = {}
        list_scores = {}

        for name, score in self.artifacts.items():
            if score is None:
                continue
            elif _scoring_utilities.is_table_metric(name):
                table_scores[name] = score
            elif name in self.list_metrics:
                try:
                    list_scores[name] = list(score)
                    if name == constants.Metric.FMPerplexity:
                        self.metrics["mean_" + name] = np.mean(score)
                except TypeError:
                    _logger.warning(f"{name} is not of type list.")
            elif name in constants.Metric.NONSCALAR_FULL_SET:
                nonscalar_scores[name] = score
            elif name in constants.FULL_NONSCALAR_SET:
                nonscalar_scores[name] = score
            elif name in constants.TrainingResultsType.ALL_TIME:
                # Filter out time metrics as we do not log these
                pass
            elif name in constants.FULL_CLASSWISE_SET:
                classwise_scores[name] = score
            else:
                _logger.warning("Unknown metric {}. Will not log.".format(name))

        # Log the scalar metrics. (Currently, these are stored in CosmosDB)
        for name, score in self.metrics.items():
            try:
                self.run.log(name, score)
                if self.parent_run is not None:
                    self.parent_run.log(name, score)
            except Exception:
                raise AzureMLMLFlowException(f"Failed to log scalar metric {name} with value {score}")

        for name, score in table_scores.items():
            try:
                self.run.log_table(name, score)
                if self.parent_run is not None:
                    self.parent_run.log_table(name, score)
            except Exception:
                raise AzureMLMLFlowException(f"Failed to log table metric {name} with value {score}")

        for name, score in list_scores.items():
            try:
                if len(score) >= 250:
                    continue
                self.run.log_list(name, score)
                if self.parent_run is not None:
                    self.parent_run.log_list(name, score)
            except Exception:
                raise AzureMLMLFlowException(f"Failed to log list metric {name} with value {score}")

        # Log the non-scalar metrics. (Currently, these are all artifact-based.)
        for name, score in nonscalar_scores.items():
            try:
                if name == constants.Metric.AccuracyTable:
                    self.run.log_accuracy_table(name, score)
                    if self.parent_run is not None:
                        self.parent_run.log_accuracy_table(name, score)
                elif name == constants.Metric.ConfusionMatrix:
                    self.run.log_confusion_matrix(name, score)
                    if self.parent_run is not None:
                        self.parent_run.log_confusion_matrix(name, score)
                elif name == constants.Metric.Residuals:
                    self.run.log_residuals(name, score)
                    if self.parent_run is not None:
                        self.parent_run.log_residuals(name, score)
                elif name == constants.Metric.PredictedTrue:
                    self.run.log_predictions(name, score)
                    if self.parent_run is not None:
                        self.parent_run.log_predictions(name, score)
                elif name == constants.Metric.IMAGE_LEVEL_BINARY_CLASSIFIER_METRICS:
                    self.run.log_table(name, score)
                    if self.parent_run is not None:
                        self.parent_run.log_table(name, score)
                elif name == constants.Metric.CONFUSION_MATRICES_PER_SCORE_THRESHOLD:
                    for key, confusion_matrix in score.items():
                        self.run.log_confusion_matrix(key, confusion_matrix)
                        if self.parent_run is not None:
                            self.parent_run.log_confusion_matrix(key, confusion_matrix)
                else:
                    _logger.warning("Unsupported non-scalar metric {}. Will not log.".format(name))
            except Exception:
                raise AzureMLMLFlowException(f"Failed to log non-scalar metric {name} with value {score}")

        # Log the classwise metrics. (Currently, these are all artifact-based.)
        for name, score in classwise_scores.items():
            try:
                if name == constants.Metric.PER_LABEL_METRICS:
                    for metrics in score.values():
                        self.run.log_table(name , metrics)
                        if self.parent_run is not None:
                            self.parent_run.log_table(name , metrics)
                else:
                    _logger.warning("Unsupported non-scalar metric {}. Will not log.".format(name))
            except Exception:
                raise AzureMLMLFlowException(f"Failed to log classwise metric {name} with value {score}")

    def _log_and_return_evaluation_result(self):
        """
        This function logs all of the produced metrics and artifacts (including custom metrics)
        along with model explainability. Then, returns an instance of EvaluationResult.
        :return:
        """
        self._log_predictions()
        self._log_metrics()
        keys = self.artifacts.keys()
        for k in keys:
            json_content = self.artifacts[k]
            json_artifact = JsonEvaluationArtifact(uri=azureml_mlflow.get_artifact_uri(k), content=json_content)
            self.artifacts[k] = json_artifact
        return EvaluationResult(self.metrics, self.artifacts)

    def _parse_aml_tracking_uri(self):
        """
        Parses workspace, resource_group, subscription from mlflow tracking uri which should be set to Azureml WS URI
        @return: workspace, resource_group, subscription
        """
        workspace, resource_group, subscription = None, None, None
        uri = azureml_mlflow.get_tracking_uri()
        if uri.startswith("azureml"):
            import re
            rg_pattern = re.compile("resourceGroups\/([\w+\-]*)\/")
            ws_pattern = re.compile("workspaces\/([\w+\-]*)?$")
            sub_pattern = re.compile("subscriptions\/([\w+\-]*)\/")
            try:
                resource_group = rg_pattern.findall(uri)[0]
                workspace = ws_pattern.findall(uri)[0]
                subscription = sub_pattern.findall(uri)[0]
            except Exception as e:
                _logger.error(f"Failed to parse AML Tracking URI with error : {repr(e)}")
                return None, None, None
        return workspace, resource_group, subscription

    def _set_run_config(self, run_id):
        self.run = Run.get_context()
        self.parent_run = None
        if isinstance(self.run, _OfflineRun):
            workspace, resource_group, subscription = self._parse_aml_tracking_uri()
            if workspace:
                ws = Workspace(subscription_id=subscription, workspace_name=workspace, resource_group=resource_group)
                self.run = Run.get(ws, run_id)
                # self.parent_run = self.run.parent
                # Not Adding parent logging right now
                self.parent_run = None
            else:
                _logger.warning("Failed to parse AzureML credentials. Using OfflineRun")
        else:
            self.parent_run = self.run.parent
        _logger.info(f"Setting up AML Run Config with run_id {self.run.id}")

    def evaluate(self,
                 *,
                 model,
                 model_type,
                 dataset,
                 run_id,
                 evaluator_config,
                 custom_metrics=None,
                 **kwargs):
        """
        Sets config, calls desired Evaluator to perform evaluation and logs the results
        @param model:
        @param model_type:
        @param dataset:
        @param run_id:
        @param evaluator_config:
        @param custom_metrics:
        @param kwargs:
        @return:
        """
        self._set_run_config(run_id)
        self.model = model
        self.model_type = model_type
        self.dataset = dataset
        self.run_id = run_id
        self.evaluator_config = evaluator_config
        self.dataset_name = dataset.name
        self.feature_names = dataset.feature_names
        self.custom_metrics = custom_metrics
        self.X = dataset.features_data
        self.y = dataset.labels_data
        self.label_columns = dataset.targets
        self.metrics = {}
        self.artifacts = {}
        self.output_path = evaluator_config.pop("output", DEFAULT_OUTPUT_FOLDER)

        if not os.path.exists(self.output_path):
            os.makedirs(self.output_path)

        if self.custom_metrics:
            raise NotImplementedError
        # This needs to be fixed and uncommented
        # inferred_model_type = _infer_model_type_by_labels(self.y)
        #
        # if inferred_model_type is not None and model_type != inferred_model_type:
        #     _logger.warning(
        #         f"According to the evaluation dataset label values, the model type looks like "
        #         f"{inferred_model_type}, but you specified model type {model_type}. Please "
        #         f"verify that you set the `model_type` and `dataset` arguments correctly."
        #     )

        self.evaluator = EvaluatorFactory().get_evaluator(model_type=model_type)
        metrics, predictions = self.evaluator.evaluate(model, self.X, self.y, **evaluator_config)
        if model_type == "forecaster":
            # If the model type is a forecaster, we cannot guarantee the same dimensions of input
            # and output, so we are returning a data frame and replace self.X and self.y
            # by the values taken from it.
            self.y = predictions.pop(ForecastColumns._ACTUAL_COLUMN_NAME).values
            self.X = predictions
            predictions = self.X.pop(ForecastColumns._FORECAST_COLUMN_NAME).values

        self.metrics.update(metrics[constants.Metric.Metrics])
        artifacts = metrics[constants.Metric.Artifacts]
        self.artifacts.update(artifacts)
        self.predictions = predictions

        return self._log_and_return_evaluation_result()

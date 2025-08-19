# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import logging
import numpy as np
import torch
import time

from typing import List, Dict

from azureml.evaluate.mlflow.aml import AzureMLInput
from azureml.evaluate.mlflow.models.evaluation.azureml._task_evaluator import TaskEvaluator
from azureml.evaluate.mlflow.models.evaluation.constants import (
    ArtifactLiterals,
    ODISLiterals,
    EvaluationSettingLiterals,
    EvaluationMetricsLiterals,
)
from azureml.evaluate.mlflow.exceptions import AzureMLMLFlowValueException
from azureml.evaluate.mlflow.constants import ErrorStrings
from azureml.metrics import compute_metrics as aml_compute_metrics, constants as aml_constants, list_metrics

_logger = logging.getLogger(__name__)


class ImageOdIsEvaluator(TaskEvaluator):

    def filter_and_convert_predictions(self, y_pred, image_meta_info, masks_required, box_score_threshold):
        """Filter and convert predictions.

        :param y_pred: Predictions, List of Dict with keys ["label", "score", "box", "polygon"]
        :param image_meta_info: List of Dict with keys ["height", "width", "is_crowd"]
        :param masks_required: Whether masks are required or not.
        :param box_score_threshold: Threshold for filtering predictions.
        """
        # common-component package is not in dependency list of evaluate-package.
        # but this is being installed in evaluate and prediction components
        # and ut gate for evaluate image tasks.
        from azureml.acft.common_components.image.runtime_common.object_detection.common.masktools import (
            convert_polygon_to_rle_masks,
            decode_rle_masks_as_binary_mask,
            encode_mask_as_rle
        )
        # converting y_pred as required by compute_metrics
        new_y_pred = []
        no_total_preds = 0
        no_valid_preds = 0
        for preds_per_image, image_meta_info in zip(y_pred, image_meta_info):
            new_pred = {}
            valid_preds = [idx for idx, pred in enumerate(preds_per_image)
                           if pred[ODISLiterals.SCORE] >= box_score_threshold]
            no_total_preds += len(preds_per_image)
            no_valid_preds += len(valid_preds)
            new_pred[ODISLiterals.LABELS] = np.empty(len(valid_preds), object)
            new_pred[ODISLiterals.SCORES] = np.empty(len(valid_preds))
            new_pred[ODISLiterals.BOXES] = np.empty((len(valid_preds), 4))
            if masks_required:
                new_pred[ODISLiterals.MASKS] = []

            height = image_meta_info[ODISLiterals.HEIGHT]
            width = image_meta_info[ODISLiterals.WIDTH]

            for array_idx, pred_idx in enumerate(valid_preds):
                new_pred[ODISLiterals.LABELS][array_idx] = preds_per_image[pred_idx][ODISLiterals.LABEL]
                new_pred[ODISLiterals.SCORES][array_idx] = preds_per_image[pred_idx][ODISLiterals.SCORE]
                box = preds_per_image[pred_idx][ODISLiterals.BOX]
                new_pred[ODISLiterals.BOXES][array_idx, :] = [
                    box[ODISLiterals.TOP_X] * width,
                    box[ODISLiterals.TOP_Y] * height,
                    box[ODISLiterals.BOTTOM_X] * width,
                    box[ODISLiterals.BOTTOM_Y] * height
                ]
                if masks_required:
                    polygon = preds_per_image[pred_idx][ODISLiterals.POLYGON]
                    for poly_idx in range(len(polygon)):
                        polygon_for_segment_i = polygon[poly_idx]
                        if len(polygon_for_segment_i) == 4:
                            # create another point in the middle of segmentation to
                            # avoid bug when using pycocotools, which thinks that a
                            # 4 value segmentation mask is a bounding box
                            x1, y1, x2, y2 = polygon_for_segment_i
                            if x2 == x1:
                                x = x1
                                y = (y2 + y1) // 2
                            elif y2 == y1:
                                x = (x2 + x1) // 2
                                y = y1
                            else:
                                a = (y2 - y1) / (x2 - x1)
                                b = y1 - a * x1
                                x = (x2 + x1) // 2
                                y = int(round(a * x + b))

                            new_segmentation = polygon_for_segment_i[:2] + [x, y] + polygon_for_segment_i[2:]
                            polygon[poly_idx] = new_segmentation
                            _logger.info(f"polygon length: {len(polygon[poly_idx])}")
                        for idx in range(0, len(polygon[poly_idx]), 2):
                            polygon[poly_idx][idx] = polygon[poly_idx][idx] * width
                            polygon[poly_idx][idx + 1] = polygon[poly_idx][idx + 1] * height
                    # convert each polygon to rle mask
                    rle_masks = convert_polygon_to_rle_masks(polygon=polygon, height=height, width=width)
                    if len(rle_masks):
                        # create binary mask from all the rle_masks
                        bin_mask = decode_rle_masks_as_binary_mask(rle_masks=rle_masks)
                        # convert bin mask to single rle mask.
                        rle_mask = encode_mask_as_rle(torch.asarray(bin_mask))
                        new_pred[ODISLiterals.MASKS].append(rle_mask)

            new_y_pred.append(new_pred)

        _logger.info(f"Valid predictions: {no_valid_preds} out of total"
                     f"predictions: {no_total_preds}, with box_score_threshold: {box_score_threshold}")
        return new_y_pred

    @staticmethod
    def predict(model,
                X_test: AzureMLInput,
                masks_required: bool = False,
                **kwargs):
        """Object detection and instance segmentation inference.

        :param model: The model to predict.
        :param X_test: The test data with coulmns ["image", "image_meta_info"]
        :param masks_required: Whether masks are required or not.
        :param kwargs: Additional arguments which are passed to model.predict
        :return: Predictions
        """
        batch_size = kwargs.get(EvaluationSettingLiterals.BATCH_SIZE, 1)
        # distributed case
        ngpus = torch.cuda.device_count()
        if ngpus > 1:
            batch_size = batch_size * ngpus
        params = {}
        if ODISLiterals.TEXT_PROMPT in X_test:
            params.update({
                ODISLiterals.TEXT_PROMPT : X_test[ODISLiterals.TEXT_PROMPT][0],
                ODISLiterals.CUSTOM_ENTITIES : True
            })

        return_preds = []
        start_time = time.time()
        for idx in range(0, len(X_test), batch_size):
            _logger.info(f"Predicting batch {idx} to {idx + batch_size}")
            batch_y_pred = model.predict(X_test.iloc[idx : idx + batch_size], params=params)

            batch_y_pred = batch_y_pred[ODISLiterals.BOXES]
            batch_y_pred = TaskEvaluator._convert_predictions(TaskEvaluator, batch_y_pred)

            return_preds.extend(batch_y_pred)

        end_time = time.time()
        infer_time = end_time - start_time
        infer_time_log = f"Total inference time {infer_time} for the data of length {len(X_test)}. " \
                         f"with batch_size: {batch_size} and number_of_gpus: {ngpus}"
        _logger.info(infer_time_log)

        return return_preds

    @staticmethod
    def compute_metrics(y_test: AzureMLInput,
                        y_pred: AzureMLInput,
                        image_meta_info: List[Dict],
                        masks_required: bool,
                        **kwargs):
        """Compute metrics for object detection and instance segmentation.

        :param y_test: pd.DataFrame with  coulmns ["labels"]
        :param y_pred: pd.DataFrame with coulmns ["labels"]
        :param image_meta_info: List of Dict with keys ["height", "width", "is_crowd"]
        :param masks_required: Whether masks are required or not.
        :param kwargs: Additional arguments["iou_threshold", "metrics"].
        :return: Metrics, Dict with keys metrics and artifacts
        """

        task_type = aml_constants.Tasks.IMAGE_INSTANCE_SEGMENTATION if masks_required else \
            aml_constants.Tasks.IMAGE_OBJECT_DETECTION
        iou_threshold = kwargs.pop(EvaluationSettingLiterals.IOU_THRESHOLD,
                                   EvaluationMetricsLiterals.DEFAULT_IOU_THRESHOLD)
        box_score_threshold = kwargs.pop(EvaluationSettingLiterals.BOX_SCORE_THRESHOLD,
                                         EvaluationMetricsLiterals.DEFAULT_BOX_SCORE_THRESHOLD)
        metrics_to_compute = kwargs.pop(EvaluationSettingLiterals.METRICS,
                                        list_metrics(task_type))

        y_pred = ImageOdIsEvaluator().filter_and_convert_predictions(y_pred, image_meta_info,
                                                                     masks_required, box_score_threshold)

        # create label map to convert labels to indexes for metrics computation
        all_labels = set()
        for pred in y_pred:
            all_labels.update(pred[ODISLiterals.LABELS])
        for test in y_test:
            all_labels.update(test[ODISLiterals.LABELS])

        all_labels = list(all_labels)
        all_labels.sort()
        num_classes = len(all_labels)
        label_map = {label_name: idx for idx, label_name in enumerate(all_labels)}

        for pred in y_pred:
            pred[ODISLiterals.CLASSES] = np.array([label_map[x] for x in pred[ODISLiterals.LABELS]])

        for test in y_test:
            test[ODISLiterals.CLASSES] = np.array([label_map[x] for x in test[ODISLiterals.LABELS]])

        metrics = aml_compute_metrics(
            task_type=task_type,
            y_test=y_test,
            y_pred=y_pred,
            num_classes=num_classes,
            image_meta_info=image_meta_info,
            iou_threshold=iou_threshold,
            metrics=metrics_to_compute
        )

        artifacts = metrics[ArtifactLiterals.ARTIFACTS]
        for artifact_name, artifact in artifacts.items():
            if artifact_name == aml_constants.Metric.CONFUSION_MATRICES_PER_SCORE_THRESHOLD:
                all_cfs = {}
                for threshold, confusion_matrix in artifact.items():
                    cf =\
                        {
                            ArtifactLiterals.DATA :
                            {
                                ArtifactLiterals.CLASS_LABELS : all_labels,
                                ArtifactLiterals.MATRIX : confusion_matrix
                            }
                        }
                    all_cfs["confusion_matrix_threshold_" + f"{threshold}"] = cf
                artifacts[aml_constants.Metric.CONFUSION_MATRICES_PER_SCORE_THRESHOLD] = all_cfs
            elif artifact_name == aml_constants.Metric.PER_LABEL_METRICS:
                new_metrics = {}
                for idx, label in enumerate(artifact):
                    new_metrics[ArtifactLiterals.LABEL_NAME] = all_labels[idx]
                    new_metrics.update(artifact[label])
                    artifact[label] = new_metrics.copy()
            elif artifact_name == aml_constants.Metric.IMAGE_LEVEL_BINARY_CLASSIFIER_METRICS:
                pass
            else:
                raise AzureMLMLFlowValueException(ErrorStrings.UnknownArtifact.format(artifact=artifact))
        return metrics

    def evaluate(self,
                 model,
                 X_test: AzureMLInput,
                 y_test: AzureMLInput,
                 **kwargs):
        """ Evaluate the image classifier model on the given test data.

        :param model: The model to evaluate.
        :param X_test: Pandas DataFrame with columns ["image", "image_meta_info"]
        :param y_test: Pandas DataFrame with columns ["labels"]
        :param kwargs: Additional arguments to evaluate model ["iou_threshold", "box_score_threshold",
        "masks_required", "metrics"]
        :return: The metrics - keys metrics and artifacts and predictions - List[Dict with keys bboxes].
        """

        masks_required = kwargs.pop(ODISLiterals.MASKS_REQUIRED)
        image_meta_info = X_test[ODISLiterals.IMAGE_META_INFO]

        y_pred = self.predict(model, X_test, masks_required, **kwargs)
        y_test = self._convert_predictions(y_test)

        metrics = ImageOdIsEvaluator.compute_metrics(y_test=y_test,
                                                     y_pred=y_pred,
                                                     image_meta_info=image_meta_info,
                                                     masks_required=masks_required,
                                                     **kwargs)

        return metrics, y_pred

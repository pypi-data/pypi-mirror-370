# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
""" Constants used for model evaluation."""


class EvaluationSettingLiterals:
    """Constants used for model evaluation settings."""

    MULTI_LABEL = "multilabel"
    IOU_THRESHOLD = "iou_threshold"
    BOX_SCORE_THRESHOLD = "box_score_threshold"
    METRICS = "metrics"
    BATCH_SIZE = "batch_size"


class EvaluationMetricsLiterals:
    """Defaults used for model evaluation metrics."""

    DEFAULT_IOU_THRESHOLD = 0.5
    DEFAULT_BOX_SCORE_THRESHOLD = 0.3


class EvaluationMiscLiterals:
    """Misc Lietrals"""

    IMAGE_OUTPUT_LABEL_COLUMN = "labels"
    IMAGE_OUTPUT_PROBS_COLUMN = "probs"
    THRESHOLD = "threshold"


class ODISLiterals:
    """Constants used for object detection and instance segmentation."""

    BOXES = "boxes"
    BOX = "box"
    CLASSES = "classes"
    CLASS = "class"
    SCORES = "scores"
    SCORE = "score"
    LABELS = "labels"
    LABEL = "label"
    IMAGE_META_INFO = "image_meta_info"
    TOP_X = "topX"
    TOP_Y = "topY"
    BOTTOM_X = "bottomX"
    BOTTOM_Y = "bottomY"
    NUM_CLASSES = "num_classes"
    MASKS = "masks"
    POLYGON = "polygon"
    HEIGHT = "height"
    WIDTH = "width"
    LABEL_INDEX = "label_index"
    MASKS_REQUIRED = "masks_required"
    TEXT_PROMPT = "text_prompt"
    CUSTOM_ENTITIES = "custom_entities"


class ArtifactLiterals:
    """Atrtifact Literals"""

    LABEL_NAME = "label_name"
    DATA = "data"
    CLASS_LABELS = "class_labels"
    MATRIX = "matrix"
    ARTIFACTS = "artifacts"


class EvaluationDefaultSetting:
    """Default settings for model evaluation."""
    MULTI_LABEL_PRED_THRESHOLD = 0.5

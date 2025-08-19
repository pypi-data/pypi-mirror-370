# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
class MODULE:
    TORCH = "torch"
    SKLEARN = "sklearn"
    TENSORFLOW = "tensorflow"


LOADING_MODULES = [MODULE.TORCH, MODULE.SKLEARN, MODULE.TENSORFLOW]

CLASSIFICATION = "classification"
REGRESSION = "regression"
FORECASTING = "forecasting"


class NLP:
    NER = "ner"
    MULTICLASS = "multiclass"
    MULTILABEL = "multilabel"


class VISION:
    CLASSIFICATION = "classification"
    OBJECT_DETECTION = "object_detection"


MODEL_TYPES = [CLASSIFICATION, REGRESSION, FORECASTING,
               NLP.NER, NLP.MULTICLASS, NLP.MULTILABEL,
               VISION.CLASSIFICATION, VISION.OBJECT_DETECTION]
MULTILCASS_SET = [CLASSIFICATION, NLP.MULTICLASS]
MULTILABEL_SET = [NLP.MULTILABEL, VISION.OBJECT_DETECTION]

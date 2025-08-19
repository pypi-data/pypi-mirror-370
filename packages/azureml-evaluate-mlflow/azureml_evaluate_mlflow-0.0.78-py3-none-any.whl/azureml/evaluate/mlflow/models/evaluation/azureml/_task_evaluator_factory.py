# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from azureml.evaluate.mlflow.models.evaluation.azureml._classifier_evaluator import ClassifierEvaluator
from azureml.evaluate.mlflow.models.evaluation.azureml._classifier_multilabel_evaluator import \
    ClassifierMultilabelEvaluator
from azureml.evaluate.mlflow.models.evaluation.azureml._forecaster_evaluator import ForecasterEvaluator
from azureml.evaluate.mlflow.models.evaluation.azureml._regressor_evaluator import RegressorEvaluator
from azureml.evaluate.mlflow.models.evaluation.azureml._translation_evaluator import TranslationEvaluator
from azureml.evaluate.mlflow.models.evaluation.azureml._qna_evaluator import QnAEvaluator
from azureml.evaluate.mlflow.models.evaluation.azureml._summarization_evaluator import SummarizationEvaluator
from azureml.evaluate.mlflow.models.evaluation.azureml._ner_evaluator import NerEvaluator
from azureml.evaluate.mlflow.models.evaluation.azureml._text_generation_evaluator import TextGenerationEvaluator
from azureml.evaluate.mlflow.models.evaluation.azureml._fill_mask_evaluator import FillMaskEvaluator
from azureml.evaluate.mlflow.models.evaluation.azureml._image_classifier_evaluator import ImageClassifierEvaluator
from azureml.evaluate.mlflow.models.evaluation.azureml._image_od_is_evaluator import ImageOdIsEvaluator


class EvaluatorFactory:
    def __init__(self):
        self._evaluators = {
            "classifier": ClassifierEvaluator,
            "classifier-multilabel": ClassifierMultilabelEvaluator,
            "multiclass": ClassifierEvaluator,
            "regressor": RegressorEvaluator,
            "ner": NerEvaluator,
            "text-ner": NerEvaluator,
            "text-classifier": ClassifierEvaluator,
            'text-classifier-multilabel': ClassifierMultilabelEvaluator,
            "translation": TranslationEvaluator,
            "summarization": SummarizationEvaluator,
            "question-answering": QnAEvaluator,
            "forecaster": ForecasterEvaluator,
            "text-generation": TextGenerationEvaluator,
            "fill-mask": FillMaskEvaluator,
            "image-classifier": ImageClassifierEvaluator,
            "image-classifier-multilabel": ImageClassifierEvaluator,
            "image-object-detection": ImageOdIsEvaluator,
            "image-instance-segmentation": ImageOdIsEvaluator,
        }

    @property
    def supported_tasks(self):
        return list(self._evaluators.keys())

    def get_evaluator(self, model_type):
        return self._evaluators[model_type]()

    def register(self, name, obj):
        self._evaluators[name] = obj

# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
""" Predictors for different tasks for HFTransformers Mlflow flavor"""
import importlib
import logging
import types
from abc import ABC, abstractmethod

import pandas as pd
import torch
import torch.cuda

from . import constants, utils
from .constants import ModelConstants

import numpy as np
from transformers import pipeline
from typing import Any
from azureml.evaluate.mlflow.hftransformers.utils import sanitize_load_args
from azureml.evaluate.mlflow.hftransformers.constants import Constants
from azureml.evaluate.mlflow.hftransformers.ner_pipeline import TokenClassificationCustomPipeline
from azureml.evaluate.mlflow.exceptions import AzureMLMLFlowUserException, AzureMLMLFlowTypeException
from azureml.evaluate.mlflow.constants import ErrorStrings

_logger = logging.getLogger(__name__)


def get_predictor(task_type: str, problem_type: str):
    """
    Helper function to return Predictor class based on task_type
    @param task_type: HuggingFace task type
    @param problem_type: multilabel or not
    @return: Return BasePredictor
    """
    if problem_type == constants.Constants.HF_SCRIPT_BASED_PREDICTION:
        return GenericScriptTaskPredictor
    if (task_type == "text-classification" and problem_type == Constants.MULTILABEL) or \
            task_type == constants.TaskTypes.MULTILABEL:
        return MultilabelPredictor
    if task_type == constants.TaskTypes.MULTICLASS or task_type == constants.TaskTypes.TEXT_CLASSIFICATION:
        return ClassificationPredictor
    elif task_type in [constants.TaskTypes.NER, constants.TaskTypes.TOKEN_CLASSIFICATION]:
        return NERPredictor
    elif task_type == constants.TaskTypes.QUESTION_ANSWERING:
        return QnAPredictor
    elif task_type == constants.TaskTypes.SUMMARIZATION:
        return SummarizationPredictor
    elif task_type == constants.TaskTypes.TRANSLATION or (isinstance(task_type, str) and "translation_" in task_type):
        return TranslationPredictor
    elif task_type == constants.TaskTypes.FILL_MASK:
        return FillMaskPredictor
    elif task_type == constants.TaskTypes.TEXT_GENERATION:
        return TextGenerationPredictor
    elif task_type == constants.TaskTypes.AUTOMATIC_SPEECH_RECOGNITION:
        return TTSPredictor
    elif task_type == constants.TaskTypes.TEXT_TO_IMAGE:
        return Text2ImagePredictor
    elif task_type == constants.TaskTypes.CONVERSATIONAL or task_type == constants.TaskTypes.CHAT_COMPLETION:
        return ChatCompletionPredictor
    _logger.error(f"Inference not support for task={task_type}. Please refer documentation for list of valid tasks")
    raise AzureMLMLFlowUserException(ErrorStrings.UnsupportedTaskType.format(task=task_type))


class BasePredictor(ABC):
    """Abstract BasePredictor Class"""

    def __init__(self, task_type: str, model, tokenizer, config, pipeline=None):
        """
        Initialize the paramteres required by Predictor
        @param task_type: Task type to be solved
        @param model: HF model to be predicted on
        @param tokenizer: HF Tokenizer to be used for prediction
        @param config: HF Config used by model
        """
        self.task_type = task_type
        self.experimental = pipeline is not None
        self.model = model
        self.tokenizer = tokenizer
        self.config = config
        self.pipeline = pipeline

    @abstractmethod
    def predict(self, data: Any, **kwargs: Any):
        """
        Abstract method required to be implemented by child classed
        @param data: Any
        @param kwargs: Any
        @return:
        """
        pass

    def _parse_data(self, data, **kwargs):
        """
        Helper to parse Data
        @param data: Numpy.NDarray, DataFrame
        @return: List data
        """
        preprocess_type = kwargs.get("type", None)
        keys = kwargs.get("keys", [])
        if isinstance(data, pd.DataFrame):
            keys = data.columns.to_list() if len(keys) == 0 else keys
            data = data[keys]
        if preprocess_type == constants.PreProcessingConstants.TEXT_PAIR:
            processed_data = utils.process_text_pairs(data, keys)
            if processed_data is not None:
                return processed_data
        seperator = kwargs.get("sep", ". ")
        return utils.concat_data_columns(data, seperator)

    def _get_set_label_mapping(self, **kwargs):
        """
        Get labels from model config or kwargs
        @param kwargs: dict
        @return: Train_labels
        """
        if isinstance(self.model, types.FunctionType):
            _logger.warning("model.config.id2label will not be "
                            "reset using train_label_list. This needs to be updated in the model directly. ")
            return {}
        if "train_label_list" not in kwargs and "class_labels" in kwargs:
            kwargs["train_label_list"] = kwargs["class_labels"]
        elif "train_label_list" not in kwargs and "train_labels" in kwargs:
            kwargs["train_label_list"] = kwargs["train_labels"]
        if "train_label_list" not in kwargs and not hasattr(self.model.config, 'id2label'):
            raise AzureMLMLFlowUserException(
                "Either set id2label in model.config or pass train_label_list in misc_conf "
                "while logging the model to use the .predict method."
            )
        if "train_label_list" not in kwargs:
            _logger.warning("train_label_list has not been passed. This might cause result in incorrect labels if the"
                            " model was finetuned on a new dataset")
            train_labels = self.model.config.id2label
        else:
            train_labels = {i: value for i, value in enumerate(kwargs["train_label_list"])}
            self.model.config.id2label = train_labels
        return train_labels

    def _parse_pipeline_results(self, data, key, depth=0):
        """
        Parse output returned by pipeline
        @param data: dict/list of dict/list of list of dict
        @param key: the key to return from final dict
        @return: list/value
        """
        result = []
        if isinstance(data, dict):
            return data[key] if depth != 0 else [
                data[key]]  # Some tasks (Qna) return a dict for input array of length 1
        if isinstance(data, list):
            for data_point in data:
                result.append(self._parse_pipeline_results(data_point, key, depth + 1))
        return result

    def _format_results(self, data, result):
        """
        Output format should be same as input data format. This has been added inline with pytorch format
        @param data: Incoming data
        @param result: output of predict
        @return: formatted output
        """
        if isinstance(data, pd.DataFrame):
            try:
                predicted = pd.DataFrame(result)
                predicted.index = data.index
            except Exception:
                _logger.warning("The output returned cannot be formatted as a DataFrame object. Returning the "
                                "results as array")
                predicted = result
        else:
            predicted = result
        return predicted

    def _get_pipeline_parameters(self, **kwargs):
        """
        Extract relevant kwargs to set in pipeline
        @param kwargs:
        @return:
        """
        pipeline_init_args = kwargs.pop("pipeline_init_args", {})
        parameters = {"device": kwargs.get("device", None),
                      "batch_size": kwargs.get("batch_size", None),
                      "model_kwargs": kwargs.pop("model_kwargs", None),
                      "pipeline_class": utils.get_custom_pipeline(**kwargs),
                      "trust_remote_code": kwargs.pop("trust_remote_code", True),
                      **sanitize_load_args(pipeline_init_args)}
        return parameters

    def _get_tokenizer_config(self, **kwargs):
        """
        Extract tokenizer config from kwargs
        :param kwargs: dict
        :return: Tokenizer Kwargs dict
        """
        output_config = {}
        if "tokenizer_config" in kwargs and isinstance(kwargs["tokenizer_config"], dict):
            output_config = kwargs["tokenizer_config"]
        if "generator_config" in kwargs and isinstance(kwargs["generator_config"], dict):
            output_config = {**output_config, **kwargs["generator_config"]}

        # Assumption is that we will never set the below parameters in tokenizer_config/generator_config
        if "addn_args" in kwargs:
            output_config = {**output_config, **kwargs["addn_args"]}
        if "max_gen_len" in output_config:
            output_config["max_new_tokens"] = output_config.pop("max_gen_len")
        return output_config

    def _preprocess_with_script(self, data, **kwargs):
        try:
            preprocess_script = kwargs.get("hf_preprocess_script", "preprocess")
            script = importlib.import_module(preprocess_script)
            return script.preprocess(data)
        except ImportError as e:
            _logger.warning(f"preprocess script not found: {e.msg}")
        except Exception as e:
            _logger.error(f"Error while processing the data using preprocess script: {repr(e)}")
        return data

    def _preprocess(self, data, **kwargs):
        data = self._preprocess_with_script(data, **kwargs)
        preprocessing_config = kwargs.get("preprocessing_config", {})
        preprocessing_config = preprocessing_config if isinstance(preprocessing_config, dict) else {}
        data = self._parse_data(data, **preprocessing_config)
        parameters = self._get_pipeline_parameters(**kwargs)
        return data, parameters


class ClassificationPredictor(BasePredictor):
    """Predictor for multi-class classification"""

    def _preprocess(self, data, **kwargs):
        """
        ToDo: USe Base class predictor after removing default processor of text_processor
        """
        data = self._preprocess_with_script(data, **kwargs)
        preprocessing_config = kwargs.get("preprocessing_config", {'type': constants.PreProcessingConstants.TEXT_PAIR})
        preprocessing_config = preprocessing_config if isinstance(preprocessing_config, dict) else {}
        data = self._parse_data(data, **preprocessing_config)
        parameters = self._get_pipeline_parameters(**kwargs)
        return data, parameters

    def _get_predictions(self, data: Any, top_k: int = None, **kwargs: Any):
        """
        Helper function to get Predictions from model
        @param data: Dataframe, np.ndArray
        @param kwargs: Any
        @return: probas, predicted_labels
        """
        data, pipeline_kwargs = self._preprocess(data, **kwargs)
        if self.experimental:
            model_pipeline = self.pipeline
        else:
            model_pipeline = pipeline("text-classification", model=self.model, tokenizer=self.tokenizer,
                                      **pipeline_kwargs)
        tokenizer_kwargs = {'padding': "max_length", 'truncation': True, **self._get_tokenizer_config(**kwargs)}
        if top_k is not None:
            tokenizer_kwargs['top_k'] = top_k
        else:
            tokenizer_kwargs['return_all_scores'] = True
        if "max_seq_length" in kwargs and "max_length" not in tokenizer_kwargs:
            tokenizer_kwargs["max_length"] = kwargs["max_seq_length"]
        result = model_pipeline(data, **tokenizer_kwargs)
        probs = self._parse_pipeline_results(result, 'score')
        labels = self._parse_pipeline_results(result, 'label')
        return probs, labels

    def predict(self, data: Any, **kwargs: Any):
        """
        Predict method to return predicted labels
        @param data: Dataframe, np.ndArray
        @param kwargs: Any
        @return: Labels predicted by model
        """
        if not self.experimental:
            _ = self._get_set_label_mapping(**kwargs)
        _, labels = self._get_predictions(data, top_k=1, **kwargs)
        labels = [label[0] for label in labels]
        return self._format_results(data, labels)

    def predict_proba(self, data, **kwargs):
        """
        Predict method to return predicted Probabilities
        @param data: Dataframe, np.ndArray
        @param kwargs: Any
        @return: Labels predicted by model
        """
        preds, _ = self._get_predictions(data, **kwargs)
        return self._format_results(data, preds)


class MultilabelPredictor(ClassificationPredictor):
    """Predictor for multi-label classification"""

    def _get_threshold(self, **kwargs):
        """
        Get threshold from kwargs
        """
        if "threshold" in kwargs:
            return kwargs["threshold"]
        return 0.5

    def _threshold_predict(self, preds, labels, threshold=0.5):
        """
        Thresholds the probabilities and return labels
        """
        final_labels = []
        for pred, label in zip(preds, labels):
            final_labels.append(str([label[j] for j, pred_value in enumerate(pred) if pred_value >= threshold]))
        return final_labels

    def predict(self, data, **kwargs):
        """
        Predict method to return predicted labels
        @param data: Dataframe, np.ndArray
        @param kwargs: Any
        @return: Labels predicted by model
        """
        if not self.experimental:
            _ = self._get_set_label_mapping(**kwargs)
        probas, labels = self._get_predictions(data, **kwargs)
        final_labels = self._threshold_predict(probas, labels, threshold=self._get_threshold(**kwargs))
        return self._format_results(data, final_labels)

    def predict_proba(self, data, **kwargs):
        """
        Predict method to return predicted Probabilities
        @param data: Dataframe, np.ndArray
        @param kwargs: Any
        @return: Labels predicted by model
        """
        preds, _ = self._get_predictions(data, **kwargs)
        return self._format_results(data, preds)


class NERPredictor(BasePredictor):
    """ Predictor for Token classification"""

    def __init__(self, task_type: str, model, tokenizer, config, pipeline=None):
        super().__init__(task_type, model, tokenizer, config, pipeline)
        if self.experimental:
            _logger.warning("Experimental not supported for NER tasks as of now")
            self.experimental = False
            self.model = model() if isinstance(self.model, types.FunctionType) else model

    def _get_pipeline_parameters(self, **kwargs):
        """
        Extract relevant kwargs to set in pipeline
        @param kwargs:
        @return:
        """
        pipeline_init_args = kwargs.pop("pipeline_init_args", {})
        parameters = {
            "model_kwargs": kwargs.pop("model_kwargs", None),
            "trust_remote_code": kwargs.pop("trust_remote_code", True),
            **sanitize_load_args(pipeline_init_args)}
        return parameters

    def predict(self, data_orig, **kwargs):
        """
        Predict method to return predicted entity for each word
        @param data_orig: Dataframe, np.ndArray
        @param kwargs: Any
        @return: Labels predicted by model
        """
        data, pipeline_kwargs = self._preprocess(data_orig, **kwargs)
        train_labels = self._get_set_label_mapping(**kwargs)
        if "max_seq_length" not in kwargs:
            pipeline_kwargs["max_seq_length"] = min(ModelConstants.MAX_SEQ_Length, self.tokenizer.model_max_length)
        tokenizer_config = self._get_tokenizer_config(**kwargs)
        if "max_length" in tokenizer_config:
            pipeline_kwargs["max_seq_length"] = tokenizer_config["max_length"]
        pipeline_kwargs["train_labels"] = train_labels
        model_pipeline = TokenClassificationCustomPipeline(task="token-classification", model=self.model,
                                                           tokenizer=self.tokenizer,
                                                           **pipeline_kwargs)
        result = model_pipeline(data, **tokenizer_config)
        return self._format_results(data_orig, result)


class QnAPredictor(BasePredictor):

    # Todo: Make it static method and share with QnAPipelinePredictor
    def _parse_data(self, data, **kwargs):
        """
        Helper to parse Data
        @param data: Numpy.NDarray, DataFrame
        @return: context, question
        """
        keys = kwargs.get("keys", None)
        if keys is not None and len(keys) < 2:
            raise AzureMLMLFlowTypeException(
                "Extractive QnA must have at least two columns set as keys in preprocessing_config corresponding to "
                "'context' and 'question'."
            )
        if isinstance(data, pd.DataFrame):
            columns = data.columns.to_list()
            if keys is None and "context" in columns and "question" in columns:
                keys = ["context", "question"]
            elif keys is None:
                _logger.warning("Assuming first column to be context and the second column to be question")
                keys = columns
            if len(columns) < 2 or keys[0] not in columns or keys[1] not in columns:
                raise AzureMLMLFlowTypeException(
                    "Extractive QnA must have at least two columns in Dataframe. The columns must match "
                    "the preprocessing_config keys if set."
                )
            question = data[keys[1]].to_list()
            context = data[keys[0]].to_list()
        elif isinstance(data, pd.Series):
            raise AzureMLMLFlowTypeException("For Extractive QnA at least two columns are required.")
        elif isinstance(data, np.ndarray):
            if data.ndim != 2:
                raise AzureMLMLFlowTypeException(
                    "The second dimension must be of size 2 corresponding to 'context' and 'question'.")
            context, question = np.hsplit(data, 2)
            context, question = list(context.ravel()), list(question.ravel())
        else:
            raise AzureMLMLFlowTypeException(ErrorStrings.UnsupportedDataType)
        return context, question

    def predict(self, data, **kwargs):
        """
        Predict method to return predicted answers from context for given question
        @param data: Dataframe, np.ndArray
        @param kwargs: Any
        @return: Answers identified by model
        """
        context, question = self._parse_data(data)
        pipeline_kwargs = self._get_pipeline_parameters(**kwargs)
        if not self.experimental:
            predictor = pipeline(task=self.task_type, model=self.model, tokenizer=self.tokenizer, config=self.config,
                                 **pipeline_kwargs)
        else:
            predictor = self.pipeline
        tokenizer_config = self._get_tokenizer_config(**kwargs)
        outputs = predictor(context=context, question=question, **tokenizer_config)
        result = self._parse_pipeline_results(outputs, 'answer')
        return self._format_results(data, result)


class TranslationPredictor(BasePredictor):

    def predict(self, data_orig, **kwargs):
        """
        Predict method to return predicted answers from context for given question
        @param data: Dataframe, np.ndArray
        @param kwargs: dict
        @return: List Answers identified by model
        """
        data, pipeline_kwargs = self._preprocess(data_orig, **kwargs)
        # ToDo check for correct task_type
        tokenizer_config = self._get_tokenizer_config(**kwargs)
        if not self.experimental:
            predictor = pipeline(task=self.task_type, model=self.model, tokenizer=self.tokenizer, config=self.config,
                                 **pipeline_kwargs)
        else:
            predictor = self.pipeline
        outputs = predictor(list(data), **tokenizer_config)
        result = self._parse_pipeline_results(outputs, 'translation_text')
        return self._format_results(data_orig, result)


class SummarizationPredictor(BasePredictor):

    def predict(self, data_orig, **kwargs):
        """
        Predict method to return Summary of text
        @param data: Dataframe, np.ndArray
        @param kwargs: dict
        @return: List Answers identified by model
        """
        data, pipeline_kwargs = self._preprocess(data_orig, **kwargs)
        if not self.experimental:
            predictor = pipeline(task=self.task_type, model=self.model, tokenizer=self.tokenizer, config=self.config,
                                 **pipeline_kwargs)
        else:
            predictor = self.pipeline
        tokenizer_config = self._get_tokenizer_config(**kwargs)
        outputs = predictor(list(data), **tokenizer_config)
        result = self._parse_pipeline_results(outputs, 'summary_text')
        return self._format_results(data_orig, result)


class FillMaskPredictor(BasePredictor):

    def _parse_pipeline_results(self, data, key, depth=0):
        """
        Parse output returned by pipeline
        Return the token with highest score only
        @param data: dict/list of dict/list of list of dict
        @param key: the key to return from final dict
        @return: list/value
        """
        result = []
        if isinstance(data, dict):
            return data[key] if depth != 0 else [
                data[key]]  # Some tasks return a dict for input array of length 1
        if isinstance(data, list):
            for data_point in data:
                return_value = self._parse_pipeline_results(data_point, key, depth + 1)
                result.append(return_value)
                # For Fill-mask we need the token with highest score only
                if not isinstance(return_value, list) and isinstance(data_point, dict):
                    return return_value
        return result

    def predict(self, data_orig, **kwargs):
        """
        Predict method to return predicted token
        @param data: Dataframe, np.ndArray
        @param kwargs: dict
        @return: List Answers identified by model
        """
        data, pipeline_kwargs = self._preprocess(data_orig, **kwargs)
        if not self.experimental:
            predictor = pipeline(task=self.task_type, model=self.model, tokenizer=self.tokenizer, config=self.config,
                                 **pipeline_kwargs)
        else:
            predictor = self.pipeline
        tokenizer_config = self._get_tokenizer_config(**kwargs)
        outputs = predictor(list(data), **tokenizer_config)
        result = self._parse_pipeline_results(outputs, 'token_str')
        if not isinstance(result, list):  # Input Only support ndarray or Dataframe
            return self._format_results(data_orig, [result])
        if len(data) == 1 and len(result) != 1:
            return self._format_results(data_orig, [",".join(result)])
        final_result = []
        # Final result type needs to be determined
        for res in result:
            final_result.append(",".join(res) if isinstance(res, list) and isinstance(data_orig, pd.DataFrame) else
                                res)
        return self._format_results(data_orig, final_result)


class TextGenerationPredictor(BasePredictor):

    def predict(self, data_orig, **kwargs):
        """
        Predict method to return predicted token
        @param data: Dataframe, np.ndArray
        @param kwargs: dict
        @return: List Answers identified by model
        """
        data, pipeline_kwargs = self._preprocess(data_orig, **kwargs)
        if not self.experimental:
            predictor = pipeline(task=self.task_type, model=self.model, tokenizer=self.tokenizer, config=self.config,
                                 **pipeline_kwargs)
        else:
            predictor = self.pipeline
        tokenizer_config = self._get_tokenizer_config(**kwargs)
        outputs = predictor(list(data), **tokenizer_config)
        result = self._parse_pipeline_results(outputs, 'generated_text')
        return self._format_results(data_orig, result)


class ChatCompletionPredictor(BasePredictor):

    @classmethod
    def _create_conversation(cls, conv_arr, **kwargs):
        assert isinstance(conv_arr, list), "Each data point should be a conversation array"
        B_SYS = kwargs.get("B_SYS", "<<SYS>>\n")
        E_SYS = kwargs.get("E_SYS", "\n<</SYS>>\n\n")
        assert len(conv_arr) > 0, "Conversation is empty"
        assert conv_arr[-1]["role"] == "user", "Last role should be 'user'"

        next_turn = "system" if conv_arr[0]["role"] == "system" else "user"
        conversation = []

        for i, conv in enumerate(conv_arr):
            if conv["role"] == "system":
                assert next_turn == "system", "System prompts can only be set at the start of the conversation"
                next_turn = "user"
                conversation.append({
                    "role": "system",
                    "content": B_SYS + conv["content"].strip() + E_SYS
                })
            elif conv["role"] == "assistant":
                assert next_turn == "assistant", "Invalid turn. Expected assistant input"
                next_turn = "user"
                conversation.append({
                    "role": "assistant",
                    "content": conv["content"].strip()
                })
            elif conv["role"] == "user":
                assert next_turn == "user", "Invalid turn. Expected user input"
                next_turn = "assistant"
                conversation.append({
                    "role": "user",
                    "content": conv["content"].strip()
                })

        return conversation

    def _parse_pipeline_results(self, data, key="", depth=0):
        """
        Parse output returned by pipeline
        @param data: dict/list of dict/list of list of dict
        @param key: the key to return from final dict
        @return: list/value
        """
        result = []
        if not isinstance(data, list):
            raise AzureMLMLFlowUserException("Expected conversations as output of the conversational pipeline.")
        for data_point in data:
            result.append(data_point.generated_responses[-1])
        return result

    @classmethod
    def _parse_data(cls, data, **kwargs):
        """
        Helper to parse Data
        @param data: Numpy.NDarray, DataFrame
        @return: List data
        """
        if isinstance(data, pd.DataFrame):
            data = data[data.columns[0]].tolist()
        else:
            raise AzureMLMLFlowUserException("Only Pandas dataframe supported currently.")
        if len(data) < 1:
            raise AzureMLMLFlowUserException(f"Expected at least one data point. Found {len(data)}.")
        if isinstance(data[0], dict):
            return [cls._create_conversation(data, **kwargs)]
        else:
            return [cls._create_conversation(conv, **kwargs) for conv in data]

    def _preprocess(self, data, **kwargs):
        data = self._preprocess_with_script(data, **kwargs)
        preprocessing_config = kwargs.get("preprocessing_config", {})
        preprocessing_config = preprocessing_config if isinstance(preprocessing_config, dict) else {}
        data = self._parse_data(data, **preprocessing_config)
        parameters = self._get_pipeline_parameters(**kwargs)
        return data, parameters

    def predict(self, data_orig, **kwargs):
        """
        Predict method to return predicted token
        @param data: Dataframe, np.ndArray
        @param kwargs: dict
        @return: List Answers identified by model
        """
        data, pipeline_kwargs = self._preprocess(data_orig, **kwargs)
        if not self.experimental:
            predictor = pipeline(task="text-generation", model=self.model, tokenizer=self.tokenizer,
                                 config=self.config, **pipeline_kwargs)
        else:
            predictor = self.pipeline
        tokenizer_config = self._get_tokenizer_config(**kwargs)
        outputs = predictor(list(data), **tokenizer_config)
        # if isinstance(outputs, Conversation):
        #     outputs = [outputs]
        # result = self._parse_pipeline_results(outputs)

        result = []

        if outputs is None or len(outputs) == 0:
            _logger.warning("ChatPipeline: Empty outputs returned.")
            return result

        if isinstance(outputs[0], dict):
            result = [outputs[0]["generated_text"][-1]["content"]]
        else:
            for output in outputs:
                result.append(output[0]["generated_text"][-1]["content"])

        return self._format_results(data_orig, result)


class FeatureExtractionPredictor(BasePredictor):

    def predict(self, data_orig, **kwargs):
        """
        Predict method to return predicted token
        @param data: Dataframe, np.ndArray
        @param kwargs: dict
        @return: List Answers identified by model
        """
        data, pipeline_kwargs = self._preprocess(data_orig, **kwargs)
        if not self.experimental:
            predictor = pipeline(task=self.task_type, model=self.model, tokenizer=self.tokenizer, config=self.config,
                                 **pipeline_kwargs)
        else:
            predictor = self.pipeline
        tokenizer_config = self._get_tokenizer_config(**kwargs)
        outputs = predictor(list(data), **tokenizer_config)
        return self._format_results(data_orig, outputs)


class GenericScriptTaskPredictor(BasePredictor):
    """Predictor for multi-label classification"""

    def _get_predict_module(self, **kwargs):
        module_name = kwargs.get("hf_predict_module", "predict")
        try:
            predict_module = importlib.import_module(module_name)
            return predict_module
        except ImportError as e:
            _logger.warning("{} script not found. Exception: {}".format(module_name, str(e)))
        except Exception as e:
            _logger.error("Error while importing the predict module {}".format(str(e)))

    def predict(self, data, **kwargs):
        """
        Predict method to return predicted labels
        @param data: Dataframe, np.ndArray
        @param kwargs: Any
        @return: Labels predicted by model
        """
        data = self._preprocess_with_script(data, **kwargs)
        predict_module = self._get_predict_module(**kwargs)
        if not hasattr(predict_module, "predict"):
            _logger.error("Predict Module does not has a predict method")
            raise AzureMLMLFlowUserException(ErrorStrings.MethodDoesNotExist.format(module=predict_module,
                                                                                    method="predict"))
        return predict_module.predict(data, task=self.task_type, model=self.model, tokenizer=self.tokenizer,
                                      config=self.config, pipeline=self.pipeline, **kwargs)

    def predict_proba(self, data, **kwargs):
        """
        Predict method to return predicted Probabilities
        @param data: Dataframe, np.ndArray
        @param kwargs: Any
        @return: Labels predicted by model
        """
        data = self._preprocess_with_script(data, **kwargs)
        predict_module = self._get_predict_module(**kwargs)
        if not hasattr(predict_module, "predict_proba"):
            _logger.error("Predict Module does not has a predict method")
            raise AzureMLMLFlowUserException(ErrorStrings.MethodDoesNotExist.format(module=predict_module,
                                                                                    method="predict_proba"))
        return predict_module.predict_proba(data, task=self.task_type, model=self.model, tokenizer=self.tokenizer,
                                            config=self.config, pipeline=self.pipeline, **kwargs)


class TTSPredictor(BasePredictor):

    def _parse_data(self, data, **kwargs):
        """
        Helper to parse Data
        @param data: Numpy.NDarray, DataFrame
        @return: List data
        """
        keys = kwargs.get("keys", [])
        if isinstance(data, pd.DataFrame):
            keys = data.columns.to_list() if len(keys) == 0 else keys
            data = data[keys]
            return data.to_dict('records').copy()
        return data  # ToDo: Need to add support for other data types

    def _preprocess(self, data, **kwargs):
        data = self._preprocess_with_script(data, **kwargs)
        preprocessing_config = kwargs.get("preprocessing_config", {})
        preprocessing_config = preprocessing_config if isinstance(preprocessing_config, dict) else {}
        data = self._parse_data(data, **preprocessing_config)
        parameters = self._get_pipeline_parameters(**kwargs)
        return data, parameters

    def predict(self, data_orig, **kwargs):
        """
        Predict method to return predicted token
        @param data: Dataframe, np.ndArray
        @param kwargs: dict
        @return: List Answers identified by model
        """
        data, pipeline_kwargs = self._preprocess(data_orig, **kwargs)
        if not self.experimental:
            feature_extractor = getattr(self.tokenizer, "feature_extractor", None)
            tokenizer = getattr(self.tokenizer, "tokenizer", None)
            if feature_extractor is None or tokenizer is None:
                raise AzureMLMLFlowUserException(
                    "For Automatic speech recognition, both tokenizer and feature extractor are supposed to be"
                    " attributes of processor (tokenizer)"
                )
            predictor = pipeline(task=self.task_type, model=self.model, tokenizer=tokenizer, config=self.config,
                                 feature_extractor=feature_extractor,
                                 **pipeline_kwargs)
        else:
            predictor = self.pipeline
        tokenizer_config = self._get_tokenizer_config(**kwargs)
        outputs = self._parse_pipeline_results(predictor(data, **tokenizer_config), 'text')  # , )
        return self._format_results(data_orig, outputs)


class Text2ImagePredictor(BasePredictor):
    def _parse_data(self, data, **kwargs):
        """
        Helper to parse Data
        @param data: Numpy.NDarray, DataFrame
        @return: List data
        """
        keys = kwargs.get("keys", [])
        if isinstance(data, pd.DataFrame):
            keys = data.columns.to_list() if len(keys) == 0 else keys
            data = data[keys[0]]
            return data.tolist()
        elif isinstance(data, np.ndarray):
            return data.tolist()
        return data  # ToDo: Need to add support for other data types

    def _get_pipeline_parameters(self, **kwargs):
        """
        Extract relevant kwargs to set in pipeline
        @param kwargs:
        @return:
        """
        parameters = {
            "local_files_only": kwargs.get("local_files_only", False),
        }
        if "low_cpu_mem_usage" in kwargs:
            parameters["low_cpu_mem_usage"] = kwargs.get("low_cpu_mem_usage")
        return parameters

    def _get_pipeline_exec_parameters(self, **kwargs):
        """
        Extract relevant kwargs to set in pipeline
        @param kwargs:
        @return:
        """
        parameters = {
            "height": kwargs.get("height", None),
            "width": kwargs.get("width", None),
            "num_inference_steps": kwargs.get("num_inference_steps", 50),
            "num_images_per_prompt": kwargs.get("num_images_per_prompt", 1),
            "generator": kwargs.get("generator", None),
            "device": kwargs.get("device", None),
        }
        return parameters

    def _preprocess(self, data, **kwargs):
        data = self._preprocess_with_script(data, **kwargs)
        preprocessing_config = kwargs.get("preprocessing_config", {})
        preprocessing_config = preprocessing_config if isinstance(preprocessing_config, dict) else {}
        data = self._parse_data(data, **preprocessing_config)
        parameters = self._get_pipeline_parameters(**kwargs)
        return data, parameters

    def _format_results(self, data, result):
        """
        Output format should be same as input data format. This has been added inline with pytorch format
        @param data: Incoming data
        @param result: output of predict
        @return: formatted output
        """
        if isinstance(data, pd.DataFrame):
            try:
                import io
                import base64

                def convert_pil_to_base64(img):
                    with io.BytesIO() as buf:
                        img.save(buf, format='JPEG')
                        return base64.encodebytes(buf.getbuffer().tobytes()).decode('utf-8')

                predicted = pd.DataFrame(result)
                predicted.index = data.index
                predicted['images'] = predicted['images'].apply(convert_pil_to_base64)
            except Exception:
                _logger.warning("The output returned cannot be formatted as a DataFrame object. Returning the "
                                "results as array")
                predicted = result
        else:
            predicted = result
        return predicted

    def predict(self, data_orig: Any, **kwargs: Any):
        # from diffusers import DPMSolverMultistepScheduler

        data, pipeline_kwargs = self._preprocess(data_orig, **kwargs)
        predictor = self.model
        # predictor.scheduler = DPMSolverMultistepScheduler.from_config(predictor.scheduler.config)
        pipeline_exec_kwargs = self._get_pipeline_exec_parameters(**kwargs)
        device = pipeline_exec_kwargs.pop("device", "cuda")
        if device != "cpu" and torch.cuda.is_available():
            predictor = predictor.to(device)
        results = predictor(data, **pipeline_exec_kwargs)
        results = self._format_results(data_orig, results)
        return results

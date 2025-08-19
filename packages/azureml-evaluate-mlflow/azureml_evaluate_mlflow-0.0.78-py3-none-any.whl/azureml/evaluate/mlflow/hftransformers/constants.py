# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
class DataLiterals:
    NER_IGNORE_TOKENS = ["", " ", "\n"]


class ModelConstants:
    MAX_SEQ_Length = 512


class Constants:
    MULTILABEL = "multi_label_classification"
    HF_SCRIPT_BASED_PREDICTION = "script_prediction"
    EXPERIMENTAL_FLAG = "exp"
    CUSTOM_CONFIG_MODULE = "custom_config_module"
    HF_CONFIG_CLASS = "hf_config_class"
    CUSTOM_TOKENIZER_MODULE = "custom_tokenizer_module"
    HF_TOKENIZER_CLASS = "hf_tokenizer_class"
    CUSTOM_MODEL_MODULE = "custom_model_module"
    HF_PRETRAINED_CLASS = "hf_pretrained_class"


class PreProcessingConstants:
    TEXT_PAIR = "text_pair"
    CONCAT = "concat"


class AdditionalPackages:
    EVALUATE_PACKAGE = "azureml-evaluate-mlflow"


class TaskTypes:
    MULTICLASS = "multiclass"
    MULTILABEL = "multilabel"
    TEXT_CLASSIFICATION = "text-classification"
    NER = "ner"
    TOKEN_CLASSIFICATION = "token-classification"
    QUESTION_ANSWERING = "question-answering"
    SUMMARIZATION = "summarization"
    TRANSLATION = "translation"
    FILL_MASK = "fill-mask"
    TEXT_GENERATION = "text-generation"
    AUTOMATIC_SPEECH_RECOGNITION = "automatic-speech-recognition"
    TEXT_TO_IMAGE = "text-to-image"
    CONVERSATIONAL = "conversational"
    CHAT_COMPLETION = "chat-completion"

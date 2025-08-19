# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import tempfile

import yaml

from ..models.utils import (  # pylint: disable=unused-import
    get_multiclass_model_class,
    newsgroup_dataset,
    PyTorchClassificationDatasetWrapper
)
import azureml.evaluate.mlflow as mlflow
from azureml.evaluate.mlflow.constants import ErrorStrings
import numpy as np
from huggingface_hub import snapshot_download
import sklearn.datasets
from transformers import AutoModelForSequenceClassification, AutoModelForSeq2SeqLM, AutoModelForQuestionAnswering, \
    AutoModelForMaskedLM, AutoModelForCausalLM
from transformers import AutoTokenizer
from transformers import AutoConfig
from transformers import Trainer, default_data_collator
import pytest
import os
from datasets import load_dataset
import pandas as pd
from transformers import pipeline
from diffusers import StableDiffusionPipeline, DPMSolverMultistepScheduler
import torch
import io
import base64
from tests.helper_functions import delete_directory


@pytest.fixture
def model_path(tmpdir, subdir="model"):
    return os.path.join(str(tmpdir), subdir)


def extra_files():
    pass


@pytest.mark.hftest3
@pytest.mark.usefixtures("new_clean_dir")
def test_multiclass_model_save_load(newsgroup_dataset, model_path):  # noqa: F811
    train_labels = newsgroup_dataset['train_labels']
    newsgroup_dataset = newsgroup_dataset['dataset']
    config = AutoConfig.from_pretrained("bert-base-uncased", num_labels=len(train_labels), output_attentions=False,
                                        output_hidden_states=False)
    config.id2label = train_labels
    model = AutoModelForSequenceClassification.from_pretrained(
        "bert-base-uncased",
        config=config
    )
    tokenizer = AutoTokenizer.from_pretrained('bert-base-uncased', config=config)
    trainer = Trainer(
        model=model,
        tokenizer=tokenizer,
        data_collator=default_data_collator,
    )
    df = newsgroup_dataset._constructor_args["data"]
    df.drop(['y'], inplace=True, axis=1)
    dataset_wrapper = PyTorchClassificationDatasetWrapper(df, tokenizer, 128)
    pred = trainer.predict(dataset_wrapper)
    hf_conf = {
        'task_type': 'multiclass',
        "hf_flavor": "hftransformers"
    }
    mlflow.hftransformers.save_model(model, model_path, tokenizer=tokenizer, config=config, hf_conf=hf_conf)
    with open(os.path.join(model_path, "MLmodel"), "r") as stream:
        mlmodel_file = yaml.safe_load(stream)
        assert "hftransformersv2" not in mlmodel_file["flavors"]
        assert "hftransformers" in mlmodel_file["flavors"]
    reloaded_task_type, r_model, r_tokenizer, r_config = mlflow.hftransformers.load_model(model_path)
    trainer2 = Trainer(
        model=r_model,
        tokenizer=r_tokenizer,
        data_collator=default_data_collator,
    )
    pred2 = trainer2.predict(dataset_wrapper)
    np.testing.assert_array_almost_equal(
        pred.predictions, pred2.predictions, decimal=4
    )
    pyfunc_loaded = mlflow.pyfunc.load_model(model_path)
    preds = np.argmax(pred.predictions, axis=1)
    predicted_labels = [train_labels[item] for item in preds]
    pyfunc_preds = pyfunc_loaded.predict(dataset_wrapper.data)
    pyfunc_preds = pyfunc_preds[pyfunc_preds.columns[0]].values
    # ToDo: Check this, not working after latest change
    # np.testing.assert_array_equal(
    #     pyfunc_preds, predicted_labels
    # )
    delete_directory(model_path)



@pytest.mark.hftest3
@pytest.mark.usefixtures("new_clean_dir")
def test_multiclass_model_save_load_with_extra_files(newsgroup_dataset, model_path):  # noqa: F811
    train_labels = newsgroup_dataset['train_labels']
    newsgroup_dataset = newsgroup_dataset['dataset']
    config = AutoConfig.from_pretrained("bert-base-uncased", num_labels=len(train_labels), output_attentions=False,
                                        output_hidden_states=False)

    config.id2label = train_labels
    model = AutoModelForSequenceClassification.from_pretrained(
        "bert-base-uncased",
        config=config
    )
    tokenizer = AutoTokenizer.from_pretrained('bert-base-uncased', config=config)
    trainer = Trainer(
        model=model,
        tokenizer=tokenizer,
        data_collator=default_data_collator,
    )
    df = newsgroup_dataset._constructor_args["data"]
    df.drop(['y'], inplace=True, axis=1)
    dataset_wrapper = PyTorchClassificationDatasetWrapper(df, tokenizer, 512)
    pred = trainer.predict(dataset_wrapper)
    hf_conf = {
        'task_type': 'multiclass',
        'hf_flavor': 'hftransformersv2'
    }
    mlflow.hftransformers.save_model(model, model_path, tokenizer=tokenizer, config=config, hf_conf=hf_conf)
    with open(os.path.join(model_path, "MLmodel"), "r") as stream:
        mlmodel_file = yaml.safe_load(stream)
        assert "hftransformersv2" in mlmodel_file["flavors"]
        assert "hftransformers" not in mlmodel_file["flavors"]
    reloaded_task_type, r_model, r_tokenizer, r_config = mlflow.hftransformers.load_model(model_path)
    # trainer2 = Trainer(
    #     model=r_model,
    #     tokenizer=r_tokenizer,
    #     data_collator=default_data_collator,
    # )
    # pred2 = trainer2.predict(dataset_wrapper)
    # np.testing.assert_array_almost_equal(
    #     pred.predictions, pred2.predictions, decimal=4
    # )
    pyfunc_loaded = mlflow.pyfunc.load_model(model_path)
    preds = np.argmax(pred.predictions, axis=1)
    predicted_labels = [train_labels[item] for item in preds]
    pyfunc_preds = pyfunc_loaded.predict(dataset_wrapper.data)
    pyfunc_preds = pyfunc_preds[pyfunc_preds.columns[0]].values
    np.testing.assert_array_equal(
        pyfunc_preds, predicted_labels
    )
    delete_directory(model_path)

@pytest.fixture
def dataset_opus():
    books = load_dataset("opus_books", "en-fr")
    books = books["train"].train_test_split(test_size=0.1)
    source, target = 'en', 'fr'
    source_texts, target_texts = [], []
    for i in range(5):
        item = books["test"][i]
        source_texts.append(item['translation'][source])
        target_texts.append(item['translation'][target])
    df = pd.DataFrame({'X': source_texts, 'y': target_texts})
    return df


@pytest.fixture
def dataset_billsum():
    articles = ['''the past decades have seen tremendous success in the implementation of control schemes for the motional state of matter via light fields either in free space or in optical cavities . 
    a diversity of examples exist where the quantum regime of motion has been reached . 
    the masses span many orders of magnitude , from the microscopic atomic size systems such as atoms in optical cavities  @xcite and laser - cooled ions in ion traps  @xcite to the macroscopic level with cavity - embedded membranes  @xcite , mirrors  @xcite or levitated dielectric nano - particles  @xcite .    a common interaction hamiltonian that well approximates many quantum light 
    matter interfaces is quadrature  quadrature coupling  @xcite ; more specifically , the displacement of the mechanics is coupled directly to a quadrature of the high-@xmath0 optical field mode that can be then used as an observable for indirect position detection . adding a second mechanical system coupled to the field then allows one to engineer an effective two - particle mechanical coupling by eliminating the mediating light mode . 
    recently , an expansion to quadratic coupling has been proposed  @xcite and the investigation of dissipation - induced  @xcite , noise - induced  @xcite and remote entanglement  @xcite has been of great interest , including a scheme for sensitive force measurements  @xcite and entanglement of macroscopic oscillators  @xcite . 
    here we show that all this can be implemented in a system consisting of two particles strongly trapped in the cosine mode of a ring cavity , where the two - particle interaction is carried by sideband photons in the sine mode . 
    for deep trapping it yields the typical linearized optomechanical hamiltonian  @xcite . ''']
    test_dataset = pd.DataFrame({"articles": articles})
    return test_dataset


@pytest.fixture
def dataset_squad_qna():
    squad = load_dataset("squad")
    squad = squad["train"].train_test_split(test_size=0.2)
    test_dataset = squad["test"][:3]
    context, questions = [], []
    for i in range(len(test_dataset["context"])):
        context.append(test_dataset["context"][i])
        questions.append(test_dataset["question"][i])
    df = pd.DataFrame({'question': questions, 'context': context})
    return df


@pytest.mark.hftest2
@pytest.mark.usefixtures("new_clean_dir")
def test_hf_translation_model_save_load_predict(dataset_opus, model_path):
    model_name = 't5-small'
    source_lang, target_lang = 'en', 'fr'
    config = AutoConfig.from_pretrained(model_name)
    model = AutoModelForSeq2SeqLM.from_pretrained(model_name, config=config)
    tokenizer = AutoTokenizer.from_pretrained(model_name, padding=True, truncation=True)
    task_type = 'translation_en_to_fr'
    predictor = pipeline(task=task_type, model=model, tokenizer=tokenizer, config=config)
    outputs = predictor(list(dataset_opus['X']))
    result1 = [output['translation_text'] for output in outputs]
    hf_conf = {
        'task_type': task_type,
        'hf_flavor': None
    }
    mlflow.hftransformers.save_model(model, model_path, tokenizer=tokenizer, config=config, hf_conf=hf_conf)
    with open(os.path.join(model_path, "MLmodel"), "r") as stream:
        mlmodel_file = yaml.safe_load(stream)
        assert "hftransformersv2" in mlmodel_file["flavors"]
        assert "hftransformers" not in mlmodel_file["flavors"]
    reloaded_task_type, r_model, r_tokenizer, r_config = mlflow.hftransformers.load_model(model_path)
    predictor = pipeline(task=task_type, model=r_model, tokenizer=r_tokenizer, config=r_config)
    outputs = predictor(list(dataset_opus['X']))
    result2 = [output['translation_text'] for output in outputs]

    np.testing.assert_array_equal(
        result1, result2
    )
    pyfunc_loaded = mlflow.pyfunc.load_model(model_path)
    pyfunc_preds = pyfunc_loaded.predict(dataset_opus['X'])
    np.testing.assert_array_equal(
        pyfunc_preds, result1
    )
    delete_directory(model_path)


@pytest.mark.hftest4
@pytest.mark.usefixtures("new_clean_dir")
def test_hf_translation_model_save_load_predict_hub_download(dataset_opus, model_path):
    model_name = 't5-small'
    path_to_model = snapshot_download(repo_id=model_name)
    task_type = 'translation_en_to_fr'
    predictor = pipeline(task=task_type, model=path_to_model)
    outputs = predictor(list(dataset_opus['X']))
    result1 = [output['translation_text'] for output in outputs]
    hf_conf = {
        'task_type': task_type,
        'exp': True
    }
    mlflow.hftransformers.save_model(path_to_model, model_path, hf_conf=hf_conf)
    reloaded_task_type, r_model, r_tokenizer, r_config = mlflow.hftransformers.load_model(model_path)
    # predictor = pipeline(task=task_type, model=r_model, tokenizer=r_tokenizer, config=r_config)
    # outputs = predictor(list(dataset_opus['X']))
    # result2 = [output['translation_text'] for output in outputs]
    #
    # np.testing.assert_array_equal(
    #     result1, result2
    # )
    pyfunc_loaded = mlflow.pyfunc.load_model(model_path)
    pyfunc_preds = pyfunc_loaded.predict(dataset_opus['X'])
    np.testing.assert_array_equal(
        pyfunc_preds, result1
    )
    delete_directory(model_path)

@pytest.mark.hftest2
@pytest.mark.usefixtures("new_clean_dir")
def test_hf_summarization_model_save_load_predict(dataset_billsum, model_path):
    model_name = 't5-small'
    config = AutoConfig.from_pretrained(model_name)
    model = AutoModelForSeq2SeqLM.from_pretrained(model_name, config=config)
    tokenizer = AutoTokenizer.from_pretrained(model_name, padding=True, truncation=True)
    task_type = 'summarization'
    predictor = pipeline(task=task_type, model=model, tokenizer=tokenizer, config=config)
    outputs = predictor(list(dataset_billsum['articles']))
    result1 = [output['summary_text'] for output in outputs]
    hf_conf = {
        'task_type': task_type,
        'model_hf_load_kwargs': {
            'torch_dtype': 'torch.bfloat16',
            'low_cpu_mem_usage': True
        }
    }
    mlflow.hftransformers.save_model(model, model_path, tokenizer=tokenizer, config=config, hf_conf=hf_conf)
    reloaded_task_type, r_model, r_tokenizer, r_config = mlflow.hftransformers.load_model(model_path)
    predictor = pipeline(task=task_type, model=r_model, tokenizer=r_tokenizer, config=r_config)
    outputs = predictor(list(dataset_billsum['articles']))
    result2 = [output['summary_text'] for output in outputs]

    np.testing.assert_array_equal(
        result1, result2
    )
    pyfunc_loaded = mlflow.pyfunc.load_model(model_path)
    pyfunc_preds = pyfunc_loaded.predict(dataset_billsum)
    np.testing.assert_array_equal(
        pyfunc_preds[pyfunc_preds.columns[0]].to_list(), result1
    )
    delete_directory(model_path)


@pytest.mark.hftest1
@pytest.mark.usefixtures("new_clean_dir")
def test_hf_qna_model_save_load_predict(dataset_squad_qna, model_path):
    model_name = 'NeuML/bert-small-cord19qa'
    config = AutoConfig.from_pretrained(model_name)
    model = AutoModelForQuestionAnswering.from_pretrained(model_name, config=config)
    tokenizer = AutoTokenizer.from_pretrained(model_name, padding=True, truncation=True)
    task_type = 'question-answering'
    predictor = pipeline(task=task_type, model=model, tokenizer=tokenizer, config=config)
    outputs = predictor(question=list(dataset_squad_qna['question']), context=list(dataset_squad_qna['context']))
    result1 = [output['answer'] for output in outputs]
    hf_conf = {
        'task_type': task_type,
        'base_model_mlmodel': {
            'flavors': {
                'hftransformers': {

                }
            }
        }
    }
    mlflow.hftransformers.save_model(model, model_path, tokenizer=tokenizer, config=config, hf_conf=hf_conf)
    with open(os.path.join(model_path, "MLmodel"), "r") as stream:
        mlmodel_file = yaml.safe_load(stream)
        assert "hftransformers" in mlmodel_file["flavors"]
        assert "hftransformersv2" not in mlmodel_file["flavors"]
    reloaded_task_type, r_model, r_tokenizer, r_config = mlflow.hftransformers.load_model(model_path)
    predictor = pipeline(task=task_type, model=r_model, tokenizer=r_tokenizer, config=r_config)
    outputs = predictor(question=list(dataset_squad_qna['question']), context=list(dataset_squad_qna['context']))
    result2 = [output['answer'] for output in outputs]

    np.testing.assert_array_equal(
        result1, result2
    )
    pyfunc_loaded = mlflow.pyfunc.load_model(model_path)
    pyfunc_preds = pyfunc_loaded.predict(dataset_squad_qna)
    np.testing.assert_array_equal(
        pyfunc_preds[pyfunc_preds.columns[0]].to_list(), result1
    )
    delete_directory(model_path)

@pytest.mark.hftest3
@pytest.mark.usefixtures("new_clean_dir")
def test_hf_fill_mask_model_save_load_predict(model_path):
    model_name = "distilbert-base-cased"
    config = AutoConfig.from_pretrained(model_name)
    model = AutoModelForMaskedLM.from_pretrained(model_name, config=config)
    tokenizer = AutoTokenizer.from_pretrained(model_name, padding=True, truncation=True)
    data = pd.DataFrame({
        'X': [f"HuggingFace is creating a {tokenizer.mask_token} that the community uses to solve NLP tasks.",
              f"Distilled models are smaller than the models they mimic. Using them instead of the large versions "
              f"would help {tokenizer.mask_token} our carbon footprint."]
    })
    task_type = 'fill-mask'
    predictor = pipeline(task=task_type, model=model, tokenizer=tokenizer, config=config)
    outputs = predictor(list(data['X']))
    result1 = [output[0]['token_str'] for output in outputs]
    hf_conf = {
        'task_type': task_type
    }
    mlflow.hftransformers.save_model(model, model_path, tokenizer=tokenizer, config=config, hf_conf=hf_conf)
    reloaded_task_type, r_model, r_tokenizer, r_config = mlflow.hftransformers.load_model(model_path)
    predictor = pipeline(task=task_type, model=r_model, tokenizer=r_tokenizer, config=r_config)
    outputs = predictor(list(data['X']))
    result2 = [output[0]['token_str'] for output in outputs]
    np.testing.assert_array_equal(
        result1, result2
    )
    pyfunc_loaded = mlflow.pyfunc.load_model(model_path)
    pyfunc_preds = pyfunc_loaded.predict(data)
    pyfunc_preds1 = pyfunc_loaded.predict(data['X'])
    np.testing.assert_array_equal(
        pyfunc_preds[pyfunc_preds.columns[0]].to_list(), result1
    )
    np.testing.assert_array_equal(
        result1, pyfunc_preds1
    )
    delete_directory(model_path)


@pytest.mark.hftest4
@pytest.mark.usefixtures("new_clean_dir")
def test_hf_fill_mask_model_save_load_predict_single_example(model_path):
    model_name = "distilbert-base-cased"
    config = AutoConfig.from_pretrained(model_name)
    model = AutoModelForMaskedLM.from_pretrained(model_name, config=config)
    tokenizer = AutoTokenizer.from_pretrained(model_name, padding=True, truncation=True)
    data = pd.DataFrame({
        'X': [f"HuggingFace is creating a {tokenizer.mask_token} that the community uses to solve NLP tasks."]
    })
    task_type = 'fill-mask'
    predictor = pipeline(task=task_type, model=model, tokenizer=tokenizer, config=config)
    outputs = predictor(list(data['X']))
    result1 = [outputs[0]['token_str']]
    hf_conf = {
        'task_type': task_type
    }
    mlflow.hftransformers.save_model(model, model_path, tokenizer=tokenizer, config=config, hf_conf=hf_conf)
    reloaded_task_type, r_model, r_tokenizer, r_config = mlflow.hftransformers.load_model(model_path)
    predictor = pipeline(task=task_type, model=r_model, tokenizer=r_tokenizer, config=r_config)
    outputs = predictor(list(data['X']))
    result2 = [outputs[0]['token_str']]
    np.testing.assert_array_equal(
        result1, result2
    )
    pyfunc_loaded = mlflow.pyfunc.load_model(model_path)
    pyfunc_preds = pyfunc_loaded.predict(data)
    pyfunc_preds1 = pyfunc_loaded.predict(data['X'])
    np.testing.assert_array_equal(
        pyfunc_preds[pyfunc_preds.columns[0]].to_list(), result1
    )
    np.testing.assert_array_equal(
        result1, pyfunc_preds1
    )
    delete_directory(model_path)


@pytest.mark.hftest3
@pytest.mark.usefixtures("new_clean_dir")
def test_hf_fill_mask_model_save_load_predict_multi_example_multi_mask(model_path):
    model_name = "distilbert-base-cased"
    config = AutoConfig.from_pretrained(model_name)
    model = AutoModelForMaskedLM.from_pretrained(model_name, config=config)
    tokenizer = AutoTokenizer.from_pretrained(model_name, padding=True, truncation=True)
    data = pd.DataFrame({
        'X': [
            f"HuggingFace is creating a {tokenizer.mask_token} that the {tokenizer.mask_token} uses to solve NLP "
            f"tasks.",
            f"Distilled models are {tokenizer.mask_token} than the models they mimic. Using them instead of the "
            f"large versions would help reduce our carbon footprint."]
    })
    task_type = 'fill-mask'
    predictor = pipeline(task=task_type, model=model, tokenizer=tokenizer, config=config)
    outputs = predictor(list(data['X']), top_k=1)
    # result1 = [outputs[0]['token_str'], outputs[1]['token_str']]
    hf_conf = {
        'task_type': task_type
    }
    mlflow.hftransformers.save_model(model, model_path, tokenizer=tokenizer, config=config, hf_conf=hf_conf)
    reloaded_task_type, r_model, r_tokenizer, r_config = mlflow.hftransformers.load_model(model_path)
    predictor = pipeline(task=task_type, model=r_model, tokenizer=r_tokenizer, config=r_config)
    outputs = predictor(list(data['X']))
    # result2 = [outputs[0]['token_str']]
    # np.testing.assert_array_equal(
    #     result1, result2
    # )
    pyfunc_loaded = mlflow.pyfunc.load_model(model_path)
    pyfunc_preds = pyfunc_loaded.predict(data)
    pyfunc_preds1 = pyfunc_loaded.predict(data['X'])
    # np.testing.assert_array_equal(
    #     pyfunc_preds[pyfunc_preds.columns[0]].to_list(), result1
    # )
    # np.testing.assert_array_equal(
    #     result1, pyfunc_preds1
    # )
    delete_directory(model_path)


@pytest.mark.hftest2
@pytest.mark.usefixtures("new_clean_dir")
def test_hf_text_generation_model_save_load_predict(model_path):
    model_name = "distilgpt2"
    config = AutoConfig.from_pretrained(model_name)
    model = AutoModelForCausalLM.from_pretrained(model_name, config=config)
    tokenizer = AutoTokenizer.from_pretrained(model_name, padding=True, truncation=True)
    task_type = 'text-generation'
    data = pd.DataFrame({'text': ["As far as I am concerned, I will",
                                  "How is it going dear"]})
    predictor = pipeline(task=task_type, model=model, tokenizer=tokenizer, config=config)
    outputs = predictor(list(data['text']))
    hf_conf = {
        'task_type': task_type
    }
    mlflow.hftransformers.save_model(model, model_path, tokenizer=tokenizer, config=config, hf_conf=hf_conf)
    reloaded_task_type, r_model, r_tokenizer, r_config = mlflow.hftransformers.load_model(model_path)
    predictor = pipeline(task=task_type, model=r_model, tokenizer=r_tokenizer, config=r_config)
    outputs2 = predictor(list(data['text']))
    # result2 = [output['generated_text'] for output in outputs]
    #
    # np.testing.assert_array_equal(
    #     outputs, outputs2
    # )
    pyfunc_loaded = mlflow.pyfunc.load_model(model_path)
    pyfunc_preds = pyfunc_loaded.predict(data['text'])
    pyfunc_preds1 = pyfunc_loaded.predict({'X': data['text'].tolist(), "parameters": {
        "max_length": 10
    }})
    for text in pyfunc_preds1[pyfunc_preds1.columns[0]].tolist():
        assert len(text.split(" ")) <= 10
    # np.testing.assert_array_equal(
    #     pyfunc_preds, outputs2
    # )
    delete_directory(model_path)


@pytest.mark.hftest3
@pytest.mark.usefixtures("new_clean_dir")
def test_hf_chat_completion_model_save_load_predict(model_path):
    model_name = "microsoft/DialoGPT-small"
    config = AutoConfig.from_pretrained(model_name)
    model = AutoModelForCausalLM.from_pretrained(model_name, config=config)
    model.max_length = 2048
    # from transformers import GPT2Tokenizer
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    task_type = 'text-generation'
    data = {
        "input_string": [[
            {
                "role": "user",
                "content": "What is the capital of France?"
            }],
            [{
                "role": "user",
                "content": "What is the capital of France?"
            },
                {
                    "role": "assistant",
                    "content": "Paris"},
                {
                    "role": "user",
                    "content": "And Italy?"
                }]
            # {
            #     "role": "assistant",
            #     "content": "Paris, the capital of France, is known for its stunning architecture, art museums, "
            #                "historical landmarks, and romantic atmosphere. Here are some of the top attractions to "
            #                "see in Paris:\n\n1. The Eiffel Tower: The iconic Eiffel Tower is one of the most "
            #                "recognizable landmarks in the world and offers breathtaking views of the city.\n2. The "
            #                "Louvre Museum: The Louvre is one of the world's largest and most famous museums, housing "
            #                "an impressive collection of art and artifacts, including the Mona Lisa.\n3. Notre-Dame "
            #                "Cathedral: This beautiful cathedral is one of the most famous landmarks in Paris and is "
            #                "known for its Gothic architecture and stunning stained glass windows.\n\nThese are just a "
            #                "few of the many attractions that Paris has to offer. With so much to see and do, it's no "
            #                "wonder that Paris is one of the most popular tourist destinations in the world."
            # },
            # {
            #     "role": "user",
            #     "content": "What is so great about #1?"
            # }
        ],
        "parameters": {
            "max_length": 200,
            "temperature": 0.6,
            "top_p": 0.9,
            "do_sample": True,
            "max_new_tokens": 200
        }
    }
    from azureml.evaluate.mlflow.hftransformers._task_based_predictors import ChatCompletionPredictor
    conv = ChatCompletionPredictor._parse_data(pd.DataFrame({"input_string": data["input_string"]}))
    predictor = pipeline(task=task_type, model=model, tokenizer=tokenizer, config=config)
    outputs = predictor(conv, **data["parameters"])
    hf_conf = {
        'task_type': task_type
    }
    mlflow.hftransformers.save_model(model, model_path, tokenizer=tokenizer, config=config, hf_conf=hf_conf)
    reloaded_task_type, r_model, r_tokenizer, r_config = mlflow.hftransformers.load_model(model_path)
    predictor = pipeline(task=task_type, model=r_model, tokenizer=r_tokenizer, config=r_config)
    conv = ChatCompletionPredictor._parse_data(pd.DataFrame({"input_string": data["input_string"]}))
    data["parameters"]["max_new_tokens"] = 1
    outputs2 = predictor(conv, **data["parameters"])

    if isinstance(outputs2[0], dict):
        assert len(outputs2[0]["generated_text"][-1]["content"]) >= 1
    else:
        assert len(outputs2[0][0]["generated_text"][-1]["content"]) >= 1
    pyfunc_loaded = mlflow.pyfunc.load_model(model_path)
    pyfunc_preds = pyfunc_loaded.predict(data)
    assert len(pyfunc_preds.iloc[0]) == 1
    # pyfunc_preds1 = pyfunc_loaded.predict({'X': data['text'].tolist(), "parameters": {
    #     "max_length": 10
    # }})
    # for text in pyfunc_preds1[pyfunc_preds1.columns[0]].tolist():
    #     assert len(text.split(" ")) <= 10
    # np.testing.assert_array_equal(
    #     pyfunc_preds, outputs2
    # )
    delete_directory(model_path)


@pytest.mark.hftest3
@pytest.mark.usefixtures("new_clean_dir")
def test_multiclass_model_save_load_with_paths(newsgroup_dataset, model_path):  # noqa: F811
    train_labels = newsgroup_dataset['train_labels']
    newsgroup_dataset = newsgroup_dataset['dataset']
    config = AutoConfig.from_pretrained("bert-base-uncased", num_labels=len(train_labels), output_attentions=False,
                                        output_hidden_states=False)
    config.id2label = train_labels
    model = AutoModelForSequenceClassification.from_pretrained(
        "bert-base-uncased",
        config=config
    )
    temp_dir = tempfile.TemporaryDirectory()
    save_model_path = temp_dir.name
    config_path = os.path.join(save_model_path, "config")
    hfmodel_path = os.path.join(save_model_path, "model")
    tokenizer_path = os.path.join(save_model_path, "tokenizer")
    tokenizer = AutoTokenizer.from_pretrained('bert-base-uncased', config=config)
    config.save_pretrained(config_path)
    model.save_pretrained(hfmodel_path)
    tokenizer.save_pretrained(tokenizer_path)
    trainer = Trainer(
        model=model,
        tokenizer=tokenizer,
        data_collator=default_data_collator,
    )
    df = newsgroup_dataset._constructor_args["data"]
    df.drop(['y'], inplace=True, axis=1)
    dataset_wrapper = PyTorchClassificationDatasetWrapper(df, tokenizer, 128)
    pred = trainer.predict(dataset_wrapper)
    train_label_list = np.unique(newsgroup_dataset.labels_data)
    hf_conf = {
        'task_type': 'multiclass',
        'train_label_list': train_label_list,
        'hf_pretrained_class': 'BertForSequenceClassification'
    }
    mlflow.hftransformers.save_model(hfmodel_path, model_path, tokenizer=tokenizer_path, config=config_path,
                                     hf_conf=hf_conf)
    reloaded_task_type, r_model, r_tokenizer, r_config = mlflow.hftransformers.load_model(model_path)
    trainer2 = Trainer(
        model=r_model,
        tokenizer=r_tokenizer,
        data_collator=default_data_collator,
    )
    pred2 = trainer2.predict(dataset_wrapper)
    np.testing.assert_array_almost_equal(
        pred.predictions, pred2.predictions, decimal=4
    )
    pyfunc_loaded = mlflow.pyfunc.load_model(model_path)
    preds = np.argmax(pred.predictions, axis=1)
    predicted_labels = [train_label_list[item] for item in preds]
    pyfunc_preds = pyfunc_loaded.predict(dataset_wrapper.data)
    pyfunc_preds = pyfunc_preds[pyfunc_preds.columns[0]].values
    temp_dir.cleanup()
    # ToDo: Check this, not working after latest change
    # np.testing.assert_array_equal(
    #     pyfunc_preds, predicted_labels
    # )
    delete_directory(model_path)

@pytest.mark.hftest3
@pytest.mark.usefixtures("new_clean_dir")
def test_multiclass_model_save_load_without_task_and_single_path(newsgroup_dataset, model_path):  # noqa: F811
    newsgroup_dataset = newsgroup_dataset['dataset']
    config = AutoConfig.from_pretrained("bert-base-uncased", num_labels=2, output_attentions=False,
                                        output_hidden_states=False,
                                        train_label_list=np.unique(newsgroup_dataset._constructor_args['targets']))
    model = AutoModelForSequenceClassification.from_pretrained(
        "bert-base-uncased",
        config=config
    )
    temp_dir = tempfile.TemporaryDirectory()
    save_model_path = temp_dir.name
    hfmodel_path = os.path.join(save_model_path, "model")
    tokenizer = AutoTokenizer.from_pretrained('bert-base-uncased', config=config)
    config.save_pretrained(hfmodel_path)
    model.save_pretrained(hfmodel_path)
    tokenizer.save_pretrained(hfmodel_path)
    trainer = Trainer(
        model=model,
        tokenizer=tokenizer,
        data_collator=default_data_collator,
    )
    df = newsgroup_dataset._constructor_args["data"]
    df.drop(['y'], inplace=True, axis=1)
    dataset_wrapper = PyTorchClassificationDatasetWrapper(df, tokenizer, 128)
    pred = trainer.predict(dataset_wrapper)
    mlflow.hftransformers.save_model(hfmodel_path, model_path, hf_conf={
        'hf_pretrained_class': 'BertForSequenceClassification'
    })
    reloaded_task_type, r_model, r_tokenizer, r_config = mlflow.hftransformers.load_model(model_path)
    trainer2 = Trainer(
        model=r_model,
        tokenizer=r_tokenizer,
        data_collator=default_data_collator,
    )
    assert reloaded_task_type is None
    pred2 = trainer2.predict(dataset_wrapper)
    np.testing.assert_array_almost_equal(
        pred.predictions, pred2.predictions, decimal=4
    )
    pyfunc_loaded = mlflow.pyfunc.load_model(model_path)
    with pytest.raises(Exception) as exc:
        pyfunc_loaded.predict(dataset_wrapper.data)
    assert str(exc.value) == ErrorStrings.UnsupportedTaskType.format(task=None)
    temp_dir.cleanup()
    delete_directory(model_path)


@pytest.mark.hftest3
@pytest.mark.usefixtures("new_clean_dir")
def test_multiclass_model_predict_with_preprocess_script(newsgroup_dataset, model_path):  # noqa: F811
    train_labels = newsgroup_dataset['train_labels']
    train_label_list = newsgroup_dataset['train_label_list']
    newsgroup_dataset = newsgroup_dataset['dataset']
    config = AutoConfig.from_pretrained("bert-base-uncased", num_labels=len(train_labels), output_attentions=False,
                                        output_hidden_states=False)
    config.id2label = train_labels
    model = AutoModelForSequenceClassification.from_pretrained(
        "bert-base-uncased",
        config=config
    )
    tokenizer = AutoTokenizer.from_pretrained('bert-base-uncased', config=config)
    trainer = Trainer(
        model=model,
        tokenizer=tokenizer,
        data_collator=default_data_collator,
    )
    df = newsgroup_dataset._constructor_args["data"]
    df.drop(['y'], inplace=True, axis=1)
    dataset_wrapper = PyTorchClassificationDatasetWrapper(df, tokenizer, 512)
    pred = trainer.predict(dataset_wrapper)
    hf_conf = {
        'task_type': 'multiclass',
        'train_label_list': train_label_list
    }
    preprocess_script = os.path.join(os.path.dirname(__file__), "preprocess.py")
    mlflow.hftransformers.save_model(model, model_path, tokenizer=tokenizer, config=config, hf_conf=hf_conf,
                                     code_paths=[preprocess_script])
    reloaded_task_type, r_model, r_tokenizer, r_config = mlflow.hftransformers.load_model(model_path)
    trainer2 = Trainer(
        model=r_model,
        tokenizer=r_tokenizer,
        data_collator=default_data_collator,
    )
    pred2 = trainer2.predict(dataset_wrapper)
    np.testing.assert_array_almost_equal(
        pred.predictions, pred2.predictions, decimal=4
    )
    pyfunc_loaded = mlflow.pyfunc.load_model(model_path)
    preds = np.argmax(pred.predictions, axis=1)
    predicted_labels = [train_label_list[item] for item in preds]
    pyfunc_preds = pyfunc_loaded.predict(dataset_wrapper.data)
    pyfunc_preds = pyfunc_preds[pyfunc_preds.columns[0]].values
    np.testing.assert_array_equal(
        pyfunc_preds, predicted_labels
    )
    delete_directory(model_path)


@pytest.mark.hftest3
@pytest.mark.usefixtures("new_clean_dir")
def test_multiclass_model_predict_with_preprocess_script(newsgroup_dataset, model_path):  # noqa: F811
    train_labels = newsgroup_dataset['train_labels']
    newsgroup_dataset = newsgroup_dataset['dataset']
    config = AutoConfig.from_pretrained("bert-base-uncased", num_labels=len(train_labels), output_attentions=False,
                                        output_hidden_states=False)
    config.id2label = train_labels
    model = AutoModelForSequenceClassification.from_pretrained(
        "bert-base-uncased",
        config=config
    )
    tokenizer = AutoTokenizer.from_pretrained('bert-base-uncased', config=config)
    trainer = Trainer(
        model=model,
        tokenizer=tokenizer,
        data_collator=default_data_collator,
    )
    df = newsgroup_dataset._constructor_args["data"]
    df.drop(['y'], inplace=True, axis=1)
    dataset_wrapper = PyTorchClassificationDatasetWrapper(df, tokenizer, 512)
    pred = trainer.predict(dataset_wrapper)
    hf_conf = {
        'task_type': 'multiclass'
    }
    preprocess_script = os.path.join(os.path.dirname(__file__), "preprocess.py")
    mlflow.hftransformers.save_model(model, model_path, tokenizer=tokenizer, config=config, hf_conf=hf_conf,
                                     code_paths=[preprocess_script])
    reloaded_task_type, r_model, r_tokenizer, r_config = mlflow.hftransformers.load_model(model_path)
    trainer2 = Trainer(
        model=r_model,
        tokenizer=r_tokenizer,
        data_collator=default_data_collator,
    )
    pred2 = trainer2.predict(dataset_wrapper)
    np.testing.assert_array_almost_equal(
        pred.predictions, pred2.predictions, decimal=4
    )
    pyfunc_loaded = mlflow.pyfunc.load_model(model_path)
    preds = np.argmax(pred.predictions, axis=1)
    predicted_labels = [train_labels[item] for item in preds]
    pyfunc_preds = pyfunc_loaded.predict(dataset_wrapper.data)
    pyfunc_preds = pyfunc_preds[pyfunc_preds.columns[0]].values
    np.testing.assert_array_equal(
        pyfunc_preds, predicted_labels
    )
    delete_directory(model_path)


@pytest.mark.hftest3
@pytest.mark.usefixtures("new_clean_dir")
def test_multiclass_model_predict_with_predict_script(newsgroup_dataset, model_path):  # noqa: F811
    train_labels = newsgroup_dataset['train_labels']
    newsgroup_dataset = newsgroup_dataset['dataset']
    config = AutoConfig.from_pretrained("bert-base-uncased", num_labels=len(train_labels), output_attentions=False,
                                        output_hidden_states=False)
    config.id2label = train_labels
    model = AutoModelForSequenceClassification.from_pretrained(
        "bert-base-uncased",
        config=config
    )
    tokenizer = AutoTokenizer.from_pretrained('bert-base-uncased', config=config)
    trainer = Trainer(
        model=model,
        tokenizer=tokenizer,
        data_collator=default_data_collator,
    )
    df = newsgroup_dataset._constructor_args["data"]
    df.drop(['y'], inplace=True, axis=1)
    dataset_wrapper = PyTorchClassificationDatasetWrapper(df, tokenizer, 512)
    pred = trainer.predict(dataset_wrapper)
    hf_conf = {
        'task_type': 'multiclass',
        'hf_predict_module': 'hf_test_predict'
    }
    predict_script = os.path.join(os.path.dirname(__file__), "hf_test_predict.py")
    mlflow.hftransformers.save_model(model, model_path, tokenizer=tokenizer, config=config, hf_conf=hf_conf,
                                     code_paths=[predict_script])
    reloaded_task_type, r_model, r_tokenizer, r_config = mlflow.hftransformers.load_model(model_path)
    trainer2 = Trainer(
        model=r_model,
        tokenizer=r_tokenizer,
        data_collator=default_data_collator,
    )
    pred2 = trainer2.predict(dataset_wrapper)
    np.testing.assert_array_almost_equal(
        pred.predictions, pred2.predictions, decimal=4
    )
    pyfunc_loaded = mlflow.pyfunc.load_model(model_path)
    preds = np.argmax(pred.predictions, axis=1)
    predicted_labels = [train_labels[item] for item in preds]
    pyfunc_preds = pyfunc_loaded.predict(dataset_wrapper.data)
    pyfunc_preds = pyfunc_preds[pyfunc_preds.columns[0]].values
    np.testing.assert_array_equal(
        pyfunc_preds, predicted_labels
    )
    delete_directory(model_path)


@pytest.mark.hftest1
@pytest.mark.usefixtures("new_clean_dir")
def test_hf_tts_model_save_load_predict(model_path):
    model_name = "openai/whisper-small"
    ds = load_dataset("hf-internal-testing/librispeech_asr_dummy", "clean", split="validation")
    from transformers import WhisperProcessor, WhisperForConditionalGeneration, WhisperConfig
    config = WhisperConfig.from_pretrained(model_name)
    model = WhisperForConditionalGeneration.from_pretrained(model_name, config=config)
    processor = WhisperProcessor.from_pretrained(model_name, padding=True, truncation=True)
    task_type = 'automatic-speech-recognition'
    audio = ds["audio"][:1]
    data = pd.DataFrame([{'raw': item["array"], 'sampling_rate': item["sampling_rate"]} for item in audio])
    predictor = pipeline(task=task_type, model=model, tokenizer=processor.tokenizer, config=config,
                         feature_extractor=processor.feature_extractor)
    outputs = predictor(data.to_dict('records'))
    hf_conf = {
        'task_type': task_type
    }
    mlflow.hftransformers.save_model(model, model_path, tokenizer=processor, config=config, hf_conf=hf_conf)
    pyfunc_loaded = mlflow.pyfunc.load_model(model_path)
    pyfunc_preds = pyfunc_loaded.predict(data)

    reloaded_task_type, r_model, r_processor, r_config = mlflow.hftransformers.load_model(model_path)
    predictor = pipeline(task=task_type, model=r_model, tokenizer=r_processor.tokenizer, config=r_config,
                         feature_extractor=r_processor.feature_extractor)
    outputs2 = predictor(data.to_dict('records'))
    result2 = [output['text'] for output in outputs2]

    np.testing.assert_array_equal(
        pyfunc_preds[pyfunc_preds.columns[0]].to_list(), result2
    )
    np.testing.assert_array_equal(
        outputs2, outputs
    )
    delete_directory(model_path)


@pytest.mark.hftest4
@pytest.mark.usefixtures("new_clean_dir")
def test_hf_text_2_image_model_save_load_predict(model_path):
    model_name = "CompVis/stable-diffusion-v1-4"
    dataset = load_dataset("YaYaB/onepiece-blip-captions")

    task_type = "text-to-image"
    hf_conf = {
        'task_type': task_type,
        'custom_config_module': 'diffusers',
        'hf_config_class': 'AutoConfig',
        "custom_tokenizer_module": "diffusers",
        "hf_tokenizer_class": "AutoTokenizer",
        "custom_model_module": "diffusers",
        "hf_pretrained_class": "StableDiffusionPipeline",
        "force_load_tokenizer": False,
        "force_load_config": False,
    }

    pipeline = StableDiffusionPipeline.from_pretrained(
        pretrained_model_name_or_path=model_name,
    )
    mlflow.hftransformers.save_model(pipeline, model_path, hf_conf=hf_conf)
    reloaded_task_type, r_model, r_tokenizer, r_config = mlflow.hftransformers.load_model(model_path)

    X_test = dataset['train'].to_pandas()['text'].tolist()[:2]

    device = "cuda" if torch.cuda.is_available() else "cpu"
    generator = torch.Generator(device=device).manual_seed(1024)

    runtime_args = {
        "generator": generator,
        "num_inference_steps": 5,
        "height": 64,
        "width": 64,
    }
    preds = pipeline(X_test, **runtime_args)

    runtime_args = {
        **runtime_args,
        "device": device,
    }
    pyfunc_r = mlflow.aml.load_model(model_path)

    preds_r_dict = pyfunc_r.predict({"inputs": {"test": X_test}}, **runtime_args)
    preds_r_ndarray = pyfunc_r.predict(np.array(X_test), **runtime_args)

    preds_r = pyfunc_r.predict(pd.DataFrame(X_test), **runtime_args)

    preds_check = [preds, preds_r, preds_r_dict, preds_r_ndarray]
    assert all(p is not None for p in preds_check)

    def convert_pil_to_base64(img):
        with io.BytesIO() as buf:
            img.save(buf, format='JPEG')
            return base64.encodebytes(buf.getbuffer().tobytes()).decode('utf-8')

    preds_df = pd.DataFrame(preds)
    preds_df['images'] = preds_df['images'].apply(convert_pil_to_base64)

    assert preds_df.shape[1] == 2
    assert preds_r.shape[1] == 2
    # Generator not working with Stable Diffusion. Uncomment below after it's fixed by HF.
    # assert preds_r.equals(preds_df)
    delete_directory(model_path)

from ..models.utils import (  # noqa: F401
    newsgroup_dataset,
    PyTorchClassificationDatasetWrapper
)
import azureml.evaluate.mlflow as mlflow
import numpy as np
from transformers import AutoModelForSequenceClassification, AutoModelForQuestionAnswering
from transformers import AutoTokenizer
from transformers import AutoConfig
import pytest
import os
from datasets import load_dataset
import pandas as pd
from transformers import pipeline
from tests.helper_functions import delete_directory


@pytest.fixture
def model_path(tmpdir, subdir="model"):
    return os.path.join(str(tmpdir), subdir)


def extra_files():
    pass


@pytest.mark.hftest3
@pytest.mark.usefixtures("new_clean_dir")
def test_multiclass_model_save_load_pipeline(newsgroup_dataset, model_path):  # noqa: F811
    train_labels = newsgroup_dataset['train_labels']
    train_label_list = newsgroup_dataset['train_label_list']
    newsgroup_dataset = newsgroup_dataset['dataset']
    config = AutoConfig.from_pretrained("bert-base-uncased", num_labels=len(train_labels), output_attentions=False,
                                        output_hidden_states=False,
                                        train_label_list=train_label_list)
    config.id2label = train_labels
    model = AutoModelForSequenceClassification.from_pretrained(
        "bert-base-uncased",
        config=config
    )
    tokenizer = AutoTokenizer.from_pretrained('bert-base-uncased', config=config)
    df = newsgroup_dataset._constructor_args["data"]
    df.drop(['y'], inplace=True, axis=1)
    dataset_wrapper = PyTorchClassificationDatasetWrapper(df, tokenizer, 128)
    # train_label_list = np.unique(newsgroup_dataset.labels_data)
    hf_conf = {
        'task_type': 'text-classification',
        'tokenizer_config': {
            'padding': "max_length",
            'truncation': True
        }
    }
    mlflow.hftransformers.save_model(model, model_path, tokenizer=tokenizer, config=config, hf_conf=hf_conf)
    p_model = mlflow.hftransformers.load_pipeline(model_path, dst_path=None,
                                                  **{'task_type': 'text-classification', 'device': -1})
    results = p_model.predict(dataset_wrapper.data)
    pipe = pipeline(hf_conf["task_type"], model=model, config=config, tokenizer=tokenizer)
    results2 = pipe(dataset_wrapper.data[dataset_wrapper.data.columns[0]].to_list(), **hf_conf["tokenizer_config"])
    np.testing.assert_array_equal(
        results, results2
    )
    delete_directory(model_path)


@pytest.mark.hftest3
@pytest.mark.usefixtures("new_clean_dir")
def test_multiclass_model_save_load_pyfunc_pipeline(newsgroup_dataset, model_path):  # noqa: F811
    train_labels = newsgroup_dataset['train_labels']
    train_label_list = newsgroup_dataset['train_label_list']
    newsgroup_dataset = newsgroup_dataset['dataset']
    config = AutoConfig.from_pretrained("bert-base-uncased", num_labels=len(train_labels), output_attentions=False,
                                        output_hidden_states=False,
                                        train_label_list=train_label_list)
    config.id2label = train_labels
    model = AutoModelForSequenceClassification.from_pretrained(
        "bert-base-uncased",
        config=config
    )
    tokenizer = AutoTokenizer.from_pretrained('bert-base-uncased', config=config)
    df = newsgroup_dataset._constructor_args["data"]
    df.drop(['y'], inplace=True, axis=1)
    dataset_wrapper = PyTorchClassificationDatasetWrapper(df, tokenizer, 128)
    # train_label_list = np.unique(newsgroup_dataset.labels_data)
    hf_conf = {
        'task_type': 'text-classification',
        'tokenizer_config': {
            'padding': "max_length",
            'truncation': True
        },
        'force_pipeline': True
    }
    mlflow.hftransformers.save_model(model, model_path, tokenizer=tokenizer, config=config, hf_conf=hf_conf)
    p_model = mlflow.pyfunc.load_model(model_path)
    results = p_model.predict(dataset_wrapper.data)
    pipe = pipeline(hf_conf["task_type"], model=model, config=config, tokenizer=tokenizer)
    results2 = pipe(dataset_wrapper.data[dataset_wrapper.data.columns[0]].to_list(), **hf_conf["tokenizer_config"])

    assert results == results2
    delete_directory(model_path)


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
        'task_type': task_type
    }
    mlflow.hftransformers.save_model(model, model_path, tokenizer=tokenizer, config=config, hf_conf=hf_conf)
    r_pipeline = mlflow.hftransformers.load_pipeline(model_path)
    outputs = r_pipeline.predict(dataset_squad_qna)
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

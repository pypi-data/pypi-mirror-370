# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
# flake8: noqa
import ast

import pytest

from azureml.metrics.tabular.regression.azureml_regression_metrics import AzureMLRegressionMetrics
import numpy as np
import pandas as pd
from azureml.metrics import compute_metrics, constants
import azureml.evaluate.mlflow as mlflow

from azureml.evaluate.mlflow.models.evaluation import evaluate
from azureml.evaluate.mlflow.models.evaluation.constants import (EvaluationMiscLiterals,
                                                                 EvaluationDefaultSetting, )

# noqa: F811
from .utils import (  # noqa: F811
    get_run_data,
    get_connll_dataset,
    get_diabetes_dataset_timeseries,
    linear_regressor_model_uri,
    diabetes_dataset,
    multiclass_logistic_regressor_model_uri,
    iris_dataset,
    get_iris,
    newsgroup_dataset,
    newsgroup_dataset_text_pair,
    arxiv_dataset,
    multiclass_llm_model_uri,
    summarization_llm_model_uri,
    qna_llm_model_uri,
    translation_llm_model_uri,
    billsum_dataset,
    squad_qna_dataset,
    opus_dataset,
    multilabel_llm_model_uri,
    y_transformer_arxiv,
    ner_dataset,
    ner_llm_model_uri,
    fill_mask_llm_model_uri,
    text_generation_llm_model_uri,
    text_gen_data,
    wiki_mask,
    forecaster_model_uri,
    diabetes_dataset_timeseries,
    fridge_object,
    image_od_model_uri,
    fridge_object_mask,
    image_is_model_uri,
)
from azureml.metrics.tabular.forecasting.azureml_forecasting_metrics import AzureMLForecastingMetrics
from azureml.evaluate.mlflow.constants import ForecastFlavors
from azureml.evaluate.mlflow.models.evaluation.base import EvaluationDataset
from pandas.tseries.frequencies import to_offset


def assert_dict_equal(d1, d2, rtol):
    for k in d1:
        assert k in d2
        assert np.isclose(d1[k], d2[k], rtol=rtol)


@pytest.mark.hftest2
@pytest.mark.usefixtures("new_clean_dir")
def test_regressor_evaluation(linear_regressor_model_uri, diabetes_dataset):  # noqa: F811
    '''
    format of result needs to be changed
    2) non-scalar metrics should be part of metrics? -> residuals, predicted_true
    '''
    # mlflow.set_tracking_uri("azureml://eastus2.api.azureml.ms/mlflow/v1.0/subscriptions/72c03bf3-4e69-41af-9532"
    #                         "-dfcdc3eefef4/resourceGroups/shared-model-evaluation-rg/providers/Microsoft"
    #                         ".MachineLearningServices/workspaces/aml-shared-model-evaluation-ws")
    with mlflow.start_run() as run:
        result = evaluate(
            linear_regressor_model_uri,
            diabetes_dataset._constructor_args["data"],
            model_type="regressor",
            targets=diabetes_dataset._constructor_args["targets"],
            dataset_name=diabetes_dataset.name,
            evaluators="azureml",
        )

    _, metrics, tags, artifacts = get_run_data(run.info.run_id)

    model = mlflow.aml.load_model(linear_regressor_model_uri, model_type="regressor")

    y = diabetes_dataset.labels_data
    y_pred = model.predict(diabetes_dataset.features_data)
    metric = AzureMLRegressionMetrics()
    expected_metrics = metric.compute(y_test=y, y_pred=y_pred)
    for metric_key in expected_metrics:
        if np.isscalar(expected_metrics[metric_key]):
            assert np.isclose(
                expected_metrics[metric_key],
                result.metrics[metric_key],
                rtol=1e-3,
            )


@pytest.mark.hftest2
@pytest.mark.usefixtures("new_clean_dir")
def test_regressor_evaluation_mlflow_model(linear_regressor_model_uri,
                                           diabetes_dataset):  # noqa: F811
    '''
    format of result needs to be changed
    2) non-scalar metrics should be part of metrics? -> residuals, predicted_true
    '''
    linear_regressor_model_mlflow = mlflow.aml.load_model(linear_regressor_model_uri)
    with mlflow.start_run() as run:
        result = evaluate(
            linear_regressor_model_mlflow,
            diabetes_dataset._constructor_args["data"],
            model_type="regressor",
            targets=diabetes_dataset._constructor_args["targets"],
            dataset_name=diabetes_dataset.name,
            evaluators="azureml",
        )

    _, metrics, tags, artifacts = get_run_data(run.info.run_id)

    y = diabetes_dataset.labels_data
    y_pred = linear_regressor_model_mlflow.predict(diabetes_dataset.features_data)
    expected_metrics = compute_metrics(task_type=constants.Tasks.REGRESSION, y_test=y, y_pred=y_pred)
    for metric_key in expected_metrics:
        if np.isscalar(expected_metrics[metric_key]):
            assert np.isclose(
                expected_metrics[metric_key],
                result.metrics[metric_key],
                rtol=1e-3,
            )


def _do_test_forecaster_evaluation(forecaster_model_uri,
                                   forecast_flavour
                                   ):  # noqa: F811
    """Test the forecasting evaluation using model uri."""
    X_train, y_train, X_test, y_test = get_diabetes_dataset_timeseries()
    cfg = {
        ForecastFlavors.FLAVOUR: forecast_flavour,
        'X_train': X_train,
        'y_train': y_train,
    }
    if forecast_flavour == ForecastFlavors.ROLLING_FORECAST:
        cfg['step'] = 2
        freq = to_offset('D')
        X_test2 = X_test.copy()
        X_test2['date'] = pd.date_range(
            X_test['date'].max() + freq, periods=X_test.shape[0], freq=freq)
        X_test = pd.concat([X_test, X_test2], sort=False, ignore_index=True)
        np.random.seed(42)
        y_test = np.concatenate([y_test, y_test + np.random.rand(len(y_test))])
    X_test['y'] = y_test

    constructor_args = {"data": X_test, "targets": "y", "name": "diabetes_dataset_timeseries"}
    diabetes_dataset_timeseries = EvaluationDataset(**constructor_args)
    diabetes_dataset_timeseries._constructor_args = constructor_args
    # diabetes_dataset_timeseries =
    with mlflow.start_run() as run:
        result = evaluate(
            forecaster_model_uri,
            diabetes_dataset_timeseries._constructor_args["data"],
            model_type="forecaster",
            targets=diabetes_dataset_timeseries._constructor_args["targets"],
            dataset_name=diabetes_dataset_timeseries.name,
            evaluators="azureml",
            evaluator_config={"azureml": cfg},
        )

    get_run_data(run.info.run_id)

    model = mlflow.aml.load_model(forecaster_model_uri, model_type="regressor")

    y = diabetes_dataset_timeseries.labels_data
    if forecast_flavour == ForecastFlavors.ROLLING_FORECAST:
        X_test = model.rolling_forecast(diabetes_dataset_timeseries.features_data, y, step=2)
        y_pred = X_test.pop(model._model_impl.forecast_column_name).values
        y = X_test.pop(model._model_impl.actual_column_name).values
    else:
        y_pred, _ = model.forecast(diabetes_dataset_timeseries.features_data)

    metric = AzureMLForecastingMetrics(
        X_train=X_train,
        y_train=y_train,
        y_std=np.std(y_train),
        time_column_name='date'
    )
    expected_metrics = metric.compute(
        y_test=y, y_pred=y_pred,
        X_test=X_test)
    for metric_key in expected_metrics:
        if np.isscalar(expected_metrics[metric_key]):
            assert np.isclose(
                expected_metrics[metric_key],
                result.metrics[metric_key],
                rtol=1e-3,
            )


@pytest.mark.hftest2
@pytest.mark.usefixtures("new_clean_dir")
def test_forecaster_evaluation(forecaster_model_uri):  # noqa: F811):
    """Test evaluation on regular forecast."""
    _do_test_forecaster_evaluation(
        forecaster_model_uri, ForecastFlavors.RECURSIVE_FORECAST)


@pytest.mark.hftest2
@pytest.mark.usefixtures("new_clean_dir")
def test_forecaster_evaluation_rolling(forecaster_model_uri):  # noqa: F811):
    """Test evaluation on regular forecast."""
    _do_test_forecaster_evaluation(
        forecaster_model_uri, ForecastFlavors.ROLLING_FORECAST)


@pytest.mark.hftest2
@pytest.mark.usefixtures("new_clean_dir")
def test_forecaster_evaluation_mlflow_model(forecaster_model_uri,
                                            diabetes_dataset_timeseries):
    """Test the forecasting evaluation using model instance."""
    forecaster_model_mlflow = mlflow.aml.load_model(forecaster_model_uri)
    with mlflow.start_run() as run:
        result = evaluate(
            forecaster_model_mlflow,
            diabetes_dataset_timeseries._constructor_args["data"],
            model_type="forecaster",
            targets=diabetes_dataset_timeseries._constructor_args["targets"],
            dataset_name=diabetes_dataset_timeseries.name,
            evaluators="azureml",
        )

    get_run_data(run.info.run_id)

    y = diabetes_dataset_timeseries.labels_data
    y_pred, _ = forecaster_model_mlflow.forecast(diabetes_dataset_timeseries.features_data)
    expected_metrics = compute_metrics(task_type=constants.Tasks.FORECASTING, y_test=y, y_pred=y_pred,
                                       X_test=diabetes_dataset_timeseries._constructor_args["data"],
                                       time_column_name='date')
    for metric_key in expected_metrics:
        if np.isscalar(expected_metrics[metric_key]):
            assert np.isclose(
                expected_metrics[metric_key],
                result.metrics[metric_key],
                rtol=1e-3,
            )


@pytest.mark.hftest3
@pytest.mark.usefixtures("new_clean_dir")
def test_multi_classifier_evaluation(multiclass_logistic_regressor_model_uri,
                                     iris_dataset):  # noqa: F811
    metrics_args = {
        "class_labels": np.unique(iris_dataset.labels_data),
        "train_labels": np.unique(iris_dataset.labels_data)
    }
    with mlflow.start_run() as run:
        result = evaluate(
            multiclass_logistic_regressor_model_uri,
            iris_dataset._constructor_args["data"],
            model_type="classifier",
            targets=iris_dataset._constructor_args["targets"],
            dataset_name=iris_dataset.name,
            evaluators="azureml",
            evaluator_config=metrics_args
        )

    _, metrics, tags, artifacts = get_run_data(run.info.run_id)

    model = mlflow.aml.load_model(multiclass_logistic_regressor_model_uri, "classifier")

    y = iris_dataset.labels_data
    y_pred = model.predict(iris_dataset.features_data)
    y_probs = model.predict_proba(iris_dataset.features_data)

    expected_metrics = compute_metrics(task_type=constants.Tasks.CLASSIFICATION, y_test=y, y_pred=y_pred,
                                       y_pred_proba=y_probs, **metrics_args)
    for metric_key in expected_metrics:
        if np.isscalar(expected_metrics[metric_key]):
            assert np.isclose(
                expected_metrics[metric_key],
                result.metrics[metric_key],
                rtol=1e-3,
            )


@pytest.mark.hftest3
@pytest.mark.usefixtures("new_clean_dir")
def test_multiclass_llm_evaluation(multiclass_llm_model_uri, newsgroup_dataset):  # noqa: F811
    train_labels = newsgroup_dataset['train_labels']
    train_label_list = newsgroup_dataset['train_label_list']
    newsgroup_dataset = newsgroup_dataset['dataset']
    metrics_args = {
        "class_labels": train_label_list,
        "train_labels": train_label_list
    }
    with mlflow.start_run() as run:
        result = evaluate(
            multiclass_llm_model_uri,
            newsgroup_dataset._constructor_args["data"],
            model_type="classifier",
            targets=newsgroup_dataset._constructor_args["targets"],
            dataset_name=newsgroup_dataset.name,
            evaluators="azureml",
            evaluator_config=metrics_args
        )

    _, metrics, tags, artifacts = get_run_data(run.info.run_id)

    model = mlflow.aml.load_model(multiclass_llm_model_uri, "classifier")

    y = newsgroup_dataset.labels_data
    y_pred = model.predict(newsgroup_dataset.features_data)
    y_probs = model.predict_proba(newsgroup_dataset.features_data)
    y_pred_numpy = model.predict(newsgroup_dataset.features_data.to_numpy())
    assert np.array_equal(y_pred[y_pred.columns[0]].to_numpy(), y_pred_numpy)
    expected_metrics = compute_metrics(task_type=constants.Tasks.CLASSIFICATION, y_test=y, y_pred=y_pred,
                                       y_pred_proba=y_probs, **metrics_args)
    for metric_key in expected_metrics:
        if np.isscalar(expected_metrics[metric_key]):
            assert np.isclose(
                expected_metrics[metric_key],
                result.metrics[metric_key],
                rtol=1e-3,
            )


@pytest.mark.hftest3
@pytest.mark.usefixtures("new_clean_dir")
def test_multiclass_llm_evaluation_text_pair(multiclass_llm_model_uri, newsgroup_dataset_text_pair):  # noqa: F811
    metrics_args = {
        "class_labels": np.unique(newsgroup_dataset_text_pair.labels_data),
        "train_labels": np.unique(newsgroup_dataset_text_pair.labels_data)
    }
    with mlflow.start_run() as run:
        result = evaluate(
            multiclass_llm_model_uri,
            newsgroup_dataset_text_pair._constructor_args["data"],
            model_type="classifier",
            targets=newsgroup_dataset_text_pair._constructor_args["targets"],
            dataset_name=newsgroup_dataset_text_pair.name,
            evaluators="azureml",
            evaluator_config=metrics_args
        )

    _, metrics, tags, artifacts = get_run_data(run.info.run_id)

    model = mlflow.aml.load_model(multiclass_llm_model_uri, "classifier")

    y = newsgroup_dataset_text_pair.labels_data
    y_pred = model.predict(newsgroup_dataset_text_pair.features_data)
    y_probs = model.predict_proba(newsgroup_dataset_text_pair.features_data)
    y_pred_numpy = model.predict(newsgroup_dataset_text_pair.features_data.to_numpy())
    assert np.array_equal(y_pred[y_pred.columns[0]].to_numpy(), y_pred_numpy)
    expected_metrics = compute_metrics(task_type=constants.Tasks.CLASSIFICATION, y_test=y, y_pred=y_pred,
                                       y_pred_proba=y_probs, **metrics_args)
    for metric_key in expected_metrics:
        if np.isscalar(expected_metrics[metric_key]):
            assert np.isclose(
                expected_metrics[metric_key],
                result.metrics[metric_key],
                rtol=1e-3,
            )


@pytest.mark.hftest1
@pytest.mark.usefixtures("new_clean_dir")
def test_multilabel_llm_evaluation(multilabel_llm_model_uri, arxiv_dataset,
                                   y_transformer_arxiv):  # noqa: F811
    metrics_args = {
        # "class_labels": np.array(y_transformer_arxiv.classes_),
        # "train_labels": np.array(y_transformer_arxiv.classes_),
        "multilabel": True
        # "y_transformer": y_transformer_arxiv
    }
    with mlflow.start_run() as run:
        result = evaluate(
            multilabel_llm_model_uri,
            arxiv_dataset._constructor_args["data"],
            model_type="classifier-multilabel",
            targets=arxiv_dataset._constructor_args["targets"],
            dataset_name=arxiv_dataset.name,
            evaluators="azureml",
            evaluator_config=metrics_args
        )

    _, metrics, tags, artifacts = get_run_data(run.info.run_id)

    model = mlflow.aml.load_model(multilabel_llm_model_uri, "classifier")

    y = np.array(list(map(lambda x: ast.literal_eval(x), arxiv_dataset.labels_data)))
    y_pred = model.predict(arxiv_dataset.features_data)
    y_pred = np.array(list(map(lambda x: ast.literal_eval(x), y_pred[y_pred.columns[0]].to_numpy())))
    y_probs = model.predict_proba(arxiv_dataset.features_data)
    expected_metrics = compute_metrics(task_type=constants.Tasks.TEXT_CLASSIFICATION, y_test=y,
                                       y_pred=y_pred, y_pred_proba=y_probs, **metrics_args)
    for metric_key in expected_metrics:
        if np.isscalar(expected_metrics[metric_key]):
            assert np.isclose(
                expected_metrics[metric_key],
                result.metrics[metric_key],
                rtol=1e-3,
            )


@pytest.mark.hftest1
@pytest.mark.usefixtures("new_clean_dir")
def test_ner_llm_evaluation(ner_llm_model_uri, ner_dataset):  # noqa: F811
    _, _, labels_list = get_connll_dataset()
    metrics_args = {
        'train_label_list': labels_list,
        'label_list': labels_list
    }
    with mlflow.start_run() as run:
        result = evaluate(
            ner_llm_model_uri,
            ner_dataset._constructor_args["data"],
            model_type="ner",
            targets=ner_dataset._constructor_args["targets"],
            dataset_name=ner_dataset.name,
            evaluators="azureml",
            evaluator_config=metrics_args
        )

    _, metrics, tags, artifacts = get_run_data(run.info.run_id)

    model = mlflow.aml.load_model(ner_llm_model_uri, "ner")
    preds = model.predict(ner_dataset.features_data)
    y_pred = list(map(lambda x: ast.literal_eval(x), preds[preds.columns[0]].values.tolist()))
    y_test = list(map(lambda x: ast.literal_eval(x), list(ner_dataset.labels_data)))
    expected_metrics = compute_metrics(task_type=constants.Tasks.TEXT_NER, y_test=y_test, y_pred=y_pred,
                                       **metrics_args)
    for metric_key in expected_metrics:
        if np.isscalar(expected_metrics[metric_key]):
            assert np.isclose(
                expected_metrics[metric_key],
                result.metrics[metric_key],
                rtol=1e-3,
            )


@pytest.mark.hftest4
@pytest.mark.usefixtures("new_clean_dir")
def test_parse_aml_tracking_uri():
    current_tracking_uri = mlflow.get_tracking_uri()
    mlflow.set_tracking_uri("azureml://eastus2.api.azureml.ms/mlflow/v1.0/subscriptions/72c03bf3-4e69-41af-9532"
                            "-dfcdc3eefef4/resourceGroups/shared-model-evaluation-rg/providers/Microsoft"
                            ".MachineLearningServices/workspaces/aml-shared-model-evaluation-ws")
    from azureml.evaluate.mlflow.models.evaluation.azureml.azureml_evaluator import AzureMLEvaluator
    azureml_evaluator = AzureMLEvaluator()
    workspace, resource_group, subscription = azureml_evaluator._parse_aml_tracking_uri()
    assert workspace == "aml-shared-model-evaluation-ws"
    assert resource_group == "shared-model-evaluation-rg"
    assert subscription == "72c03bf3-4e69-41af-9532-dfcdc3eefef4"
    mlflow.set_tracking_uri(current_tracking_uri)


@pytest.mark.hftest1
@pytest.mark.usefixtures("new_clean_dir")
def test_summarization_llm_evaluation(summarization_llm_model_uri, billsum_dataset):  # noqa: F811
    metrics_args = {

    }
    with mlflow.start_run() as run:
        result = evaluate(
            summarization_llm_model_uri,
            billsum_dataset._constructor_args["data"],
            model_type="summarization",
            targets=billsum_dataset._constructor_args["targets"],
            dataset_name=billsum_dataset.name,
            evaluators="azureml",
            evaluator_config=metrics_args
        )

    _, metrics, tags, artifacts = get_run_data(run.info.run_id)

    model = mlflow.aml.load_model(summarization_llm_model_uri)

    y = billsum_dataset.labels_data
    y_test = np.reshape(y, (-1, 1))
    y_pred = model.predict(billsum_dataset.features_data)
    y_pred = y_pred[y_pred.columns[0]].to_numpy().tolist()
    expected_metrics = compute_metrics(task_type=constants.Tasks.SUMMARIZATION, y_test=y_test.tolist(), y_pred=y_pred,
                                       **metrics_args)
    for metric_key in expected_metrics:
        if np.isscalar(expected_metrics[metric_key]):
            assert np.isclose(
                expected_metrics[metric_key],
                result.metrics[metric_key],
                rtol=1e-3,
            )


@pytest.mark.hftest2
@pytest.mark.usefixtures("new_clean_dir")
def test_translation_llm_evaluation(translation_llm_model_uri, opus_dataset):  # noqa: F811
    metrics_args = {

    }
    with mlflow.start_run() as run:
        result = evaluate(
            translation_llm_model_uri,
            opus_dataset._constructor_args["data"],
            model_type="translation",
            targets=opus_dataset._constructor_args["targets"],
            dataset_name=opus_dataset.name,
            evaluators="azureml",
            evaluator_config=metrics_args
        )

    _, metrics, tags, artifacts = get_run_data(run.info.run_id)

    model = mlflow.aml.load_model(translation_llm_model_uri)

    y = opus_dataset.labels_data
    y_test = np.reshape(y, (-1, 1))
    y_pred = model.predict(opus_dataset.features_data)
    _ = model.predict(opus_dataset.features_data, task_type='translation_en_to_de')
    y_pred = y_pred[y_pred.columns[0]].to_numpy().tolist()
    expected_metrics = compute_metrics(task_type=constants.Tasks.TRANSLATION, y_test=y_test.tolist(), y_pred=y_pred,
                                       **metrics_args)
    for metric_key in expected_metrics:
        if np.isscalar(expected_metrics[metric_key]):
            assert np.isclose(
                expected_metrics[metric_key],
                result.metrics[metric_key],
                rtol=1e-3,
            )


@pytest.mark.hftest1
@pytest.mark.usefixtures("new_clean_dir")
def test_qna_llm_evaluation(qna_llm_model_uri, squad_qna_dataset):  # noqa: F811
    metrics_args = {

    }
    with mlflow.start_run() as run:
        result = evaluate(
            qna_llm_model_uri,
            squad_qna_dataset._constructor_args["data"],
            model_type="question-answering",
            targets=squad_qna_dataset._constructor_args["targets"],
            dataset_name=squad_qna_dataset.name,
            evaluators="azureml",
            evaluator_config=metrics_args
        )

    _, metrics, tags, artifacts = get_run_data(run.info.run_id)

    model = mlflow.aml.load_model(qna_llm_model_uri)

    y = squad_qna_dataset.labels_data
    # y_test = np.reshape(y, (-1, 1))
    y_pred = model.predict(squad_qna_dataset.features_data)
    y_pred = y_pred[y_pred.columns[0]].to_numpy().tolist()
    expected_metrics = compute_metrics(task_type=constants.Tasks.QUESTION_ANSWERING, y_test=y.tolist(), y_pred=y_pred,
                                       **metrics_args)
    for metric_key in expected_metrics:
        if np.isscalar(expected_metrics[metric_key]):
            assert np.isclose(
                expected_metrics[metric_key],
                result.metrics[metric_key],
                rtol=1e-3,
            )


@pytest.mark.hftest3
@pytest.mark.usefixtures("new_clean_dir")
def test_text_generation_llm_evaluation(text_generation_llm_model_uri, text_gen_data):  # noqa: F811
    metrics_args = {

    }
    with mlflow.start_run() as run:
        result = evaluate(
            text_generation_llm_model_uri,
            text_gen_data._constructor_args["data"],
            model_type="text-generation",
            targets=text_gen_data._constructor_args["targets"],
            dataset_name=text_gen_data.name,
            evaluators="azureml",
            evaluator_config=metrics_args
        )

    _, metrics, tags, artifacts = get_run_data(run.info.run_id)

    model = mlflow.aml.load_model(text_generation_llm_model_uri, model_type="text-generation")

    y = text_gen_data.labels_data
    y_test = np.reshape(y, (-1, 1))
    y_pred = model.predict(text_gen_data.features_data)
    y_pred = y_pred[y_pred.columns[0]].to_numpy().tolist()
    expected_metrics = compute_metrics(task_type=constants.Tasks.TEXT_GENERATION, y_test=y_test.tolist(), y_pred=y_pred,
                                       **metrics_args)
    for metric_key in expected_metrics:
        if np.isscalar(expected_metrics[metric_key]):
            assert np.isclose(
                expected_metrics[metric_key],
                result.metrics[metric_key],
                rtol=1e-3,
            )


@pytest.mark.hftest4
@pytest.mark.usefixtures("new_clean_dir")
def test_fill_mask_llm_evaluation(fill_mask_llm_model_uri, wiki_mask):  # noqa: F811
    metrics_args = {

    }
    with mlflow.start_run() as run:
        result = evaluate(
            fill_mask_llm_model_uri,
            wiki_mask._constructor_args["data"],
            model_type="fill-mask",
            targets=wiki_mask._constructor_args["targets"],
            dataset_name=wiki_mask.name,
            evaluators="azureml",
            evaluator_config=metrics_args
        )

    _, metrics, tags, artifacts = get_run_data(run.info.run_id)

    model = mlflow.aml.load_model(fill_mask_llm_model_uri, model_type="fill-mask")

    y = wiki_mask.labels_data
    y_test = np.reshape(y, (-1, 1))
    y_pred = model.predict(wiki_mask.features_data)
    y_pred = y_pred[y_pred.columns[0]].to_numpy().tolist()
    expected_metrics = compute_metrics(task_type=constants.Tasks.FILL_MASK, y_test=y_test.tolist(), y_pred=y_pred,
                                       **metrics_args)
    for metric_key in expected_metrics:
        if np.isscalar(expected_metrics[metric_key]):
            assert np.isclose(
                expected_metrics[metric_key],
                result.metrics[metric_key],
                rtol=1e-3,
            )


def convert_predictions(preds):
    if isinstance(preds, pd.DataFrame) and len(preds.columns) == 1:
        return preds[preds.columns[0]].to_numpy()
    if isinstance(preds, pd.DataFrame) or isinstance(preds, pd.Series):
        return preds.to_numpy()
    if isinstance(preds, list):
        return np.array(preds)
    return preds

@pytest.mark.hftest2
@pytest.mark.usefixtures("new_clean_dir")
def test_image_object_detection_evaluation(image_od_model_uri, fridge_object):  # noqa: F811
    from azureml.evaluate.mlflow.models.evaluation.azureml._image_od_is_evaluator import ImageOdIsEvaluator
    with mlflow.start_run() as run:
        masks_required = False
        metrics_args = {
            "iou_threshold": 0.2,
            "box_score_threshold": 0.2,
            "masks_required": masks_required,
        }
        result = evaluate(
            image_od_model_uri,
            fridge_object._constructor_args["data"],
            model_type="image-object-detection",
            targets=fridge_object._constructor_args["targets"],
            dataset_name=fridge_object.name,
            evaluators="azureml",
            evaluator_config=metrics_args
        )
    model = mlflow.aml.load_model(image_od_model_uri, "image-object-detection")

    y_pred = ImageOdIsEvaluator.predict(model=model,
                                        X_test=fridge_object._constructor_args["data"],
                                        masks_required=masks_required)

    image_meta_info = fridge_object._constructor_args["data"]["image_meta_info"]
    targets=fridge_object._constructor_args["targets"]
    y_test = convert_predictions(fridge_object._constructor_args["data"][targets])

    expected_metrics = ImageOdIsEvaluator.compute_metrics(y_test=y_test,
                                                          y_pred=y_pred,
                                                          image_meta_info=image_meta_info,
                                                          **metrics_args)

    for metric_key, expected_metric_value in expected_metrics["metrics"].items():
        if np.isscalar(expected_metric_value) and np.isnan(expected_metric_value) == False:
            assert np.isclose(
                expected_metric_value,
                result.metrics[metric_key],
                rtol=1e-3,
            )


@pytest.mark.hftest2
@pytest.mark.usefixtures("new_clean_dir")
def test_image_instance_segmentation_evaluation(image_is_model_uri, fridge_object_mask):  # noqa: F811
    from azureml.evaluate.mlflow.models.evaluation.azureml._image_od_is_evaluator import ImageOdIsEvaluator
    with mlflow.start_run() as run:

        masks_required = True
        metrics_args = {
            "iou_threshold": 0.2,
            "box_score_threshold": 0.2,
            "masks_required": masks_required,
        }
        result = evaluate(
            image_is_model_uri,
            fridge_object_mask._constructor_args["data"],
            model_type="image-instance-segmentation",
            targets=fridge_object_mask._constructor_args["targets"],
            dataset_name=fridge_object_mask.name,
            evaluators="azureml",
            evaluator_config=metrics_args
        )
    model = mlflow.aml.load_model(image_is_model_uri, "image-instance-segmentation")

    y_pred = ImageOdIsEvaluator.predict(model=model,
                                        X_test=fridge_object_mask._constructor_args["data"],
                                        masks_required=masks_required)

    image_meta_info = fridge_object_mask._constructor_args["data"]["image_meta_info"]
    targets = fridge_object_mask._constructor_args["targets"]
    y_test = convert_predictions(fridge_object_mask._constructor_args["data"][targets])

    expected_metrics = ImageOdIsEvaluator.compute_metrics(y_test=y_test,
                                                          y_pred=y_pred,
                                                          image_meta_info=image_meta_info,
                                                          **metrics_args)

    for metric_key, expected_metric_value in expected_metrics["metrics"].items():
        if np.isscalar(expected_metric_value) and np.isnan(expected_metric_value) == False:
            assert np.isclose(
                expected_metric_value,
                result.metrics[metric_key],
                rtol=1e-3,
            )


@pytest.mark.usefixtures("new_clean_dir")
def test_load_model():
    pass


@pytest.mark.usefixtures("new_clean_dir")
def test_log_predictions():
    pass

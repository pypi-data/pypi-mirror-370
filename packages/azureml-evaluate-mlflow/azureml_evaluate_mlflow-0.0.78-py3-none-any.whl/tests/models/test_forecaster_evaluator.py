# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""The tests for forecasting scoring."""
import unittest

import numpy as np
import pandas as pd
import tempfile

from ddt import ddt, data, unpack
from typing import Any, Dict

import pytest
from mlflow.models.model import Model
from sklearn.pipeline import Pipeline

import azureml.evaluate.mlflow as aml_mlflow
from azureml.automl.runtime import _ml_engine
from azureml.automl.runtime.featurizer.transformer.timeseries.timeseries_transformer import TimeSeriesPipelineType, \
    TimeSeriesTransformer
from azureml.automl.runtime.shared.model_wrappers import ForecastingPipelineWrapper
from azureml.automl.core.featurization.featurizationconfig import FeaturizationConfig
from azureml.automl.core.shared.constants import TimeSeries, TimeSeriesInternal
from azureml.evaluate.mlflow.aml import AMLForecastModel
from azureml.evaluate.mlflow.constants import ForecastFlavors
from azureml.metrics import constants
from azureml.metrics.tabular.regression._regression import NormRMSE
import mlflow
from tests.helper_functions import delete_directory


@pytest.mark.hftest2
@ddt
class TestForecasterEvaluator(unittest.TestCase):
    """The set of tests for forecast model testing."""
    TIME_COLUMN_NAME = 'date'

    def _train_forecasting_model(self, X_train: pd.DataFrame, y_train: np.ndarray,
                                 ts_param_dict: Dict[str, Any] = None, agg_len: int = 1):
        """Train the model for Forecasting."""
        ts_config = {
            TimeSeries.TIME_COLUMN_NAME: TestForecasterEvaluator.TIME_COLUMN_NAME,
            TimeSeries.GRAIN_COLUMN_NAMES: None,
            TimeSeries.MAX_HORIZON: 10,
            TimeSeriesInternal.DROP_NA: True,
        }
        if ts_param_dict:
            ts_config.update(ts_param_dict)
        featurization_config = FeaturizationConfig()
        if ts_config.get("featurization_config"):
            del ts_config["featurization_config"]
        (
            forecasting_pipeline,
            ts_param_dict,
            lookback_removed,
            time_index_non_holiday_features
        ) = _ml_engine.suggest_featurizers_timeseries(
            X_train,
            y_train,
            featurization_config,
            ts_config,
            TimeSeriesPipelineType.FULL,
            y_transformer=None
        )

        ts_transformer = TimeSeriesTransformer(
            forecasting_pipeline,
            TimeSeriesPipelineType.FULL,
            featurization_config,
            time_index_non_holiday_features,
            lookback_removed,
            **ts_config
        )
        ts_transformer.fit(X_train, y_train)
        mock_estimator = MockPredictor(agg_len)

        mock_estimator.fit(X_train, y_train)
        model = Pipeline([('ts_transformer', ts_transformer),
                          ('estimator', mock_estimator)])

        stdev = list(np.arange(1, ts_config[TimeSeries.MAX_HORIZON] + 1))
        fw = ForecastingPipelineWrapper(
            pipeline=model, stddev=stdev)
        model_meta = Model()
        return AMLForecastModel(model_meta=model_meta, model_impl=fw)

    def _assert_metrics(self, eval_result, expected_nrmse, expect_artifacts, test_len=10):
        """Check that the metrics are correct."""
        # Check metrics
        self.assertIn(constants.Metric.NormRMSE, eval_result.metrics)
        self.assertAlmostEqual(eval_result.metrics[constants.Metric.NormRMSE], expected_nrmse)
        # Check artifacts
        if expect_artifacts:
            self.assertIn(constants.Metric.ForecastMAPE, eval_result.artifacts)
            mape = eval_result.artifacts[constants.Metric.ForecastMAPE].content
            self.assertEqual(len(mape['data']), test_len)
            self.assertFalse(any(np.isnan(mape['data'][i]['mape']) for i in np.arange(10, dtype='float')))
        else:
            # The time series ID distribution table is present regardless if historic data are provided.
            self.assertEqual(len(eval_result.artifacts), 1)
            self.assertListEqual(list(eval_result.artifacts.keys()), ['forecast_time_series_id_distribution_table'])

    @data([True, True],
          [True, False],
          [False, True],
          [False, False]
          )
    @unpack
    def test_model_evaluator(self, use_X_train, model_has_min_max):
        """Test model evaluator with default parameters."""
        X = pd.DataFrame({
            TestForecasterEvaluator.TIME_COLUMN_NAME: pd.date_range('2001-01-01', freq='D', periods=40)
        })
        X_train = X.iloc[:-10]
        X_test = X.iloc[-10:]
        y_train = np.arange(30)
        y_test = np.arange(30, 40)
        ml_model = self._train_forecasting_model(X_train, y_train)
        X_test['y'] = y_test
        cfg = {ForecastFlavors.FLAVOUR: ForecastFlavors.RECURSIVE_FORECAST}
        if not model_has_min_max:
            ml_model._model_impl._ts_transformer.y_min_dict = {}
            ml_model._model_impl._ts_transformer.y_max_dict = {}
        else:
            # Deliberately set different value to make check work
            ml_model._model_impl.y_min_dict[TimeSeriesInternal.DUMMY_GRAIN_COLUMN] = 25
            ml_model._model_impl.y_max_dict[TimeSeriesInternal.DUMMY_GRAIN_COLUMN] = 34
        if use_X_train:
            cfg['X_train'] = X_train
            cfg['y_train'] = y_train
            y_min = np.min(y_train)
            y_max = np.max(y_train)
            y_std = np.std(y_train)
        else:
            y_std = np.std(y_test)
            y_min = 25 if model_has_min_max else np.min(y_test)
            y_max = 34 if model_has_min_max else np.max(y_test)

        eval_result = aml_mlflow.evaluate(
            ml_model,
            X_test,
            targets='y',
            feature_names=[TestForecasterEvaluator.TIME_COLUMN_NAME],
            model_type='forecaster',
            dataset_name='test_experiment',
            evaluators=["azureml"],
            evaluator_config={"azureml": cfg},
        )
        expected_nrmse = NormRMSE(
            y_test=y_test,
            y_pred=ml_model._model_impl.steps[-1][1].predict(X_test),
            y_min=y_min,
            y_max=y_max,
            y_std=y_std).compute()
        self._assert_metrics(eval_result, expected_nrmse, use_X_train)

    @data(
        ForecastFlavors.RECURSIVE_FORECAST,
        ForecastFlavors.ROLLING_FORECAST)
    def test_model_evaluator_with_grains(self, forecast_flavor):
        """Test model evaluation if there are grain columns in a data set."""
        ts_dict = {
            TimeSeries.GRAIN_COLUMN_NAMES: 'grain',
        }
        np.random.seed(42)
        X_train = pd.DataFrame({
            TestForecasterEvaluator.TIME_COLUMN_NAME: 2 * list(
                pd.date_range('2001-01-01', freq='D', periods=20)),
            'grain': np.repeat(['a', 'b'], 20),
        })
        y_train = np.concatenate([np.random.rand(20), 3 * np.random.rand(20)])
        X_test = pd.DataFrame({
            TestForecasterEvaluator.TIME_COLUMN_NAME: 2 * list(
                pd.date_range('2001-01-21', freq='D', periods=10)),
            'grain': np.repeat(['a', 'b'], 10)
        })
        y_test = np.concatenate([np.random.rand(10), 3 * np.random.rand(10)])
        X_test['y'] = y_test
        ml_model = self._train_forecasting_model(X_train, y_train, ts_dict)
        y_pred, _ = ml_model.forecast(X_test)
        y_std = np.std(y_train)
        cfg = {
            ForecastFlavors.FLAVOUR: forecast_flavor,
            'X_train': X_train,
            'y_train': y_train
        }
        eval_result = aml_mlflow.evaluate(
            ml_model,
            X_test,
            targets='y',
            feature_names=[TestForecasterEvaluator.TIME_COLUMN_NAME, 'grain'],
            model_type='forecaster',
            dataset_name='test_experiment',
            evaluators=["azureml"],
            evaluator_config={"azureml": cfg},
        )
        rmse1 = NormRMSE(
            y_test=y_test, y_pred=y_pred,
            y_min=np.min(y_train[:-20]),
            y_max=np.max(y_train[:-20]),
            y_std=y_std).compute()
        rmse2 = NormRMSE(
            y_test=y_test, y_pred=y_pred,
            y_min=np.min(y_train[-10:]),
            y_max=np.max(y_train[-10:]),
            y_std=y_std).compute()
        self._assert_metrics(eval_result, np.mean([rmse1, rmse2]), True)

    @staticmethod
    def _check_attached_file_rolling(name, path_or_stream, **kwargs):
        """Check that the file contains the correct values."""
        data = pd.read_csv(path_or_stream)
        assert 'grain' in data
        assert 'date' in data
        assert '_automl_forecast_origin' in data

    @staticmethod
    def _check_attached_file(name, path_or_stream, **kwargs):
        """Check that the file contains the correct values."""
        data = pd.read_csv(path_or_stream)
        assert 'grain' in data
        assert 'date' in data

    def test_evaluation_on_aggregated_data_set(self):
        """Test evaluation if data were aggregated."""
        ts_dict = {
            TimeSeries.TARGET_AGG_FUN: 'sum',
            TimeSeries.FREQUENCY: 'W-MON'
        }
        X = pd.DataFrame({
            TestForecasterEvaluator.TIME_COLUMN_NAME: pd.date_range('2001-01-02', freq='D', periods=210)
        })
        X_train = X.iloc[:-70]
        X_test = X.iloc[-70:]
        X_train['y'] = np.arange(140)
        X_test['y'] = np.arange(140, 210)
        # Preaggregate data here
        X_agg = X_train.copy()
        X_agg.set_index([TestForecasterEvaluator.TIME_COLUMN_NAME], inplace=True)
        X_agg = X_agg.resample(rule='W-MON').agg('sum')
        X_agg.reset_index(inplace=True, drop=False)
        y_agg = X_agg.pop('y').values
        ml_model = self._train_forecasting_model(X_agg, y_agg, ts_dict, agg_len=7)
        X_agg_test = X_test.copy()
        X_agg_test.set_index([TestForecasterEvaluator.TIME_COLUMN_NAME], inplace=True)
        X_agg_test = X_agg_test.resample(rule='W-MON').agg('sum')
        X_agg_test.reset_index(inplace=True, drop=False)
        expected_nrmse = NormRMSE(
            y_test=X_agg_test['y'].values,
            y_pred=ml_model._model_impl.steps[-1][1].predict(X_agg_test),
            y_min=np.min(y_agg),
            y_max=np.max(y_agg),
            y_std=np.std(y_agg)).compute()
        y_train = X_train.pop('y').values
        eval_result = aml_mlflow.evaluate(
            ml_model,
            X_test,
            targets='y',
            feature_names=[TestForecasterEvaluator.TIME_COLUMN_NAME],
            model_type='forecaster',
            dataset_name='test_experiment',
            evaluators=["azureml"],
            evaluator_config={"azureml": {
                ForecastFlavors.FLAVOUR: ForecastFlavors.RECURSIVE_FORECAST,
                'X_train': X_train, 'y_train': y_train
            }},
        )
        self._assert_metrics(eval_result, expected_nrmse, True)

    def test_load_mlflow_model(self):
        """Test loading of an mlflow model."""
        X = pd.DataFrame({
            TestForecasterEvaluator.TIME_COLUMN_NAME: pd.date_range('2001-01-01', freq='D', periods=40)
        })
        X_train = X.iloc[:-10]
        X_test = X.iloc[-10:]
        y_train = np.arange(30)
        y_test = np.arange(30, 40)
        X_test['y'] = y_test
        cfg = {ForecastFlavors.FLAVOUR: ForecastFlavors.RECURSIVE_FORECAST}
        ml_model = self._train_forecasting_model(X_train, y_train)
        metadata = {}
        mlflow_model = Model(metadata=metadata)
        with tempfile.TemporaryDirectory() as d:
            mlflow.sklearn.save_model(ml_model._model_impl, d, mlflow_model=mlflow_model)
            eval_result = aml_mlflow.evaluate(
                d,
                X_test,
                targets='y',
                feature_names=[TestForecasterEvaluator.TIME_COLUMN_NAME],
                model_type='forecaster',
                dataset_name='test_experiment',
                evaluators=["azureml"],
                evaluator_config={"azureml": cfg},
            )
            delete_directory(d)

        expected_nrmse = NormRMSE(
            y_test=y_test,
            y_pred=ml_model._model_impl.steps[-1][1].predict(X_test),
            y_min=np.min(y_train),
            y_max=np.max(y_train),
            y_std=np.std(y_test)).compute()
        self._assert_metrics(eval_result, expected_nrmse, False)


class MockPredictor:
    """Mock predictor class"""

    def __init__(self, window_size):
        self.last = 0
        self.window_size = window_size

    def fit(self, X, y):
        self.last = X.shape[0] * self.window_size

    def predict(self, X):
        first = self.last
        predictions = np.zeros((X.shape[0]))
        for i in range(X.shape[0]):
            predictions[i] = np.sum(np.arange(first, first + self.window_size))
            first += self.window_size
        np.random.seed(42)
        return predictions + np.random.rand(predictions.shape[0])


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()

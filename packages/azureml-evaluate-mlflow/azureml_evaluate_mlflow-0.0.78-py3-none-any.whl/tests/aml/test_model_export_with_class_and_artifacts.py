# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import cloudpickle
import os
from unittest import mock
import numpy as np
import pandas as pd
import pytest
import sklearn.datasets
import sklearn.linear_model
import sklearn.neighbors
import yaml
from azureml.evaluate.mlflow.aml import AMLGenericModel
from mlflow.types import Schema, ColSpec
import azureml.evaluate.mlflow as azureml_mlflow
import azureml.evaluate.mlflow.aml
import azureml.evaluate.mlflow.aml.model
from mlflow.exceptions import MlflowException
from mlflow.models.utils import _read_example
from mlflow.tracking.artifact_utils import (
    get_artifact_uri as utils_get_artifact_uri,
    _download_artifact_from_uri,
)
from mlflow.models import Model, infer_signature, ModelSignature
from mlflow.utils.environment import _mlflow_conda_env
from mlflow.utils.file_utils import TempDir
from mlflow.utils.model_utils import _get_flavor_configuration
from azureml.evaluate.mlflow.hftransformers import extract_package_and_extra
from mlflow.tracking._model_registry import DEFAULT_AWAIT_MAX_SLEEP_SECONDS

import tests
from tests.helper_functions import pyfunc_serve_and_score_model
from tests.helper_functions import (
    _compare_conda_env_requirements,
    _assert_pip_requirements,
    delete_directory,
)

from ..models.utils import (  # pylint: disable=unused-import
    multiclass_llm_model_uri,
    multiclass_llm_aml_model_uri,
    newsgroup_dataset
)


def get_model_class():
    """
    Defines a custom Python model class that wraps a scikit-learn estimator.
    This can be invoked within a pytest fixture to define the class in the ``__main__`` scope.
    Alternatively, it can be invoked within a module to define the class in the module's scope.
    """

    class CustomSklearnModel(azureml_mlflow.aml.AzureMLModel):
        def __init__(self, predict_fn):
            self.predict_fn = predict_fn

        def load_context(self, context):
            super().load_context(context)
            # pylint: disable=attribute-defined-outside-init
            self.model = azureml_mlflow.sklearn.load_model(model_uri=context.artifacts["sk_model"])

        def predict(self, context, model_input):
            return self.predict_fn(self.model, model_input)

    return CustomSklearnModel


class ModuleScopedSklearnModel(get_model_class()):
    """
    A custom Python model class defined in the test module scope.
    """


@pytest.fixture(scope="module")
def main_scoped_model_class():
    """
    A custom Python model class defined in the ``__main__`` scope.
    """
    return get_model_class()


@pytest.fixture(scope="module")
def iris_data():
    iris = sklearn.datasets.load_iris()
    x = iris.data[:, :2]
    y = iris.target
    return x, y


@pytest.fixture(scope="module")
def sklearn_knn_model(iris_data):
    x, y = iris_data
    knn_model = sklearn.neighbors.KNeighborsClassifier()
    knn_model.fit(x, y)
    return knn_model


@pytest.fixture(scope="module")
def sklearn_logreg_model(iris_data):
    x, y = iris_data
    linear_lr = sklearn.linear_model.LogisticRegression()
    linear_lr.fit(x, y)
    return linear_lr


@pytest.fixture
def model_path(tmpdir):
    return os.path.join(str(tmpdir), "model")


@pytest.fixture
def pyfunc_custom_env(tmpdir):
    conda_env = os.path.join(str(tmpdir), "conda_env.yml")
    _mlflow_conda_env(
        conda_env,
        additional_pip_deps=["scikit-learn", "pytest", "cloudpickle"],
    )
    return conda_env


def _conda_env():
    # NB: We need azureml_mlflow as a dependency in the environment.
    return _mlflow_conda_env(
        additional_pip_deps=[
            "cloudpickle=={}".format(cloudpickle.__version__),
            "scikit-learn=={}".format(sklearn.__version__),
        ],
    )


@pytest.mark.hftest1
@pytest.mark.parametrize("requirement, expected_package_name, expected_extra_name",
                         [("azureml-metrics[all]", "azureml-metrics", "all"),
                          ("azureml-metrics", "azureml-metrics", None),
                          ("torch", "torch", None)])
def test_extract_package_and_extra(requirement, expected_package_name, expected_extra_name):
    package_name, extra_name = extract_package_and_extra(requirement)

    assert package_name == expected_package_name
    if expected_extra_name is None:
        assert extra_name is None
    else:
        assert extra_name == expected_extra_name


@pytest.mark.hftest1
@pytest.mark.usefixtures("new_clean_dir")
def test_model_save_load(sklearn_knn_model, main_scoped_model_class, iris_data, tmpdir):
    sklearn_model_path = os.path.join(str(tmpdir), "sklearn_model")
    azureml_mlflow.sklearn.save_model(sk_model=sklearn_knn_model, path=sklearn_model_path)

    def test_predict(sk_model, model_input):
        return sk_model.predict(model_input) * 2

    aml_model_path = os.path.join(str(tmpdir), "aml_model")

    azureml_mlflow.aml.save_model(
        path=aml_model_path,
        artifacts={"sk_model": sklearn_model_path},
        conda_env=_conda_env(),
        aml_model=main_scoped_model_class(test_predict),
    )

    loaded_pyfunc_model = azureml_mlflow.aml.load_model(model_uri=aml_model_path, model_type="classifier")
    np.testing.assert_array_equal(
        loaded_pyfunc_model.predict(iris_data[0]),
        test_predict(sk_model=sklearn_knn_model, model_input=iris_data[0]),
    )
    delete_directory(tmpdir)

# def test_multiclass_model_save_load(multiclass_llm_aml_model_uri, newsgroup_dataset):
#     loaded_aml_model = azureml_mlflow.aml.load_model(model_uri=multiclass_llm_aml_model_uri)
#     # loaded_aml_model = azureml_mlflow.aml.load_model(model_uri=multiclass_llm_model_uri)
#     assert hasattr(loaded_aml_model, "predict")
#     assert hasattr(loaded_aml_model, "predict_proba")
#     # ToDo: add assertion for prediciton comparison

@pytest.mark.hftest1
@pytest.mark.usefixtures("new_clean_dir")
def test_pyfunc_model_log_load_no_active_run(sklearn_knn_model, main_scoped_model_class, iris_data):
    sklearn_artifact_path = "sk_model_no_run"
    with azureml_mlflow.start_run():
        azureml_mlflow.sklearn.log_model(sk_model=sklearn_knn_model, artifact_path=sklearn_artifact_path)
        sklearn_model_uri = "runs:/{run_id}/{artifact_path}".format(
            run_id=azureml_mlflow.active_run().info.run_id, artifact_path=sklearn_artifact_path
        )

    def test_predict(sk_model, model_input):
        return sk_model.predict(model_input) * 2

    pyfunc_artifact_path = "aml_model"
    assert azureml_mlflow.active_run() is None
    azureml_mlflow.aml.log_model(
        artifact_path=pyfunc_artifact_path,
        artifacts={"sk_model": sklearn_model_uri},
        aml_model=main_scoped_model_class(test_predict),
    )
    pyfunc_model_uri = "runs:/{run_id}/{artifact_path}".format(
        run_id=azureml_mlflow.active_run().info.run_id, artifact_path=pyfunc_artifact_path
    )
    loaded_pyfunc_model = azureml_mlflow.aml.load_model(model_uri=pyfunc_model_uri, model_type="classifier")
    np.testing.assert_array_equal(
        loaded_pyfunc_model.predict(iris_data[0]),
        test_predict(sk_model=sklearn_knn_model, model_input=iris_data[0]),
    )
    azureml_mlflow.end_run()


@pytest.mark.hftest1
@pytest.mark.usefixtures("new_clean_dir")
def test_model_log_load(sklearn_knn_model, main_scoped_model_class, iris_data):
    sklearn_artifact_path = "sk_model"
    with azureml_mlflow.start_run():
        azureml_mlflow.sklearn.log_model(sk_model=sklearn_knn_model, artifact_path=sklearn_artifact_path)
        sklearn_model_uri = "runs:/{run_id}/{artifact_path}".format(
            run_id=azureml_mlflow.active_run().info.run_id, artifact_path=sklearn_artifact_path
        )

    def test_predict(sk_model, model_input):
        return sk_model.predict(model_input) * 2

    pyfunc_artifact_path = "aml_model"
    with azureml_mlflow.start_run():
        model_info = azureml_mlflow.aml.log_model(
            artifact_path=pyfunc_artifact_path,
            artifacts={"sk_model": sklearn_model_uri},
            aml_model=main_scoped_model_class(test_predict),
        )
        aml_model_uri = "runs:/{run_id}/{artifact_path}".format(
            run_id=azureml_mlflow.active_run().info.run_id, artifact_path=pyfunc_artifact_path
        )
        assert model_info.model_uri == aml_model_uri
        aml_model_path = _download_artifact_from_uri(
            "runs:/{run_id}/{artifact_path}".format(
                run_id=azureml_mlflow.active_run().info.run_id, artifact_path=pyfunc_artifact_path
            )
        )
        model_config = Model.load(os.path.join(aml_model_path, "MLmodel"))

    loaded_pyfunc_model = azureml_mlflow.aml.load_model(model_uri=aml_model_uri, model_type="classifier")
    assert model_config.to_yaml() == loaded_pyfunc_model.metadata.to_yaml()
    np.testing.assert_array_equal(
        loaded_pyfunc_model.predict(iris_data[0]),
        test_predict(sk_model=sklearn_knn_model, model_input=iris_data[0]),
    )


@pytest.mark.hftest1
@pytest.mark.usefixtures("new_clean_dir")
def test_signature_and_examples_are_saved_correctly(iris_data, main_scoped_model_class, tmpdir):
    sklearn_model_path = tmpdir.join("sklearn_model").strpath
    azureml_mlflow.sklearn.save_model(sk_model=sklearn_knn_model, path=sklearn_model_path)

    def test_predict(sk_model, model_input):
        return sk_model.predict(model_input) * 2

    data = iris_data
    signature_ = infer_signature(*data)
    example_ = data[0][:3, ]
    for signature in (None, signature_):
        for example in (None, example_):
            with TempDir() as tmp:
                path = tmp.path("model")
                azureml_mlflow.aml.save_model(
                    path=path,
                    artifacts={"sk_model": sklearn_model_path},
                    aml_model=main_scoped_model_class(test_predict),
                    signature=signature,
                    input_example=example,
                )
                mlflow_model = Model.load(path)
                assert signature == mlflow_model.signature
                if example is None:
                    assert mlflow_model.saved_input_example_info is None
                else:
                    assert np.array_equal(_read_example(mlflow_model, path), example)
    delete_directory(tmpdir)


# def test_log_model_calls_register_model(sklearn_knn_model, main_scoped_model_class):
#     register_model_patch = mock.patch("azureml.evaluate.mlflow.register_model")
#     with register_model_patch:
#         sklearn_artifact_path = "sk_model_no_run"
#         with azureml_mlflow.start_run():
#             azureml_mlflow.sklearn.log_model(
#                 sk_model=sklearn_knn_model, artifact_path=sklearn_artifact_path
#             )
#             sklearn_model_uri = "runs:/{run_id}/{artifact_path}".format(
#                 run_id=azureml_mlflow.active_run().info.run_id, artifact_path=sklearn_artifact_path
#             )
#
#         def test_predict(sk_model, model_input):
#             return sk_model.predict(model_input) * 2
#
#         pyfunc_artifact_path = "aml_model"
#         assert azureml_mlflow.active_run() is None
#         azureml_mlflow.aml.log_model(
#             artifact_path=pyfunc_artifact_path,
#             artifacts={"sk_model": sklearn_model_uri},
#             aml_model=main_scoped_model_class(test_predict),
#             registered_model_name="AdsModel1",
#         )
#         model_uri = "runs:/{run_id}/{artifact_path}".format(
#             run_id=azureml_mlflow.active_run().info.run_id, artifact_path=pyfunc_artifact_path
#         )
#         azureml_mlflow.register_model.assert_called_once_with(
#             model_uri, "AdsModel1", await_registration_for=DEFAULT_AWAIT_MAX_SLEEP_SECONDS
#         )
#         azureml_mlflow.end_run()
#

@pytest.mark.hftest1
@pytest.mark.usefixtures("new_clean_dir")
def test_log_model_no_registered_model_name(sklearn_knn_model, main_scoped_model_class):
    register_model_patch = mock.patch("azureml.evaluate.mlflow.register_model")
    with register_model_patch:
        sklearn_artifact_path = "sk_model_no_run"
        with azureml_mlflow.start_run():
            azureml_mlflow.sklearn.log_model(
                sk_model=sklearn_knn_model, artifact_path=sklearn_artifact_path
            )
            sklearn_model_uri = "runs:/{run_id}/{artifact_path}".format(
                run_id=azureml_mlflow.active_run().info.run_id, artifact_path=sklearn_artifact_path
            )

        def test_predict(sk_model, model_input):
            return sk_model.predict(model_input) * 2

        pyfunc_artifact_path = "aml_model"
        assert azureml_mlflow.active_run() is None
        azureml_mlflow.aml.log_model(
            artifact_path=pyfunc_artifact_path,
            artifacts={"sk_model": sklearn_model_uri},
            aml_model=main_scoped_model_class(test_predict),
        )
        azureml_mlflow.register_model.assert_not_called()
        azureml_mlflow.end_run()


# def test_model_load_from_remote_uri_succeeds(
#     sklearn_knn_model, main_scoped_model_class, tmpdir, mock_s3_bucket, iris_data
# ):
#     artifact_root = "s3://{bucket_name}".format(bucket_name=mock_s3_bucket)
#     artifact_repo = S3ArtifactRepository(artifact_root)
#
#     sklearn_model_path = os.path.join(str(tmpdir), "sklearn_model")
#     azureml_mlflow.sklearn.save_model(sk_model=sklearn_knn_model, path=sklearn_model_path)
#     sklearn_artifact_path = "sk_model"
#     artifact_repo.log_artifacts(sklearn_model_path, artifact_path=sklearn_artifact_path)
#
#     def test_predict(sk_model, model_input):
#         return sk_model.predict(model_input) * 2
#
#     pyfunc_model_path = os.path.join(str(tmpdir), "aml_model")
#     azureml_mlflow.aml.save_model(
#         path=pyfunc_model_path,
#         artifacts={"sk_model": sklearn_model_path},
#         aml_model=main_scoped_model_class(test_predict),
#         conda_env=_conda_env(),
#     )
#
#     pyfunc_artifact_path = "aml_model"
#     artifact_repo.log_artifacts(pyfunc_model_path, artifact_path=pyfunc_artifact_path)
#
#     model_uri = artifact_root + "/" + pyfunc_artifact_path
#     loaded_pyfunc_model = azureml_mlflow.aml.load_model(model_uri=model_uri, model_type="classifier")
#     np.testing.assert_array_equal(
#         loaded_pyfunc_model.predict(iris_data[0]),
#         test_predict(sk_model=sklearn_knn_model, model_input=iris_data[0]),
#     )

@pytest.mark.hftest1
@pytest.mark.usefixtures("new_clean_dir")
def test_add_to_model_adds_specified_kwargs_to_mlmodel_configuration():
    custom_kwargs = {
        "key1": "value1",
        "key2": 20,
        "key3": range(10),
    }
    model_config = Model()
    azureml_mlflow.aml.add_to_model(
        model=model_config,
        loader_module=os.path.basename(__file__)[:-3],
        data="data",
        code="code",
        env=None,
        **custom_kwargs,
    )

    assert azureml_mlflow.aml.FLAVOR_NAME in model_config.flavors
    assert all(item in model_config.flavors[azureml_mlflow.aml.FLAVOR_NAME] for item in custom_kwargs)


#
# def test_pyfunc_model_serving_without_conda_env_activation_succeeds_with_main_scoped_class(
#     sklearn_knn_model, main_scoped_model_class, iris_data, tmpdir
# ):
#     sklearn_model_path = os.path.join(str(tmpdir), "sklearn_model")
#     azureml_mlflow.sklearn.save_model(sk_model=sklearn_knn_model, path=sklearn_model_path)
#
#     def test_predict(sk_model, model_input):
#         return sk_model.predict(model_input) * 2
#
#     pyfunc_model_path = os.path.join(str(tmpdir), "aml_model")
#     azureml_mlflow.aml.save_model(
#         path=pyfunc_model_path,
#         artifacts={"sk_model": sklearn_model_path},
#         aml_model=main_scoped_model_class(test_predict),
#         conda_env=_conda_env(),
#     )
#     loaded_pyfunc_model = azureml_mlflow.aml.load_model(model_uri=pyfunc_model_path, model_type="classifier")
#
#     sample_input = pd.DataFrame(iris_data[0])
#     scoring_response = pyfunc_serve_and_score_model(
#         model_uri=pyfunc_model_path,
#         data=sample_input,
#         content_type=pyfunc_scoring_server.CONTENT_TYPE_JSON_SPLIT_ORIENTED,
#         extra_args=["--env-manager", "local"],
#     )
#     assert scoring_response.status_code == 200
#     np.testing.assert_array_equal(
#         np.array(json.loads(scoring_response.text)), loaded_pyfunc_model.predict(sample_input)
#     )
#
#
# def test_pyfunc_model_serving_with_conda_env_activation_succeeds_with_main_scoped_class(
#     sklearn_knn_model, main_scoped_model_class, iris_data, tmpdir
# ):
#     sklearn_model_path = os.path.join(str(tmpdir), "sklearn_model")
#     azureml_mlflow.sklearn.save_model(sk_model=sklearn_knn_model, path=sklearn_model_path)
#
#     def test_predict(sk_model, model_input):
#         return sk_model.predict(model_input) * 2
#
#     pyfunc_model_path = os.path.join(str(tmpdir), "aml_model")
#     azureml_mlflow.aml.save_model(
#         path=pyfunc_model_path,
#         artifacts={"sk_model": sklearn_model_path},
#         aml_model=main_scoped_model_class(test_predict),
#         conda_env=_conda_env(),
#     )
#     loaded_pyfunc_model = azureml_mlflow.aml.load_model(model_uri=pyfunc_model_path, model_type="classifier")
#
#     sample_input = pd.DataFrame(iris_data[0])
#     scoring_response = pyfunc_serve_and_score_model(
#         model_uri=pyfunc_model_path,
#         data=sample_input,
#         content_type=pyfunc_scoring_server.CONTENT_TYPE_JSON_SPLIT_ORIENTED,
#     )
#     assert scoring_response.status_code == 200
#     np.testing.assert_array_equal(
#         np.array(json.loads(scoring_response.text)), loaded_pyfunc_model.predict(sample_input)
#     )
#
#
# def test_pyfunc_model_serving_without_conda_env_activation_succeeds_with_module_scoped_class(
#     sklearn_knn_model, iris_data, tmpdir
# ):
#     sklearn_model_path = os.path.join(str(tmpdir), "sklearn_model")
#     azureml_mlflow.sklearn.save_model(sk_model=sklearn_knn_model, path=sklearn_model_path)
#
#     def test_predict(sk_model, model_input):
#         return sk_model.predict(model_input) * 2
#
#     pyfunc_model_path = os.path.join(str(tmpdir), "aml_model")
#     azureml_mlflow.aml.save_model(
#         path=pyfunc_model_path,
#         artifacts={"sk_model": sklearn_model_path},
#         aml_model=ModuleScopedSklearnModel(test_predict),
#         code_path=[os.path.dirname(tests.__file__)],
#         conda_env=_conda_env(),
#     )
#     loaded_pyfunc_model = azureml_mlflow.aml.load_model(model_uri=pyfunc_model_path, model_type="classifier")
#
#     sample_input = pd.DataFrame(iris_data[0])
#     scoring_response = pyfunc_serve_and_score_model(
#         model_uri=pyfunc_model_path,
#         data=sample_input,
#         content_type=pyfunc_scoring_server.CONTENT_TYPE_JSON_SPLIT_ORIENTED,
#         extra_args=["--env-manager", "local"],
#     )
#     assert scoring_response.status_code == 200
#     np.testing.assert_array_equal(
#         np.array(json.loads(scoring_response.text)), loaded_pyfunc_model.predict(sample_input)
#     )
#

# def test_pyfunc_cli_predict_command_without_conda_env_activation_succeeds(
#     sklearn_knn_model, main_scoped_model_class, iris_data, tmpdir
# ):
#     sklearn_model_path = os.path.join(str(tmpdir), "sklearn_model")
#     azureml_mlflow.sklearn.save_model(sk_model=sklearn_knn_model, path=sklearn_model_path)
#
#     def test_predict(sk_model, model_input):
#         return sk_model.predict(model_input) * 2
#
#     pyfunc_model_path = os.path.join(str(tmpdir), "aml_model")
#     azureml_mlflow.aml.save_model(
#         path=pyfunc_model_path,
#         artifacts={"sk_model": sklearn_model_path},
#         aml_model=main_scoped_model_class(test_predict),
#         conda_env=_conda_env(),
#     )
#     loaded_pyfunc_model = azureml_mlflow.aml.load_model(model_uri=pyfunc_model_path, model_type="classifier")
#
#     sample_input = pd.DataFrame(iris_data[0])
#     input_csv_path = os.path.join(str(tmpdir), "input with spaces.csv")
#     sample_input.to_csv(input_csv_path, header=True, index=False)
#     output_json_path = os.path.join(str(tmpdir), "output.json")
#     process = Popen(
#         [
#             "azureml_mlflow",
#             "models",
#             "predict",
#             "--model-uri",
#             pyfunc_model_path,
#             "-i",
#             input_csv_path,
#             "--content-type",
#             "csv",
#             "-o",
#             output_json_path,
#             "--env-manager",
#             "local",
#         ],
#         stdout=PIPE,
#         stderr=PIPE,
#         preexec_fn=os.setsid,
#     )
#     _, stderr = process.communicate()
#     assert 0 == process.wait(), "stderr = \n\n{}\n\n".format(stderr)
#
#     result_df = pandas.read_json(output_json_path, orient="records")
#     np.testing.assert_array_equal(
#         result_df.values.transpose()[0], loaded_pyfunc_model.predict(sample_input)
#     )

#
# def test_pyfunc_cli_predict_command_with_conda_env_activation_succeeds(
#     sklearn_knn_model, main_scoped_model_class, iris_data, tmpdir
# ):
#     sklearn_model_path = os.path.join(str(tmpdir), "sklearn_model")
#     azureml_mlflow.sklearn.save_model(sk_model=sklearn_knn_model, path=sklearn_model_path)
#
#     def test_predict(sk_model, model_input):
#         return sk_model.predict(model_input) * 2
#
#     pyfunc_model_path = os.path.join(str(tmpdir), "aml_model")
#     azureml_mlflow.aml.save_model(
#         path=pyfunc_model_path,
#         artifacts={"sk_model": sklearn_model_path},
#         aml_model=main_scoped_model_class(test_predict),
#         conda_env=_conda_env(),
#     )
#     loaded_pyfunc_model = azureml_mlflow.aml.load_model(model_uri=pyfunc_model_path, model_type="classifier")
#
#     sample_input = pd.DataFrame(iris_data[0])
#     input_csv_path = os.path.join(str(tmpdir), "input with spaces.csv")
#     sample_input.to_csv(input_csv_path, header=True, index=False)
#     output_json_path = os.path.join(str(tmpdir), "output.json")
#     process = Popen(
#         [
#             "azureml_mlflow",
#             "models",
#             "predict",
#             "--model-uri",
#             pyfunc_model_path,
#             "-i",
#             input_csv_path,
#             "--content-type",
#             "csv",
#             "-o",
#             output_json_path,
#         ],
#         stderr=PIPE,
#         stdout=PIPE,
#         preexec_fn=os.setsid,
#     )
#     _, stderr = process.communicate()
#     assert 0 == process.wait(), "stderr = \n\n{}\n\n".format(stderr)
#     result_df = pandas.read_json(output_json_path, orient="records")
#     np.testing.assert_array_equal(
#         result_df.values.transpose()[0], loaded_pyfunc_model.predict(sample_input)
#     )
#

@pytest.mark.hftest1
@pytest.mark.usefixtures("new_clean_dir")
def test_save_model_persists_specified_conda_env_in_mlflow_model_directory(
        sklearn_knn_model, main_scoped_model_class, pyfunc_custom_env, tmpdir
):
    sklearn_model_path = os.path.join(str(tmpdir), "sklearn_model")
    azureml_mlflow.sklearn.save_model(
        sk_model=sklearn_knn_model,
        path=sklearn_model_path,
        serialization_format=azureml_mlflow.sklearn.SERIALIZATION_FORMAT_CLOUDPICKLE,
    )

    pyfunc_model_path = os.path.join(str(tmpdir), "aml_model")
    azureml_mlflow.aml.save_model(
        path=pyfunc_model_path,
        artifacts={"sk_model": sklearn_model_path},
        aml_model=main_scoped_model_class(predict_fn=None),
        conda_env=pyfunc_custom_env,
    )

    pyfunc_conf = _get_flavor_configuration(
        model_path=pyfunc_model_path, flavor_name=azureml_mlflow.aml.FLAVOR_NAME
    )
    saved_conda_env_path = os.path.join(pyfunc_model_path, pyfunc_conf[azureml_mlflow.aml.ENV])
    assert os.path.exists(saved_conda_env_path)
    assert saved_conda_env_path != pyfunc_custom_env

    with open(pyfunc_custom_env, "r") as f:
        pyfunc_custom_env_parsed = yaml.safe_load(f)
    with open(saved_conda_env_path, "r") as f:
        saved_conda_env_parsed = yaml.safe_load(f)
    assert saved_conda_env_parsed == pyfunc_custom_env_parsed
    delete_directory(tmpdir)


@pytest.mark.hftest1
@pytest.mark.usefixtures("new_clean_dir")
def test_save_model_persists_requirements_in_mlflow_model_directory(
        sklearn_knn_model, main_scoped_model_class, pyfunc_custom_env, tmpdir
):
    sklearn_model_path = os.path.join(str(tmpdir), "sklearn_model")
    azureml_mlflow.sklearn.save_model(
        sk_model=sklearn_knn_model,
        path=sklearn_model_path,
        serialization_format=azureml_mlflow.sklearn.SERIALIZATION_FORMAT_CLOUDPICKLE,
    )

    pyfunc_model_path = os.path.join(str(tmpdir), "aml_model")
    azureml_mlflow.aml.save_model(
        path=pyfunc_model_path,
        artifacts={"sk_model": sklearn_model_path},
        aml_model=main_scoped_model_class(predict_fn=None),
        conda_env=pyfunc_custom_env,
    )

    saved_pip_req_path = os.path.join(pyfunc_model_path, "requirements.txt")
    _compare_conda_env_requirements(pyfunc_custom_env, saved_pip_req_path)
    delete_directory(tmpdir)


# def test_log_model_with_pip_requirements(main_scoped_model_class, tmpdir):
#     aml_model = main_scoped_model_class(predict_fn=None)
#     # Path to a requirements file
#     req_file = tmpdir.join("requirements.txt")
#     req_file.write("a")
#     with azureml_mlflow.start_run():
#         azureml_mlflow.aml.log_model(
#             "model", aml_model=aml_model, pip_requirements=req_file.strpath
#         )
#         _assert_pip_requirements(azureml_mlflow.get_artifact_uri("model"), ["azureml_mlflow", "a"], strict=True)
#
#     # List of requirements
#     with azureml_mlflow.start_run():
#         azureml_mlflow.aml.log_model(
#             "model", aml_model=aml_model, pip_requirements=[f"-r {req_file.strpath}", "b"]
#         )
#         _assert_pip_requirements(
#             azureml_mlflow.get_artifact_uri("model"), ["azureml_mlflow", "a", "b"], strict=True
#         )
#
#     # Constraints file
#     with azureml_mlflow.start_run():
#         azureml_mlflow.aml.log_model(
#             "model", aml_model=aml_model, pip_requirements=[f"-c {req_file.strpath}", "b"]
#         )
#         _assert_pip_requirements(
#             azureml_mlflow.get_artifact_uri("model"),
#             ["azureml_mlflow", "b", "-c constraints.txt"],
#             ["a"],
#             strict=True,
#         )
#

# def test_log_model_with_extra_pip_requirements(sklearn_knn_model, main_scoped_model_class, tmpdir):
#     sklearn_model_path = tmpdir.join("sklearn_model").strpath
#     azureml_mlflow.sklearn.save_model(sk_model=sklearn_knn_model, path=sklearn_model_path)
#
#     aml_model = main_scoped_model_class(predict_fn=None)
#     default_reqs = azureml_mlflow.aml.get_default_pip_requirements()
#
#     # Path to a requirements file
#     req_file = tmpdir.join("requirements.txt")
#     req_file.write("a")
#     with azureml_mlflow.start_run():
#         azureml_mlflow.aml.log_model(
#             "model",
#             aml_model=aml_model,
#             artifacts={"sk_model": sklearn_model_path},
#             extra_pip_requirements=req_file.strpath,
#         )
#         _assert_pip_requirements(azureml_mlflow.get_artifact_uri("model"), ["azureml_mlflow", *default_reqs, "a"])
#
#     # List of requirements
#     with azureml_mlflow.start_run():
#         azureml_mlflow.aml.log_model(
#             "model",
#             artifacts={"sk_model": sklearn_model_path},
#             aml_model=aml_model,
#             extra_pip_requirements=[f"-r {req_file.strpath}", "b"],
#         )
#         _assert_pip_requirements(
#             azureml_mlflow.get_artifact_uri("model"), ["azureml_mlflow", *default_reqs, "a", "b"]
#         )
#
#     # Constraints file
#     with azureml_mlflow.start_run():
#         azureml_mlflow.aml.log_model(
#             "model",
#             artifacts={"sk_model": sklearn_model_path},
#             aml_model=aml_model,
#             extra_pip_requirements=[f"-c {req_file.strpath}", "b"],
#         )
#         _assert_pip_requirements(
#             azureml_mlflow.get_artifact_uri("model"),
#             ["azureml_mlflow", *default_reqs, "b", "-c constraints.txt"],
#             ["a"],
#         )

@pytest.mark.hftest1
@pytest.mark.usefixtures("new_clean_dir")
def test_log_model_persists_specified_conda_env_in_mlflow_model_directory(
        sklearn_knn_model, main_scoped_model_class, pyfunc_custom_env
):
    sklearn_artifact_path = "sk_model"
    with azureml_mlflow.start_run():
        azureml_mlflow.sklearn.log_model(sk_model=sklearn_knn_model, artifact_path=sklearn_artifact_path)
        sklearn_run_id = azureml_mlflow.active_run().info.run_id

    pyfunc_artifact_path = "aml_model"
    with azureml_mlflow.start_run():
        azureml_mlflow.aml.log_model(
            artifact_path=pyfunc_artifact_path,
            artifacts={
                "sk_model": utils_get_artifact_uri(
                    artifact_path=sklearn_artifact_path, run_id=sklearn_run_id
                )
            },
            aml_model=main_scoped_model_class(predict_fn=None),
            conda_env=pyfunc_custom_env,
        )
        pyfunc_model_path = _download_artifact_from_uri(
            "runs:/{run_id}/{artifact_path}".format(
                run_id=azureml_mlflow.active_run().info.run_id, artifact_path=pyfunc_artifact_path
            )
        )

    pyfunc_conf = _get_flavor_configuration(
        model_path=pyfunc_model_path, flavor_name=azureml_mlflow.aml.FLAVOR_NAME
    )
    saved_conda_env_path = os.path.join(pyfunc_model_path, pyfunc_conf[azureml_mlflow.aml.ENV])
    assert os.path.exists(saved_conda_env_path)
    assert saved_conda_env_path != pyfunc_custom_env

    with open(pyfunc_custom_env, "r") as f:
        pyfunc_custom_env_parsed = yaml.safe_load(f)
    with open(saved_conda_env_path, "r") as f:
        saved_conda_env_parsed = yaml.safe_load(f)
    assert saved_conda_env_parsed == pyfunc_custom_env_parsed


@pytest.mark.hftest1
@pytest.mark.usefixtures("new_clean_dir")
def test_model_log_persists_requirements_in_mlflow_model_directory(
        sklearn_knn_model, main_scoped_model_class, pyfunc_custom_env
):
    sklearn_artifact_path = "sk_model"
    with azureml_mlflow.start_run():
        azureml_mlflow.sklearn.log_model(sk_model=sklearn_knn_model, artifact_path=sklearn_artifact_path)
        sklearn_run_id = azureml_mlflow.active_run().info.run_id

    pyfunc_artifact_path = "aml_model"
    with azureml_mlflow.start_run():
        azureml_mlflow.aml.log_model(
            artifact_path=pyfunc_artifact_path,
            artifacts={
                "sk_model": utils_get_artifact_uri(
                    artifact_path=sklearn_artifact_path, run_id=sklearn_run_id
                )
            },
            aml_model=main_scoped_model_class(predict_fn=None),
            conda_env=pyfunc_custom_env,
        )
        pyfunc_model_path = _download_artifact_from_uri(
            "runs:/{run_id}/{artifact_path}".format(
                run_id=azureml_mlflow.active_run().info.run_id, artifact_path=pyfunc_artifact_path
            )
        )

    saved_pip_req_path = os.path.join(pyfunc_model_path, "requirements.txt")
    _compare_conda_env_requirements(pyfunc_custom_env, saved_pip_req_path)


@pytest.mark.hftest1
@pytest.mark.usefixtures("new_clean_dir")
def test_save_model_without_specified_conda_env_uses_default_env_with_expected_dependencies(
        sklearn_logreg_model, main_scoped_model_class, tmpdir
):
    sklearn_model_path = os.path.join(str(tmpdir), "sklearn_model")
    azureml_mlflow.sklearn.save_model(sk_model=sklearn_logreg_model, path=sklearn_model_path)

    pyfunc_model_path = os.path.join(str(tmpdir), "aml_model")
    azureml_mlflow.aml.save_model(
        path=pyfunc_model_path,
        artifacts={"sk_model": sklearn_model_path},
        aml_model=main_scoped_model_class(predict_fn=None),
        conda_env=_conda_env(),
    )
    _assert_pip_requirements(pyfunc_model_path, azureml_mlflow.aml.get_default_pip_requirements())
    delete_directory(tmpdir)


@pytest.mark.hftest1
@pytest.mark.usefixtures("new_clean_dir")
def test_log_model_without_specified_conda_env_uses_default_env_with_expected_dependencies(
        sklearn_knn_model, main_scoped_model_class
):
    sklearn_artifact_path = "sk_model"
    with azureml_mlflow.start_run():
        azureml_mlflow.sklearn.log_model(sk_model=sklearn_knn_model, artifact_path=sklearn_artifact_path)
        sklearn_run_id = azureml_mlflow.active_run().info.run_id

    pyfunc_artifact_path = "aml_model"
    with azureml_mlflow.start_run():
        azureml_mlflow.aml.log_model(
            artifact_path=pyfunc_artifact_path,
            artifacts={
                "sk_model": utils_get_artifact_uri(
                    artifact_path=sklearn_artifact_path, run_id=sklearn_run_id
                )
            },
            aml_model=main_scoped_model_class(predict_fn=None),
        )
        model_uri = azureml_mlflow.get_artifact_uri(pyfunc_artifact_path)
    _assert_pip_requirements(model_uri, azureml_mlflow.aml.get_default_pip_requirements())


@pytest.mark.hftest1
@pytest.mark.usefixtures("new_clean_dir")
def test_save_model_correctly_resolves_directory_artifact_with_nested_contents(
        tmpdir, model_path, iris_data
):
    directory_artifact_path = os.path.join(str(tmpdir), "directory_artifact")
    nested_file_relative_path = os.path.join(
        "my", "somewhat", "heavily", "nested", "directory", "myfile.txt"
    )
    nested_file_path = os.path.join(directory_artifact_path, nested_file_relative_path)
    os.makedirs(os.path.dirname(nested_file_path))
    nested_file_text = "some sample file text"
    with open(nested_file_path, "w") as f:
        f.write(nested_file_text)

    class ArtifactValidationModel(azureml.evaluate.mlflow.aml.AzureMLModel):
        def predict(self, context, model_input):
            expected_file_path = os.path.join(
                context.artifacts["testdir"], nested_file_relative_path
            )
            if not os.path.exists(expected_file_path):
                return False
            else:
                with open(expected_file_path, "r") as f:
                    return f.read() == nested_file_text

    azureml_mlflow.aml.save_model(
        path=model_path,
        artifacts={"testdir": directory_artifact_path},
        aml_model=ArtifactValidationModel(),
        conda_env=_conda_env(),
    )

    loaded_model = azureml_mlflow.aml.load_model(model_uri=model_path, model_type="classifier")
    assert loaded_model.predict(iris_data[0])
    delete_directory(tmpdir)
    delete_directory(model_path)


@pytest.mark.hftest1
@pytest.mark.usefixtures("new_clean_dir")
def test_save_model_with_no_artifacts_does_not_produce_artifacts_dir(model_path):
    azureml_mlflow.aml.save_model(
        path=model_path,
        aml_model=ModuleScopedSklearnModel(predict_fn=None),
        artifacts=None,
        conda_env=_conda_env(),
    )

    assert os.path.exists(model_path)
    assert "artifacts" not in os.listdir(model_path)
    pyfunc_conf = _get_flavor_configuration(
        model_path=model_path, flavor_name=azureml_mlflow.aml.FLAVOR_NAME
    )
    assert azureml_mlflow.aml.model.CONFIG_KEY_ARTIFACTS not in pyfunc_conf
    delete_directory(model_path)


@pytest.mark.hftest1
@pytest.mark.usefixtures("new_clean_dir")
def test_save_model_with_python_model_argument_of_invalid_type_raises_exeption(tmpdir):
    match = "aml_model` must be a subclass of `AzureMLModel`"
    with pytest.raises(MlflowException, match=match):
        azureml_mlflow.aml.save_model(
            path=os.path.join(str(tmpdir), "model1"), aml_model="not the right type"
        )

    with pytest.raises(MlflowException, match=match):
        azureml_mlflow.aml.save_model(
            path=os.path.join(str(tmpdir), "model2"), aml_model="not the right type"
        )
    delete_directory(tmpdir)


@pytest.mark.hftest1
@pytest.mark.usefixtures("new_clean_dir")
def test_save_model_with_unsupported_argument_combinations_throws_exception(model_path):
    with pytest.raises(
            MlflowException, match="Either `loader_module` or `aml_model` must be specified"
    ) as exc_info:
        azureml_mlflow.aml.save_model(
            path=model_path, artifacts={"artifact": "/path/to/artifact"}, aml_model=None
        )

    aml_model = ModuleScopedSklearnModel(predict_fn=None)
    loader_module = __name__
    with pytest.raises(
            MlflowException, match="The following sets of parameters cannot be specified together"
    ) as exc_info:
        azureml_mlflow.aml.save_model(
            path=model_path, aml_model=aml_model, loader_module=loader_module
        )
    assert str(aml_model) in str(exc_info)
    assert str(loader_module) in str(exc_info)

    with pytest.raises(
            MlflowException, match="The following sets of parameters cannot be specified together"
    ) as exc_info:
        azureml_mlflow.aml.save_model(
            path=model_path,
            aml_model=aml_model,
            data_path="/path/to/data",
            artifacts={"artifact": "/path/to/artifact"},
        )

    with pytest.raises(
            MlflowException, match="Either `loader_module` or `aml_model` must be specified"
    ):
        azureml_mlflow.aml.save_model(path=model_path, aml_model=None, loader_module=None)
    delete_directory(model_path)

@pytest.mark.hftest1
@pytest.mark.usefixtures("new_clean_dir")
def test_log_model_with_unsupported_argument_combinations_throws_exception():
    match = (
        "Either `loader_module` or `aml_model` must be specified. A `loader_module` "
        "should be a python module. A `aml_model` should be a subclass of "
        "AzureMLModel"
    )
    with azureml_mlflow.start_run(), pytest.raises(MlflowException, match=match):
        azureml_mlflow.aml.log_model(
            artifact_path="aml_model",
            artifacts={"artifact": "/path/to/artifact"},
            aml_model=None,
        )

    aml_model = ModuleScopedSklearnModel(predict_fn=None)
    loader_module = __name__
    with azureml_mlflow.start_run(), pytest.raises(
            MlflowException,
            match="The following sets of parameters cannot be specified together",
    ) as exc_info:
        azureml_mlflow.aml.log_model(
            artifact_path="aml_model",
            aml_model=aml_model,
            loader_module=loader_module,
        )
    assert str(aml_model) in str(exc_info)
    assert str(loader_module) in str(exc_info)

    with azureml_mlflow.start_run(), pytest.raises(
            MlflowException, match="The following sets of parameters cannot be specified together"
    ) as exc_info:
        azureml_mlflow.aml.log_model(
            artifact_path="aml_model",
            aml_model=aml_model,
            data_path="/path/to/data",
            artifacts={"artifact1": "/path/to/artifact"},
        )

    with azureml_mlflow.start_run(), pytest.raises(
            MlflowException, match="Either `loader_module` or `aml_model` must be specified"
    ):
        azureml_mlflow.aml.log_model(artifact_path="aml_model", aml_model=None, loader_module=None)


@pytest.mark.hftest1
@pytest.mark.usefixtures("new_clean_dir")
def test_repr_can_be_called_withtout_run_id_or_artifact_path():
    model_meta = Model(
        artifact_path=None,
        run_id=None,
        flavors={"aml": {"loader_module": "someFlavour"}},
    )

    class TestModel:
        def predict(self, model_input):
            return model_input

    model_impl = TestModel()

    assert "flavor: someFlavour" in azureml_mlflow.aml.AMLModel(model_meta, model_impl).__repr__()


@pytest.mark.hftest1
@pytest.mark.usefixtures("new_clean_dir")
def test_load_model_with_differing_cloudpickle_version_at_micro_granularity_logs_warning(
        model_path,
):
    class TestModel(azureml.evaluate.mlflow.aml.AzureMLModel):
        def predict(self, context, model_input):
            return model_input

    azureml_mlflow.aml.save_model(path=model_path, aml_model=TestModel())
    saver_cloudpickle_version = "0.5.8"
    model_config_path = os.path.join(model_path, "MLmodel")
    model_config = Model.load(model_config_path)
    model_config.flavors[azureml_mlflow.aml.FLAVOR_NAME][
        azureml_mlflow.aml.model.CONFIG_KEY_CLOUDPICKLE_VERSION
    ] = saver_cloudpickle_version
    model_config.save(model_config_path)

    log_messages = []

    def custom_warn(message_text, *args, **kwargs):
        log_messages.append(message_text % args % kwargs)

    loader_cloudpickle_version = "0.5.7"
    with mock.patch("azureml.evaluate.mlflow.aml._logger.warning") as warn_mock, mock.patch(
            "cloudpickle.__version__"
    ) as cloudpickle_version_mock:
        cloudpickle_version_mock.__str__ = lambda *args, **kwargs: loader_cloudpickle_version
        warn_mock.side_effect = custom_warn
        azureml_mlflow.aml.load_model(model_uri=model_path, model_type="classifier")

    assert any(
        "differs from the version of CloudPickle that is currently running" in log_message
        and saver_cloudpickle_version in log_message
        and loader_cloudpickle_version in log_message
        for log_message in log_messages
    )
    delete_directory(model_path)


@pytest.mark.hftest1
@pytest.mark.usefixtures("new_clean_dir")
def test_load_model_with_missing_cloudpickle_version_logs_warning(model_path):
    class TestModel(azureml.evaluate.mlflow.aml.AzureMLModel):
        def predict(self, context, model_input):
            return model_input

    azureml_mlflow.aml.save_model(path=model_path, aml_model=TestModel())
    model_config_path = os.path.join(model_path, "MLmodel")
    model_config = Model.load(model_config_path)
    del model_config.flavors[azureml_mlflow.aml.FLAVOR_NAME][
        azureml_mlflow.aml.model.CONFIG_KEY_CLOUDPICKLE_VERSION
    ]
    model_config.save(model_config_path)

    log_messages = []

    def custom_warn(message_text, *args, **kwargs):
        log_messages.append(message_text % args % kwargs)

    with mock.patch("azureml.evaluate.mlflow.aml._logger.warning") as warn_mock:
        warn_mock.side_effect = custom_warn
        azureml_mlflow.aml.load_model(model_uri=model_path, model_type="classifier")

    assert any(
        (
            "The version of CloudPickle used to save the model could not be found"
            " in the MLmodel configuration"
        )
        in log_message
        for log_message in log_messages
    )
    delete_directory(model_path)


# def test_save_and_load_model_with_special_chars(
#     sklearn_knn_model, main_scoped_model_class, iris_data, tmpdir
# ):
#     sklearn_model_path = os.path.join(str(tmpdir), "sklearn_  model")
#     azureml_mlflow.sklearn.save_model(sk_model=sklearn_knn_model, path=sklearn_model_path)
#
#     def test_predict(sk_model, model_input):
#         return sk_model.predict(model_input) * 2
#
#     # Intentionally create a path that has non-url-compatible characters
#     pyfunc_model_path = os.path.join(str(tmpdir), "pyfunc_ :% model")
#
#     azureml_mlflow.aml.save_model(
#         path=pyfunc_model_path,
#         artifacts={"sk_model": sklearn_model_path},
#         conda_env=_conda_env(),
#         aml_model=main_scoped_model_class(test_predict),
#     )
#
#     loaded_pyfunc_model = azureml_mlflow.aml.load_model(model_uri=pyfunc_model_path, model_type="classifier")
#     np.testing.assert_array_equal(
#         loaded_pyfunc_model.predict(iris_data[0]),
#         test_predict(sk_model=sklearn_knn_model, model_input=iris_data[0]),
#     )


class TestModel:
    @staticmethod
    def predict(pdf):
        return pdf


@pytest.mark.hftest1
@pytest.mark.usefixtures("new_clean_dir")
def test_column_schema_enforcement():
    m = Model()
    input_schema = Schema(
        [
            ColSpec("integer", "a"),
            ColSpec("long", "b"),
            ColSpec("float", "c"),
            ColSpec("double", "d"),
            ColSpec("boolean", "e"),
            ColSpec("string", "g"),
            ColSpec("binary", "f"),
            ColSpec("datetime", "h"),
        ]
    )
    m.signature = ModelSignature(inputs=input_schema)
    pyfunc_model = AMLGenericModel(model_meta=m, model_impl=TestModel())
    pdf = pd.DataFrame(
        data=[[1, 2, 3, 4, True, "x", bytes([1]), "2021-01-01 00:00:00.1234567"]],
        columns=["b", "d", "a", "c", "e", "g", "f", "h"],
        dtype=object,
    )
    pdf["a"] = pdf["a"].astype(np.int32)
    pdf["b"] = pdf["b"].astype(np.int64)
    pdf["c"] = pdf["c"].astype(np.float32)
    pdf["d"] = pdf["d"].astype(np.float64)
    pdf["h"] = pdf["h"].astype(np.datetime64)
    # test that missing column raises
    match_missing_inputs = "Model is missing inputs"
    with pytest.raises(MlflowException, match=match_missing_inputs):
        res = pyfunc_model.predict(pdf[["b", "d", "a", "e", "g", "f", "h"]])

    # test that extra column is ignored
    pdf["x"] = 1

    # test that columns are reordered, extra column is ignored
    res = pyfunc_model.predict(pdf)
    assert all((res == pdf[input_schema.input_names()]).all())

    expected_types = dict(zip(input_schema.input_names(), input_schema.pandas_types()))
    # MLflow datetime type in input_schema does not encode precision, so add it for assertions
    expected_types["h"] = np.dtype("datetime64[ns]")
    # object cannot be converted to pandas Strings at the moment
    expected_types["f"] = object
    expected_types["g"] = object
    actual_types = res.dtypes.to_dict()
    assert expected_types == actual_types

    # Test conversions
    # 1. long -> integer raises
    pdf["a"] = pdf["a"].astype(np.int64)
    match_incompatible_inputs = "Incompatible input types"
    with pytest.raises(MlflowException, match=match_incompatible_inputs):
        pyfunc_model.predict(pdf)
    pdf["a"] = pdf["a"].astype(np.int32)
    # 2. integer -> long works
    pdf["b"] = pdf["b"].astype(np.int32)
    res = pyfunc_model.predict(pdf)
    assert all((res == pdf[input_schema.input_names()]).all())
    assert res.dtypes.to_dict() == expected_types
    pdf["b"] = pdf["b"].astype(np.int64)

    # 3. unsigned int -> long works
    pdf["b"] = pdf["b"].astype(np.uint32)
    res = pyfunc_model.predict(pdf)
    assert all((res == pdf[input_schema.input_names()]).all())
    assert res.dtypes.to_dict() == expected_types
    pdf["b"] = pdf["b"].astype(np.int64)

    # 4. unsigned int -> int raises
    pdf["a"] = pdf["a"].astype(np.uint32)
    with pytest.raises(MlflowException, match=match_incompatible_inputs):
        pyfunc_model.predict(pdf)
    pdf["a"] = pdf["a"].astype(np.int32)

    # 5. double -> float raises
    pdf["c"] = pdf["c"].astype(np.float64)
    with pytest.raises(MlflowException, match=match_incompatible_inputs):
        pyfunc_model.predict(pdf)
    pdf["c"] = pdf["c"].astype(np.float32)

    # 6. float -> double works, double -> float does not
    pdf["d"] = pdf["d"].astype(np.float32)
    res = pyfunc_model.predict(pdf)
    assert res.dtypes.to_dict() == expected_types
    pdf["d"] = pdf["d"].astype(np.float64)
    pdf["c"] = pdf["c"].astype(np.float64)
    with pytest.raises(MlflowException, match=match_incompatible_inputs):
        pyfunc_model.predict(pdf)
    pdf["c"] = pdf["c"].astype(np.float32)

    # 7. int -> float raises
    pdf["c"] = pdf["c"].astype(np.int32)
    with pytest.raises(MlflowException, match=match_incompatible_inputs):
        pyfunc_model.predict(pdf)
    pdf["c"] = pdf["c"].astype(np.float32)

    # 8. int -> double works
    pdf["d"] = pdf["d"].astype(np.int32)
    pyfunc_model.predict(pdf)
    assert all((res == pdf[input_schema.input_names()]).all())
    assert res.dtypes.to_dict() == expected_types

    # 9. long -> double raises
    pdf["d"] = pdf["d"].astype(np.int64)
    with pytest.raises(MlflowException, match=match_incompatible_inputs):
        pyfunc_model.predict(pdf)
    pdf["d"] = pdf["d"].astype(np.float64)

    # 10. any float -> any int raises
    pdf["a"] = pdf["a"].astype(np.float32)
    with pytest.raises(MlflowException, match=match_incompatible_inputs):
        pyfunc_model.predict(pdf)
    # 10. any float -> any int raises
    pdf["a"] = pdf["a"].astype(np.float64)
    with pytest.raises(MlflowException, match=match_incompatible_inputs):
        pyfunc_model.predict(pdf)
    pdf["a"] = pdf["a"].astype(np.int32)
    pdf["b"] = pdf["b"].astype(np.float64)
    with pytest.raises(MlflowException, match=match_incompatible_inputs):
        pyfunc_model.predict(pdf)
    pdf["b"] = pdf["b"].astype(np.int64)

    pdf["b"] = pdf["b"].astype(np.float64)
    with pytest.raises(MlflowException, match=match_incompatible_inputs):
        pyfunc_model.predict(pdf)
    pdf["b"] = pdf["b"].astype(np.int64)

    # 11. objects work
    pdf["b"] = pdf["b"].astype(object)
    pdf["d"] = pdf["d"].astype(object)
    pdf["e"] = pdf["e"].astype(object)
    pdf["f"] = pdf["f"].astype(object)
    pdf["g"] = pdf["g"].astype(object)
    res = pyfunc_model.predict(pdf)
    assert res.dtypes.to_dict() == expected_types

    # 12. datetime64[D] (date only) -> datetime64[x] works
    pdf["h"] = pdf["h"].astype("datetime64[D]")
    res = pyfunc_model.predict(pdf)
    assert res.dtypes.to_dict() == expected_types
    pdf["h"] = pdf["h"].astype("datetime64[s]")

    # 13. np.ndarrays can be converted to dataframe but have no columns
    with pytest.raises(MlflowException, match=match_missing_inputs):
        pyfunc_model.predict(pdf.values)

    # 14. dictionaries of str -> list/nparray work
    arr = np.array([1, 2, 3])
    d = {
        "a": arr.astype("int32"),
        "b": arr.astype("int64"),
        "c": arr.astype("float32"),
        "d": arr.astype("float64"),
        "e": [True, False, True],
        "g": ["a", "b", "c"],
        "f": [bytes(0), bytes(1), bytes(1)],
        "h": np.array(["2020-01-01", "2020-02-02", "2020-03-03"], dtype=np.datetime64),
    }
    res = pyfunc_model.predict(d)
    assert res.dtypes.to_dict() == expected_types

    # 15. dictionaries of str -> list[list] fail
    d = {
        "a": [arr.astype("int32")],
        "b": [arr.astype("int64")],
        "c": [arr.astype("float32")],
        "d": [arr.astype("float64")],
        "e": [[True, False, True]],
        "g": [["a", "b", "c"]],
        "f": [[bytes(0), bytes(1), bytes(1)]],
        "h": [np.array(["2020-01-01", "2020-02-02", "2020-03-03"], dtype=np.datetime64)],
    }
    with pytest.raises(MlflowException, match=match_incompatible_inputs):
        pyfunc_model.predict(d)

    # 16. conversion to dataframe fails
    d = {
        "a": [1],
        "b": [1, 2],
        "c": [1, 2, 3],
    }
    with pytest.raises(
            MlflowException,
            match="This model contains a column-based signature, which suggests a DataFrame input.",
    ):
        pyfunc_model.predict(d)

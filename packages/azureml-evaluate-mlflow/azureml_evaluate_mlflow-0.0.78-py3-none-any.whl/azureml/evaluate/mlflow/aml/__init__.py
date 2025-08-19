# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import importlib
import inspect
import os
import mlflow.pyfunc
import yaml
from copy import deepcopy
import logging
import azureml.evaluate.mlflow as aml_mlflow
from mlflow import pyfunc
from mlflow.pyfunc import FLAVOR_NAME as PYFUNC_FLAVOR_NAME
from mlflow.models import Model, ModelSignature, ModelInputExample
from mlflow.models.model import MLMODEL_FILE_NAME
from mlflow.models.utils import _save_example

from azureml.evaluate.mlflow.exceptions import AzureMLMLFlowUserException, AzureMLMLFlowTypeException
from azureml.evaluate.mlflow.constants import ErrorStrings
import azureml.evaluate.mlflow.aml
from azureml.evaluate.mlflow.aml.model import (  # pylint: disable=unused-import
    AzureMLModel,
    AzureMLClassifierModel,
    AzureMLGenericModel,
    AzureMLForecastModel,
    AzureMLInput,
    get_default_conda_env,
)
from azureml.evaluate.mlflow import AZUREML_FLAVORS_SUPPORTED
from azureml.evaluate.mlflow.aml.utils import _enforce_schema
from azureml.evaluate.mlflow.aml.model import get_default_pip_requirements
from mlflow.utils.requirements_utils import warn_dependency_requirement_mismatches
from mlflow.tracking.artifact_utils import _download_artifact_from_uri
from mlflow.utils import PYTHON_VERSION, get_major_minor_py_version
from mlflow.utils.annotations import deprecated
from mlflow.utils.file_utils import _copy_file_or_tree, write_to
from mlflow.utils.model_utils import (
    _validate_and_copy_code_paths,
    _add_code_from_conf_to_system_path,
    _get_flavor_configuration_from_uri,
    _validate_and_prepare_target_save_path,
)
from mlflow.utils.uri import append_to_uri_path
from mlflow.utils.environment import (
    _validate_env_arguments,
    _process_pip_requirements,
    _process_conda_env,
    _CONDA_ENV_FILE_NAME,
    _REQUIREMENTS_FILE_NAME,
    _CONSTRAINTS_FILE_NAME,
    _PYTHON_ENV_FILE_NAME,
    _PythonEnv,
)
from mlflow.utils.docstring_utils import format_docstring, LOG_MODEL_PARAM_DOCS
from mlflow.tracking._model_registry import DEFAULT_AWAIT_MAX_SLEEP_SECONDS
from mlflow.protos.databricks_pb2 import (
    INVALID_PARAMETER_VALUE,
    RESOURCE_DOES_NOT_EXIST,
)

FLAVOR_NAME = "aml"
MAIN = "loader_module"
CODE = "code"
DATA = "data"
ENV = "env"
PY_VERSION = "python_version"

LOADER_MODULE_PREFIX = "azureml.evaluate.mlflow._loader_modules."

_logger = logging.getLogger(__name__)


def add_to_model(model, loader_module, data=None, code=None, env=None, **kwargs):
    """
    Add a ``pyfunc`` spec to the model configuration.

    Defines ``pyfunc`` configuration schema. Caller can use this to create a valid ``pyfunc`` model
    flavor out of an existing directory structure. For example, other model flavors can use this to
    specify how to use their output as a ``pyfunc``.

    NOTE:

        All paths are relative to the exported model root directory.

    :param model: Existing model.
    :param loader_module: The module to be used to load the model.
    :param data: Path to the model data.
    :param code: Path to the code dependencies.
    :param env: Conda environment.
    :param req: pip requirements file.
    :param kwargs: Additional key-value pairs to include in the ``pyfunc`` flavor specification.
                   Values must be YAML-serializable.
    :return: Updated model configuration.
    """
    params = deepcopy(kwargs)
    params[MAIN] = loader_module
    params[PY_VERSION] = PYTHON_VERSION
    if code:
        params[CODE] = code
    if data:
        params[DATA] = data
    if env:
        params[ENV] = env

    return model.add_flavor(FLAVOR_NAME, **params)


class AMLModel:

    def __init__(self, model_meta, model_impl) -> None:
        if not model_meta:
            raise AzureMLMLFlowUserException(ErrorStrings.MissingMetadata)
        self._model_meta = model_meta
        self._model_impl = model_impl

    @property
    def metadata(self):
        """Model metadata."""
        if self._model_meta is None:
            raise AzureMLMLFlowUserException(ErrorStrings.MissingMetadata)
        return self._model_meta

    def __repr__(self):
        info = {}
        if self._model_meta is not None:
            if hasattr(self._model_meta, "run_id") and self._model_meta.run_id is not None:
                info["run_id"] = self._model_meta.run_id
            if (
                    hasattr(self._model_meta, "artifact_path") and
                    self._model_meta.artifact_path is not None
            ):
                info["artifact_path"] = self._model_meta.artifact_path
            info["flavor"] = self._model_meta.flavors[FLAVOR_NAME]["loader_module"]
        return yaml.safe_dump({"mlflow.aml.loaded_model": info}, default_flow_style=False)

    # This is  a hack for enabling kwargs in aml. We need to get  better way of
    # passing the kwargs while runtime
    def _support_kwargs_for_predict(self):
        from azureml.evaluate.mlflow.hftransformers import ALL_FLAVOR_NAMES
        return any([i in self._model_meta.flavors for i in ALL_FLAVOR_NAMES])


class AMLGenericModel(AMLModel):
    def __init__(self, model_meta, model_impl):
        super().__init__(model_meta, model_impl)
        if not hasattr(self._model_impl, "predict"):
            raise AzureMLMLFlowUserException(ErrorStrings.MissingMethod.format(method="predict"))

    def predict(self, data: AzureMLInput, **kwargs):
        input_schema = self.metadata.get_input_schema()
        if input_schema is not None:
            data = _enforce_schema(data, input_schema)
        if self._support_kwargs_for_predict():
            return self._model_impl.predict(data, **kwargs)
        if inspect.signature(self._model_impl.predict).parameters.get("params"):
            params = kwargs.get("params", None)
            return self._model_impl.predict(data, params=params)
        else:
            return self._model_impl.predict(data)


class AMLClassifierModel(AMLGenericModel):
    def __init__(self, model_meta, model_impl):
        super().__init__(model_meta, model_impl)
        if not hasattr(self._model_impl, "predict"):
            raise AzureMLMLFlowUserException(ErrorStrings.MissingMethod.format(method="predict"))
        if not hasattr(self._model_impl, "predict_proba"):
            raise AzureMLMLFlowUserException(ErrorStrings.MissingMethod.format(method="predict_proba"))

    def predict_proba(self, data: AzureMLInput, **kwargs):
        input_schema = self.metadata.get_input_schema()
        if input_schema is not None:
            data = _enforce_schema(data, input_schema)
        if self._support_kwargs_for_predict():
            return self._model_impl.predict_proba(data, **kwargs)
        return self._model_impl.predict_proba(data)


class AMLForecastModel(AMLGenericModel):
    def __init__(self, model_meta, model_impl):
        super().__init__(model_meta, model_impl)
        self._model_impl = model_impl
        if not hasattr(self._model_impl, "forecast"):
            raise AzureMLMLFlowUserException(ErrorStrings.MissingMethod.format(method="forecast"))

    def forecast(self, data: AzureMLInput):
        input_schema = self.metadata.get_input_schema()
        if input_schema is not None:
            data = _enforce_schema(data, input_schema)
        return self._model_impl.forecast(data, ignore_data_errors=True)

    def rolling_forecast(self, data_x: AzureMLInput, data_y: AzureMLInput, step: int = 1):
        if not hasattr(self._model_impl, "rolling_forecast"):
            return self.forecast(data_x)
        input_schema = self.metadata.get_input_schema()
        if input_schema is not None:
            data_x = _enforce_schema(data_x, input_schema)
            data_y = _enforce_schema(data_y, input_schema)
        return self._model_impl.rolling_forecast(data_x, data_y, step=step, ignore_data_errors=True)


def _get_model(model_type, model_meta, model_impl):
    is_model_impl_classifier = hasattr(model_impl, "predict_proba") and hasattr(model_impl, "predict")
    is_aml_model_classifier = hasattr(model_impl, "aml_model") and all(hasattr(model_impl.aml_model, attr)
                                                                       for attr in ["predict", "predict_proba"])
    is_forecaster = (
        hasattr(model_impl, "forecast") and
        hasattr(model_impl, "rolling_forecast") and
        hasattr(model_impl, "forecast_quantiles"))
    # Todo: Should AMLCLassifierModel be returned if model_type=="classifier"
    if model_type in ["classifier", "multiclass", "text-classifier"] and not (is_model_impl_classifier or
                                                                              is_aml_model_classifier):
        _logger.warning("The model provided does not contains predict_proba method. This is required in order to "
                        "use evaluate functionality")
    if is_model_impl_classifier or is_aml_model_classifier:
        return AMLClassifierModel(model_meta, model_impl)
    elif is_forecaster:
        return AMLForecastModel(model_meta, model_impl)
    return AMLGenericModel(model_meta, model_impl)


def load_model(
        model_uri: str, model_type: str = "", suppress_warnings: bool = False, dst_path: str = None, **kwargs
) -> AMLModel:
    """
    Load a model stored in AzureML format.

    :param model_uri: The location, in URI format, of the MLflow model. For example:

                      - ``/Users/me/path/to/local/model``
                      - ``relative/path/to/local/model``
                      - ``s3://my_bucket/path/to/model``
                      - ``runs:/<mlflow_run_id>/run-relative/path/to/model``
                      - ``models:/<model_name>/<model_version>``
                      - ``models:/<model_name>/<stage>``
                      - ``mlflow-artifacts:/path/to/model``

                      For more information about supported URI schemes, see
                      `Referencing Artifacts <https://www.mlflow.org/docs/latest/concepts.html#
                      artifact-locations>`_.
    :param suppress_warnings: If ``True``, non-fatal warning messages associated with the model
                              loading process will be suppressed. If ``False``, these warning
                              messages will be emitted.
    :param dst_path: The local filesystem path to which to download the model artifact.
                     This directory must already exist. If unspecified, a local output
                     path will be created.
    """
    local_path = _download_artifact_from_uri(artifact_uri=model_uri, output_path=dst_path)

    if not suppress_warnings:
        warn_dependency_requirement_mismatches(local_path)  # Can this be common for pyfunc and azureml?

    model_meta = Model.load(os.path.join(local_path, MLMODEL_FILE_NAME))

    conf = model_meta.flavors.get(FLAVOR_NAME)
    pyfunc_model_impl = None
    if conf is None:
        conf = model_meta.flavors.get(pyfunc.FLAVOR_NAME)
        _logger.warn(f"{FLAVOR_NAME} not found in logged model. Trying {PYFUNC_FLAVOR_NAME} instead.")
        if conf is not None:
            try:
                loader_module = conf[MAIN]
                if loader_module.startswith("mlflow"):
                    main_flavor = loader_module.split(".")[1]
                    assert (main_flavor in AZUREML_FLAVORS_SUPPORTED)
                    conf[MAIN] = LOADER_MODULE_PREFIX + main_flavor
                    if mlflow.pyfunc.FLAVOR_NAME in model_meta.flavors and FLAVOR_NAME not in model_meta.flavors:
                        model_meta.flavors[FLAVOR_NAME] = model_meta.flavors[mlflow.pyfunc.FLAVOR_NAME]
                elif loader_module.startswith("azureml.evaluate.mlflow."):
                    main_flavor = loader_module.split(".")[3]
                    assert (main_flavor in AZUREML_FLAVORS_SUPPORTED)
                    conf[MAIN] = LOADER_MODULE_PREFIX + main_flavor
                    if mlflow.pyfunc.FLAVOR_NAME in model_meta.flavors and FLAVOR_NAME not in model_meta.flavors:
                        model_meta.flavors[FLAVOR_NAME] = model_meta.flavors[mlflow.pyfunc.FLAVOR_NAME]
            except Exception:
                pass
        else:
            raise AzureMLMLFlowUserException(
                'Model does not have the "{flavor_name}" flavor'.format(flavor_name=FLAVOR_NAME),
                error_code=RESOURCE_DOES_NOT_EXIST,
            )

    model_py_version = conf.get(PY_VERSION)
    if not suppress_warnings:
        _warn_potentially_incompatible_py_version_if_necessary(model_py_version=model_py_version)

    _add_code_from_conf_to_system_path(local_path, conf, code_key=CODE)
    data_path = os.path.join(local_path, conf[DATA]) if (DATA in conf) else local_path

    def _support_kwargs_for_load():
        from azureml.evaluate.mlflow.hftransformers import ALL_FLAVOR_NAMES
        return any([i in model_meta.flavors for i in ALL_FLAVOR_NAMES])

    try:
        if _support_kwargs_for_load():
            _logger.info(f"Calling _load_azureml with kwargs {kwargs}")
            model_impl = importlib.import_module(conf[MAIN])._load_azureml(data_path, **kwargs)
        else:
            model_impl = importlib.import_module(conf[MAIN])._load_azureml(data_path)
    except Exception as e:
        try:
            _logger.info("Unable to load using aml flavor. Trying out pyfunc. Exception: {}".format(str(e)))
            if _support_kwargs_for_load():
                _logger.info(f"Calling _load_pyfunc with kwargs {kwargs}")
                model_impl = importlib.import_module(conf[MAIN])._load_pyfunc(data_path, **kwargs)
            else:
                model_impl = importlib.import_module(conf[MAIN])._load_pyfunc(data_path)
        except Exception as e1:
            _logger.error("Error while loading the models.")
            raise e1
    return _get_model(model_type=model_type, model_meta=model_meta, model_impl=model_impl)


def _download_model_conda_env(model_uri):
    conda_yml_file_name = _get_flavor_configuration_from_uri(model_uri, FLAVOR_NAME)[ENV]
    return _download_artifact_from_uri(append_to_uri_path(model_uri, conda_yml_file_name))


@deprecated("mlflow.aml.load_model", 1.0)
def load_azureml(model_uri, suppress_warnings=False):
    return load_model(model_uri, suppress_warnings)


def _warn_potentially_incompatible_py_version_if_necessary(model_py_version=None):
    if model_py_version is None:
        _logger.warning(
            "The specified model does not have a specified Python version. It may be"
            " incompatible with the version of Python that is currently running: Python %s",
            PYTHON_VERSION,
        )
    elif get_major_minor_py_version(model_py_version) != get_major_minor_py_version(PYTHON_VERSION):
        _logger.warning(
            "The version of Python that the model was saved in, `Python %s`, differs"
            " from the version of Python that is currently running, `Python %s`,"
            " and may be incompatible",
            model_py_version,
            PYTHON_VERSION,
        )


_MLFLOW_SERVER_OUTPUT_TAIL_LINES_TO_KEEP = 200


@format_docstring(LOG_MODEL_PARAM_DOCS.format(package_name="scikit-learn"))
def save_model(
        path,
        loader_module=None,
        data_path=None,
        code_path=None,
        conda_env=None,
        mlflow_model=None,
        aml_model=None,
        artifacts=None,
        signature: ModelSignature = None,
        input_example: ModelInputExample = None,
        pip_requirements=None,
        extra_pip_requirements=None,
        **kwargs,
):
    """
    save_model(path, loader_module=None, data_path=None, code_path=None, conda_env=None,\
               mlflow_model=Model(), aml_model=None, artifacts=None)

    Save an AzureML model with custom inference logic and optional data dependencies to a path on the
    local filesystem.

    :param path: The path to which to save the Python model.
    :param loader_module: The name of the Python module that is used to load the model
                          from ``data_path``. This module must define a method with the prototype
                          ``_load_azureml(data_path)``. If not ``None``, this module and its
                          dependencies must be included in one of the following locations:

                          - The MLflow library.
                          - Package(s) listed in the model's Conda environment, specified by
                            the ``conda_env`` parameter.
                          - One or more of the files specified by the ``code_path`` parameter.

    :param data_path: Path to a file or directory containing model data.
    :param code_path: A list of local filesystem paths to Python file dependencies (or directories
                      containing file dependencies). These files are *prepended* to the system
                      path before the model is loaded.
    :param conda_env: {{ conda_env }}
    :param mlflow_model: :py:mod:`mlflow.models.Model` configuration to which to add the
                         **python_function** flavor.
    :param aml_model: An instance of a subclass of :class:`~AzureMLModel`. This class is
                         serialized using the CloudPickle library. Any dependencies of the class
                         should be included in one of the following locations:

                            - The MLflow library.
                            - Package(s) listed in the model's Conda environment, specified by
                              the ``conda_env`` parameter.
                            - One or more of the files specified by the ``code_path`` parameter.

                         Note: If the class is imported from another module, as opposed to being
                         defined in the ``__main__`` scope, the defining module should also be
                         included in one of the listed locations.
    :param artifacts: A dictionary containing ``<name, artifact_uri>`` entries. Remote artifact URIs
                      are resolved to absolute filesystem paths, producing a dictionary of
                      ``<name, absolute_path>`` entries. ``aml_model`` can reference these
                      resolved entries as the ``artifacts`` property of the ``context`` parameter
                      in :func:`AzureMLModel.load_context() <mlflow.aml.AzureMLModel.load_context>`
                      and :func:`AzureMLModel.predict() <mlflow.aml.AzureMLModel.predict>`.
                      For example, consider the following ``artifacts`` dictionary::

                        {
                            "my_file": "s3://my-bucket/path/to/my/file"
                        }

                      In this case, the ``"my_file"`` artifact is downloaded from S3. The
                      ``aml_model`` can then refer to ``"my_file"`` as an absolute filesystem
                      path via ``context.artifacts["my_file"]``.

                      If ``None``, no artifacts are added to the model.

    :param signature: :py:class:`ModelSignature <mlflow.models.ModelSignature>`
                      describes model input and output :py:class:`Schema <mlflow.types.Schema>`.
                      The model signature can be :py:func:`inferred <mlflow.models.infer_signature>`
                      from datasets with valid model input (e.g. the training dataset with target
                      column omitted) and valid model output (e.g. model predictions generated on
                      the training dataset), for example:

                      .. code-block:: python

                        from mlflow.models.signature import infer_signature
                        train = df.drop_column("target_label")
                        predictions = ... # compute model predictions
                        signature = infer_signature(train, predictions)
    :param input_example: Input example provides one or several instances of valid
                          model input. The example can be used as a hint of what data to feed the
                          model. The given example can be a Pandas DataFrame where the given
                          example will be serialized to json using the Pandas split-oriented
                          format, or a numpy array where the example will be serialized to json
                          by converting it to a list. Bytes are base64-encoded.
    :param pip_requirements: {{ pip_requirements }}
    :param extra_pip_requirements: {{ extra_pip_requirements }}
    """
    _validate_env_arguments(conda_env, pip_requirements, extra_pip_requirements)

    mlflow_model = kwargs.pop("model", mlflow_model)
    if len(kwargs) > 0:
        raise AzureMLMLFlowTypeException("save_model() got unexpected keyword arguments: {}".format(kwargs))
    if code_path is not None:
        if not isinstance(code_path, list):
            raise AzureMLMLFlowTypeException("Argument code_path should be a list, not {}".format(type(code_path)))

    first_argument_set = {
        "loader_module": loader_module,
        "data_path": data_path,
    }
    second_argument_set = {
        "artifacts": artifacts,
        "aml_model": aml_model,
    }
    first_argument_set_specified = any(item is not None for item in first_argument_set.values())
    second_argument_set_specified = any(item is not None for item in second_argument_set.values())
    if first_argument_set_specified and second_argument_set_specified:
        raise AzureMLMLFlowUserException(
            message=(
                "The following sets of parameters cannot be specified together: {first_set_keys}"
                " and {second_set_keys}. All parameters in one set must be `None`. Instead, found"
                " the following values: {first_set_entries} and {second_set_entries}.".format(
                    first_set_keys=first_argument_set.keys(),
                    second_set_keys=second_argument_set.keys(),
                    first_set_entries=first_argument_set,
                    second_set_entries=second_argument_set,
                )
            ),
            error_code=INVALID_PARAMETER_VALUE,
        )
    elif (loader_module is None) and (aml_model is None):
        msg = (
            "Either `loader_module` or `aml_model` must be specified. A `loader_module` "
            "should be a python module. A `aml_model` should be a subclass of AzureMLModel."
        )
        raise AzureMLMLFlowUserException(message=msg, error_code=INVALID_PARAMETER_VALUE)

    _validate_and_prepare_target_save_path(path)
    if mlflow_model is None:
        mlflow_model = Model()
    if signature is not None:
        mlflow_model.signature = signature
    if input_example is not None:
        _save_example(mlflow_model, input_example, path)

    if first_argument_set_specified:
        return _save_model_with_loader_module_and_data_path(
            path=path,
            loader_module=loader_module,
            data_path=data_path,
            code_paths=code_path,
            conda_env=conda_env,
            mlflow_model=mlflow_model,
            pip_requirements=pip_requirements,
            extra_pip_requirements=extra_pip_requirements,
        )
    elif second_argument_set_specified:
        return aml_mlflow.aml.model._save_model_with_class_artifacts_params(
            path=path,
            aml_model=aml_model,
            artifacts=artifacts,
            conda_env=conda_env,
            code_paths=code_path,
            mlflow_model=mlflow_model,
            pip_requirements=pip_requirements,
            extra_pip_requirements=extra_pip_requirements,
        )


@format_docstring(LOG_MODEL_PARAM_DOCS.format(package_name="scikit-learn"))
def log_model(
        artifact_path,
        loader_module=None,
        data_path=None,
        code_path=None,
        conda_env=None,
        aml_model=None,
        artifacts=None,
        registered_model_name=None,
        signature: ModelSignature = None,
        input_example: ModelInputExample = None,
        await_registration_for=DEFAULT_AWAIT_MAX_SLEEP_SECONDS,
        pip_requirements=None,
        extra_pip_requirements=None,
):
    """
    Log an Azureml model with custom inference logic and optional data dependencies as an MLflow
    artifact for the current run.

    :param artifact_path: The run-relative artifact path to which to log the Python model.
    :param loader_module: The name of the Python module that is used to load the model
                          from ``data_path``. This module must define a method with the prototype
                          ``_load_azureml(data_path)``. If not ``None``, this module and its
                          dependencies must be included in one of the following locations:

                          - The MLflow library.
                          - Package(s) listed in the model's Conda environment, specified by
                            the ``conda_env`` parameter.
                          - One or more of the files specified by the ``code_path`` parameter.

    :param data_path: Path to a file or directory containing model data.
    :param code_path: A list of local filesystem paths to Python file dependencies (or directories
                      containing file dependencies). These files are *prepended* to the system
                      path before the model is loaded.
    :param conda_env: {{ conda_env }}
    :param aml_model: An instance of a subclass of :class:`~AzureMLModel`. This class is
                         serialized using the CloudPickle library. Any dependencies of the class
                         should be included in one of the following locations:

                            - The MLflow library.
                            - Package(s) listed in the model's Conda environment, specified by
                              the ``conda_env`` parameter.
                            - One or more of the files specified by the ``code_path`` parameter.

                         Note: If the class is imported from another module, as opposed to being
                         defined in the ``__main__`` scope, the defining module should also be
                         included in one of the listed locations.
    :param artifacts: A dictionary containing ``<name, artifact_uri>`` entries. Remote artifact URIs
                      are resolved to absolute filesystem paths, producing a dictionary of
                      ``<name, absolute_path>`` entries. ``aml_model`` can reference these
                      resolved entries as the ``artifacts`` property of the ``context`` parameter
                      in :func:`AzureMLModel.load_context() <mlflow.aml.AzureMLModel.load_context>`
                      and :func:`AzureMLModel.predict() <mlflow.aml.AzureMLModel.predict>`.
                      For example, consider the following ``artifacts`` dictionary::

                        {
                            "my_file": "s3://my-bucket/path/to/my/file"
                        }

                      In this case, the ``"my_file"`` artifact is downloaded from S3. The
                      ``aml_model`` can then refer to ``"my_file"`` as an absolute filesystem
                      path via ``context.artifacts["my_file"]``.

                      If ``None``, no artifacts are added to the model.
    :param registered_model_name: This argument may change or be removed in a
                                  future release without warning. If given, create a model
                                  version under ``registered_model_name``, also creating a
                                  registered model if one with the given name does not exist.

    :param signature: :py:class:`ModelSignature <mlflow.models.ModelSignature>`
                      describes model input and output :py:class:`Schema <mlflow.types.Schema>`.
                      The model signature can be :py:func:`inferred <mlflow.models.infer_signature>`
                      from datasets with valid model input (e.g. the training dataset with target
                      column omitted) and valid model output (e.g. model predictions generated on
                      the training dataset), for example:

                      .. code-block:: python

                        from mlflow.models.signature import infer_signature
                        train = df.drop_column("target_label")
                        predictions = ... # compute model predictions
                        signature = infer_signature(train, predictions)
    :param input_example: Input example provides one or several instances of valid
                          model input. The example can be used as a hint of what data to feed the
                          model. The given example can be a Pandas DataFrame where the given
                          example will be serialized to json using the Pandas split-oriented
                          format, or a numpy array where the example will be serialized to json
                          by converting it to a list. Bytes are base64-encoded.
    :param await_registration_for: Number of seconds to wait for the model version to finish
                            being created and is in ``READY`` status. By default, the function
                            waits for five minutes. Specify 0 or None to skip waiting.
    :param pip_requirements: {{ pip_requirements }}
    :param extra_pip_requirements: {{ extra_pip_requirements }}
    :return: A :py:class:`ModelInfo <mlflow.models.model.ModelInfo>` instance that contains the
             metadata of the logged model.
    """
    return Model.log(
        artifact_path=artifact_path,
        flavor=aml_mlflow.aml,
        loader_module=loader_module,
        data_path=data_path,
        code_path=code_path,
        aml_model=aml_model,
        artifacts=artifacts,
        conda_env=conda_env,
        registered_model_name=registered_model_name,
        signature=signature,
        input_example=input_example,
        await_registration_for=await_registration_for,
        pip_requirements=pip_requirements,
        extra_pip_requirements=extra_pip_requirements,
    )


def _save_model_with_loader_module_and_data_path(
        path,
        loader_module,
        data_path=None,
        code_paths=None,
        conda_env=None,
        mlflow_model=None,
        pip_requirements=None,
        extra_pip_requirements=None,
):
    """
    Export model as a generic AzureML model.
    :param path: The path to which to save the Python model.
    :param loader_module: The name of the Python module that is used to load the model
                          from ``data_path``. This module must define a method with the prototype
                          ``_load_azureml_model(data_path)``.
    :param data_path: Path to a file or directory containing model data.
    :param code_paths: A list of local filesystem paths to Python file dependencies (or directories
                      containing file dependencies). These files are *prepended* to the system
                      path before the model is loaded.
    :param conda_env: Either a dictionary representation of a Conda environment or the path to a
                      Conda environment yaml file. If provided, this decsribes the environment
                      this model should be run in.
    :return: Model configuration containing model info.
    """

    data = None

    if data_path is not None:
        model_file = _copy_file_or_tree(src=data_path, dst=path, dst_dir="data")
        data = model_file

    code_dir_subpath = _validate_and_copy_code_paths(code_paths, path)

    if mlflow_model is None:
        mlflow_model = Model()

    aml_mlflow.aml.add_to_model(
        mlflow_model,
        loader_module=loader_module,
        code=code_dir_subpath,
        data=data,
        env=_CONDA_ENV_FILE_NAME,
    )
    mlflow_model.save(os.path.join(path, MLMODEL_FILE_NAME))

    if conda_env is None:
        if pip_requirements is None:
            default_reqs = get_default_pip_requirements()
            # To ensure `_load_azureml_model` can successfully load the model during the dependency
            # inference, `mlflow_model.save` must be called beforehand to save an MLmodel file.
            inferred_reqs = aml_mlflow.models.infer_pip_requirements(
                path,
                FLAVOR_NAME,
                fallback=default_reqs,
            )
            default_reqs = sorted(set(inferred_reqs).union(default_reqs))
        else:
            default_reqs = None
        conda_env, pip_requirements, pip_constraints = _process_pip_requirements(
            default_reqs,
            pip_requirements,
            extra_pip_requirements,
        )
    else:
        conda_env, pip_requirements, pip_constraints = _process_conda_env(conda_env)

    with open(os.path.join(path, _CONDA_ENV_FILE_NAME), "w") as f:
        yaml.safe_dump(conda_env, stream=f, default_flow_style=False)

    # Save `constraints.txt` if necessary
    if pip_constraints:
        write_to(os.path.join(path, _CONSTRAINTS_FILE_NAME), "\n".join(pip_constraints))

    # Save `requirements.txt`
    write_to(os.path.join(path, _REQUIREMENTS_FILE_NAME), "\n".join(pip_requirements))

    _PythonEnv.current().to_yaml(os.path.join(path, _PYTHON_ENV_FILE_NAME))
    return mlflow_model


loader_template = """

import importlib
import os
import sys

def load_azureml_model():
    {update_path}return importlib.import_module('{main}')._load_azureml_model('{data_path}')

"""

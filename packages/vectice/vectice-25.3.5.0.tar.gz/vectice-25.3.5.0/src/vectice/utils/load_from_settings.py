from __future__ import annotations

import json
import logging
import os
from dataclasses import asdict, dataclass, field
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from pandas import DataFrame

    from vectice import Connection
    from vectice.models.representation.model_version_representation import ModelVersionRepresentation

_logger = logging.getLogger(__name__)


def load_from_settings(
    config_file_path: str, api_token: str | None = None, output_directory_for_attachment: str = "./"
) -> tuple[dict | None, ModelVersionRepresentation | None, DataFrame | None, DataFrame | None, Any | None]:
    """Loads configuration from a settings file, retrieves the train and test datasets,
    and handles downloading model attachments.

    Args:
        config_file_path (str): The file path to the configuration JSON file.
        api_token (str | None, optional): API token for authentication. Defaults to None.
        output_directory_for_attachment (str, optional): Directory path to store model version attachments. Defaults to './'.

    Returns:
        tuple: A tuple containing the following:
            - config_file_json (dict | None): The loaded configuration as a dictionary.
            - model_version (ModelVersionRepresentation | None): The model version object if available.
            - train_df (DataFrame | None): The training dataset as a DataFrame.
            - test_df (DataFrame | None): The testing dataset as a DataFrame.
            - predictor (Any | None): The model predictor/estimator object if available.

    Example:
        >>> config_json, model_version, train_df, test_df, predictor = load_from_settings(
        >>>     config_file_path='path/to/config.json',
        >>>     api_token='your_api_token',
        >>>     output_directory_for_attachment='/path/to/attachments'
        >>> )
    """
    config = Config.read_config_json(config_file_path, api_token)

    # Initialize outputs
    config_file_json = config.to_dict()
    # Get the train and test df from csvs
    train_df, test_df = config.get_train_test()

    model_version = config.get_model_version()
    if model_version:
        _logger.info(f"Downloading model version {model_version.id} attachments...")
        model_version.download_attachments(output_dir=output_directory_for_attachment)
        _logger.info(f"Model version {model_version.id} attachments download complete.")
    # Get the predictor/estimator after downloading
    predictor = config.get_model_estimator(output_directory_for_attachment)

    os.environ["VECTICE_CONFIG"] = json.dumps(config_file_json)
    return config_file_json, model_version, train_df, test_df, predictor


@dataclass
class Paths:
    train: str | None = field(default=None)
    test: str | None = field(default=None)

    def to_dict(self):
        return asdict(self)


@dataclass
class ValidationConfig:
    model: str | None = field(default=None)
    target: str | None = field(default=None)
    predictor: str | None = field(default=None)
    paths: Paths | None = field(default=None)

    def __post_init__(self):
        if isinstance(self.paths, dict):
            self.paths = Paths(**self.paths)

    def to_dict(self):
        return asdict(self)


@dataclass
class Config:
    api_token: str
    host: str
    phase: str
    validation_config: ValidationConfig
    connection: Connection | None = field(default=None)

    def __post_init__(self):
        from vectice import connect

        if isinstance(self.validation_config, dict):
            self.validation_config = ValidationConfig(**self.validation_config)

        # TODO suppress ?
        self.connection = connect(  # pyright: ignore[reportAttributeAccessIssue]
            api_token=self.api_token, host=self.host
        )

    def to_dict(self):
        val_config = asdict(self.validation_config)
        data = asdict(self)
        data["validation_config"] = val_config
        # remove connection for json serialization
        data.pop("connection")
        return data

    @staticmethod
    def read_config_json(path: str, api_token: str | None = None) -> Config:
        from vectice.connection import DEFAULT_HOST

        with open(path, "r") as file:
            data = json.load(file)
        if api_token:
            if data.get("api_token"):
                _logger.warning(
                    "The config file has an api token provided already. The api_token parameter will overwrite it."
                )
            data["api_token"] = api_token
        if data.get("host") is None:
            data["host"] = DEFAULT_HOST
        return Config(**data)

    def get_train_test(self) -> tuple:
        import pandas as pd

        train, test = None, None
        try:
            if self.validation_config.paths.train:  # pyright: ignore[reportOptionalMemberAccess]
                train = pd.read_csv(self.validation_config.paths.train)  # pyright: ignore[reportOptionalMemberAccess]
        except Exception as e:
            _logger.info(f"Validation train df failed to load. With the following error\n{e}")
        try:
            if self.validation_config.paths.test:  # pyright: ignore[reportOptionalMemberAccess]
                test = pd.read_csv(self.validation_config.paths.test)  # pyright: ignore[reportOptionalMemberAccess]
        except Exception as e:
            _logger.info(f"Validation test df failed to load. With the following error\n{e}")
        return train, test

    def get_model_estimator(self, directory: str | None = None) -> Any | None:
        import pickle

        # Loads the pre-trained model from the specified path in the configuration file
        pickle_path = self.validation_config.predictor
        if pickle_path is None:
            _logger.info(
                "Validation predictor is not set. Please set the predictor parameter to retrieve the predictor pickle."
            )
            return None
        try:
            full_path = directory + pickle_path if directory else pickle_path  # pyright: ignore[reportOperatorIssue]
            with open(full_path, "rb") as file:  # pyright: ignore[reportCallIssue, reportArgumentType]
                predictor = pickle.load(file)
                _logger.info(f"Model estimator {full_path} pickle loaded.")
        except FileNotFoundError:
            _logger.info("The model pickle was not found. Please check the path")
            return None
        return predictor

    def get_model_version(self) -> ModelVersionRepresentation | None:
        from vectice.models.representation.model_version_representation import ModelVersionRepresentation

        if self.validation_config.model is None:
            return None

        if self.connection:
            mdv = self.validation_config.model
            try:
                mdv_repr = self.connection.browse(mdv)
                if isinstance(mdv_repr, ModelVersionRepresentation):
                    return mdv_repr
                else:
                    _logger.warning(f"The id provided for model version returned {mdv_repr.__class__}")
                    return None
            except Exception:
                _logger.warning(f"Failed to get model version {mdv}. Please check the provided id.")
                return None
        raise ValueError("Connection not set. Please provide credentials to setup a connection.")

    def get_phase(self):
        if self.connection:
            return self.connection.browse(self.phase)
        raise ValueError("Connection not set. Please provide credentials to setup a connection.")

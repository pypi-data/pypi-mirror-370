# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import json

from typing import Dict, List, Optional, Tuple

from azureml._common._error_definition.azureml_error import AzureMLError  # type: ignore

from azureml.acft.accelerator.utils.error_handling.error_definitions import LLMInternalError
from azureml.acft.accelerator.utils.error_handling.exceptions import LLMException
from azureml.acft.common_components import get_logger_app

from azureml.acft.multimodal.components.constants.constants import AdditionalFeatureType, ColumnTypesInfoLiterals

from azureml.automl.core.constants import FeatureType
from azureml.automl.core.featurization import FeaturizationConfig
from azureml.automl.core.shared.constants import Tasks, MLTableLiterals, MLTableDataLabel
from azureml.automl.runtime.column_purpose_detection import StatsAndColumnPurposeType
from azureml.automl.runtime._ml_engine.validation import common_data_validations

from azureml.core import Run

from azureml.train.automl._azureautomlsettings import AzureAutoMLSettings
from azureml.train.automl.runtime._automl_job_phases import ExperimentPreparationPhase
from azureml.train.automl.runtime._entrypoints.utils import featurization


logger = get_logger_app(__name__)


class AutomlColumnPurposeDetector:
    """Class to detect the column types in the input data using AutoML."""

    def __init__(self, train_mltable_path: str, validation_mltable_path: str, label_column: str, image_column: str,
                 drop_columns: Optional[List[str]],
                 numerical_columns_overrides: Optional[List[str]],
                 categorical_columns_overrides: Optional[List[str]],
                 text_columns_overrides: Optional[List[str]]):
        """Init function

        :param train_mltable_path: Train MLTable
        :type train_mltable_path: str
        :param validation_mltable_path: Validation MLTable
        :type validation_mltable_path: str
        :param label_column: Target label column
        :type label_column: str
        :param image_column: Image column
        :type image_column: str
        :param drop_columns: List of columns to ignore
        :type drop_columns: Optional[List[str]]
        :param numerical_columns_overrides: Numerical column overrides
        :type numerical_columns_overrides: Optional[List[str]]
        :param categorical_columns_overrides: Categorical column overrides
        :type categorical_columns_overrides: Optional[List[str]]
        :param text_columns_overrides: Text column overrides
        :type text_columns_overrides: Optional[List[str]]
        """
        self.train_mltable_path = train_mltable_path
        self.validation_mltable_path = validation_mltable_path
        self.label_column = label_column
        self.image_column = image_column
        self.drop_columns = drop_columns
        self.numerical_columns_overrides = numerical_columns_overrides
        self.categorical_columns_overrides = categorical_columns_overrides
        self.text_columns_overrides = text_columns_overrides

    @staticmethod
    def _get_mltable_dict_from_mltable_path(mltable_path: Optional[str]) -> Optional[Dict[str, str]]:
        """Get MLTable dictionary representation from mltable path.

        :param mltable_path: MLTable path.
        :type mltable_path: Optional[str]
        :return: MLTable dictionary representation.
        :rtype: Optional[Dict[str, str]]
        """
        if mltable_path is None:
            return None

        return {
            "Uri": "",
            MLTableLiterals.MLTABLE_RESOLVEDURI: mltable_path,
            "AssetId": ""
        }

    def _get_mltable_json(self) -> str:
        """ Get json representation of train, validation mltable paths.

        :return: Mltable json representation.
        :rtype: str
        """
        mltable_json_dict = {
            "Type": MLTableLiterals.MLTABLE,
            MLTableDataLabel.TrainData.value: self._get_mltable_dict_from_mltable_path(self.train_mltable_path),
            MLTableDataLabel.ValidData.value: self._get_mltable_dict_from_mltable_path(self.validation_mltable_path),
            MLTableDataLabel.TestData.value: None
        }
        return json.dumps(mltable_json_dict)

    def _get_automl_settings(self, drop_columns: List[str]) -> AzureAutoMLSettings:
        """Get Automl Settings for column purpose detection.

        :param drop_columns: List of columns to ignore.
        :type drop_columns: List[str]
        :return: Automl Settings
        :rtype AzureAutoMLSettings
        """
        column_purpose_overrides = {}
        if self.numerical_columns_overrides is not None:
            for column in self.numerical_columns_overrides:
                column_purpose_overrides[column] = FeatureType.Numeric
        if self.categorical_columns_overrides is not None:
            for column in self.categorical_columns_overrides:
                column_purpose_overrides[column] = FeatureType.Categorical
        if self.text_columns_overrides is not None:
            for column in self.text_columns_overrides:
                column_purpose_overrides[column] = FeatureType.Text

        if not column_purpose_overrides:
            column_purpose_overrides = None

        featurization_config = FeaturizationConfig(
            column_purposes=column_purpose_overrides,
            drop_columns=drop_columns
        )

        automl_settings_obj = AzureAutoMLSettings(
            label_column_name=self.label_column,
            task_type=Tasks.CLASSIFICATION,
            featurization=featurization_config
        )
        return automl_settings_obj

    def _get_final_drop_columns(self) -> List[str]:
        """Add image columns to the list of drop columns and return the updated drop columns.

        :return: Updated list of drop columns
        :rtype: List[str]
        """
        result = []
        if self.drop_columns is not None:
            result.extend(self.drop_columns)
        result.append(self.image_column)
        return result

    @staticmethod
    def _get_supported_column_types() -> List[str]:
        """Get supported column types.

        :return: List of supported column types.
        :rtype: List[str]
        """
        return [FeatureType.Categorical, FeatureType.Numeric, FeatureType.Text, AdditionalFeatureType.Image,
                AdditionalFeatureType.Label]

    def _get_updated_stats_and_column_purposes(
            self, stats_and_column_purposes: Optional[List[StatsAndColumnPurposeType]]
    ) -> Optional[List[StatsAndColumnPurposeType]]:
        """Get updated stats and column purposes by fixing the following:
            - Treat all categoricalHash columns as Categorical
            - Treat self.image_column as Images

        :param stats_and_column_purposes: Stats and column purposes.
        :type stats_and_column_purposes: Optional[List[StatsAndColumnPurposeType]]
        :return: Updates stats and column purposes.
        :rtype: Optional[List[StatsAndColumnPurposeType]]
        """
        if stats_and_column_purposes is None:
            return stats_and_column_purposes

        logger.info("Updating stats_and_column_purposes obtained from column purpose detection.")
        result = []
        for entry in stats_and_column_purposes:
            column_type = entry[1]
            column_name = entry[2]
            if column_type == FeatureType.CategoricalHash:
                logger.info("{} column is detected to be of type {}. Updating it's type as {}".format(
                    column_name, column_type, FeatureType.Categorical))
                # Multimodal preprocessing doesn't differentiate between Categorical and CategoricalHash.
                result.append((entry[0], FeatureType.Categorical, entry[2]))
            elif column_name == self.image_column:
                # Special handling for image column as stats_and_column_purpose detection doesn't recognize Image
                # feature type.
                logger.info("Updating type for column {} to {}".format(column_name, AdditionalFeatureType.Image))
                result.append((entry[0], AdditionalFeatureType.Image, entry[2]))
            else:
                result.append(entry)
        return result

    @staticmethod
    def _get_column_types_and_ignore_columns_from_column_purposes(
            stats_and_column_purposes: Optional[List[StatsAndColumnPurposeType]]
    ) -> Tuple[List[Dict[str, str]], List[str]]:
        """Get column types and ignore columns from stats and column purposes.

        :param stats_and_column_purposes: Stats and column purposes.
        :type stats_and_column_purposes: Optional[List[StatsAndColumnPurposeType]]
        :return: Tuple of Column types, Ignore columns
        :rtype: Tuple[List[Dict[str, str]], List[str]]
        """
        logger.info("Fetching column types and ignore columns from stats_and_column_purposes.")
        supported_column_types = AutomlColumnPurposeDetector._get_supported_column_types()
        if not stats_and_column_purposes:
            logger.warning("Stats_and_column_purpose is None. No columns of types {} will be processed.".format(
                supported_column_types))
            return [], []

        column_types = []
        ignore_columns = []

        for entry in stats_and_column_purposes:
            column_type = entry[1]
            column_name = entry[2]

            if column_type in supported_column_types:
                logger.info("{} column is detected to be of supported type {}".format(column_name, column_type))
                column_type_info = {
                    ColumnTypesInfoLiterals.COLUMN_TYPE: column_type,
                    ColumnTypesInfoLiterals.COLUMN_NAME: column_name
                }
                column_types.append(column_type_info)
            else:
                logger.warning("{} column is detected to be of unsupported type {}. It will be ignored.".format(
                    column_name, column_type
                ))
                ignore_columns.append(column_name)

        logger.info("Column type info obtained for {} supported columns.".format(len(column_types)))
        logger.info("Number of unsupported columns ignored: {}".format(len(ignore_columns)))
        return column_types, ignore_columns

    def get_column_types_and_ignore_columns(self) -> Tuple[List[Dict[str, str]], List[str]]:
        """Get column types and ignore columns from train and validation mltable.

        :return: Tuple of Column types, ignore columns
        :rtype: Tuple[List[Dict[str, str]], List[str]]
        """
        run = Run.get_context()
        try:
            parent_run_id = ""

            mltable_data_json = self._get_mltable_json()
            drop_columns = self._get_final_drop_columns()
            automl_settings_obj = self._get_automl_settings(drop_columns=drop_columns)

            try:
                logger.info("Initializing data for column purpose detection.")
                raw_experiment_data, feature_config_manager = featurization.initialize_data(
                    run=run, iteration_name="setup", automl_settings_obj=automl_settings_obj,
                    script_directory=None, dataprep_json=mltable_data_json, entry_point=None,
                    parent_run_id=parent_run_id
                )
            except Exception as e:
                logger.error("Exception while trying to initialize data for column purpose detection: {}".format(e))
                common_data_validations.materialized_tabular_data_user_error_handler(e)

            logger.info("Running column purpose detection.")
            feature_sweeped_state_container = ExperimentPreparationPhase.run(
                parent_run_id=parent_run_id,
                automl_settings=automl_settings_obj,
                cache_store=None,
                current_run=run,
                experiment_observer=None,
                feature_config_manager=feature_config_manager,
                raw_experiment_data=raw_experiment_data,
                validate_training_data=True,
                verifier=None
            )
            logger.info("Column purpose detection done.")

            # Update stats_and_column_purposes with known fixes.
            stats_and_column_purposes = self._get_updated_stats_and_column_purposes(
                feature_sweeped_state_container.data_transformer.stats_and_column_purposes)

            # Get column types and ignore columns from updated stats_and_column_purposes.
            column_types, ignore_columns = self._get_column_types_and_ignore_columns_from_column_purposes(
                stats_and_column_purposes)

            # Add label column to column_types
            column_types.append({
                ColumnTypesInfoLiterals.COLUMN_TYPE: AdditionalFeatureType.Label,
                ColumnTypesInfoLiterals.COLUMN_NAME: self.label_column
            })
            logger.info("Label column added to column types.")
            logger.info("Final number of column types detected: {}".format(len(column_types)))

            return column_types, ignore_columns
        except Exception as e:
            error_message = "Exception during column purpose detection: {}".format(e)
            raise LLMException._with_error(AzureMLError.create(LLMInternalError, error=error_message))

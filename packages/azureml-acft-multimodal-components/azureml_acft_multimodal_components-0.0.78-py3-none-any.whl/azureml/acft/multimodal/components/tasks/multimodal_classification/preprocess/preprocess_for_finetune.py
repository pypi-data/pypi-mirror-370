# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
# Copyright 2020 The HuggingFace Inc. team. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ---------------------------------------------------------
import copy
import os
import json
from argparse import Namespace
from typing import Dict, List, Optional

from azureml._common._error_definition.azureml_error import AzureMLError  # type: ignore

from azureml.acft.multimodal.components.constants.constants import SaveFileConstants, AdditionalFeatureType, \
    ColumnTypesInfoLiterals
from azureml.acft.multimodal.components.tasks.multimodal_classification.preprocess.automl_column_purpose_detector \
    import AutomlColumnPurposeDetector
from azureml.acft.contrib.hf.nlp.constants.constants import DataSliceConstants
from azureml.acft.contrib.hf.nlp.tasks.nlp_multiclass.preprocess.preprocess_for_finetune import \
    NLPMulticlassPreprocessForFinetune, NLPMulticlassPreprocessArgs
from azureml.acft.contrib.hf.nlp.tasks.nlp_multilabel.preprocess.preprocess_for_finetune import \
    NLPMultilabelPreprocessForFinetune, NLPMultilabelPreprocessArgs
from azureml.acft.contrib.hf.nlp.constants.constants import AzuremlConstants, AutomlConstants, PreprocessArgsTemplate
from azureml.acft.common_components import get_logger_app

from azureml.automl.core.constants import FeatureType
from transformers import AutoConfig, AutoModel
from azureml.acft.multimodal.components.model.mmeft.mm_early_fusion_config import AzuremlMMEarlyFusionConfig
from azureml.acft.multimodal.components.model.mmeft.mm_early_fusion_model import (
    AzuremlMMEarlyFusionModelForClassification
)


logger = get_logger_app(__name__)


class PreprocessForFinetune:
    """
    Class pre-processing data for Multimodal model.
    This is base class common for Single label and multilabel classification.
    """
    def __init__(self, component_args: Namespace) -> None:

        AutoConfig.register("mmeft", AzuremlMMEarlyFusionConfig)
        AutoModel.register(AzuremlMMEarlyFusionConfig, AzuremlMMEarlyFusionModelForClassification)

        self.preprocess_params = vars(component_args)
        logger.info("Preprocess parameters before parsing: {}".format(self.preprocess_params))
        comma_separated_params = ["drop_columns", "numerical_columns_overrides", "categorical_columns_overrides",
                                  "text_columns_overrides"]
        for param_name in comma_separated_params:
            self.preprocess_params[param_name] = self._parse_comma_separated_parameter(
                self.preprocess_params[param_name])
        logger.info("Preprocess parameters after parsing: {}".format(self.preprocess_params))

        self.column_types: List[Dict[str, str]] = []
        self.ignore_columns: List[str] = []

    def _encode_data_splits(self):
        # override to disable encoding for multimodal encoding done at training.
        return

    @staticmethod
    def _parse_comma_separated_parameter(param_value: Optional[str]) -> Optional[List[str]]:
        """Parse a comma separated string parameter to list of strings

        :param param_value: Parameter value
        :type param_value: Optional[str]
        :return: List of strings
        :rtype: Optional[List[str]]
        """
        if param_value is None or param_value == "":
            result = None
        else:
            param_value_split = param_value.split(",")
            result = [entry.strip() for entry in param_value_split]
        return result

    def _fetch_column_types_and_ignore_columns_from_data(self) -> None:
        """
        Fetch column properties from data and update column types information and ignore columns.
        """
        label_column = self.preprocess_params["label_column"]
        image_column = self.preprocess_params["image_column"]
        drop_columns = self.preprocess_params["drop_columns"]
        numerical_columns_overrides = self.preprocess_params["numerical_columns_overrides"]
        categorical_columns_overrides = self.preprocess_params["categorical_columns_overrides"]
        text_columns_overrides = self.preprocess_params["text_columns_overrides"]
        train_mltable_path = self.preprocess_params["train_data_path"]
        validation_mltable_path = self.preprocess_params["validation_data_path"]

        # Compute column_types and ignore columns from automl column_purpose_detector
        logger.info("Detecting column types and ignore columns from input data.")
        automl_column_purpose_detector = AutomlColumnPurposeDetector(
            train_mltable_path=train_mltable_path,
            validation_mltable_path=validation_mltable_path,
            label_column=label_column,
            image_column=image_column,
            drop_columns=drop_columns,
            numerical_columns_overrides=numerical_columns_overrides,
            categorical_columns_overrides=categorical_columns_overrides,
            text_columns_overrides=text_columns_overrides)
        self.column_types, self.ignore_columns = \
            automl_column_purpose_detector.get_column_types_and_ignore_columns()

    def _fetch_pass_through_columns_and_dataset_columns_from_column_types(self) -> None:
        """Update list of pass through columns and dataset columns from column types information.
        """
        pass_through_columns = []
        dataset_columns = []
        for column_type_info in self.column_types:
            column_type = column_type_info[ColumnTypesInfoLiterals.COLUMN_TYPE]
            column_name = column_type_info[ColumnTypesInfoLiterals.COLUMN_NAME]
            # Add all columns to list of dataset columns
            dataset_columns.append(column_name)
            # Add non text and label columns to list of pass through columns
            if column_type in [AdditionalFeatureType.Image, FeatureType.Categorical, FeatureType.Numeric]:
                pass_through_columns.append(column_name)
        # Add ignore columns also to list of dataset columns since they are also part of input data
        dataset_columns.extend(self.ignore_columns)
        self.pass_through_columns = pass_through_columns
        self.dataset_columns = dataset_columns

    def _get_column_types_for_preprocessed_data(self) -> List[Dict[str, str]]:
        """This function returns the preprocessed column types that reflect the NLP preprocessing does the following:
            - Removes text columns from the data
            - Creates a new text column with merged text columns data.
            - Adds a prefix to all column names

        :return: Column types for preprocessed data.
        :rtype: List[Dict[str, str]]
        """
        column_types_for_preprocessed_data = []

        for index, column_type_info in enumerate(self.column_types):
            # Add info about non-text columns
            if column_type_info[ColumnTypesInfoLiterals.COLUMN_TYPE] != FeatureType.Text:
                column_types_for_preprocessed_data.append(copy.deepcopy(column_type_info))

        # Append the merged text column
        column_types_for_preprocessed_data.append({
            ColumnTypesInfoLiterals.COLUMN_TYPE: FeatureType.Text,
            ColumnTypesInfoLiterals.COLUMN_NAME: AutomlConstants.TEXT_CLASSIFICATION_COLUMN_NAME,
        })

        # Add prefix to all column names
        for index, column_type_info in enumerate(column_types_for_preprocessed_data):
            column_type_info[ColumnTypesInfoLiterals.COLUMN_NAME] = \
                AzuremlConstants.DATASET_COLUMN_PREFIX + column_type_info[ColumnTypesInfoLiterals.COLUMN_NAME]

        return column_types_for_preprocessed_data

    def pre_preprocess(self) -> None:
        """
        This should be called before calling preprocess() method of
        NLPMultilabelPreprocessForFinetune or NLPMultilabelPreprocessForFinetune
        """
        # Fetch column types and ignore columns from the dataset.
        self._fetch_column_types_and_ignore_columns_from_data()

        # Update pass through columns and dataset columns in NLP preprocessor before running preprocess.
        self._fetch_pass_through_columns_and_dataset_columns_from_column_types()

    def post_preprocess(self) -> None:
        """
        This should be called after calling preprocess() method of
        NLPMultilabelPreprocessForFinetune or NLPMultilabelPreprocessForFinetune
        """
        column_types_for_preprocessed_data = self._get_column_types_for_preprocessed_data()

        output_folder = self.preprocess_params["output_dir"]
        # Save metadata (column types information) to output folder
        column_types_save_path = os.path.join(output_folder, SaveFileConstants.COLUMN_TYPES_SAVE_PATH)
        column_types_info = {
            ColumnTypesInfoLiterals.COLUMN_TYPES: column_types_for_preprocessed_data
        }
        logger.info(f"Saving column types info to {column_types_save_path}")
        with open(column_types_save_path, 'w') as fp:
            json.dump(column_types_info, fp, indent=2)


class SingleLabelPreprocessForFinetune(PreprocessForFinetune, NLPMulticlassPreprocessForFinetune):
    """
    Class pre-processing data for Multimodal model.
    This class is specific for single label classification.
    """
    def __init__(self, component_args: Namespace, preprocess_args: NLPMulticlassPreprocessArgs) -> None:
        PreprocessForFinetune.__init__(self, component_args=component_args)
        component_args.train_slice = component_args.validation_slice = component_args.test_slice = \
            DataSliceConstants.NO_SPLIT
        NLPMulticlassPreprocessForFinetune.__init__(self, component_args=component_args,
                                                    preprocess_args=preprocess_args)

    def preprocess(self) -> None:
        """
        Method to preprocess data specific for Single-label Multimodal classification task.
        """
        super().pre_preprocess()
        logger.info("Calling preprocess method of NLPMulticlassPreprocessForFinetune class.")
        super().preprocess()
        super().post_preprocess()


class MultiLabelPreprocessForFinetune(PreprocessForFinetune, NLPMultilabelPreprocessForFinetune):
    """
    Class pre-processing data for Multimodal model.
    This class is specific for multilabel classification.
    """

    def __init__(self, component_args: Namespace, preprocess_args: NLPMultilabelPreprocessArgs) -> None:
        PreprocessForFinetune.__init__(self, component_args=component_args)
        component_args.train_slice = component_args.validation_slice = component_args.test_slice = \
            DataSliceConstants.NO_SPLIT
        NLPMultilabelPreprocessForFinetune.__init__(self, component_args=component_args,
                                                    preprocess_args=preprocess_args)

    def preprocess(self) -> None:
        """
        Method to preprocess data specific for Multi-label Multimodal classification task.
        """
        super().pre_preprocess()
        logger.info("Calling preprocess method of NLPMultilabelPreprocessForFinetune class.")
        super().preprocess()
        super().post_preprocess()

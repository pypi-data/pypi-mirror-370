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
"""
Base dataset for loading MLTable
"""
import ast
import pandas as pd
from datasets import Image, Dataset
from sklearn.preprocessing import StandardScaler
from transformers.tokenization_utils_base import PreTrainedTokenizerBase
from typing import Any, Callable, Dict, List, Optional, Set, Tuple, Union

from azureml.acft.common_components import get_logger_app
from azureml.acft.multimodal.components.data.mltable_helper import MLTableHelper
from azureml.acft.multimodal.components.data.utils import empty_list_if_None
from azureml.acft.multimodal.components.constants.constants import DatasetSplit, DataMode

from azureml._common._error_definition.azureml_error import AzureMLError
logger = get_logger_app(__name__)


class AzuremlTabularFeaturizer:
    """Class to perform featurization on tabular (numerical + categorical) columns and label encode the label column.
    """
    def __init__(self, categorical_columns: List[str], numerical_columns: List[str], data_split: DatasetSplit,
                 active_modes: List[str]) -> None:
        """Init function

        :param categorical_columns: Categorical columns
        :type categorical_columns: List[str]
        :param numerical_columns: Numerical columns
        :type numerical_columns: List[str]
        :param data_split: Data split.
        :type data_split: DatasetSplit
        :param active_modes: List of active modes in the data - tabular/text/vision
        :type active_modes: List[str]
        """
        self.categorical_columns = categorical_columns
        self.numerical_columns = numerical_columns
        self.data_split = data_split
        self.active_modes = active_modes

        self.id_set: Dict[str, Set] = {}
        self.scaler: Optional[StandardScaler] = None
        self.categorical_encoders: Dict[str, Any] = {}

    def fit_transform(self, df: pd.DataFrame) -> pd.DataFrame:
        """Perform fit transform on the input dataframe.

        :param df: Input dataframe
        :type df: pd.DataFrame
        :return: Transformed dataframe
        :rtype: pd.DataFrame
        """

        if len(self.numerical_columns) > 0 and (DataMode.TABULAR in self.active_modes):
            self.scaler = StandardScaler()
            df[self.numerical_columns] = self.scaler.fit_transform(df[self.numerical_columns])

            logger.info(f"Scaling Mean = {self.scaler.mean_}")
            logger.info(f"Scaling Variance = {self.scaler.var_}")

        categorical_encoders = {}

        for column_name in self.categorical_columns:
            self.id_set[column_name] = set(df[column_name])

        for column_name in self.categorical_columns:
            df[column_name] = df[column_name].astype('category').cat.as_ordered()
            categorical_encoders[column_name] = df[column_name].cat.categories
            df[column_name] = df[column_name].cat.codes + 1  # + 1 in nunique here
        self.categorical_encoders = categorical_encoders

        return df

    def transform(
            self, df: pd.DataFrame, return_original: bool = False
    ) -> Union[pd.DataFrame, Tuple[pd.DataFrame, pd.DataFrame]]:
        """Transform input data frame

        :param df: Input data frame
        :type df: pd.DataFrame
        :param return_original: Whether to return original dataframe or not
        :type return_original: bool
        :return: Transformed dataframe or tuple of transformed, original dataframes
        :rtype: Union[pd.DataFrame, Tuple[pd.DataFrame, pd.DataFrame]]
        """

        if len(self.numerical_columns) > 0 and (DataMode.TABULAR in self.active_modes):
            df[self.numerical_columns] = self.scaler.transform(df[self.numerical_columns])

            logger.info(f"Scaling Mean = {self.scaler.mean_}")
            logger.info(f"Scaling Variance = {self.scaler.var_}")

        df_orig = None
        df_tmp = df

        if return_original:
            logger.info("Return orig flow")
            df_orig = df_tmp.copy(deep=True)
            df = df_tmp
        else:
            df = df_tmp

        if self.categorical_columns:
            for column_name in self.categorical_columns:
                df[column_name] = pd.Categorical(df[column_name], categories=self.categorical_encoders[column_name],
                                                 ordered=True)
                df[column_name] = df[column_name].cat.codes + 1  # + 1 in nunique here

        if return_original:
            return df, df_orig
        else:
            return df

    def get_categorical_cardinalities(self) -> List[int]:
        """Get categorical cardinalities in the data. Should be called after transforming the data.

        :return: List of categorical cardinalities
        :rtype: List[int]
        """
        categorical_cardinalities = []
        if self.categorical_columns:
            for c in self.categorical_columns:
                categorical_cardinalities.append(len(self.categorical_encoders[c]) + 1)  # +1 for others
        return categorical_cardinalities


class AzureMLMultiModalDataset:
    """Dataset for MultiModal datasets that parses MLTable, downloads image data and creates a HF dataset.
    """

    def __init__(
            self,
            jsonl_path: str,
            data_split: DatasetSplit,
            dataset_args: Dict[str, Any],
            collation_fn: Callable,
            image_transforms_fn: Callable,
            label2id: Dict[Any, Any],
            tabular_featurizer: Optional[AzuremlTabularFeaturizer] = None,
            text_tokenizer: Optional[PreTrainedTokenizerBase] = None,
            processor: Optional[Any] = None,
            is_multilabel: bool = False,
            device: str = "cpu",
            download_files: bool = True
    ):
        """Init function

        :param jsonl_path: Jsonl file path.
        :type jsonl_path: str
        :param data_split: Dataset split type
        :type data_split: DatasetSplit
        :param dataset_args: Dataset arguments contains information about columns
        :type dataset_args: Dict[str, Any]
        :param collation_fn: Collation function.
        :type collation_fn: Callable
        :param image_transforms_fn: Image transformation function.
        :type image_transforms_fn: Callable
        :param label2id: Label to ID mapping
        :type label2id: Dict[Any, Any]
        :param tabular_featurizer: Tabular featurizer. Should be None when data_split is train.
            Should be the featurizer from train dataset when data_split is validation/test.
        :type tabular_featurizer: Optional[AzuremlTabularFeaturizer]
        :param text_tokenizer: Text tokenizer
        :type text_tokenizer: Optional[PreTrainedTokenizerBase]
        :param processor: Model Preprocessor. Used in the case of CLIP model.
        :type processor: Optional[Any]
        :param is_multilabel: True if its a multilabel dataset. False if its multiclass (single label) dataset.
        :type is_multilabel: bool
        :param device: Device
        :type device: str
        """
        self.collation_fn = collation_fn
        self.image_transforms_fn = image_transforms_fn
        self.processor = processor
        self.jsonl_path = jsonl_path
        self.dataset_args = dataset_args
        self.data_split = data_split
        self.is_multilabel = is_multilabel
        self.device = device
        self.tabular_featurizer = tabular_featurizer
        self.text_tokenizer = text_tokenizer
        self.input_size = 224
        self.label2id = label2id

        self.image_column_name = dataset_args.get("image_column_name")
        self.text_columns = dataset_args.get("text_columns")
        self.numerical_columns = empty_list_if_None(dataset_args.get("numerical_columns"))
        self.categorical_columns = empty_list_if_None(dataset_args.get("categorical_columns"))
        self.label_column = dataset_args.get("label_column_name")
        self.download_files = download_files

        self.modes = []
        if len(self.numerical_columns) != 0 or len(self.categorical_columns) != 0:
            self.modes.append(DataMode.TABULAR)
        if len(self.text_columns) != 0:
            self.modes.append(DataMode.TEXT)
        if self.image_column_name is not None:
            self.modes.append(DataMode.IMAGE)

        if self.tabular_data_present():
            if self.data_split == DatasetSplit.TRAIN:
                # Initializer tabular featurizer
                self.tabular_featurizer = AzuremlTabularFeaturizer(categorical_columns=self.categorical_columns,
                                                                   numerical_columns=self.numerical_columns,
                                                                   data_split=data_split,
                                                                   active_modes=self.modes)
            else:
                self.tabular_featurizer.data_split = data_split

        dataset_df = self._get_dataframe_from_jsonl_path()
        processed_dataset_df = self._preprocess_data(dataset_df=dataset_df)

        self.dataset = self.load(processed_dataset_df)
        self.set_image_transform()

    def get_tabular_featurizer(self) -> Optional[AzuremlTabularFeaturizer]:
        """Get tabular featurizer

        :return: Tabular featurizer
        :rtype: Optional[AzuremlTabularFeaturizer]
        """
        return self.tabular_featurizer

    def get_modes(self) -> List[DataMode]:
        """Get list of data modes.

        :return: List of data modes.
        :rtypes: List[DataMode]
        """
        return self.modes

    def get_num_numericals(self) -> int:
        """Get number of numerical columns.

        :return: Number of numerical columns
        :rtype: int
        """
        return len(self.numerical_columns)

    def get_categorical_cardinalities(self) -> List[int]:
        """Get categorical cardinalities in the data

        :return: List of categorical cardinalities
        :rtype: List[int]
        """
        if self.tabular_featurizer:
            return self.tabular_featurizer.get_categorical_cardinalities()
        return []

    def get_num_text_columns(self) -> int:
        """Get number of text columns.

        :return: Number of numerical columns.
        :rtype: int
        """
        return len(self.text_columns)

    def tabular_data_present(self) -> bool:
        """Is tabular data present

        :return: Whether tabular data is present or not
        :rtype: bool
        """
        return DataMode.TABULAR in self.modes

    def text_data_present(self) -> bool:
        """Is text data present

        :return: Whether text data is present or not
        :rtype: bool
        """
        return DataMode.TEXT in self.modes

    def image_data_present(self) -> bool:
        """Is image data present

        :return: Whether image data is present or not
        :rtype: bool
        """
        return DataMode.IMAGE in self.modes

    def _get_dataframe_from_jsonl_path(self) -> pd.DataFrame:
        """Get Dataframe from jsonl path. This function uses MLTableHelper to load the jsonl into a dataframe.

        :return: Dataframe corresponding to the jsonl file
        :rtype: pd.DataFrame
        """
        mltable_helper = MLTableHelper.from_jsonl_path(jsonl_path=self.jsonl_path,
                                                       image_column_name=self.image_column_name,
                                                       download_files=self.download_files)
        dataset_df = mltable_helper.dataframe
        return dataset_df

    def _convert_label2id(self, label_instance: Union[str, int]) -> Union[List, int]:
        """
        Convert label string to its corresponding id.
        For single label tuple="ClassA", for multi-label tuple="['ClassA','ClassB']"

        :param label_instance: label or labels.
        :type label_instance: str or int
        :return: A single number label id for single label. And a list of number i.e. label ids
        :rtype: Union[List, int]
        """
        if label_instance is not None:
            if self.is_multilabel and len(label_instance) > 0:
                label_str = ast.literal_eval(label_instance)
                return [self.label2id[x] for x in label_str]
            else:
                return self.label2id[label_instance]
        else:
            logger.info("Label for some of the rows in dataset is Null. Ignoring these rows.")

        return None

    def _preprocess_data(self, dataset_df: pd.DataFrame) -> pd.DataFrame:
        """Preprocess data in the dataframe.

        :param dataset_df: Dataframe corresponding to the dataset
        :type dataset_df: pd.DataFrame
        :return: Preprocessed dataframe
        :rtype: pd.DataFrame
        """
        if self.tabular_data_present():
            if self.data_split == DatasetSplit.TRAIN:
                processed_dataset_df = self.tabular_featurizer.fit_transform(dataset_df)
            else:
                processed_dataset_df = self.tabular_featurizer.transform(dataset_df)
        else:
            processed_dataset_df = dataset_df

        if self.text_data_present():
            # Filling missing text columns with Blank
            processed_dataset_df[self.text_columns] = processed_dataset_df[self.text_columns].fillna('')

        # Convert label to ids
        if self.data_split != DatasetSplit.TEST:
            processed_dataset_df[self.label_column] = \
                processed_dataset_df[self.label_column].apply(lambda x: self._convert_label2id(x))

        return processed_dataset_df

    def load(self, dataset_df) -> Dataset:
        """Loads a HF dataset from Pandas dataframe
        """
        if self.image_column_name is not None:
            dataset = Dataset.from_pandas(dataset_df).cast_column(self.image_column_name, Image())
        else:
            dataset = Dataset.from_pandas(dataset_df)

        return dataset

    def set_image_transform(self):
        """Set Image transform on the dataset
        """
        if self.image_data_present():
            image_transform = self.image_transforms_fn(self, data_split=self.data_split)
            if image_transform is not None:
                self.dataset.set_transform(image_transform)

    def get_collation_function(self) -> Optional[Callable]:
        """Get collation function
        """
        return self.collation_fn(self)

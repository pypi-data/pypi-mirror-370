# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import copy
import json
import numpy as np
import os
import pandas
import pickle
import tempfile
import torch
from transformers import PreTrainedModel
from transformers.tokenization_utils_base import PreTrainedTokenizerBase
from typing import Dict, Optional

from dataclasses import asdict
from torch.utils.data import DataLoader

from azureml.acft.contrib.hf.nlp.tasks.nlp_multiclass.preprocess.base import NLPMulticlassDatasetInference
from azureml.acft.contrib.hf.nlp.tasks.nlp_multiclass.preprocess.base import NLPMulticlassPreprocessArgs
from azureml.acft.multimodal.components.constants.constants import PreprocessJsonConstants, \
    DatasetSplit, MLFlowHFFlavourPredictConstants, ModelTypes, SaveFileConstants
from azureml.acft.multimodal.components.data.dataset import AzureMLMultiModalDataset, AzuremlTabularFeaturizer
from azureml.acft.multimodal.components.data.utils import get_dataset_args_from_column_types
from azureml.acft.multimodal.components.collators.collators import get_collation_function
from azureml.acft.multimodal.components.image_transformations.transformations import get_transform_function


def predict(data, model, tokenizer, **kwargs):
    """Predict function.

    :param data: Data to evaluate on in pandas dataframe format.
    :type data: pd.Dataframe
    :param model: Model used to predict
    :type model: Any
    :param tokenizer: Tokenizer
    :type tokenizer: Any
    :param kwargs: Additional kwargs to be used during predict
    :type kwargs: Dict[str, Any]
    :return: Prediction labels for the evaluation data. This is of shape num_data_points * 1
    :rtype: numpy.array
    """
    probs = predict_proba(data, model, tokenizer, **kwargs)
    prediction_ids = np.argmax(probs, axis=1)
    # Convert predictions from ids to labels
    prediction_labels = np.array(
        [model.config.id2label[prediction_id] for prediction_id in prediction_ids]
    )
    return prediction_labels


def get_tabular_featurizer(tabular_featurizer_path: str):
    """Get tabular featurizer if it is saved as part of mlflow model. Else, return None

    :param tabular_featurizer_path: Path to tabular featurizer
    :type tabular_featurizer_path: str
    :return: Tabular featurizer
    :rtype: Optional[AzuremlTabularFeaturizer]
    """
    if not tabular_featurizer_path:
        # Tabular featurizer not saved as part of model.
        return None

    with open(tabular_featurizer_path, "rb") as rptr:
        tabular_featurizer = pickle.load(rptr)

    return tabular_featurizer


def get_preprocess_args(preprocess_output_path: str,
                        tabular_featurizer_path: str,
                        tokenizer: Optional[PreTrainedTokenizerBase]) -> \
        (Dict, Optional[AzuremlTabularFeaturizer], Dict):
    """
    :param preprocess_output_path: Path to directory where we have output of data preprocessing
    :type preprocess_output_path: str
    :param tabular_featurizer_path: Path to pickle file that has featurizer for tabular portion of dataset.
    :type tabular_featurizer_path: str
    :param tokenizer: Tokenizer object of for textual data
    :type tokenizer: Optional[PreTrainedTokenizerBase]
    :return: (Arguments that were given to NLP preprocessor, plus other properties related to dataset,
              Featurizer for tabular data,
              Columns segregated based on its type
              )
    :rtype: (Dict, Optional[AzuremlTabularFeaturizer], Dict)
    """
    preprocess_json_path = os.path.join(preprocess_output_path, SaveFileConstants.PREPROCESS_ARGS_SAVE_PATH)
    column_types_path = os.path.join(preprocess_output_path, SaveFileConstants.COLUMN_TYPES_SAVE_PATH)

    with open(preprocess_json_path) as rptr:
        preprocess_args_json = json.load(rptr)
        dataset_columns = preprocess_args_json[PreprocessJsonConstants.DATASET_COLUMNS]
        ignore_columns = preprocess_args_json[PreprocessJsonConstants.IGNORE_COLUMNS]
        pass_through_columns = preprocess_args_json[PreprocessJsonConstants.PASS_THROUGH_COLUMNS]
        preprocess_args = NLPMulticlassPreprocessArgs()
        preprocess_args.label_column = preprocess_args_json[PreprocessJsonConstants.LABEL_COLUMN]

    nlp_dataset_args = asdict(preprocess_args)
    dataset_kwargs = dict(
        dataset_args=nlp_dataset_args,
        required_columns=preprocess_args.required_columns,
        required_column_dtypes=preprocess_args.required_column_dtypes,
        label_column=preprocess_args.label_column,
        tokenizer=tokenizer,
        pass_through_columns=pass_through_columns,
        ignore_columns=ignore_columns,
        dataset_columns=dataset_columns
    )

    mm_dataset_args = get_dataset_args_from_column_types(column_types_path)

    tabular_featurizer = None
    if tabular_featurizer_path:
        tabular_featurizer = get_tabular_featurizer(tabular_featurizer_path)

    return dataset_kwargs, tabular_featurizer, mm_dataset_args


def predict_probabilities(data: pandas.core.frame.DataFrame, model: PreTrainedModel, batch_size: int,
                          nlp_dataset_kwargs: Dict, tabular_featurizer: Optional[AzuremlTabularFeaturizer],
                          mm_dataset_args: Dict, device: torch.device,
                          download_files: bool = True):
    """Predict probabilities function.

    :param data: Data in pandas dataframe format for prediction.
    :type data: pandas.core.frame.DataFrame
    :param model: Finetuned model
    :type model: transformers.PreTrainedModel
    :param batch_size: Batch size for prediction
    :type batch_size: int
    :param nlp_dataset_kwargs: Details related to fields/columns present in dataset.
                               These are also sent to NLP pre-processor.
    :type nlp_dataset_kwargs: Dict
    :param tabular_featurizer: Featurizer for tabular dataset.
    :type tabular_featurizer: Optional[AzuremlTabularFeaturizer]
    :param mm_dataset_args: Information in which columns have what kind of data.
    :type mm_dataset_args: Dict
    :param device: Current device
    :type device: torch.device
    :param download_files: Whether to make an attempt to download files from blob.
                           While serving from online/batch endpoint it should be False. during finetuning it's True.
    :type download_files: bool
    :return: Prediction probabilities for the evaluation data. This is of shape num_data_points * num_labels
    :rtype: numpy array
    """
    nlp_dataset = NLPMulticlassDatasetInference(data, **copy.deepcopy(nlp_dataset_kwargs))
    tmp_output_dir = tempfile.TemporaryDirectory().name
    dataset_file_name = nlp_dataset.save(save_folder=tmp_output_dir, save_name=DatasetSplit.TEST)
    mm_dataset = AzureMLMultiModalDataset(jsonl_path=os.path.join(tmp_output_dir, dataset_file_name),
                                          data_split=DatasetSplit.TEST,
                                          dataset_args=mm_dataset_args,
                                          label2id=model.config.label2id,
                                          tabular_featurizer=tabular_featurizer,
                                          text_tokenizer=nlp_dataset_kwargs["tokenizer"],
                                          collation_fn=get_collation_function(ModelTypes.MMEFT),
                                          image_transforms_fn=get_transform_function(ModelTypes.MMEFT),
                                          device=device,
                                          download_files=download_files)
    dataloader = DataLoader(mm_dataset.dataset, batch_size=batch_size, shuffle=False,
                            collate_fn=mm_dataset.get_collation_function())
    preds = []
    for (idx, batch) in enumerate(dataloader):
        res = torch.softmax(model(**batch)[1], dim=1)
        preds += res.cpu().detach().numpy().tolist()

    return preds


def predict_proba(data, model, tokenizer, **kwargs):
    """Predict probabilities function.

    :param data: Data to evaluate on in pandas dataframe format.
    :type data: pd.Dataframe
    :param model: Model used to predict
    :type model: Any
    :param tokenizer: Tokenizer
    :type tokenizer: Any
    :param kwargs: Additional kwargs to be used during predict
    :type kwargs: Dict[str, Any]
    :return: Prediction probabilities for the evaluation data. This is of shape num_data_points * num_labels
    :rtype: numpy array
    """

    extra_files = kwargs[MLFlowHFFlavourPredictConstants.EXTRA_FILES]
    model_path = kwargs[MLFlowHFFlavourPredictConstants.PATH]
    preprocess_json_path = os.path.join(model_path, extra_files[0])
    column_types_path = os.path.join(model_path, extra_files[1])

    with open(preprocess_json_path) as rptr:
        preprocess_args_json = json.load(rptr)
        dataset_columns = preprocess_args_json[PreprocessJsonConstants.DATASET_COLUMNS]
        ignore_columns = preprocess_args_json[PreprocessJsonConstants.IGNORE_COLUMNS]
        pass_through_columns = preprocess_args_json[PreprocessJsonConstants.PASS_THROUGH_COLUMNS]
        preprocess_args = NLPMulticlassPreprocessArgs()
        preprocess_args.label_column = preprocess_args_json[PreprocessJsonConstants.LABEL_COLUMN]

    # First preprocess data using NLPInferenceDataset
    # Output to jsonl file
    nlp_dataset_args = asdict(preprocess_args)
    nlp_dataset_kwargs = dict(
        dataset_args=nlp_dataset_args,
        required_columns=preprocess_args.required_columns,
        required_column_dtypes=preprocess_args.required_column_dtypes,
        label_column=preprocess_args.label_column,
        tokenizer=tokenizer,
        pass_through_columns=pass_through_columns,
        ignore_columns=ignore_columns,
        dataset_columns=dataset_columns
    )
    device = kwargs.get("device", "cuda" if torch.cuda.is_available() else "cpu")
    tabular_featurizer = get_tabular_featurizer(model_path, extra_files)
    # Create a mmdataset using this jsonl
    mm_dataset_args = get_dataset_args_from_column_types(column_types_path)
    preds = predict_probabilities(data, model, 1, nlp_dataset_kwargs, tabular_featurizer, mm_dataset_args, device)
    return preds

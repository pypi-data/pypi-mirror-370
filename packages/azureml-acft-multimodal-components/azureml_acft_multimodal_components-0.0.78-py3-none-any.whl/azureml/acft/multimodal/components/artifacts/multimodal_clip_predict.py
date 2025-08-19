# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import json
import pickle
import tempfile
import numpy as np
import torch
import copy
import os
from azureml.acft.multimodal.components.data.dataset import AzureMLMultiModalDataset
from torch.utils.data import DataLoader
from azureml.acft.contrib.hf.nlp.tasks.nlp_multiclass.preprocess.base import NLPMulticlassDatasetInference
from azureml.acft.contrib.hf.nlp.tasks.nlp_multiclass.preprocess.base import NLPMulticlassPreprocessArgs
from azureml.acft.multimodal.components.constants.constants import MLFlowHFFlavourPredictConstants, \
    PreprocessJsonConstants, DatasetSplit, ModelTypes
from azureml.acft.multimodal.components.data.utils import get_dataset_args_from_column_types
from dataclasses import asdict
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


def _get_tabular_featurizer(model_path, extra_files):
    """Get tabular featurizer if it is saved as part of mlflow model. Else, return None

    :param model_path: Model path
    :type model_path: str
    :param extra_files: List of extra files saved as part of MLFlow model
    :type extra_files: List[Dict[str, str]]
    :return: Tabular featurizer
    :rtype: Optional[AzuremlTabularFeaturizer]
    """
    if len(extra_files) < 3:
        # Tabular featurizer not saved as part of model.
        return None

    tabular_featurizer_path = os.path.join(model_path, extra_files[2][MLFlowHFFlavourPredictConstants.PATH])
    with open(tabular_featurizer_path, "rb") as rptr:
        tabular_featurizer = pickle.load(rptr)

    return tabular_featurizer


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
    preprocess_json_path = os.path.join(model_path, extra_files[0][MLFlowHFFlavourPredictConstants.PATH])
    column_types_path = os.path.join(model_path, extra_files[1][MLFlowHFFlavourPredictConstants.PATH])
    with open(preprocess_json_path) as rptr:
        preprocess_args_json = json.load(rptr)
        dataset_columns = preprocess_args_json[PreprocessJsonConstants.DATASET_COLUMNS]
        ignore_columns = preprocess_args_json[PreprocessJsonConstants.IGNORE_COLUMNS]
        pass_through_columns = preprocess_args_json[PreprocessJsonConstants.PASS_THROUGH_COLUMNS]
        # TODO: How to read this from json dict
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
    nlp_dataset = NLPMulticlassDatasetInference(data, **copy.deepcopy(nlp_dataset_kwargs))
    tmp_output_dir = tempfile.TemporaryDirectory().name
    dataset_file_name = nlp_dataset.save(save_folder=tmp_output_dir, save_name=DatasetSplit.TEST)
    device = kwargs.get("device", "cuda" if torch.cuda.is_available() else "cpu")
    # Create a mmdataset using this jsonl
    tabular_featurizer = _get_tabular_featurizer(model_path, extra_files)
    mm_dataset_args = get_dataset_args_from_column_types(column_types_path)
    mm_dataset = AzureMLMultiModalDataset(jsonl_path=os.path.join(tmp_output_dir, dataset_file_name),
                                          data_split=DatasetSplit.TEST,
                                          dataset_args=mm_dataset_args, label2id=model.config.label2id,
                                          tabular_featurizer=tabular_featurizer,
                                          processor=tokenizer, collation_fn=get_collation_function(ModelTypes.CLIP),
                                          image_transforms_fn=get_transform_function(ModelTypes.CLIP), device=device)

    dataloader = DataLoader(mm_dataset.dataset, shuffle=True, collate_fn=mm_dataset.get_collation_function())
    preds = []
    model.to(device)
    for (idx, batch) in enumerate(dataloader):
        res = torch.softmax(model(**batch)["prediction"], dim=1)
        preds += res.cpu().detach().numpy().tolist()
    return preds

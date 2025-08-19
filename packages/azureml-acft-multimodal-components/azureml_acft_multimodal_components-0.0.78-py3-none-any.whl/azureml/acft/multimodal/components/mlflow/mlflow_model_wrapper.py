# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Mlflow PythonModel wrapper class that loads the Mlflow model, preprocess inputs and performs inference."""

import math
import mlflow
import pandas as pd
import torch
from transformers import AutoConfig, AutoModel, AutoTokenizer
import tempfile
from typing import Union

from azureml.acft.multimodal.components.artifacts.multimodal_mmeft_predict \
    import get_preprocess_args, predict_probabilities
from azureml.acft.multimodal.components.constants.constants \
    import MLFlowPyfuncLiterals, ModelTypes, FinetuneParamLiterals, SaveFileConstants
from azureml.acft.multimodal.components.model.mmeft.mm_early_fusion_config \
    import AzuremlMMEarlyFusionConfig
from azureml.acft.multimodal.components.model.mmeft.mm_early_fusion_model \
    import AzuremlMMEarlyFusionModelForClassification
from azureml.acft.multimodal.components.utils.common_utils import get_current_device
from azureml.acft.multimodal.components.mlflow.utils \
    import create_temp_file, process_image, get_image_column_name, get_class_labels


class MultimodalMLFlowModelWrapper(mlflow.pyfunc.PythonModel):
    """MLFlow model wrapper for AutoML for Images models."""

    def __init__(
        self
    ) -> None:
        """
        This method is called when the python model wrapper is initialized.
        """
        super().__init__()
        self.model = None
        self.tabular_featurizer = None
        self.nlp_dataset_kwargs = None
        self.mm_dataset_args = None
        self._device = None
        self.image_column_name = None
        self.class_labels = None

    def load_context(self, context: mlflow.pyfunc.PythonModelContext) -> None:
        """This method is called when loading a Mlflow model with pyfunc.load_model().

        :param context: Mlflow context containing artifacts that the model can use for inference.
        :type context: mlflow.pyfunc.PythonModelContext
        """

        print("Inside load_context()")
        self._device = get_current_device()
        tabular_featurizer_path = None
        try:
            model_checkpoint_path = context.artifacts[MLFlowPyfuncLiterals.CHECKPOINT_FOLDER]

            tokenizer = AutoTokenizer.from_pretrained(model_checkpoint_path)
            print("Tokenizer loaded successfully")
            if MLFlowPyfuncLiterals.TABULAR_FEATURIZER_PKL in context.artifacts:
                # For not-fine tuned raw base model, tabular_featurizer_path won't be present
                tabular_featurizer_path = context.artifacts[MLFlowPyfuncLiterals.TABULAR_FEATURIZER_PKL]
                print("Tabular featurizer pickle file found")

            if FinetuneParamLiterals.PREPROCESS_OUTPUT in context.artifacts:
                # For not-fine tuned raw base model, preprocess_output_path won't be present
                preprocess_output_path = context.artifacts[FinetuneParamLiterals.PREPROCESS_OUTPUT]

                self.image_column_name = get_image_column_name(preprocess_output_path + "/" +
                                                               SaveFileConstants.COLUMN_TYPES_SAVE_PATH)
                self.class_labels = get_class_labels(preprocess_output_path + "/" +
                                                     SaveFileConstants.CLASSES_SAVE_PATH)

                self.nlp_dataset_kwargs, self.tabular_featurizer, self.mm_dataset_args = \
                    get_preprocess_args(preprocess_output_path, tabular_featurizer_path, tokenizer)
            else:
                print("Model doesn't have any information on class labels or input columns of dataset.\
                      This is possible when model wasn't finetuned and you are using the raw model.")

            AutoConfig.register(model_type=ModelTypes.MMEFT, config=AzuremlMMEarlyFusionConfig)
            AutoModel.register(config_class=AzuremlMMEarlyFusionConfig,
                               model_class=AzuremlMMEarlyFusionModelForClassification)
            config = AutoConfig.from_pretrained(pretrained_model_name_or_path=model_checkpoint_path)
            self.model = AutoModel.from_config(config=config).to(self._device)
            print("Model loaded successfully")
        except Exception:
            print("Failed to load some of the files needed to load the model and perform data preprocessing.")
            raise


    def predict(
        self, context: mlflow.pyfunc.PythonModelContext, input_data: Union[dict, pd.DataFrame]
    ) -> pd.DataFrame:
        """This method performs inference on the input data.

        :param context: Mlflow context containing artifacts that the model can use for inference.
        :type context: mlflow.pyfunc.PythonModelContext
        :param input_data: Input data for prediction.
        :type input_data: Union[dict, pd.DataFrame]
        :return: Output of inference
        :rtype: Pandas DataFrame with columns ["probs", "labels"] i.e. probabilities for each class and
                label corresponding to class that had max probability.
        """
        print("predicting for received input")
        ngpus = torch.cuda.device_count()
        batch_size = len(input_data)
        if ngpus > 1:
            batch_size = int(math.ceil(batch_size // ngpus))

        print(f"evaluating with batch_size: {batch_size} and n_gpus: {ngpus}")
        if isinstance(input_data, dict):
            # for online endpoint, input_data is a dictionary, convert to the pandas dataframe
            # for batch endpoint, input_data is already a dataframe
            input_data = pd.DataFrame(input_data['data'], columns=input_data['columns'].tolist())

        if any(input_data[self.image_column_name].str.startswith('azureml://')):
            # Image column contains azureml url; when image persisted on blb store.
            # If at least 1 tuple has azureml url, it is assumed that all the images would be on azureml storage.
            result = predict_probabilities(input_data, self.model, batch_size,
                                           self.nlp_dataset_kwargs, self.tabular_featurizer,
                                           self.mm_dataset_args, self._device, True)
        else:
            # Image given as http web url or as base64 encoded string
            processed_images = input_data.loc[:, [self.image_column_name]] \
                .apply(axis=1, func=process_image)

            with tempfile.TemporaryDirectory() as tmp_output_dir:
                image_path_list = (
                    processed_images.iloc[:, 0].map(lambda row: create_temp_file(row, tmp_output_dir)).tolist()
                )
                input_data[self.image_column_name] = image_path_list

                result = predict_probabilities(input_data, self.model, batch_size,
                                               self.nlp_dataset_kwargs, self.tabular_featurizer,
                                               self.mm_dataset_args, self._device, False)

        return pd.DataFrame(result, columns=self.class_labels)

# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from argparse import Namespace
from typing import List

from azureml.acft.multimodal.components.base_runner import BaseRunner

from azureml.acft.accelerator.utils.hf_argparser import HfArgumentParser
from azureml.acft.common_components import get_logger_app
from azureml.acft.contrib.hf.nlp.tasks.nlp_multiclass.preprocess.preprocess_for_finetune import \
            NLPMulticlassPreprocessArgs
from azureml.acft.contrib.hf.nlp.tasks.nlp_multilabel.preprocess.preprocess_for_finetune \
    import NLPMultilabelPreprocessArgs
from azureml.acft.multimodal.components.tasks.multimodal_classification.finetune.finetune \
    import SingleLabelFinetune
from azureml.acft.multimodal.components.tasks.multimodal_classification.finetune_mmeft.finetune \
    import FinetuneForMmeft
from azureml.acft.multimodal.components.tasks.multimodal_classification.preprocess.preprocess_for_finetune \
    import MultiLabelPreprocessForFinetune
from azureml.acft.multimodal.components.tasks.multimodal_classification.preprocess.preprocess_for_finetune \
    import SingleLabelPreprocessForFinetune
from azureml.acft.multimodal.components.utils.model_selector_utils import model_selector

logger = get_logger_app(__name__)


class SingleLabelRunner(BaseRunner):

    def run_preprocess_for_finetune(self, component_args: Namespace, unknown_args: List[str]) -> None:
        preprocess_arg_parser = HfArgumentParser([NLPMulticlassPreprocessArgs])
        preprocess_args: NLPMulticlassPreprocessArgs = preprocess_arg_parser.parse_args_into_dataclasses(
            unknown_args)[0]

        preprocess_args.label_key = component_args.label_column
        preprocess_args.label_column = component_args.label_column
        preprocess_args.task_name = component_args.task_name
        preprocess_obj = SingleLabelPreprocessForFinetune(component_args, preprocess_args)
        preprocess_obj.preprocess()

    def run_finetune(self, component_args: Namespace) -> None:
        finetune_obj = SingleLabelFinetune(vars(component_args))
        finetune_obj.finetune()

    def run_finetune_for_mmeft(self, component_plus_preprocess_args: Namespace = None) -> None:
        finetune_obj = FinetuneForMmeft(vars(component_plus_preprocess_args))
        finetune_obj.finetune()

    def run_modelselector(self, *args, **kwargs) -> None:
        model_selector(kwargs)


class MultiLabelRunner(SingleLabelRunner):
    def run_preprocess_for_finetune(self, component_args: Namespace, unknown_args: List[str]) -> None:
        preprocess_arg_parser = HfArgumentParser([NLPMultilabelPreprocessArgs])
        preprocess_args: NLPMultilabelPreprocessArgs = preprocess_arg_parser.parse_args_into_dataclasses(
            unknown_args)[0]

        preprocess_args.label_key = component_args.label_column
        preprocess_args.label_column = component_args.label_column
        preprocess_args.task_name = component_args.task_name
        preprocess_obj = MultiLabelPreprocessForFinetune(component_args, preprocess_args)
        preprocess_obj.preprocess()

# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""
File for factory method for all Multimodal tasks
This file is called by component scripts files to fetch the corresponding task runners
"""

from azureml.acft.multimodal.components.constants.constants import Tasks
from azureml.acft.multimodal.components.tasks.multimodal_classification.runner import SingleLabelRunner
from azureml.acft.multimodal.components.tasks.multimodal_classification.runner import MultiLabelRunner


def get_task_runner(task_name: str):
    """
    returns task related runner
    """
    if task_name == Tasks.MUTIMODAL_CLASSIFICATION:
        return SingleLabelRunner
    elif task_name == Tasks.MULTIMODAL_MULTILABEL_CLASSIFICATION:
        return MultiLabelRunner
    raise NotImplementedError(f"Runner for the task {task_name} is not supported")

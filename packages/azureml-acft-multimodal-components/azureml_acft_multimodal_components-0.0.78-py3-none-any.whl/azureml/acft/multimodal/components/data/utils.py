# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import json
from typing import Any

def get_dataset_args_from_column_types(column_types_path):
    dataset_args = {}
    with open(column_types_path) as fp:
        column_types = json.load(fp)
        for entry in column_types["column_types"]:
            column_type = entry["column_type"]
            column_name = entry["column_name"]
            if column_type == "Image":
                dataset_args["image_column_name"] = column_name
            elif column_type == "Label":
                dataset_args["label_column_name"] = column_name
            elif column_type == "Text":
                if "text_columns" not in dataset_args:
                    dataset_args["text_columns"] = []
                dataset_args["text_columns"].append(column_name)
            elif column_type == "Numeric":
                if "numerical_columns" not in dataset_args:
                    dataset_args["numerical_columns"] = []
                dataset_args["numerical_columns"].append(column_name)
            elif column_type == "Categorical":
                if "categorical_columns" not in dataset_args:
                    dataset_args["categorical_columns"] = []
                dataset_args["categorical_columns"].append(column_name)
    return dataset_args


def empty_list_if_None(obj: Any) -> Any:
    """
    Return empty list if obj is None, else return obj itself

    :param obj: Any object
    :type obj: Any
    :return: Empty list if input is None else return same input object.
    :rtype: Any
    """
    if obj is None:
        return []
    return obj

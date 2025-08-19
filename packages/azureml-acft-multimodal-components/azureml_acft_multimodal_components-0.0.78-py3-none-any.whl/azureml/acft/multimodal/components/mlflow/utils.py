# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Mlflow PythonModel wrapper helper scripts."""

import base64
import io
import json
import logging
import pandas as pd
from PIL import Image, UnidentifiedImageError
import re
import requests
import tempfile
from typing import List

from azureml.acft.multimodal.components.constants.constants import ColumnTypesInfoLiterals, ColumnTypesValue, \
    SaveFileConstants

logger = logging.getLogger(__name__)

# Uncomment the following line for mlflow debug mode
# logging.getLogger("mlflow").setLevel(logging.DEBUG)


def get_image_column_name(column_types_file_path: str) -> str:
    """
    Get column name that has images in it. Refer to output of data preprocessing component.
    It has a json which has column names and its data types.

    :param column_types_file_path: Json file path that has mapping of column names and its data type.
    :type column_types_file_path: str
    :return: Name of column that stores image data
    :rtype: str
    """
    with open(column_types_file_path, "r") as f:
        column_types_data = json.load(f)

    column_types_data = column_types_data[ColumnTypesInfoLiterals.COLUMN_TYPES]
    for column_type_data in column_types_data:
        column_type = column_type_data[ColumnTypesInfoLiterals.COLUMN_TYPE]
        column_name = column_type_data[ColumnTypesInfoLiterals.COLUMN_NAME]
        if column_type == ColumnTypesValue.IMAGE:
            prefix_len = len(ColumnTypesInfoLiterals.COLUMN_PREFIX)
            return column_name[prefix_len:]

    return None


def get_class_labels(class_labels_file_path: str) -> List:
    """
    Get list of class labels. Refer to output of data preprocessing component.
    It has a json which has column names and its data types.

    :param class_labels_file_path: Json file path that has list of class labels.
    :type class_labels_file_path: str
    :return: List of class labels
    :rtype: List
    """
    with open(class_labels_file_path, "r") as f:
        class_names_data = json.load(f)

    class_names_list = class_names_data[SaveFileConstants.CLASSES_SAVE_KEY]
    return class_names_list


def _is_valid_url(text: str) -> bool:
    """check if text is url or base64 string

    :param text: text to validate
    :type text: str
    :return: True if url else false
    :rtype: bool
    """
    regex = (
        "((http|https)://)(www.)?"
        + "[a-zA-Z0-9@:%._\\+~#?&//=]"
        + "{2,256}\\.[a-z]"
        + "{2,6}\\b([-a-zA-Z0-9@:%"
        + "._\\+~#?&//=]*)"
    )
    p = re.compile(regex)

    # If the string is empty
    # return false
    if str is None:
        return False

    # Return if the string
    # matched the ReGex
    if re.search(p, text):
        return True
    else:
        return False


def process_image(img: pd.Series) -> pd.Series:
    """If input image is in base64 string format, decode it to bytes. If input image is in url format,
    download it and return bytes.
    https://github.com/mlflow/mlflow/blob/master/examples/flower_classifier/image_pyfunc.py

    :param img: pandas series with image in base64 string format or url.
    :type img: pd.Series
    :return: decoded image in pandas series format.
    :rtype: Pandas Series
    """
    image = img[0]
    if isinstance(image, bytes):
        return img
    elif isinstance(image, str):
        if _is_valid_url(image):
            try:
                response = requests.get(image)
                response.raise_for_status()  # Raise exception in case of unsuccessful response code.
                image = response.content
                return pd.Series(image)
            except requests.exceptions.RequestException as ex:
                raise ValueError(f"Unable to retrieve image from url string due to exception: {ex}")
        else:
            try:
                return pd.Series(base64.b64decode(image))
            except ValueError:
                raise ValueError("The provided image string cannot be decoded."
                                 "Expected format is base64 string or url string.")
    else:
        raise ValueError(f"Image received in {type(image)} format which is not supported."
                         "Expected format is bytes, base64 string or url string.")


def create_temp_file(request_body: bytes, parent_dir: str) -> str:
    """Create temporory file, save image and return path to the file.

    :param request_body: Image
    :type request_body: bytes
    :param parent_dir: directory name
    :type parent_dir: str
    :return: Path to the file
    :rtype: str
    """
    with tempfile.NamedTemporaryFile(dir=parent_dir, mode="wb", delete=False) as image_file_fp:
        img_path = image_file_fp.name + ".png"
        try:
            img = Image.open(io.BytesIO(request_body))
        except UnidentifiedImageError as e:
            logger.error("Invalid image format. Please use base64 encoding for input images.")
            raise e
        img.save(img_path)
        return img_path


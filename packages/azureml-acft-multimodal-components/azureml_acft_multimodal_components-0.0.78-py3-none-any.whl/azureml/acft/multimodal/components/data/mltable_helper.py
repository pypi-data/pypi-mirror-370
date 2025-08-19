# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import mltable
import os
import pandas as pd
import tempfile

from azureml.core import Run
from mltable import DataType, MLTable
from typing import Dict, Optional


class MLTableHelper:
    """Helper class to create MLTable from jsonl files and to download image files present in the MLTable"""

    def __init__(self, input_mltable: MLTable, image_column_name: Optional[str] = None,
                 ignore_not_found: bool = True, download_files: bool = True):
        """Init function

        :param input_mltable: Input mltable
        :type input_mltable: MLTable
        :param image_column_name: Image column name
        :type image_column_name: Optional[str]
        :param ignore_not_found: Whether to ignore image files that are not found.
            Valid when image_column_name is not None.
        :type ignore_not_found: bool
        :param download_files: Whether to download image files. Valid when image_column_name is not None.
        :type download_files: bool
        """
        self._mltable = input_mltable
        self._image_column_name = image_column_name
        self._ignore_not_found = ignore_not_found
        self._download_files = download_files

        if self._image_column_name is None:
            self._local_data_dir = None
            self._dataset_df = self._mltable.to_pandas_dataframe()
        else:
            self._local_data_dir = tempfile.TemporaryDirectory().name
            if self._download_files:
                self._download_image_files()

            self._dataset_df = self._mltable.to_pandas_dataframe()

            if self._download_files:
                self._replace_with_local_paths()

    @staticmethod
    def from_jsonl_path(jsonl_path: str, **kwargs) -> "MLTableHelper":
        """Create mltable helper from jsonl file.

        :param jsonl_path: Jsonl file path
        :type jsonl_path: str
        :param kwargs: kwargs to pass to init function.
        :type kwargs: Dict
        :return: MLTable helper
        :rtype: MLTableHelper
        """
        paths = [{"file": jsonl_path}]
        input_mltable = mltable.from_json_lines_files(paths)
        return MLTableHelper(input_mltable=input_mltable, **kwargs)

    @property
    def dataframe(self) -> pd.DataFrame:
        """Get dataframe from mltable

        :return: Pandas dataframe
        :rtype: pd.DataFrame
        """
        return self._dataset_df

    def _convert_image_column_to_stream_info(self) -> None:
        """Convert image column in mltable to stream info.
        """
        column_types = {
            self._image_column_name: DataType.to_stream()
        }
        self._mltable = self._mltable.convert_column_types(column_types)

    @staticmethod
    def _get_workspace_storage_options() -> Dict:
        """Get workspace storage options to be used for mltable download.

        :return: Storage options
        :rtype: Dict
        """
        # from azureml.core import Workspace
        # ws = Workspace("dbd697c3-ef40-488f-83e6-5ad4dfb78f9b", "phmantri_eastus", "phmantri_eastus_2")
        ws = Run.get_context().experiment.workspace

        return {
            'subscription': ws.subscription_id,
            'resource_group': ws.resource_group,
            'workspace': ws.name,
            'location': ws.location
        }

    def _get_mltable_with_empty_rows_removed(self) -> MLTable:
        """ Get a new mltable with rows with empty image column removed. Please note that rows are not removed from
        the original mltable as other columns in such rows might be needed by the caller.

        :return: MLTable with empty image rows removed.
        :rtype: MLTable
        """
        mltable_empty_rows_removed = self._mltable.filter(
            'col("{}") != "None"'.format(self._image_column_name, self._image_column_name)
        )
        return mltable_empty_rows_removed

    def _download_image_files(self) -> None:
        """Download image files to local disk
        """
        if self._image_column_name is None:
            return

        self._convert_image_column_to_stream_info()
        mltable_empty_rows_removed = self._get_mltable_with_empty_rows_removed()

        storage_options = self._get_workspace_storage_options()
        mltable_empty_rows_removed._download(
            stream_column=self._image_column_name,
            target_path=self._local_data_dir,
            ignore_not_found=self._ignore_not_found,
            storage_options=storage_options
        )

    def _replace_with_local_paths(self) -> None:
        """Replace paths in image column with local paths
        """
        self._dataset_df[self._image_column_name] = self._dataset_df[self._image_column_name].apply(
            lambda x: os.path.join(self._local_data_dir, str(x)) if x is not None and str(x) != "" else None
        )

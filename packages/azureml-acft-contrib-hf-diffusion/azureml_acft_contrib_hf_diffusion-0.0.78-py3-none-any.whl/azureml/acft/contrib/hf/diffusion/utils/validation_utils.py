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
validation utils
"""

from abc import ABC
from typing import List, Optional, Union

from datasets import Value, Sequence

from azureml.acft.accelerator.utils.logging_utils import get_logger_app
from azureml.acft.accelerator.utils.error_handling.exceptions import ValidationException
from azureml.acft.accelerator.utils.error_handling.error_definitions import ValidationError
from azureml._common._error_definition.azureml_error import AzureMLError

from ..constants.constants import AzuremlConstants


logger = get_logger_app()


class AzuremlValidatorMixin(ABC):
    """
    This is a mixin to be used with 'AzuremlDataset' class to provide common utility functions for data validation
    """

    def __init__(self, required_columns: Optional[List[str]] = None, required_column_dtypes: Optional[List[List[str]]] = None):
        """
        Azureml Dataset atleast should have the columns that are present in required_columns. The required_columns should confirm to the dtypes present in required_column_dtypes

        :param required_columns - mandatory columns to be present in Azureml Dataset
        :param required_column_dtypes - valid dtypes of required_columns
        """

        if required_column_dtypes is None:
            required_column_dtypes = []
        if required_columns is None:
            required_columns = []
        if len(required_columns) != len(required_column_dtypes):
            raise ValueError("Required columns and their dtypes should be of same length")

        self.required_columns = required_columns
        self.required_column_dtypes = required_column_dtypes
        if self.label_column_optional and self.label_column is not None and \
            self.label_column not in self.dataset.column_names:
            logger.info(f"Removing label_column {self.label_column} from required columns and its dtypes")
            label_column_index = self.required_columns.index(self.label_column)
            _ = self.required_columns.pop(label_column_index)
            _ = self.required_column_dtypes.pop(label_column_index)
            self.label_column = None

    def remove_extra_columns(self) -> None:
        """
        Removes columns other than required columns and updates the self.dataset
        """
        columns_to_remove = [name for name in self.dataset.column_names if name not in self.required_columns]
        self.dataset = self.dataset.remove_columns(columns_to_remove)
        logger.info(f"Removed columns: {columns_to_remove} from dataset")

    def match_columns(self) -> None:
        """
        Match the dataset columns with the keep columns and raise error otherwise 
        """
        if sorted(self.required_columns) != sorted(self.dataset.column_names):
            raise ValidationException._with_error(
                AzureMLError.create(
                    ValidationError,
                    error=(
                        f"Path or dict: {self.path_or_dict}."
                        f"Dataset Columns: {self._remove_dataset_column_prefix(self.dataset.column_names)}."
                        f"User Passed Columns: {self._remove_dataset_column_prefix(self.required_columns)}."
                    )
                )
            )

    def check_column_dtypes(self) -> None:
        """
        check the keep columns with keep column dtypes and raise error otherwise
        """

        datset_features = self.dataset.features
        for column_name, valid_dtypes in zip(self.required_columns, self.required_column_dtypes):
            if column_name not in datset_features:
                raise ValueError(
                    f"{column_name} not present in column to dtypes map file."
                    f"The following columns are present: {list(datset_features.keys())}"
                )
            sequence_column_type = isinstance(datset_features[column_name], Sequence)
            value_column_dtype = isinstance(datset_features[column_name], Value)
            if sequence_column_type:
                column_dtype = datset_features[column_name].feature.dtype
            elif value_column_dtype:
                column_dtype = datset_features[column_name].dtype
            else:
                raise ValidationException._with_error(
                    AzureMLError.create(
                        ValidationError,
                        error=(
                            f"File path or data: {self.path_or_dict}\n"
                            f"Data formating error for feature {self._remove_dataset_column_prefix(column_name)}\n"
                            f"Found Type: {type(datset_features[column_name])}\n"
                            "Expected Type: Value or Sequence"
                        )
                    )
                )

            if column_dtype not in valid_dtypes:
                raise ValidationException._with_error(
                    AzureMLError.create(
                        ValidationError,
                        error=(
                            f"File path or data: {self.path_or_dict}\n"
                            f"dtype mismatch for feature {self._remove_dataset_column_prefix(column_name)}\n"
                            f"Found dtype: {column_dtype}\n"
                            f"Expected dtypes: {valid_dtypes}"
                        )
                    )
                )
    
    def _check_if_non_empty(self, val: Union[str, List, int]) -> bool:
        """
        Checks if a value is empty based on data type
        """
        # For the supported tasks val will be the following
        # Single Label - int, str
        # Multi Label - int, str
        # NER - list
        # Summarization, Translation - str
        # QnA - data validation is `skipped`
        if val is None:
            return False
        if isinstance(val, (str, List)):
            return len(val) != 0

        return True

    def remove_null_examples(self) -> None:
        """
        Removes the null examples and update the dataset
        Raises error if the number of examples after filter is 0
        """
        null_filter = lambda example: all([self._check_if_non_empty(value) for _, value in example.items()])
        pre_filter_rows = self.dataset.num_rows
        self.dataset = self.dataset.filter(null_filter)
        post_filter_rows = self.dataset.num_rows
        logger.info(f"Null filter - examples before filter: {pre_filter_rows} | examples after filter: {post_filter_rows}")
        if post_filter_rows == 0:
            raise ValidationException._with_error(
                AzureMLError.create(
                    ValidationError,
                    error=f"Found no examples after data preprocessing for {self.path_or_dict}"
                )
            )

    def update_required_columns_with_prefix(self) -> None:
        """
        This function  will update the :param `required_columns` with a constant prefix
        """
        self.required_columns = [AzuremlConstants.DATASET_COLUMN_PREFIX + col for col in self.required_columns]

    def _remove_dataset_column_prefix_string_data(self, data: str) -> str:
        """Remove the dataset column prefix to data string"""
        if isinstance(data, str):
            prefix_to_remove = AzuremlConstants.DATASET_COLUMN_PREFIX
            if data.startswith(prefix_to_remove):
                return prefix_to_remove.join(data.split(prefix_to_remove)[1:])
            else:
                logger.warning("Prefix not found! Skipping removal")
                return data

    def _remove_dataset_column_prefix(self, data: Union[str, List]) -> Union[str, List]:
        """Remove the dataset column prefix from data"""

        if isinstance(data, str):
            return self._remove_dataset_column_prefix_string_data(data=data)
        elif isinstance(data, List):
            output_data = []
            for ele in data:
                output_data.append(self._remove_dataset_column_prefix_string_data(data=ele))
            return output_data
        else:
            logger.warning(f"Prefix removal is not supported for input of type: {type(data)}")
            return data


def remove_dataset_column_prefix_string_data(data: str) -> str:
    """Remove the dataset column prefix to data string"""
    if isinstance(data, str):
        prefix_to_remove = AzuremlConstants.DATASET_COLUMN_PREFIX
        if data.startswith(prefix_to_remove):
            return prefix_to_remove.join(data.split(prefix_to_remove)[1:])
        else:
            logger.warning("Prefix not found! Skipping removal")
            return data
    return data


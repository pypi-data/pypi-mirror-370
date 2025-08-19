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
model selector utils
"""

import os
from pathlib import Path
from typing import Dict, Any, Union
import shutil
import yaml
import json

from ..constants.constants import SaveFileConstants, MLFlowHFFlavourConstants

from ..base_runner import STABLE_DIFFUSION_SUPPORTED_MODELS

from azureml.acft.accelerator.utils.logging_utils import get_logger_app
from azureml.acft.accelerator.utils.error_handling.exceptions import LLMException, ValidationException
from azureml.acft.accelerator.utils.error_handling.error_definitions import LLMInternalError, ModelNotSupported
from azureml._common._error_definition.azureml_error import AzureMLError  # type: ignore


logger = get_logger_app()


MODEL_REGISTRY_NAME = "azureml-preview"


def validate_diffusion_text_to_image_model_name(model_name: str) -> None:
    if model_name not in STABLE_DIFFUSION_SUPPORTED_MODELS:
        raise ValidationException._with_error(
            AzureMLError.create(ModelNotSupported, ModelName=model_name)
        )


def get_model_name_from_pytorch_model(model_path: str) -> str:
    """
    Fetch model_name information from pytorch model metadata file
    """
    finetune_args_file = Path(model_path, SaveFileConstants.FINETUNE_ARGS_SAVE_PATH)

    # load the metadata file
    try:
        with open(finetune_args_file, "r") as rptr:
            finetune_args = json.load(rptr)
    except Exception as e:
        raise LLMException._with_error(
            AzureMLError.create(LLMInternalError, error=(
                f"Failed to load {finetune_args_file}\n"
                f"{e}"
                )
            )
        )

    # check for `model_name` in metadata file
    if finetune_args and "model_name" in finetune_args:
        return finetune_args["model_name"]
    else:
       raise LLMException._with_error(
            AzureMLError.create(LLMInternalError, error=(
                f"model_name is missing in "
                f"{SaveFileConstants.FINETUNE_ARGS_SAVE_PATH} file"
                )
            )
        )


def get_model_name_from_mlflow_model(model_path: str) -> str:
    """
    Fetch model_name information from mlflow metadata file
    """
    mlflow_config_file = Path(model_path, MLFlowHFFlavourConstants.MISC_CONFIG_FILE)

    # load mlflow config file
    try:
        with open(mlflow_config_file, "r") as rptr:
            mlflow_data = yaml.safe_load(rptr)
    except Exception as e:
        raise LLMException._with_error(
            AzureMLError.create(LLMInternalError, error=(
                f"Failed to load {mlflow_config_file}\n"
                f"{e}"
                )
            )
        )

    # fetch the model name
    try:
        return mlflow_data["flavors"]["hftransformers"][MLFlowHFFlavourConstants.HUGGINGFACE_ID]
    except Exception as e:
        raise LLMException._with_error(
            AzureMLError.create(LLMInternalError, error=(
                "{Invalid mlflow config file}\n"
                f"{e}"
                )
            )
        )

def convert_mlflow_model_to_pytorch_model(mlflow_model_path: Union[str, Path], download_dir: Path):
    """
    converts mlflow model to pytorch model
    """
    download_dir.mkdir(exist_ok=True, parents=True)
    try:
        # copy the model files
        shutil.copytree(
            Path(mlflow_model_path, 'data/model'),
            download_dir,
            dirs_exist_ok=True
        )
        # copy LICENSE file
        license_file_path = Path(mlflow_model_path, MLFlowHFFlavourConstants.LICENSE_FILE)
        if license_file_path.is_file():
            shutil.copy(str(license_file_path), download_dir)
    except Exception as e:
        shutil.rmtree(download_dir, ignore_errors=True)
        raise LLMException._with_error(
            AzureMLError.create(
                LLMInternalError,
                error=(
                    "Failed to convert mlflow model to pytorch model.\n"
                    f"{e}"
                )
            )
        )


def model_selector(model_selector_args: Dict[str, Any]):
    """
    Prepares model for continual finetuning
    Save model selector args
    """
    logger.info(f"Model Selector args - {model_selector_args}")
    # pytorch model port
    pytorch_model_path = model_selector_args.get("pytorch_model_path", None)
    # mlflow model port
    mlflow_model_path = model_selector_args.get("mlflow_model_path", None)

    # if both pytorch and mlflow model ports are specified, pytorch port takes precedence
    if pytorch_model_path is not None:
        logger.info("Working with pytorch model")
        # copy model to download_dir
        model_name = get_model_name_from_pytorch_model(pytorch_model_path)
        validate_diffusion_text_to_image_model_name(model_name)
        model_selector_args["model_name"] = model_name
        download_dir = Path(model_selector_args["output_dir"], model_name)
        download_dir.mkdir(exist_ok=True, parents=True)
        try:
            shutil.copytree(pytorch_model_path, download_dir, dirs_exist_ok=True)
        except Exception as e:
            shutil.rmtree(download_dir, ignore_errors=True)
            raise LLMException._with_error(
                AzureMLError.create(
                    LLMInternalError,
                    error=(
                        "shutil copy failed.\n"
                        f"{e}"
                    )
                )
            )
    elif mlflow_model_path is not None:
        logger.info("Working with Mlflow model")
        model_name = get_model_name_from_mlflow_model(mlflow_model_path)
        validate_diffusion_text_to_image_model_name(model_name)
        model_selector_args["model_name"] = model_name
        # convert mlflow model to pytorch model and save it to model_save_path
        download_dir = Path(model_selector_args["output_dir"], model_name)
        convert_mlflow_model_to_pytorch_model(mlflow_model_path, download_dir)
    elif model_selector_args["model_name"]:
        validate_diffusion_text_to_image_model_name(model_selector_args["model_name"])
        logger.info(f'Will fetch {model_selector_args["model_name"]} model while fine-tuning')
    else:
        raise LLMException._with_error(
                AzureMLError.create(
                    LLMInternalError,
                    error=(
                        "Please provide `huggingface_id` or pass valid model to `pytorch_model_path` or `mlflow_model_path`"
                    )
                )
            )

    # Saving model selector args
    model_selector_args_save_path = str(Path(model_selector_args["output_dir"], SaveFileConstants.MODEL_SELECTOR_ARGS_SAVE_PATH))
    logger.info(f"Saving the model selector args to {model_selector_args_save_path}")
    with open(model_selector_args_save_path, "w") as wptr:
        json.dump(model_selector_args, wptr, indent=2)

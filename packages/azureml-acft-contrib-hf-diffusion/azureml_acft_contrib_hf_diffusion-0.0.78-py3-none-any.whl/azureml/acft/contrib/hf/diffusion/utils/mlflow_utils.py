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
mlflow utilities
"""
from pathlib import Path
import json
import shutil
import yaml
from distutils.dir_util import copy_tree
from typing import List, Union, Optional

from pathlib import Path
from mlflow.models import Model

from ..constants.constants import MLFlowHFFlavourConstants

from ..diffusion_auto.model import StableDiffusionPipeline, AzuremlStableDiffusionPipeline

from transformers import TrainerCallback, TrainingArguments, TrainerState, TrainerControl
from transformers import PreTrainedModel
from torch_ort import ORTModule

from azureml._common._error_definition.azureml_error import AzureMLError
from azureml.acft.accelerator.utils.error_handling.exceptions import LLMException
from azureml.acft.accelerator.utils.error_handling.error_definitions import LLMInternalError
from azureml.acft.accelerator.utils.license_utils import download_license_file

from azureml.acft.accelerator.utils.logging_utils import get_logger_app
import azureml.evaluate.mlflow as mlflow

from .mlflow_preprocess import prepare_mlflow_preprocess, restructure_mlflow_acft_code


logger = get_logger_app()


class SaveMLflowModelCallback(TrainerCallback):
    """
    A [`TrainerCallback`] that sends the logs to [AzureML](https://pypi.org/project/azureml-sdk/).
    """

    def __init__(
        self,
        mlflow_model_save_path: Union[str, Path],
        mlflow_infer_params_file_path: Union[str, Path],
        mlflow_task_type: str,
        model_name: str,
        model_name_or_path: Optional[str] = None,
        class_names: Optional[List[str]] = None,
        metadata: dict = {},
        **kwargs
    ) -> None:
        """
        init azureml_run which is azureml Run object
        """
        self.mlflow_model_save_path = mlflow_model_save_path
        self.mlflow_infer_params_file_path = mlflow_infer_params_file_path
        self.mlflow_task_type = mlflow_task_type
        self.class_names = class_names
        self.model_name = model_name
        self.model_name_or_path = model_name_or_path
        self.mlflow_ft_conf = kwargs.get("mlflow_ft_conf", {})
        self.mlflow_hftransformers_misc_conf = self.mlflow_ft_conf.get("mlflow_hftransformers_misc_conf", {})
        self.mlflow_model_signature = self.mlflow_ft_conf.get("mlflow_model_signature", None)
        self.metadata = metadata

    def on_train_end(self, args: TrainingArguments, state: TrainerState, control: TrainerControl, **kwargs):
        """
        Event called at the end of training.
        Save MLflow model at the end of training

        Model and Tokenizer information is part of kwargs
        """

        model, tokenizer = kwargs["model"], kwargs["tokenizer"]

        # saving the mlflow on world process 0
        if state.is_world_process_zero:
            # tokenization parameters for inference
            # task related parameters
            # with open(self.mlflow_infer_params_file_path, 'r') as fp:
            #     mlflow_inference_params = json.load(fp)

            misc_conf = {
                MLFlowHFFlavourConstants.TASK_TYPE: self.mlflow_task_type,
                MLFlowHFFlavourConstants.TRAIN_LABEL_LIST: self.class_names,
                MLFlowHFFlavourConstants.HUGGINGFACE_ID: self.model_name,
                # **mlflow_inference_params,
                "custom_config_module": "diffusers",
                "custom_tokenizer_module": "diffusers",
                "custom_model_module": "diffusers",
                "force_load_tokenizer": False,
                "force_load_config": False,
                "hf_config_class": "AutoConfig",
                "hf_tokenizer_class": "AutoTokenizer",
            }

            if isinstance(model, AzuremlStableDiffusionPipeline):
                acft_model = model
            else:
                raise LLMException._with_error(
                    AzureMLError.create(LLMInternalError, error=(
                        f"Got unexpected model - {model}"
                    ))
                )
            # mlflow.hftransformers.save_model(
            #     acft_model, self.mlflow_model_save_path, tokenizer, model.config, misc_conf,)
            #     #code_paths=files_list, artifact_path=model_artifact_path, conda_env=conda_env,)
            # restructure_mlflow_acft_code(self.mlflow_model_save_path)
            # logger.info("Saved as mlflow model at {}".format(self.mlflow_model_save_path))

            diffusion_model = StableDiffusionPipeline.from_pretrained(
                acft_model.hf_model_name_or_path, # type: ignore
                text_encoder=acft_model.text_encoder, # type: ignore
                vae=acft_model.vae, # type: ignore
                unet=acft_model.unet, # type: ignore
                revision=acft_model.revision, # type: ignore
            )

            misc_conf["hf_pretrained_class"] = diffusion_model.__class__.__name__

            logger.info(f"Adding additional misc to MLModel - {self.mlflow_hftransformers_misc_conf}")
            misc_conf.update(self.mlflow_hftransformers_misc_conf)
            mlflow_model = Model(metadata=self.metadata)

            mlflow.hftransformers.save_model(
                diffusion_model,
                self.mlflow_model_save_path,
                hf_conf=misc_conf,
                mlflow_model=mlflow_model
            ) # type: ignore

            # save LICENSE file to MlFlow model
            if self.model_name_or_path:
                license_file_path = Path(self.model_name_or_path, MLFlowHFFlavourConstants.LICENSE_FILE)
                if license_file_path.is_file():
                    shutil.copy(str(license_file_path), self.mlflow_model_save_path)
                    logger.info("LICENSE file is copied to mlflow model folder")
                else:
                    download_license_file(self.model_name, str(self.mlflow_model_save_path))

            # setting mlflow model signature for inference
            if self.mlflow_model_signature is not None:
                logger.info(f"Adding mlflow model signature - {self.mlflow_model_signature}")
                mlflow_model_file = Path(self.mlflow_model_save_path, MLFlowHFFlavourConstants.MISC_CONFIG_FILE)
                if mlflow_model_file.is_file():
                    mlflow_model_data = {}
                    with open(str(mlflow_model_file), "r") as fp:
                        yaml_data = yaml.safe_load(fp)
                        mlflow_model_data.update(yaml_data)
                        mlflow_model_data["signature"] = self.mlflow_model_signature
                    
                    with open(str(mlflow_model_file), "w") as fp:
                        yaml.dump(mlflow_model_data, fp)
                        logger.info(f"Updated mlflow model file with 'signature': {self.mlflow_model_signature}")
                else:
                    logger.info("No MLmodel file to update signature")
            else:
                logger.info("No signature will be added to mlflow model")

            logger.info("Saved as mlflow model at {}".format(self.mlflow_model_save_path))


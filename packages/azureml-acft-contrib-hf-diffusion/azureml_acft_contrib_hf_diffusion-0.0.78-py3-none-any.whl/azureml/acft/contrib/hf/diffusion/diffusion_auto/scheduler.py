# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""
File containing HF scheduler related functions
"""


from diffusers import DDPMScheduler

from azureml.acft.accelerator.utils.logging_utils import get_logger_app


logger = get_logger_app()


class AzuremlDDPMScheduler(DDPMScheduler):

    @classmethod
    def from_pretrained(cls, hf_model_name_or_path: str, **kwargs) -> DDPMScheduler:

        return super(cls, cls).from_pretrained(hf_model_name_or_path, subfolder="scheduler")
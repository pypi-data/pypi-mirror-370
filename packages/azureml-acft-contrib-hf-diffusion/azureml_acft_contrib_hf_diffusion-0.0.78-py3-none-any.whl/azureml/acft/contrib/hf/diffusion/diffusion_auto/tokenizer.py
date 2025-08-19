# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""
File containing HF tokenizer related functions
"""

from typing import Dict, Any

from transformers import CLIPTokenizer, PreTrainedTokenizerBase

from ..constants.constants import HfConstants
from .config import AzuremlAutoConfig

from azureml.acft.accelerator.utils.logging_utils import get_logger_app


logger = get_logger_app()


class AzuremlCLIPTokenizer(CLIPTokenizer):

    @staticmethod
    def pre_init(hf_model_name_or_path: str) -> Dict[str, Any]:
        """Apply model adjustments before calling the Base tokenizer"""

        model_specific_args = {}

        # model specific adjustments for all tasks
        # model_type = AzuremlAutoConfig.get_model_type(hf_model_name_or_path=hf_model_name_or_path)

        return model_specific_args

    @classmethod
    def from_pretrained(cls, hf_model_name_or_path: str, **kwargs) -> PreTrainedTokenizerBase:
        """
        All the model specific adjustments are defined in their respective task preprocessing files
        :param kwargs
            The kwargs can't contain arbitrary key-value pairs as most of the kwargs will be sent to tokenizer
            during initialization
        """

        apply_adjust = kwargs.pop("apply_adjust", True)
        revision = kwargs.pop("revision", None)
        model_specific_args = kwargs
        if apply_adjust:
            logger.info("Applying model adjustments")
            model_specific_args.update(AzuremlCLIPTokenizer.pre_init(hf_model_name_or_path))

        logger.info(f"Tokenizer initialized with args {model_specific_args}")
        logger.info(hf_model_name_or_path)
        try:
            # fast tokenizer
            tokenizer = super().from_pretrained(
                hf_model_name_or_path,
                use_fast=True,
                subfolder="tokenizer",
                revision=revision,
                **model_specific_args,
            )
        except Exception as e:
            logger.warning(f"Fast tokenizer not supported: {e}")
            logger.info("Trying default tokenizer.")
            # slow tokenizer
            tokenizer = super(cls, cls).from_pretrained(
               hf_model_name_or_path,
               subfolder="tokenizer",
               revision=revision,
                **model_specific_args,
            )
        logger.debug("Loaded tokenizer : {}".format(tokenizer))

        return tokenizer


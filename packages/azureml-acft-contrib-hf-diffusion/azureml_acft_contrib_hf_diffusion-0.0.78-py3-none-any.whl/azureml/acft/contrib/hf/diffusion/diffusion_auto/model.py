# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""
File containing HF model related functions
"""


from __future__ import annotations
import os
import shutil
from distutils.dir_util import copy_tree

from typing import Union, Optional, Dict, Any

from diffusers import AutoencoderKL, UNet2DConditionModel, DDPMScheduler, StableDiffusionPipeline
from transformers import CLIPTextModel

import torch
import torch.nn as nn
import torch.nn.functional as F

from azureml.acft.accelerator.utils.logging_utils import get_logger_app

from .scheduler import AzuremlDDPMScheduler

logger = get_logger_app()


class AzuremlAutoEncoderKL():

    @classmethod
    def from_pretrained(cls, hf_model_name_or_path: str, **kwargs) -> AutoencoderKL:

        revision = kwargs["revision"]
        freeze_weights = kwargs.get("freeze_weights", False)
        device: int = kwargs.get("device", torch.device("cuda"))
        weight_dtype: torch.dtype = kwargs.get("weight_dtype", torch.float32)

        vae = AutoencoderKL.from_pretrained(hf_model_name_or_path, subfolder="vae", revision=revision)
        return AzuremlAutoEncoderKL._post_init(
            vae, freeze_weights=freeze_weights, device=device, weight_dtype=weight_dtype,
        )

    @staticmethod
    def _post_init(
        model: AutoencoderKL, freeze_weights: bool, device: int, weight_dtype: Union[str, torch.dtype]) -> AutoencoderKL:

        if freeze_weights:
            model.requires_grad_(False)
        # model.to(device, dtype=weight_dtype)

        return model


class AzuremlUNet2DConditionModel():

    @classmethod
    def from_pretrained(cls, hf_model_name_or_path: str, **kwargs) -> UNet2DConditionModel:

        revision = kwargs["non_ema_revision"]
        freeze_weights = kwargs.get("freeze_weights", False)
        device: int = kwargs.get("device", torch.device("cuda"))
        weight_dtype: torch.dtype = kwargs.get("weight_dtype", torch.float32)

        unet = UNet2DConditionModel.from_pretrained(hf_model_name_or_path, subfolder="unet", revision=revision)
        return AzuremlUNet2DConditionModel._post_init(
            unet, freeze_weights=freeze_weights, device=device, weight_dtype=weight_dtype,
        )

    @staticmethod
    def _post_init(
        model: UNet2DConditionModel, freeze_weights: bool, device: int, weight_dtype: Union[str, torch.dtype]) -> UNet2DConditionModel:

        if freeze_weights:
            model.requires_grad_(False)
        # model.to(device, dtype=weight_dtype)

        return model


class AzuremlStableDiffusionPipeline(nn.Module):

    def __init__(
        self,
        unet: UNet2DConditionModel,
        vae: AutoencoderKL,
        text_encoder: CLIPTextModel,
        noise_scheduler: DDPMScheduler,
        hf_model_name_or_path: str,
        revision: Optional[str]=None,
        weight_dtype: torch.dtype=torch.float32,
    ) -> None:

        super().__init__()

        self.unet = unet
        self.vae = vae  # require_grad set to False
        self.text_encoder = text_encoder  # require_grad set to False
        self.noise_scheduler = noise_scheduler
        self.weight_dtype = weight_dtype
        self.hf_model_name_or_path = hf_model_name_or_path
        self.revision = revision

    def forward(self, input_ids, pixel_values):
        # Convert images to latent space
        latents = self.vae.encode(pixel_values.to(self.weight_dtype)).latent_dist.sample()
        latents = latents * 0.18215

        # Sample noise that we'll add to the latents
        noise = torch.randn_like(latents)
        bsz = latents.shape[0]
        # Sample a random timestep for each image
        timesteps = torch.randint(0, self.noise_scheduler.num_train_timesteps, (bsz,), device=latents.device)
        timesteps = timesteps.long()

        # Add noise to the latents according to the noise magnitude at each timestep
        # (this is the forward diffusion process)
        noisy_latents = self.noise_scheduler.add_noise(latents, noise, timesteps)

        # Get the text embedding for conditioning
        encoder_hidden_states = self.text_encoder(input_ids)[0]

        # Predict the noise residual and compute loss
        model_pred = self.unet(noisy_latents, timesteps, encoder_hidden_states).sample
        loss = F.mse_loss(model_pred.float(), noise.float(), reduction="mean")

        return loss, model_pred

    @classmethod
    def from_pretrained(cls, hf_model_name_or_path: str, **kwargs):

        non_ema_revision = kwargs.get("non_ema_revision", None)
        revision = kwargs.get("revision", None)
        weight_dtype = kwargs.get("weight_dtype", torch.float32)
        device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

        # set the vae, noise_scheduler and text encoder
        # freezing the weights for vae and text_encoder
        vae = AzuremlAutoEncoderKL.from_pretrained(
            hf_model_name_or_path, revision=revision, freeze_weights=True, weight_dtype=weight_dtype, device=device)
        text_encoder = AzuremlCLIPTextEncoder.from_pretrained(
            hf_model_name_or_path, revision=revision, freeze_weights=True, weight_dtype=weight_dtype, device=device
        )
        noise_scheduler = AzuremlDDPMScheduler.from_pretrained(hf_model_name_or_path)
        unet: UNet2DConditionModel = AzuremlUNet2DConditionModel.from_pretrained(
            hf_model_name_or_path, non_ema_revision=revision)

        return cls(
            unet=unet,
            vae=vae,
            text_encoder=text_encoder,
            noise_scheduler=noise_scheduler,
            weight_dtype=weight_dtype,
            hf_model_name_or_path=hf_model_name_or_path,
            revision=revision)

    def save_pretrained(self, output_dir: str, state_dict: Optional[Dict[str, Any]]=None):

        pipeline = StableDiffusionPipeline.from_pretrained(
            self.hf_model_name_or_path,
            text_encoder=self.text_encoder,
            vae=self.vae,
            unet=self.unet,
            revision=self.revision,
        )
        pipeline.save_pretrained(output_dir)

    @property
    def config(self) -> str:
        return ""

class AzuremlCLIPTextEncoder():

    @classmethod
    def from_pretrained(cls, hf_model_name_or_path: str, **kwargs) -> CLIPTextModel:

        revision = kwargs["revision"]
        freeze_weights = kwargs.get("freeze_weights", False)
        device: int = kwargs.get("device", torch.device("cuda"))
        weight_dtype: torch.dtype = kwargs.get("weight_dtype", torch.float32)
        text_encoder = CLIPTextModel.from_pretrained(hf_model_name_or_path, subfolder="text_encoder", revision=revision)

        return AzuremlCLIPTextEncoder._post_init(
            text_encoder, freeze_weights=freeze_weights, device=device, weight_dtype=weight_dtype,
        )

    @staticmethod
    def _post_init(
        model: CLIPTextModel, freeze_weights: bool, device: int, weight_dtype: Union[str, torch.dtype]) -> CLIPTextModel:

        if freeze_weights:
            model.requires_grad_(False)
        # model.to(device, dtype=weight_dtype)

        return model


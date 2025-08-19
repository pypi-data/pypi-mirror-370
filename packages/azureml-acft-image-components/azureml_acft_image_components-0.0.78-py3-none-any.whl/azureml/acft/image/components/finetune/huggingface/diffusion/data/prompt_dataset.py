# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""A simple dataset to prepare the prompts to generate class images on multiple GPUs."""

from typing import Dict, Union

from azureml.acft.image.components.finetune.huggingface.diffusion.constants.constants import DataConstants
from torch.utils.data import DataLoader, Dataset


class PromptDataset(Dataset):
    """A simple dataset to prepare the prompts to generate class images on multiple GPUs."""

    def __init__(self, prompt: str, num_samples: int):
        """Initialize the dataset with the prompt and number of samples to generate."""
        self.prompt = prompt
        self.num_samples = num_samples

    def __len__(self) -> int:
        """Return the number of samples to generate.

        :return: Number of samples to generate
        :rtype: int
        """
        return self.num_samples

    def __getitem__(self, index: int) -> Dict[str, Union[str, int]]:
        """Get the prompt and index to generate the class image.

        :param index: Index of the sample
        :type index: int
        :return: Prompt and index
        :rtype: Dict[str, Union[str, int]]
        """
        return {DataConstants.PROMPT: self.prompt, DataConstants.INDEX: index}


def get_prompt_dataloader(prompt: str, num_samples: int, batch_size: int = 1) -> DataLoader:
    """Get the prompt dataset to generate class images.

    :param prompt: Prompt to generate the class image
    :type prompt: str
    :param num_samples: Number of samples to generate
    :type num_samples: int
    :param batch_size: Batch size, defaults to 1
    :type batch_size: int
    """
    dataset = PromptDataset(prompt, num_samples)
    dataloader = DataLoader(dataset, batch_size=batch_size)
    return dataloader

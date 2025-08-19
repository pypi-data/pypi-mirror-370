# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""AzureML ACFT Image finetune component - classification dataset using HuggingFace download manager."""

import datasets
import numpy as np
import os
import pandas as pd

from PIL import Image
from typing import List, Dict, Tuple, Any, Generator
from datasets.tasks import ImageClassification
from datasets.download.download_manager import DownloadManager as HFDownloadManager

from azureml.acft.image.components.finetune.common.data.download_manager import (
    DownloadManager,
)
from azureml.acft.image.components.finetune.common.constants.constants import (
    ImageDataFrameConstants,
    ImageDataItemLiterals,
)


class ClassificationHFDataset(datasets.GeneratorBasedBuilder):
    """Image Classification Hugging Face dataset"""

    def __init__(self, *args, mltable_path: str, **kwargs) -> None:
        """Constructor - This reads the MLTable and creates Classification pytorch dataset using Builder
        class exposed by hugging face datasets library.

        :param mltable_data: azureml MLTable path.
        :type mltable_data: str
        :return: None
        :rtype: None
        """

        self.mltable_path = mltable_path

        # Using download manager to download data from MLTable
        # and prepare the dataframe from the same
        self.download_manager = DownloadManager(mltable_path)

        # get list of labels from dataframe
        self.class_labels = self._get_labels()

        super().__init__(*args, writer_batch_size=None, **kwargs)

    def _get_labels(self) -> List[str]:
        """Get labels from dataframe

        :return: List of labels
        :rtype: List[str]
        """
        labels = self.download_manager._images_df[
            self.download_manager._label_column_name
        ]
        classes = set(labels)

        return list(classes)

    def _info(self) -> datasets.DatasetInfo:
        """Prepare the dataset information used by Builder class

        :return: HF Dataset information
        :rtype: datasets.DatasetInfo
        """
        return datasets.DatasetInfo(
            description=None,
            features=datasets.Features(
                {
                    ImageDataItemLiterals.DEFAULT_IMAGE_KEY: datasets.Image(),
                    ImageDataItemLiterals.DEFAULT_LABEL_KEY: datasets.ClassLabel(
                        names=self.class_labels
                    ),
                }
            ),
            supervised_keys=(
                ImageDataItemLiterals.DEFAULT_IMAGE_KEY,
                ImageDataItemLiterals.DEFAULT_LABEL_KEY,
            ),
            homepage=None,
            citation=None,
            license=None,
            task_templates=[
                ImageClassification(
                    image_column=ImageDataItemLiterals.DEFAULT_IMAGE_KEY,
                    label_column=ImageDataItemLiterals.DEFAULT_LABEL_KEY,
                )
            ],
        )

    def _split_generators(
        self, dl_manager: HFDownloadManager
    ) -> List[datasets.SplitGenerator]:
        """Specify feature dictionary generators and dataset splits. This information is
        used by Builder class to generate custom training examples.

        :param dl_manager: Download manager exposed by HF.
        :type dl_manager: Hugging Face download manager
        :return: List of custom split generators
        :rtype: List[datasets.SplitGenerator]
        """
        # we are using our own download manager not HF download manager
        # as it doesn't support downloading data from MLTable
        # but split generator expect HF dl manager in its arguments

        return [
            datasets.SplitGenerator(
                name=datasets.Split.TRAIN,
                gen_kwargs={
                    "data_dir": self.download_manager._data_dir,
                    "data_frame": self.download_manager._images_df,
                },
            )
        ]

    def _generate_examples(
        self, data_dir: str, data_frame: pd.DataFrame
    ) -> Generator[Tuple[str, Dict[str, Any]], None, None]:
        """Generate images and labels for splits.

        :param data_dir: images download directory.
        :type data_dir: str
        :param data_frame: image dataframe.
        :type data_frame: pandas dataframe
        :return: HF required classification dataset generator
        :rtype: Generator[Tuple[str, Dict[str, Any]], None, None]
        """

        for index in range(len(data_frame)):
            rel_path = data_frame[
                ImageDataFrameConstants.DEFAULT_IMAGE_COLUMN_NAME
            ].iloc[index]
            image_path = os.path.join(data_dir, str(rel_path))
            image = Image.open(image_path).convert("RGB")
            label = data_frame[ImageDataFrameConstants.DEFAULT_LABEL_COLUMN_NAME].iloc[
                index
            ]
            yield image_path, {
                ImageDataItemLiterals.DEFAULT_IMAGE_KEY: {
                    ImageDataItemLiterals.HF_PATH_KEY: image_path,
                    ImageDataItemLiterals.HF_BYTES_KEY: np.asarray(image),
                },
                ImageDataItemLiterals.DEFAULT_LABEL_KEY: label,
            }

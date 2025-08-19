# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Metric computation for image generation."""

import logging
import os

import numpy as np

from typing import Any, Callable, Dict, Iterator, Optional

from azureml.metrics import constants
from azureml.metrics.common import utilities
from azureml.metrics.common.azureml_metrics import AzureMLMetrics
from azureml.metrics.common.exceptions import MetricsException
from azureml.metrics.common.import_utilities import load_image_generation_utilities


class AzureMLImageGenerationMetrics(AzureMLMetrics):
    """Class for computing image generation metrics.

    Delegates to the clean-fid package.
    """

    # Internal name for Inception model.
    INCEPTION_V3 = "inception_v3"

    # Size for center cropping.
    RESIZE_SIZE = 256

    def __init__(
        self,
        log_activity: Optional[
            Callable[[logging.Logger, str, Optional[str], Optional[Dict[str, Any]]], Iterator[Optional[Any]]]
        ] = None,
        log_traceback: Optional[
            Callable[[BaseException, logging.Logger, Optional[str], Optional[bool], Optional[Any]], None]
        ] = None,
    ) -> None:
        """Initialize the Frechet Inception Distance computation object from torchmetrics."""
        super().__init__(log_activity, log_traceback)

        # Import utilities via function that checks availability of relevant packages.
        torch, Image, center_crop, fid = load_image_generation_utilities()

        # Use GPU if available.
        self.device = torch.device("cuda") if torch.cuda.is_available() else torch.device("cpu")

        def center_crop_and_resize(image_np):
            image_pil = Image.fromarray(image_np)

            image_pil = center_crop(image_pil, min(image_pil.size))
            image_pil = image_pil.resize((self.RESIZE_SIZE, self.RESIZE_SIZE), Image.LANCZOS)

            return np.array(image_pil)

        self.image_transform, self.fid = center_crop_and_resize, fid

    def compute(self, y_test: str, y_pred: str) -> Dict[str, Any]:
        """
        Compute image generation metrics, eg the Frechet Inception Distance.

        :param y_test: Name of folder with real images.
        :type y_test: str
        :param y_pred: Name of folder with model generated images.
        :type y_pred: str
        :return: A dictionary mapping metric names to metric values.
        :rtype: Dict[str, Any]
        """

        try:
            # Need at least two real and two generated images.
            def count_files(folder_name):
                return len(
                    [
                        file_name
                        for file_name in os.listdir(folder_name)
                        if os.path.isfile(os.path.join(folder_name, file_name))
                    ]
                )

            if count_files(y_test) < 2:
                raise ValueError("The computation needs at least two real images.")
            if count_files(y_pred) < 2:
                raise ValueError("The computation needs at least two generated images.")

            # Delegate to `clean-fid` package.
            fid_value = self.fid.compute_fid(
                y_test, y_pred, model_name=self.INCEPTION_V3, custom_image_tranform=self.image_transform,
                device=self.device
            )

        except Exception as e:
            raise MetricsException(f"Failed to compute image generation metrics. Exception thrown: <{e}>.")

        metrics = {constants.Metric.FID: fid_value}
        return utilities.segregate_scalar_non_scalar(metrics)

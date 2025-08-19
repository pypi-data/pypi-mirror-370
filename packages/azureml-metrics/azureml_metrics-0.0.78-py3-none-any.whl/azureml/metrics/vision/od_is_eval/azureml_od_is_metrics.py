# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Metric computation for object detection and instance segmentation."""

import logging

from typing import Any, Callable, Dict, Iterator, List, Optional

from azureml.metrics import constants
from azureml.metrics.common import utilities
from azureml.metrics.common.azureml_metrics import AzureMLMetrics

from azureml.metrics.common.exceptions import MissingDependencies


logger = logging.getLogger(__name__)


class AzureMLODISMetrics(AzureMLMetrics):
    """Class for computing object detection and instance segmentation metrics.

    Also supports batch mode computation.
    """

    DEFAULT_IOU_THRESHOLD = 0.5

    def __init__(
        self,
        task_is_detection: bool,
        num_classes: int,
        iou_threshold: float = None,
        metrics: Optional[List[str]] = None,
        log_activity: Optional[
            Callable[[logging.Logger, str, Optional[str], Optional[Dict[str, Any]]], Iterator[Optional[Any]]]
        ] = None,
        log_traceback: Optional[
            Callable[[BaseException, logging.Logger, Optional[str], Optional[bool], Optional[Any]], None]
        ] = None,
    ) -> None:
        """
        Initialize computation of OD/IS metrics.

        :params num_classes: The number of classes in the dataset.
        :params iou_threshold: IOU threshold used when matching ground truth objects with predicted objects.
        :param metrics: list of metrics to be computed
        :param log_activity is a callback to log the activity with parameters
            :param logger: logger
            :param activity_name: activity name
            :param activity_type: activity type
            :param custom_dimensions: custom dimensions
        :param log_traceback is a callback to log exception traces. with parameters
            :param exception: The exception to log.
            :param logger: The logger to use.
            :param override_error_msg: The message to display that will override the current error_msg.
            :param is_critical: If is_critical, the logger will use log.critical, otherwise log.error.
            :param tb: The traceback to use for logging; if not provided,
                        the one attached to the exception is used.
        :return: None
        """

        # Copy the requested metric names.
        self.requested_metric_names = metrics if metrics is not None else AzureMLODMetrics.list_metrics()

        # Make new `IncrementalVocEvaluator` object.
        self.task_is_detection = task_is_detection
        self.num_classes = num_classes
        self.iou_threshold = iou_threshold if iou_threshold is not None else self.DEFAULT_IOU_THRESHOLD
        self.reset()

        super().__init__(log_activity, log_traceback)

    def update_states(self, y_test: List[Dict], image_meta_info: List[Dict], y_pred: List[Dict]) -> Dict[str, Any]:
        """
        Compute intermediate statistics for OD/IS evaluation of an image set.

        :param y_test: Ground truth objects for each image.
        :type y_test: list of dicts with keys "boxes" or "masks", and "classes":
            a. the value for "boxes" is a numpy.ndarray of shape (m, 4): (pixel x1, y1, x2, y2)
            b. the value for "masks" is a list of length m of of dict's representing run length-encoded masks (with
                "counts" key). this is required for instance segmentation only.
            c. the value for "classes" is a numpy.ndarray of shape (m)
        :param y_pred: Predicted objects for each image.
        :type y_pred: list of dicts with keys "boxes" or "masks", "classes" and "scores":
            a. the value for "boxes" is a numpy.ndarray of shape (n, 4): (pixel x1, y1, x2, y2)
            b. the value for "masks" is a list of length n of dict's representing run length-encoded masks (with
                "counts" key)
            c. the value for "classes" is a numpy.ndarray of shape (n)
            d. the value for "scores" is a numpy.ndarray of shape (n)
        :param image_meta_info: Meta information for each image.
        :type image_meta_info: list of dict's that have "iscrowd" key
        """

        self.incremental_voc_evaluator.evaluate_batch(
            gt_objects_per_image=y_test,
            predicted_objects_per_image=y_pred,
            meta_info_per_image=image_meta_info,
        )

    def reset(self):
        """Reset the intermediate statistics."""
        try:
            from azureml.metrics.vision.od_is_eval.incremental_voc_evaluator import IncrementalVocEvaluator

        except (ImportError, MissingDependencies):
            safe_message = "Vision packages are not available. Please run pip install azureml-metrics[image]"
            raise MissingDependencies(
                safe_message, safe_message=safe_message
            )

        self.incremental_voc_evaluator = IncrementalVocEvaluator(
            task_is_detection=self.task_is_detection,
            num_classes=self.num_classes,
            iou_threshold=self.iou_threshold,
        )

    def aggregate_compute(self) -> Dict:
        """
        Evaluate the images seen so far using their intermediate statistics.

        :return: `dict` of metrics
        """

        # Delegate to `IncrementalVocEvaluator` for the computation.
        computed_metrics = self.incremental_voc_evaluator.compute_metrics()

        # Extract the requested metrics.
        requested_metrics = {
            metric_name: computed_metrics[metric_name]
            for metric_name in self.requested_metric_names if metric_name in computed_metrics
        }

        # Divide metrics into scalar and non-scalar.
        return utilities.segregate_scalar_non_scalar(requested_metrics)

    def compute(self, y_test: List[Dict], image_meta_info: List[Dict], y_pred: List[Dict]) -> Dict[str, Any]:
        """
        Evaluate an image set, computing the requested OD/IS metrics.

        :param y_test: Ground truth objects for each image.
        :type y_test: list of dicts with keys "boxes" or "masks", and "classes":
            a. the value for "boxes" is a numpy.ndarray of shape (m, 4): (pixel x1, y1, x2, y2)
            b. the value for "masks" is a list of length m of of dict's representing run length-encoded masks (with
                "counts" key). this is required for instance segmentation only.
            c. the value for "classes" is a numpy.ndarray of shape (m)
        :param y_pred: Predicted objects for each image.
        :type y_pred: list of dicts with keys "boxes" or "masks", "classes" and "scores":
            a. the value for "boxes" is a numpy.ndarray of shape (n, 4): (pixel x1, y1, x2, y2)
            b. the value for "masks" is a list of length n of dict's representing run length-encoded masks (with
                "counts" key)
            c. the value for "classes" is a numpy.ndarray of shape (n)
            d. the value for "scores" is a numpy.ndarray of shape (n)
        :param image_meta_info: Meta information for each image.
        :type image_meta_info: list of dict's that have "iscrowd" key
        """

        # Compute intermediate statistics from the passed ground truth and predictions, deleting any existing
        # intermediate statistics first.
        self.reset()
        self.update_states(y_test=y_test, y_pred=y_pred, image_meta_info=image_meta_info)

        # Compute the metrics by aggregating the intermediate statistics.
        return self.aggregate_compute()


class AzureMLODMetrics(AzureMLODISMetrics):
    """Class for computing object detection metrics."""

    def __init__(
        self,
        num_classes: int,
        iou_threshold: float = None,
        metrics: Optional[List[str]] = None,
        log_activity: Optional[
            Callable[[logging.Logger, str, Optional[str], Optional[Dict[str, Any]]], Iterator[Optional[Any]]]
        ] = None,
        log_traceback: Optional[
            Callable[[BaseException, logging.Logger, Optional[str], Optional[bool], Optional[Any]], None]
        ] = None,
    ) -> None:
        """
        :params num_classes: The number of classes in the dataset.
        :params iou_threshold: IOU threshold used when matching ground truth objects with predicted objects.
        :param metrics: list of metrics to be computed
        :param log_activity is a callback to log the activity with parameters
            :param logger: logger
            :param activity_name: activity name
            :param activity_type: activity type
            :param custom_dimensions: custom dimensions
        :param log_traceback is a callback to log exception traces. with parameters
            :param exception: The exception to log.
            :param logger: The logger to use.
            :param override_error_msg: The message to display that will override the current error_msg.
            :param is_critical: If is_critical, the logger will use log.critical, otherwise log.error.
            :param tb: The traceback to use for logging; if not provided,
                        the one attached to the exception is used.
        :return: None

        Example usage for batch mode:
        -------------------------------
        >>> from azureml.metrics.azureml_od_is_metrics import AzureMLODMetrics
        >>> metric_computer = AzureMLODMetrics(num_classes=num_classes, iou_threshold=iou_threshold)
        >>> for i in range(num_batches):
        >>>   metric_computer.update_states(
                y_test=gt_objects_per_image[i*batch_size:(i+1)*batch_size],
                image_meta_info=image_meta_info_per_image[i*batch_size:(i+1)*batch_size],
                y_pred=predicted_objects_per_image[i*batch_size:(i+1)*batch_size]
              )
        >>> metrics = metric_computer.aggregate_compute()
        """

        super().__init__(
            task_is_detection=True,
            num_classes=num_classes,
            iou_threshold=iou_threshold,
            metrics=metrics,
            log_activity=log_activity,
            log_traceback=log_traceback,
        )

    @staticmethod
    def list_metrics() -> List[str]:
        """Default metric names for object detection.

        :return: List of supported metric names.
        """
        return list(constants.Metric.IMAGE_OBJECT_DETECTION_SET)


class AzureMLISMetrics(AzureMLODISMetrics):
    """Class for computing instance segmentation metrics."""

    def __init__(
        self,
        num_classes: int,
        iou_threshold: float = None,
        metrics: Optional[List[str]] = None,
        log_activity: Optional[
            Callable[[logging.Logger, str, Optional[str], Optional[Dict[str, Any]]], Iterator[Optional[Any]]]
        ] = None,
        log_traceback: Optional[
            Callable[[BaseException, logging.Logger, Optional[str], Optional[bool], Optional[Any]], None]
        ] = None,
    ) -> None:
        """
        :params num_classes: The number of classes in the dataset.
        :params iou_threshold: IOU threshold used when matching ground truth objects with predicted objects.
        :param metrics: list of metrics to be computed
        :param log_activity is a callback to log the activity with parameters
            :param logger: logger
            :param activity_name: activity name
            :param activity_type: activity type
            :param custom_dimensions: custom dimensions
        :param log_traceback is a callback to log exception traces. with parameters
            :param exception: The exception to log.
            :param logger: The logger to use.
            :param override_error_msg: The message to display that will override the current error_msg.
            :param is_critical: If is_critical, the logger will use log.critical, otherwise log.error.
            :param tb: The traceback to use for logging; if not provided,
                        the one attached to the exception is used.
        :return: None

        Example usage for batch mode:
        -------------------------------
        >>> from azureml.metrics.azureml_od_is_metrics import AzureMLISMetrics
        >>> metric_computer = AzureMLISMetrics(num_classes=num_classes, iou_threshold=iou_threshold)
        >>> for i in range(num_batches):
        >>>   metric_computer.update_states(
                y_test=gt_objects_per_image[i*batch_size:(i+1)*batch_size],
                image_meta_info=image_meta_info_per_image[i*batch_size:(i+1)*batch_size],
                y_pred=predicted_objects_per_image[i*batch_size:(i+1)*batch_size]
              )
        >>> metrics = metric_computer.aggregate_compute()
        """

        super().__init__(
            task_is_detection=False,
            num_classes=num_classes,
            iou_threshold=iou_threshold,
            metrics=metrics,
            log_activity=log_activity,
            log_traceback=log_traceback,
        )

    @staticmethod
    def list_metrics() -> List[str]:
        """Default metric names for instance segmentation.

        :return: List of supported metric names.
        """
        return list(constants.Metric.IMAGE_INSTANCE_SEGMENTATION_SET)

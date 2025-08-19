# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Metric computation for multi-object-tracking."""

import logging

from typing import Any, Callable, Dict, Iterator, List, Optional
from azureml.metrics import constants
from azureml.metrics.common import utilities
from azureml.metrics.common.azureml_metrics import AzureMLMetrics
from azureml.metrics.common.import_utilities import load_mmtrack_eval_mot
from azureml.metrics.vision.od_is_eval.azureml_od_is_metrics import AzureMLODMetrics

logger = logging.getLogger(__name__)


class AzureMLMOTMetrics(AzureMLMetrics):
    """Class for computing multi object tracking metrics.

    Also supports batch mode computation.
    """
    DEFAULT_IOU_THRESHOLD = 0.5

    def __init__(
        self,
        num_classes: int,
        iou_threshold: float = None,
        metrics: Optional[List[str]] = None,
        custom_dimensions: Optional[Dict[str, Any]] = None,
        log_activity: Optional[
            Callable[[logging.Logger, str, Optional[str], Optional[Dict[str, Any]]], Iterator[Optional[Any]]]
        ] = None,
        log_traceback: Optional[
            Callable[[BaseException, logging.Logger, Optional[str], Optional[bool], Optional[Any]], None]
        ] = None,
    ) -> None:
        """
        Initialize computation of MOT metrics.

        :params num_classes: The number of classes in the dataset.
        :params iou_threshold: IOU threshold used when matching ground truth objects with predicted objects.
        :param metrics: list of metrics to be computed
        :param custom_dimensions to report the telemetry data.
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
        self.eval_mot = load_mmtrack_eval_mot()
        # Copy the requested metric names.
        self.requested_metric_names = metrics if metrics is not None else AzureMLMOTMetrics.list_metrics()

        # Make new `IncrementalVocEvaluator` object.
        self.num_classes = num_classes
        self.iou_threshold = iou_threshold if iou_threshold is not None else self.DEFAULT_IOU_THRESHOLD

        self.reset()

        self.__custom_dimensions = custom_dimensions
        super().__init__(log_activity, log_traceback)

    def update_states(self, y_test, y_pred, image_meta_info) -> Dict[str, Any]:
        """
        Compute intermediate statistics for MOT evaluation of a video set.

        :param y_test: Ground truth objects for each image.
        :type y_test: dict: Keys of annotations are
            - `bboxes`: numpy array of shape (n, 4)
            - `labels`: numpy array of shape (n, )
            - `instance_ids`: numpy array of shape (n, )
            - `bboxes_ignore` (optional): numpy array of shape (k, 4) k could be 0
        :param y_pred: Predicted objects for each video.
        :type y_pred: list[ndarray]: List indicates categories.
                The ndarray indicates the tracking results, it's of shape (n, 6),
                the 6 columns are [instance_id, x1, y1, x2, y2, score]
        :param image_meta_info: Meta information for each video.
        :type image_meta_info: list of dict's that have "frame_id", "video_name" keys
        """
        self.image_metas.extend(image_meta_info)
        self.predictions.append(y_pred)
        self.gts.append(y_test)

    def reset(self):
        """Reset the intermediate statistics."""

        self.image_metas = []
        self.predictions = []
        self.gts = []

    def eval_mot_name_mapping(self, required_name: str) -> str:
        """Map the metric name to the name used in mmtrack.
           eval_mot function has different name for precision and recall.
           to have unified names in azureml-metrics package, we perform a name mapping.
        """
        name_mapping = {constants.Metric.TRACKING_PRECISION: "Prcn",
                        constants.Metric.TRACKING_RECALL: "Rcll"}
        if required_name not in name_mapping:
            return required_name
        else:
            return name_mapping[required_name]

    def aggregate_compute(self) -> Dict:
        """
        Evaluate the videos seen so far using their intermediate statistics.
        :return: `dict` of metrics
        """
        assert len(self.predictions) == len(self.gts), "Number of predictions and ground truths should be equal."
        assert len(self.predictions) == len(self.image_metas), "Number of predictions and image meta should be equal."

        inds = [
            i for i, _ in enumerate(self.image_metas) if _['frame_id'] == 0
        ]
        num_vids = len(inds)
        inds.append(len(self.image_metas))

        track_bboxes = [
            self.predictions[inds[i]:inds[i + 1]]
            for i in range(num_vids)
        ]
        ann_infos = [
            self.gts[inds[i]:inds[i + 1]] for i in range(num_vids)
        ]
        computed_metrics = self.eval_mot(
            results=track_bboxes,
            annotations=ann_infos,
            logger=logger,
            classes=range(self.num_classes),
            iou_thr=self.iou_threshold)
        # Extract the requested metrics.
        requested_metrics = {
            metric_name: computed_metrics[self.eval_mot_name_mapping(metric_name)]
            for metric_name in self.requested_metric_names
            if self.eval_mot_name_mapping(metric_name) in computed_metrics
        }

        # Divide metrics into scalar and non-scalar.
        return utilities.segregate_scalar_non_scalar(requested_metrics)

    @staticmethod
    def list_metrics() -> List[str]:
        """Default metric names for multi-object-tracking.

        :return: List of supported metric names.
        """
        return list(constants.Metric.VIDEO_MULTI_OBJECT_TRACKING_SET)

    def compute(self, y_test: List[Dict], image_meta_info: List[Dict], y_pred: List[Dict]) -> Dict[str, Any]:
        """
        Evaluate an image set, computing the requested MOT metrics.

        :param y_test: Ground truth objects for each image.
        :type y_test: dict: Keys of annotations are
            - `bboxes`: numpy array of shape (n, 4)
            - `labels`: numpy array of shape (n, )
            - `instance_ids`: numpy array of shape (n, )
            - `bboxes_ignore` (optional): numpy array of shape (k, 4) k could be 0
        :param image_meta_info: Meta information for each video.
        :type image_meta_info: list of dict's that have "frame_id", "video_name" keys
        :param y_pred: Predicted objects for each video.
        :type y_pred: list[ndarray]: List indicates categories.
                The ndarray indicates the tracking results, it's of shape (n, 6),
                the 6 columns are [instance_id, x1, y1, x2, y2, score]
        """

        # Compute intermediate statistics from the passed ground truth and predictions, deleting any existing
        # intermediate statistics first.
        self.reset()
        self.update_states(y_test=y_test, y_pred=y_pred, image_meta_info=image_meta_info)

        # Compute the metrics by aggregating the intermediate statistics.
        return self.aggregate_compute()


class AzureMlMOTODMetrics:
    """Class for computing object detection and multi-object-tracking metrics."""

    def __init__(
        self,
        num_classes: int,
        iou_threshold: float = None,
        metrics: Optional[List[str]] = None,
        custom_dimensions: Optional[Dict[str, Any]] = None,
        log_activity: Optional[
            Callable[[logging.Logger, str, Optional[str], Optional[Dict[str, Any]]], Iterator[Optional[Any]]]
        ] = None,
        log_traceback: Optional[
            Callable[[BaseException, logging.Logger, Optional[str], Optional[bool], Optional[Any]], None]
        ] = None,
    ) -> None:
        """
        Initialize computation of MOT metrics and OD metrics.

        :params num_classes: The number of classes in the dataset.
        :params iou_threshold: IOU threshold used when matching ground truth objects with predicted objects.
        :param metrics: list of metrics to be computed
        :param custom_dimensions to report the telemetry data.
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
        self.od_metrics_computer = AzureMLODMetrics(num_classes, iou_threshold, metrics, log_activity, log_traceback)
        self.mot_metrics_computer = AzureMLMOTMetrics(num_classes, iou_threshold, metrics, custom_dimensions,
                                                      log_activity, log_traceback)

    def update_states(self, od_y_test, od_y_pred, od_image_meta_info,
                      track_y_test, track_y_pred, track_image_meta_info):
        """
        Compute intermediate statistics for MOT evaluation of a video set.

        :param od_y_test: Ground truth objects for each image.
        :type od_y_test: list of dicts with keys "boxes", and "classes":
            a. the value for "boxes" is a numpy.ndarray of shape (m, 4): (pixel x1, y1, x2, y2)
            c. the value for "classes" is a numpy.ndarray of shape (m)
        :param od_y_pred: Predicted objects for each video.
        :type od_y_pred: list of dicts with keys "boxes", "classes" and "scores":
            a. the value for "boxes" is a numpy.ndarray of shape (n, 4): (pixel x1, y1, x2, y2)
                "counts" key)
            c. the value for "classes" is a numpy.ndarray of shape (n)
            d. the value for "scores" is a numpy.ndarray of shape (n)
        :param od_image_meta_info: Meta information for each video.
        :type od_image_meta_info: list of dict's that have "iscrowd" key
        :param track_y_test: Ground truth objects for each video.
        :type track_y_test: dict: Keys of annotations are
            - `bboxes`: numpy array of shape (n, 4)
            - `labels`: numpy array of shape (n, )
            - `instance_ids`: numpy array of shape (n, )
            - `bboxes_ignore` (optional): numpy array of shape (k, 4) k could be 0
        :param track_y_pred: Predicted objects for each video.
        :type track_y_pred: list[ndarray]: List indicates categories.
                The ndarray indicates the tracking results, it's of shape (n, 6),
                the 6 columns are [instance_id, x1, y1, x2, y2, score]
        :param track_image_meta_info: Meta information for each video.
        :type track_image_meta_info: list of dict's that have "frame_id", "video_name" keys
        """
        self.od_metrics_computer.update_states(y_test=od_y_test, y_pred=od_y_pred,
                                               image_meta_info=od_image_meta_info)
        self.mot_metrics_computer.update_states(y_test=track_y_test, y_pred=track_y_pred,
                                                image_meta_info=track_image_meta_info)

    def reset(self):
        """reset for the class"""
        self.od_metrics_computer.reset()
        self.mot_metrics_computer.reset()

    def aggregate_compute(self) -> Dict:
        """Evaluate the videos seen so far using their intermediate statistics.
        :return: `dict` of metrics
        """
        mot_metrics = self.mot_metrics_computer.aggregate_compute()
        od_metrics = self.od_metrics_computer.aggregate_compute()
        od_metrics["metrics"].update(mot_metrics["metrics"])
        od_metrics["artifacts"].update(mot_metrics["artifacts"])
        return od_metrics

    @staticmethod
    def list_metrics() -> List[str]:
        """Default metric names for multi-object-tracking and object detection."""

        return AzureMLODMetrics.list_metrics() + AzureMLMOTMetrics.list_metrics()

    def compute(self, y_test: List[Dict], image_meta_info: List[Dict], y_pred: List[Dict]) -> Dict[str, Any]:
        """
        Evaluate a video set, computing the requested MOT metrics.

        :param y_test: Ground truth objects for each video.
        :type y_test: dict: Keys of annotations are
            - `bboxes`: numpy array of shape (n, 4)
            - `labels`: numpy array of shape (n, )
            - `instance_ids`: numpy array of shape (n, )
            - `bboxes_ignore` (optional): numpy array of shape (k, 4) k could be 0
        :param image_meta_info: Meta information for each video.
        :type image_meta_info: list of dict's that have "frame_id", "video_name" keys
        :param y_pred: Predicted objects for each video.
        :type y_pred: list[ndarray]: List indicates categories.
                The ndarray indicates the tracking results, it's of shape (n, 6),
                the 6 columns are [instance_id, x1, y1, x2, y2, score]
        """

        # Compute intermediate statistics from the passed ground truth and predictions, deleting any existing
        # intermediate statistics first.
        self.mot_metrics_computer.reset()
        self.mot_metrics_computer.update_states(y_test=y_test, y_pred=y_pred, image_meta_info=image_meta_info)

        # Compute the metrics by aggregating the intermediate statistics.
        return self.mot_metrics_computer.aggregate_compute()

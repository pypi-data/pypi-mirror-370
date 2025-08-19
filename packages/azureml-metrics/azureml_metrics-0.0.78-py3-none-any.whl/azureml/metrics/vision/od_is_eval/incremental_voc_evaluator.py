# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Incremental VOC-style evaluation for object detection."""

import itertools
import logging
import numpy as np

from typing import Any, Dict, List

from azureml.metrics.constants import Metric as MetricsLiterals
from azureml.metrics.common.exceptions import MissingDependencies

try:
    from azureml.metrics.vision.od_is_eval.metric_computation_utils import calculate_confusion_matrices, \
        calculate_pr_metrics, match_objects, EPSILON, UNASSIGNED

except ImportError:
    safe_message = "Vision packages are not available. Please run pip install azureml-metrics[image]"
    raise MissingDependencies(
        safe_message, safe_message=safe_message
    )


logger = logging.getLogger(__name__)


class IncrementalVocEvaluator:
    """
    Incremental VOC-style evaluation for object detection and instance segmentation.

    Suggested flow: make new object at beginning of evaluation, call `evaluate_batch()` after each batch, and
    eventually call `compute_metrics()` to get the final evaluation results.
    Users must specify whether the task is object detection or instance segmentation, the number of classes and the
    IOU threshold.
    """

    # Min and max allowed values for the IOU threshold parameter used to decide whether a predicted object matches a
    # ground truth object.
    MIN_IOU_THRESHOLD = 0.1
    MAX_IOU_THRESHOLD = 1.0

    # Constant to mark undefined metric value.
    UNDEFINED_METRIC_VALUE = -1.0

    def __init__(self, task_is_detection: bool, num_classes: int, iou_threshold: float):
        """
        Construct an incremental VOC-style evaluator.

        :params task_is_detection: Whether the task is object detection (True) or instance segmentation (False).
        :type task_is_detection: bool
        :params num_classes: The number of classes in the dataset.
        :type num_classes: int
        :params iou_threshold: IOU threshold used when matching ground truth objects with predicted objects.
        :type iou_threshold: float
        """

        # Copy the flag for task type and the number of classes.
        self._task_is_detection = task_is_detection
        self._num_classes = num_classes

        # Validate the IOU threshold value.
        self._iou_threshold = self._validate_iou_threshold(iou_threshold)

        # Set the type of AP computation to its default value.
        self._use_voc_11_point_metric = False

        # Initialize the number of images that have at least one ground truth object.
        self._num_images_with_gt_objects = 0

        # Initialize the list of (ground truth class, predicted class, predicted score) triplets for the matched
        # ground truth and predicted objects.
        self._all_matched_classes_and_scores = [np.zeros((0, 3), dtype=np.float32)]

        # Initialize per class lists for the number of ground truth objects, the predicted object label (TP/FP/other),
        # the predicted object score, the predicted object image index.
        self._num_gt_objects_per_class = {i: 0 for i in range(num_classes)}
        self._tp_fp_labels_per_class = {i: [np.zeros((0,), dtype=np.uint8)] for i in range(num_classes)}
        self._scores_per_class = {i: [np.zeros((0,))] for i in range(num_classes)}
        self._image_indexes_per_class = {i: [np.zeros((0,), dtype=np.uint32)] for i in range(num_classes)}

        # Initialize the current image index.
        self._current_image_index = 0

    def set_from_others(self, incremental_evaluators: List[Any]) -> None:
        """
        Aggregate the necessary statistics computed by other evaluators and save the result in this evaluator.

        Used when running evaluation in multi-GPU mode, with multiple incremental evaluators running in parallel, on
        different images.

        :param incremental_evaluators: Incremental evaluators that ran in parallel on other images
        :type incremental_evaluators: IncrementalVocEvaluator
        """

        # Calculate the total number of images with ground truth objects.
        self._num_images_with_gt_objects = sum([ie._num_images_with_gt_objects for ie in incremental_evaluators])

        # Accumulate the information on the matched ground truth and predicted objects.
        self._all_matched_classes_and_scores = list(itertools.chain.from_iterable(
            [ie._all_matched_classes_and_scores for ie in incremental_evaluators]
        ))

        # Calculate the offset for each evaluator that must be added to its image indexes in order to obtain overall
        # unique indexes. Eg, if evaluator 0 sees 2 images, evaluator 1 4 and evaluator 2 1, then the offsets will be
        # 0, 2, 6.
        num_images_per_ie = [0] + [ie._current_image_index for ie in incremental_evaluators]
        image_index_offset_per_ie = np.cumsum(num_images_per_ie, dtype=np.uint32)

        # Go through each class and aggregate the necessary statistics (eg sum the number of ground truth objects per
        # class).
        for i in range(self._num_classes):
            self._num_gt_objects_per_class[i] = sum([ie._num_gt_objects_per_class[i] for ie in incremental_evaluators])
            self._tp_fp_labels_per_class[i] = list(itertools.chain.from_iterable(
                [ie._tp_fp_labels_per_class[i] for ie in incremental_evaluators]
            ))
            self._scores_per_class[i] = list(itertools.chain.from_iterable(
                [ie._scores_per_class[i] for ie in incremental_evaluators]
            ))
            self._image_indexes_per_class[i] = list(itertools.chain.from_iterable(
                [
                    [o + a for a in ie._image_indexes_per_class[i]]
                    for ie, o in zip(incremental_evaluators, image_index_offset_per_ie)
                ]
            ))

    def evaluate_batch(
        self,
        gt_objects_per_image: List[Dict[str, Any]],
        predicted_objects_per_image: List[Dict[str, Any]],
        meta_info_per_image: List[Dict[str, Any]],
    ) -> None:
        """
        Compute necessary statistics for evaluating the predicted object boxes/masks in the images of a batch.

        No metric values computed directly, just per-class statistics that can be aggregated after running for all
        batches.

        :param gt_objects_per_image: Ground truth objects for each image.
        :type gt_objects_per_image: list of dicts with keys "boxes" or "masks", and "classes":
            a. the value for "boxes" is a numpy.ndarray of shape (m, 4): (pixel x1, y1, x2, y2)
            b. the value for "masks" is a list of length m of of dict's representing run length-encoded masks (with
                "counts" key)
            c. the value for "classes" is a numpy.ndarray of shape (m)
        :param predicted_objects_per_image: Predicted objects for each image.
        :type predicted_objects_per_image: list of dicts with keys "boxes" or "masks", "classes" and "scores":
            a. the value for "boxes" is a numpy.ndarray of shape (n, 4): (pixel x1, y1, x2, y2)
            b. the value for "masks" is a list of length n of dict's representing run length-encoded masks (with
                "counts" key)
            c. the value for "classes" is a numpy.ndarray of shape (n)
            d. the value for "scores" is a numpy.ndarray of shape (n)
        :param meta_info_per_image: Meta information for each image.
        :type meta_info_per_image: list of dict's that have "iscrowd" key
        """

        # Go through each image and evaluate its predictions.
        for gt_objects, predicted_objects, meta_info in zip(
            gt_objects_per_image, predicted_objects_per_image, meta_info_per_image
        ):
            # Get the ground truth boxes/masks and classes for the current image.
            gt_supports, gt_classes, _ = self._get_supports_classes_maybe_scores(gt_objects, get_scores=False)

            # Get the crowd labels of the ground truth boxes/masks for the current image.
            is_crowd = np.array(meta_info["iscrowd"]).astype(bool)

            # Get the predicted boxes/masks, classes and scores for the current image.
            predicted_supports, predicted_classes, predicted_scores = self._get_supports_classes_maybe_scores(
                predicted_objects, get_scores=True
            )

            # Evaluate the box/mask predictions for the current image.
            self._evaluate_image(
                gt_supports, gt_classes, is_crowd, predicted_supports, predicted_classes, predicted_scores
            )

    def compute_metrics(self) -> Dict[str, Any]:
        """
        Compute metrics for the batches seen so far.

        Aggregates the necessary statistics computed for each batch.

        :return: mAP, highest recall, precision at highest recall + per label AP, highest recall and precision at
            highest recall + image level AP, highest recall and precision at highest recall + confusion matrices at
            representative score thresholds
        :rtype: dict with precision, recall, mean_average_precision, per_label_metrics, image_level_binary_classifier,
            confusion_matrices_per_score_thresholds keys
        """

        # Initialize the per class metrics to empty.
        metrics_per_class = {}

        # Initialize the lists with all labels, scores and image indexes of predicted objects.
        all_tp_fp_labels = []
        all_scores = []
        all_image_indexes = []

        # Go through each class and calculate the metrics for its objects (e.g. AP).
        for c in range(self._num_classes):
            # Get the labels and scores of predicted objects across all images.
            tp_fp_labels = np.concatenate(self._tp_fp_labels_per_class[c])
            scores = np.concatenate(self._scores_per_class[c])

            # Calculate metrics for the objects in the current class.
            metrics_per_class[c] = calculate_pr_metrics(
                self._num_gt_objects_per_class[c], tp_fp_labels, scores, None,
                self._use_voc_11_point_metric, self.UNDEFINED_METRIC_VALUE
            )

            if self._task_is_detection:
                # Accumulate the per class lists with all labels, scores and image indexes of predicted objects.
                all_tp_fp_labels.extend(self._tp_fp_labels_per_class[c])
                all_scores.extend(self._scores_per_class[c])
                all_image_indexes.extend(self._image_indexes_per_class[c])

        # Calculate the mean over all classes for the last precision, last recall and AP (=>mAP) metrics.
        object_level_metrics = {
            MetricsLiterals.PER_LABEL_METRICS: metrics_per_class,
            MetricsLiterals.PRECISION: self._calculate_metric_mean_over_classes(
                metrics_per_class, MetricsLiterals.PRECISION
            ),
            MetricsLiterals.RECALL: self._calculate_metric_mean_over_classes(
                metrics_per_class, MetricsLiterals.RECALL
            ),
            MetricsLiterals.MEAN_AVERAGE_PRECISION: self._calculate_metric_mean_over_classes(
                metrics_per_class, MetricsLiterals.AVERAGE_PRECISION
            )
        }

        if self._task_is_detection:
            # Image level metrics and confusion matrices for object detection.

            # Calculate the image level metrics.
            image_level_metrics = {
                MetricsLiterals.IMAGE_LEVEL_BINARY_CLASSIFIER_METRICS: calculate_pr_metrics(
                    self._num_images_with_gt_objects,
                    np.concatenate([np.zeros((0,), dtype=np.uint8)] + all_tp_fp_labels),
                    np.concatenate([np.zeros((0,))] + all_scores),
                    np.concatenate([np.zeros((0,), dtype=np.uint32)] + all_image_indexes),
                    False,
                    self.UNDEFINED_METRIC_VALUE
                )
            }

            # Calculate the confusion matrices at representative scores.
            confusion_matrix_metrics = {
                MetricsLiterals.CONFUSION_MATRICES_PER_SCORE_THRESHOLD: calculate_confusion_matrices(
                    self._num_gt_objects_per_class,
                    np.concatenate([np.zeros((0, 3), dtype=np.float32)] + self._all_matched_classes_and_scores)
                )
            }

        else:
            # No image level metrics or confusion matrices for instance segmentation.
            image_level_metrics = {}
            confusion_matrix_metrics = {}

        return {**object_level_metrics, **image_level_metrics, **confusion_matrix_metrics}

    def _get_supports_classes_maybe_scores(self, objects, get_scores):
        """
        Extract the object boxes/masks, classes and possibly scores.

        The objects parameter had been passed to `evaluate_batch()`.
        """

        if self._task_is_detection:
            # Get boxes, classes and scores for object detection.
            if (len(objects) > 0) and (objects.get("boxes") is not None) and (len(objects["boxes"]) > 0):
                # Get boxes and convert from xyxy to xywh format.
                boxes = np.array(objects["boxes"], copy=True)
                boxes[:, 2] -= boxes[:, 0]
                boxes[:, 3] -= boxes[:, 1]

                # Get classes.
                classes = objects["classes"]

                # Get scores, if present.
                scores = objects["scores"] if get_scores else None

            else:
                # No objects.
                boxes, classes = np.zeros((0, 4)), np.zeros((0,))
                scores = np.zeros((0,)) if get_scores else None

            return boxes, classes, scores

        # Get masks, classes and scores for instance segmentation.
        if (len(objects) > 0) and (objects.get("masks") is not None) and (len(objects["masks"]) > 0):
            # Get masks.
            masks = objects["masks"]

            # Get classes.
            classes = objects["classes"]

            # Get scores, if present.
            scores = objects["scores"] if get_scores else None

        else:
            # No objects.
            masks, classes = [], np.zeros((0,))
            scores = np.zeros((0,)) if get_scores else None

        return masks, classes, scores

    def _validate_iou_threshold(self, iou_threshold):
        """
        Make the iou threshold value sane if it's not.

        :param iou_threshold: Arbitrary IOU threshold value.
        :type iou_threshold: float
        :return: Validated IOU threshold value.
        :rtype: float
        """

        if (iou_threshold < self.MIN_IOU_THRESHOLD) or (iou_threshold > self.MAX_IOU_THRESHOLD):
            logger.info(
                "Clamping IOU threshold for validation to [{}, {}] interval.".format(
                    self.MIN_IOU_THRESHOLD, self.MAX_IOU_THRESHOLD
                )
            )

        return max(self.MIN_IOU_THRESHOLD, min(self.MAX_IOU_THRESHOLD, iou_threshold))

    def _evaluate_image(
        self, gt_supports, gt_classes, is_crowd, predicted_supports, predicted_classes, predicted_scores
    ):
        """
        Compute necessary statistics for evaluating the objects predicted in an image.

        The per class statistics are: number of ground truth objects, TP/FP/other labels for predicted objects, scores
        for predicted objects, image indexes for predicted objects. The global statistic is the number of images with
        ground truth objects.

        :param gt_supports: Ground truth object supports (boxes or masks) for an image.
        :type gt_supports: numpy.ndarray of shape (m, 4): (pixel x1, y1, w, h) or list of length n of dict's
            representing run length-encoded masks (with "counts" key)
        :param gt_classes: Classes for the ground truth objects for an image.
        :type gt_classes: numpy.ndarray of shape (m,)
        :param is_crowd: Crowd attribute for the ground truth objects for an image.
        :type is_crowd: numpy.ndarray of shape (m,)
        :param predicted_supports: Predicted object supports (boxes or masks) for an image.
        :type predicted_supports: numpy.ndarray of shape (n, 4): (pixel x1, y1, w, h) or list of length n of dict's
            representing run length-encoded masks (with "counts" key)
        :param predicted_classes: Classes for the predicted objects for an image.
        :type predicted_classes: numpy.ndarray of shape (n)
        :param predicted_scores: Scores for the predicted objects for an image.
        :type predicted_scores: numpy.ndarray of shape (n)
        :return: None
        """

        # Initialize the number of ground truth objects in this image to 0.
        num_gt_objects_current_image = 0

        # Go through each class and extract the statistics necessary to evaluate the predictions for that class.
        for c in range(self._num_classes):
            # Get indicators for the ground truth and the predicted objects for the current class.
            gt_indicator_class = gt_classes == c
            predicted_indicator_class = predicted_classes == c

            # Using both box coordinates/masks and scores, match the predicted objects with the ground truth objects
            # for the current class. Assign a label of TP/FP/other to each prediction based on the match.
            tp_fp_labels, _ = match_objects(
                self._select_supports(gt_supports, gt_indicator_class),
                is_crowd[gt_indicator_class],
                self._select_supports(predicted_supports, predicted_indicator_class),
                predicted_scores[predicted_indicator_class],
                self._iou_threshold
            )

            # Get the number of ground truth objects, the predicted object scores and the predicted object image
            # indexes for the current class.
            num_gt_objects = np.sum(~is_crowd[gt_indicator_class])
            scores = predicted_scores[predicted_indicator_class]
            image_indexes = np.full((len(scores),), self._current_image_index, dtype=np.uint32)

            # Update the number of ground truth objects for the current image.
            num_gt_objects_current_image += num_gt_objects

            # Update for the current class: a. the number of ground truth objects; b. the list of tp/fp/other labels;
            # c. the list of scores; d. the list of image indexes.
            self._num_gt_objects_per_class[c] += num_gt_objects
            self._tp_fp_labels_per_class[c].append(tp_fp_labels)
            self._scores_per_class[c].append(scores)
            self._image_indexes_per_class[c].append(image_indexes)

        # Match all the ground truth objects with all the predicted objects in the image, without using their classes.
        _, predicted_assignment = match_objects(
            gt_supports, is_crowd, predicted_supports, predicted_scores, self._iou_threshold
        )
        mask = predicted_assignment != UNASSIGNED
        matched_classes_and_scores = np.transpose(np.stack(
            (gt_classes[predicted_assignment[mask]], predicted_classes[mask], predicted_scores[mask])
        ))
        self._all_matched_classes_and_scores.append(matched_classes_and_scores)

        # If there is at least one ground truth object in this image, then increment the number of images with ground
        # truth objects.
        self._num_images_with_gt_objects += min(1, num_gt_objects_current_image)

        # Increment the current image index.
        self._current_image_index += 1

    def _select_supports(self, supports, indicator):
        """
        Select object supports according to indicator.

        :param supports: Object supports (boxes or masks) for an image.
        :type supports: numpy.ndarray of shape (n, 4): (pixel x1, y1, w, h) or list of length n of dict's representing
            run length-encoded masks (with "counts" key)
        :param indicator: Indicator for the objects for an image.
        :type indicator: numpy.ndarray of shape (n) of boolean's
        :return: Selected object supports (boxes or masks) for an image.
        :rtype: numpy.ndarray of shape (k, 4): (pixel x1, y1, w, h) or list of length k of dict's representing
            run length-encoded masks (with "counts" key)
        """

        if self._task_is_detection:
            return supports[indicator]

        return [s for s, i in zip(supports, indicator) if i]

    def _calculate_metric_mean_over_classes(self, metrics_per_class, metric_name):
        """
        Average a metric's values over all classes.

        :param metrics_per_class: PR metrics by class.
        :type metrics_per_class: dict from int to PR metrics
        :param metric_name: One of the PR metrics, eg. "precision".
        :type metric_name: str
        :return: Mean metric value.
        :rtype: float
        """

        # Get the list of values of a metric across classes.
        values = [metrics_per_class[c][metric_name] for c in range(self._num_classes)]

        # Calculate the mean of valid values.
        valid_values = [v for v in values if v != self.UNDEFINED_METRIC_VALUE]
        average_value = sum(valid_values) / (len(valid_values) + EPSILON)

        return average_value

# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Implementation details: mAP score computation functions."""

import logging
import numpy as np

from azureml.metrics.constants import Metric as MetricsLiterals
from azureml.metrics.common.exceptions import ValidationException
from azureml.metrics.common.exceptions import MissingDependencies


# Codes for TP, FP, other.
_TP_CODE, _FP_CODE, _OTHER_CODE = 1, 0, 2

# Score thresholds at which to compute confusion matrices.
_SCORE_THRESHOLDS = [(i / 10.0) for i in range(10)]

# Code for predicted objects not assigned to ground truth objects.
UNASSIGNED = -1

# Constant to avoid division by 0.
EPSILON = 1E-9


logger = logging.getLogger(__name__)


def _map_score_voc_11_point_metric(precision_list, recall_list):
    """
    Compute mAP score using Voc 11 point metric.

    The maximum precision at 11 recall values (0, 0.1, ..., 1.0) is computed and the average of these precision
    values is used as the mAP score.
    precision_list and recall_list should have same dimensions.

    :param precision_list: List of precision values
    :type precision_list: <class 'numpy.ndarray'> of shape (number of precision values)
    :param recall_list: List of recall values
    :type precision_list: <class 'numpy.ndarray'> of shape (number of recall values)
    :return: mAP score computed
    :rtype: <class 'numpy.ndarray'> of shape ()
    """

    # Check that the precision and recall lists are of the same length.
    if precision_list.shape != recall_list.shape:
        msg = "Precision list (shape {}) and recall list (shape {}) are not of same length. " \
              "Cannot compute map score".format(precision_list.shape, recall_list.shape)
        logger.error(msg)
        raise ValidationException(msg, has_pii=False)

    # Iterate over 11 recall thresholds and sum up the precision values for them.
    sum_precisions = 0.0
    for recall_threshold in np.arange(0.0, 1.1, 0.1):
        # Get the PR curve points with recall greater than the current threshold.
        mask_recall_above_threshold = recall_list >= recall_threshold

        # If points exist, add maximum precision to running sum of precisions.
        if mask_recall_above_threshold.any():
            precisions_recall_above_threshold = precision_list[mask_recall_above_threshold]
            sum_precisions += np.max(precisions_recall_above_threshold)

    # Calculate the AUC for the PR curve via the 11 recall thresholds.
    auc = sum_precisions / 11.0

    return auc


def _map_score_voc_auc(precision_list, recall_list):
    """
    Compute mAP score using Voc Area Under Curve (auc) metric.

    The recall values at which maximum precision changes are identified and these points of change are used
    to compute the area under precision recall curve.
    precision_list and recall_list should have the same length.

    :param precision_list: List of precision values
    :type precision_list: <class 'numpy.ndarray'> of shape (number of precision values)
    :param recall_list: List of recall values
    :type precision_list: <class 'numpy.ndarray'> of shape (number of recall values)
    :return: mAP score computed.
    :rtype: <class 'numpy.ndarray'> of shape ()
    """

    # Check that the precision and recall lists are of the same length.
    if precision_list.shape != recall_list.shape:
        msg = "Precision list (shape {}) and recall list (shape {}) are not of same length. " \
              "Cannot compute map score".format(precision_list.shape, recall_list.shape)
        logger.error(msg)
        raise ValidationException(msg, has_pii=False)

    # Add precision 1 at recall 0.
    precision_list = np.concatenate((np.array([1.0]), precision_list))
    recall_list = np.concatenate((np.array([0.0]), recall_list))

    # Verify that the recalls are sorted.
    recall_delta = recall_list[1:] - recall_list[:-1]
    if np.any(recall_delta < 0):
        msg = "Recall list is not sorted in ascending order. Cannot compute map score using auc."
        logger.error(msg)
        raise ValidationException(msg, has_pii=False)

    # TODO: use precision instead of max precision to the right. (investigate, propose, implement)
    # Calculate the maximum precision over the points on the curve to the right of the current point. Mathematically,
    # calculate vector p' with p'_i = max{j>=i}{p_j} .
    precision_invcummax = np.maximum.accumulate(precision_list[::-1])[::-1]

    # Calculate the AUC for the PR curve via rectangular integration.
    auc = np.sum(precision_invcummax[1:] * (recall_list[1:] - recall_list[:-1]))

    return auc


def match_objects(gt_supports, is_crowd, predicted_supports, predicted_scores, iou_threshold):
    """
    Match ground truth object supports with predicted object supports based on IOU and predicted scores.

    Assign predicted objects to ground truth objects and based on this assignment and the `is_crowd` information,
    compute a label (TP/FP/other) for each predicted object.

    :param gt_supports: Ground truth object supports (boxes or masks) for an image.
    :type gt_supports: numpy.ndarray of shape (m, 4): (pixel x1, y1, w, h) or list of length m of dict's representing
        run length-encoded masks (with "counts" key)
    :param is_crowd: Whether the ground truth objects represent crowd objects.
    :type is_crowd: numpy.ndarray of shape (m)
    :param predicted_supports: Predicted object supports (boxes or masks) for an image.
    :type predicted_supports: numpy.ndarray of shape (n, 4): (pixel x1, y1, w, h) or list of length n of dict's
        representing run length-encoded masks (with "counts" key)
    :param predicted scores: Predicted scores.
    :type predicted_scores: numpy.ndarray of shape (n)
    :param iou_threshold: IOU threshold for deciding whether two objects match.
    :type iou_threshold: float
    :return: For each predicted object, a TP/FP/other label and the index of the assigned ground truth object/an
        invalid index if unassigned.
    :rtype: two numpy.ndarray's of shape (n) with int codes
    """
    try:
        from pycocotools import mask as pycoco_mask

    except ImportError:
        safe_message = "Vision packages are not available. Please run pip install azureml-metrics[image]"
        raise MissingDependencies(
            safe_message, safe_message=safe_message
        )

    # Get the number of ground truth and predicted objects.
    m, n = len(gt_supports), len(predicted_supports)

    # Initialize the TP/FP/other label vector to all FP and the ground truth index vector to all invalid.
    tp_fp_labels = _FP_CODE * np.ones((n,), dtype=np.uint8)
    predicted_assignment = UNASSIGNED * np.ones((n,), dtype=np.int32)
    if (m == 0) or (n == 0):
        # All false positives (n > 0, m=0) or no predictions (n=0, m does not matter).
        return tp_fp_labels, predicted_assignment

    # Calculate an nxm matrix of IOUs for the predicted objects and ground truth objects.
    ious = pycoco_mask.iou(predicted_supports, gt_supports, is_crowd)

    # Calculate the indexes that sort the predicted objects descending by score and the index of the ground truth
    # object with the highest IOU given a predicted object.
    predicted_indexes = np.argsort(predicted_scores)[::-1]
    gt_indexes_max = np.argmax(ious, axis=1)

    # TODO: investigate alternative assignments: from ground truth objects to predicted objects, Hungarian.

    # Assign predicted objects to ground truth objects greedily: go through predicted objects in decreasing order of
    # scores and for each object assign the ground truth object with highest IOU with it.
    gt_assigned = np.zeros((m,), dtype=bool)
    for predicted_index, gt_index in zip(predicted_indexes, gt_indexes_max[predicted_indexes]):
        # Check that the IOU is above the threshold.
        if ious[predicted_index, gt_index] >= iou_threshold:
            # Check that ground truth object is not marked as crowd.
            if not is_crowd[gt_index]:
                # Check that the ground truth object has not been assigned to a predicted object yet.
                if not gt_assigned[gt_index]:
                    # The predicted object is true positive. Mark the ground truth object as assigned.
                    tp_fp_labels[predicted_index] = _TP_CODE
                    gt_assigned[gt_index] = True
                    predicted_assignment[predicted_index] = gt_index
            else:
                # The predicted object is neither true positive nor false positive.
                tp_fp_labels[predicted_index] = _OTHER_CODE

    return tp_fp_labels, predicted_assignment


def calculate_pr_metrics(m, tp_fp_labels, scores, image_indexes, use_voc_11_point_metric, undefined_value):
    """
    Calculate AP, highest recall and precision at highest recall given TP/FP labels, scores and image indexes.

    If the image indexes are set to `None`, then the regular object level metrics are computed. If valid image indexes
    are provided, then the image level metrics are computed.

    :param m: Number of ground truth objects/images with ground truth objects.
    :type m: int
    :param tp_fp_labels: Labels for predicted objects.
    :type tp_fp_labels: numpy.ndarray
    :param scores: Scores for predicted objects.
    :type scores: numpy.ndarray
    :param image_indexes: The indexes of the images the predicted objects belong to.
    :type image_indexes: Optional[numpy.ndarray]
    :param use_voc_11_point_metric: Whether to use the 11 point computation style.
    :type use_voc_11_point_metric: bool
    :param undefined_value: Value to use when a metric is undefined.
    :type undefined_value: float
    :return: AP, highest recall, precision@highest recall.
    :rtype: dict with precision, recall, AP
    """

    if image_indexes is None:
        # Get the number of predicted objects.
        n = len(tp_fp_labels)
    else:
        # Get the number of images with predicted objects.
        n = len(np.unique(image_indexes))

    # If there are no ground truth objects/images with ground truth objects and no predicted objects/images with
    # predicted objects, AP, precision and recall are undefined.
    if (m == 0) and (n == 0):
        return {
            MetricsLiterals.AVERAGE_PRECISION: undefined_value,
            MetricsLiterals.PRECISION: undefined_value,
            MetricsLiterals.RECALL: undefined_value
        }
    # If there are no ground truth objects/images with ground truth objects but predicted objects/images with predicted
    # objects exist, AP and recall are undefined and precision is 0.
    if m == 0:
        return {
            MetricsLiterals.AVERAGE_PRECISION: undefined_value,
            MetricsLiterals.PRECISION: 0.0,
            MetricsLiterals.RECALL: undefined_value
        }
    # If ground truth objects/images with ground truth objects exist but there are no predicted objects/images with
    # predicted objects, AP and recall are 0 and precision is undefined.
    if n == 0:
        return {
            MetricsLiterals.AVERAGE_PRECISION: 0.0,
            MetricsLiterals.PRECISION: undefined_value,
            MetricsLiterals.RECALL: 0.0
        }

    # Get the predictions in decreasing order by score.
    indexes_scores_decreasing = np.argsort(scores)[::-1]
    labels_sorted_by_score_desc = tp_fp_labels[indexes_scores_decreasing]

    if image_indexes is None:
        # Count the true positive and the false positive objects for each score threshold.
        cum_tp = np.cumsum(labels_sorted_by_score_desc == _TP_CODE)
        cum_fp = np.cumsum(labels_sorted_by_score_desc == _FP_CODE)

    else:
        # Get the image indexes in decreasing order by score.
        image_indexes_sorted_by_score_desc = image_indexes[indexes_scores_decreasing]

        # Count the true positive and the false positive images for each score threshold. This has to be done in a for
        # loop with custom logic to obtain the image counts from object level information.

        # Initialize the counts to all zero and sets of images to empty.
        cum_tp = np.zeros((len(image_indexes),))
        cum_fp = np.zeros((len(image_indexes),))
        tp_images = set()
        fp_images = set()

        # Go through each score threshold and incrementally update the sets of true positive and false positive images.
        for k, (c, i) in enumerate(zip(labels_sorted_by_score_desc, image_indexes_sorted_by_score_desc)):
            # Update the sets of true positives and false positives: if at least one true positive object exists in an
            # image, then the image becomes a true positive. If only false positive objects are present, then the image
            # is a false positive.
            if c == _TP_CODE:
                tp_images.add(i)
                fp_images.discard(i)
            elif c == _FP_CODE:
                if i not in tp_images:
                    fp_images.add(i)
            # Get the counts from the sets.
            cum_tp[k] = len(tp_images)
            cum_fp[k] = len(fp_images)

    # Calculate the precision and the recall values for each score threshold.
    precisions = cum_tp / (cum_tp + cum_fp + EPSILON)
    recalls = cum_tp / m

    # Calculate the area under the PR curve.
    if use_voc_11_point_metric:
        average_precision = _map_score_voc_11_point_metric(precisions, recalls)
    else:
        average_precision = _map_score_voc_auc(precisions, recalls)

    # TODO: add F1 score.
    return {
        MetricsLiterals.AVERAGE_PRECISION: average_precision,
        MetricsLiterals.PRECISION: precisions[-1],
        MetricsLiterals.RECALL: recalls[-1]
    }


def calculate_confusion_matrices(num_gt_objects_per_class, matched_classes_and_scores):
    """Calculate the confusion matrices at fixed score thresholds.

    The confusion matrix is of size Cx(C+1) where C is the number of classes. The element at (i,j) where j<=C
    represents the number of ground truth objects of class i that have been predicted to be of class j. The last column
    (j=C+1) has the number of missed objects per class. The score thresholds are 0.0, 0.1, ..., 0.9.

    :param num_gt_objects_per_class: The number of ground truth objects per class.
    :type num_gt_objects_per_class: Union[List[int], Dict[int, int], numpy.ndarray]
    :param matched_classes_and_scores: Information on the matched ground truth and predicted objects, ie list of
        (ground truth class, predicted class, predicted score) triplets.
    :type matched_classes_and_scores: <class 'numpy.ndarray'> of shape (number of matches,3)
    :return: map from score thresholds to confusion matrices
    :rtype: Dict[float, List[List[int]]]
    """

    # Initialize the confusion matrix to all zeros except the last column, which has the number of ground truth objects
    # per class.
    num_classes = len(num_gt_objects_per_class)
    confusion_matrix = np.concatenate((
        np.zeros((num_classes, num_classes), dtype=np.uint32),
        np.expand_dims(np.array([num_gt_objects_per_class[c] for c in range(num_classes)], dtype=np.uint32), 1)
    ), axis=1)

    # If no ground truth objects are matched to predicted objects, then just return the initial confusion matrix.
    if len(matched_classes_and_scores) == 0:
        return {-1.0: confusion_matrix.tolist()}

    # Sort the matches in descending order of scores.
    indexes_scores_decreasing = np.argsort(matched_classes_and_scores[:, 2])
    matched_classes_and_scores = matched_classes_and_scores[indexes_scores_decreasing, :]

    # Go through the score thresholds in descending order and through the matches in descending order of score.
    confusion_matrices_per_score_threshold = {}
    score_index = len(matched_classes_and_scores) - 1
    for score_threshold in sorted(_SCORE_THRESHOLDS, reverse=True):
        # Update the confusion matrix with the matches with score >= the current score threshold.
        while score_index >= 0:
            # Get the ground truth object class, predicted object class and score.
            gt_class, predicted_class, score = matched_classes_and_scores[score_index]
            gt_class, predicted_class = int(gt_class), int(predicted_class)

            # The matches with scores less than the score threshold do not count towards the confusion matrix for the
            # score threshold.
            if score < score_threshold:
                break

            # Increment the confusion matrix element for the ground truth and predicted object classes. Decrement the
            # last column element for the ground truth class, as the number of missed objects for it decreases by one.
            confusion_matrix[gt_class, predicted_class] += 1
            confusion_matrix[gt_class, -1] -= 1

            # Move to the previous match by score.
            score_index -= 1

        # Take a snapshot of the confusion matrix and map it to the current score threshold.
        confusion_matrices_per_score_threshold[score_threshold] = confusion_matrix.tolist()

    return confusion_matrices_per_score_threshold

# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
# Source for BERT Score: https://github.com/huggingface/evaluate/blob/main/metrics/bertscore/bertscore.py
# Copyright 2020 The HuggingFace Datasets Authors and the current dataset script contributor.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


"""Definitions for Question/Answering metrics with multiple ground truth."""
import logging

from typing import Any

from azureml.metrics.common._metric_base import ScalarMetric
from azureml.metrics.text.qa._seq2seq_qa import ExactMatch, F1Score, Seq2SeqQAMetric

logger = logging.getLogger(__name__)


class MacroAveragedExactMatch(Seq2SeqQAMetric, ScalarMetric):
    """ExactMatch metric for Sequence to Sequence Question Answering Tasks"""

    """
    Function is similar to exact_match_score(a_gold, a_pred) with modifications
    Modified from
    https://github.com/huggingface/evaluate/blob/main/metrics/squad_v2/compute_score.py
    """

    def compute(self) -> Any:
        """Compute the score for ExactMatch metric"""
        exact_match_score = 0
        for prediction, reference_list in zip(self.y_pred, self.y_test):
            exact_match_score += self.metric_max_over_references(ExactMatch.exact_match_score,
                                                                 prediction, reference_list)

        exact_match_score = 100 * exact_match_score / len(self.y_pred)

        return exact_match_score


class MacroAveragedF1(Seq2SeqQAMetric, ScalarMetric):
    """F1 score metric for Sequence to Sequence Question Answering Tasks with multiple ground truth"""

    """
    Function is similar to f1_score(a_gold, a_pred) with modifications
    Modified from
    https://github.com/huggingface/evaluate/blob/main/metrics/squad_v2/compute_score.py
    """

    def compute(self) -> Any:
        """Compute the score for F1 score metric"""
        f1_score = 0
        for prediction, reference_list in zip(self.y_pred, self.y_test):
            f1_score += self.metric_max_over_references(F1Score.f1_score, prediction, reference_list)

        f1_score = 100 * f1_score / len(self.y_pred)

        return f1_score

# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
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

"""Definitions for Groundedness QA metrics."""
import logging
import numpy as np

from typing import Any

from azureml.metrics.common._metric_base import NonScalarMetric
from azureml.metrics.rai.groundedness._groundedness_base import GroundednessBase
from azureml.metrics import constants

logger = logging.getLogger(__name__)


class LLMGroundednessQA(GroundednessBase, NonScalarMetric):
    """Groundedness metric for question answering"""

    def compute(self) -> Any:
        """compute the score for LLMGroundedness metric"""
        if self.check_kwargs(constants.Metric.LLMGroundedness) == "nan":
            return [float(np.nan) for _ in range(len(self.generated_contents))]

        prompt_list = []

        for context, generated_content in zip(self.contexts, self.generated_contents):
            prompt = self.construct_user_prompts(context, generated_content)
            prompt_list.append(prompt)

        results_raw = self.llm_url_connector.get_llm_prediction(prompt_list)
        logger.debug("llm groundedness results : {}".format(results_raw))

        # post process
        results = self.post_process(results_raw)
        return results

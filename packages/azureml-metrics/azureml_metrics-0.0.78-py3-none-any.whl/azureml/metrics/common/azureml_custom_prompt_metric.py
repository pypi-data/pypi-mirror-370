# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Definition for AzureMLCustomPromptMetrics class."""
import asyncio
import logging
import sys
import numpy as np
import pandas as pd
from typing import Optional, List

from azureml.metrics.common._metric_base import NonScalarMetric
from azureml.metrics.common.exceptions import MissingDependencies
from azureml.metrics.common.import_utilities import load_nest_asyncio, load_jinja2_template
from azureml.metrics import constants

logger = logging.getLogger(constants.TelemetryConstants.APP_NAME)


class AzureMLCustomPromptMetric(NonScalarMetric):
    """Class for custom prompt metric."""

    def __init__(self,
                 *,
                 metric_name: str,
                 metric_description: str = None,
                 prompt_instruction: str = None,
                 few_shot_examples: str = None,
                 placeholder_prompt: str = None,
                 user_prompt_template: str = None,
                 input_vars: List[str] = None,
                 system_prompt_template: str = constants.DefaultValues.DEFAULT_SYSTEM_PROMPT,
                 custom_prompt_data: pd.DataFrame = None,
                 openai_api_batch_size: Optional[int] = 20,
                 use_openai_endpoint: Optional[bool] = False,
                 openai_params: Optional[dict] = None,
                 use_chat_completion_api: Optional[bool] = None,
                 **kwargs) -> None:
        """
        Initializes an instance of the AzureML Custom Prompt Metric.

        Args:
            metric_name (str): The metric_name of the metric.
            metric_description (str, optional): The description of the metric. Defaults to None.
            prompt_instruction (str, optional): The instruction for the prompt. Defaults to None.
            few_shot_examples (str, optional): Few-shot examples for the prompt. Defaults to None.
            placeholder_prompt (str, optional): The placeholder prompt. Defaults to None.
            user_prompt_template (str, optional): The template for the user prompt. Defaults to None.
            input_vars (List[str], optional): The list of input variables. Defaults to None.
            system_prompt_template (str, optional): The template for the system prompt.
                Defaults to constants.DefaultValues.DEFAULT_SYSTEM_PROMPT
            openai_api_batch_size (int, optional): The batch size for the OpenAI API. Defaults to 20.
            use_openai_endpoint (bool, optional): Flag to indicate whether to use the OpenAI endpoint.
            openai_params (dict, optional): Additional parameters for the OpenAI connector. Defaults to None.
            use_chat_completion_api (bool, optional): Flag to indicate whether to use the chat completion API.
                Defaults to None.
            **kwargs: Additional keyword arguments.

        Raises:
            MissingDependencies: If the relevant GPT Star metrics packages are not available.

        """
        try:
            from azureml.metrics.common.llm_connector._openai_connector import OpenAIConnector
        except ImportError:
            safe_message = "Relevant GPT Star metrics packages are not available. " \
                           "Please run pip install azureml-metrics[prompt-flow]"
            raise MissingDependencies(
                safe_message, safe_message=safe_message
            )

        self.metric_name = metric_name
        self.metric_description = metric_description
        self.prompt_instruction = prompt_instruction
        self.few_shot_examples = few_shot_examples
        self.placeholder_prompt = placeholder_prompt
        self.user_prompt_template = user_prompt_template
        self.input_vars = input_vars
        self.system_prompt_template = system_prompt_template
        self.custom_prompt_data = custom_prompt_data
        self.openai_api_batch_size = openai_api_batch_size
        self.use_openai_endpoint = use_openai_endpoint
        self.openai_params = openai_params
        self.use_chat_completion_api = use_chat_completion_api
        self.kwargs = kwargs
        self.metric_computation_status = "NOT_STARTED"

        if self.metric_name in constants.Metric.NONSCALAR_FULL_SET:
            custom_artifact_name = constants.MetricExtrasConstants.CustomPromptMetricSuffix.format(self.metric_name)
            logger.info("Renaming custom metric from {} to {} due to the conflict with built"
                        " it metric. ".format(self.metric_name, custom_artifact_name))
            self.metric_name = custom_artifact_name

        self.custom_metric_results = {
            constants.Metric.Metrics: {},
            constants.Metric.Artifacts: {
                self.metric_name: np.nan
            }
        }
        self._create_user_prompt_template()
        self.openai_connector = OpenAIConnector(self.openai_params, self.openai_api_batch_size,
                                                self.use_chat_completion_api, llm_state=None,
                                                compute_custom_metric=True,
                                                use_openai_endpoint=self.use_openai_endpoint)
        super().__init__()

    def _create_user_prompt_template(self):
        """
        Creates the user prompt template by combining the prompt instruction, few-shot examples,
        and placeholder prompt.

        Returns:
            str: The user prompt template.
        """
        if self.user_prompt_template is None:
            self.user_prompt_template = "{}\n{}\n{}".format(self.prompt_instruction,
                                                            self.few_shot_examples,
                                                            self.placeholder_prompt)
        logger.debug("user prompt template : {}".format(self.user_prompt_template))

    def _compute_async_gpt_metric(self, prompt_list):
        """
        Computes the GPT metric asynchronously for a given list of prompts.

        Args:
            prompt_list (list): A list of prompts to compute the metric for.

        Returns:
            dict: The results of the GPT metric computation.
        """
        nest_asyncio = load_nest_asyncio()
        prompt_batch_list = self.openai_connector.get_prompt_batches(prompt_list)

        nest_asyncio.apply()
        if sys.platform.startswith("win"):
            asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        results = asyncio.run(self.openai_connector.get_async_prediction(prompt_batch_list=prompt_batch_list,
                                                                         system_prompt=self.system_prompt_template))
        return results

    def get_custom_metric_details(self):
        """
        Returns a dictionary containing details of the custom metric.

        Returns:
            dict: A dictionary with the following keys:
                - custom_metric_name (str): The metric_name of the custom metric.
                - custom_metric_description (str): The description of the custom metric.
                - custom_metric_results (list): The results of the custom metric.
                - custom_metric_computation_status (str): The computation status of the custom metric.
        """
        metric_info_dict = {
            "custom_metric_name": self.metric_name,
            "custom_metric_description": self.metric_description,
            "custom_metric_results": self.custom_metric_results,
            "custom_metric_computation_status": self.metric_computation_status,
        }
        return metric_info_dict

    def __str__(self):
        """
        Returns a string representation of the custom metric details.

        Returns:
            str: A string representation of the custom metric details.
        """
        return str(self.get_custom_metric_details())

    def __repr__(self):
        """
        Returns a string representation of the AzureMLCustomPromptMetric object.

        :return: A string representation of the object.
        """
        return str(self.get_custom_metric_details())

    def get_custom_metric_prompt(self):
        """
        Retrieves the custom metric prompt.

        Returns:
            dict: A dictionary containing the user prompt template and, if applicable, the system prompt template.
        """
        prompt = {
            "user_prompt_template": self.user_prompt_template
        }

        if self.use_chat_completion_api is True:
            prompt["system_prompt_template"] = self.system_prompt_template

        return prompt

    def compute(self, **kwargs):
        """
        Computes the custom prompt template metric.

        Args:
            **kwargs: Additional keyword arguments passed by the user.

        Returns:
            The results of the custom metric computation.
        """
        logger.debug("Computing custom prompt template metric")
        self.metric_computation_status = "IN_PROGRESS"

        # update the kwargs with the input variables passed by the user
        self.kwargs.update(kwargs)

        Template = load_jinja2_template()
        template = Template(self.user_prompt_template)

        self.map_input_vars_to_kwargs(self.kwargs)
        variable_dict = {}

        if self.input_vars is not None and isinstance(self.input_vars, list):
            if self.custom_prompt_data is not None and isinstance(self.custom_prompt_data, pd.DataFrame):
                for var in self.input_vars:
                    if var in self.custom_prompt_data.columns:
                        variable_dict[var] = self.custom_prompt_data["var"].to_list()
                    else:
                        logger.warning("custom_prompt_data doesn't have the column name : {}".format(var))
                        logger.warning("Please ensure to set the data correctly.")
                        return self.custom_metric_results
            else:
                for var in self.input_vars:
                    if var not in self.kwargs:
                        logger.warning("{} is not set in kwargs".format(var))
                        logger.warning("Please ensure to set the values for input variables as kwargs")
                        return self.custom_metric_results
                    else:
                        variable_dict[var] = self.kwargs.get(var)
        else:
            logger.warning("input_vars are not set. Proceeding without any input variables")

        try:
            self._compute_prompt_metric(template, variable_dict)
        except ValueError as e:
            logger.error("Please ensure that the values input variables are set in kwargs and have same length")
            self.log_error_message(e)
        except Exception as e:
            self.log_error_message(e)

        return self.custom_metric_results  # dict of str

    def log_error_message(self, e):
        """
        Logs the exception message in case of exception.

        Args:
            e (Exception): The exception object.

        Returns:
            None
        """
        logger.error("Scoring failed for custom prompt based metric {} with the"
                     " exception {}".format(self.metric_name, str(e)))
        self.metric_computation_status = "FAILED"

    def _compute_prompt_metric(self, template, variable_dict):
        """
        Takes the input of a prompt template and variable_dict to compute the results.

        Args:
            template (jinja2.Template): The prompt template to be rendered.
            variable_dict (dict): A dictionary containing the input variables.

        Returns:
            None

        Raises:
            None
        """
        prompt_list = []
        # Create an iterator for all input variables
        input_vars_data = pd.DataFrame(variable_dict)
        input_vars_data_list = input_vars_data.to_dict(orient="records")
        # Create a prompt for each input variable
        for input_data in input_vars_data_list:
            prompt = template.render(**input_data)
            prompt_list.append(prompt)
        results = self._compute_async_gpt_metric(prompt_list)

        self.custom_metric_results[constants.Metric.Artifacts][self.metric_name] = results
        self.compute_aggregated_results(results)
        logger.debug("custom prompt template results : {}".format(results))
        self.metric_computation_status = "SUCCESS"

    def compute_aggregated_results(self, results):
        """
        Computes the aggregated results for the given list of results.

        Args:
            results (list): A list of result values.

        Returns:
            None
        """
        non_integer_results = False
        formatted_results = []
        for result_value in results:
            try:
                formatted_result = int(result_value)
            except Exception:
                non_integer_results = True
                formatted_result = float(np.nan)
            formatted_results.append(formatted_result)
        if non_integer_results is True:
            logger.debug("Results cannot be converted to integer scores."
                         " Mean and median cannot be computed")
        metric_value = np.array(formatted_results)
        mean_metric_name = constants.MetricExtrasConstants.MeanExtrasFormat.format(self.metric_name)
        median_metric_name = constants.MetricExtrasConstants.MedianExtrasFormat.format(self.metric_name)
        self.custom_metric_results[constants.Metric.Metrics][mean_metric_name] = np.nanmean(metric_value)
        self.custom_metric_results[constants.Metric.Metrics][median_metric_name] = np.nanmedian(metric_value)

    def map_input_vars_to_kwargs(self, kwargs):
        """
        Maps the input variables to the data sent as input in keyword arguments.

        Args:
            kwargs (dict): The keyword arguments containing the data.

        Returns:
            None

        Raises:
            None
        """
        data_mapping = kwargs.get("data_mapping", None)
        if data_mapping is not None and isinstance(data_mapping, dict):
            if self.metric_name in data_mapping:
                mapping_dict = data_mapping[self.metric_name]
            else:
                mapping_dict = data_mapping
            # Consider question -- it can be mapped to multiple input variables in prompt templates
            # key = input variable metric_name in prompt template,
            # value = name of the keyword argument where data is present
            for key, value in mapping_dict.items():
                kwargs[key] = kwargs.get(value, None)

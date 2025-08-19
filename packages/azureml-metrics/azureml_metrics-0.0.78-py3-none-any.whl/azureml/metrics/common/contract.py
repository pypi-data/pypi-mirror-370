# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Metric contracts."""

import logging
from typing import Any, List, Optional

from azureml.metrics.common.exceptions import InvalidOperationException, InvalidValueException

logger = logging.getLogger(__name__)


class Contract:
    """Class with helper methods to enforce and validate system invariants.

    Use this class' methods to enforce system asserts (i.e. contracts defined within AzureML are adhered to). The
    methods defined in this class will raise exceptions when an invariant is broken.
    """

    @staticmethod
    def assert_true(
            condition: bool,
            message: str,
            target: Optional[str] = None,
            reference_code: Optional[str] = None,
            log_safe: bool = False,
    ) -> None:
        """
        Assert that the provided condition evaluates to True.

        :param condition: The condition to evaluate, should result in a boolean.
        :param message: The assertion message that explains the condition when the assertion evaluates to False.
        :param target: The metric_name of the element (e.g. argument) that caused the error.
        :param reference_code: A string that a developer or the user can use to get further context on the error.
        :param log_safe: If the assertion message is safe to log. Defaults to False.
        :return: None
        """
        if not condition:
            log_safe_exception_message = Contract._build_assertion_message(
                "Invalid Operation", target, reference_code
            )
            exception_message = ". ".join([log_safe_exception_message, "Details: " + message])
            if log_safe:
                log_safe_exception_message = exception_message

            logger.error(log_safe_exception_message)
            raise InvalidOperationException(exception_message, target=target or "InvalidOperationException",
                                            reference_code=reference_code, safe_message=log_safe_exception_message)

    @staticmethod
    def assert_value(
            value: Any,
            name: str,
            valid_values: Optional[List[Any]] = None,
            reference_code: Optional[str] = None,
            log_safe: bool = False,
    ) -> None:
        """
        Assert that the value is non-null, fails otherwise. For also checking for empty strings or lists.

        :param value: The object that should be evaluated for the null check.
        :param name: The metric_name of the object.
        :param valid_values: An optional list of values to verify the validity of the 'value' against.
        :param reference_code: A string that a developer or the user can use to get further context on the error.
        :param log_safe: If the assertion message is safe to log. Defaults to True.
        :return: None
        """
        assert_failed = False
        if value is None:
            log_safe_exception_message = Contract._build_assertion_message(
                assertion_message="Argument {} is null".format(name), target=name, reference_code=reference_code
            )
            exception_message = log_safe_exception_message
            assert_failed = True
        if valid_values is not None and isinstance(valid_values, list) and value not in valid_values:
            log_safe_exception_message = Contract._build_assertion_message(
                assertion_message="Argument {} has an invalid value".format(name),
                target=name,
                reference_code=reference_code,
            )

            exception_message = log_safe_exception_message + ". Supported values: {}".format(valid_values)
            if log_safe:
                log_safe_exception_message = exception_message
            assert_failed = True

        if assert_failed:
            logger.error(log_safe_exception_message)

            raise InvalidValueException(exception_message, target=name, reference_code=reference_code,
                                        safe_message=log_safe_exception_message)

    @staticmethod
    def _build_assertion_message(
            assertion_message: str,
            target: Optional[str],
            reference_code: Optional[str] = None,
    ) -> str:
        """Append the optional fields to the error message with headers (i.e., field names)."""
        result = ["Assertion Failed", assertion_message]
        if target:
            result.append("Target: {}".format(target))
        if reference_code:
            result.append("Reference Code: {}".format(reference_code))
        return ". ".join(result)

# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Metrics Exceptions"""


class MetricsException(Exception):
    """
    Initialize a new instance of MetricsException.

    :param exception_message: Exception Message.
    :type exception_message: str
    :param target: Target for the exception.
    :type target: str
    :param safe_message: message that can be logged to the telemetry service for remote diag.
    :type safe_message: str
    """

    def __init__(self, exception_message, target=None, reference_code=None, safe_message=None, **kwargs):
        self.exception_message = exception_message
        self.target = target
        self.reference_code = reference_code
        self.safe_message = safe_message


class MetricsSystemException(Exception):
    """
    Initialize a new instance of MetricsSystemException.

    :param exception_message: Exception Message.
    :type exception_message: str
    :param target: Target for the exception.
    :type target: str
    :param safe_message: message that can be logged to the telemetry service for remote diag.
    :type safe_message: str
    """

    def __init__(self, exception_message, target=None, reference_code=None, safe_message=None, **kwargs):
        self.exception_message = exception_message
        self.target = target
        self.reference_code = reference_code
        self.safe_message = safe_message


class InvalidOperationException(MetricsException):
    """
    Initialize a new instance of InvalidOperationException.

    :param exception_message: Exception Message.
    :type exception_message: str
    :param target: Target for the exception.
    :type target: str
    :param safe_message: message that can be logged to the telemetry service for remote diag.
    :type safe_message: str
    """

    def __init__(self, exception_message, target=None, reference_code=None, safe_message=None, **kwargs):
        super(InvalidOperationException, self).__init__(exception_message, target, reference_code,
                                                        safe_message, **kwargs)


class InvalidValueException(MetricsException):
    """
    Initialize a new instance of InvalidValueException.

    :param exception_message: Exception Message.
    :type exception_message: str
    :param target: Target for the exception.
    :type target: str
    :param safe_message: message that can be logged to the telemetry service for remote diag.
    :type safe_message: str
    """

    def __init__(self, exception_message, target=None, reference_code=None, safe_message=None, **kwargs):
        super(InvalidValueException, self).__init__(exception_message, target, reference_code,
                                                    safe_message, **kwargs)


class InvalidUserInputException(MetricsException):
    """
    Initialize a new instance of InvalidUserInputException.

    :param exception_message: Exception Message.
    :type exception_message: str
    :param target: Target for the exception.
    :type target: str
    :param safe_message: message that can be logged to the telemetry service for remote diag.
    :type safe_message: str
    """

    def __init__(self, exception_message, target=None, reference_code=None, safe_message=None, **kwargs):
        super(InvalidUserInputException, self).__init__(exception_message, target, reference_code,
                                                        safe_message, **kwargs)


class DataErrorException(MetricsException):
    """
    Initialize a new instance of DataErrorException.

    :param exception_message: Exception Message.
    :type exception_message: str
    :param target: Target for the exception.
    :type target: str
    :param safe_message: message that can be logged to the telemetry service for remote diag.
    :type safe_message: str
    """

    def __init__(self, exception_message, target=None, reference_code=None,
                 safe_message=None, has_pii=None, **kwargs):
        self.has_pii = has_pii
        super(DataErrorException, self).__init__(exception_message, target, reference_code, safe_message, **kwargs)


class ClientException(MetricsException):
    """
    Initialize a new instance of ClientException.

    :param exception_message: Exception Message.
    :type exception_message: str
    :param target: Target for the exception.
    :type target: str
    :param safe_message: message that can be logged to the telemetry service for remote diag.
    :type safe_message: str
    """

    def __init__(self, exception_message, target=None, reference_code=None, safe_message=None, **kwargs):
        super(ClientException, self).__init__(exception_message, target, reference_code, safe_message, **kwargs)


class ResourceException(MetricsException):
    """
    Initialize a new instance of ResourceException.

    :param exception_message: Exception Message.
    :type exception_message: str
    :param target: Target for the exception.
    :type target: str
    :param safe_message: message that can be logged to the telemetry service for remote diag.
    :type safe_message: str
    """

    def __init__(self, exception_message, target=None, reference_code=None, safe_message=None, **kwargs):
        super(ResourceException, self).__init__(exception_message, target, reference_code, safe_message, **kwargs)


class ValidationException(MetricsException):
    """
    Initialize a new instance of ValidationException.

    :param exception_message: Exception Message.
    :type exception_message: str
    :param target: Target for the exception.
    :type target: str
    :param safe_message: message that can be logged to the telemetry service for remote diag.
    :type safe_message: str
    """

    def __init__(self, exception_message, target=None, reference_code=None, safe_message=None, **kwargs):
        super(ValidationException, self).__init__(exception_message, target, reference_code, safe_message, **kwargs)


class TimeseriesTableTrainAbsent(MetricsException):
    """
    :param exception_message: Exception Message.
    :type exception_message: str
    :param target: Target for the exception.
    :type target: str
    :param safe_message: message that can be logged to the telemetry service for remote diag.
    :type safe_message: str
    """

    def __init__(self, exception_message, target=None, reference_code=None, safe_message=None, **kwargs):
        super(TimeseriesTableTrainAbsent, self).__init__(
            exception_message, target, reference_code, safe_message, **kwargs)


class ForecastMetricGrainAbsent(MetricsException):
    """
    :param exception_message: Exception Message.
    :type exception_message: str
    :param target: Target for the exception.
    :type target: str
    :param safe_message: message that can be logged to the telemetry service for remote diag.
    :type safe_message: str
    """

    def __init__(self, exception_message, target=None, reference_code=None, safe_message=None, **kwargs):
        super(ForecastMetricGrainAbsent, self).__init__(
            exception_message, target, reference_code, safe_message, **kwargs)


class ForecastMetricValidAbsent(MetricsException):
    """
    :param exception_message: Exception Message.
    :type exception_message: str
    :param target: Target for the exception.
    :type target: str
    :param safe_message: message that can be logged to the telemetry service for remote diag.
    :type safe_message: str
    """

    def __init__(self, exception_message, target=None, reference_code=None, safe_message=None, **kwargs):
        super(ForecastMetricValidAbsent, self).__init__(
            exception_message, target, reference_code, safe_message, **kwargs)


class HFEvaluateClientException(MetricsSystemException):
    """
    :param exception_message: Exception Message.
    :type exception_message: str
    :param target: Target for the exception.
    :type target: str
    :param safe_message: message that can be logged to the telemetry service for remote diag.
    :type safe_message: str
    """

    def __init__(self, exception_message, target=None, reference_code=None, safe_message=None, **kwargs):
        super(HFEvaluateClientException, self).__init__(
            exception_message, target, reference_code, safe_message, **kwargs)


class MissingDependencies(MetricsException):
    """
    :param exception_message: Exception Message.
    :type exception_message: str
    :param target: Target for the exception.
    :type target: str
    """

    def __init__(self, exception_message, target=None, reference_code=None, safe_message=None, **kwargs):
        super(MissingDependencies, self).__init__(
            exception_message, target, reference_code, safe_message, **kwargs)


class OAIClientException(MetricsSystemException):
    """
    :param exception_message: Exception Message.
    :type exception_message: str
    :param target: Target for the exception.
    :type target: str
    :param safe_message: message that can be logged to the telemetry service for remote diag.
    :type safe_message: str
    """

    def __init__(self, exception_message, target=None, reference_code=None, safe_message=None, **kwargs):
        super(OAIClientException, self).__init__(
            exception_message, target, reference_code, safe_message, **kwargs)


class OAIClientContentFilterException(MetricsSystemException):
    """
    :param exception_message: Exception Message.
    :type exception_message: str
    :param target: Target for the exception.
    :type target: str
    :param safe_message: message that can be logged to the telemetry service for remote diag.
    :type safe_message: str
    """

    def __init__(self, exception_message, target=None, reference_code=None, safe_message=None, **kwargs):
        DEFAULT_CONTENT_FILTER_MESSAGE = "Content Filter: The response was filtered due to the prompt " \
                                         "triggering Azure OpenAI’s content management policy. Please " \
                                         "modify your prompt and retry. To learn more about our content filtering " \
                                         "policies please read our documentation: " \
                                         "https://go.microsoft.com/fwlink/?linkid=2198766"
        if safe_message is None:
            safe_message = DEFAULT_CONTENT_FILTER_MESSAGE

        super(OAIClientContentFilterException, self).__init__(
            exception_message, target, reference_code, safe_message, **kwargs)


class OAIClientLengthFinishException(MetricsSystemException):
    """
    :param exception_message: Exception Message.
    :type exception_message: str
    :param target: Target for the exception.
    :type target: str
    :param safe_message: message that can be logged to the telemetry service for remote diag.
    :type safe_message: str
    """

    def __init__(self, exception_message, target=None, reference_code=None, safe_message=None, **kwargs):
        DEFAULT_FINISH_REASON_MESSAGE = "Azure OpenAI: finish_reason='length'. Completion limit reached." \
                                        " Please ask more specific question to the model."

        if safe_message is None:
            safe_message = DEFAULT_FINISH_REASON_MESSAGE

        super(OAIClientLengthFinishException, self).__init__(
            exception_message, target, reference_code, safe_message, **kwargs)


class MetricUnregisteredException(MetricsException):
    """
    :param exception_message: Exception Message.
    :type exception_message: str
    :param target: Target for the exception.
    :type target: str
    """

    def __init__(self, exception_message, target=None, reference_code=None, safe_message=None, **kwargs):
        super(MetricUnregisteredException, self).__init__(
            exception_message, target, reference_code, safe_message, **kwargs)

# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Methods specific to logging utilities."""

import contextlib
import logging
import sys
import os
import platform
import uuid
import time

from datetime import datetime
from typing import Optional, Dict, Any, Iterator, Union
from azureml.metrics.common.exceptions import MetricsException
from azureml.metrics.common._run_utils import TestRun
from azureml.metrics.constants import TelemetryConstants, ExceptionTypes


@contextlib.contextmanager
def default_log_activity(
        logger: logging.Logger,
        activity_name: str,
        activity_type: Optional[str] = None,
        custom_dimensions: Optional[Dict[str, Any]] = None,
) -> Iterator[Optional[Any]]:
    """
    Log the activity status with duration.

    :param logger: logger
    :param activity_name: activity name
    :param activity_type: activity type
    :param custom_dimensions: custom dimensions
    """
    start_time = datetime.utcnow()
    activity_info = {"activity_name": activity_name, "activity_type": activity_type}  # type: Dict[str, Any]
    log_record = {"activity": activity_name, "type": activity_type, "dimesions": custom_dimensions}
    logger.info("[azureml-metrics] ActivityStarted: {}, ActivityType: {},"
                " CustomDimensions: {}".format(activity_name, activity_type, custom_dimensions))
    completion_status = "SUCCESS"
    try:
        yield
    except Exception as e:
        completion_status = "FAILED"
        logger.error(str(e))
        raise
    finally:
        end_time = datetime.utcnow()
        duration_ms = round((end_time - start_time).total_seconds() * 1000, 2)
        activity_info["durationMs"] = duration_ms
        activity_info["completionStatus"] = completion_status

        logger.info(
            "[azureml-metrics] ActivityCompleted: Activity={}, HowEnded={}, Duration={}[ms]".format(
                activity_name, completion_status, duration_ms
            ),
            extra={"properties": activity_info},
        )

    return log_record


def default_log_traceback(
        exception: Union[MetricsException, Exception],
        logger: Optional[Union[logging.Logger, logging.LoggerAdapter]],
        override_error_msg: Optional[str] = None,
        is_critical: Optional[bool] = False,
        tb: Optional[Any] = None,
) -> None:
    """
    Log exception traces.

    :param exception: The exception to log.
    :param logger: The logger to use.
    :param override_error_msg: The message to display that will override the current error_msg.
    :param is_critical: If is_critical, the logger will use log.critical, otherwise log.error.
    :param tb: The traceback to use for logging; if not provided, the one attached to the exception is used.
    """
    if override_error_msg is not None:
        error_msg = override_error_msg
    else:
        error_msg = str(exception)

    # Some exceptions may not have a __traceback__ attr
    traceback_obj = tb or exception.__traceback__ if hasattr(exception, "__traceback__") else None or sys.exc_info()[2]

    exception_class_name = exception.__class__.__name__

    # User can see original log message in their log file
    message = [
        "Class: {}".format(exception_class_name),
        "Message: {}".format(error_msg),
    ]

    if is_critical:
        logger.critical("\n".join(message))
    else:
        logger.error("\n".join(message))

    if traceback_obj is not None and hasattr(traceback_obj, "format_exc"):
        logger.debug(traceback_obj.format_exc())


class AppInsightsPIIStrippingFormatter(logging.Formatter):
    """Formatter for App Insights Logging.

    Args:
        logging (_type_): _description_
    """

    def format(self, record: logging.LogRecord) -> str:
        """Format incoming log record.

        Args:
            record (logging.LogRecord): _description_

        Returns:
            str: _description_
        """
        exception_tb = getattr(record, 'exception_tb_obj', None)
        if exception_tb is None:
            return super().format(record)

        not_available_message = '[Not available]'

        properties = getattr(record, 'properties', {})

        message = properties.get('exception_message', TelemetryConstants.NON_PII_MESSAGE)
        traceback_msg = properties.get('exception_traceback', not_available_message)

        record.message = record.msg = '\n'.join([
            'Type: {}'.format(properties.get('error_type', ExceptionTypes.Unclassified)),
            'Class: {}'.format(properties.get('exception_class', not_available_message)),
            'Message: {}'.format(message),
            'Traceback: {}'.format(traceback_msg),
            'ExceptionTarget: {}'.format(properties.get('exception_target', not_available_message))
        ])

        # Update exception message and traceback in extra properties as well
        properties['exception_message'] = message

        return super().format(record)


class CustomDimensions:
    """Custom Dimensions Class for App Insights."""

    def __init__(self,
                 run_details: TestRun,
                 app_name=TelemetryConstants.APP_NAME,
                 metrics_package_version=TelemetryConstants.DEFAULT_VERSION,
                 os_info=platform.system(),
                 task_type="") -> None:
        """__init__.

        Args:
            app_name (_type_, optional): _description_. Defaults to "azureml-metrics".
            metrics_package_version (str, optional): _description_. Defaults to "0.0.25".
            os_info (_type_, optional): _description_. Defaults to platform.system().
            task_type (str, optional): _description_. Defaults to "".
        """
        self.app_name = app_name
        self.os_info = os_info
        self.task_type = task_type
        self.metrics_package_version = metrics_package_version
        self.run_id = run_details.run.id
        self.experiment_id = run_details.experiment.id
        self.region = run_details.region
        self.subscription_id = run_details.subscription
        run_info = run_details.get_extra_run_info
        self.location = run_info.get("location", "")
        self.moduleId = run_info.get("moduleId", "")
        self.moduleName = run_info.get("moduleName", "")


current_run = TestRun()
custom_dimensions = CustomDimensions(current_run)


def sanitize_custom_dims(custom_dims):
    """Override custom dimensions to use passed run id."""
    try:
        if isinstance(custom_dims, str):
            import json
            custom_dims = json.loads(custom_dims)
        custom_dims = dict(custom_dims)
    except Exception:
        custom_dims = dict()
    custom_dimensions.run_id = custom_dims.get('run_id', custom_dimensions.run_id)
    return custom_dimensions


def flush_logger(logger):
    """Flush logger."""
    for handler in logger.handlers:
        handler.flush()
    time.sleep(5)


class AppInsightsPIIStrippingFormatterManager:
    """Context manager for AppInsightsPIIStrippingFormatter."""

    def __init__(self, custom_dimensions):
        """__init__."""
        app_name = custom_dimensions.app_name
        run_id = custom_dimensions.run_id
        self.formatter = AppInsightsPIIStrippingFormatter(fmt=TelemetryConstants.LOGGING_FMT.format(app_name, run_id))

    def get_formatter(self):
        """Get formatter instance."""
        return self.formatter

    def reset_formatter(self, custom_dimensions):
        """Reset formatter instance to use latest run id and app name from custom dimensions."""
        app_name = custom_dimensions.app_name
        run_id = custom_dimensions.run_id
        self.formatter.__init__(fmt=TelemetryConstants.LOGGING_FMT.format(app_name, run_id))


formatter = AppInsightsPIIStrippingFormatterManager(custom_dimensions)


class DisableLoggingFilter(logging.Filter):
    """Filter for enabling/disabling azureml-metrics Telemetry logging."""

    def __init__(self, force_disabled=False, *args, **kwargs):
        """__init__."""
        self.force_disabled = force_disabled
        super().__init__(*args, **kwargs)

    def filter(self, record):
        """Filter definition."""
        return not self.is_telemetry_disabled()

    def is_telemetry_disabled(self):
        """Check if azureml-metrics telemetry is disabled in env variables."""
        logging_disabled = os.environ.get(TelemetryConstants.AZUREML_METRICS_DISABLE_LOGGING, str(False)).lower()
        return (logging_disabled in TelemetryConstants.TRUTHY) or self.force_disabled


telemetry_filter = DisableLoggingFilter()


def get_logger(logging_level: str = 'DEBUG',
               custom_dimensions: dict = vars(custom_dimensions),
               name: str = TelemetryConstants.LOGGER_NAME):
    """Get logger.

    Args:
        logging_level (str, optional): _description_. Defaults to 'DEBUG'.
        custom_dimensions (dict, optional): _description_. Defaults to vars(custom_dimensions).
        name (str, optional): _description_. Defaults to constants.TelemetryConstants.LOGGER_NAME.

    Raises:
        ValueError: _description_

    Returns:
        _type_: _description_
    """
    numeric_log_level = getattr(logging, logging_level.upper(), None)
    if not isinstance(numeric_log_level, int):
        raise ValueError('Invalid log level: %s' % logging_level)

    logger = logging.getLogger(name)
    logger.propagate = True
    logger.setLevel(numeric_log_level)
    handler_names = [handler.get_name() for handler in logger.handlers]

    app_name = custom_dimensions["app_name"]

    if app_name not in handler_names:
        try:
            from azureml.telemetry import INSTRUMENTATION_KEY
            from azureml.telemetry.logging_handler import get_appinsights_log_handler
            child_namespace = __name__
            current_logger = logging.getLogger("azureml.telemetry").getChild(child_namespace)
            current_logger.propagate = False
            current_logger.setLevel(logging.CRITICAL)
            appinsights_handler = get_appinsights_log_handler(
                instrumentation_key=INSTRUMENTATION_KEY,
                logger=current_logger, properties=custom_dimensions
            )
            appinsights_handler.setFormatter(formatter.get_formatter())
            appinsights_handler.setLevel(numeric_log_level)
            appinsights_handler.set_name(app_name)
            appinsights_handler.addFilter(telemetry_filter)
            logger.addHandler(appinsights_handler)
        except Exception as e:
            logger.info("Failed to add App Insights handler. Error: %s", str(e))

    return logger


@contextlib.contextmanager
def log_activity(logger, activity_name, activity_type=None, custom_dimensions=None):
    """Duplicate with custom logic from azureml.telemetry.activity

    Log an activity.

    An activity is a logical block of code that consumers want to monitor.
    To monitor, wrap the logical block of code with the ``log_activity()`` method. As an alternative, you can
    also use the ``@monitor_with_activity`` decorator.

    :param logger: The logger adapter.
    :type logger: logging.LoggerAdapter
    :param activity_name: The name of the activity. The name should be unique per the wrapped logical code block.
    :type activity_name: str
    :param activity_type: One of PUBLICAPI, INTERNALCALL, or CLIENTPROXY which represent an incoming API call,
        an internal (function) call, or an outgoing API call. If not specified, INTERNALCALL is used.
    :type activity_type: str
    :param custom_dimensions: The custom properties of the activity.
    :type custom_dimensions: dict
    """
    try:
        from azureml.telemetry.activity import ActivityLoggerAdapter, ActivityCompletionStatus, ActivityType
        activity_type = activity_type or ActivityType.INTERNALCALL
        activity_info = dict(activity_id=str(uuid.uuid4()), activity_name=activity_name, activity_type=activity_type)
        custom_dimensions = custom_dimensions or {}
        activity_info.update(custom_dimensions)

        start_time = datetime.utcnow()
        completion_status = ActivityCompletionStatus.SUCCESS

        message = "ActivityStarted, {}".format(activity_name)
        activityLogger = ActivityLoggerAdapter(logger, activity_info)

        activityLogger.info(message)
        exception = None

        try:
            yield activityLogger
        except Exception as e:
            exception = e
            completion_status = ActivityCompletionStatus.FAILURE
            raise
        finally:
            end_time = datetime.utcnow()
            duration_ms = round((end_time - start_time).total_seconds() * 1000, 2)

            activityLogger.activity_info["completionStatus"] = completion_status
            activityLogger.activity_info["durationMs"] = duration_ms
            message = "ActivityCompleted: Activity={}, HowEnded={}, Duration={} [ms]".format(
                activity_name, completion_status, duration_ms)
            if exception:
                message += ", Exception occurred."
                activityLogger.error(message)
            else:
                activityLogger.info(message)
    except ImportError:
        with default_log_activity(logger, activity_name, activity_type, custom_dimensions) as log_record:
            yield log_record

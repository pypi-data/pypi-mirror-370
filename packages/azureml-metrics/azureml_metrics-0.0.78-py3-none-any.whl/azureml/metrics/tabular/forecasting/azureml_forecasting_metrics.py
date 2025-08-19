# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Methods specific to a Foreasting task type."""
import logging
import numpy as np
import pandas as pd

from typing import Any, Callable, Dict, Iterator, List, Optional, Sequence, Tuple, Union

from azureml.metrics import constants
from azureml.metrics.common import _scoring, utilities
from azureml.metrics.common.azureml_metrics import AzureMLMetrics
from azureml.metrics.common.contract import Contract
from azureml.metrics.common.reference_codes import ReferenceCodes


logger = logging.getLogger(__name__)


class AzureMLForecastingMetrics(AzureMLMetrics):
    """
    Class for AzureML forecasting metrics.

    Forecasting metrics include regression metrics but normalized metrics are calculated
    differently because forecasting data set may contain several time series. In this case metrics,
    are calculated in series-by-series manner.
    """

    def __init__(
            self,
            metrics: Optional[List[str]] = None,
            sample_weight: Optional[np.ndarray] = None,
            X_train: Optional[pd.DataFrame] = None,
            y_train: Optional[np.ndarray] = None,
            y_std: Optional[float] = None,
            time_series_id_column_names: Optional[List[str]] = None,
            time_column_name: Optional[str] = None,
            origin_column_name: Optional[Any] = None,
            aggregation_method: Callable[[Sequence[float]], float] = np.mean,
            custom_dimensions: Optional[Dict[str, Any]] = None,
            y_min_dict: Dict[Union[str, Tuple[str]], float] = None,
            y_max_dict: Dict[Union[str, Tuple[str]], float] = None,
            log_activity: Optional[Callable[[logging.Logger, str, Optional[str], Optional[Dict[str, Any]]],
                                            Iterator[Optional[Any]]]] = None,
            log_traceback: Optional[Callable[[BaseException, logging.Logger, Optional[str],
                                              Optional[bool], Optional[Any]], None]] = None) -> None:
        """
        Initialize the forecasting metric class.

        :param metrics: Regression metrics to compute point estimates
        :param sample_weight: Weighting of each sample in the calculation.
        :param X_train: The inputs which were used to train the model.
        :param y_train: The targets which were used to train the model.
        :param y_std: The standard deviation of a target.
        :param time_series_id_column_names: The time series id column names also
                                            known as grain column name.
        :param time_column_name: The time column name.
        :param origin_column_name: The origin time column name.
        :param aggregation_method: the method to be used to aggregate normalized metrics from
                                   different grains.
        :param custom_dimensions to report the telemetry data.
        :param y_min_dict: The dictionary, with minimum target values per time series ID, time series ID
                           is used as a key. Not used if X_train and y_train are provided.
        :param y_max_dict: The dictionary, with maximum target values per time series ID, time series ID
                           is used as a key. Not used if X_train and y_train are provided.
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
        """

        if X_train is not None and y_train is not None:
            all_metrics = AzureMLForecastingMetrics.list_metrics()
        else:
            # Do not generate artifacts if training set was not provided.
            all_metrics = (constants.Metric.SCALAR_REGRESSION_SET
                           | constants.Metric.FORECASTING_NONSCALAR_SET_NO_TRAINING)
        if metrics:
            all_metrics = list(set(metrics).intersection(set(all_metrics)))
            if len(all_metrics) < len(metrics):
                logger.warn("Some metrics were not evaluated because "
                            "they are not supported or data context was not provided.")
                fc_metrics = AzureMLForecastingMetrics.list_metrics()
                if not all_metrics and any(m not in fc_metrics for m in metrics):
                    # User has provided at least one non supported metric, and no other metrics are
                    # present or supported. We will set the metric and allow it to fail later.
                    all_metrics = metrics
        self.metrics = all_metrics
        self._sample_weight = sample_weight
        self._X_train = X_train
        self._y_train = y_train
        self._y_std = y_std
        Contract.assert_true(
            (X_train is None) == (y_train is None),
            message="X_train and y_train should be both None or be pd.DataFrame and numpy array respectively",
            target="X_train_y_train", reference_code=ReferenceCodes._METRIC_VALIDATION_INCONSISTENT_X_Y)
        Contract.assert_true(
            bool(y_min_dict) == bool(y_max_dict),
            message=("The dictionaries with minimal and maximal values should be provided together "
                     "or both set to None or empty dictionaries."),
            target="y_min_max_dict", reference_code=ReferenceCodes._METRIC_VALIDATION_INCONSISTENT_MIN_MAX
        )
        self._time_column_name = time_column_name
        self._origin_column_name = origin_column_name
        if time_series_id_column_names:
            if not isinstance(time_series_id_column_names, list):
                self._time_series_id_column_names = [time_series_id_column_names]
            else:
                self._time_series_id_column_names = time_series_id_column_names
        else:
            self._time_series_id_column_names = [constants._TimeSeriesInternal.DUMMY_GRAIN_COLUMN]
        if X_train is None or y_train is None:
            self._y_min_dict = y_min_dict if y_min_dict else {}
            self._y_max_dict = y_max_dict if y_max_dict else {}
            Contract.assert_true(
                set(self._y_min_dict.keys()) == set(self._y_max_dict.keys()),
                message="The dictionary with minimal and maximal values must contain the same keys.",
                target="y_min_max_dict_keys",
                reference_code=ReferenceCodes._METRIC_VALIDATION_INCONSISTENT_MIN_MAX_KEYS
            )
        else:
            Contract.assert_true(
                X_train.shape[0] == y_train.shape[0],
                message="The number of covariates in X_train does not match the numer of targets in y_train.",
                target="X_train_y_train_shape", reference_code=ReferenceCodes._METRIC_VALIDATION_TEST_SHAPE_MISMATCH
            )
            self._y_min_dict = {}
            self._y_max_dict = {}
            drop_columns = [constants._TimeSeriesInternal.DUMMY_TARGET_COLUMN]
            X_train[constants._TimeSeriesInternal.DUMMY_TARGET_COLUMN] = y_train
            index = self._get_tsds_index(X_train)
            if self._time_series_id_column_names == [constants._TimeSeriesInternal.DUMMY_GRAIN_COLUMN]:
                if (constants._TimeSeriesInternal.DUMMY_GRAIN_COLUMN not in X_train.columns
                        and constants._TimeSeriesInternal.DUMMY_GRAIN_COLUMN not in X_train.index.names):
                    X_train[constants._TimeSeriesInternal.DUMMY_GRAIN_COLUMN] = \
                        constants._TimeSeriesInternal.DUMMY_GRAIN_COLUMN
                    drop_columns.append(constants._TimeSeriesInternal.DUMMY_GRAIN_COLUMN)
                self._X_train = X_train.drop(constants._TimeSeriesInternal.DUMMY_TARGET_COLUMN, axis=1, inplace=False)
                self._X_train = self._reindex_dataframe_maybe(self._X_train, index)
            else:
                # Copy the data frame not to break the index on the original one
                self._X_train = self._reindex_dataframe_maybe(self._X_train.copy(), index)

            for ts_id, df_one in X_train.groupby(self._time_series_id_column_names):
                self._y_min_dict[ts_id] = df_one[constants._TimeSeriesInternal.DUMMY_TARGET_COLUMN].min(skipna=True)
                self._y_max_dict[ts_id] = df_one[constants._TimeSeriesInternal.DUMMY_TARGET_COLUMN].max(skipna=True)

            X_train.drop(drop_columns, axis=1, inplace=True)

        Contract.assert_true(aggregation_method in (np.mean, np.median), target='aggregation_method',
                             message='only numpy.mean and numpy.median are allowed as an aggregation functions.',
                             reference_code=ReferenceCodes._METRIC_INVALID_AGGREGATION_FUNCTION)
        self._aggregation_method = aggregation_method
        self.__custom_dimensions = custom_dimensions

        super().__init__(log_activity, log_traceback)

    def _get_tsds_index(self, X: pd.DataFrame) -> List[str]:
        """
        Generate the time series data set index for data frame. This index
        is [time_column_name, ts_id_column_names, origin_column_name].
        origin_column_name should present only if it is present in the data.

        :param X: The data frame for which index need to be set.
        :return: The proposed index for the data frame.
        """
        index = [self._time_column_name]
        index.extend(self._time_series_id_column_names)
        if self._origin_column_name and self._origin_column_name in X.columns:
            index.append(self._origin_column_name)
        return index

    def _reindex_dataframe_maybe(self, X: pd.DataFrame, index: Sequence) -> pd.DataFrame:
        """
        Add the dummy grain only if it is absent.

        :param X: The data frame to be modified.
        :param index: The new index
        """
        if set(X.index.names) != set(index):
            if X.index.names[0]:
                X.reset_index(drop=False, inplace=True)
            if index[0]:
                X.set_index(index, inplace=True)
        return X

    def _remove_nan_from_target(
            self, X: pd.DataFrame,
            y_test: np.ndarray,
            y_pred: np.ndarray) -> Tuple[pd.DataFrame, np.ndarray, np.ndarray]:
        """
        Remove The NaN-s pesent in target.

        :param y_test: True labels for the test set.
        :param y_pred: Predictions for each sample.
        :param X_test: The regressors for the test data set. It must align with y_train and
                       to contain time and time series ID.
        """
        X['pred'] = y_pred
        X['actual'] = y_test
        X.dropna(subset=['pred', 'actual'], axis=0, inplace=True)
        y_pred = X.pop('pred').values
        y_test = X.pop('actual').values
        return X, y_test, y_pred

    def compute(self,
                y_test: Union[np.ndarray, pd.DataFrame, List],
                y_pred: Union[np.ndarray, pd.DataFrame, List],
                X_test: pd.DataFrame) -> Dict[str, Dict[str, Any]]:
        """
        Given the scored data, generate metrics for forecasting task.

        :param y_test: True labels for the test set.
        :param y_pred: Predictions for each sample.
        :param X_test: The regressors for the test data set. It must align with y_train and
                       to contain time and time series ID.
        :return: The dictionary with metrics and artifacts.
        """
        Contract.assert_true(
            X_test.shape[0] == y_test.shape[0],
            message="The number of covariates in X_test does not match the number of targets in y_test.",
            target="X_test_y_test_shape", reference_code=ReferenceCodes._METRIC_VALIDATION_TEST_SHAPE_MISMATCH
        )
        y_test = utilities.check_and_convert_to_np(y_test)
        y_pred = utilities.check_and_convert_to_np(y_pred)
        drop_columns = []
        columns_set = set(X_test.columns)
        if X_test.index.names[0]:
            columns_set.update(X_test.index.names)
        old_index = X_test.index.names
        if (self._time_series_id_column_names == [constants._TimeSeriesInternal.DUMMY_GRAIN_COLUMN]):
            if (
               constants._TimeSeriesInternal.DUMMY_GRAIN_COLUMN not in X_test.columns
               and constants._TimeSeriesInternal.DUMMY_GRAIN_COLUMN not in X_test.index.names):
                X_test[constants._TimeSeriesInternal.DUMMY_GRAIN_COLUMN] = \
                    constants._TimeSeriesInternal.DUMMY_GRAIN_COLUMN
                drop_columns.append(constants._TimeSeriesInternal.DUMMY_GRAIN_COLUMN)
        X_test = self._reindex_dataframe_maybe(X_test, self._get_tsds_index(X_test))
        # Remove NaN values from X_test.
        # If predictions or actuals are None, we will raise the error later.
        if (y_test is not None and y_pred is not None
                and len(y_test) == len(y_pred) and len(y_pred) == X_test.shape[0]):
            X_test, y_test, y_pred = self._remove_nan_from_target(X_test, y_test, y_pred)
        # Calculate the horizons by grains
        ORDER = 'order'
        if constants._TimeSeriesInternal.HORIZON_NAME in X_test.columns:
            horizons = X_test[constants._TimeSeriesInternal.HORIZON_NAME].values
        else:
            horizons = np.zeros(X_test.shape[0])
            X_test[ORDER] = np.arange(X_test.shape[0])
            grain_num = 0
            for _, test_one in X_test.groupby(self._time_series_id_column_names):
                grain_num += 1
                test_one.reset_index(inplace=True, drop=False)
                test_one.sort_values(self._time_column_name, inplace=True)
                horizons[test_one[ORDER].values] = np.arange(test_one.shape[0])
            Contract.assert_true(
                np.sum(horizons == 0) == grain_num, message="Unable to calculate horizons.", target="horizons",
                reference_code=ReferenceCodes._METRIC_VALIDATION_FORECAST_HORIZON)
            X_test.drop([ORDER], inplace=True, axis=1)
        scored_metrics = _scoring._score_forecasting(
            log_activity=self._log_activity,
            log_traceback=self._log_traceback,
            y_test=y_test,
            y_pred=y_pred,
            horizons=horizons,
            X_test=X_test,
            metrics=self.metrics,
            time_column_name=self._time_column_name,
            time_series_id_column_names=self._time_series_id_column_names,
            origin_column_name=self._origin_column_name,
            y_min_dict=self._y_min_dict,
            y_max_dict=self._y_max_dict,
            y_std=self._y_std,
            sample_weight=self._sample_weight,
            X_train=self._X_train,
            y_train=self._y_train,
            aggregation_method=self._aggregation_method,
        )
        # We will drop columns, not present in the original data frame.
        drop_columns = set(X_test.columns)
        if X_test.index.names[0]:
            drop_columns.update(X_test.index.names)
        drop_columns.difference_update(columns_set)
        if drop_columns:
            X_test.reset_index(drop=False, inplace=True)
            X_test.drop(drop_columns, axis=1, inplace=True)
        X_test = self._reindex_dataframe_maybe(X_test, old_index)

        # Note: In regression tasks, we are calculating metrics confidence intervals
        # by sampling y_pred and y_test.
        # This way of calculation of confidence intervals does not make
        # sense for forecasting as metrics deteriorate while moving further
        # from forecast origin.
        return scored_metrics

    @staticmethod
    def list_metrics():
        """
        Get the list of supported metrics.

        :return: List of supported metrics.
        """
        supported_metrics = (constants.Metric.SCALAR_REGRESSION_SET | constants.Metric.FORECAST_SET)
        return supported_metrics

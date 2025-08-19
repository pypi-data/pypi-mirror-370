# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Definitions for forecasting metrics."""
import logging
import numpy as np
import pandas as pd

from abc import abstractmethod
from collections import OrderedDict
from typing import Any, Callable, Dict, List, Optional, Sequence, Tuple, Type, Union, cast

from azureml.metrics import _scoring_utilities, constants
from azureml.metrics.tabular.regression import _regression
from azureml.metrics.common._metric_base import Metric, NonScalarMetric, ScalarMetric
from azureml.metrics.common.contract import Contract
from azureml.metrics.common.exceptions import (
    DataErrorException,
    ForecastMetricGrainAbsent,
    ForecastMetricValidAbsent,
    TimeseriesTableTrainAbsent,
    MissingDependencies
)
from azureml.metrics.common.reference_codes import ReferenceCodes

_logger = logging.getLogger(__name__)


class ForecastingMetric(Metric):
    """Abstract class for forecast metrics."""

    y_pred_str = "y_pred"
    y_test_str = "y_test"

    @staticmethod
    def convert_to_list_of_str(val: Union[Any, Tuple[Any], List[Any]]) -> List[str]:
        """
        Convert an input to a list of str.

        Useful for converting grain column names or values to a list of strings.
        """
        if not val:
            return []
        val_collection = val if isinstance(val, list) or isinstance(val, tuple) else [val]
        return list(map(str, val_collection))

    def __init__(
        self,
        y_test: np.ndarray,
        y_pred: np.ndarray,
        horizons: np.ndarray,
        y_min: Optional[float] = None,
        y_max: Optional[float] = None,
        y_std: Optional[float] = None,
        sample_weight: Optional[np.ndarray] = None,
        X_test: Optional[pd.DataFrame] = None,
        X_train: Optional[pd.DataFrame] = None,
        y_train: Optional[np.ndarray] = None,
        time_series_id_column_names: Optional[List[str]] = None,
        time_column_name: Optional[str] = None,
        origin_column_name: Optional[Any] = None,
        **kwargs: Any
    ) -> None:
        """
        Initialize the forecasting metric class.

        :param y_test: True labels for the test set.
        :param y_pred: Predictions for each sample.
        :param horizons: The integer horizon alligned to each y_test. These values should be computed
            by the timeseries transformer. If the timeseries transformer does not compute a horizon,
            ensure all values are the same (ie. every y_test should be horizon 1.)
        :param y_min: Minimum target value.
        :param y_max: Maximum target value.
        :param y_std: Standard deviation of the targets.
        :param sample_weight: Weighting of each sample in the calculation.
        :param X_test: The inputs which were used to compute the predictions.
        :param X_train: The inputs which were used to train the model.
        :param y_train: The targets which were used to train the model.
        :param time_series_id_column_names: The time series id column names also known as
                                            grain column names.
        :param time_column_name: The time column name.
        :param origin_column_name: The origin time column name.
        """
        if y_test.shape[0] != y_pred.shape[0]:
            raise DataErrorException(
                exception_message="Mismatched input shapes: y_test, y_pred",
                target="y_pred", reference_code=ReferenceCodes._METRIC_INVALID_DATA_SHAPE)
        self._y_test = y_test
        self._y_pred = y_pred
        self._horizons = horizons
        self._y_min = y_min
        self._y_max = y_max
        self._y_std = y_std
        self._sample_weight = sample_weight
        self._X_test = X_test
        self._X_train = X_train
        self._y_train = y_train
        if not isinstance(time_series_id_column_names, list) and time_series_id_column_names is not None:
            self._time_series_id_column_names = [time_series_id_column_names]
        else:
            self._time_series_id_column_names = time_series_id_column_names
        self._time_column_name = time_column_name
        self._origin_column_name = origin_column_name

        super().__init__()

    @abstractmethod
    def compute(self) -> Dict[str, Any]:
        """Compute the score for the metric."""
        ...

    def _group_raw_by_horizon(self) -> Dict[int, Dict[str, List[float]]]:
        """
        Group y_true and y_pred by horizon.

        :return: A dictionary of horizon to y_true, y_pred.
        """
        grouped_values = {}  # type: Dict[int, Dict[str, List[float]]]
        for idx, h in enumerate(self._horizons):
            if h in grouped_values:
                grouped_values[h][ForecastingMetric.y_pred_str].append(self._y_pred[idx])
                grouped_values[h][ForecastingMetric.y_test_str].append(self._y_test[idx])
            else:
                grouped_values[h] = {
                    ForecastingMetric.y_pred_str: [self._y_pred[idx]],
                    ForecastingMetric.y_test_str: [self._y_test[idx]],
                }

        return grouped_values

    @staticmethod
    def _group_scores_by_horizon(score_data: List[Dict[int, Dict[str, Any]]]) -> Dict[int, List[Any]]:
        """
        Group computed scores by horizon.

        :param score_data: The dictionary of data from a cross-validated model.
        :return: The data grouped by horizon in sorted order.
        """
        grouped_data = {}  # type: Dict[int, List[Any]]
        for cv_fold in score_data:
            for horizon in cv_fold.keys():
                if horizon in grouped_data.keys():
                    grouped_data[horizon].append(cv_fold[horizon])
                else:
                    grouped_data[horizon] = [cv_fold[horizon]]

        # sort data by horizon
        grouped_data_sorted = OrderedDict(sorted(grouped_data.items()))
        return grouped_data_sorted


class ForecastMAPE(ForecastingMetric, NonScalarMetric):
    """Mape Metric based on horizons."""

    SCHEMA_TYPE = constants.SCHEMA_TYPE_MAPE
    SCHEMA_VERSION = "1.0.0"

    MAPE = "mape"
    COUNT = "count"

    def compute(self) -> Dict[str, Any]:
        """Compute mape by horizon."""
        grouped_values = self._group_raw_by_horizon()
        for h in grouped_values:
            partial_pred = np.array(grouped_values[h][ForecastingMetric.y_pred_str])
            partial_test = np.array(grouped_values[h][ForecastingMetric.y_test_str])

            self._data[h] = {
                ForecastMAPE.MAPE: _regression._mape(partial_test, partial_pred),
                ForecastMAPE.COUNT: len(partial_pred),
            }

        ret = NonScalarMetric._data_to_dict(ForecastMAPE.SCHEMA_TYPE, ForecastMAPE.SCHEMA_VERSION, self._data)
        return cast(Dict[str, Any], _scoring_utilities.make_json_safe(ret))

    @staticmethod
    def aggregate(scores: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Fold several scores from a computed metric together.

        :param scores: List of computed scores.
        :return: Aggregated score.
        """
        if not Metric.check_aggregate_scores(scores, constants.Metric.ForecastMAPE):
            return NonScalarMetric.get_error_metric()

        score_data = [score[NonScalarMetric.DATA] for score in scores]
        grouped_data = ForecastingMetric._group_scores_by_horizon(score_data)

        data = {}
        for horizon in grouped_data:
            agg_count = 0
            agg_mape = 0.0
            folds = grouped_data[horizon]
            for fold in folds:
                fold_count = fold[ForecastMAPE.COUNT]
                agg_count += fold_count
                agg_mape += fold[ForecastMAPE.MAPE] * fold_count
            agg_mape = agg_mape / agg_count
            data[horizon] = {ForecastMAPE.MAPE: agg_mape, ForecastMAPE.COUNT: agg_count}

        ret = NonScalarMetric._data_to_dict(ForecastMAPE.SCHEMA_TYPE, ForecastMAPE.SCHEMA_VERSION, data)
        return cast(Dict[str, Any], _scoring_utilities.make_json_safe(ret))


class ForecastResiduals(ForecastingMetric, NonScalarMetric):
    """Forecasting residuals metric."""

    SCHEMA_TYPE = constants.SCHEMA_TYPE_RESIDUALS
    SCHEMA_VERSION = "1.0.0"

    EDGES = "bin_edges"
    COUNTS = "bin_counts"
    MEAN = "mean"
    STDDEV = "stddev"
    RES_COUNT = "res_count"

    def compute(self) -> Dict[str, Any]:
        """Compute the score for the metric."""
        if self._y_std is None:
            raise DataErrorException(
                "y_std required to compute Residuals",
                target="_y_std", reference_code="_forecasting.ForecastResiduals.compute",
                has_pii=False)

        num_bins = 10
        # If full dataset targets are all zero we still need a bin
        y_std = self._y_std if self._y_std != 0 else 1

        self._data = {}
        grouped_values = self._group_raw_by_horizon()
        for h in grouped_values:
            self._data[h] = {}
            partial_residuals = np.array(grouped_values[h][ForecastingMetric.y_pred_str]) - np.array(
                grouped_values[h][ForecastingMetric.y_test_str]
            )
            mean = np.mean(partial_residuals)
            stddev = np.std(partial_residuals)
            res_count = len(partial_residuals)

            counts, edges = _regression.Residuals._hist_by_bound(partial_residuals, 2 * y_std, num_bins)
            _regression.Residuals._simplify_edges(partial_residuals, edges)
            self._data[h][ForecastResiduals.EDGES] = edges
            self._data[h][ForecastResiduals.COUNTS] = counts
            self._data[h][ForecastResiduals.MEAN] = mean
            self._data[h][ForecastResiduals.STDDEV] = stddev
            self._data[h][ForecastResiduals.RES_COUNT] = res_count

        ret = NonScalarMetric._data_to_dict(
            ForecastResiduals.SCHEMA_TYPE, ForecastResiduals.SCHEMA_VERSION, self._data
        )
        return cast(Dict[str, Any], _scoring_utilities.make_json_safe(ret))

    @staticmethod
    def aggregate(scores: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Fold several scores from a computed metric together.

        :param scores: List of computed scores.
        :return: Aggregated score.
        """
        if not Metric.check_aggregate_scores(scores, constants.Metric.ForecastResiduals):
            return NonScalarMetric.get_error_metric()

        score_data = [score[NonScalarMetric.DATA] for score in scores]
        grouped_data = ForecastingMetric._group_scores_by_horizon(score_data)

        data = {}
        for horizon in grouped_data:
            # convert data to how residuals expects
            partial_scores = [{NonScalarMetric.DATA: fold_data} for fold_data in grouped_data[horizon]]
            # use aggregate from residuals
            data[horizon] = _regression.Residuals.aggregate(partial_scores)[NonScalarMetric.DATA]

        ret = NonScalarMetric._data_to_dict(ForecastResiduals.SCHEMA_TYPE, ForecastResiduals.SCHEMA_VERSION, data)
        return cast(Dict[str, Any], _scoring_utilities.make_json_safe(ret))


class ForecastTable(ForecastingMetric, NonScalarMetric):
    """The table, containing the list of true and predicted values."""
    SCHEMA_TYPE = constants.SCHEMA_TYPE_FORECAST_HORIZON_TABLE
    SCHEMA_VERSION = '1.0.0'
    MAX_CROSS_VALIDATION_FOLDS = 5
    MAX_FORECAST_TRAIN_DATA_POINTS = 20  # Showing at most 20 training data points
    MAX_FORECAST_VALID_DATA_POINTS = 80  # limited by UI, showing up to 80 validate data points per grain
    MAX_FORECAST_GRAINS = 20

    def compute(self) -> Dict[str, Any]:
        """ Gather train table metrics for a single fold"""
        try:
            from scipy.stats import norm
        except ImportError:
            safe_message = "Tabular packages are not available. " \
                           "Please run pip install azureml-metrics[tabular]"
            raise MissingDependencies(
                safe_message, safe_message=safe_message
            )

        if self._X_train is None or self._y_train is None:
            raise TimeseriesTableTrainAbsent(
                exception_message="X_train/y_train is required to compute ForecastTable",
                target="_train_data",
                reference_code=ReferenceCodes._TS_METRIX_NO_TRAIN)

        if self._time_series_id_column_names is None:
            raise ForecastMetricGrainAbsent(
                exception_message="grain column name is required to compute ForecastTable",
                target="_grain_column_name",
                reference_code=ReferenceCodes._TS_METRIX_NO_GRAIN)

        if self._X_test is None or self._y_test is None or self._y_pred is None:
            raise ForecastMetricValidAbsent(
                exception_message="X_test/y_test/y_pred is required to compute ForecastTable",
                target="_valid_data",
                reference_code=ReferenceCodes._TS_METRIX_NO_VALID)
        # time col and grain col are stored in index
        df_train = self._X_train.index.to_frame(index=False)
        df_train['y_true'] = self._y_train

        df_valid = self._X_test.index.to_frame(index=False)
        df_valid['y_true'] = self._y_test
        df_valid['y_pred'] = self._y_pred
        groupby_valid = df_valid.groupby(self._time_series_id_column_names)

        grain_column_names = self.convert_to_list_of_str(self._time_series_id_column_names)
        self._data = {'time': [],
                      'grain_names': grain_column_names,
                      'grain_value_list': [],
                      'y_true': [],
                      'y_pred': [],
                      'PI_upper_bound': [],
                      'PI_lower_bound': []
                      }
        # For UI purpose, we are calculateing intervals for each fold using the residuals from each fold, in sequence.
        # But these estimates are likely to be noisy because we can't calculate PIs until we have predictions
        # from all cv folds which is the nature of the estimation process.
        z_score = norm.ppf(0.05)
        for igrain, (grain, df_one_train) in enumerate(df_train.groupby(grain_column_names)):
            # If user has provided the valid data set, missing given grain,
            # do not show it in the visual.
            if grain not in groupby_valid.groups.keys():
                continue
            # add built-in mechanism for lowering the cap on grains
            if igrain >= ForecastTable.MAX_FORECAST_GRAINS:
                break
            df_one_valid = groupby_valid.get_group(grain)
            # We may have introduced multiple horizons during training, here we are
            # removing it.
            # For validation set the horizons were already removed.
            if self._origin_column_name and self._origin_column_name in df_train.columns:
                ix = [self._time_column_name]
                if self._time_series_id_column_names:
                    ix.extend(self._time_series_id_column_names)
                ix.append(self._origin_column_name)
                df_one_train.set_index(ix, inplace=True)
                df_one_train = self._select_latest_origin_dates(df_one_train)
                df_one_train.reset_index(inplace=True, drop=False)

            df_one_train.sort_values(by=self._time_column_name, ascending=True, inplace=True)

            df_one_train_trimmed = df_one_train.iloc[-ForecastTable.MAX_FORECAST_TRAIN_DATA_POINTS:]
            df_one_valid = df_one_valid.iloc[:ForecastTable.MAX_FORECAST_VALID_DATA_POINTS]
            df_one = pd.concat([df_one_train_trimmed, df_one_valid], sort=False, ignore_index=True)

            grain_vals = self.convert_to_list_of_str(grain)

            self._data['grain_value_list'].append(grain_vals)

            y_true_list = list(df_one_valid['y_true'].astype(float).values)
            y_pred_list = list(df_one_valid['y_pred'].astype(float).values)
            stddev = np.std([a - b for a, b in zip(y_true_list, y_pred_list)])  # compute std(y_true, y_pred)
            if stddev == 0:
                # If all residuals are the same, we will clculate the residuals of training set.
                resid_train = df_one_train['y_true'].values - y_pred_list[-1]
                stddev = np.std(resid_train)
            # we introduce horizon in PI computation since the further the forecast date,
            # the less confident of the prediction we have.
            ci_bound = abs(z_score * stddev * np.sqrt(np.arange(1, len(y_pred_list) + 1)))
            PI_upper_bound = [a + b for a, b in zip(y_pred_list, ci_bound)]
            PI_lower_bound = [a - b for a, b in zip(y_pred_list, ci_bound)]
            self._data['y_true'].append(round(df_one['y_true'], 2).astype(float).values)
            self._data['y_pred'].append(y_pred_list)
            self._data['PI_upper_bound'].append(PI_upper_bound)
            self._data['PI_lower_bound'].append(PI_lower_bound)

            # convert time column to "iso" format and extract the last train_length values
            self._data['time'].append(list(df_one[self._time_column_name].apply(lambda x: x.isoformat())))

        ret = NonScalarMetric._data_to_dict(
            ForecastTable.SCHEMA_TYPE,
            ForecastTable.SCHEMA_VERSION,
            self._data)
        return cast(Dict[str, Any], _scoring_utilities.make_json_safe(ret))

    def _select_latest_origin_dates(self, X: pd.DataFrame) -> pd.DataFrame:
        """
        Select rows from X with latest origin times within time-grain groups.

        Logic: Group X by time, grain -> Find latest origin in each group
        -> Return row containing latest origin for each group.
        """
        expected_lvls = [self._time_column_name] + self._time_series_id_column_names + [self._origin_column_name]
        Contract.assert_true(
            list(X.index.names) == expected_lvls,
            "X.index doesn't contain expected levels.",
            log_safe=True
        )

        keys = [self._time_column_name] + self._time_series_id_column_names

        def get_origin_vals(df: pd.DataFrame) -> pd.DatetimeIndex:
            return df.index.get_level_values(self._origin_column_name)

        # Pandas groupby no longer allows `by` to contain keys which are both column and index values (0.24)
        # pandas.pydata.org/pandas-docs/stable/whatsnew/v0.24.0.html#removal-of-prior-version-deprecations-changes
        # One way around this is to use the Grouper.
        groupers = []
        for key in keys:
            groupers.append(pd.Grouper(level=key))
        return (X.groupby(groupers, group_keys=False)
                .apply(lambda df: df[get_origin_vals(df) == get_origin_vals(df).max()]))

    @staticmethod
    def aggregate(
        scores: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Fold several scores from a computed metric together.

        :param scores: List of computed table metrics.
        :return: Aggregated table metrics.
        """
        if not Metric.check_aggregate_scores(scores, constants.Metric.ForecastTable):
            return NonScalarMetric.get_error_metric()

        score_data = [score[NonScalarMetric.DATA] for score in scores][:ForecastTable.MAX_CROSS_VALIDATION_FOLDS]
        # only store up to 5 folds data

        ret = NonScalarMetric._data_to_dict(
            ForecastTable.SCHEMA_TYPE,
            ForecastTable.SCHEMA_VERSION,
            score_data)
        return cast(Dict[str, Any], _scoring_utilities.make_json_safe(ret))


class _NormalizedRegressorWrapper(ForecastingMetric, ScalarMetric):
    """
        The internal class to wrap the scalar regressor metric to calculate it by grain.

        :param y_test: True labels for the test set.
        :param y_pred: Predictions for each sample.
        :param horizons: The integer horizon alligned to each y_test. These values should be computed
            by the timeseries transformer. If the timeseries transformer does not compute a horizon,
            ensure all values are the same (ie. every y_test should be horizon 1.)
        :param y_min_dict: The dictionary with minimal target values by grain.
        :param y_max_dict: The dictionary with maximal target values by grain.
        :param y_std: Standard deviation of the targets.
        :param sample_weight: Weighting of each sample in the calculation.
        :param X_test: The inputs which were used to compute the predictions.
        :param X_train: The inputs which were used to train the model.
        :param y_train: The targets which were used to train the model.
        :param time_series_id_column_names: The time series id column names also known as
                                            grain column names.
        :param time_column_name: The time column name.
        :param origin_column_name: The origin time column name.
        :param metric_class: The scalar metric to wrap.
        :param aggregation_function: The function used to aggregate by grain metrics.
        """

    def __init__(
            self,
            y_test: np.ndarray,
            y_pred: np.ndarray,
            horizons: np.ndarray,
            y_min_dict: Dict[Union[str, Tuple[str]], float],
            y_max_dict: Dict[Union[str, Tuple[str]], float],
            metric_class: Type,
            aggregation_function: Callable[[Sequence[float]], float],
            sample_weight: Optional[np.ndarray] = None,
            X_test: Optional[pd.DataFrame] = None,
            X_train: Optional[pd.DataFrame] = None,
            y_train: Optional[np.ndarray] = None,
            time_series_id_column_names: Optional[List[str]] = None,
            time_column_name: Optional[str] = None,
            origin_column_name: Optional[Any] = None,
    ) -> None:
        super().__init__(
            y_test,
            y_pred,
            horizons,
            sample_weight=sample_weight,
            X_test=X_test,
            X_train=X_train,
            y_train=y_train,
            time_series_id_column_names=time_series_id_column_names,
            time_column_name=time_column_name,
            origin_column_name=origin_column_name)
        self._y_min_dict = y_min_dict
        self._y_max_dict = y_max_dict
        self._metric_class = metric_class
        self._aggregation_function = aggregation_function

    def compute(self) -> float:
        """Calculate grain-aware scalar metric."""
        if self._time_series_id_column_names is None:
            raise ForecastMetricGrainAbsent(
                exception_message="grain column name is required to compute normalized metric",
                target="_grain_column_name",
                reference_code=ReferenceCodes._TS_METRIX_WRAPPER_NO_GRAIN)

        if self._X_test is None or self._y_test is None or self._y_pred is None:
            raise ForecastMetricValidAbsent(
                exception_message="X_test/y_test/y_pred is required to compute normalized metric",
                target="_valid_data",
                reference_code=ReferenceCodes._TS_METRIX_WRAPPER_NO_VALID)
        metrics = []
        self._X_test['actuals'] = self._y_test
        self._X_test['predictions'] = self._y_pred
        for ts_id, df_one in self._X_test.groupby(self._time_series_id_column_names):
            y_act_one = df_one.pop('actuals').values
            y_pred_one = df_one.pop('predictions').values
            y_min_gr = self._y_min_dict.get(ts_id, np.min(y_act_one))
            y_max_gr = self._y_max_dict.get(ts_id, np.max(y_act_one))
            metric_inst = self._metric_class(y_act_one, y_pred_one, y_min=y_min_gr, y_max=y_max_gr, y_std=self._y_std,
                                             sample_weight=self._sample_weight)
            metrics.append(metric_inst.compute())
        self._X_test.drop(['actuals', 'predictions'], axis=1, inplace=True)
        return float(self._aggregation_function(metrics))


class ForecastTsIDDistributionTable(ForecastingMetric, NonScalarMetric):
    """Metric distribution by grain and forecast horizon.

    :param y_test: True labels for the test set.
    :param y_pred: Predictions for each sample.
    :param horizons: The integer horizon alligned to each y_test. These values should be computed
        by the timeseries transformer. If the timeseries transformer does not compute a horizon,
        ensure all values are the same (ie. every y_test should be horizon 1.)
    :param y_min_dict: The dictionary with minimal target values by grain.
    :param y_max_dict: The dictionary with maximal target values by grain.
    :param y_std: Standard deviation of the targets.
    :param sample_weight: Weighting of each sample in the calculation.
    :param X_test: The inputs which were used to compute the predictions.
    :param X_train: The inputs which were used to train the model.
    :param y_train: The targets which were used to train the model.
    :param time_series_id_column_names: The time series id column names also known as
                                        grain column names.
    :param time_column_name: The time column name.
    :param origin_column_name: The origin time column name.
    :param metric_class: The scalar metric to wrap.
    :param aggregation_function: The function used to aggregate by grain metrics.
    """

    SCHEMA_TYPE = constants.SCHEMA_TYPE_DISTRIBUTION_TABLE
    SCHEMA_VERSION = "1.0.0"

    _ACTUALS = 'actuals'
    _PREDICTIONS = 'predictions'

    def __init__(
            self,
            y_test: np.ndarray,
            y_pred: np.ndarray,
            horizons: np.ndarray,
            sample_weight: Optional[np.ndarray] = None,
            X_test: Optional[pd.DataFrame] = None,
            X_train: Optional[pd.DataFrame] = None,
            y_train: Optional[np.ndarray] = None,
            time_series_id_column_names: Optional[List[str]] = None,
            time_column_name: Optional[str] = None,
            origin_column_name: Optional[Any] = None,
            y_min_dict: Optional[Dict[Union[str, Tuple[str]], float]] = None,
            y_max_dict: Optional[Dict[Union[str, Tuple[str]], float]] = None,
            **kwargs
    ) -> None:
        super().__init__(
            y_test,
            y_pred,
            horizons,
            sample_weight=sample_weight,
            X_test=X_test,
            X_train=X_train,
            y_train=y_train,
            time_series_id_column_names=time_series_id_column_names,
            time_column_name=time_column_name,
            origin_column_name=origin_column_name,
            **kwargs)
        self._y_min_dict = y_min_dict if y_min_dict else {}
        self._y_max_dict = y_max_dict if y_max_dict else {}

    def _compute_all_regression_metrics(
            self,
            data: pd.DataFrame,
            y_min: float,
            y_max: float,
            time_series_id_dict: Dict[str, Any]) -> Dict[str, float]:
        """
        Calculate all the regression metrics for one time series.

        :param data: The data frame, containing predictions and ground truth.
        :param y_min: Minimal actual value to be used for normalization.
        :param y_max: Maximal actual value to be used for normalization.
        :param time_series_id_dict: The dictionary containing
                                    ts_id -> value columns.
        :return: The dictionary with metics.
        """
        actuals = data.pop(ForecastTsIDDistributionTable._ACTUALS).values
        predictions = data.pop(ForecastTsIDDistributionTable._PREDICTIONS).values
        metrics = {}
        for metric_name in constants.Metric.SCALAR_REGRESSION_SET:
            metric_class = _scoring_utilities.get_metric_class(metric_name)
            metrics_inst = metric_class(
                actuals,
                predictions,
                y_min=y_min,
                y_max=y_max,
                y_std=self._y_std,
                sample_weight=self._sample_weight)
            metrics[metric_name] = metrics_inst.compute()
        metrics.update(time_series_id_dict)
        return metrics

    def _to_ts_id_dict(self, time_series_id: Union[Any, Tuple[Any]], ts_id_column_names: List[str]) -> Dict[str, Any]:
        """
        Return the time series ID-s in form of dictionary.

        :param time_series_id: The time series id.
        :param ts_id_column_names: Time series id column names.
        :return: The dictionary column name -> column value
        """
        if not isinstance(time_series_id, tuple):
            time_series_id = [time_series_id]
        return {col: val for col, val in zip(ts_id_column_names, time_series_id)}

    def compute(self) -> Dict[str, Any]:
        """Calculate metrics by grain."""
        if self._time_series_id_column_names is None:
            raise ForecastMetricGrainAbsent(
                exception_message=("Time series ID column name is required "
                                   "to compute Forecast time series ID distribution table"),
                target="_grain_column_name",
                reference_code=ReferenceCodes._TS_METRIX_NO_GRAIN_DISTRIBUTION)
        self._X_test[ForecastTsIDDistributionTable._ACTUALS] = self._y_test
        self._X_test[ForecastTsIDDistributionTable._PREDICTIONS] = self._y_pred
        index = self.convert_to_list_of_str(self._time_series_id_column_names)
        metrics_list = []
        for ts_id, df_one in self._X_test.groupby(index):
            # If we do not have minimum and maximum from the training set, we will use min and max from the test set.
            y_min_gr = self._y_min_dict.get(ts_id, np.min(df_one[ForecastTsIDDistributionTable._ACTUALS].values))
            y_max_gr = self._y_max_dict.get(ts_id, np.max(df_one[ForecastTsIDDistributionTable._ACTUALS].values))
            time_series_id_dict = self._to_ts_id_dict(ts_id, index)
            if constants._TimeSeriesInternal.FORECAST_ORIGIN_COLUMN_NAME in self._X_test.columns:
                for fc_origin, df_one_orig in df_one.groupby(
                        constants._TimeSeriesInternal.FORECAST_ORIGIN_COLUMN_NAME):
                    all_metrics = self._compute_all_regression_metrics(
                        df_one_orig, y_min_gr, y_max_gr, time_series_id_dict)
                    all_metrics[constants._TimeSeriesInternal.FORECAST_ORIGIN_COLUMN_NAME] = fc_origin.isoformat()
                    metrics_list.append(all_metrics)
            else:
                all_metrics = self._compute_all_regression_metrics(df_one, y_min_gr, y_max_gr, time_series_id_dict)
                metrics_list.append(all_metrics)

        self._X_test.drop([ForecastTsIDDistributionTable._ACTUALS,
                           ForecastTsIDDistributionTable._PREDICTIONS], axis=1, inplace=True)
        ret = NonScalarMetric._data_to_dict(
            ForecastTable.SCHEMA_TYPE,
            ForecastTable.SCHEMA_VERSION,
            metrics_list)
        return cast(Dict[str, Any], _scoring_utilities.make_json_safe(ret))

    @staticmethod
    def aggregate(scores: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Fold several scores from a computed metric together.

        :param scores: List of computed scores.
        :return: Aggregated score.
        """
        mt_table = []
        for dt in scores:
            mt_table.extend(dt['data'])

        metrics_df = pd.DataFrame.from_records(mt_table)
        index = list(set(metrics_df.columns) - constants.Metric.SCALAR_REGRESSION_SET)
        data = metrics_df.groupby(index, as_index=False).agg(np.nanmean)
        data_dt = data.to_dict(orient='records')
        ret = NonScalarMetric._data_to_dict(ForecastResiduals.SCHEMA_TYPE, ForecastResiduals.SCHEMA_VERSION, data_dt)
        return cast(Dict[str, Any], _scoring_utilities.make_json_safe(ret))

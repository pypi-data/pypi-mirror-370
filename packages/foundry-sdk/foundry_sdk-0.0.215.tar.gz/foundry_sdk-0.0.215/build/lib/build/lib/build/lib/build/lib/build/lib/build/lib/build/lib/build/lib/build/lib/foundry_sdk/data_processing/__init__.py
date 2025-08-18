"""
Data processing module for foundry_sdk.

This module provides functions for data processing operations including:
- Date manipulation and gap filling
- Time series aggregation at different frequencies
- Outlier detection and removal
- Lag feature creation
"""

from .data_processing import (
    add_date_rows,
    add_lag_features,
    aggregate_by_frequency,
    aggregate_by_frequency_fill_0,
    aggregate_by_frequency_fill_mean,
    check_min_max_dates,
    convert_date_column,
    create_min_max_date_df,
    cut_outliers,
    fill_date_gaps,
    filter_incomplete_periods,
    get_period_end_date,
)

__all__ = [
    "add_date_rows",
    "add_lag_features",
    "aggregate_by_frequency",
    "aggregate_by_frequency_fill_0",
    "aggregate_by_frequency_fill_mean",
    "check_min_max_dates",
    "convert_date_column",
    "create_min_max_date_df",
    "cut_outliers",
    "fill_date_gaps",
    "filter_incomplete_periods",
    "get_period_end_date",
]

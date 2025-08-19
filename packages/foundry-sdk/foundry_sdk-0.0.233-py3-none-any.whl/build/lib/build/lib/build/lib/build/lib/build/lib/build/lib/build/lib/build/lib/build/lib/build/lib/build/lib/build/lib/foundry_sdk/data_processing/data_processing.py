import datetime
import logging
import typing as t

import pandas as pd
import polars as pl

from foundry_sdk.data_processing.constants import FREQUENCY_PL_INTERVAL

# import re
# from tqdm import tqdm

logger = logging.getLogger(__name__)


def add_date_rows(
    df: pl.DataFrame,
    additional_rows: int,
    frequency: str = "monthly",
    date_col: str = "date",
    fixed_id_cols: t.Optional[t.List[str]] = None,
) -> pl.DataFrame:
    """

    Take an exsiting dataframe, for each max date in each fixed_id_cols group add  "additional_rows" addition rows counting the date upwards
    with frequency.

    """

    min_date = df.select(pl.col("date").min()).to_series().item()
    max_date = df.select(pl.col("date").max()).to_series().item()
    end_date = get_period_end_date(start_date=max_date, frequency=frequency, periods=additional_rows)

    extra = pl.date_range(start=min_date, end=end_date, interval=FREQUENCY_PL_INTERVAL[frequency], eager=True)

    extra = pl.DataFrame(
        {
            "date": extra,
        }
    ).with_columns(pl.col("date").cast(pl.Date))

    full_df = extra.join(df.with_columns(pl.col("date").cast(pl.Date)), on="date", how="left")

    if fixed_id_cols:
        full_df = full_df.sort("date")
        full_df = full_df.with_columns(pl.col(col).fill_null(strategy="forward").alias(col) for col in fixed_id_cols)

    return full_df


def get_period_end_date(start_date: datetime.date, frequency: str = "monthly", periods: int = 1) -> datetime.date:
    """
    Get the end date for a given start date and frequency.

    Parameters:
    start_date (datetime.date): The start date.
    frequency (str): The frequency of the period ('daily', 'weekly', 'monthly', 'quarterly', 'yearly').
    periods (int): Number of periods to add.

    Returns:
    datetime.date: The calculated end date.
    """
    if frequency == "daily":
        return start_date + datetime.timedelta(days=periods)
    elif frequency == "weekly":
        return start_date + datetime.timedelta(weeks=periods)
    elif frequency == "monthly":
        return start_date + pd.DateOffset(months=periods)
    elif frequency == "quarterly":
        return start_date + pd.DateOffset(months=3 * (periods))
    elif frequency == "yearly":
        return start_date + pd.DateOffset(years=periods)
    else:
        raise ValueError(f"Unsupported frequency: {frequency}")


def cut_outliers(
    df: pl.DataFrame,
    value_col: str,
    group_by_cols: None | str | t.List[str] = None,
    threshold: float = 3.0,
    absolute_threshold: float = 10.0,
) -> pl.DataFrame:
    if group_by_cols is None:
        group_by_cols = []

    # Calculate the mean and standard deviation per group
    stats = (
        df.group_by(group_by_cols)
        .agg([pl.col(value_col).mean().alias("mean"), pl.col(value_col).std().alias("std")])
        .with_columns((pl.col("mean") + (pl.col("std") * threshold)).alias("cutoff"))
        .with_columns(cutoff=pl.max_horizontal("cutoff", pl.lit(absolute_threshold)))
        .drop(["mean", "std"])
    )

    df = (
        df.join(stats, on=group_by_cols, how="left")
        .with_columns(value_capped=pl.min_horizontal(pl.col(value_col), pl.col("cutoff")))
        .drop(["cutoff"])
    )

    return df


def aggregate_by_frequency(
    df: pl.DataFrame,
    group_by_col: t.Union[str, t.List[str]] = "skuID",
    date_col: str = "date",
    frequencies: t.List[str] = None,
    period_start_end_handling: t.Optional[str] = "omit",  # 'omit' or 'keep'
    na_handling: t.Optional[str] = "fill_0",  # 'fill_0' or 'fill_mean'
    log: bool = True,
) -> pl.DataFrame:
    if isinstance(group_by_col, str):
        group_by_col = [group_by_col]

    if na_handling == "fill_0":
        return aggregate_by_frequency_fill_0(
            df,
            group_by_col=group_by_col,
            date_col=date_col,
            frequencies=frequencies,
            period_start_end_handling=period_start_end_handling,
            log=log,
        )
    elif na_handling == "fill_mean":
        return aggregate_by_frequency_fill_mean(
            df,
            group_by_col=group_by_col,
            date_col=date_col,
            frequencies=frequencies,
            period_start_end_handling=period_start_end_handling,
            log=log,
        )
    else:
        raise ValueError(f"Unsupported na_handling: {na_handling}. Supported values are 'fill_0' or 'fill_mean'.")


def aggregate_by_frequency_fill_0(
    df: pl.DataFrame,
    group_by_col: t.List[str],
    date_col: str = "date",
    frequencies: t.List[str] = None,
    period_start_end_handling: t.Optional[str] = "omit",  # 'omit' or 'keep'
    log: bool = True,
) -> pl.DataFrame:
    """
    Aggregate a DataFrame over multiple time frequencies.

    Parameters
    ----------
    df : pl.DataFrame
        Input DataFrame. Must contain a datetime-like column for dates,
        a grouping column, and a numeric 'value' column.
    group_by_col : str, default "skuID"
        Name of the column to group by (e.g., SKU identifier).
    date_col : str, default "date"
        Name of the column containing dates.
    frequencies : List[str], optional
        List of aggregation frequencies to compute. Supported values:
        ['daily', 'weekly', 'monthly', 'quarterly', 'yearly'].
        If None, defaults to all five frequencies.
    period_start_end_handling : str, optional
        How to handle periods that do not fully cover the range of dates:
        - "omit": Exclude periods that do not fully cover the date range.
        - "keep": Include all periods, even if they are partial.

    Returns
    -------
    pl.DataFrame
        A concatenated DataFrame containing the original or aggregated
        rows for each requested frequency, with an added 'frequency' column.
    """
    default_freqs = ["daily", "weekly", "monthly", "quarterly", "yearly"]
    if frequencies is None:
        frequencies = default_freqs

    df = convert_date_column(df, date_col=date_col)

    original_column_order = df.columns

    value_cols = [col for col in df.columns if col not in group_by_col and col != date_col]

    # Precompute each group's min/max date if we may omit partial periods
    if period_start_end_handling == "omit":
        min_max_df = create_min_max_date_df(df, group_by_col=group_by_col, date_col=date_col)

    period_dfs = []
    for freq in frequencies:
        if freq == "daily":
            # For daily, just tag the rows and keep as-is
            period_df = df.with_columns(pl.lit("daily").alias("frequency"))
            new_column_order = original_column_order + ["frequency"]
            period_df = period_df.select(new_column_order)
            period_dfs.append(period_df)
            continue

        # Map frequency to a truncation string
        if freq == "weekly":
            trunc = "1w"
        elif freq == "monthly":
            trunc = "1mo"
        elif freq == "quarterly":
            trunc = "1q"
        elif freq == "yearly":
            trunc = "1y"
        else:
            raise ValueError(f"Unsupported frequency: {freq}")

        # Truncate dates and sum values within each period and group
        period_df = (
            df.with_columns(pl.col(date_col).dt.truncate(trunc).alias("period_start"))
            .group_by("period_start", *group_by_col)
            .agg(pl.col(value_cols).sum())
            .sort([*group_by_col, "period_start"])
            .rename({"period_start": date_col})
            .with_columns(pl.lit(freq).alias("frequency"))
        )

        if period_start_end_handling == "omit":
            period_df = filter_incomplete_periods(
                period_df, min_max_df, trunc, group_by_col=group_by_col, date_col=date_col
            )

        new_column_order = original_column_order + ["frequency"]
        period_df = period_df.select(new_column_order)
        period_dfs.append(period_df)

    return pl.concat(period_dfs)


def aggregate_by_frequency_fill_mean(
    df: pl.DataFrame,
    group_by_col: t.List[str],
    date_col: str = "date",
    frequencies: t.List[str] = None,
    period_start_end_handling: t.Optional[str] = "omit",  # 'omit' or 'keep'
    log: bool = True,
) -> pl.DataFrame:
    default_freqs = ["daily", "weekly", "monthly", "quarterly", "yearly"]
    if frequencies is None:
        frequencies = default_freqs

    df = convert_date_column(df, date_col=date_col)

    original_column_order = df.columns
    value_cols = [col for col in df.columns if col not in group_by_col and col != date_col]

    if period_start_end_handling == "omit":
        min_max_df = create_min_max_date_df(df, group_by_col=group_by_col, date_col=date_col)

    period_dfs = []
    for freq in frequencies:
        if freq == "daily":
            # For daily, just tag the rows and keep as-is
            period_df = df.with_columns(pl.lit("daily").alias("frequency"))
            new_column_order = original_column_order + ["frequency"]
            period_df = period_df.select(new_column_order)
            period_dfs.append(period_df)
            continue

        # Map frequency to a truncation string
        if freq == "weekly":
            trunc = "1w"
        elif freq == "monthly":
            trunc = "1mo"
        elif freq == "quarterly":
            trunc = "1q"
        elif freq == "yearly":
            trunc = "1y"
        else:
            raise ValueError(f"Unsupported frequency: {freq}")

        # Truncate dates and sum values within each period and group
        period_df = (
            df.with_columns(pl.col(date_col).dt.truncate(trunc).alias("period_start"))
            .with_columns(pl.col("period_start").dt.offset_by(trunc).alias("period_end_plus_one"))
            .with_columns(
                (pl.col("period_end_plus_one") - pl.col("period_start")).dt.total_days().alias("days_in_period")
            )
            .group_by("period_start", *group_by_col)
            .agg(
                [
                    pl.col("days_in_period").first().alias("days_in_period"),
                    *[(pl.col(col).mean() * pl.col("days_in_period").first()).alias(col) for col in value_cols],
                ]
            )
            .sort([*group_by_col, "period_start"])
            .rename({"period_start": date_col})
            .with_columns(pl.lit(freq).alias("frequency"))
        )

        period_df = period_df.drop("days_in_period")

        if period_start_end_handling == "omit":
            period_df = filter_incomplete_periods(
                period_df, min_max_df, trunc, group_by_col=group_by_col, date_col=date_col
            )

        new_column_order = original_column_order + ["frequency"]
        period_df = period_df.select(new_column_order)
        period_dfs.append(period_df)

    # Concatenate all frequencies together
    return pl.concat(period_dfs)


def filter_incomplete_periods(
    df: pl.DataFrame,
    min_max_df: pl.DataFrame,
    trunc: str = "1d",
    group_by_col: t.List[str] = ["skuID"],
    date_col: str = "date",
) -> pl.DataFrame:
    df = (
        df.join(min_max_df, on=group_by_col, how="left")
        .with_columns(pl.col(date_col).dt.offset_by(trunc).dt.offset_by("-1d").alias("period_end"))
        .filter((pl.col(date_col) >= pl.col("min_date")) & (pl.col("period_end") <= pl.col("max_date")))
    )

    return df.drop(["min_date", "max_date"])


def create_min_max_date_df(
    df: pl.DataFrame, group_by_col: t.List[str] = ["skuID"], date_col: str = "date"
) -> pl.DataFrame:
    """
    Create a DataFrame with the minimum and maximum dates for each SKU.
    """

    min_max_df = df.group_by(*group_by_col).agg(
        pl.col(date_col).min().alias("min_date"), pl.col(date_col).max().alias("max_date")
    )

    return min_max_df


def convert_date_column(df: pl.DataFrame, date_col: str = "date") -> None:
    """
    Convert the date column to datetime type if it is not already.
    """
    if date_col not in df.columns:
        raise ValueError(f"Column '{date_col}' not found in DataFrame.")

    if df[date_col].dtype != pl.Datetime:
        if df[date_col].dtype == pl.Utf8:
            df = df.with_columns(pl.col(date_col).str.to_datetime())
        else:
            df = df.with_columns(pl.col(date_col).cast(pl.Datetime))
    return df


def fill_date_gaps(
    df: pl.DataFrame,
    group_by_col: str | list[str] = "skuID",
    date_col: str = "date",
    frequency: str = "daily",
    log: bool = True,
    global_min_max: bool = False
) -> pl.DataFrame:
    """
    Fill in missing dates for each SKU in the DataFrame.

    Parameters:
    df (pl.DataFrame): Input DataFrame with 'skuID' and 'date' columns.
    group_by (str): Column name to group by (default is 'skuID').
    global_min_max (bool): Whether to use global min/max of min/max per group (default is False).

    Returns:
    pl.DataFrame: DataFrame with filled date gaps.
    """
    if isinstance(group_by_col, str):
        group_by_col = [group_by_col]

    length_df = df.shape[0]

    # check if type of date is string
    if df[date_col].dtype == pl.String:
        df = df.with_columns(pl.col(date_col).str.strptime(pl.Date, format="%Y-%m-%d"))
    elif df[date_col].dtype != pl.Date:
        df = df.with_columns(pl.col(date_col).cast(pl.Date))

    # Compute ranges: group-wise or global
    if global_min_max:
        min_date = df[date_col].min()
        max_date = df[date_col].max()
        ranges = df.select(group_by_col).unique()
        ranges = ranges.with_columns(
            pl.lit(min_date).alias("min_date"),
            pl.lit(max_date).alias("max_date"),
        )
    else:
        ranges = df.group_by(*group_by_col).agg(
            [
                pl.col(date_col).min().alias("min_date"),
                pl.col(date_col).max().alias("max_date"),
            ]
        )

    check_min_max_dates(ranges, frequency)

    ranges_expanded = (
        ranges.with_columns(
            pl.date_ranges(pl.col("min_date"), pl.col("max_date"), interval=FREQUENCY_PL_INTERVAL[frequency]).alias(
                date_col
            )
        )
        .explode(date_col)
        .select([*group_by_col, date_col])
    )

    # 4) left-join back to original to bring in existing values (missing → null)
    full = ranges_expanded.join(df, on=[*group_by_col, date_col], how="left").sort([*group_by_col, date_col])

    length_full = full.shape[0]

    if log:
        logger.info(f"Original DataFrame length: {length_df}, Filled DataFrame length: {length_full}")

    return full


def check_min_max_dates(ranges: pl.DataFrame, cols_to_check: str | t.List[str], frequency: str = "daily") -> None:
    """
    Checks if the values in cols_to_check are valid for the given frequency. It checks:

    daily: no check
    weekly: dates must be mondays
    monthly: dates must be first of the month
    quarterly: dates must be first of the month in January, April, July, October
    yearly: dates must be first of the month in January
    """

    if isinstance(cols_to_check, str):
        cols_to_check = [cols_to_check]

    if frequency == "daily":
        return
    elif frequency == "weekly":
        for col in cols_to_check:
            if not all(ranges[col].dt.weekday() == 0):  # 0 is Monday
                raise ValueError(f"Column '{col}' must contain dates that are Mondays for weekly frequency.")
    elif frequency == "monthly":
        for col in cols_to_check:
            if not all(ranges[col].dt.day() == 1):
                raise ValueError(f"Column '{col}' must contain the first day of the month for monthly frequency.")
    elif frequency == "quarterly":
        for col in cols_to_check:
            if not all(ranges[col].dt.month().is_in([1, 4, 7, 10]) & (ranges[col].dt.day() == 1)):
                raise ValueError(
                    f"Column '{col}' must contain the first day of January, April, July, or October for quarterly frequency."
                )
    elif frequency == "yearly":
        for col in cols_to_check:
            if not all(ranges[col].dt.month() == 1 & (ranges[col].dt.day() == 1)):
                raise ValueError(f"Column '{col}' must contain the first day of January for yearly frequency.")
    else:
        raise ValueError(f"Unsupported frequency: {frequency}")


def add_lag_features(
    df: pl.DataFrame,
    lags: int | t.List[int] | range = 1,
    group_by_cols: t.List[str] = None,
    value_col: str = "value",
    date_col: str = "date",
) -> pl.DataFrame:
    """
    Add lag features to a DataFrame.

    Parameters
    ----------
    df : pl.DataFrame
        Input DataFrame containing time series data.
    value_col : str, default "value"
        Name of the column to create lag features for.
    group_by_cols : List[str], optional
        List of columns to group by when creating lags. If None, defaults to
        ["skuID", "frequency"] if both exist, otherwise ["skuID"].
    date_col : str, default "date"
        Name of the date column used for sorting.
    lags : Union[int, List[int], range], optional
        Lag periods to create. If int, creates lags from 1 to that number.
        If List[int] or range, creates lags for those specific values.
        If None, defaults to range(1, 8).

    Returns
    -------
    pl.DataFrame
        DataFrame with added lag columns named "{value_col}_lag_{lag}".
    """

    # Handle default parameters
    if group_by_cols is None:
        group_by_cols = ["skuID", "frequency"]

    sort_cols = group_by_cols + [date_col]

    # Validate that required columns exist
    missing_cols = [col for col in sort_cols + [value_col] if col not in df.columns]
    if missing_cols:
        raise ValueError(f"Missing columns in DataFrame: {missing_cols}")

    # Sort the DataFrame
    df_sorted = df.sort(sort_cols)

    if len(group_by_cols) == 0:
        lag_features = [pl.col(value_col).shift(lag).alias(f"{value_col}_lag_{lag}") for lag in lags]
    else:
        lag_features = [
            pl.col(value_col).shift(lag).over(group_by_cols).alias(f"{value_col}_lag_{lag}") for lag in lags
        ]

    # Add lag columns to the DataFrame
    result = df_sorted.with_columns(lag_features)

    return result

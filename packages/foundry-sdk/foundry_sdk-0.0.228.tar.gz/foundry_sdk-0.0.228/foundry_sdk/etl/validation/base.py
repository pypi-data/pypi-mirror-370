import typing as t
import pandas as pd


def validate_dataframe_columns(
    df: pd.DataFrame, 
    expected_columns: t.List[str], 
    expected_types: t.List[t.Type],
    dataframe_name: str, 
    allow_additional: bool = False,
    additional_types: t.Optional[t.List[t.Type]] = None
) -> pd.DataFrame:

    """
    Validates that the DataFrame contains the expected columns. 
    If `allow_additional` is False, the DataFrame must contain exactly the expected columns.
    If `allow_additional` is True, additional columns are allowed, but the expected ones must be present.

    Parameters:
        df (pd.DataFrame): The DataFrame to validate.
        expected_columns (List[str]): The list of expected column names.
        dataframe_name (str): Name of the DataFrame (used for error messages).
        allow_additional (bool): Whether to allow additional columns beyond the expected ones.

    Returns:
        pd.DataFrame: The DataFrame with expected columns in order, followed by any additional columns.
    """
    
    missing_columns = [col for col in expected_columns if col not in df.columns]
    
    if missing_columns:
        raise ValueError(
            f"Columns for dataframe {dataframe_name} are missing. "
            f"Expected: {expected_columns}, Found: {list(df.columns)}"
        )
    
    if not allow_additional:
        if set(df.columns) != set(expected_columns):
            raise ValueError(
                f"Columns for dataframe {dataframe_name} do not match exactly. "
                f"Expected: {expected_columns}, Found: {list(df.columns)}"
            )
        
        # order columns
        df = df[expected_columns]

        if len(df) == 0:
            return df
        for col, expected_type in zip(df.columns, expected_types):
            actual_dtype = df[col].dtype

            # Allow both pd.Timestamp and datetime64[ns]
            if expected_type == pd.Timestamp and not (actual_dtype == "datetime64[ns]" or isinstance(df[col].iloc[0], pd.Timestamp)):
                raise ValueError(
                    f"Column '{col}' in dataframe {dataframe_name} has an unexpected type. "
                    f"Expected: {expected_type}, Found: {actual_dtype}"
                )
            elif expected_type != pd.Timestamp and not are_types_compatible(actual_dtype, expected_type):
                raise ValueError(
                    f"Column '{col}' in dataframe {dataframe_name} has an unexpected type. "
                    f"Expected: {expected_type}, Found: {actual_dtype}"
                )

        return df

    else:
        # Check that all expected columns are present
        missing_columns = [col for col in expected_columns if col not in df.columns]
        if missing_columns:
            raise ValueError(
                f"Columns for dataframe {dataframe_name} are missing. "
                f"Expected: {expected_columns}, Found: {list(df.columns)}"
            )

        # Reorder DataFrame so expected columns come first
        additional_columns = [col for col in df.columns if col not in expected_columns]
        df = df[expected_columns + additional_columns]

        if len(df) == 0:
            return df

        # Check type for expected columns
        for col, expected_type in zip(expected_columns, expected_types):
            actual_dtype = df[col].dtype

            # Allow both pd.Timestamp and datetime64[ns]
            if expected_type == pd.Timestamp:
                if not (actual_dtype == "datetime64[ns]" or isinstance(df[col].dropna().iloc[0], pd.Timestamp)):
                    raise ValueError(
                        f"Column '{col}' in dataframe {dataframe_name} has an unexpected type. "
                        f"Expected: {expected_type} (or datetime64[ns]), Found: {actual_dtype}"
                    )
            elif not are_types_compatible(actual_dtype, expected_type):
                raise ValueError(
                    f"Column '{col}' in dataframe {dataframe_name} has an unexpected type. "
                    f"Expected: {expected_type}, Found: {actual_dtype}"
                )


        # Check additional column types if provided
        if additional_types is not None:
            if len(additional_columns) != len(additional_types):
                raise ValueError(
                    f"Mismatch between number of additional columns and additional_types for dataframe {dataframe_name}. "
                    f"Expected {len(additional_types)} additional columns but found {len(additional_columns)}."
                )
            for col, additional_type in zip(additional_columns, additional_types):
                if not df[col].dtype == additional_type:
                    raise ValueError(
                        f"Additional column '{col}' in dataframe {dataframe_name} has an unexpected type. "
                        f"Expected: {additional_type}, Found: {df[col].dtype}"
                    )
        return df

def are_types_compatible(actual_dtype, expected_type):
    string_types = {'object', 'str', 'string'}
    int_types = {'int', 'int64', 'int32', 'int16', 'int8'}
    float_types = {'float', 'float64', 'float32', 'float16'}

    # Normalize actual_dtype to string
    if isinstance(actual_dtype, pd.api.extensions.ExtensionDtype):
        actual_dtype = actual_dtype.name
    elif hasattr(actual_dtype, "name"):
        actual_dtype = actual_dtype.name
    elif isinstance(actual_dtype, type):
        actual_dtype = actual_dtype.__name__
    else:
        actual_dtype = str(actual_dtype)

    # Normalize expected_type to string
    if isinstance(expected_type, type):
        expected_type_str = expected_type.__name__
    else:
        expected_type_str = str(expected_type)

    # Compatibility checks
    return (
        actual_dtype == expected_type_str or
        (actual_dtype in string_types and expected_type_str in string_types) or
        (actual_dtype in int_types and expected_type_str in int_types) or
        (actual_dtype in float_types and expected_type_str in float_types)
    )

def encode_boolean_values(df: pd.DataFrame, columns="value") -> pd.DataFrame:
    """
    Converts boolean-like values in specified columns of the DataFrame to string "1"/"0",
    and converts all other values to strings—except for missing/null values.

    Parameters:
        df (pd.DataFrame): The DataFrame to process.
        columns (str or list of str): Column name(s) to apply the transformation.

    Returns:
        pd.DataFrame: The DataFrame with updated columns.
    """

    mapping = {
        True: "1", "True": "1", "true": "1", "1": "1",
        False: "0", "False": "0", "false": "0", "0": "0"
    }

    def convert_value(val):
        return mapping.get(val, val)

    # Normalize columns to list
    if isinstance(columns, str):
        columns = [columns]

    df = df.copy()  # To avoid modifying original DataFrame
    for col in columns:
        df[col] = df[col].map(convert_value).astype("string")

    return df
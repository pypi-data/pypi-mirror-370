from typing import Any, Dict, List, Tuple
import pandas as pd

def verify_dataframe_parsing(
    df: pd.DataFrame,
    grouped_dataframes: Dict[Any, pd.DataFrame],
    activity_name_col="activity_name",
) -> Tuple[bool, Dict[str, set]]:
    """
    Verify that activity names in the parsed JSON match those in the grouped DataFrame keys.

    Parameters:
        df (pd.DataFrame): The input DataFrame containing an 'activity_name' column.
        grouped_dataframes (dict): A dictionary where keys are activity names and values are DataFrames.

    Returns:
        Tuple[bool, dict]: A tuple containing:
            - A boolean indicating if the activity names match.
            - A dictionary with the sets of activity names for debugging.
    """
    # Extract unique activity names from the DataFrame and grouped DataFrames
    activity_names_parsed_json = set(df[activity_name_col].unique())
    activity_names_grouped_df = set(grouped_dataframes.keys())

    # Store the names for debugging purposes
    names = {
        "parsed_json": activity_names_parsed_json,
        "grouped_df": activity_names_grouped_df,
    }

    # Compare the two sets of activity names
    validation = activity_names_parsed_json == activity_names_grouped_df

    return validation, names


def validate_input(df: Any, required_columns: List[str] = None) -> None:
    """
    Validate that the input is a DataFrame and contains the required columns.

    Parameters:
        df (Any): The input to validate.
        required_columns (list, optional): A list of required column names.

    Raises:
        TypeError: If the input is not a pandas DataFrame.
        ValueError: If any required columns are missing.
    """
    if not isinstance(df, pd.DataFrame):
        raise TypeError("Input must be a pandas DataFrame.")

    if required_columns:
        missing = [col for col in required_columns if col not in df.columns]
        if missing:
            raise ValueError(f"Missing required columns: {missing}")

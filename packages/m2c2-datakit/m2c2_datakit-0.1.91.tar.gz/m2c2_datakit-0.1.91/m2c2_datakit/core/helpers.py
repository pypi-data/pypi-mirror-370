import json
import zipfile
from datetime import date
from typing import Any, Callable, Dict, List, Tuple

import pandas as pd
import pyreadr

from .config import settings
from .utils import compute_md5_hash, get_uuid


def list_zip_contents(zip_path: str) -> Dict[str, int]:
    """
    List the contents and file sizes within a zip archive.

    Args:
        zip_path (str): Path to the zip file.

    Returns:
        Dict[str, int]: Dictionary mapping filenames to file sizes in bytes.
    """
    with zipfile.ZipFile(zip_path, "r") as zip_ref:
        return {name: zip_ref.getinfo(name).file_size for name in zip_ref.namelist()}


def read_zip_files(
    zip_path: str, zip_contents: Dict[str, int]
) -> Dict[str, pd.DataFrame]:
    """
    Read pipe-delimited files from a zip archive into DataFrames.

    Args:
        zip_path (str): Path to the zip file.
        zip_contents (Dict[str, int]): List of files to read.

    Returns:
        Dict[str, pd.DataFrame]: Dictionary of DataFrames keyed by filename.
    """
    file_data = {}
    with zipfile.ZipFile(zip_path, "r") as zip_ref:
        for file_name in zip_contents:
            with zip_ref.open(file_name) as f:
                df = pd.read_csv(f, delimiter="|")
                file_data[file_name] = df
                print(f"[INFO] Loaded {file_name} with {len(df)} rows.")
    return file_data


def parse_json_to_dfs(
    df: pd.DataFrame, activity_name_col: str = "activity_name"
) -> Dict[str, pd.DataFrame]:
    """
    Split a DataFrame into multiple DataFrames based on unique values in a column.

    Args:
        df (pd.DataFrame): The input DataFrame.
        activity_name_col (str): The column used for splitting.

    Returns:
        Dict[str, pd.DataFrame]: Dictionary of DataFrames keyed by activity name.
    """
    return {
        name: group.reset_index(drop=True)
        for name, group in df.groupby(activity_name_col)
    }


def parse_trial_data(json_str):
    try:
        return json.loads(json_str)
    except (json.JSONDecodeError, TypeError):
        return {}


def verify_dataframe_parsing(
    df: pd.DataFrame,
    grouped_dataframes: Dict[Any, pd.DataFrame],
    activity_name_col: str = "activity_name",
) -> Tuple[bool, Dict[str, set]]:
    """
    Verify that grouped DataFrames match the expected activity names.

    Args:
        df (pd.DataFrame): Original ungrouped DataFrame.
        grouped_dataframes (Dict[Any, pd.DataFrame]): Grouped output.
        activity_name_col (str): Column used for grouping.

    Returns:
        Tuple[bool, Dict[str, set]]: Whether the names match and the parsed name sets.
    """
    parsed_names = set(df[activity_name_col].unique())
    grouped_names = set(grouped_dataframes.keys())
    return parsed_names == grouped_names, {
        "parsed_json": parsed_names,
        "grouped_df": grouped_names,
    }


def validate_input(df: Any, required_columns: List[str] = None) -> None:
    """
    Validate that the input is a DataFrame and contains required columns.

    Args:
        df (Any): Object to validate.
        required_columns (List[str], optional): Required columns.

    Raises:
        TypeError: If input is not a DataFrame.
        ValueError: If required columns are missing.
    """
    if not isinstance(df, pd.DataFrame):
        raise TypeError("Input must be a pandas DataFrame.")
    if required_columns:
        missing = [col for col in required_columns if col not in df.columns]
        if missing:
            raise ValueError(f"Missing required columns: {missing}")


def unnest_trial_level_data(
    df: pd.DataFrame, drop_duplicates: bool = True, column_order: List[str] = None
) -> pd.DataFrame:
    """
    Unnest trial-level data from a JSON-like 'content' column containing trials.

    Args:
        df (pd.DataFrame): Input DataFrame with nested content.
        drop_duplicates (bool): Whether to drop duplicate rows.
        column_order (List[str], optional): Column order to prioritize.

    Returns:
        pd.DataFrame: Flattened trial-level DataFrame.
    """
    column_order = column_order or [
        "participant_id",
        "session_id",
        "group",
        "wave",
        "activity_id",
        "study_id",
        "document_uuid",
    ]
    all_trials = [
        trial for _, row in df.iterrows() for trial in row["content"].get("trials", [])
    ]
    trial_df = pd.DataFrame(all_trials)

    prioritized = [col for col in column_order if col in trial_df.columns]
    others = [col for col in trial_df.columns if col not in prioritized]
    trial_df = trial_df[prioritized + others]

    if drop_duplicates:
        trial_df = trial_df.drop_duplicates(
            subset=["activity_uuid", "session_uuid", "trial_begin_iso8601_timestamp"]
        )
    return trial_df


def summarize_common_metadata(x: pd.DataFrame, trials_expected: int, filter: dict) -> Dict[str, Any]:
    """
    Extract shared metadata and trial count checks from a grouped DataFrame.

    Args:
        x (pd.DataFrame): Grouped trial-level DataFrame.
        trials_expected (int): Expected number of trials.

    Returns:
        Dict[str, Any]: Summary metadata and quality flags.
    """
    if "trial_index" in x.columns:
        n_trials = x["trial_index"].nunique()
    else:
        # warnings.warn("No 'trial_index' column found; assuming single-trial task.")
        # For single-trial tasks (like Trailmaking), treat as one trial
        n_trials = 1
    return {
        "activity_begin_iso8601_timestamp": x["activity_begin_iso8601_timestamp"].iloc[
            0
        ],
        "n_trials": n_trials,
        "flag_trials_match_expected": n_trials == trials_expected,
        "flag_trials_lt_expected": n_trials < trials_expected,
        "flag_trials_gt_expected": n_trials > trials_expected,
    }


def read_json_file(file_path: str) -> Any:
    """
    Read and parse a JSON file.

    Args:
        file_path (str): Path to the JSON file.

    Returns:
        Any: Parsed JSON content.
    """
    with open(file_path) as f:
        return json.load(f)


def get_data_from_json_files(json_files: List[str]) -> List[Any]:
    """
    Read multiple JSON files and return a list of their parsed content.

    Args:
        json_files (List[str]): Paths to JSON files.

    Returns:
        List[Any]: List of JSON objects.
    """
    return [read_json_file(file) for file in json_files]


def filter_dataframe(df: pd.DataFrame, **kwargs: Any) -> pd.DataFrame:
    """
    Filter a DataFrame based on column-value criteria.

    Args:
        df (pd.DataFrame): The DataFrame to filter.
        **kwargs (Any): Column=value pairs to filter on. Skips `None` values.

    Returns:
        pd.DataFrame: Filtered DataFrame.

    Raises:
        ValueError: If df is not a DataFrame.

    Example:
        >>> filter_dataframe(df, group='control', wave=2)
    """
    if not isinstance(df, pd.DataFrame):
        raise ValueError("The 'df' parameter must be a pandas DataFrame.")

    for col, val in kwargs.items():
        if col in df.columns and val is not None:
            df = df[df[col] == val]

    return df


def export_dataframe(df, file_name, format=".csv", table_name="my_table", **kwargs):
    """
    Exports a Pandas DataFrame to a specified file format.

    Parameters:
        df (pd.DataFrame): The DataFrame to export.
        file_name (str): The base name (without extension).
        format (str): File format (e.g., '.csv', '.json', '.xlsx', etc.).
        table_name (str): Table name for SQL `INSERT` statements (placeholder).
        **kwargs: Additional keyword arguments for Pandas export functions.

    Returns:
        str: Full path to the exported file.
    """
    try:
        import os

        # Normalize file extension
        if not format.startswith("."):
            format = f".{format}"
        format_l = format.lower()

        file_name_with_extension = f"{file_name}{format}"

        # Export handlers for supported formats
        def export_csv():
            return df.to_csv(file_name_with_extension, index=False, **kwargs)

        def export_json():
            return df.to_json(file_name_with_extension, orient="records", **kwargs)

        def export_xlsx():
            return df.to_excel(file_name_with_extension, index=False, **kwargs)

        def export_parquet():
            return df.to_parquet(file_name_with_extension, index=False, **kwargs)

        def export_html():
            return df.to_html(file_name_with_extension, index=False, **kwargs)

        def export_pkl():
            return df.to_pickle(file_name_with_extension, **kwargs)

        def export_txt():
            return df.to_csv(file_name_with_extension, index=False, sep="\t", **kwargs)

        def export_rdata():
            try:
                import pyreadr

                return pyreadr.write_rdata(
                    file_name_with_extension, df, df_name=os.path.basename(file_name)
                )
            except ImportError:
                raise ImportError(
                    "`pyreadr` is required for exporting to .rdata. Please install it."
                )

        def export_rds():
            try:
                import pyreadr

                return pyreadr.write_rds(file_name_with_extension, df)
            except ImportError:
                raise ImportError(
                    "`pyreadr` is required for exporting to .rds. Please install it."
                )

        exporters = {
            ".csv": export_csv,
            ".json": export_json,
            ".xlsx": export_xlsx,
            ".parquet": export_parquet,
            ".html": export_html,
            ".pkl": export_pkl,
            ".txt": export_txt,
            ".rdata": export_rdata,
            ".rds": export_rds,
        }

        if format_l not in exporters:
            raise ValueError(f"Unsupported file format: {format}")

        # Execute export function
        exporters[format]()
        print(
            f"[EXPORT] DataFrame successfully exported to: {file_name_with_extension}"
        )
        return file_name_with_extension

    except Exception as e:
        print(f"[ERROR] Export failed: {e}")
        return None


def export_jsonld_metadata(df, filename="dataset_metadata.json"):
    today = date.today().isoformat()
    metadata = {
        "@context": "https://schema.org/",
        "@type": "Dataset",
        "name": "M2C2Kit Dataset",
        "description": "This dataset contains M2C2kit data processed via the DataKit Python package.",
        "creator": {"@type": "Person", "name": "Nelson Roque", "affiliation": "M2C2"},
        "dateCreated": today,
        # TODO: make dynamic date
        "variableMeasured": [],
    }

    for col in df.columns:
        metadata["variableMeasured"].append(
            {
                "@type": "PropertyValue",
                "name": col,
                "description": f"Auto-description for {col}",  # you can enrich this
                "value": str(df[col].dtype),
            }
        )

    with open(filename, "w") as f:
        json.dump(metadata, f, indent=2)

    print(f"Metadata saved to {filename}")


# === Metadata & Scoring Utilities ===
def _generate_metadata(df_before: pd.DataFrame, df_after: pd.DataFrame) -> dict:
    return {
        "pkg_batch_id": get_uuid(),
        "pkg_process_timestamp": pd.Timestamp.now(),
        "pkg_process_prehash": compute_md5_hash(df_before),
        "pkg_process_posthash": compute_md5_hash(df_after),
        "pkg_version": settings.PACKAGE_VERSION,
    }


def _append_metadata(df: pd.DataFrame, metadata: dict) -> pd.DataFrame:
    df_meta = df.assign(**metadata)
    return df_meta[
        [col for col in df_meta.columns if not col.startswith("pkg_")]
        + [col for col in df_meta.columns if col.startswith("pkg_")]
    ]


def add_metadata(df: pd.DataFrame) -> pd.DataFrame:
    validate_input(df)
    return _append_metadata(df, _generate_metadata(df, df))


def score(df: pd.DataFrame, metric_name: str, scoring_funcs, **kwargs) -> pd.DataFrame:
    for metric_name, score_func in scoring_funcs:
        df = df.copy()
        df[f"metric_{metric_name}"] = df.apply(score_func, axis=1, **kwargs)
    return add_metadata(df)


def score_by_group_key(
    grouped_df: Dict[str, pd.DataFrame],
    scoring_func_map: Dict[str, List[Tuple[str, Callable]]],
    **kwargs,
) -> Dict[str, pd.DataFrame]:
    """
    Applies group-specific scoring functions to each DataFrame in a dictionary.

    Returns:
        Dict[str, pd.DataFrame]: Scored dataframes by group.
    """
    result_dict = {}

    for group_key, group_df in grouped_df.items():
        scoring_funcs = scoring_func_map.get(group_key)

        if scoring_funcs is None:
            print(
                f"[WARN] No scoring functions defined for activity '{group_key}', skipping."
            )
            continue

        group_copy = group_df.copy()
        for metric_name, func in scoring_funcs:
            group_copy[f"metric_{metric_name}"] = group_copy.apply(
                func, axis=1, **kwargs
            )

        group_copy = add_metadata(group_copy)
        result_dict[group_key] = group_copy

    return result_dict


def summarize_by_group_key(
    grouped_scored: Dict[str, pd.DataFrame],
    summary_func_map: Dict[str, Callable],
    groupby_cols: List[str] = ["participant_id", "session_id", "session_uuid"],
    **kwargs,
) -> Dict[str, pd.DataFrame]:
    """
    Apply task-specific summary functions to grouped/scored dataframes.

    Parameters:
        grouped_scored (Dict[str, pd.DataFrame]): Dictionary of scored dataframes.
        summary_func_map (Dict[str, Callable]): Dictionary of summarization functions.
        groupby_cols (List[str]): Columns to group by before summarizing.
        **kwargs: Passed into each summarization function.

    Returns:
        Dict[str, pd.DataFrame]: Summary results per task.
    """
    summary_results = {}

    for task_name, df in grouped_scored.items():
        summary_func = summary_func_map.get(task_name)

        if summary_func is None:
            print(f"[WARN] No summary function found for: {task_name}")
            continue

        if df is None or df.empty:
            print(f"[WARN] No data available for: {task_name}")
            continue

        try:
            summary_df = (
                df.groupby(groupby_cols)
                .apply(lambda x: summary_func(x, **kwargs))
                .reset_index()
            )
            summary_df_wmd = summary_df.copy()
            summary_df_wmd = add_metadata(summary_df_wmd)
            summary_results[task_name] = summary_df_wmd
        except Exception as e:
            print(f"[ERROR] Summary failed for {task_name}: {e}")
            continue

    return summary_results

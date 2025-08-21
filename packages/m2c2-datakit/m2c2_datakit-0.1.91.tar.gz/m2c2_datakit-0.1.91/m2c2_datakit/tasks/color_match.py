import json

import numpy as np
import pandas as pd

from ..core import helpers


def hex_to_rgb(hex_color):
    """
    Convert hex color to RGB values.

    Args:
        hex_color (str): Hex color string (with or without #)

    Returns:
        tuple: RGB values (r, g, b)
    """
    hex_color = hex_color.lstrip("#")
    return tuple(int(hex_color[i : i + 2], 16) for i in (0, 2, 4))


def calculate_color_distance(stim_color, tap_color):
    """
    Calculate Euclidean distance between two colors in RGB space.

    Args:
        stim_color (str): Hex color string
        tap_color (str): Hex color string

    Returns:
        float: Euclidean distance between colors
    """
    try:
        rgb_stim = hex_to_rgb(stim_color)
        rgb_tap = hex_to_rgb(tap_color)

        # Euclidean distance in RGB space
        distance = np.sqrt(sum((a - b) ** 2 for a, b in zip(rgb_stim, rgb_tap)))
        return distance
    except Exception as e:
        print(f"Error calculating color distance: {e}")
        return None


def score_accuracy(row):
    """
    Scores the accuracy of the response for a single trial in the Color Match task.

    Args:
        row (pd.Series): A single row of the trial-level Color Match task dataframe.

    Returns:
        (bool | None): The value from response_correct column, indicating whether
            the response was correct (True) or incorrect (False).
            None is returned if an error occurs while processing the row.
    """
    try:
        return row["response_correct"]
    except Exception as e:
        print(f"Error processing row: {e}")
        return None


def score_color_distance(row):
    """
    Calculates the color distance between stimulus color and user response.

    Args:
        row (pd.Series): A single row of the trial-level Color Match task dataframe.

    Returns:
        (float | None): Euclidean color distance in RGB space, or None if error occurs.
    """
    try:
        stimulus_color = row["stimulus_color"]

        # Extract tap_value from actions_array
        actions_array = row["actions_array"]
        if isinstance(actions_array, str):
            actions_array = json.loads(actions_array)

        if actions_array and len(actions_array) > 0:
            tap_value = actions_array[0]["tap_value"]
            return calculate_color_distance(stimulus_color, tap_value)
        else:
            return None

    except Exception as e:
        print(f"Error calculating color distance: {e}")
        return None


def summarize(x, trials_expected=20, rt_outlier_low=100, rt_outlier_high=10000):
    """
    Summarizes the Color Match task data by calculating various statistics.

    This function calculates accuracy metrics, color distance statistics, and response times
    for the Color Match task.

    Args:
        x (pd.DataFrame): The trial-level scored dataset for the Color Match task.
        trials_expected (int, optional): The expected number of trials. Defaults to 20.
        rt_outlier_low (int, optional): The lower bound for filtering outliers in response times. Defaults to 100.
        rt_outlier_high (int, optional): The upper bound for filtering outliers in response times. Defaults to 10000.

    Returns:
        (pd.Series): A Pandas Series containing the summary statistics for the Color Match task.
    """

    d = helpers.summarize_common_metadata(x, trials_expected)

    # Basic accuracy metrics
    d["n_trials_correct"] = (x["metric_accuracy"] == True).sum()
    d["n_trials_incorrect"] = (x["metric_accuracy"] == False).sum()

    # Color distance metrics
    valid_distance_mask = pd.notna(x["metric_euclidean_color_distance"])

    # Color distance for incorrect trials
    incorrect_distance_mask = (x["metric_accuracy"] == False) & valid_distance_mask
    incorrect_distance_data = x.loc[
        incorrect_distance_mask, "metric_euclidean_color_distance"
    ]

    d["median_euclidean_color_distance_incorrect"] = incorrect_distance_data.median()
    d["sd_euclidean_color_distance_incorrect"] = incorrect_distance_data.std()
    d["mean_euclidean_color_distance_incorrect"] = incorrect_distance_data.mean()

    # Response Times - Handle null/invalid response times first
    valid_rt_mask = pd.notna(x["response_time_ms"]) & (x["response_time_ms"] > 0)
    valid_rt_data = x.loc[valid_rt_mask, "response_time_ms"]

    # Number of trials that had null/invalid response times
    d["n_trials_rt_invalid"] = x["response_time_ms"].shape[0] - valid_rt_data.shape[0]

    # Overall Response Times (all trials)
    d["median_rt_all"] = valid_rt_data.median()
    d["sd_rt_all"] = valid_rt_data.std()

    # Response Times by accuracy
    correct_rt_mask = (x["metric_accuracy"] == True) & valid_rt_mask
    incorrect_rt_mask = (x["metric_accuracy"] == False) & valid_rt_mask

    correct_rt_data = x.loc[correct_rt_mask, "response_time_ms"]
    incorrect_rt_data = x.loc[incorrect_rt_mask, "response_time_ms"]

    d["median_rt_correct"] = correct_rt_data.median()
    d["sd_rt_correct"] = correct_rt_data.std()
    d["median_rt_incorrect"] = incorrect_rt_data.median()
    d["sd_rt_incorrect"] = incorrect_rt_data.std()

    # Filtered Response Times (outliers removed)
    rt_filtered_overall = x.loc[
        valid_rt_mask
        & (x["response_time_ms"] >= rt_outlier_low)
        & (x["response_time_ms"] <= rt_outlier_high),
        "response_time_ms",
    ]

    # Count of outliers filtered out
    d["n_outliers_rt_filtered"] = valid_rt_data.shape[0] - rt_filtered_overall.shape[0]

    # Filtered Response Times for all valid trials
    d["median_rt_all_filtered"] = rt_filtered_overall.median()
    d["sd_rt_all_filtered"] = rt_filtered_overall.std()

    # Filtered Response Times by accuracy
    correct_rt_filtered_data = x.loc[
        correct_rt_mask
        & (x["response_time_ms"] >= rt_outlier_low)
        & (x["response_time_ms"] <= rt_outlier_high),
        "response_time_ms",
    ]
    incorrect_rt_filtered_data = x.loc[
        incorrect_rt_mask
        & (x["response_time_ms"] >= rt_outlier_low)
        & (x["response_time_ms"] <= rt_outlier_high),
        "response_time_ms",
    ]
    d["median_rt_correct_trials_filtered"] = correct_rt_filtered_data.median()
    d["sd_rt_correct_trials_filtered"] = correct_rt_filtered_data.std()
    d["median_rt_incorrect_trials_filtered"] = incorrect_rt_filtered_data.median()
    d["sd_rt_incorrect_trials_filtered"] = incorrect_rt_filtered_data.std()

    return pd.Series(d)

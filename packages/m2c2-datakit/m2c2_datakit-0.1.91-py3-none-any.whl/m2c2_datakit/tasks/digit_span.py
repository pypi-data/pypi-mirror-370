import pandas as pd

from ..core import helpers


def score_accuracy(row):
    """
    Scores the accuracy of the response for a single trial in the Digit Span task.

    Args:
        row (pd.Series): A single row of the trial-level Digit Span task dataframe.

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


def summarize(x, trials_expected=3, rt_outlier_low=100, rt_outlier_high=10000):
    """
    Summarizes the Digit Span task data by calculating various statistics.

    This function calculates accuracy metrics and response times for the Digit Span task,
    including the number of correct and incorrect trials, and median/standard deviation
    of response times with and without outlier filtering.

    Args:
        x (pd.DataFrame): The trial-level scored dataset for the Digit Span task.
        trials_expected (int, optional): The expected number of trials. Defaults to 3.
        rt_outlier_low (int, optional): The lower bound for filtering outliers in response times. Defaults to 100.
        rt_outlier_high (int, optional): The upper bound for filtering outliers in response times. Defaults to 10000.

    Returns:
        (pd.Series): A Pandas Series containing the summary statistics for the Digit Span task.
    """

    d = helpers.summarize_common_metadata(x, trials_expected)

    # Basic accuracy metric counts
    d["n_trials_correct"] = (x["metric_accuracy"] == True).sum()
    d["n_trials_incorrect"] = (x["metric_accuracy"] == False).sum()

    # Response Times - Handle null/invalid response times first
    valid_rt_mask = pd.notna(x["response_time_ms"]) & (x["response_time_ms"] > 0)
    valid_rt_data = x.loc[valid_rt_mask, "response_time_ms"]

    # Number of trials that had null/invalid response times
    d["n_trials_rt_invalid"] = x["response_time_ms"].shape[0] - valid_rt_data.shape[0]

    # Overall Response Times (all trials)
    d["median_response_time_all"] = valid_rt_data.median()
    d["sd_response_time_all"] = valid_rt_data.std()

    # Response Times by accuracy
    correct_rt_mask = (x["metric_accuracy"] == True) & valid_rt_mask
    incorrect_rt_mask = (x["metric_accuracy"] == False) & valid_rt_mask

    correct_rt_data = x.loc[correct_rt_mask, "response_time_ms"]
    incorrect_rt_data = x.loc[incorrect_rt_mask, "response_time_ms"]

    d["median_response_time_correct"] = correct_rt_data.median()
    d["sd_response_time_correct"] = correct_rt_data.std()
    d["median_response_time_incorrect"] = incorrect_rt_data.median()
    d["sd_response_time_incorrect"] = incorrect_rt_data.std()

    # Filtered Response Times (outliers removed)
    rt_filtered_overall = x.loc[
        valid_rt_mask
        & (x["response_time_ms"] >= rt_outlier_low)
        & (x["response_time_ms"] <= rt_outlier_high),
        "response_time_ms",
    ]

    # Count of outliers filtered out
    d["n_outliers_rt_filtered"] = valid_rt_data.shape[0] - rt_filtered_overall.shape[0]

    d["median_response_time_all_filtered"] = rt_filtered_overall.median()
    d["sd_response_time_all_filtered"] = rt_filtered_overall.std()

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

    d["median_response_time_correct_filtered"] = correct_rt_filtered_data.median()
    d["sd_response_time_correct_filtered"] = correct_rt_filtered_data.std()
    d["median_response_time_incorrect_filtered"] = incorrect_rt_filtered_data.median()
    d["sd_response_time_incorrect_filtered"] = incorrect_rt_filtered_data.std()

    return pd.Series(d)

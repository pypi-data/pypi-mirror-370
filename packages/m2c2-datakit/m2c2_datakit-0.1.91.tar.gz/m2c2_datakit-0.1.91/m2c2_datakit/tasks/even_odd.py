import pandas as pd

from ..core import helpers


def score_accuracy(row):
    """
    Scores the accuracy of the response for a single trial in the Even-Odd task.

    Args:
        row (pd.Series): A single row of the trial-level Even-Odd task dataframe.

    Returns:
        (bool | None): The value from selection_correct column, indicating whether
            the response was correct (True) or incorrect (False).
            None is returned if an error occurs while processing the row.
    """
    try:
        return row["selection_correct"]
    except Exception as e:
        print(f"Error processing row: {e}")
        return None


def score_trial_type(row):
    """
    Determines the trial type for a single trial in the Even-Odd task.

    Args:
        row (pd.Series): A single row of the trial-level Even-Odd task dataframe.

    Returns:
        (str | None): "EVEN" if the presented number is even,
            "ODD" if the presented number is odd, None if error occurs.
    """
    try:
        presented_number = row["presented_number"]

        if presented_number % 2 == 0:
            return "EVEN"
        else:
            return "ODD"
    except Exception as e:
        print(f"Error processing row: {e}")
        return None


def summarize(x, trials_expected=20, rt_outlier_low=100, rt_outlier_high=10000):
    """
    Summarizes the Even-Odd task data by calculating various statistics.

    This function calculates accuracy metrics, trial type counts, and response times
    for the Even-Odd task, including the number of correct and incorrect trials,
    counts by trial type (odd/even), and median/standard deviation of response times
    with and without outlier filtering.

    Args:
        x (pd.DataFrame): The trial-level scored dataset for the Even-Odd task.
        trials_expected (int, optional): The expected number of trials. Defaults to 20.
        rt_outlier_low (int, optional): The lower bound for filtering outliers in response times. Defaults to 100.
        rt_outlier_high (int, optional): The upper bound for filtering outliers in response times. Defaults to 10000.

    Returns:
        (pd.Series): A Pandas Series containing the summary statistics for the Even-Odd task.
    """

    d = helpers.summarize_common_metadata(x, trials_expected)

    # Basic accuracy metric counts
    d["n_trials_correct"] = (x["metric_accuracy"] == True).sum()
    d["n_trials_incorrect"] = (x["metric_accuracy"] == False).sum()

    # Trial type counts
    d["n_trials_even"] = (x["metric_trial_type"] == "EVEN").sum()
    d["n_trials_odd"] = (x["metric_trial_type"] == "ODD").sum()

    # Accuracy by trial type counts
    d["n_trials_even_correct"] = (
        (x["metric_trial_type"] == "EVEN") & (x["metric_accuracy"] == True)
    ).sum()
    d["n_trials_even_incorrect"] = (
        (x["metric_trial_type"] == "EVEN") & (x["metric_accuracy"] == False)
    ).sum()
    d["n_trials_odd_correct"] = (
        (x["metric_trial_type"] == "ODD") & (x["metric_accuracy"] == True)
    ).sum()
    d["n_trials_odd_incorrect"] = (
        (x["metric_trial_type"] == "ODD") & (x["metric_accuracy"] == False)
    ).sum()

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

    # Response Times by trial type
    even_rt_mask = (x["metric_trial_type"] == "EVEN") & valid_rt_mask
    odd_rt_mask = (x["metric_trial_type"] == "ODD") & valid_rt_mask

    even_rt_data = x.loc[even_rt_mask, "response_time_ms"]
    odd_rt_data = x.loc[odd_rt_mask, "response_time_ms"]

    d["median_response_time_even"] = even_rt_data.median()
    d["sd_response_time_even"] = even_rt_data.std()
    d["median_response_time_odd"] = odd_rt_data.median()
    d["sd_response_time_odd"] = odd_rt_data.std()

    # Response Times by trial type and accuracy
    even_correct_rt_mask = (x["metric_trial_type"] == "EVEN") & correct_rt_mask
    even_incorrect_rt_mask = (x["metric_trial_type"] == "EVEN") & incorrect_rt_mask
    odd_correct_rt_mask = (x["metric_trial_type"] == "ODD") & correct_rt_mask
    odd_incorrect_rt_mask = (x["metric_trial_type"] == "ODD") & incorrect_rt_mask

    even_correct_rt_data = x.loc[even_correct_rt_mask, "response_time_ms"]
    even_incorrect_rt_data = x.loc[even_incorrect_rt_mask, "response_time_ms"]
    odd_correct_rt_data = x.loc[odd_correct_rt_mask, "response_time_ms"]
    odd_incorrect_rt_data = x.loc[odd_incorrect_rt_mask, "response_time_ms"]

    d["median_rt_even_correct"] = even_correct_rt_data.median()
    d["sd_rt_even_correct"] = even_correct_rt_data.std()
    d["median_rt_even_incorrect"] = even_incorrect_rt_data.median()
    d["sd_rt_even_incorrect"] = even_incorrect_rt_data.std()
    d["median_rt_odd_correct"] = odd_correct_rt_data.median()
    d["sd_rt_odd_correct"] = odd_correct_rt_data.std()
    d["median_rt_odd_incorrect"] = odd_incorrect_rt_data.median()
    d["sd_rt_odd_incorrect"] = odd_incorrect_rt_data.std()

    # Filtered Response Times (outliers removed)
    rt_filtered_overall = x.loc[
        valid_rt_mask
        & (x["response_time_ms"] >= rt_outlier_low)
        & (x["response_time_ms"] <= rt_outlier_high),
        "response_time_ms",
    ]

    # Count of outliers filtered out
    d["n_outliers_rt_filtered"] = valid_rt_data.shape[0] - rt_filtered_overall.shape[0]

    d["median_response_time_filtered"] = rt_filtered_overall.median()
    d["sd_response_time_filtered"] = rt_filtered_overall.std()

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

    # Filtered Response Times by trial type
    even_rt_filtered_data = x.loc[
        even_rt_mask
        & (x["response_time_ms"] >= rt_outlier_low)
        & (x["response_time_ms"] <= rt_outlier_high),
        "response_time_ms",
    ]
    odd_rt_filtered_data = x.loc[
        odd_rt_mask
        & (x["response_time_ms"] >= rt_outlier_low)
        & (x["response_time_ms"] <= rt_outlier_high),
        "response_time_ms",
    ]

    d["median_response_time_even_filtered"] = even_rt_filtered_data.median()
    d["sd_response_time_even_filtered"] = even_rt_filtered_data.std()
    d["median_response_time_odd_filtered"] = odd_rt_filtered_data.median()
    d["sd_response_time_odd_filtered"] = odd_rt_filtered_data.std()

    # Filtered Response Times by trial type and accuracy
    even_correct_rt_filtered_data = x.loc[
        even_correct_rt_mask
        & (x["response_time_ms"] >= rt_outlier_low)
        & (x["response_time_ms"] <= rt_outlier_high),
        "response_time_ms",
    ]
    even_incorrect_rt_filtered_data = x.loc[
        even_incorrect_rt_mask
        & (x["response_time_ms"] >= rt_outlier_low)
        & (x["response_time_ms"] <= rt_outlier_high),
        "response_time_ms",
    ]
    odd_correct_rt_filtered_data = x.loc[
        odd_correct_rt_mask
        & (x["response_time_ms"] >= rt_outlier_low)
        & (x["response_time_ms"] <= rt_outlier_high),
        "response_time_ms",
    ]
    odd_incorrect_rt_filtered_data = x.loc[
        odd_incorrect_rt_mask
        & (x["response_time_ms"] >= rt_outlier_low)
        & (x["response_time_ms"] <= rt_outlier_high),
        "response_time_ms",
    ]

    d["median_rt_even_correct_filtered"] = even_correct_rt_filtered_data.median()
    d["sd_rt_even_correct_filtered"] = even_correct_rt_filtered_data.std()
    d["median_rt_even_incorrect_filtered"] = even_incorrect_rt_filtered_data.median()
    d["sd_rt_even_incorrect_filtered"] = even_incorrect_rt_filtered_data.std()
    d["median_rt_odd_correct_filtered"] = odd_correct_rt_filtered_data.median()
    d["sd_rt_odd_correct_filtered"] = odd_correct_rt_filtered_data.std()
    d["median_rt_odd_incorrect_filtered"] = odd_incorrect_rt_filtered_data.median()
    d["sd_rt_odd_incorrect_filtered"] = odd_incorrect_rt_filtered_data.std()

    return pd.Series(d)

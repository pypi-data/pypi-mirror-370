import pandas as pd

from ..core import helpers


def score_accuracy(row):
    """
    Scores the accuracy of the response for a single trial in the Stroop task.

    Args:
        row (pd.Series): A single row of the trial-level Stroop task dataframe.

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
    Determines the trial type for a single trial in the Stroop task.

    Args:
        row (pd.Series): A single row of the trial-level Stroop task dataframe.

    Returns:
        (str | None): "NORMAL" if word text matches word color,
            "LURE" if they differ, None if error occurs.
    """
    try:
        word_text = row["presented_word_text"]
        word_color = row["presented_word_color"]

        if word_text.lower() == word_color.lower():
            return "NORMAL"
        else:
            return "LURE"
    except Exception as e:
        print(f"Error processing row: {e}")
        return None


def summarize(x, trials_expected=20, rt_outlier_low=100, rt_outlier_high=10000):
    """
    Summarizes the Stroop task data by calculating various statistics.

    This function calculates accuracy metrics, response times, and trial type
    statistics for the Stroop task, including lure and normal trials.

    Args:
        x (pd.DataFrame): The trial-level scored dataset for the Stroop task.
        trials_expected (int, optional): The expected number of trials. Defaults to 20.
        rt_outlier_low (int, optional): The lower bound for filtering outliers in response times. Defaults to 100.
        rt_outlier_high (int, optional): The upper bound for filtering outliers in response times. Defaults to 10000.

    Returns:
        (pd.Series): A Pandas Series containing the summary statistics for the Stroop task.
    """

    d = helpers.summarize_common_metadata(x, trials_expected)

    # Basic accuracy metric counts
    d["n_trials_correct"] = (x["metric_accuracy"] == True).sum()
    d["n_trials_incorrect"] = (x["metric_accuracy"] == False).sum()

    # Trial type counts
    d["n_trials_lure"] = (x["metric_trial_type"] == "LURE").sum()
    d["n_trials_normal"] = (x["metric_trial_type"] == "NORMAL").sum()

    # Accuracy by trial type counts
    d["n_trials_normal_correct"] = (
        (x["metric_trial_type"] == "NORMAL") & (x["metric_accuracy"] == True)
    ).sum()
    d["n_trials_normal_incorrect"] = (
        (x["metric_trial_type"] == "NORMAL") & (x["metric_accuracy"] == False)
    ).sum()
    d["n_trials_lure_correct"] = (
        (x["metric_trial_type"] == "LURE") & (x["metric_accuracy"] == True)
    ).sum()
    d["n_trials_lure_incorrect"] = (
        (x["metric_trial_type"] == "LURE") & (x["metric_accuracy"] == False)
    ).sum()

    # Response Times - Handle null/invalid response times first
    valid_rt_mask = pd.notna(x["response_time_ms"]) & (x["response_time_ms"] > 0)
    valid_rt_data = x.loc[valid_rt_mask, "response_time_ms"]

    # Number of trials that had null/invalid response times
    d["n_trials_rt_invalid"] = x["response_time_ms"].shape[0] - valid_rt_data.shape[0]

    # Overall Response Times (all trials)
    d["median_rt_all_trials"] = valid_rt_data.median()
    d["sd_rt_all_trials"] = valid_rt_data.std()

    # Response Times by accuracy
    correct_rt_mask = (x["metric_accuracy"] == True) & valid_rt_mask
    incorrect_rt_mask = (x["metric_accuracy"] == False) & valid_rt_mask

    correct_rt_data = x.loc[correct_rt_mask, "response_time_ms"]
    incorrect_rt_data = x.loc[incorrect_rt_mask, "response_time_ms"]

    d["median_rt_correct_trials"] = correct_rt_data.median()
    d["sd_rt_correct_trials"] = correct_rt_data.std()
    d["median_rt_incorrect_trials"] = incorrect_rt_data.median()
    d["sd_rt_incorrect_trials"] = incorrect_rt_data.std()

    # Response Times by trial type
    lure_rt_mask = (x["metric_trial_type"] == "LURE") & valid_rt_mask
    normal_rt_mask = (x["metric_trial_type"] == "NORMAL") & valid_rt_mask

    lure_rt_data = x.loc[lure_rt_mask, "response_time_ms"]
    normal_rt_data = x.loc[normal_rt_mask, "response_time_ms"]

    d["median_rt_lure_trials"] = lure_rt_data.median()
    d["sd_rt_lure_trials"] = lure_rt_data.std()
    d["median_rt_normal_trials"] = normal_rt_data.median()
    d["sd_rt_normal_trials"] = normal_rt_data.std()

    # Response Times by trial type and accuracy combinations
    normal_correct_rt_mask = (
        (x["metric_trial_type"] == "NORMAL")
        & (x["metric_accuracy"] == True)
        & valid_rt_mask
    )
    normal_incorrect_rt_mask = (
        (x["metric_trial_type"] == "NORMAL")
        & (x["metric_accuracy"] == False)
        & valid_rt_mask
    )
    lure_correct_rt_mask = (
        (x["metric_trial_type"] == "LURE")
        & (x["metric_accuracy"] == True)
        & valid_rt_mask
    )
    lure_incorrect_rt_mask = (
        (x["metric_trial_type"] == "LURE")
        & (x["metric_accuracy"] == False)
        & valid_rt_mask
    )

    normal_correct_rt_data = x.loc[normal_correct_rt_mask, "response_time_ms"]
    normal_incorrect_rt_data = x.loc[normal_incorrect_rt_mask, "response_time_ms"]
    lure_correct_rt_data = x.loc[lure_correct_rt_mask, "response_time_ms"]
    lure_incorrect_rt_data = x.loc[lure_incorrect_rt_mask, "response_time_ms"]

    d["median_rt_normal_correct"] = normal_correct_rt_data.median()
    d["sd_rt_normal_correct"] = normal_correct_rt_data.std()
    d["median_rt_normal_incorrect"] = normal_incorrect_rt_data.median()
    d["sd_rt_normal_incorrect"] = normal_incorrect_rt_data.std()
    d["median_rt_lure_correct"] = lure_correct_rt_data.median()
    d["sd_rt_lure_correct"] = lure_correct_rt_data.std()
    d["median_rt_lure_incorrect"] = lure_incorrect_rt_data.median()
    d["sd_rt_lure_incorrect"] = lure_incorrect_rt_data.std()

    # Filtered Response Times (outliers removed)
    rt_filtered_overall = x.loc[
        valid_rt_mask
        & (x["response_time_ms"] >= rt_outlier_low)
        & (x["response_time_ms"] <= rt_outlier_high),
        "response_time_ms",
    ]

    # Count of outliers filtered out
    d["n_outliers_rt_filtered"] = valid_rt_data.shape[0] - rt_filtered_overall.shape[0]

    d["median_rt_overall_filtered"] = rt_filtered_overall.median()
    d["sd_rt_overall_filtered"] = rt_filtered_overall.std()

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
    d["median_rt_correct_filtered"] = correct_rt_filtered_data.median()
    d["sd_rt_correct_filtered"] = correct_rt_filtered_data.std()

    d["median_rt_incorrect_filtered"] = incorrect_rt_filtered_data.median()
    d["sd_rt_incorrect_filtered"] = incorrect_rt_filtered_data.std()

    # Filtered Response Times by trial type
    lure_rt_filtered_data = x.loc[
        lure_rt_mask
        & (x["response_time_ms"] >= rt_outlier_low)
        & (x["response_time_ms"] <= rt_outlier_high),
        "response_time_ms",
    ]
    normal_rt_filtered_data = x.loc[
        normal_rt_mask
        & (x["response_time_ms"] >= rt_outlier_low)
        & (x["response_time_ms"] <= rt_outlier_high),
        "response_time_ms",
    ]
    d["median_rt_lure_filtered"] = lure_rt_filtered_data.median()
    d["sd_rt_lure_filtered"] = lure_rt_filtered_data.std()

    d["median_rt_normal_filtered"] = normal_rt_filtered_data.median()
    d["sd_rt_normal_filtered"] = normal_rt_filtered_data.std()

    # Filtered Response Times by trial type and accuracy combinations
    normal_correct_rt_filtered_data = x.loc[
        normal_correct_rt_mask
        & (x["response_time_ms"] >= rt_outlier_low)
        & (x["response_time_ms"] <= rt_outlier_high),
        "response_time_ms",
    ]
    normal_incorrect_rt_filtered_data = x.loc[
        normal_incorrect_rt_mask
        & (x["response_time_ms"] >= rt_outlier_low)
        & (x["response_time_ms"] <= rt_outlier_high),
        "response_time_ms",
    ]
    lure_correct_rt_filtered_data = x.loc[
        lure_correct_rt_mask
        & (x["response_time_ms"] >= rt_outlier_low)
        & (x["response_time_ms"] <= rt_outlier_high),
        "response_time_ms",
    ]
    lure_incorrect_rt_filtered_data = x.loc[
        lure_incorrect_rt_mask
        & (x["response_time_ms"] >= rt_outlier_low)
        & (x["response_time_ms"] <= rt_outlier_high),
        "response_time_ms",
    ]
    d["median_rt_normal_correct_filtered"] = normal_correct_rt_filtered_data.median()
    d["sd_rt_normal_correct_filtered"] = normal_correct_rt_filtered_data.std()
    d["median_rt_normal_incorrect_filtered"] = (
        normal_incorrect_rt_filtered_data.median()
    )
    d["sd_rt_normal_incorrect_filtered"] = normal_incorrect_rt_filtered_data.std()
    d["median_rt_lure_correct_filtered"] = lure_correct_rt_filtered_data.median()
    d["sd_rt_lure_correct_filtered"] = lure_correct_rt_filtered_data.std()
    d["median_rt_lure_incorrect_filtered"] = lure_incorrect_rt_filtered_data.median()
    d["sd_rt_lure_incorrect_filtered"] = lure_incorrect_rt_filtered_data.std()

    return pd.Series(d)

import pandas as pd

from ..core import helpers


def score_accuracy(row):
    """
    Identifies and returns the type of error in a Go No Go Fade task trial.

    The function classifies the trial based on the correctness and the type of response
    provided. It returns "omission" for a missed response to a "GO" trial and "commission"
    for an incorrect response to a "NOGO" trial. "correct" is returned if the response is correct.

    Args:
        row (pd.Series): A single row of the trial-level Go No Go Fade task dataframe containing
                         the columns "trial_type", "trial_response", and "correct".

    Returns:
        str:
            * "omission" if the trial is a "GO" trial and incorrectly responded as "NOGO".
            * "commission" if the trial is a "NOGO" trial and incorrectly responded as "GO".
            * "correct" if the response is correct.

    Raises:
        ValueError: If the trial type or response values are invalid.
    """
    try:
        trial_type = row["trial_type"]
        trial_response = row["trial_response"]
        trial_correct = row["correct"]

        # If trial_correct is false return "Omission" or "Commission"
        if trial_correct is False:
            if trial_type == "GO" and trial_response == "NOGO":
                return "omission"
            elif trial_type == "NOGO" and trial_response == "GO":
                return "commission"
            else:
                raise ValueError(
                    f"Invalid trial_type or trial_response values: {trial_type}, {trial_response}"
                )
        # If trial_correct is true return "correct"
        elif trial_correct is True:
            return "correct"
        else:
            raise ValueError(f"Invalid trial_correct value: {trial_correct}")

    except Exception as e:
        print(f"Error processing row: {e}")
        return None


def score_response_time(row):
    """
    Calculates response time from trial begin and end timestamps.

    Args:
        row (pd.Series): A single row of the trial-level Go No Go Fade task dataframe.

    Returns:
        (float | None): Response time in milliseconds, or None if error occurs.
    """
    try:
        begin_time = pd.to_datetime(row["trial_begin_iso8601_timestamp"])
        end_time = pd.to_datetime(row["trial_end_iso8601_timestamp"])

        # Calculate difference in milliseconds
        response_time_ms = (end_time - begin_time).total_seconds() * 1000

        return response_time_ms
    except Exception as e:
        print(f"Error calculating response time: {e}")
        return None


def summarize(x, trials_expected=10, rt_outlier_low=100, rt_outlier_high=10000):
    """
    Summarizes the Go No Go Fade task data by calculating various statistics.

    This function calculates accuracy metrics and response times for the Go No Go Fade task.

    Args:
        x (pd.DataFrame): The trial-level scored dataset for the Go No Go Fade task.
        trials_expected (int, optional): The expected number of trials. Defaults to 10.
        rt_outlier_low (int, optional): The lower bound for filtering outliers in response times. Defaults to 100.
        rt_outlier_high (int, optional): The upper bound for filtering outliers in response times. Defaults to 10000.

    Returns:
        (pd.Series): A Pandas Series containing the summary statistics for the Go No Go Fade task.
    """

    d = helpers.summarize_common_metadata(x, trials_expected)

    # Summarize errors for omissions and commissions or correct responses
    d["n_errors_omission"] = (x["metric_accuracy"] == "omission").sum()
    d["n_errors_commission"] = (x["metric_accuracy"] == "commission").sum()
    d["n_trials_correct"] = (x["metric_accuracy"] == "correct").sum()

    # Response Times - Handle null/invalid response times first
    valid_rt_mask = pd.notna(x["metric_response_time"]) & (
        x["metric_response_time"] > 0
    )

    # Number of trials that had null/invalid response times
    d["n_trials_rt_invalid"] = x["metric_response_time"].shape[0] - valid_rt_mask.sum()

    # Overall Response Times (all trials with valid RT)
    d["median_response_time_all_valid"] = x.loc[
        valid_rt_mask, "metric_response_time"
    ].median()
    d["sd_response_time_all_valid"] = x.loc[valid_rt_mask, "metric_response_time"].std()

    # Response Times by error type - correct trials
    d["median_response_time_correct_valid"] = x.loc[
        (x["metric_accuracy"] == "correct") & valid_rt_mask, "metric_response_time"
    ].median()
    d["sd_response_time_correct_valid"] = x.loc[
        (x["metric_accuracy"] == "correct") & valid_rt_mask, "metric_response_time"
    ].std()

    # Response Times by error type - error trials (omission + commission)
    d["median_response_time_error_all_valid"] = x.loc[
        (x["metric_accuracy"].isin(["omission", "commission"])) & valid_rt_mask,
        "metric_response_time",
    ].median()
    d["sd_response_time_error_all_valid"] = x.loc[
        (x["metric_accuracy"].isin(["omission", "commission"])) & valid_rt_mask,
        "metric_response_time",
    ].std()

    # Response Times by specific error types
    for error_type in ["omission", "commission"]:
        error_mask = (x["metric_accuracy"] == error_type) & valid_rt_mask
        d[f"median_response_time_error_{error_type}_valid"] = x.loc[
            error_mask, "metric_response_time"
        ].median()
        d[f"sd_response_time_error_{error_type}_valid"] = x.loc[
            error_mask, "metric_response_time"
        ].std()

    # ? Question: Filtered?

    return pd.Series(d)

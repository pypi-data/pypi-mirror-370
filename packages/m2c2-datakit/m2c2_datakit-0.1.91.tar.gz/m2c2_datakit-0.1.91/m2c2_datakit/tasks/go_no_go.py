import pandas as pd

from ..core import helpers


def score_errors(row: pd.Series) -> str | None:
    """
    Identifies and returns the type of error in a Go/No-Go task trial.

    The function classifies the trial based on the correctness and the type of response
    provided. It returns "omission" for a missed response to a "GO" trial and "commission"
    for an incorrect response to a "NOGO" trial. "correct" is returned if the response is correct.

    Args:
        row (pd.Series): A single row of the trial-level Go/No-Go task dataframe containing
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
        trial_type: str = row["trial_type"]
        trial_response: str = row["trial_response"]
        trial_correct: bool = row["correct"]

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
        # If trial_correct is true return None
        elif trial_correct is True:
            return "correct"
        else:
            raise ValueError(f"Invalid trial_correct value: {trial_correct}")

    except Exception as e:
        print(f"Error processing row: {e}")
        return None


def summarize(x, trials_expected=30, rt_outlier_low=100):
    """
    Summarizes the Go/No-Go task data by calculating statistics such as omission errors, commission errors, correct responses, and response times.

    This function computes the number of omission errors, commission errors, correct responses, and overall response times for the Go/No-Go task.

    Args:
        x (pd.DataFrame): The trial-level scored dataset for the Go/No-Go task.
        trials_expected (int, optional): The expected number of trials. Defaults to 30.

    Returns:
        (pd.Series): A Pandas Series containing the summary statistics for the Go/No-Go task.
    """

    d = helpers.summarize_common_metadata(x, trials_expected)

    # Summarize errors for omissions and commissions or correct responses
    d["n_errors_omission"] = (x["metric_accuracy"] == "omission").sum()
    d["n_errors_commission"] = (x["metric_accuracy"] == "commission").sum()
    d["n_trials_correct"] = (x["metric_accuracy"] == "correct").sum()

    # Unfiltered RT for whole task
    d["median_response_time_all"] = x["response_time_ms"].median()

    # Unfiltered RT for omission and commission errors and correct responses
    for metric in ["omission", "commission", "correct"]:
        d[f"median_response_time_{metric}"] = x.loc[
            x["metric_accuracy"] == metric, "response_time_ms"
        ].median()

    # Max RT for whole task to see if any trials were displayed longer than expected
    d["max_response_time_all"] = x["response_time_ms"].max()

    # * Only using low filter since the stimulus is only on screen for 1 second
    # Filter out outliers: RT < 100 ms for whole task
    rt_filtered = x.loc[
        (x["response_time_ms"] >= rt_outlier_low),
        "response_time_ms",
    ]
    d["median_response_time_low_filtered"] = rt_filtered.median()

    # Count of outliers filtered out
    d["n_trials_rt_filtered"] = x["response_time_ms"].shape[0] - rt_filtered.shape[0]

    # Filtered RT for omission and commission errors and correct responses
    for metric in ["omission", "commission", "correct"]:
        d[f"median_response_time_{metric}_low_filtered"] = x.loc[
            (x["metric_accuracy"] == metric)
            & (x["response_time_ms"] >= rt_outlier_low),
            "response_time_ms",
        ].median()

    return pd.Series(d)

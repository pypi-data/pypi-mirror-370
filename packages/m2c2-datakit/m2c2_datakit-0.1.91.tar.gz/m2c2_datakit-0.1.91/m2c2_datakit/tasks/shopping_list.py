"""Shopping List Task Functions

This module contains functions to score and summarize the Shopping List task data.

Functions:
    score_accuracy(row):
        Retrieves the accuracy of the response for a single trial in the Shopping List task.

    summarize(x, trials_expected=20, rt_outlier_low=100, rt_outlier_high=10000):
        Summarizes the scored Shopping List task data by calculating various statistics for each phase of the task.

"""

import numpy as np
import pandas as pd

from ..core import helpers

# TODO: Check summarize() for notes/questions on summary keys/columns and missing response time values.


def score_accuracy(row: pd.Series) -> str | None:
    """Retrieves the accuracy of the response for a single trial in the Shopping List task.

    In practice, this is the same value as the current row of the `response_correct` column in the trial-level shopping list task dataframe.

    Args:
        row (pd.Series): A single row of the trial-level shopping list task dataframe.

    Returns:
        (str | None):
            The value of the `response_correct` column for the given row. Could be an empty string, "true", "false", or None if an error occurs.

    Raises:
        Exception: If an error occurs while processing the row.
    """

    try:
        return row["response_correct"]
    except Exception as e:
        print(f"Error processing row: {e}")
        return None


def summarize(x, trials_expected=20, rt_outlier_low=100, rt_outlier_high=10000):
    """Summarizes the Shopping List task data by calculating various statistics for each phase of the task.

    This function calculates the number of trials, median response times, and accuracy for both the judgement and retrieval phases of the Shopping List task.
    It filters out invalid response times (e.g., -999) and outliers based on the provided lower and upper bounds.
    The results are returned as a Pandas Series with keys corresponding to the calculated statistics.

    Args:
        x (pd.DataFrame): The trial-level scored dataset for the Shopping List task.
        trials_expected (int, optional): The expected number of trials for the Shopping List task. Defaults to 20.
        rt_outlier_low (int, optional): The lower bound for filtering outliers in response times. Defaults to 100.
        rt_outlier_high (int, optional): The upper bound for filtering outliers in response times. Defaults to 10000.

    Returns:
        (pd.Series): A Pandas Series containing the summary statistics for each phase of the Shopping List task.

    """
    # ABSTRACTION TO APPEAR IN EACH SCORING SCRIPT
    d = helpers.summarize_common_metadata(x, trials_expected)

    # Define expected summary keys for both phases
    # ! HACK: These are the column names that will be returned in the summary.
    # * Having to add here so that if a phase is empty, it won't cause an error later.
    # * For instance, if the retrieval phase is empty, you get:
    # * [ERROR] Summary failed for Shopping List: 'int' object has no attribute 'startswith'
    # * This is because the summary function tries to access keys that don't exist in the dictionary when a phase/variable is empty.
    # ! This is a bit of a hack, but it works for now.
    # ? QUESTION: Is there a better way to handle this?
    # ? I'm sure there is a better way to handle this, but I've been staring at this for too long
    default_keys_by_phase = {
        "judgement": [
            "n_trials_phase_judgement",
            "phase_judgement_median_valid_response_time_overall",
            "phase_judgement_median_response_time_filtered",
        ],
        "retrieval": [
            "n_trials_phase_retrieval",
            "n_trials_phase_retrieval_correct",
            "n_trials_phase_retrieval_incorrect",
            "trials_phase_retrieval_correct_proportion",
            "trials_phase_retrieval_incorrect_proportion",
            "phase_retrieval_median_valid_response_time_overall",
            "phase_retrieval_median_valid_response_time_correct",
            "phase_retrieval_median_valid_response_time_incorrect",
            "phase_retrieval_median_response_time_filtered",
            "phase_retrieval_median_response_time_filtered_correct",
            "phase_retrieval_median_response_time_filtered_incorrect",
        ],
    }

    # Phase specific dataframes
    phase_judgement_df = x[x["phase"] == 0]
    phase_retrieval_df = x[x["phase"] == 1]
    phases = {"judgement": phase_judgement_df, "retrieval": phase_retrieval_df}

    # For each phase, calculate the trial and response time statistics
    for i in phases:
        phase = phases[i]
        # If the phase dataframe is empty, skip to the next phase
        if phase.empty:
            # Debugging output to check which phase is empty
            # print(f"Skipping empty phase dataframe: {i}")

            # Fill keys with NaN values if phase dataframe is empty, in the same order as the phases are called
            for phase_name, keys in default_keys_by_phase.items():
                if i == phase_name:
                    d.update({k: np.nan for k in keys})
            continue

        # Phase-specific trial counts
        d[f"n_trials_phase_{i}"] = phase["trial_index"].nunique()

        # Retrieval Phase Accuracy
        if i == "retrieval":
            d["n_trials_phase_retrieval_correct"] = sum(
                phase["metric_retrieval_accuracy"] == True
            )
            d["n_trials_phase_retrieval_incorrect"] = sum(
                phase["metric_retrieval_accuracy"] == False
            )
            d["trials_phase_retrieval_correct_proportion"] = (
                d["n_trials_phase_retrieval_correct"] / d["n_trials_phase_retrieval"]
            )
            d["trials_phase_retrieval_incorrect_proportion"] = (
                d["n_trials_phase_retrieval_incorrect"] / d["n_trials_phase_retrieval"]
            )

        # Overall response time stats for valid responses (not -999)
        # ! ALERT: Was noticing a lot of -999 values in the response_time_ms column for the shopping list task.
        # * I'm assuming these are invalid responses, so we filter them out.
        # * I'm filtering them out BEFORE calculating the overall median response times and filtered median response times.
        # ? QUESTION: Is that correct, or should I leave them in for the overall median response time calculation and let the rt_outlier variables take care of them?
        valid_rt = phase.loc[(phase["response_time_ms"] != -999), "response_time_ms"]
        d[f"phase_{i}_median_valid_response_time_overall"] = valid_rt.median()

        # Retrieval Phase Accuracy Valid Response Time Stats
        if i == "retrieval":
            valid_rt_correct = phase.loc[
                (phase["response_time_ms"] != -999)
                & (phase["metric_retrieval_accuracy"] == True),
                "response_time_ms",
            ]
            d["phase_retrieval_median_valid_response_time_correct"] = (
                valid_rt_correct.median()
            )

            valid_rt_incorrect = phase.loc[
                (phase["response_time_ms"] != -999)
                & (phase["metric_retrieval_accuracy"] == False),
                "response_time_ms",
            ]
            d["phase_retrieval_median_valid_response_time_incorrect"] = (
                valid_rt_incorrect.median()
            )

        # Filter response times to remove outliers and missing values (-999)
        rt_filtered = phase.loc[
            (phase["response_time_ms"] >= rt_outlier_low)
            & (phase["response_time_ms"] <= rt_outlier_high),
            "response_time_ms",
        ]
        d[f"phase_{i}_median_response_time_filtered"] = rt_filtered.median()

        # Filtered Retrieval Phase Accuracy Response Time Stats
        if i == "retrieval":
            rt_filtered_correct = phase.loc[
                (phase["metric_retrieval_accuracy"] == True)
                & (phase["response_time_ms"] >= rt_outlier_low)
                & (phase["response_time_ms"] <= rt_outlier_high),
                "response_time_ms",
            ]
            d["phase_retrieval_median_response_time_filtered_correct"] = (
                rt_filtered_correct.median()
            )

            rt_filtered_incorrect = phase.loc[
                (phase["metric_retrieval_accuracy"] == False)
                & (phase["response_time_ms"] >= rt_outlier_low)
                & (phase["response_time_ms"] <= rt_outlier_high),
                "response_time_ms",
            ]
            d["phase_retrieval_median_response_time_filtered_incorrect"] = (
                rt_filtered_incorrect.median()
            )

    # Debugging output to check the summary dictionary keys for each session of the Shopping List task
    # print("[DEBUG] Summary dict keys:", list(d.keys()))
    return pd.Series(d)

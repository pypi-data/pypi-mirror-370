import ast

import pandas as pd

from ..core import helpers

# ! BUG: The scored data export with Trailmaking is incredibly broken.
#      In "mongodb_export_scored.csv"
#      The JSON is not properly formatted in the csv, it's spanning multiple rows and columns.


def score_pen_lifts(row: pd.Series):
    """
    Retrieves the number of pen lifts from the "drawpad_strokes" column for a single trial in the Trailmaking task.

    Args:
        row (pd.Series): A single row of the trial-level Trailmaking task dataframe.

    Returns:
        (int | None):
            The number of pen lifts, or None if an error occurs.
    """

    try:
        strokes = row.get("drawpad_strokes", [])
        # Handle stringified lists
        if isinstance(strokes, str):
            try:
                strokes = ast.literal_eval(strokes)
            except Exception:
                strokes = []
        pen_lifts = sum(
            1
            for stroke in strokes
            if isinstance(stroke, list)
            for event in stroke
            if isinstance(event, dict) and event.get("type") == "StrokeEnd"
        )
        # print(f"Pen lifts: {pen_lifts}")
        return pen_lifts
    except Exception as e:
        print(f"Error processing row for pen lifts: {e}")
        return None


def score_dots_correct(row: pd.Series):
    """
    Retrieves the number of correct dots from the "node_touch_events" column for a single trial in the Trailmaking task.

    Args:
        row (pd.Series): A single row of the trial-level Trailmaking task dataframe.

    Returns:
        (int | None):
            The number of correct dots, or None if an error occurs.
    """

    try:
        node_events = row.get("node_touch_events", [])
        # Handle stringified lists
        if isinstance(node_events, str):
            try:
                node_events = ast.literal_eval(node_events)
            except Exception:
                node_events = []
        correct_dots = sum(
            1
            for event in node_events
            if isinstance(event, dict) and event.get("correct_in_sequence") is True
        )
        return correct_dots
    except Exception as e:
        print(f"Error processing row for correct dots: {e}")
        return None


def summarize(x, trials_expected=1):
    """
    Summarizes the Trailmaking task data by calculating statistics such as pen lifts and correct dots.

    This function computes the number of pen lifts and correct dots for the Trailmaking task,
    and retrieves overall response time.

    Args:
        x (pd.DataFrame): The trial-level scored dataset for the Trailmaking task.
        trials_expected (int, optional): The expected number of trials. Defaults to 1.

    Returns:
        pd.Series: A Pandas Series containing the summary statistics for the Trailmaking task.
    """

    d = helpers.summarize_common_metadata(x, trials_expected)

    # Summarize pen lift and correct dot counts
    d["n_pen_lifts"] = x["metric_pen_lifts"].sum()
    d["n_dots_correct"] = x["metric_dots_correct"].sum()
    # RT for whole task
    d["median_response_time_overall"] = x["response_time_ms"].median()

    return pd.Series(d)

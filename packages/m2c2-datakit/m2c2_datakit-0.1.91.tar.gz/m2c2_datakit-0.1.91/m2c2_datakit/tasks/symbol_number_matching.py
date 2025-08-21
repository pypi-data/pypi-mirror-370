import pandas as pd


def score(row, legacy=False):
    try:
        if legacy:
            return row["user_response"] == row["correct_response"]
        else:
            return row["user_response_index"] == row["correct_response_index"]
    except Exception as e:
        print(f"Error processing row: {e}")
        return None


def summarize(x, rt_outlier_low=100, rt_outlier_high=10000):
    d = {}

    # trial counts and validation checks
    d["n_trials"] = x["trial_index"].nunique()

    # tabulate accuracy
    d["n_trials_correct"] = (x["response_correct"] == True).sum()

    # Check if trials match expectations
    d["prop_correct"] = d["n_trials_correct"] / d["n_trials"]
    d["perc_correct"] = d["prop_correct"] * 100

    # Filter out outliers: RT < 100 ms or RT > 10,000 ms
    rt_filtered = x.loc[
        (x["response_time_ms"] >= rt_outlier_low)
        & (x["response_time_ms"] <= rt_outlier_high),
        "response_time_ms",
    ]
    d["median_response_time_filtered"] = rt_filtered.median()
    d["n_trials_filtered"] = d["n_trials"] - rt_filtered.count()

    # get RTs for correct and incorrect trials
    d["median_response_time_overall"] = x["response_time_ms"].median()
    d["median_response_time_correct"] = x.loc[
        (x["response_correct"] == True),
        "response_time_ms",
    ].median()

    # return as series
    indices = list(d.keys())
    return pd.Series(
        d,
        index=indices,
    )

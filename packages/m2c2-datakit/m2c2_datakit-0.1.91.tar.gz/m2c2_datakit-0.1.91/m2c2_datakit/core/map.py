import re

from m2c2_datakit.tasks import (
    color_dots,
    color_match,
    color_shapes,
    digit_span,
    even_odd,
    go_no_go,
    go_no_go_fade,
    grid_memory,
    shopping_list,
    stroop,
    symbol_number_matching,
    symbol_search,
    trailmaking,
)


def expand_func_map(base_map):
    expanded_map = {}
    for key, value in base_map.items():
        lower = key.lower()
        sentence = key.capitalize()
        hyphenated = re.sub(r"\s+", "-", lower)

        # Original
        expanded_map[key] = value
        # Lowercase
        expanded_map[lower] = value
        # Sentence case
        expanded_map[sentence] = value
        # Hyphenated lowercase
        expanded_map[hyphenated] = value

    return expanded_map


DEFAULT_FUNC_MAP_SCORING = {
    "Grid Memory": [
        ("error_distance_hausdorff", grid_memory.score_hausdorff),
        ("error_distance_mean", grid_memory.score_mean_error),
        ("error_distance_sum", grid_memory.score_sum_error),
    ],
    "Symbol Search": [
        ("accuracy", symbol_search.score_accuracy),
    ],
    "Color Dots": [
        ("accuracy_location", color_dots.score_accuracy_location),
        ("accuracy_color", color_dots.score_acccuracy_color),
    ],
    "Shopping List": [
        ("retrieval_accuracy", shopping_list.score_accuracy),
    ],
    "Trailmaking": [
        ("pen_lifts", trailmaking.score_pen_lifts),
        ("dots_correct", trailmaking.score_dots_correct),
    ],
    "Go No Go": [
        ("accuracy", go_no_go.score_errors),
    ],
    "Color Shapes": [
        ("accuracy", color_shapes.score_accuracy),
        ("trial_type", color_shapes.score_signal),
    ],
    "Stroop": [
        ("accuracy", stroop.score_accuracy),
        ("trial_type", stroop.score_trial_type),
    ],
    "Go No Go Fade": [
        ("accuracy", go_no_go_fade.score_accuracy),
        ("response_time", go_no_go_fade.score_response_time),
    ],
    "Color Match": [
        ("accuracy", color_match.score_accuracy),
        ("euclidean_color_distance", color_match.score_color_distance),
    ],
    "Digit Span": [
        ("accuracy", digit_span.score_accuracy),
    ],
    "Odd or Even": [
        ("accuracy", even_odd.score_accuracy),
        ("trial_type", even_odd.score_trial_type),
    ],
}

DEFAULT_FUNC_MAP_SCORING = expand_func_map(DEFAULT_FUNC_MAP_SCORING)

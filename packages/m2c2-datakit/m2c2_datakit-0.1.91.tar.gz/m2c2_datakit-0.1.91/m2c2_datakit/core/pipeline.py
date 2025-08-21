import pandas as pd
from pathlib import Path
from typing import Callable, Dict, List, Tuple, Optional, Union

from .config import settings
from .log import log_info, log_exception, log_error
from .helpers import (
    validate_input,
    export_dataframe,
    export_jsonld_metadata,
    _append_metadata,
    _generate_metadata,
    score_by_group_key,
    summarize_by_group_key,
)
from .importers import DataImporter, MultiCSVImporter


# === LASSIE Core ===
class LASSIE:
    def __init__(self):
        self.flat: Optional[pd.DataFrame] = None
        self.grouped: Optional[Dict[str, pd.DataFrame]] = None
        self.flat_scored: Optional[pd.DataFrame] = None
        self.grouped_scored: Optional[Dict[str, pd.DataFrame]] = None
        self.grouped_summary: Optional[pd.DataFrame] = None
        self.scoring_func_map: Optional[Dict[str, List[Tuple[str, Callable]]]] = None
        self.validated: bool = False
        self.activities: Optional[Dict[str, set]] = None
        self.timestamp: Optional[str] = None
        self.source_name: Optional[str] = None
        self.source_path: Optional[str] = None
        self.errors: Optional[List[str]] = None
        self.activity_name_col: Optional[str] = None
        self.raw_data_stats: Optional[Dict[str, pd.DataFrame]] = None

    def load(
        self,
        source_name: str,
        source_path: str = None,
        source_map: dict = None,
        activity_name_col="activity_name",
    ):
        self.source_name = source_name

        if source_name == "multicsv":
            if activity_name_col is None:
                log_error("[L] Missing activity_name_col for multicsv load", {})
                raise ValueError(
                    "`activity_name_col` must be provided for source_name='multicsv'"
                )
            if source_map is None:
                log_error("[L] Missing source_map for multicsv load", {})
                raise ValueError(
                    "`source_map` must be provided for source_name='multicsv'"
                )
            importer = MultiCSVImporter()
            (
                self.flat,
                self.grouped,
                self.validated,
                self.activities,
                self.timestamp,
            ) = importer.load(source_map, activity_name_col=activity_name_col)
        else:
            if source_path is None:
                log_error(
                    "[L] Missing source_path for standard load",
                    {"source_name": source_name},
                )
                raise ValueError(
                    "`source_path` must be provided for source_name other than 'multicsv'"
                )
            self.source_path = source_path
            (
                self.flat,
                self.grouped,
                self.validated,
                self.activities,
                self.timestamp,
            ) = DataImporter.load_from(source_name, source_path)

        log_info(
            f"[L] Loaded {source_name} data at {self.timestamp}",
            {"session_timestamp": self.timestamp},
        )
        return self

    def assure(self, required_columns: List[str]):
        if self.flat is None:
            raise ValueError("No DataFrame loaded. Make sure to call `load()` first.")
        # TODO: leverage self.source_name for default required_columns
        validate_input(self.flat, required_columns=required_columns)
        log_info(
            "[A] Data assurance check passed.", {"session_timestamp": self.timestamp}
        )
        return self

    def score(
        self,
        scoring_func_map: Dict[
            str, List[Tuple[str, Callable]]
        ] = settings.DEFAULT_FUNC_MAP_SCORING,
    ):
        if scoring_func_map is None:
            self.errors = self.errors.append[
                "Must provide a scoring_func_map to the score() method."
            ]
            raise ValueError(
                "You must provide a scoring_func_map to the score() method."
            )
            # consider an autoscoring method withd defaults
        if not self.grouped:
            self.errors = self.errors.append[
                "No grouped data available. Did you run `load()`?"
            ]
            raise ValueError("No grouped data available. Did you run `load()`?")
        self.scoring_func_map = scoring_func_map or settings.DEFAULT_FUNC_MAP_SCORING
        self.grouped_scored = score_by_group_key(self.grouped, scoring_func_map)
        self.flat_scored = pd.concat(self.grouped_scored.values(), ignore_index=True)

        log_info("[S] Scoring completed.", {"session_timestamp": self.timestamp})
        return self

    def summarize(
        self,
        summary_func_map: Dict[str, Callable],
        groupby_cols: List[str] = ['participant_id', 'session_id', 'session_uuid'],
        **kwargs,
    ):
        """
        Summarize scored data using task-specific summary functions, with metadata.

        Parameters:
            summary_func_map (Dict[str, Callable]): Map of activity/task -> summary function.
            **kwargs: Additional arguments passed to the summarization functions.
        """
        if self.grouped_scored is None:
            raise ValueError("Scoring must be completed before summarizing.")

        self.summary_func_map = summary_func_map
        
        # TODO: add a default func map
        # summary_func_map = {
        #     "Symbol Search": m2c2.tasks.symbol_search.summarize,
        #     "Grid Memory": m2c2.tasks.grid_memory.summarize,
        # }

        try:
            # Determine columns based on data source (diff keys, diff platforms)
            
            # Apply group-specific summarization
            self.grouped_summary = summarize_by_group_key(
                self.grouped_scored,
                summary_func_map,
                groupby_cols=groupby_cols,
                **kwargs,
            )

            # Optionally flatten into one wide dataframe
            self.flat_summary = pd.concat(
                self.grouped_summary.values(), ignore_index=True
            )

            log_info(
                "[S] Summarization by activity completed.",
                {"session_timestamp": self.timestamp},
            )
        except Exception as e:
            log_exception(
                "Summarization by activity failed",
                e,
                {
                    "session_timestamp": self.timestamp,
                    "activities": list(self.grouped_scored.keys()),
                },
            )
            raise

        return self

    def inspect(self, plot_type: str = "distribution"):
        if self.flat_scored is None:
            self.errors = self.errors.append["No scored data to inspect."]
            raise ValueError("No scored data to inspect.")
        if plot_type == "distribution":
            from .plot import plot_distribution, plot_pairplot  # lazy import

            plot_distribution(self.flat_scored)
            log_info(
                "[I] Distribution plot generated.",
                {"session_timestamp": self.timestamp},
            )
        elif plot_type == "pairplot":
            from .plot import plot_distribution, plot_pairplot  # lazy import

            plot_pairplot(self.flat_scored)
            log_info("[I] Pairplot generated.", {"session_timestamp": self.timestamp})
        else:
            raise ValueError("Invalid plot type. Use 'distribution' or 'pairplot'.")
        return self

    def export(
        self,
        file_basename: str,
        formats: List[str] = [".csv"],
        include_metadata: bool = True,
        directory: Union[str, Path] = ".",
    ):
        export_dir = Path(directory)
        export_dir.mkdir(parents=True, exist_ok=True)

        if self.flat_scored is not None:
            for fmt in formats:
                export_dataframe(
                    self.flat_scored,
                    export_dir / f"{file_basename}_scored",
                    format=fmt,
                )

        if self.grouped_summary is not None:
            for task_name, df in self.grouped_summary.items():
                for fmt in formats:
                    export_dataframe(
                        df,
                        export_dir / f"{file_basename}_summary_{task_name}",
                        format=fmt,
                    )

        if include_metadata and self.flat_scored is not None:
            export_jsonld_metadata(
                self.flat_scored,
                filename=export_dir / f"{file_basename}_metadata.json",
            )

        return self

    def export_codebook(
        self,
        filename: str = "codebook",
        custom_descriptions: Dict[str, str] = None,
        directory: Union[str, Path] = ".",
    ):

        export_dir = Path(directory)
        export_dir.mkdir(parents=True, exist_ok=True)

        # TODO: add way to do this for grouped summary data
        df = self.flat_scored
        custom_descriptions = custom_descriptions or {}

        codebook_df = pd.DataFrame(
            {
                "Variable": df.columns,
                "Data Type": [df[col].dtype for col in df.columns],
                "Non-Null Count": [df[col].count() for col in df.columns],
                "Description": [custom_descriptions.get(col, "") for col in df.columns],
            }
        )

        filename = (
            export_dir / f"{self.source_name}_codebook_flat_scored_{self.timestamp}.md"
        )
        md = codebook_df.to_markdown(index=False)

        with open(filename, "w") as f:
            f.write(f"# Codebook\n")
            f.write("----")
            f.write(f"\n\nGenerated on `{self.timestamp}`\n")
            f.write(f"Package version: `{settings.PACKAGE_VERSION}`\n")
            f.write(f"Source: `{self.source_name}`\n")
            f.write(f"Source Path: `{self.source_path}`\n")
            f.write("----")
            f.write("\n\n")
            f.write(md)

    def whats_inside(
        self, verbose: bool = True
    ) -> Dict[str, Union[str, int, bool, None]]:
        state = {
            "timestamp": self.timestamp,
            "source_name": self.source_name,
            "source_path": self.source_path,
            "flat_loaded": self.flat is not None,
            "flat_shape": self.flat.shape if self.flat is not None else None,
            "grouped_loaded": self.grouped is not None,
            "n_groups": len(self.grouped) if self.grouped else None,
            "flat_scored": self.flat_scored is not None,
            "flat_scored_shape": (
                self.flat_scored.shape if self.flat_scored is not None else None
            ),
            "grouped_scored": self.grouped_scored is not None,
            "n_grouped_scored": (
                len(self.grouped_scored) if self.grouped_scored else None
            ),
            "grouped_summary": self.grouped_summary is not None,
            "grouped_summary_shape": (
                self.grouped_summary.shape if self.grouped_summary is not None else None
            ),
            "scoring_func_map_loaded": self.scoring_func_map is not None,
            "activities_loaded": self.activities is not None,
            "validated": self.validated,
            "errors": self.errors,
        }

        if verbose:
            from pprint import pprint

            print("🧠 LASSIE Instance Overview:")
            pprint(state)

        return state

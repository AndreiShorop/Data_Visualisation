from __future__ import annotations

from pathlib import Path

import pandas as pd
import sweetviz as sv


class SweetvizReportService:
    def __init__(self, output_paths: dict[str, Path]) -> None:
        self._output_paths = output_paths

    def generate_report(self, key: str, df: pd.DataFrame) -> Path:
        output_path = self._output_paths[key]
        output_path.parent.mkdir(parents=True, exist_ok=True)

        report = sv.analyze(df)
        report.show_html(
            filepath=str(output_path),
            open_browser=False,
            layout="widescreen",
            scale=1.0,
        )
        return output_path

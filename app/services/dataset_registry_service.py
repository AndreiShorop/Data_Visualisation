from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path

import pandas as pd


@dataclass(frozen=True)
class DatasetPlugin:
    key: str
    label: str
    csv_path: Path
    report_path: Path
    read_csv_options: dict[str, object] = field(default_factory=dict)
    date_columns: list[str] = field(default_factory=list)
    multi_value_columns: list[str] = field(default_factory=list)


class DatasetRegistryService:
    def __init__(self, base_dir: Path, config_path: Path) -> None:
        self._base_dir = base_dir
        self._config_path = config_path

    def load_plugins(self) -> list[DatasetPlugin]:
        payload = json.loads(self._config_path.read_text(encoding="utf-8"))
        plugins: list[DatasetPlugin] = []

        for item in payload.get("datasets", []):
            schema = item.get("schema", {})
            plugins.append(
                DatasetPlugin(
                    key=str(item["key"]),
                    label=str(item.get("label", item["key"])).strip() or str(item["key"]),
                    csv_path=self._base_dir / str(item["csv_path"]),
                    report_path=self._base_dir / str(item["report_path"]),
                    read_csv_options=dict(item.get("read_csv_options", {})),
                    date_columns=list(schema.get("date_columns", [])),
                    multi_value_columns=list(schema.get("multi_value_columns", [])),
                )
            )

        if not plugins:
            raise ValueError("No datasets defined in datasets configuration.")
        return plugins

    def load_dataframes(self, plugins: list[DatasetPlugin]) -> dict[str, pd.DataFrame]:
        datasets: dict[str, pd.DataFrame] = {}
        for plugin in plugins:
            datasets[plugin.key] = pd.read_csv(plugin.csv_path, **plugin.read_csv_options)
        return datasets

    def build_report_paths(self, plugins: list[DatasetPlugin]) -> dict[str, Path]:
        return {plugin.key: plugin.report_path for plugin in plugins}

    def build_labels(self, plugins: list[DatasetPlugin]) -> dict[str, str]:
        return {plugin.key: plugin.label for plugin in plugins}

    def build_schema_hints(self, plugins: list[DatasetPlugin]) -> dict[str, dict[str, list[str]]]:
        return {
            plugin.key: {
                "date_columns": plugin.date_columns,
                "multi_value_columns": plugin.multi_value_columns,
            }
            for plugin in plugins
        }

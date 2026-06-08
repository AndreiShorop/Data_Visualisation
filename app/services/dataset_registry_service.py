from __future__ import annotations

import json
import re
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

    def register_new_dataset(self, key: str, label: str, csv_content: bytes, read_csv_options: dict = None) -> bool:
        """Saves a new CSV file and updates the datasets_config.json file."""
        try:
            # 1. Save CSV file
            safe_key = re.sub(r'[^a-zA-Z0-9_]', '', key.lower())
            upload_dir = self._base_dir / "data" / "Uploads"
            upload_dir.mkdir(parents=True, exist_ok=True)
            
            csv_filename = f"{safe_key}.csv"
            csv_path = upload_dir / csv_filename
            csv_path.write_bytes(csv_content)

            # 2. Update config file
            config = json.loads(self._config_path.read_text(encoding="utf-8"))
            
            # Check if key already exists
            if any(d["key"] == safe_key for d in config.get("datasets", [])):
                return False

            new_entry = {
                "key": safe_key,
                "label": label,
                "csv_path": str(Path("data/Uploads") / csv_filename),
                "report_path": str(Path("html_reports") / f"{safe_key}_report.html"),
                "read_csv_options": read_csv_options or {},
                "schema": {
                    "date_columns": [],
                    "multi_value_columns": []
                }
            }
            
            config.setdefault("datasets", []).append(new_entry)
            self._config_path.write_text(json.dumps(config, indent=2), encoding="utf-8")
            return True
        except Exception:
            return False

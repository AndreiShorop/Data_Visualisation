from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path

from app.models.state import AppState, DatasetViewState, FilterState, SortSpec


class PreferencesService:
    def __init__(self, settings_path: Path) -> None:
        self._settings_path = settings_path

    def load(self) -> AppState:
        if not self._settings_path.exists():
            return AppState()

        try:
            data = json.loads(self._settings_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return AppState()

        state = AppState(
            selected_dataset=data.get("selected_dataset", "fifa"),
            window_geometry=data.get("window_geometry", "1280x820"),
            current_page=data.get("current_page", "Dashboard"),
        )

        raw_dataset_states = data.get("dataset_states", {})
        for key, value in raw_dataset_states.items():
            raw_sorts = value.get("sort_specs", [])
            sort_specs = [SortSpec(column=item.get("column", ""), ascending=bool(item.get("ascending", True))) for item in raw_sorts if item.get("column")]
            raw_filters = value.get("filters", {})
            filters = FilterState(
                text_query=raw_filters.get("text_query", ""),
                categorical_column=raw_filters.get("categorical_column", ""),
                categorical_value=raw_filters.get("categorical_value", ""),
                numeric_column=raw_filters.get("numeric_column", ""),
                min_value=raw_filters.get("min_value", ""),
                max_value=raw_filters.get("max_value", ""),
            )
            state.dataset_states[key] = DatasetViewState(
                visible_columns=list(value.get("visible_columns", [])),
                sort_specs=sort_specs,
                filters=filters,
            )
        return state

    def save(self, state: AppState) -> None:
        payload = asdict(state)
        self._settings_path.parent.mkdir(parents=True, exist_ok=True)
        self._settings_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

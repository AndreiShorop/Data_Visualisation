from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class SortSpec:
    column: str
    ascending: bool = True


@dataclass
class FilterState:
    text_query: str = ""
    categorical_column: str = ""
    categorical_value: str = ""
    numeric_column: str = ""
    min_value: str = ""
    max_value: str = ""


@dataclass
class DatasetViewState:
    visible_columns: list[str] = field(default_factory=list)
    sort_specs: list[SortSpec] = field(default_factory=list)
    filters: FilterState = field(default_factory=FilterState)


@dataclass
class AppState:
    selected_dataset: str = "fifa"
    window_geometry: str = "1280x820"
    current_page: str = "Dashboard"
    dataset_states: dict[str, DatasetViewState] = field(default_factory=dict)

    def get_dataset_state(self, key: str) -> DatasetViewState:
        if key not in self.dataset_states:
            self.dataset_states[key] = DatasetViewState()
        return self.dataset_states[key]

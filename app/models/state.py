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
    multi_select_column: str = ""
    multi_select_values: list[str] = field(default_factory=list)
    numeric_column: str = ""
    min_value: str = ""
    max_value: str = ""
    date_column: str = ""
    start_date: str = ""
    end_date: str = ""


@dataclass
class WidgetConfig:
    widget_id: str
    title: str
    widget_type: str
    size: str = "medium"
    pinned: bool = False
    visible: bool = True


@dataclass
class DatasetViewState:
    visible_columns: list[str] = field(default_factory=list)
    sort_specs: list[SortSpec] = field(default_factory=list)
    filters: FilterState = field(default_factory=FilterState)
    dashboard_widgets: list[WidgetConfig] = field(default_factory=list)


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

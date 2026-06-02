from __future__ import annotations

from collections.abc import Callable
import uuid

import pandas as pd

from app.models.state import FilterState, SortSpec, WidgetConfig
from app.services.metadata_service import MetadataService
from app.services.preferences_service import PreferencesService
from app.services.query_service import QueryService


class DashboardController:
    def __init__(
        self,
        datasets: dict[str, pd.DataFrame],
        dataset_labels: dict[str, str],
        schema_hints: dict[str, dict[str, list[str]]],
        preferences_service: PreferencesService,
        query_service: QueryService,
        metadata_service: MetadataService,
        on_generate_report: Callable[[str, pd.DataFrame], None],
    ) -> None:
        self._datasets = datasets
        self._dataset_labels = dataset_labels
        self._schema_hints = schema_hints
        self._preferences_service = preferences_service
        self._query_service = query_service
        self._metadata_service = metadata_service
        self._on_generate_report = on_generate_report

        self._state = self._preferences_service.load()
        self._history: list[tuple[str, str]] = []

        self._view = None
        self._current_df = pd.DataFrame()

    def bind_view(self, view: object) -> None:
        self._view = view
        self._view.set_window_geometry(self._state.window_geometry)
        self._view.set_dataset_buttons(self._dataset_labels)

        selected = self._state.selected_dataset
        if selected not in self._datasets:
            selected = next(iter(self._datasets.keys()))

        self.select_dataset(selected, push_history=False)

    def select_dataset(self, key: str, push_history: bool = True) -> None:
        if key not in self._datasets:
            return

        if push_history and self._state.selected_dataset:
            self._history.append(("dataset", self._state.selected_dataset))

        self._state.selected_dataset = key
        source_df = self._datasets[key]
        dataset_state = self._state.get_dataset_state(key)
        hints = self._schema_hints.get(key, {})

        categorical_columns, numeric_columns, date_columns, multi_columns = self._metadata_service.classify_columns(source_df, hints)
        category_values = self._metadata_service.categorical_values(source_df, dataset_state.filters.categorical_column)
        multi_values = self._metadata_service.multi_values(source_df, dataset_state.filters.multi_select_column)

        self._view.set_filter_options(
            all_columns=[str(col) for col in source_df.columns],
            categorical_columns=categorical_columns,
            numeric_columns=numeric_columns,
            date_columns=date_columns,
            multi_columns=multi_columns,
            categorical_values=category_values,
            multi_values=multi_values,
        )
        self._view.set_filter_state(dataset_state.filters)

        if not dataset_state.dashboard_widgets:
            dataset_state.dashboard_widgets = self._default_widgets()

        self._refresh_table_and_charts()
        self._view.select_tab(self._state.current_page)

    def on_filter_column_changed(self, column: str) -> None:
        key = self._state.selected_dataset
        source_df = self._datasets[key]
        values = self._metadata_service.categorical_values(source_df, column)
        self._view.update_filter_values(values)

    def on_multi_filter_column_changed(self, column: str) -> None:
        key = self._state.selected_dataset
        source_df = self._datasets[key]
        values = self._metadata_service.multi_values(source_df, column)
        self._view.update_multi_filter_values(values)

    def on_filters_changed(self, filters: FilterState) -> None:
        key = self._state.selected_dataset
        self._state.get_dataset_state(key).filters = filters
        self._refresh_table_and_charts()

    def on_sorts_changed(self, specs: list[SortSpec]) -> None:
        key = self._state.selected_dataset
        self._state.get_dataset_state(key).sort_specs = specs
        self._refresh_table_and_charts()

    def on_visible_columns_changed(self, columns: list[str]) -> None:
        key = self._state.selected_dataset
        self._state.get_dataset_state(key).visible_columns = columns
        self._refresh_table_only()

    def on_row_selected(self, row: pd.Series) -> None:
        self._view.show_detail(self._state.selected_dataset, row)
        self._state.current_page = "Details"
        self._view.select_tab("Details")
        self._view.set_breadcrumb(f"Dashboard > Table > Record > Details ({self._state.selected_dataset.title()})")

    def on_chart_item_clicked(self, filter_column: str, filter_value: str) -> None:
        key = self._state.selected_dataset
        dataset_state = self._state.get_dataset_state(key)

        if filter_column == "risk_tier":
            dataset_state.filters.numeric_column = "addiction_score"
            if filter_value == "Low":
                dataset_state.filters.min_value = ""
                dataset_state.filters.max_value = "55"
            elif filter_value == "Moderate":
                dataset_state.filters.min_value = "55"
                dataset_state.filters.max_value = "60"
            elif filter_value == "High":
                dataset_state.filters.min_value = "60"
                dataset_state.filters.max_value = "65"
            else:
                dataset_state.filters.min_value = "65"
                dataset_state.filters.max_value = ""
            dataset_state.filters.categorical_column = ""
            dataset_state.filters.categorical_value = ""
        else:
            dataset_state.filters.categorical_column = filter_column
            dataset_state.filters.categorical_value = filter_value
            if filter_column == dataset_state.filters.multi_select_column:
                dataset_state.filters.multi_select_values = [filter_value]

        source_df = self._datasets[key]
        values = self._metadata_service.categorical_values(source_df, filter_column)
        self._view.update_filter_values(values)
        self._view.set_filter_state(dataset_state.filters)

        self._refresh_table_and_charts()
        self._state.current_page = "Table"
        self._view.select_tab("Table")
        self._view.set_breadcrumb(f"Dashboard > Table ({filter_column}={filter_value})")

    def on_back(self) -> None:
        if not self._history:
            return
        kind, value = self._history.pop()
        if kind == "dataset":
            self.select_dataset(value, push_history=False)

    def on_generate_report_requested(self) -> None:
        key = self._state.selected_dataset
        self._on_generate_report(key, self._current_df if not self._current_df.empty else self._datasets[key])

    def on_tab_changed(self, tab_name: str) -> None:
        self._state.current_page = tab_name
        self._view.set_breadcrumb(f"Dashboard > {tab_name}")

    def on_widget_add(self, widget_type: str, title: str) -> None:
        dataset_state = self._state.get_dataset_state(self._state.selected_dataset)
        dataset_state.dashboard_widgets.append(
            WidgetConfig(
                widget_id=str(uuid.uuid4()),
                title=title,
                widget_type=widget_type,
                size="medium",
            )
        )
        self._refresh_dashboard_widgets()

    def on_widget_remove(self, widget_id: str) -> None:
        dataset_state = self._state.get_dataset_state(self._state.selected_dataset)
        dataset_state.dashboard_widgets = [w for w in dataset_state.dashboard_widgets if w.widget_id != widget_id]
        self._refresh_dashboard_widgets()

    def on_widget_move(self, widget_id: str, delta: int) -> None:
        dataset_state = self._state.get_dataset_state(self._state.selected_dataset)
        widgets = dataset_state.dashboard_widgets
        index = next((i for i, w in enumerate(widgets) if w.widget_id == widget_id), None)
        if index is None:
            return
        new_index = max(0, min(len(widgets) - 1, index + delta))
        if new_index == index:
            return
        widgets[index], widgets[new_index] = widgets[new_index], widgets[index]
        self._refresh_dashboard_widgets()

    def on_widget_pin_toggle(self, widget_id: str) -> None:
        dataset_state = self._state.get_dataset_state(self._state.selected_dataset)
        for widget in dataset_state.dashboard_widgets:
            if widget.widget_id == widget_id:
                widget.pinned = not widget.pinned
                break
        self._refresh_dashboard_widgets()

    def on_widget_resize(self, widget_id: str) -> None:
        cycle = {"small": "medium", "medium": "large", "large": "small"}
        dataset_state = self._state.get_dataset_state(self._state.selected_dataset)
        for widget in dataset_state.dashboard_widgets:
            if widget.widget_id == widget_id:
                widget.size = cycle.get(widget.size, "medium")
                break
        self._refresh_dashboard_widgets()

    def shutdown(self, window_geometry: str) -> None:
        self._state.window_geometry = window_geometry
        self._preferences_service.save(self._state)

    def _refresh_table_and_charts(self) -> None:
        key = self._state.selected_dataset
        source_df = self._datasets[key]
        dataset_state = self._state.get_dataset_state(key)

        filtered = self._query_service.apply_filters_and_sorts(
            source_df,
            dataset_state.filters,
            dataset_state.sort_specs,
        )
        self._current_df = filtered

        visible_columns = dataset_state.visible_columns or [str(c) for c in source_df.columns]
        self._view.set_overview(self._build_summary_text(key, filtered), key)
        self._view.render_charts(key, filtered)
        self._view.render_dashboard_widgets(dataset_state.dashboard_widgets, filtered)
        self._view.set_table(filtered, visible_columns, dataset_state.sort_specs)
        self._view.set_breadcrumb(f"Dashboard > {self._state.current_page} ({key.title()})")

    def _refresh_dashboard_widgets(self) -> None:
        key = self._state.selected_dataset
        dataset_state = self._state.get_dataset_state(key)
        self._view.render_dashboard_widgets(dataset_state.dashboard_widgets, self._current_df)

    def _refresh_table_only(self) -> None:
        key = self._state.selected_dataset
        dataset_state = self._state.get_dataset_state(key)
        self._view.set_table(self._current_df, dataset_state.visible_columns, dataset_state.sort_specs)

    def _build_summary_text(self, key: str, df: pd.DataFrame) -> str:
        if key == "fifa":
            avg_rating = pd.to_numeric(df.get("rating", pd.Series(dtype=float)), errors="coerce").mean()
            rating = f"{avg_rating:.2f}" if pd.notna(avg_rating) else "N/A"
            countries = df["country"].nunique() if "country" in df.columns else 0
            return f"Rows: {len(df):,} | Columns: {df.shape[1]} | Unique Countries: {countries}\nAverage Rating: {rating}"

        if key == "movie":
            avg_pop = pd.to_numeric(df.get("Popularity", pd.Series(dtype=float)), errors="coerce").mean()
            avg_vote = pd.to_numeric(df.get("Vote_Average", pd.Series(dtype=float)), errors="coerce").mean()
            pop = f"{avg_pop:.2f}" if pd.notna(avg_pop) else "N/A"
            vote = f"{avg_vote:.2f}" if pd.notna(avg_vote) else "N/A"
            langs = df["Original_Language"].nunique() if "Original_Language" in df.columns else 0
            return f"Rows: {len(df):,} | Columns: {df.shape[1]} | Unique Languages: {langs}\nAverage Popularity: {pop} | Average Vote: {vote}"

        avg_add = pd.to_numeric(df.get("addiction_score", pd.Series(dtype=float)), errors="coerce").mean()
        avg_sleep = pd.to_numeric(df.get("sleep_hours", pd.Series(dtype=float)), errors="coerce").mean()
        add = f"{avg_add:.2f}" if pd.notna(avg_add) else "N/A"
        sleep = f"{avg_sleep:.2f}" if pd.notna(avg_sleep) else "N/A"
        countries = df["country"].nunique() if "country" in df.columns else 0
        return f"Rows: {len(df):,} | Columns: {df.shape[1]} | Countries: {countries}\nAverage Addiction Score: {add} | Average Sleep Hours: {sleep}"

    def _default_widgets(self) -> list[WidgetConfig]:
        return [
            WidgetConfig(widget_id=str(uuid.uuid4()), title="Rows KPI", widget_type="kpi_rows", size="small", pinned=True),
            WidgetConfig(widget_id=str(uuid.uuid4()), title="Columns KPI", widget_type="kpi_columns", size="small"),
            WidgetConfig(widget_id=str(uuid.uuid4()), title="Missing Values KPI", widget_type="kpi_missing", size="small"),
            WidgetConfig(widget_id=str(uuid.uuid4()), title="Table Preview", widget_type="table_preview", size="medium"),
        ]

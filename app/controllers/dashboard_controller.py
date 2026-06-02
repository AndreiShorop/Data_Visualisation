from __future__ import annotations

from collections.abc import Callable

import pandas as pd

from app.models.state import AppState, FilterState, SortSpec
from app.services.metadata_service import MetadataService
from app.services.preferences_service import PreferencesService
from app.services.query_service import QueryService


class DashboardController:
    def __init__(
        self,
        datasets: dict[str, pd.DataFrame],
        preferences_service: PreferencesService,
        query_service: QueryService,
        metadata_service: MetadataService,
        on_generate_report: Callable[[str, pd.DataFrame], None],
    ) -> None:
        self._datasets = datasets
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

        categorical_columns, numeric_columns = self._metadata_service.classify_columns(source_df)
        category_values = self._metadata_service.categorical_values(source_df, dataset_state.filters.categorical_column)

        self._view.set_filter_options(
            all_columns=[str(col) for col in source_df.columns],
            categorical_columns=categorical_columns,
            numeric_columns=numeric_columns,
            categorical_values=category_values,
        )
        self._view.set_filter_state(dataset_state.filters)

        self._refresh_table_and_charts()
        self._view.select_tab(self._state.current_page)

    def on_filter_column_changed(self, column: str) -> None:
        key = self._state.selected_dataset
        source_df = self._datasets[key]
        values = self._metadata_service.categorical_values(source_df, column)
        self._view.update_filter_values(values)

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
        dataset_state.filters.categorical_column = filter_column
        dataset_state.filters.categorical_value = filter_value

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
        self._view.set_table(filtered, visible_columns, dataset_state.sort_specs)
        self._view.set_breadcrumb(f"Dashboard > {self._state.current_page} ({key.title()})")

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

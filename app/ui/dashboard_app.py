from __future__ import annotations

from pathlib import Path
import webbrowser

import pandas as pd

from app.controllers.dashboard_controller import DashboardController
from app.services.metadata_service import MetadataService
from app.services.preferences_service import PreferencesService
from app.services.query_service import QueryService
from app.reports.sweetviz_service import SweetvizReportService
from app.views.dashboard_view import DashboardView


class DashboardApp:
    def __init__(
        self,
        datasets: dict[str, pd.DataFrame],
        dataset_labels: dict[str, str],
        schema_hints: dict[str, dict[str, list[str]]],
        report_service: SweetvizReportService,
        settings_path: Path,
    ) -> None:
        self._report_service = report_service
        self._controller = DashboardController(
            datasets=datasets,
            dataset_labels=dataset_labels,
            schema_hints=schema_hints,
            preferences_service=PreferencesService(settings_path=settings_path),
            query_service=QueryService(),
            metadata_service=MetadataService(),
            on_generate_report=self._generate_report,
        )
        self._view = DashboardView(
            callbacks={
                "dataset": self._controller.select_dataset,
                "filter_column_changed": self._controller.on_filter_column_changed,
                "multi_filter_column_changed": self._controller.on_multi_filter_column_changed,
                "filters_changed": self._controller.on_filters_changed,
                "sorts_changed": self._controller.on_sorts_changed,
                "columns_changed": self._controller.on_visible_columns_changed,
                "row_selected": self._controller.on_row_selected,
                "chart_clicked": self._controller.on_chart_item_clicked,
                "widget_add": self._controller.on_widget_add,
                "widget_remove": self._controller.on_widget_remove,
                "widget_move": self._controller.on_widget_move,
                "widget_pin": self._controller.on_widget_pin_toggle,
                "widget_resize": self._controller.on_widget_resize,
                "report": self._controller.on_generate_report_requested,
                "tab_changed": self._controller.on_tab_changed,
                "back": self._controller.on_back,
                "close": self._controller.shutdown,
            }
        )
        self._controller.bind_view(self._view)

    def _generate_report(self, key: str, df: pd.DataFrame) -> None:
        file_path = self._report_service.generate_report(key, df)
        webbrowser.open(file_path.as_uri())

    def run(self) -> None:
        self._view.run()

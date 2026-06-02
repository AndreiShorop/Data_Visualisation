from __future__ import annotations

from pathlib import Path
import webbrowser

import pandas as pd

from app.controllers.dashboard_controller import DashboardController
from app.models.state import FilterState, SortSpec
from app.services.metadata_service import MetadataService
from app.services.preferences_service import PreferencesService
from app.services.query_service import QueryService
from app.reports.sweetviz_service import SweetvizReportService
from app.views.dashboard_view import DashboardView


class DashboardApp:
    def __init__(self, datasets: dict[str, pd.DataFrame], report_service: SweetvizReportService, settings_path: Path) -> None:
        self._report_service = report_service
        self._controller = DashboardController(
            datasets=datasets,
            preferences_service=PreferencesService(settings_path=settings_path),
            query_service=QueryService(),
            metadata_service=MetadataService(),
            on_generate_report=self._generate_report,
        )
        self._view = DashboardView(
            callbacks={
                "dataset": self._controller.select_dataset,
                "filter_column_changed": self._controller.on_filter_column_changed,
                "filters_changed": self._controller.on_filters_changed,
                "sorts_changed": self._controller.on_sorts_changed,
                "columns_changed": self._controller.on_visible_columns_changed,
                "row_selected": self._controller.on_row_selected,
                "chart_clicked": self._controller.on_chart_item_clicked,
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

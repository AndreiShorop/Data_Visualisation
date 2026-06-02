from app.config import (
    BASE_DIR,
    DATASETS_CONFIG_PATH,
    SETTINGS_PATH,
)
from app.reports.sweetviz_service import SweetvizReportService
from app.services.dataset_registry_service import DatasetRegistryService
from app.ui.dashboard_app import DashboardApp


def create_dashboard_app() -> DashboardApp:
    registry = DatasetRegistryService(base_dir=BASE_DIR, config_path=DATASETS_CONFIG_PATH)
    plugins = registry.load_plugins()
    datasets = registry.load_dataframes(plugins)
    labels = registry.build_labels(plugins)
    schema_hints = registry.build_schema_hints(plugins)
    report_service = SweetvizReportService(registry.build_report_paths(plugins))

    return DashboardApp(
        datasets,
        labels,
        schema_hints,
        report_service,
        SETTINGS_PATH,
    )


def main() -> None:
    app = create_dashboard_app()
    app.run()


if __name__ == "__main__":
    main()
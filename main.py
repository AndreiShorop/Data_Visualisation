from app.config import (
    FIFA_CSV,
    FIFA_REPORT,
    MOVIE_CSV,
    MOVIE_REPORT,
    SOCIAL_CSV,
    SOCIAL_REPORT,
    SETTINGS_PATH,
)
from app.data_loader import load_datasets
from app.reports.sweetviz_service import SweetvizReportService
from app.ui.dashboard_app import DashboardApp


def create_dashboard_app() -> DashboardApp:
    datasets = load_datasets(FIFA_CSV, MOVIE_CSV, SOCIAL_CSV)
    report_service = SweetvizReportService(
        {
            "fifa": FIFA_REPORT,
            "movie": MOVIE_REPORT,
            "social": SOCIAL_REPORT,
        }
    )
    return DashboardApp(
        {
            "fifa": datasets.fifa,
            "movie": datasets.movies,
            "social": datasets.social,
        },
        report_service,
        SETTINGS_PATH,
    )


def main() -> None:
    app = create_dashboard_app()
    app.run()


if __name__ == "__main__":
    main()
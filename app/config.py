from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
REPORTS_DIR = BASE_DIR / "html_reports"
SETTINGS_PATH = BASE_DIR / "data_visualization_settings.json"
DATASETS_CONFIG_PATH = BASE_DIR / "datasets_config.json"

FIFA_CSV = DATA_DIR / "FIFA" / "elo_ratings_wc2026.csv"
MOVIE_CSV = DATA_DIR / "Movie" / "mymoviedb.csv"
SOCIAL_CSV = DATA_DIR / "Social_Media_Addiction" / "country_wise_analysis_addiction.csv"

FIFA_REPORT = REPORTS_DIR / "fifa_dashboard.html"
MOVIE_REPORT = REPORTS_DIR / "movie_dashboard.html"
SOCIAL_REPORT = REPORTS_DIR / "social_media_addiction_dashboard.html"

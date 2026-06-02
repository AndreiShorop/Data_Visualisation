# Technical Documentation

## 1. Overview
This application renders dashboard charts inside a Tkinter desktop app and generates Sweetviz HTML reports in the browser on demand.

Flow:
1. `main.py` loads datasets.
2. `DashboardApp` displays in-app metrics and pie/bar visualizations for selected dataset.
3. `SweetvizReportService` generates HTML report for selected dataset.
4. Browser opens the generated report from `html_reports/`.

## 2. Architecture

### Entry Layer
- `main.py`
- Responsibility: wiring and bootstrapping only

### Configuration Layer
- `app/config.py`
- Responsibility: centralized paths and constants

### Data Layer
- `app/data_loader.py`
- Responsibility: CSV ingestion and parser behavior
- Note: movie data uses `engine="python"` and `on_bad_lines="skip"` for malformed rows

### Domain/Report Layer
- `app/reports/sweetviz_service.py`
- Responsibility: generate Sweetviz HTML output for a selected dataset key

### UI Layer
- `app/ui/dashboard_app.py`
- Responsibility: Tkinter controls, selected dataset state, overview text, in-app charts

## 3. SOLID Mapping
- Single Responsibility Principle:
  each module has one reason to change (data loading, Sweetviz generation, or UI).
- Open/Closed Principle:
  new datasets are added by extending dataset handlers and chart routes.
- Liskov Substitution Principle:
  dataset-specific chart logic follows a consistent selection and rendering pattern.
- Interface Segregation Principle:
  focused services (`load_datasets`, `generate_report`) expose minimal interfaces.
- Dependency Inversion Principle:
  UI depends on provided datasets and `SweetvizReportService`, not on file-system details.

## 4. Report Outputs
Generated files:
- `html_reports/fifa_dashboard.html`
- `html_reports/movie_dashboard.html`
- `html_reports/social_media_addiction_dashboard.html`

Each file is produced by Sweetviz (`sv.analyze(...).show_html(...)`) and includes automated profiling visuals.

## 5. Error Handling and Robustness
- Movie dataset parser uses tolerant mode for malformed CSV records.
- Chart rendering checks required columns and gracefully skips unavailable visuals.

## 6. Future Improvements
- Add logging and structured exceptions.
- Add unit tests for chart rendering helpers and Sweetviz service.
- Add schema validation for input datasets.
- Add caching if datasets grow significantly.

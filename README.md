# Data Visualisation Dashboard

A desktop analytics workspace built with Tkinter, Matplotlib, and Sweetviz.

This project provides:
- In-app dashboard visuals (inside Tkinter): pie charts + bar charts + summary metrics
- Browser reports generated with `sv.analyze(...).show_html(...)` for full Sweetviz profiling

## Datasets
- FIFA ratings: `data/FIFA/elo_ratings_wc2026.csv`
- Movies: `data/Movie/mymoviedb.csv`
- Social media addiction: `data/Social_Media_Addiction/country_wise_analysis_addiction.csv`

## Project Structure
- `main.py`: thin application entry point
- `app/config.py`: file and output paths
- `app/data_loader.py`: dataset loading and parsing
- `app/reports/sweetviz_service.py`: Sweetviz report generation service
- `app/ui/dashboard_app.py`: Tkinter UI with embedded pie/bar charts and overview
- `html_reports/`: generated Sweetviz HTML output files
- `docs/DOCUMENTATION.md`: technical documentation

## Installation
1. Create and activate your environment.
2. Install dependencies:

```bash
pip install -r requirements.txt
```

## Run
```bash
python main.py
```

## Usage
1. Launch the app.
2. Click one of the top dataset buttons.
3. View metrics and charts directly inside the app window.
4. Click **Generate & Open Sweetviz Report** to create/open the browser report.

## Design Principles
The codebase is intentionally modular and follows clean code and SOLID ideas:
- Single Responsibility: each module has one clear concern
- Open/Closed: add new datasets by extending chart/report handlers
- Dependency Inversion: Tkinter UI depends on data + report-service abstractions

## Extending With a New Dataset
1. Add file path constants in `app/config.py`.
2. Add loading logic in `app/data_loader.py`.
3. Register dataset key and report path in `main.py`.
4. Add chart rendering handler and button route in `app/ui/dashboard_app.py`.
5. Sweetviz generation will use the shared service automatically.

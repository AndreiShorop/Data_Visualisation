# Technical Documentation - Analytical Platform Pro

## 1. Overview
This application is a full-scale analytical platform for CSV data, featuring automated quality assessment, interactive dashboard building, and dataset version comparison.

Flow:
1. `streamlit_app.py` serves as the primary entry point.
2. `DatasetRegistryService` manages dynamic data indexing.
3. Modules:
   - **Data Quality**: Automated DQ scoring and cleaning recommendations.
   - **Dashboard Builder**: Drag-and-drop style visualization constructor using Plotly.
   - **Dataset Comparison**: Differential analysis between two file versions.

## 2. Architecture (V2.0)

### Entry Layer
- `streamlit_app.py` (Modern Web UI)
- `main.py` (Legacy Launcher)

### Service Layer
- `app/services/quality_service.py`: Logic for data validation and Quality Score (0-100).
- `app/services/comparison_service.py`: Logic for row/column/cell diffs.
- `app/services/export_service.py`: PDF (Quality) and Excel (Comparison) exports.
- `app/services/dataset_registry_service.py`: Dynamic dataset loading.

### Data Layer
- `app/data_loader.py`: Specialized loaders (e.g., tolerant parsing for Movie data).
- `data/`: Local storage for source CSV files.

## 3. SOLID Mapping
- **Single Responsibility**: Each service handles a distinct analytical domain.
- **Open/Closed**: New chart types or quality metrics can be added to services without modifying the core UI logic.
- **Liskov Substitution**: Different datasets are treated as generic Pandas objects within the builder.
- **Interface Segregation**: Focused services provide clean APIs for UI consumption.
- **Dependency Inversion**: The UI layer depends on high-level services through the registry.

## 4. Analytical Modules

### 4.1 Data Quality Report
Analyzes missing values, duplicates, outliers (IQR), and data types.
Outputs:
- **Quality Score**: 0-100 metric.
- **Issue Breakdown**: Severity-coded list (High/Medium/Low).
- **Export**: PDF summary.

### 4.2 Interactive Dashboard Builder
Professional "Power BI" style layout:
- KPI cards for global metrics.
- Multi-chart support (Bar, Line, Scatter, Pie, Histogram, Heatmap, Boxplot).
- Interactive widget management (Add/Remove/Filter).

### 4.3 Dataset Comparison
Tracks changes between file versions:
- Structural changes (Added/Removed columns).
- Statistical drift (Mean, Std, Max shifts).
- Row-level alignment via key columns.
- Export: Full Excel diff report.

## 5. Deployment
To run the platform:
```powershell
streamlit run streamlit_app.py
```

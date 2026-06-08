import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
import io

from app.services.dataset_registry_service import DatasetRegistryService
from app.services.quality_service import QualityService
from app.services.comparison_service import ComparisonService
from app.services.export_service import ExportService
from app.config import BASE_DIR, DATASETS_CONFIG_PATH

# Page Config
st.set_page_config(
    page_title="Analytical Platform Pro",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize Services
@st.cache_resource
def get_services():
    registry = DatasetRegistryService(BASE_DIR, DATASETS_CONFIG_PATH)
    quality = QualityService()
    comparison = ComparisonService()
    export = ExportService()
    return registry, quality, comparison, export

registry, quality_service, comparison_service, export_service = get_services()

# Session State for Dashboard Builder
if 'widgets' not in st.session_state:
    st.session_state.widgets = []

# Sidebar Navigation
st.sidebar.title("🚀 Navigation")
app_mode = st.sidebar.radio("Choose Module", ["Data Quality", "Dashboard Builder", "Dataset Comparison"])

# Data Loading
@st.cache_data
def load_all_datasets():
    plugins = registry.load_plugins()
    return registry.load_dataframes(plugins)

all_dfs = load_all_datasets()
dataset_options = list(all_dfs.keys())

# --- MODULE 1: DATA QUALITY ---
if app_mode == "Data Quality":
    st.title("🎯 Data Quality Report")
    selected_ds = st.selectbox("Select Dataset to Analyze", dataset_options)
    df = all_dfs[selected_ds]

    report = quality_service.analyze(df)

    # KPI Row
    col1, col2, col3, col4 = st.columns(4)
    
    # Score color coding
    score_color = "green" if report.score > 80 else "orange" if report.score > 50 else "red"
    col1.metric("Quality Score", f"{report.score}/100")
    col2.metric("Missing Values", report.missing_count)
    col3.metric("Duplicates", report.duplicate_count)
    col4.metric("Columns", len(df.columns))

    # Recommendations
    if report.recommendations:
        with st.expander("💡 Recommendations", expanded=True):
            for rec in report.recommendations:
                st.info(rec)

    # Detailed Issues Table
    st.subheader("⚠️ Detected Issues")
    if report.issues:
        issue_data = [{
            "Column": i.column,
            "Type": i.issue_type,
            "Severity": i.severity.upper(),
            "Description": i.description
        } for i in report.issues]
        
        def color_severity(val):
            color = 'red' if val == 'HIGH' else 'orange' if val == 'MEDIUM' else 'gray'
            return f'color: {color}'

        st.table(pd.DataFrame(issue_data).style.map(color_severity, subset=['Severity']))
    else:
        st.success("No significant issues detected!")

    # Exports
    st.sidebar.divider()
    if st.sidebar.button("Export Quality Report to PDF"):
        # This is a placeholder for actual PDF generation logic
        pdf_bytes = export_service.quality_report_to_pdf({
            "score": report.score,
            "missing_count": report.missing_count,
            "duplicate_count": report.duplicate_count,
            "issues": report.issues
        })
        st.sidebar.download_button("Download PDF", pdf_bytes, "quality_report.pdf", "application/pdf")

# --- MODULE 2: INTERACTIVE DASHBOARD BUILDER ---
elif app_mode == "Dashboard Builder":
    st.title("🛠️ Interactive Dashboard Builder")
    
    # Sidebar Builder Controls
    st.sidebar.subheader("Add New Widget")
    selected_ds = st.sidebar.selectbox("Source Dataset", dataset_options)
    df = all_dfs[selected_ds]
    
    chart_type = st.sidebar.selectbox("Chart Type", ["Bar", "Line", "Scatter", "Pie", "Histogram", "Boxplot", "Heatmap"])
    
    x_axis = st.sidebar.selectbox("X Axis", df.columns)
    y_axis = None
    if chart_type not in ["Histogram", "Pie"]:
        y_axis = st.sidebar.selectbox("Y Axis", [None] + list(df.columns))
    
    if st.sidebar.button("Add Widget"):
        st.session_state.widgets.append({
            "dataset": selected_ds,
            "type": chart_type,
            "x": x_axis,
            "y": y_axis,
            "id": len(st.session_state.widgets)
        })

    # Display Dashboard
    if not st.session_state.widgets:
        st.info("Start by adding widgets using the sidebar controls.")
    else:
        # KPI Row (Static example)
        kpi1, kpi2, kpi3 = st.columns(3)
        kpi1.card = True # Not a real streamlit attribute, just for visual logic
        kpi1.metric("Total Records", len(df))
        kpi2.metric("Selected Dataset", selected_ds.title())
        kpi3.metric("Active Widgets", len(st.session_state.widgets))
        
        # Grid of Widgets
        cols = st.columns(2)
        for i, widget in enumerate(st.session_state.widgets):
            with cols[i % 2]:
                with st.container(border=True):
                    st.write(f"**{widget['type']}**: {widget['x']} vs {widget['y'] or 'Count'}")
                    w_df = all_dfs[widget['dataset']]
                    
                    # Optimization: Sample large datasets for faster rendering
                    MAX_POINTS = 10000
                    if len(w_df) > MAX_POINTS and widget['type'] in ["Scatter", "Line"]:
                        w_df = w_df.sample(MAX_POINTS)
                        st.caption(f"Note: Rendering a sample of {MAX_POINTS} points for better performance.")
                    
                    fig = None
                    if widget['type'] == "Bar":
                        # For Bar charts, aggregate if there are too many unique categories
                        if w_df[widget['x']].nunique() > 50:
                            plot_df = w_df.groupby(widget['x'])[widget['y']].sum().sort_values(ascending=False).head(50).reset_index()
                            fig = px.bar(plot_df, x=widget['x'], y=widget['y'])
                        else:
                            fig = px.bar(w_df, x=widget['x'], y=widget['y'])
                    elif widget['type'] == "Line":
                        fig = px.line(w_df, x=widget['x'], y=widget['y'])
                    elif widget['type'] == "Scatter":
                        fig = px.scatter(w_df, x=widget['x'], y=widget['y'], render_mode='webgl')
                    elif widget['type'] == "Pie":
                        fig = px.pie(w_df, names=widget['x'])
                    elif widget['type'] == "Histogram":
                        fig = px.histogram(w_df, x=widget['x'])
                    elif widget['type'] == "Boxplot":
                        fig = px.box(w_df, x=widget['x'], y=widget['y'])
                    elif widget['type'] == "Heatmap":
                        corr = w_df.select_dtypes(include=[np.number]).corr()
                        fig = px.imshow(corr, text_auto=True)
                    
                    if fig:
                        fig.update_layout(height=400, margin=dict(l=20, r=20, t=40, b=20))
                        st.plotly_chart(fig, use_container_width=True)
                    
                    if st.button(f"Remove Widget {i}", key=f"del_{i}"):
                        st.session_state.widgets.pop(i)
                        st.rerun()

# --- MODULE 3: DATASET COMPARISON ---
elif app_mode == "Dataset Comparison":
    st.title("🔄 Dataset Comparison")
    
    col1, col2 = st.columns(2)
    with col1:
        ds1_name = st.selectbox("Baseline Dataset", dataset_options)
        df1 = all_dfs[ds1_name]
    with col2:
        ds2_name = st.selectbox("Comparison Dataset", dataset_options)
        df2 = all_dfs[ds2_name]
    
    key_col = st.selectbox("Key Column (to align rows)", [None] + list(df1.columns))
    
    if st.button("Run Comparison"):
        result = comparison_service.compare(df1, df2, key_col)
        
        # Stats summary
        c1, c2, c3 = st.columns(3)
        c1.metric("Rows Added", result.added_rows, delta_color="normal")
        c2.metric("Rows Removed", result.removed_rows, delta_color="inverse")
        c3.metric("Cells Changed", result.changed_cells)
        
        # Structure changes
        with st.expander("📋 Structure Differences"):
            st.write("**Added Columns:**", result.structure_diff['added'])
            st.write("**Removed Columns:**", result.structure_diff['removed'])
            
        # Stats Diff Chart
        st.subheader("📊 Statistical Shift")
        if not result.stats_diff.empty:
            st.dataframe(result.stats_diff)
            
        # Sample Diffs
        if not result.diff_sample.empty:
            st.subheader("🔍 Sample of Differences")
            st.dataframe(result.diff_sample)
            
        # Export Comparison
        st.sidebar.divider()
        if st.sidebar.button("Export Comparison to Excel"):
            excel_data = export_service.to_excel({
                "Baseline": df1,
                "Comparison": df2,
                "Stats_Diff": result.stats_diff
            })
            st.sidebar.download_button("Download Excel", excel_data, "comparison.xlsx")

# Footer
st.sidebar.divider()
st.sidebar.caption("© 2026 Analytical Platform Pro v2.0")

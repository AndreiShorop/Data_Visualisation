import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
import io
import re

from app.services.dataset_registry_service import DatasetRegistryService
from app.services.quality_service import QualityService
from app.services.comparison_service import ComparisonService
from app.services.export_service import ExportService
from app.services.auth_service import AuthService
from app.config import BASE_DIR, DATASETS_CONFIG_PATH, USERS_DB_PATH

# Page Config
st.set_page_config(
    page_title="Analytical Platform Pro",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Auth Initialization
def get_auth_service():
    return AuthService(USERS_DB_PATH)

auth_service = get_auth_service()

if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
    st.session_state.user = None

# Login Screen
if not st.session_state.authenticated:
    st.title("🔐 Login to Analytical Platform")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        with st.form("login_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            submit = st.form_submit_button("Login", use_container_width=True)
            
            if submit:
                user = auth_service.verify_user(username, password)
                if user:
                    st.session_state.authenticated = True
                    st.session_state.user = user
                    # Load widgets from DB on login
                    st.session_state.widgets = auth_service.get_user_widgets(user.username)
                    st.success(f"Welcome, {username}!")
                    st.rerun()
                else:
                    st.error("Invalid username or password")
    st.stop()

# Initialize Services
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
st.sidebar.write(f"Logged in as: **{st.session_state.user.username}**")
if st.sidebar.button("Logout"):
    st.session_state.authenticated = False
    st.session_state.user = None
    st.rerun()

st.sidebar.divider()
app_mode = st.sidebar.radio("Choose Module", ["Interactive Table", "Data Quality", "Dashboard Builder", "Dataset Comparison", "Upload Data"])

# Data Loading
def load_all_datasets():
    plugins = registry.load_plugins()
    return registry.load_dataframes(plugins)

all_dfs = load_all_datasets()
dataset_options = list(all_dfs.keys())

# --- MODULE 0: INTERACTIVE TABLE ---
if app_mode == "Interactive Table":
    st.title("📂 Interactive Table Explorer")
    selected_ds = st.selectbox("Select Dataset", dataset_options)
    df = all_dfs[selected_ds]

    # Filters Section
    with st.expander("🔍 Table Filters & Search", expanded=True):
        f_col1, f_col2, f_col3 = st.columns([2, 1, 1])
        
        # Text Search
        search_query = f_col1.text_input("Global Search (any column)", "")
        
        # Categorical Filter
        filter_col = f_col2.selectbox("Filter by Column", [None] + list(df.columns))
        filter_val = None
        if filter_col:
            unique_vals = df[filter_col].dropna().unique()
            filter_val = f_col3.selectbox(f"Value for {filter_col}", [None] + list(unique_vals))

    # Apply Filtering
    filtered_df = df.copy()
    if search_query:
        # Search across all string columns
        mask = filtered_df.astype(str).apply(lambda x: x.str.contains(search_query, case=False)).any(axis=1)
        filtered_df = filtered_df[mask]
    
    if filter_col and filter_val:
        filtered_df = filtered_df[filtered_df[filter_col] == filter_val]

    # Table Display
    st.write(f"Showing {len(filtered_df)} of {len(df)} rows")
    st.dataframe(filtered_df, use_container_width=True, height=600)

# --- MODULE 1: DATA QUALITY ---
elif app_mode == "Data Quality":
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
        new_widget = {
            "dataset": selected_ds,
            "type": chart_type,
            "x": x_axis,
            "y": y_axis
        }
        # Save to DB
        widget_id = auth_service.add_user_widget(st.session_state.user.username, new_widget)
        new_widget["id"] = widget_id
        st.session_state.widgets.append(new_widget)
        st.rerun()

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
                    
                    if st.button(f"Remove Widget {i}", key=f"del_{widget['id']}"):
                        auth_service.remove_user_widget(widget['id'], st.session_state.user.username)
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

# --- MODULE 4: UPLOAD DATA ---
elif app_mode == "Upload Data":
    st.title("📤 Upload New Dataset")
    st.write("Upload a CSV file to add it to the platform. Once uploaded, it will be available in all modules.")
    
    with st.form("upload_form"):
        new_dataset_label = st.text_input("Dataset Label (e.g. Sales 2024)", "")
        uploaded_file = st.file_uploader("Choose a CSV file", type="csv")
        
        col_sep, col_enc = st.columns(2)
        delimiter = col_sep.selectbox("CSV Delimiter", [",", ";", "\\t", "|"], help="Select the character that separates columns in your file.")
        # Handle tab specifically
        actual_sep = "\t" if delimiter == "\\t" else delimiter
        
        submit_upload = st.form_submit_button("Upload and Register", use_container_width=True)
        
        if submit_upload:
            if not new_dataset_label or not uploaded_file:
                st.error("Please provide both a label and a file.")
            else:
                # Create a simple key from label
                new_key = re.sub(r'[^a-zA-Z0-9_]', '', new_dataset_label.lower().replace(" ", "_"))
                
                success = registry.register_new_dataset(
                    key=new_key,
                    label=new_dataset_label,
                    csv_content=uploaded_file.getvalue(),
                    read_csv_options={"sep": actual_sep}
                )
                
                if success:
                    st.success(f"Dataset '{new_dataset_label}' uploaded successfully!")
                    st.info("The application will refresh to load the new data.")
                    st.cache_data.clear() # Clear cache to force reload
                    st.rerun()
                else:
                    st.error("Failed to register dataset. The key might already exist.")

# Footer
st.sidebar.divider()
st.sidebar.caption("© 2026 Analytical Platform Pro v2.0")

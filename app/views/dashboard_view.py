from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import pandas as pd

from app.models.state import FilterState, SortSpec
from app.widgets.detail_panel import DetailPanel
from app.widgets.filter_panel import FilterPanel
from app.widgets.interactive_table import InteractiveTable
from app.widgets.tooltip import ToolTip


class DashboardView:
    def __init__(self, callbacks: dict[str, callable]) -> None:
        self._callbacks = callbacks
        self.root = tk.Tk()
        self.root.title("Data Analysis Dashboard")
        self.root.geometry("1280x820")
        self.root.minsize(1180, 760)

        self._overview_title = tk.StringVar(value="Overview")
        self._overview_body = tk.StringVar(value="Select a dataset to view insights.")
        self._breadcrumb = tk.StringVar(value="Dashboard")
        self._chart_canvas: FigureCanvasTkAgg | None = None
        self._artists_to_filter: dict[object, tuple[str, str]] = {}

        self._build_ui()

    def _build_ui(self) -> None:
        container = ttk.Frame(self.root)
        container.pack(fill="both", expand=True, padx=10, pady=8)

        top_bar = ttk.Frame(container)
        top_bar.pack(fill="x", pady=(0, 8))

        btn_fifa = ttk.Button(top_bar, text="FIFA", command=lambda: self._callbacks["dataset"]("fifa"))
        btn_movie = ttk.Button(top_bar, text="Movies", command=lambda: self._callbacks["dataset"]("movie"))
        btn_social = ttk.Button(top_bar, text="Social", command=lambda: self._callbacks["dataset"]("social"))
        btn_back = ttk.Button(top_bar, text="Back", command=self._callbacks["back"])
        btn_report = ttk.Button(top_bar, text="Generate & Open Sweetviz Report", command=self._callbacks["report"])

        btn_fifa.pack(side="left", padx=4)
        btn_movie.pack(side="left", padx=4)
        btn_social.pack(side="left", padx=4)
        btn_back.pack(side="left", padx=8)
        btn_report.pack(side="right", padx=4)

        ToolTip(btn_fifa, "Switch to FIFA dataset")
        ToolTip(btn_movie, "Switch to Movie dataset")
        ToolTip(btn_social, "Switch to Social dataset")
        ToolTip(btn_report, "Generate Sweetviz report for current dataset")

        ttk.Label(container, textvariable=self._breadcrumb, font=("Segoe UI", 9)).pack(fill="x", pady=(0, 6))

        self._notebook = ttk.Notebook(container)
        self._notebook.pack(fill="both", expand=True)
        self._notebook.bind("<<NotebookTabChanged>>", self._on_tab_changed)

        self._dashboard_tab = ttk.Frame(self._notebook)
        self._table_tab = ttk.Frame(self._notebook)
        self._details_tab = ttk.Frame(self._notebook)

        self._notebook.add(self._dashboard_tab, text="Dashboard")
        self._notebook.add(self._table_tab, text="Table")
        self._notebook.add(self._details_tab, text="Details")

        self._build_dashboard_tab()
        self._build_table_tab()
        self._build_details_tab()

        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

    def _build_dashboard_tab(self) -> None:
        frame = ttk.Frame(self._dashboard_tab, padding=10)
        frame.pack(fill="both", expand=True)

        ttk.Label(frame, textvariable=self._overview_title, font=("Segoe UI", 14, "bold")).pack(anchor="w")
        ttk.Label(frame, textvariable=self._overview_body, justify="left").pack(anchor="w", pady=(4, 10))

        self._chart_host = ttk.Frame(frame)
        self._chart_host.pack(fill="both", expand=True)

    def _build_table_tab(self) -> None:
        paned = ttk.Panedwindow(self._table_tab, orient="horizontal")
        paned.pack(fill="both", expand=True, padx=8, pady=8)

        left = ttk.Frame(paned, width=280)
        center = ttk.Frame(paned)

        paned.add(left, weight=1)
        paned.add(center, weight=4)

        self.filter_panel = FilterPanel(left, on_change=self._emit_filters_changed)
        self.filter_panel.pack(fill="both", expand=True, padx=8, pady=8)
        self.filter_panel.bind_categorical_value_updater(self._callbacks["filter_column_changed"])

        self.table_widget = InteractiveTable(
            center,
            on_row_selected=self._callbacks["row_selected"],
            on_sort_changed=self._on_sort_changed,
            on_visible_columns_changed=self._callbacks["columns_changed"],
        )
        self.table_widget.pack(fill="both", expand=True, padx=8, pady=8)

    def _build_details_tab(self) -> None:
        self.detail_panel = DetailPanel(self._details_tab)
        self.detail_panel.pack(fill="both", expand=True, padx=8, pady=8)

    def set_window_geometry(self, geometry: str) -> None:
        if geometry:
            self.root.geometry(geometry)

    def set_overview(self, text: str, key: str) -> None:
        self._overview_title.set(f"{key.title()} Dashboard Overview")
        self._overview_body.set(text)

    def render_charts(self, key: str, df: pd.DataFrame) -> None:
        self._artists_to_filter = {}
        fig = Figure(figsize=(12.8, 5.6), dpi=100)
        ax1 = fig.add_subplot(1, 2, 1)
        ax2 = fig.add_subplot(1, 2, 2)

        if key == "fifa":
            confed = df.get("confederation", pd.Series(dtype=str)).dropna().astype(str).value_counts().head(8)
            if not confed.empty:
                wedges, _ = ax1.pie(confed.values, labels=confed.index, startangle=110)
                for wedge, label in zip(wedges, confed.index):
                    wedge.set_picker(True)
                    self._artists_to_filter[wedge] = ("confederation", str(label))
            ax1.set_title("Confederation Distribution")

            if {"country", "rating_avg"}.issubset(df.columns):
                top = df[["country", "rating_avg"]].copy()
                top["rating_avg"] = pd.to_numeric(top["rating_avg"], errors="coerce")
                top = top.dropna().sort_values("rating_avg", ascending=False).head(10)
                bars = ax2.bar(top["country"], top["rating_avg"], color="#0f766e")
                ax2.tick_params(axis="x", labelrotation=35)
                for bar, country in zip(bars, top["country"]):
                    bar.set_picker(True)
                    self._artists_to_filter[bar] = ("country", str(country))
            ax2.set_title("Top 10 Countries by Average Rating")

        elif key == "movie":
            langs = df.get("Original_Language", pd.Series(dtype=str)).dropna().astype(str).value_counts().head(8)
            if not langs.empty:
                wedges, _ = ax1.pie(langs.values, labels=langs.index, startangle=120)
                for wedge, label in zip(wedges, langs.index):
                    wedge.set_picker(True)
                    self._artists_to_filter[wedge] = ("Original_Language", str(label))
            ax1.set_title("Language Distribution")

            genre_counts: dict[str, int] = {}
            if "Genre" in df.columns:
                for value in df["Genre"].dropna().astype(str):
                    for genre in value.split(","):
                        clean = genre.strip()
                        if clean:
                            genre_counts[clean] = genre_counts.get(clean, 0) + 1
            top_genres = pd.Series(genre_counts).sort_values(ascending=False).head(10) if genre_counts else pd.Series(dtype=int)
            if not top_genres.empty:
                bars = ax2.bar(top_genres.index, top_genres.values, color="#1d4ed8")
                ax2.tick_params(axis="x", labelrotation=35)
                for bar, genre in zip(bars, top_genres.index):
                    bar.set_picker(True)
                    self._artists_to_filter[bar] = ("Genre", str(genre))
            ax2.set_title("Top 10 Genres")

        else:
            scores = pd.to_numeric(df.get("addiction_score", pd.Series(dtype=float)), errors="coerce")
            tiers = pd.cut(scores, bins=[-1, 55, 60, 65, 100], labels=["Low", "Moderate", "High", "Critical"], include_lowest=True)
            tier_counts = tiers.value_counts().sort_index()
            if not tier_counts.empty:
                wedges, _ = ax1.pie(tier_counts.values, labels=tier_counts.index, startangle=110)
                for wedge, label in zip(wedges, tier_counts.index):
                    wedge.set_picker(True)
                    self._artists_to_filter[wedge] = ("risk_tier", str(label))
            ax1.set_title("Addiction Risk Tiers")

            if {"country", "addiction_score"}.issubset(df.columns):
                top = df[["country", "addiction_score"]].copy()
                top["addiction_score"] = pd.to_numeric(top["addiction_score"], errors="coerce")
                top = top.dropna().sort_values("addiction_score", ascending=False).head(10)
                bars = ax2.bar(top["country"], top["addiction_score"], color="#dc2626")
                ax2.tick_params(axis="x", labelrotation=35)
                for bar, country in zip(bars, top["country"]):
                    bar.set_picker(True)
                    self._artists_to_filter[bar] = ("country", str(country))
            ax2.set_title("Top 10 Countries by Addiction Score")

        fig.tight_layout(pad=2.2)
        self._draw_figure(fig)

    def _draw_figure(self, figure: Figure) -> None:
        if self._chart_canvas is not None:
            self._chart_canvas.get_tk_widget().destroy()

        self._chart_canvas = FigureCanvasTkAgg(figure, master=self._chart_host)
        self._chart_canvas.mpl_connect("pick_event", self._on_chart_pick)
        self._chart_canvas.draw()
        self._chart_canvas.get_tk_widget().pack(fill="both", expand=True)

    def _on_chart_pick(self, event: object) -> None:
        artist = getattr(event, "artist", None)
        if artist in self._artists_to_filter:
            column, value = self._artists_to_filter[artist]
            self._callbacks["chart_clicked"](column, value)

    def set_table(self, df: pd.DataFrame, visible_columns: list[str], sort_specs: list[SortSpec]) -> None:
        self.table_widget.set_table(df, visible_columns=visible_columns, sort_specs=sort_specs)

    def set_filter_options(
        self,
        all_columns: list[str],
        categorical_columns: list[str],
        numeric_columns: list[str],
        categorical_values: list[str],
    ) -> None:
        self.filter_panel.configure_columns(all_columns, categorical_columns, numeric_columns, categorical_values)

    def update_filter_values(self, values: list[str]) -> None:
        self.filter_panel.set_categorical_values(values)

    def set_filter_state(self, state: FilterState) -> None:
        self.filter_panel.set_state(state)

    def show_detail(self, dataset_key: str, row: pd.Series) -> None:
        self.detail_panel.show_record(dataset_key, row)

    def set_breadcrumb(self, text: str) -> None:
        self._breadcrumb.set(text)

    def select_tab(self, tab_name: str) -> None:
        names = {"Dashboard": 0, "Table": 1, "Details": 2}
        if tab_name in names:
            self._notebook.select(names[tab_name])

    def _emit_filters_changed(self) -> None:
        filters = self.filter_panel.get_state()
        self._callbacks["filters_changed"](filters)

    def _on_sort_changed(self, specs: list[SortSpec]) -> None:
        self._callbacks["sorts_changed"](specs)

    def _on_tab_changed(self, _: tk.Event) -> None:
        tab_text = self._notebook.tab(self._notebook.select(), "text")
        self._callbacks["tab_changed"](tab_text)

    def _on_close(self) -> None:
        self._callbacks["close"](self.root.winfo_geometry())
        self.root.destroy()

    def run(self) -> None:
        self.root.mainloop()

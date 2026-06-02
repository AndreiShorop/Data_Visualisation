from __future__ import annotations

import tkinter as tk
from tkinter import ttk

import pandas as pd

from app.models.state import WidgetConfig


WIDGET_CATALOG: list[tuple[str, str]] = [
    ("kpi_rows", "Rows KPI"),
    ("kpi_columns", "Columns KPI"),
    ("kpi_missing", "Missing Values KPI"),
    ("table_preview", "Table Preview"),
]


class DashboardWidgetsPanel(ttk.Frame):
    def __init__(self, parent: tk.Widget, callbacks: dict[str, callable]) -> None:
        super().__init__(parent)
        self._callbacks = callbacks
        self._widgets: list[WidgetConfig] = []

        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        controls = ttk.Frame(self)
        controls.grid(row=0, column=0, sticky="ew", pady=(0, 8))

        ttk.Label(controls, text="Widget catalog").pack(side="left")
        self._catalog = ttk.Combobox(controls, state="readonly", values=[label for _, label in WIDGET_CATALOG], width=24)
        self._catalog.pack(side="left", padx=6)
        if WIDGET_CATALOG:
            self._catalog.current(0)

        ttk.Button(controls, text="Add Widget", command=self._add_widget).pack(side="left", padx=4)

        self._body = ttk.Frame(self)
        self._body.grid(row=1, column=0, sticky="nsew")
        self._body.columnconfigure(0, weight=1)

    def set_widgets(self, widgets: list[WidgetConfig], df: pd.DataFrame) -> None:
        self._widgets = list(widgets)
        for child in self._body.winfo_children():
            child.destroy()

        ordered = sorted(self._widgets, key=lambda w: (not w.pinned, self._widgets.index(w)))
        for idx, widget in enumerate(ordered):
            if not widget.visible:
                continue
            self._render_widget(idx, widget, df)

    def _render_widget(self, idx: int, config: WidgetConfig, df: pd.DataFrame) -> None:
        frame = ttk.LabelFrame(self._body, text=config.title)
        frame.grid(row=idx, column=0, sticky="ew", pady=4)
        frame.columnconfigure(0, weight=1)

        actions = ttk.Frame(frame)
        actions.grid(row=0, column=0, sticky="ew", padx=6, pady=(4, 2))

        ttk.Button(actions, text="↑", width=3, command=lambda wid=config.widget_id: self._callbacks["move"](wid, -1)).pack(side="left", padx=2)
        ttk.Button(actions, text="↓", width=3, command=lambda wid=config.widget_id: self._callbacks["move"](wid, 1)).pack(side="left", padx=2)
        ttk.Button(actions, text="Pin" if not config.pinned else "Unpin", command=lambda wid=config.widget_id: self._callbacks["pin"](wid)).pack(side="left", padx=2)
        ttk.Button(actions, text="Resize", command=lambda wid=config.widget_id: self._callbacks["resize"](wid)).pack(side="left", padx=2)
        ttk.Button(actions, text="Remove", command=lambda wid=config.widget_id: self._callbacks["remove"](wid)).pack(side="right", padx=2)

        content = ttk.Frame(frame)
        content.grid(row=1, column=0, sticky="ew", padx=8, pady=(0, 8))
        content.columnconfigure(0, weight=1)

        if config.widget_type == "kpi_rows":
            ttk.Label(content, text=f"Rows: {len(df):,}", font=("Segoe UI", 12, "bold")).grid(row=0, column=0, sticky="w")
        elif config.widget_type == "kpi_columns":
            ttk.Label(content, text=f"Columns: {df.shape[1]}", font=("Segoe UI", 12, "bold")).grid(row=0, column=0, sticky="w")
        elif config.widget_type == "kpi_missing":
            missing = int(df.isna().sum().sum()) if not df.empty else 0
            ttk.Label(content, text=f"Missing values: {missing:,}", font=("Segoe UI", 12, "bold")).grid(row=0, column=0, sticky="w")
        elif config.widget_type == "table_preview":
            preview = df.head(5)
            text = tk.Text(content, height=self._height_for_size(config.size), wrap="none")
            text.grid(row=0, column=0, sticky="ew")
            text.insert("1.0", preview.to_string(index=False) if not preview.empty else "No data")
            text.configure(state="disabled")
        else:
            ttk.Label(content, text="Unknown widget type").grid(row=0, column=0, sticky="w")

    def _height_for_size(self, size: str) -> int:
        if size == "small":
            return 4
        if size == "large":
            return 12
        return 8

    def _add_widget(self) -> None:
        selected_idx = self._catalog.current()
        if selected_idx < 0:
            return
        widget_type, default_title = WIDGET_CATALOG[selected_idx]
        self._callbacks["add"](widget_type, default_title)

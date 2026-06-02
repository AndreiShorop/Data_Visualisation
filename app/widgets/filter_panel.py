from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from app.models.state import FilterState


class FilterPanel(ttk.Frame):
    def __init__(self, parent: tk.Widget, on_change: callable) -> None:
        super().__init__(parent)
        self._on_change = on_change

        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)

        self.text_var = tk.StringVar()
        self.cat_col_var = tk.StringVar()
        self.cat_val_var = tk.StringVar()
        self.num_col_var = tk.StringVar()
        self.min_var = tk.StringVar()
        self.max_var = tk.StringVar()

        ttk.Label(self, text="Filters", font=("Segoe UI", 10, "bold")).grid(row=0, column=0, columnspan=2, sticky="w", pady=(4, 8))

        ttk.Label(self, text="Text search").grid(row=1, column=0, sticky="w")
        text_entry = ttk.Entry(self, textvariable=self.text_var)
        text_entry.grid(row=1, column=1, sticky="ew", padx=(6, 0))

        ttk.Label(self, text="Dropdown column").grid(row=2, column=0, sticky="w", pady=(6, 0))
        self.cat_col = ttk.Combobox(self, textvariable=self.cat_col_var, state="readonly")
        self.cat_col.grid(row=2, column=1, sticky="ew", padx=(6, 0), pady=(6, 0))

        ttk.Label(self, text="Dropdown value").grid(row=3, column=0, sticky="w", pady=(6, 0))
        self.cat_val = ttk.Combobox(self, textvariable=self.cat_val_var, state="readonly")
        self.cat_val.grid(row=3, column=1, sticky="ew", padx=(6, 0), pady=(6, 0))

        ttk.Label(self, text="Numeric column").grid(row=4, column=0, sticky="w", pady=(6, 0))
        self.num_col = ttk.Combobox(self, textvariable=self.num_col_var, state="readonly")
        self.num_col.grid(row=4, column=1, sticky="ew", padx=(6, 0), pady=(6, 0))

        ttk.Label(self, text="Min").grid(row=5, column=0, sticky="w", pady=(6, 0))
        ttk.Entry(self, textvariable=self.min_var).grid(row=5, column=1, sticky="ew", padx=(6, 0), pady=(6, 0))

        ttk.Label(self, text="Max").grid(row=6, column=0, sticky="w", pady=(6, 0))
        ttk.Entry(self, textvariable=self.max_var).grid(row=6, column=1, sticky="ew", padx=(6, 0), pady=(6, 0))

        controls = [text_entry, self.cat_col, self.cat_val, self.num_col]
        for control in controls:
            control.bind("<<ComboboxSelected>>", self._notify)
            control.bind("<KeyRelease>", self._notify)

    def configure_columns(self, all_columns: list[str], categorical_columns: list[str], numeric_columns: list[str], categorical_values: list[str]) -> None:
        self.cat_col["values"] = [""] + categorical_columns
        self.cat_val["values"] = [""] + categorical_values
        self.num_col["values"] = [""] + numeric_columns

    def bind_categorical_value_updater(self, callback: callable) -> None:
        self.cat_col.bind("<<ComboboxSelected>>", lambda _: callback(self.cat_col_var.get()))

    def set_categorical_values(self, values: list[str]) -> None:
        current = self.cat_val_var.get()
        self.cat_val["values"] = [""] + values
        if current not in values:
            self.cat_val_var.set("")

    def get_state(self) -> FilterState:
        return FilterState(
            text_query=self.text_var.get(),
            categorical_column=self.cat_col_var.get(),
            categorical_value=self.cat_val_var.get(),
            numeric_column=self.num_col_var.get(),
            min_value=self.min_var.get(),
            max_value=self.max_var.get(),
        )

    def set_state(self, state: FilterState) -> None:
        self.text_var.set(state.text_query)
        self.cat_col_var.set(state.categorical_column)
        self.cat_val_var.set(state.categorical_value)
        self.num_col_var.set(state.numeric_column)
        self.min_var.set(state.min_value)
        self.max_var.set(state.max_value)

    def _notify(self, _: tk.Event) -> None:
        self._on_change()

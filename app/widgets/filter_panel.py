from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from app.models.state import FilterState


class FilterPanel(ttk.Frame):
    def __init__(self, parent: tk.Widget, on_change: callable) -> None:
        super().__init__(parent)
        self._on_change = on_change
        self._multi_values: list[str] = []

        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)

        self.text_var = tk.StringVar()
        self.cat_col_var = tk.StringVar()
        self.cat_val_var = tk.StringVar()
        self.multi_col_var = tk.StringVar()
        self.num_col_var = tk.StringVar()
        self.min_var = tk.StringVar()
        self.max_var = tk.StringVar()
        self.date_col_var = tk.StringVar()
        self.start_date_var = tk.StringVar()
        self.end_date_var = tk.StringVar()

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

        ttk.Label(self, text="Multi-select column").grid(row=4, column=0, sticky="w", pady=(6, 0))
        self.multi_col = ttk.Combobox(self, textvariable=self.multi_col_var, state="readonly")
        self.multi_col.grid(row=4, column=1, sticky="ew", padx=(6, 0), pady=(6, 0))

        ttk.Label(self, text="Multi-select values").grid(row=5, column=0, sticky="nw", pady=(6, 0))
        multi_host = ttk.Frame(self)
        multi_host.grid(row=5, column=1, sticky="nsew", padx=(6, 0), pady=(6, 0))
        multi_host.columnconfigure(0, weight=1)
        multi_host.rowconfigure(0, weight=1)

        self.multi_list = tk.Listbox(multi_host, selectmode=tk.MULTIPLE, exportselection=False, height=4)
        self.multi_list.grid(row=0, column=0, sticky="nsew")
        multi_scroll = ttk.Scrollbar(multi_host, orient="vertical", command=self.multi_list.yview)
        multi_scroll.grid(row=0, column=1, sticky="ns")
        self.multi_list.configure(yscrollcommand=multi_scroll.set)
        self.multi_list.bind("<<ListboxSelect>>", self._notify)

        ttk.Label(self, text="Numeric column").grid(row=6, column=0, sticky="w", pady=(6, 0))
        self.num_col = ttk.Combobox(self, textvariable=self.num_col_var, state="readonly")
        self.num_col.grid(row=6, column=1, sticky="ew", padx=(6, 0), pady=(6, 0))

        ttk.Label(self, text="Min").grid(row=7, column=0, sticky="w", pady=(6, 0))
        min_entry = ttk.Entry(self, textvariable=self.min_var)
        min_entry.grid(row=7, column=1, sticky="ew", padx=(6, 0), pady=(6, 0))

        ttk.Label(self, text="Max").grid(row=8, column=0, sticky="w", pady=(6, 0))
        max_entry = ttk.Entry(self, textvariable=self.max_var)
        max_entry.grid(row=8, column=1, sticky="ew", padx=(6, 0), pady=(6, 0))

        ttk.Label(self, text="Date column").grid(row=9, column=0, sticky="w", pady=(6, 0))
        self.date_col = ttk.Combobox(self, textvariable=self.date_col_var, state="readonly")
        self.date_col.grid(row=9, column=1, sticky="ew", padx=(6, 0), pady=(6, 0))

        ttk.Label(self, text="Start date (YYYY-MM-DD)").grid(row=10, column=0, sticky="w", pady=(6, 0))
        start_entry = ttk.Entry(self, textvariable=self.start_date_var)
        start_entry.grid(row=10, column=1, sticky="ew", padx=(6, 0), pady=(6, 0))

        ttk.Label(self, text="End date (YYYY-MM-DD)").grid(row=11, column=0, sticky="w", pady=(6, 0))
        end_entry = ttk.Entry(self, textvariable=self.end_date_var)
        end_entry.grid(row=11, column=1, sticky="ew", padx=(6, 0), pady=(6, 0))

        controls = [text_entry, self.cat_col, self.cat_val, self.multi_col, self.num_col, self.date_col, min_entry, max_entry, start_entry, end_entry]
        for control in controls:
            control.bind("<<ComboboxSelected>>", self._notify)
            control.bind("<KeyRelease>", self._notify)

    def configure_columns(
        self,
        all_columns: list[str],
        categorical_columns: list[str],
        numeric_columns: list[str],
        date_columns: list[str],
        multi_columns: list[str],
        categorical_values: list[str],
        multi_values: list[str],
    ) -> None:
        self.cat_col["values"] = [""] + categorical_columns
        self.cat_val["values"] = [""] + categorical_values
        self.multi_col["values"] = [""] + multi_columns
        self.num_col["values"] = [""] + numeric_columns
        self.date_col["values"] = [""] + date_columns
        self.set_multi_values(multi_values)

    def bind_categorical_value_updater(self, callback: callable) -> None:
        self.cat_col.bind("<<ComboboxSelected>>", lambda _: callback(self.cat_col_var.get()))

    def bind_multi_value_updater(self, callback: callable) -> None:
        self.multi_col.bind("<<ComboboxSelected>>", lambda _: callback(self.multi_col_var.get()))

    def set_categorical_values(self, values: list[str]) -> None:
        current = self.cat_val_var.get()
        self.cat_val["values"] = [""] + values
        if current not in values:
            self.cat_val_var.set("")

    def set_multi_values(self, values: list[str]) -> None:
        self._multi_values = list(values)
        self.multi_list.delete(0, tk.END)
        for value in self._multi_values:
            self.multi_list.insert(tk.END, value)

    def get_state(self) -> FilterState:
        selected_values = [self._multi_values[idx] for idx in self.multi_list.curselection() if idx < len(self._multi_values)]
        return FilterState(
            text_query=self.text_var.get(),
            categorical_column=self.cat_col_var.get(),
            categorical_value=self.cat_val_var.get(),
            multi_select_column=self.multi_col_var.get(),
            multi_select_values=selected_values,
            numeric_column=self.num_col_var.get(),
            min_value=self.min_var.get(),
            max_value=self.max_var.get(),
            date_column=self.date_col_var.get(),
            start_date=self.start_date_var.get(),
            end_date=self.end_date_var.get(),
        )

    def set_state(self, state: FilterState) -> None:
        self.text_var.set(state.text_query)
        self.cat_col_var.set(state.categorical_column)
        self.cat_val_var.set(state.categorical_value)
        self.multi_col_var.set(state.multi_select_column)
        self.num_col_var.set(state.numeric_column)
        self.min_var.set(state.min_value)
        self.max_var.set(state.max_value)
        self.date_col_var.set(state.date_column)
        self.start_date_var.set(state.start_date)
        self.end_date_var.set(state.end_date)

        self.multi_list.selection_clear(0, tk.END)
        selected = set(state.multi_select_values)
        for idx, value in enumerate(self._multi_values):
            if value in selected:
                self.multi_list.selection_set(idx)

    def _notify(self, _: tk.Event) -> None:
        self._on_change()

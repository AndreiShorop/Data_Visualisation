from __future__ import annotations

import tkinter as tk
from tkinter import ttk

import pandas as pd


class DetailPanel(ttk.Frame):
    def __init__(self, parent: tk.Widget) -> None:
        super().__init__(parent)
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        self._title_var = tk.StringVar(value="Record Details")
        ttk.Label(self, textvariable=self._title_var, font=("Segoe UI", 11, "bold")).grid(row=0, column=0, sticky="ew", padx=8, pady=(8, 4))

        self._tree = ttk.Treeview(self, columns=("field", "value"), show="headings", height=10)
        self._tree.heading("field", text="Field")
        self._tree.heading("value", text="Value")
        self._tree.column("field", width=180, anchor="w")
        self._tree.column("value", width=440, anchor="w")
        self._tree.grid(row=1, column=0, sticky="nsew", padx=8, pady=(0, 8))

        scrollbar = ttk.Scrollbar(self, orient="vertical", command=self._tree.yview)
        self._tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.grid(row=1, column=1, sticky="ns", pady=(0, 8))

    def show_record(self, dataset_key: str, row: pd.Series) -> None:
        self._title_var.set(f"Record Details - {dataset_key.title()}")
        for item in self._tree.get_children(""):
            self._tree.delete(item)

        for field, value in row.to_dict().items():
            self._tree.insert("", "end", values=(field, str(value)))

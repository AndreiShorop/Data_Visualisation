from __future__ import annotations

import tkinter as tk
from tkinter import ttk

import pandas as pd

from app.models.state import SortSpec


class InteractiveTable(ttk.Frame):
    def __init__(
        self,
        parent: tk.Widget,
        on_row_selected: callable,
        on_sort_changed: callable,
        on_visible_columns_changed: callable,
    ) -> None:
        super().__init__(parent)
        self._on_row_selected = on_row_selected
        self._on_sort_changed = on_sort_changed
        self._on_visible_columns_changed = on_visible_columns_changed
        self._data = pd.DataFrame()
        self._all_columns: list[str] = []
        self._visible_columns: list[str] = []
        self._sort_specs: list[SortSpec] = []

        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        toolbar = ttk.Frame(self)
        toolbar.grid(row=0, column=0, sticky="ew", pady=(0, 6))

        ttk.Button(toolbar, text="Columns", command=self._open_column_chooser).pack(side="left")
        ttk.Label(toolbar, text="Tip: Shift+Click column headers for multi-sort.").pack(side="left", padx=10)

        self.tree = ttk.Treeview(self, show="headings")
        self.tree.grid(row=1, column=0, sticky="nsew")

        yscroll = ttk.Scrollbar(self, orient="vertical", command=self.tree.yview)
        xscroll = ttk.Scrollbar(self, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=yscroll.set, xscrollcommand=xscroll.set)
        yscroll.grid(row=1, column=1, sticky="ns")
        xscroll.grid(row=2, column=0, sticky="ew")

        self.tree.bind("<<TreeviewSelect>>", self._handle_row_select)
        self.tree.bind("<Button-3>", self._open_context_menu)

        self._menu = tk.Menu(self, tearoff=0)
        self._menu.add_command(label="Open details", command=self._open_selected_details)

    @property
    def visible_columns(self) -> list[str]:
        return self._visible_columns

    @property
    def sort_specs(self) -> list[SortSpec]:
        return self._sort_specs

    def set_table(self, df: pd.DataFrame, visible_columns: list[str] | None = None, sort_specs: list[SortSpec] | None = None) -> None:
        self._data = df.copy()
        self._all_columns = [str(col) for col in df.columns]
        if visible_columns:
            self._visible_columns = [c for c in visible_columns if c in self._all_columns]
        if not self._visible_columns:
            self._visible_columns = list(self._all_columns)

        self._sort_specs = [s for s in (sort_specs or []) if s.column in self._all_columns]
        self._rebuild_tree()

    def _rebuild_tree(self) -> None:
        self.tree.delete(*self.tree.get_children(""))
        self.tree["columns"] = tuple(self._visible_columns)

        for column in self._visible_columns:
            self.tree.heading(column, text=self._heading_text(column), command=lambda c=column: self._toggle_sort(c))
            self.tree.column(column, width=150, minwidth=80, anchor="w", stretch=True)

        for row_index, row in self._data.iterrows():
            values = [str(row[column]) for column in self._visible_columns]
            self.tree.insert("", "end", iid=str(row_index), values=values)

    def _heading_text(self, column: str) -> str:
        index = next((i for i, spec in enumerate(self._sort_specs) if spec.column == column), None)
        if index is None:
            return column
        direction = "ASC" if self._sort_specs[index].ascending else "DESC"
        if len(self._sort_specs) == 1:
            return f"{column} ({direction})"
        return f"{column} ({index + 1}:{direction})"

    def _toggle_sort(self, column: str) -> None:
        existing = next((spec for spec in self._sort_specs if spec.column == column), None)

        if existing is None:
            self._sort_specs = [SortSpec(column=column, ascending=True)] + [spec for spec in self._sort_specs if spec.column != column]
            self._sort_specs = self._sort_specs[:3]
        else:
            existing.ascending = not existing.ascending

        self._on_sort_changed(self._sort_specs)

    def _handle_row_select(self, _: tk.Event) -> None:
        selected = self.tree.selection()
        if not selected:
            return

        row_id = selected[0]
        if row_id.isdigit():
            row = self._data.loc[int(row_id)]
        else:
            row = self._data.loc[row_id]
        self._on_row_selected(row)

    def _open_context_menu(self, event: tk.Event) -> None:
        row_id = self.tree.identify_row(event.y)
        if row_id:
            self.tree.selection_set(row_id)
            self._menu.tk_popup(event.x_root, event.y_root)

    def _open_selected_details(self) -> None:
        selected = self.tree.selection()
        if not selected:
            return
        row_id = selected[0]
        if row_id.isdigit():
            row = self._data.loc[int(row_id)]
        else:
            row = self._data.loc[row_id]
        self._on_row_selected(row)

    def _open_column_chooser(self) -> None:
        dialog = tk.Toplevel(self)
        dialog.title("Select Columns")
        dialog.transient(self.winfo_toplevel())
        dialog.grab_set()

        vars_by_column: dict[str, tk.BooleanVar] = {}
        for idx, column in enumerate(self._all_columns):
            var = tk.BooleanVar(value=column in self._visible_columns)
            vars_by_column[column] = var
            ttk.Checkbutton(dialog, text=column, variable=var).grid(row=idx, column=0, sticky="w", padx=10, pady=2)

        controls = ttk.Frame(dialog)
        controls.grid(row=len(self._all_columns) + 1, column=0, sticky="ew", padx=10, pady=10)

        def apply_changes() -> None:
            selected = [column for column in self._all_columns if vars_by_column[column].get()]
            if selected:
                self._visible_columns = selected
                self._rebuild_tree()
                self._on_visible_columns_changed(self._visible_columns)
            dialog.destroy()

        ttk.Button(controls, text="Apply", command=apply_changes).pack(side="left")
        ttk.Button(controls, text="Cancel", command=dialog.destroy).pack(side="left", padx=8)

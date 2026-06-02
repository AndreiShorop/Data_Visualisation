from __future__ import annotations

import tkinter as tk


class ToolTip:
    def __init__(self, widget: tk.Widget, text: str) -> None:
        self._widget = widget
        self._text = text
        self._tip: tk.Toplevel | None = None

        self._widget.bind("<Enter>", self._on_enter)
        self._widget.bind("<Leave>", self._on_leave)

    def _on_enter(self, _: tk.Event) -> None:
        if self._tip is not None:
            return

        x = self._widget.winfo_rootx() + 16
        y = self._widget.winfo_rooty() + 22

        self._tip = tk.Toplevel(self._widget)
        self._tip.wm_overrideredirect(True)
        self._tip.wm_geometry(f"+{x}+{y}")

        label = tk.Label(
            self._tip,
            text=self._text,
            background="#111827",
            foreground="#f9fafb",
            relief="solid",
            borderwidth=1,
            padx=8,
            pady=4,
        )
        label.pack()

    def _on_leave(self, _: tk.Event) -> None:
        if self._tip is not None:
            self._tip.destroy()
            self._tip = None

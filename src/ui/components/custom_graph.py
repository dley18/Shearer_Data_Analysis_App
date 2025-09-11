"""Custom graph component to show a listbox of IO points for selection."""

from typing import Callable

import customtkinter as ctk


from src.config.point_mapping import IO_POINTS, VFD_POINTS
from src.config.ui_config import UI_PADDING, UI_COLORS


class CustomGraph(ctk.CTkFrame):
    """Custom graph selection component."""

    def __init__(self, parent: ctk.CTkFrame, **kwargs):
        super().__init__(parent, **kwargs)
        self.io_state = {}
        self.vfd_state = {}
        self.callbacks = {}
        self.checkboxes = []

        self.setup_component()

    def setup_component(self) -> None:
        """Initialize component and fill with IO points."""

        component_listbox = ctk.CTkScrollableFrame(self)
        component_listbox.pack(fill="both", expand=True, padx=10, pady=10)

        # Configure grid columns to expand equally
        component_listbox.grid_columnconfigure(0, weight=1)
        component_listbox.grid_columnconfigure(1, weight=1)

        row = 0
        col = 0

        # Populate frame with IO points
        for key, value in IO_POINTS.items():
            io_point_var = ctk.StringVar(value="off")
            self.io_state[key] = io_point_var
            io_point_checkbox = ctk.CTkCheckBox(
                component_listbox,
                text=value["readable_name"],
                font=ctk.CTkFont(family="Inter", size=14, weight="bold"),
                width=18,
                height=18,
                checkbox_width=16,
                checkbox_height=16,
                variable=io_point_var,
                onvalue="on",
                offvalue="off",
                fg_color=UI_COLORS["checkbox"],
                hover_color=UI_COLORS["checkbox_hover"],
                corner_radius=3,
                border_width=1,
                text_color=UI_COLORS["white"],
            )
            io_point_checkbox.grid(
                row=row,
                column=col,
                padx=UI_PADDING["small"],
                pady=UI_PADDING["small"],
                sticky="ew",  # Expand horizontally to fill column
            )
            self.checkboxes.append(io_point_checkbox)

            # Move to next column, wrap to next row after 3 columns
            col += 1
            if col >= 2:
                col = 0
                row += 1

        # Populate frame with VFD points
        for key, value in VFD_POINTS.items():
            vfd_point_var = ctk.StringVar(value="off")
            self.vfd_state[key] = vfd_point_var
            vfd_point_checkbox = ctk.CTkCheckBox(
                component_listbox,
                text=key,
                font=ctk.CTkFont(family="Inter", size=14, weight="bold"),
                width=18,
                height=18,
                checkbox_width=16,
                checkbox_height=16,
                variable=vfd_point_var,
                onvalue="on",
                offvalue="off",
                fg_color=UI_COLORS["checkbox"],
                hover_color=UI_COLORS["checkbox_hover"],
                corner_radius=3,
                border_width=1,
                text_color=UI_COLORS["white"],
            )
            vfd_point_checkbox.grid(
                row=row,
                column=col,
                padx=UI_PADDING["small"],
                pady=UI_PADDING["small"],
                sticky="ew",  # Expand horizontally to fill column
            )
            self.checkboxes.append(vfd_point_checkbox)

            # Move to next column, wrap to next row after 3 columns
            col += 1
            if col >= 2:
                col = 0
                row += 1

    def clear(self) -> None:
        """Clear all selected checkboxes"""

        count = 0

        for var in self.io_state.values():
            if var.get() == "on":
                count += 1
            var.set("off")
        for var in self.vfd_state.values():
            if var.get() == "on":
                count += 1
            var.set("off")

        if "cleared_custom_points" in self.callbacks:
            self.callbacks["cleared_custom_points"](count)

    def set_callback(self, event_name: str, callback: Callable) -> None:
        """
        Set callback function for events.

        Parameters:
          event_name (str): Event name ('files_added', 'files_removed', 'files_cleared', 'selection_changed')
          callback (Callable): Callback function
        """

        self.callbacks[event_name] = callback

    def disable_checkboxes(self):
        """Disable all checkboxes during processing."""
        for checkbox in self.checkboxes:
            checkbox.configure(state="disabled")

    def enable_checkboxes(self):
        """Enable all checkboxes after processing."""
        for checkbox in self.checkboxes:
            checkbox.configure(state="normal")

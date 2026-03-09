"""Column preferences dialog for Media Archive Manager GUI.

This module provides a dialog for managing column visibility preferences.

History:
20260309  V1.0: Initial column preferences dialog implementation
20260309  V1.1: Fixed dialog height and button frame layout
20260309  V1.2: Fixed button clipping by increasing width and restructuring canvas frame
"""

import logging
import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional, Callable

logger = logging.getLogger(__name__)


class BaseDialog(tk.Toplevel):
    """Base class for all dialog windows.
    
    Provides common functionality for dialog windows including:
    - Modal behavior
    - OK/Cancel buttons
    - Result handling
    """

    def __init__(self, parent: tk.Widget, title: str = "Dialog") -> None:
        """Initialize base dialog.
        
        Args:
            parent: Parent window.
            title: Dialog window title.
        """
        super().__init__(parent)
        self.title(title)
        self.resizable(False, False)
        self.result = None
        
        # Make dialog modal
        self.transient(parent)
        self.grab_set()
        
        logger.debug(f"BaseDialog initialized: {title}")

    def center_on_parent(self) -> None:
        """Center dialog on parent window."""
        self.update_idletasks()
        parent = self.master
        x = parent.winfo_x() + (parent.winfo_width() // 2) - (self.winfo_width() // 2)
        y = parent.winfo_y() + (parent.winfo_height() // 2) - (self.winfo_height() // 2)
        self.geometry(f"+{x}+{y}")

    def show(self) -> Optional[object]:
        """Show dialog and wait for result.
        
        Returns:
            Dialog result or None if cancelled.
        """
        self.center_on_parent()
        self.wait_window()
        return self.result


class ColumnPreferencesDialog(BaseDialog):
    """Dialog for managing column visibility preferences.
    
    Allows users to show/hide columns in the media table and save preferences.
    """

    def __init__(
        self,
        parent: tk.Widget,
        visible_columns: dict,
        on_save: Optional[Callable[[dict], None]] = None,
    ) -> None:
        """Initialize column preferences dialog.
        
        Args:
            parent: Parent window.
            visible_columns: Dictionary of column names to visibility (True/False).
            on_save: Optional callback when preferences are saved.
        """
        super().__init__(parent, "Column Preferences")
        self.visible_columns = visible_columns.copy()
        self.on_save = on_save
        self.result = None
        
        # Create content
        self._create_content()
        
        logger.debug("ColumnPreferencesDialog initialized")

    def _create_content(self) -> None:
        """Create dialog content."""
        # Main frame with padding
        main_frame = ttk.Frame(self, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(
            main_frame,
            text="Select columns to display in Media table",
            font=("TkDefaultFont", 11, "bold")
        )
        title_label.pack(pady=(0, 15))
        
        # Create scrollable frame for checkboxes
        canvas_frame = ttk.Frame(main_frame)
        canvas_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
        
        canvas = tk.Canvas(canvas_frame, highlightthickness=0, height=250)
        scrollbar = ttk.Scrollbar(canvas_frame, orient=tk.VERTICAL, command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Create checkbox variables and widgets
        self.column_vars = {}
        for column_name, is_visible in self.visible_columns.items():
            var = tk.BooleanVar(value=is_visible)
            self.column_vars[column_name] = var
            
            checkbox = ttk.Checkbutton(
                scrollable_frame,
                text=column_name,
                variable=var
            )
            checkbox.pack(anchor=tk.W, pady=5)
        
        # Pack canvas and scrollbar
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Info label
        info_label = ttk.Label(
            main_frame,
            text="Note: At least one column must be visible.",
            font=("TkDefaultFont", 9, "italic"),
            foreground="gray"
        )
        info_label.pack(anchor=tk.W, pady=(0, 10))
        
        # Buttons frame - pack inside main_frame to ensure visibility
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Button(button_frame, text="Save", command=self._save).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Reset to Defaults", command=self._reset_defaults).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=self._cancel).pack(side=tk.LEFT, padx=5)
        
        # Set size - increased width to show all buttons
        self.geometry("550x600")

    def _save(self) -> None:
        """Save column preferences and close dialog."""
        try:
            # Check that at least one column is visible
            visible_count = sum(1 for var in self.column_vars.values() if var.get())
            if visible_count == 0:
                messagebox.showwarning(
                    "Validation Error",
                    "At least one column must be visible"
                )
                return
            
            # Update visible columns
            for column_name, var in self.column_vars.items():
                self.visible_columns[column_name] = var.get()
            
            self.result = self.visible_columns
            
            if self.on_save:
                self.on_save(self.visible_columns)
            
            logger.info(f"Column preferences saved: {self.visible_columns}")
            self.destroy()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save preferences: {e}")
            logger.error(f"Error in ColumnPreferencesDialog._save: {e}")

    def _reset_defaults(self) -> None:
        """Reset all columns to default visibility."""
        try:
            # Default: all columns visible
            for var in self.column_vars.values():
                var.set(True)
            
            logger.debug("Column preferences reset to defaults")
        except Exception as e:
            logger.error(f"Error resetting defaults: {e}")

    def _cancel(self) -> None:
        """Cancel and close dialog."""
        self.result = None
        self.destroy()

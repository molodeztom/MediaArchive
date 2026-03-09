"""Batch edit dialog for Media Archive Manager GUI.

This module provides a dialog for batch editing multiple media items.

History:
20260309  V1.0: Initial batch edit dialog implementation
"""

import logging
import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional, Callable, List
from datetime import date

from models.media import Media
from models.enums import MediaType
from utils.date_utils import format_date, parse_date

logger = logging.getLogger(__name__)


class BaseDialog(tk.Toplevel):
    """Base class for all dialog windows."""

    def __init__(self, parent: tk.Widget, title: str = "Dialog") -> None:
        """Initialize base dialog."""
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
        """Show dialog and wait for result."""
        self.center_on_parent()
        self.wait_window()
        return self.result


class BatchEditDialog(BaseDialog):
    """Dialog for batch editing multiple media items.
    
    Allows users to set common fields for multiple selected media items.
    """

    def __init__(
        self,
        parent: tk.Widget,
        selected_media: List[Media],
        categories: List[str],
        on_save: Optional[Callable[[dict], None]] = None,
    ) -> None:
        """Initialize batch edit dialog.
        
        Args:
            parent: Parent window.
            selected_media: List of selected media items to edit.
            categories: List of existing categories for dropdown.
            on_save: Optional callback when batch edit is saved.
        """
        super().__init__(parent, f"Batch Edit {len(selected_media)} Media Items")
        self.selected_media = selected_media
        self.categories = categories
        self.on_save = on_save
        self.result = None
        
        # Create form
        self._create_form()
        
        logger.debug(f"BatchEditDialog initialized for {len(selected_media)} items")

    def _create_form(self) -> None:
        """Create form fields."""
        # Main frame with padding
        main_frame = ttk.Frame(self, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Info label
        info_label = ttk.Label(
            main_frame,
            text=f"Editing {len(self.selected_media)} media items. Leave fields empty to skip.",
            font=("TkDefaultFont", 9, "italic")
        )
        info_label.grid(row=0, column=0, columnspan=2, sticky=tk.W, pady=(0, 10))
        
        # Media Type field
        ttk.Label(main_frame, text="Media Type").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.media_type_var = tk.StringVar()
        type_combo = ttk.Combobox(
            main_frame,
            textvariable=self.media_type_var,
            values=[""] + MediaType.get_all_values(),
            state="readonly",
            width=37
        )
        type_combo.grid(row=1, column=1, sticky=tk.EW, pady=5)
        
        # Category field
        ttk.Label(main_frame, text="Category").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.category_var = tk.StringVar()
        category_combo = ttk.Combobox(
            main_frame,
            textvariable=self.category_var,
            values=[""] + self.categories,
            state="normal",
            width=37
        )
        category_combo.grid(row=2, column=1, sticky=tk.EW, pady=5)
        
        # Valid Until Date field
        ttk.Label(main_frame, text="Valid Until Date").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.valid_until_var = tk.StringVar()
        valid_until_entry = ttk.Entry(
            main_frame,
            textvariable=self.valid_until_var,
            width=40
        )
        valid_until_entry.grid(row=3, column=1, sticky=tk.EW, pady=5)
        ttk.Label(main_frame, text="(DD.MM.YYYY)", font=("TkDefaultFont", 8)).grid(
            row=3, column=2, sticky=tk.W, padx=5
        )
        
        # Configure grid weights
        main_frame.columnconfigure(1, weight=1)
        
        # Buttons frame
        button_frame = ttk.Frame(self)
        button_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Button(button_frame, text="Apply", command=self._save).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=self._cancel).pack(side=tk.LEFT, padx=5)
        
        # Set minimum size
        self.geometry("450x200")

    def _save(self) -> None:
        """Save batch edit and close dialog."""
        try:
            # Get values
            media_type = self.media_type_var.get().strip() or None
            category = self.category_var.get().strip() or None
            valid_until_str = self.valid_until_var.get().strip() or None
            
            # Parse date if provided
            valid_until_date = None
            if valid_until_str:
                try:
                    valid_until_date = parse_date(valid_until_str)
                except ValueError as e:
                    messagebox.showerror("Date Error", str(e))
                    return
            
            # Create result dictionary with only non-empty fields
            result = {}
            if media_type:
                result["media_type"] = media_type
            if category:
                result["category"] = category
            if valid_until_date:
                result["valid_until_date"] = valid_until_date
            
            # Check if at least one field is set
            if not result:
                messagebox.showwarning("No Changes", "Please set at least one field to update")
                return
            
            self.result = result
            
            if self.on_save:
                self.on_save(result)
            
            logger.info(f"Batch edit applied: {result}")
            self.destroy()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to apply batch edit: {e}")
            logger.error(f"Error in BatchEditDialog._save: {e}")

    def _cancel(self) -> None:
        """Cancel and close dialog."""
        self.result = None
        self.destroy()

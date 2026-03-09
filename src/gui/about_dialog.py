"""About dialog for displaying application information.

This module provides a dialog for showing application name, version,
description, and technology stack information.

History:
20260309  V1.0: Initial about dialog implementation
"""

import logging
import tkinter as tk
from tkinter import ttk

from utils.config import APP_NAME, APP_VERSION

logger = logging.getLogger(__name__)


class AboutDialog:
    """Dialog for displaying application information."""

    def __init__(self, parent: tk.Widget) -> None:
        """Initialize about dialog.
        
        Args:
            parent: Parent window.
        """
        self.parent = parent
        self.result = False
        
        logger.debug("AboutDialog initialized")

    def show(self) -> bool:
        """Show the about dialog.
        
        Returns:
            True if dialog was closed normally, False if cancelled.
        """
        # Create dialog window
        self.dialog = tk.Toplevel(self.parent)
        self.dialog.title("About Media Archive Manager")
        self.dialog.geometry("500x520")
        self.dialog.resizable(False, False)
        
        # Make dialog modal
        self.dialog.transient(self.parent)
        self.dialog.grab_set()
        
        # Create content
        self._create_content()
        
        # Center dialog on parent
        self.dialog.update_idletasks()
        x = self.parent.winfo_x() + (self.parent.winfo_width() // 2) - (self.dialog.winfo_width() // 2)
        y = self.parent.winfo_y() + (self.parent.winfo_height() // 2) - (self.dialog.winfo_height() // 2)
        self.dialog.geometry(f"+{x}+{y}")
        
        # Wait for dialog to close
        self.parent.wait_window(self.dialog)
        
        return self.result

    def _create_content(self) -> None:
        """Create dialog content."""
        # Main frame with padding
        main_frame = ttk.Frame(self.dialog, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Application name and version
        title_label = ttk.Label(
            main_frame,
            text=f"{APP_NAME}",
            font=("Arial", 16, "bold"),
            foreground="darkblue"
        )
        title_label.pack(pady=(0, 5))
        
        version_label = ttk.Label(
            main_frame,
            text=f"Version {APP_VERSION}",
            font=("Arial", 11),
            foreground="gray"
        )
        version_label.pack(pady=(0, 15))
        
        # Separator
        separator = ttk.Separator(main_frame, orient=tk.HORIZONTAL)
        separator.pack(fill=tk.X, pady=10)
        
        # Description
        description_frame = ttk.LabelFrame(main_frame, text="Description", padding=10)
        description_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        description_text = tk.Text(description_frame, height=6, width=50, wrap=tk.WORD, relief=tk.FLAT)
        description_text.pack(fill=tk.BOTH, expand=True)
        
        description_content = """Local desktop application for managing physical media inventory.

Provides comprehensive tools for cataloging, searching, and organizing media collections with support for multiple storage locations and expiration tracking.

Supports import/export from Microsoft Access databases and CSV files."""
        
        description_text.insert(tk.END, description_content)
        description_text.config(state=tk.DISABLED)
        
        # Technology stack
        tech_frame = ttk.LabelFrame(main_frame, text="Technology Stack", padding=10)
        tech_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        tech_items = [
            "• Python 3.x",
            "• Tkinter (GUI framework)",
            "• SQLite (Database)",
            "• CSV import/export",
        ]
        
        for item in tech_items:
            label = ttk.Label(tech_frame, text=item)
            label.pack(anchor=tk.W, pady=2)
        
        # Close button
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Button(button_frame, text="Close", command=self._on_close).pack(side=tk.RIGHT)
        
        logger.debug("About dialog content created")

    def _on_close(self) -> None:
        """Handle close button click."""
        self.result = True
        self.dialog.destroy()
        logger.debug("About dialog closed")

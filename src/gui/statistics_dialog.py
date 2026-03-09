"""Statistics dialog for displaying media and location statistics.

This module provides a dialog for viewing comprehensive statistics about
the media archive including counts by type, location, and expiration status.

History:
20260309  V1.0: Initial statistics dialog implementation
"""

import logging
import tkinter as tk
from tkinter import ttk

logger = logging.getLogger(__name__)


class StatisticsDialog:
    """Dialog for displaying media and location statistics."""

    def __init__(self, parent: tk.Widget, stats: dict, locations_count: int) -> None:
        """Initialize statistics dialog.
        
        Args:
            parent: Parent window.
            stats: Statistics dictionary from MediaService.get_media_statistics().
            locations_count: Total number of storage locations.
        """
        self.parent = parent
        self.stats = stats
        self.locations_count = locations_count
        self.result = False
        
        logger.debug("StatisticsDialog initialized")

    def show(self) -> bool:
        """Show the statistics dialog.
        
        Returns:
            True if dialog was closed normally, False if cancelled.
        """
        # Create dialog window
        self.dialog = tk.Toplevel(self.parent)
        self.dialog.title("Media Archive Statistics")
        self.dialog.geometry("500x600")
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
        main_frame = ttk.Frame(self.dialog, padding=15)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(main_frame, text="Media Archive Statistics", font=("Arial", 14, "bold"))
        title_label.pack(pady=(0, 15))
        
        # Create notebook for tabs
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
        
        # Overview tab
        self._create_overview_tab(notebook)
        
        # By Type tab
        self._create_by_type_tab(notebook)
        
        # Close button
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Button(button_frame, text="Close", command=self._on_close).pack(side=tk.RIGHT)
        
        logger.debug("Statistics dialog content created")

    def _create_overview_tab(self, notebook: ttk.Notebook) -> None:
        """Create overview statistics tab.
        
        Args:
            notebook: Parent notebook widget.
        """
        frame = ttk.Frame(notebook, padding=10)
        notebook.add(frame, text="Overview")
        
        # Create scrollable frame
        canvas = tk.Canvas(frame, highlightthickness=0)
        scrollbar = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Media statistics
        self._add_stat_section(scrollable_frame, "Media Statistics")
        self._add_stat_row(scrollable_frame, "Total Media:", str(self.stats["total_media"]))
        self._add_stat_row(scrollable_frame, "Expired Media:", str(self.stats["expired_media"]))
        self._add_stat_row(scrollable_frame, "Expiring Soon (30 days):", str(self.stats["expiring_soon"]))
        
        # Location statistics
        self._add_stat_section(scrollable_frame, "Location Statistics")
        self._add_stat_row(scrollable_frame, "Total Locations:", str(self.locations_count))
        self._add_stat_row(scrollable_frame, "Media with Location:", str(self.stats["media_with_location"]))
        self._add_stat_row(scrollable_frame, "Media without Location:", str(self.stats["media_without_location"]))
        
        # Pack canvas and scrollbar
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        logger.debug("Overview tab created")

    def _create_by_type_tab(self, notebook: ttk.Notebook) -> None:
        """Create media by type statistics tab.
        
        Args:
            notebook: Parent notebook widget.
        """
        frame = ttk.Frame(notebook, padding=10)
        notebook.add(frame, text="By Type")
        
        # Create scrollable frame
        canvas = tk.Canvas(frame, highlightthickness=0)
        scrollbar = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Media by type
        self._add_stat_section(scrollable_frame, "Media Count by Type")
        
        if self.stats["media_by_type"]:
            # Sort by count descending, then by type name
            sorted_types = sorted(
                self.stats["media_by_type"].items(),
                key=lambda x: (-x[1], x[0])
            )
            
            for media_type, count in sorted_types:
                self._add_stat_row(scrollable_frame, f"{media_type}:", str(count))
        else:
            label = ttk.Label(scrollable_frame, text="No media types found", foreground="gray")
            label.pack(anchor=tk.W, pady=5)
        
        # Pack canvas and scrollbar
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        logger.debug("By Type tab created")

    def _add_stat_section(self, parent: ttk.Frame, title: str) -> None:
        """Add a statistics section header.
        
        Args:
            parent: Parent frame.
            title: Section title.
        """
        label = ttk.Label(parent, text=title, font=("Arial", 11, "bold"), foreground="darkblue")
        label.pack(anchor=tk.W, pady=(10, 5))

    def _add_stat_row(self, parent: ttk.Frame, label_text: str, value_text: str) -> None:
        """Add a statistics row with label and value.
        
        Args:
            parent: Parent frame.
            label_text: Label text.
            value_text: Value text.
        """
        row_frame = ttk.Frame(parent)
        row_frame.pack(anchor=tk.W, fill=tk.X, pady=2)
        
        label = ttk.Label(row_frame, text=label_text, width=30)
        label.pack(side=tk.LEFT)
        
        value = ttk.Label(row_frame, text=value_text, font=("Arial", 10, "bold"), foreground="darkgreen")
        value.pack(side=tk.LEFT)

    def _on_close(self) -> None:
        """Handle close button click."""
        self.result = True
        self.dialog.destroy()
        logger.debug("Statistics dialog closed")

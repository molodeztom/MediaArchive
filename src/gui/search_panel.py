"""Search panel widget for Media Archive Manager GUI.

This module provides a reusable search panel widget with multiple filter options.

History:
20260307  V1.0: Initial search panel implementation
"""

import logging
import tkinter as tk
from tkinter import ttk
from typing import Optional, Callable, List
from datetime import date

from models.enums import MediaType
from models.location import StorageLocation

logger = logging.getLogger(__name__)


class SearchPanel(ttk.Frame):
    """Reusable search panel widget with multiple filter options.
    
    Provides search by name, filter by type, filter by location,
    date range filtering, and expired media filtering.
    """

    def __init__(
        self,
        parent: tk.Widget,
        locations: Optional[List[StorageLocation]] = None,
        on_search: Optional[Callable[[], None]] = None,
        on_clear: Optional[Callable[[], None]] = None,
    ) -> None:
        """Initialize search panel.
        
        Args:
            parent: Parent widget.
            locations: List of available storage locations.
            on_search: Optional callback when search button is clicked.
            on_clear: Optional callback when clear button is clicked.
        """
        super().__init__(parent)
        self.locations = locations or []
        self.on_search = on_search
        self.on_clear = on_clear
        
        # Create UI
        self._create_widgets()
        
        logger.debug("SearchPanel initialized")

    def _create_widgets(self) -> None:
        """Create search panel widgets."""
        # Main frame with padding
        main_frame = ttk.LabelFrame(self, text="Search & Filter Media", padding=10)
        main_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Row 1: Search by name
        ttk.Label(main_frame, text="Search by name:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.search_entry = ttk.Entry(main_frame, width=25)
        self.search_entry.grid(row=0, column=1, sticky=tk.EW, padx=5, pady=5)
        
        # Row 1: Filter by type
        ttk.Label(main_frame, text="Filter by type:").grid(row=0, column=2, sticky=tk.W, padx=5, pady=5)
        self.type_filter_var = tk.StringVar()
        type_values = ["All"] + MediaType.get_all_values()
        type_combo = ttk.Combobox(
            main_frame,
            textvariable=self.type_filter_var,
            values=type_values,
            state="readonly",
            width=15
        )
        type_combo.set("All")
        type_combo.grid(row=0, column=3, sticky=tk.EW, padx=5, pady=5)
        
        # Row 2: Filter by location
        ttk.Label(main_frame, text="Filter by location:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.location_filter_var = tk.StringVar()
        self.location_filter_combo = ttk.Combobox(
            main_frame,
            textvariable=self.location_filter_var,
            state="readonly",
            width=25
        )
        self.location_filter_combo.grid(row=1, column=1, sticky=tk.EW, padx=5, pady=5)
        self._update_location_filter()
        
        # Row 2: Show expired checkbox
        self.show_expired_var = tk.BooleanVar()
        ttk.Checkbutton(
            main_frame,
            text="Show only expired",
            variable=self.show_expired_var
        ).grid(row=1, column=2, columnspan=2, sticky=tk.W, padx=5, pady=5)
        
        # Row 3: Date range
        ttk.Label(main_frame, text="Date range:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        
        ttk.Label(main_frame, text="From:").grid(row=2, column=1, sticky=tk.E, padx=5, pady=5)
        self.date_from_var = tk.StringVar()
        date_from_entry = ttk.Entry(main_frame, textvariable=self.date_from_var, width=12)
        date_from_entry.grid(row=2, column=2, sticky=tk.W, padx=5, pady=5)
        ttk.Label(main_frame, text="(YYYY-MM-DD)", font=("TkDefaultFont", 8)).grid(
            row=2, column=3, sticky=tk.W, padx=2, pady=5
        )
        
        ttk.Label(main_frame, text="To:").grid(row=3, column=1, sticky=tk.E, padx=5, pady=5)
        self.date_to_var = tk.StringVar()
        date_to_entry = ttk.Entry(main_frame, textvariable=self.date_to_var, width=12)
        date_to_entry.grid(row=3, column=2, sticky=tk.W, padx=5, pady=5)
        ttk.Label(main_frame, text="(YYYY-MM-DD)", font=("TkDefaultFont", 8)).grid(
            row=3, column=3, sticky=tk.W, padx=2, pady=5
        )
        
        # Row 4: Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=4, column=0, columnspan=4, sticky=tk.W, padx=5, pady=10)
        
        ttk.Button(button_frame, text="Search", command=self._on_search).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Clear", command=self._on_clear).pack(side=tk.LEFT, padx=5)
        
        # Configure grid weights
        main_frame.columnconfigure(1, weight=1)
        main_frame.columnconfigure(3, weight=1)

    def _update_location_filter(self) -> None:
        """Update location filter dropdown."""
        location_values = ["All"] + [f"{loc.id}: {loc}" for loc in self.locations]
        self.location_filter_combo.config(values=location_values)
        self.location_filter_combo.set("All")

    def update_locations(self, locations: List[StorageLocation]) -> None:
        """Update available locations.
        
        Args:
            locations: List of storage locations.
        """
        self.locations = locations
        self._update_location_filter()

    def get_search_criteria(self) -> dict:
        """Get current search criteria.
        
        Returns:
            Dictionary with search criteria.
        """
        return {
            "query": self.search_entry.get().strip(),
            "type_filter": self.type_filter_var.get(),
            "location_filter": self.location_filter_var.get(),
            "show_expired": self.show_expired_var.get(),
            "date_from": self.date_from_var.get().strip(),
            "date_to": self.date_to_var.get().strip(),
        }

    def clear_filters(self) -> None:
        """Clear all search filters."""
        self.search_entry.delete(0, tk.END)
        self.type_filter_var.set("All")
        self.location_filter_var.set("All")
        self.show_expired_var.set(False)
        self.date_from_var.set("")
        self.date_to_var.set("")

    def _on_search(self) -> None:
        """Handle search button click."""
        if self.on_search:
            self.on_search()

    def _on_clear(self) -> None:
        """Handle clear button click."""
        self.clear_filters()
        if self.on_clear:
            self.on_clear()

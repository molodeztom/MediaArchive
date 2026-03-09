"""Main application window for Media Archive Manager.

This module provides the main GUI window with menu bar, toolbar, and main content area.

History:
20260307  V1.0: Initial main window implementation
20260307  V1.1: Added location management and search/filter functionality
20260307  V1.2: Integrated SearchPanel and enhanced filter menu
20260307  V1.3: Added import/export and backup functionality
20260308  V1.4: Implement two-phase import for locations and media
20260309  V1.5: Added location assignment after import and manual assignment tool
20260309  V1.6: Fixed position display in media tab to show place from DB
20260309  V1.7: Hide internal ID column, display media number as first column
20260309  V1.8: Added Category column to media tab between Type and Box
20260309  V1.9: Hide location tab ID column, store ID in treeview iid
20260309  V1.10: Sort media tab by Number column (numeric first)
20260309  V1.11: Added position parameter to media update callback
20260309  V1.12: Pass categories to media dialogs for combobox
20260309  V1.13: Updated search to use separate box and place filters
20260309  V1.14: Removed Filter > By Location menu item
20260309  V1.15: Search results show Number, Name, Type, Box, Position, Place
20260309  V1.16: Added column sorting to media tab with visual indicators
20260309  V1.17: Added column sorting to locations tab with visual indicators
20260309  V1.18: Added StatisticsDialog and AboutDialog for Phase 7
20260309  V1.19: Updated date display to DD.MM.YYYY format using format_date()
"""

import logging
import tkinter as tk
from tkinter import ttk, messagebox
from pathlib import Path
from datetime import date
import shutil

from data.database import Database
from data.preferences_repository import PreferencesRepository
from business.location_service import LocationService
from business.media_service import MediaService
from models.location import StorageLocation
from models.enums import MediaType
from utils.config import APP_NAME, APP_VERSION, DB_PATH, WINDOW_WIDTH, WINDOW_HEIGHT
from utils.date_utils import format_date
from gui.dialogs import (
    AddMediaDialog, EditMediaDialog, DeleteConfirmDialog,
    AddLocationDialog, EditLocationDialog, DeleteLocationConfirmDialog,
    LocationAssignmentResultsDialog
)
from gui.search_panel import SearchPanel
from gui.import_dialog import ImportDialog
from gui.export_dialog import ExportDialog
from gui.statistics_dialog import StatisticsDialog
from gui.about_dialog import AboutDialog

logger = logging.getLogger(__name__)


class MainWindow:
    """Main application window.
    
    Provides the primary user interface with menu bar, toolbar, and content area.
    """

    def __init__(self, root: tk.Tk) -> None:
        """Initialize main window.
        
        Args:
            root: Tkinter root window.
        """
        self.root = root
        self.root.title(f"{APP_NAME} v{APP_VERSION}")
        self.root.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
        
        # Initialize status variable first
        self.status_var = tk.StringVar()
        self.status_var.set("Initializing...")
        
        # Initialize database and services first (needed for preferences)
        self._init_database()
        
        # Load sorting preferences from database
        self.media_sort_column = self.preferences_repo.get_preference("media_sort_column", "Number")
        self.media_sort_reverse = self.preferences_repo.get_preference("media_sort_reverse", "False") == "True"
        
        self.location_sort_column = self.preferences_repo.get_preference("location_sort_column", "Box")
        self.location_sort_reverse = self.preferences_repo.get_preference("location_sort_reverse", "False") == "True"
        
        # Build UI
        self._create_menu_bar()
        self._create_toolbar()
        self._create_main_content()
        self._create_status_bar()
        
        logger.info("Main window initialized")

    def _init_database(self) -> None:
        """Initialize database connection and services."""
        try:
            self.db = Database(DB_PATH)
            self.db.init_schema()
            self.location_service = LocationService(self.db)
            self.media_service = MediaService(self.db)
            self.preferences_repo = PreferencesRepository(self.db)
            logger.info("Database initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")
            messagebox.showerror("Database Error", f"Failed to initialize database: {e}")
            raise

    def _create_menu_bar(self) -> None:
        """Create menu bar with File, Edit, View, and Help menus."""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Import", command=self._import_data, accelerator="Ctrl+I")
        file_menu.add_command(label="Export", command=self._export_data, accelerator="Ctrl+E")
        file_menu.add_separator()
        file_menu.add_command(label="Backup Database", command=self._backup_database)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit, accelerator="Ctrl+Q")
        
        # Edit menu
        edit_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Edit", menu=edit_menu)
        edit_menu.add_command(label="Preferences", command=self._show_preferences)
        
        # View menu
        view_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="View", menu=view_menu)
        view_menu.add_command(label="Refresh", command=self._refresh_view, accelerator="F5")
        view_menu.add_separator()
        view_menu.add_command(label="Show All Media", command=self._show_all_media)
        view_menu.add_command(label="Show Expired Media", command=self._show_expired, accelerator="Ctrl+X")
        view_menu.add_separator()
        view_menu.add_command(label="Statistics", command=self._show_statistics)
        
        # Tools menu
        tools_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Tools", menu=tools_menu)
        tools_menu.add_command(label="Assign Locations to Media", command=self._assign_locations)
        
        # Filter menu
        filter_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Filter", menu=filter_menu)
        
        # Filter by type submenu
        type_menu = tk.Menu(filter_menu, tearoff=0)
        filter_menu.add_cascade(label="By Type", menu=type_menu)
        for media_type in MediaType.get_all_values():
            type_menu.add_command(
                label=media_type,
                command=lambda mt=media_type: self._filter_by_type(mt)
            )
        
        filter_menu.add_separator()
        filter_menu.add_command(label="Clear Filters", command=self._clear_all_filters)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="User Guide", command=self._show_user_guide, accelerator="F1")
        help_menu.add_separator()
        help_menu.add_command(label="About", command=self._show_about)
        
        # Bind keyboard shortcuts
        self.root.bind("<Control-q>", lambda e: self.root.quit())
        self.root.bind("<F5>", lambda e: self._refresh_view())
        self.root.bind("<Control-n>", lambda e: self._add_media())
        self.root.bind("<Control-e>", lambda e: self._edit_media())
        self.root.bind("<Delete>", lambda e: self._delete_media())
        self.root.bind("<Control-l>", lambda e: self._show_locations())
        self.root.bind("<Control-f>", lambda e: self.notebook.select(2))
        self.root.bind("<Control-x>", lambda e: self._show_expired())
        self.root.bind("<Control-i>", lambda e: self._import_data())
        self.root.bind("<Control-e>", lambda e: self._export_data())
        self.root.bind("<F1>", lambda e: self._show_user_guide())
        
        logger.debug("Menu bar created")

    def _create_toolbar(self) -> None:
        """Create toolbar with action buttons."""
        toolbar = ttk.Frame(self.root)
        toolbar.pack(side=tk.TOP, fill=tk.X, padx=2, pady=2)
        
        # Buttons with tooltips
        add_btn = ttk.Button(toolbar, text="Add Media", command=self._add_media)
        add_btn.pack(side=tk.LEFT, padx=2)
        self._create_tooltip(add_btn, "Add new media item (Ctrl+N)")
        
        edit_btn = ttk.Button(toolbar, text="Edit Media", command=self._edit_media)
        edit_btn.pack(side=tk.LEFT, padx=2)
        self._create_tooltip(edit_btn, "Edit selected media (Ctrl+E)")
        
        delete_btn = ttk.Button(toolbar, text="Delete Media", command=self._delete_media)
        delete_btn.pack(side=tk.LEFT, padx=2)
        self._create_tooltip(delete_btn, "Delete selected media (Delete)")
        
        ttk.Separator(toolbar, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=5)
        
        loc_btn = ttk.Button(toolbar, text="Locations", command=self._show_locations)
        loc_btn.pack(side=tk.LEFT, padx=2)
        self._create_tooltip(loc_btn, "Manage storage locations (Ctrl+L)")
        
        exp_btn = ttk.Button(toolbar, text="Expired", command=self._show_expired)
        exp_btn.pack(side=tk.LEFT, padx=2)
        self._create_tooltip(exp_btn, "Show expired media (Ctrl+X)")
        
        logger.debug("Toolbar created")

    def _create_main_content(self) -> None:
        """Create main content area with notebook (tabs)."""
        # Create notebook for tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Media tab
        self._create_media_tab()
        
        # Locations tab
        self._create_locations_tab()
        
        # Search tab
        self._create_search_tab()
        
        logger.debug("Main content area created")

    def _create_media_tab(self) -> None:
        """Create media management tab."""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Media")
        
        # Create treeview for media list
        columns = ("Number", "Name", "Type", "Category", "Box", "Position", "Company", "License", "Created", "Expires")
        self.media_tree = ttk.Treeview(frame, columns=columns, height=20)
        self.media_tree.column("#0", width=0, stretch=tk.NO)
        self.media_tree.column("Number", anchor=tk.W, width=80)
        self.media_tree.column("Name", anchor=tk.W, width=150)
        self.media_tree.column("Type", anchor=tk.W, width=80)
        self.media_tree.column("Category", anchor=tk.W, width=80)
        self.media_tree.column("Box", anchor=tk.W, width=60)
        self.media_tree.column("Position", anchor=tk.W, width=80)
        self.media_tree.column("Company", anchor=tk.W, width=100)
        self.media_tree.column("License", anchor=tk.W, width=80)
        self.media_tree.column("Created", anchor=tk.W, width=100)
        self.media_tree.column("Expires", anchor=tk.W, width=100)
        
        self.media_tree.heading("#0", text="", anchor=tk.W)
        self.media_tree.heading("Number", text="Number", anchor=tk.W, command=lambda: self._sort_media_by_column("Number"))
        self.media_tree.heading("Name", text="Name", anchor=tk.W, command=lambda: self._sort_media_by_column("Name"))
        self.media_tree.heading("Type", text="Type", anchor=tk.W, command=lambda: self._sort_media_by_column("Type"))
        self.media_tree.heading("Category", text="Category", anchor=tk.W, command=lambda: self._sort_media_by_column("Category"))
        self.media_tree.heading("Box", text="Box", anchor=tk.W, command=lambda: self._sort_media_by_column("Box"))
        self.media_tree.heading("Position", text="Position", anchor=tk.W, command=lambda: self._sort_media_by_column("Position"))
        self.media_tree.heading("Company", text="Company", anchor=tk.W, command=lambda: self._sort_media_by_column("Company"))
        self.media_tree.heading("License", text="License", anchor=tk.W, command=lambda: self._sort_media_by_column("License"))
        self.media_tree.heading("Created", text="Created", anchor=tk.W, command=lambda: self._sort_media_by_column("Created"))
        self.media_tree.heading("Expires", text="Expires", anchor=tk.W, command=lambda: self._sort_media_by_column("Expires"))
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=self.media_tree.yview)
        self.media_tree.configure(yscroll=scrollbar.set)
        
        self.media_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Bind double-click to jump to location
        self.media_tree.bind("<Double-1>", self._on_media_double_click)
        
        # Load media
        self._refresh_media_list()
        
        # Update header indicators to show current sort state
        self._update_media_header_indicators()
        
        logger.debug("Media tab created")

    def _create_locations_tab(self) -> None:
        """Create location management tab."""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Locations")
        
        # Create toolbar for location management
        toolbar = ttk.Frame(frame)
        toolbar.pack(side=tk.TOP, fill=tk.X, padx=2, pady=2)
        
        ttk.Button(toolbar, text="Add Location", command=self._add_location).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="Edit Location", command=self._edit_location).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="Delete Location", command=self._delete_location).pack(side=tk.LEFT, padx=2)
        
        # Create treeview for locations (ID hidden, stored in iid)
        columns = ("Box", "Place", "Detail", "Media Count")
        self.location_tree = ttk.Treeview(frame, columns=columns, height=20)
        self.location_tree.column("#0", width=0, stretch=tk.NO)
        self.location_tree.column("Box", anchor=tk.W, width=150)
        self.location_tree.column("Place", anchor=tk.W, width=150)
        self.location_tree.column("Detail", anchor=tk.W, width=150)
        self.location_tree.column("Media Count", anchor=tk.W, width=100)
        
        self.location_tree.heading("#0", text="", anchor=tk.W)
        self.location_tree.heading("Box", text="Box", anchor=tk.W, command=lambda: self._sort_locations_by_column("Box"))
        self.location_tree.heading("Place", text="Place", anchor=tk.W, command=lambda: self._sort_locations_by_column("Place"))
        self.location_tree.heading("Detail", text="Detail", anchor=tk.W, command=lambda: self._sort_locations_by_column("Detail"))
        self.location_tree.heading("Media Count", text="Media Count", anchor=tk.W, command=lambda: self._sort_locations_by_column("Media Count"))
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=self.location_tree.yview)
        self.location_tree.configure(yscroll=scrollbar.set)
        
        self.location_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Load locations
        self._refresh_locations_list()
        
        # Update header indicators to show current sort state
        self._update_locations_header_indicators()
        
        logger.debug("Locations tab created")

    def _create_search_tab(self) -> None:
        """Create search and filter tab."""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Search")
        
        # Create search panel
        self.search_panel = SearchPanel(
            frame,
            locations=self.location_service.get_all_locations(),
            on_search=self._perform_search,
            on_clear=self._clear_search
        )
        self.search_panel.pack(fill=tk.X)
        
        # Results frame
        results_frame = ttk.LabelFrame(frame, text="Search Results", padding=10)
        results_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        columns = ("Number", "Name", "Type", "Box", "Position", "Place")
        self.search_tree = ttk.Treeview(results_frame, columns=columns, height=15)
        self.search_tree.column("#0", width=0, stretch=tk.NO)
        self.search_tree.column("Number", anchor=tk.W, width=80)
        self.search_tree.column("Name", anchor=tk.W, width=150)
        self.search_tree.column("Type", anchor=tk.W, width=80)
        self.search_tree.column("Box", anchor=tk.W, width=80)
        self.search_tree.column("Position", anchor=tk.W, width=80)
        self.search_tree.column("Place", anchor=tk.W, width=150)
        
        self.search_tree.heading("#0", text="", anchor=tk.W)
        self.search_tree.heading("Number", text="Number", anchor=tk.W)
        self.search_tree.heading("Name", text="Name", anchor=tk.W)
        self.search_tree.heading("Type", text="Type", anchor=tk.W)
        self.search_tree.heading("Box", text="Box", anchor=tk.W)
        self.search_tree.heading("Position", text="Position", anchor=tk.W)
        self.search_tree.heading("Place", text="Place", anchor=tk.W)
        
        scrollbar = ttk.Scrollbar(results_frame, orient=tk.VERTICAL, command=self.search_tree.yview)
        self.search_tree.configure(yscroll=scrollbar.set)
        
        self.search_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        logger.debug("Search tab created")

    def _create_status_bar(self) -> None:
        """Create status bar at bottom of window."""
        self.status_var.set("Ready")
        
        status_bar = ttk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        logger.debug("Status bar created")

    def _create_tooltip(self, widget: tk.Widget, text: str) -> None:
        """Create a tooltip for a widget.
        
        Args:
            widget: Widget to attach tooltip to.
            text: Tooltip text.
        """
        def on_enter(event):
            tooltip = tk.Toplevel()
            tooltip.wm_overrideredirect(True)
            tooltip.wm_geometry(f"+{event.x_root+10}+{event.y_root+10}")
            label = ttk.Label(tooltip, text=text, background="lightyellow", relief=tk.SOLID, borderwidth=1)
            label.pack()
            widget.tooltip = tooltip
        
        def on_leave(event):
            if hasattr(widget, 'tooltip'):
                widget.tooltip.destroy()
                del widget.tooltip
        
        widget.bind("<Enter>", on_enter)
        widget.bind("<Leave>", on_leave)

    def _refresh_media_list(self) -> None:
        """Refresh media list in media tab."""
        try:
            # Clear existing items
            for item in self.media_tree.get_children():
                self.media_tree.delete(item)
            
            # Load media
            media_list = self.media_service.get_all_media()
            
            # Sort media by current sort column and direction
            media_list = self._sort_media_list(media_list, self.media_sort_column, self.media_sort_reverse)
            
            # Create location lookup for display
            locations = self.location_service.get_all_locations()
            location_map = {loc.id: loc for loc in locations}
            
            for media in media_list:
                created = format_date(media.creation_date) if media.creation_date else "N/A"
                expires = format_date(media.valid_until_date) if media.valid_until_date else "N/A"
                company = media.company if media.company else "N/A"
                license_code = media.license_code if media.license_code else "N/A"
                position = media.position if media.position else "N/A"
                number = media.number if media.number else "N/A"
                category = media.category if media.category else "N/A"
                
                # Get box from location table
                if media.location_id and media.location_id in location_map:
                    box = location_map[media.location_id].box
                else:
                    box = "N/A"
                
                # Use media.id as the item ID in treeview for later retrieval
                self.media_tree.insert("", tk.END, iid=str(media.id), values=(
                    number,
                    media.name,
                    media.media_type,
                    category,
                    box,
                    position,
                    company,
                    license_code,
                    created,
                    expires
                ))
            
            self.status_var.set(f"Loaded {len(media_list)} media items")
            logger.debug(f"Refreshed media list: {len(media_list)} items")
        except Exception as e:
            logger.error(f"Failed to refresh media list: {e}")
            messagebox.showerror("Error", f"Failed to load media: {e}")

    def _update_media_header_indicators(self) -> None:
        """Update media table header indicators to show current sort state."""
        try:
            for col in self.media_tree["columns"]:
                if col == self.media_sort_column:
                    indicator = " ▼" if self.media_sort_reverse else " ▲"
                    self.media_tree.heading(col, text=col + indicator)
                else:
                    self.media_tree.heading(col, text=col)
        except Exception as e:
            logger.error(f"Error updating media header indicators: {e}")

    def _update_locations_header_indicators(self) -> None:
        """Update locations table header indicators to show current sort state."""
        try:
            for col in self.location_tree["columns"]:
                if col == self.location_sort_column:
                    indicator = " ▼" if self.location_sort_reverse else " ▲"
                    self.location_tree.heading(col, text=col + indicator)
                else:
                    self.location_tree.heading(col, text=col)
        except Exception as e:
            logger.error(f"Error updating locations header indicators: {e}")

    def _sort_media_list(self, media_list: list, column: str, reverse: bool) -> list:
        """Sort media list by specified column.
        
        Args:
            media_list: List of media to sort.
            column: Column name to sort by.
            reverse: If True, sort in descending order.
        
        Returns:
            Sorted media list.
        """
        def get_sort_key(media):
            if column == "Number":
                if media.number:
                    try:
                        return (0, int(media.number))
                    except ValueError:
                        return (1, media.number)
                return (2, "")
            elif column == "Name":
                return media.name.lower() if media.name else ""
            elif column == "Type":
                return media.media_type.lower() if media.media_type else ""
            elif column == "Category":
                return media.category.lower() if media.category else ""
            elif column == "Box":
                # Get box from location
                if media.location_id:
                    locations = self.location_service.get_all_locations()
                    location_map = {loc.id: loc for loc in locations}
                    if media.location_id in location_map:
                        box = location_map[media.location_id].box
                        try:
                            return (0, int(box))
                        except ValueError:
                            return (1, box.lower())
                return (2, "")
            elif column == "Position":
                return media.position.lower() if media.position else ""
            elif column == "Company":
                return media.company.lower() if media.company else ""
            elif column == "License":
                return media.license_code.lower() if media.license_code else ""
            elif column == "Created":
                return media.creation_date if media.creation_date else date.min
            elif column == "Expires":
                return media.valid_until_date if media.valid_until_date else date.min
            else:
                return ""
        
        return sorted(media_list, key=get_sort_key, reverse=reverse)

    def _sort_media_by_column(self, column: str) -> None:
        """Sort media by clicked column header.
        
        Args:
            column: Column name to sort by.
        """
        try:
            # Toggle direction if same column, otherwise start ascending
            if self.media_sort_column == column:
                self.media_sort_reverse = not self.media_sort_reverse
            else:
                self.media_sort_column = column
                self.media_sort_reverse = False
            
            # Save preferences to database
            self.preferences_repo.set_preference("media_sort_column", self.media_sort_column)
            self.preferences_repo.set_preference("media_sort_reverse", str(self.media_sort_reverse))
            
            # Refresh with new sort
            self._refresh_media_list()
            
            # Update header indicators
            self._update_media_header_indicators()
            
            logger.debug(f"Sorted media by {column} ({'descending' if self.media_sort_reverse else 'ascending'})")
        except Exception as e:
            logger.error(f"Error sorting media: {e}")

    def _sort_locations_list(self, locations: list, column: str, reverse: bool) -> list:
        """Sort locations list by specified column.
        
        Args:
            locations: List of locations to sort.
            column: Column name to sort by.
            reverse: If True, sort in descending order.
        
        Returns:
            Sorted locations list with media counts.
        """
        def get_sort_key(item):
            loc, media_count = item
            if column == "Box":
                try:
                    return (0, int(loc.box))
                except ValueError:
                    return (1, loc.box.lower())
            elif column == "Place":
                return loc.place.lower() if loc.place else ""
            elif column == "Detail":
                return loc.detail.lower() if loc.detail else ""
            elif column == "Media Count":
                return media_count
            else:
                return ""
        
        # Create list of (location, media_count) tuples
        location_items = []
        for loc in locations:
            media_count = len(self.media_service.get_media_by_location(loc.id))
            location_items.append((loc, media_count))
        
        # Sort and return just the locations
        sorted_items = sorted(location_items, key=get_sort_key, reverse=reverse)
        return [(loc, count) for loc, count in sorted_items]

    def _sort_locations_by_column(self, column: str) -> None:
        """Sort locations by clicked column header.
        
        Args:
            column: Column name to sort by.
        """
        try:
            # Toggle direction if same column, otherwise start ascending
            if self.location_sort_column == column:
                self.location_sort_reverse = not self.location_sort_reverse
            else:
                self.location_sort_column = column
                self.location_sort_reverse = False
            
            # Save preferences to database
            self.preferences_repo.set_preference("location_sort_column", self.location_sort_column)
            self.preferences_repo.set_preference("location_sort_reverse", str(self.location_sort_reverse))
            
            # Refresh with new sort
            self._refresh_locations_list()
            
            # Update header indicators
            self._update_locations_header_indicators()
            
            logger.debug(f"Sorted locations by {column} ({'descending' if self.location_sort_reverse else 'ascending'})")
        except Exception as e:
            logger.error(f"Error sorting locations: {e}")

    def _refresh_locations_list(self) -> None:
        """Refresh locations list in locations tab."""
        try:
            # Clear existing items
            for item in self.location_tree.get_children():
                self.location_tree.delete(item)
            
            # Load locations
            locations = self.location_service.get_all_locations()
            
            # Sort locations by current sort column and direction
            sorted_locations_with_counts = self._sort_locations_list(locations, self.location_sort_column, self.location_sort_reverse)
            
            for loc, media_count in sorted_locations_with_counts:
                # Store location ID in iid, not in values
                self.location_tree.insert("", tk.END, iid=str(loc.id), values=(
                    loc.box,
                    loc.place,
                    loc.detail or "",
                    media_count
                ))
            
            self.status_var.set(f"Loaded {len(locations)} locations")
            logger.debug(f"Refreshed locations list: {len(locations)} items")
            
            # Update search panel locations
            if hasattr(self, 'search_panel'):
                self.search_panel.update_locations(locations)
        except Exception as e:
            logger.error(f"Failed to refresh locations list: {e}")
            messagebox.showerror("Error", f"Failed to load locations: {e}")

    def _refresh_view(self) -> None:
        """Refresh all views."""
        self._refresh_media_list()
        self._refresh_locations_list()
        self.status_var.set("View refreshed")

    def _add_media(self) -> None:
        """Add new media item."""
        try:
            # Get available locations
            locations = self.location_service.get_all_locations()
            
            # Get existing categories
            categories = self.media_service.get_unique_categories()
            
            # Create and show dialog
            dialog = AddMediaDialog(self.root, locations, categories, on_save=self._on_media_added)
            result = dialog.show()
            
            if result:
                self.status_var.set("Media added successfully")
                self._refresh_media_list()
        except Exception as e:
            logger.error(f"Error adding media: {e}")
            messagebox.showerror("Error", f"Failed to add media: {e}")

    def _on_media_added(self, media) -> None:
        """Callback when media is added via dialog."""
        try:
            # Save media to database
            created = self.media_service.create_media(
                name=media.name,
                number=media.number,
                media_type=media.media_type,
                category=media.category,
                content_description=media.content_description,
                remarks=media.remarks,
                creation_date=media.creation_date,
                valid_until_date=media.valid_until_date,
                company=media.company,
                license_code=media.license_code,
                location_id=media.location_id,
            )
            logger.info(f"Media created: {created.id}")
        except Exception as e:
            logger.error(f"Error saving media: {e}")
            messagebox.showerror("Error", f"Failed to save media: {e}")

    def _edit_media(self) -> None:
        """Edit selected media item."""
        try:
            # Get selected media
            selection = self.media_tree.selection()
            if not selection:
                messagebox.showwarning("Selection Error", "Please select a media item to edit")
                return
            
            # Get media ID from treeview item ID
            item = selection[0]
            media_id = int(item)
            
            # Get media details
            media = self.media_service.get_media(media_id)
            
            # Get available locations
            locations = self.location_service.get_all_locations()
            
            # Get existing categories
            categories = self.media_service.get_unique_categories()
            
            # Create and show dialog
            dialog = EditMediaDialog(self.root, media, locations, categories, on_save=self._on_media_updated)
            result = dialog.show()
            
            if result:
                self.status_var.set("Media updated successfully")
                self._refresh_media_list()
        except Exception as e:
            logger.error(f"Error editing media: {e}")
            messagebox.showerror("Error", f"Failed to edit media: {e}")

    def _on_media_updated(self, media) -> None:
        """Callback when media is updated via dialog."""
        try:
            # Update media in database
            updated = self.media_service.update_media(
                media_id=media.id,
                name=media.name,
                number=media.number,
                media_type=media.media_type,
                category=media.category,
                content_description=media.content_description,
                remarks=media.remarks,
                creation_date=media.creation_date,
                valid_until_date=media.valid_until_date,
                company=media.company,
                license_code=media.license_code,
                location_id=media.location_id,
                position=media.position,
            )
            logger.info(f"Media updated: {updated.id}")
        except Exception as e:
            logger.error(f"Error updating media: {e}")
            messagebox.showerror("Error", f"Failed to update media: {e}")

    def _delete_media(self) -> None:
        """Delete selected media item."""
        try:
            # Get selected media
            selection = self.media_tree.selection()
            if not selection:
                messagebox.showwarning("Selection Error", "Please select a media item to delete")
                return
            
            # Get media ID from treeview item ID
            item = selection[0]
            media_id = int(item)
            
            # Get media details
            media = self.media_service.get_media(media_id)
            
            # Create and show confirmation dialog
            dialog = DeleteConfirmDialog(self.root, media, on_confirm=self._on_media_deleted)
            result = dialog.show()
            
            if result:
                self.status_var.set("Media deleted successfully")
                self._refresh_media_list()
        except Exception as e:
            logger.error(f"Error deleting media: {e}")
            messagebox.showerror("Error", f"Failed to delete media: {e}")

    def _on_media_deleted(self, media) -> None:
        """Callback when media is deleted via dialog."""
        try:
            # Delete media from database
            self.media_service.delete_media(media.id)
            logger.info(f"Media deleted: {media.id}")
        except Exception as e:
            logger.error(f"Error deleting media: {e}")
            messagebox.showerror("Error", f"Failed to delete media: {e}")

    def _add_location(self) -> None:
        """Add new location."""
        try:
            # Create and show dialog
            dialog = AddLocationDialog(self.root, on_save=self._on_location_added)
            result = dialog.show()
            
            if result:
                self.status_var.set("Location added successfully")
                self._refresh_locations_list()
        except Exception as e:
            logger.error(f"Error adding location: {e}")
            messagebox.showerror("Error", f"Failed to add location: {e}")

    def _on_location_added(self, location: StorageLocation) -> None:
        """Callback when location is added via dialog."""
        try:
            # Save location to database
            created = self.location_service.create_location(
                box=location.box,
                place=location.place,
                detail=location.detail,
            )
            logger.info(f"Location created: {created.id}")
        except Exception as e:
            logger.error(f"Error saving location: {e}")
            messagebox.showerror("Error", f"Failed to save location: {e}")

    def _edit_location(self) -> None:
        """Edit selected location."""
        try:
            # Get selected location
            selection = self.location_tree.selection()
            if not selection:
                messagebox.showwarning("Selection Error", "Please select a location to edit")
                return
            
            # Get location ID from iid
            item = selection[0]
            location_id = int(item)
            
            # Get location details
            location = self.location_service.get_location(location_id)
            
            # Create and show dialog
            dialog = EditLocationDialog(self.root, location, on_save=self._on_location_updated)
            result = dialog.show()
            
            if result:
                self.status_var.set("Location updated successfully")
                self._refresh_locations_list()
        except Exception as e:
            logger.error(f"Error editing location: {e}")
            messagebox.showerror("Error", f"Failed to edit location: {e}")

    def _on_location_updated(self, location: StorageLocation) -> None:
        """Callback when location is updated via dialog."""
        try:
            # Update location in database
            updated = self.location_service.update_location(
                location_id=location.id,
                box=location.box,
                place=location.place,
                detail=location.detail,
            )
            logger.info(f"Location updated: {updated.id}")
        except Exception as e:
            logger.error(f"Error updating location: {e}")
            messagebox.showerror("Error", f"Failed to update location: {e}")

    def _delete_location(self) -> None:
        """Delete selected location."""
        try:
            # Get selected location
            selection = self.location_tree.selection()
            if not selection:
                messagebox.showwarning("Selection Error", "Please select a location to delete")
                return
            
            # Get location ID from iid
            item = selection[0]
            location_id = int(item)
            
            # Get location details
            location = self.location_service.get_location(location_id)
            
            # Count media in this location
            media_count = len(self.media_service.get_media_by_location(location_id))
            
            # Create and show confirmation dialog
            dialog = DeleteLocationConfirmDialog(
                self.root, location, media_count, on_confirm=self._on_location_deleted
            )
            result = dialog.show()
            
            if result:
                self.status_var.set("Location deleted successfully")
                self._refresh_locations_list()
        except Exception as e:
            logger.error(f"Error deleting location: {e}")
            messagebox.showerror("Error", f"Failed to delete location: {e}")

    def _on_location_deleted(self, location: StorageLocation) -> None:
        """Callback when location is deleted via dialog."""
        try:
            # Delete location from database
            self.location_service.delete_location(location.id)
            logger.info(f"Location deleted: {location.id}")
        except Exception as e:
            logger.error(f"Error deleting location: {e}")
            messagebox.showerror("Error", f"Failed to delete location: {e}")

    def _show_locations(self) -> None:
        """Show locations tab."""
        self.notebook.select(1)

    def _show_expired(self) -> None:
        """Show expired media."""
        try:
            # Switch to search tab
            self.notebook.select(2)
            
            # Clear and set filter to show only expired
            self.search_panel.clear_filters()
            self.search_panel.show_expired_var.set(True)
            
            # Perform search
            self._perform_search()
            self.status_var.set("Showing expired media")
        except Exception as e:
            logger.error(f"Error showing expired media: {e}")
            messagebox.showerror("Error", f"Failed to show expired media: {e}")

    def _show_statistics(self) -> None:
        """Show media statistics."""
        try:
            stats = self.media_service.get_media_statistics()
            locations = self.location_service.get_all_locations()
            
            dialog = StatisticsDialog(self.root, stats, len(locations))
            dialog.show()
            
            self.status_var.set("Statistics dialog closed")
        except Exception as e:
            logger.error(f"Error getting statistics: {e}")
            messagebox.showerror("Error", f"Failed to get statistics: {e}")

    def _show_preferences(self) -> None:
        """Show preferences dialog."""
        messagebox.showinfo("Preferences", "Preferences dialog coming soon")

    def _show_about(self) -> None:
        """Show about dialog."""
        dialog = AboutDialog(self.root)
        dialog.show()
        self.status_var.set("About dialog closed")

    def _show_user_guide(self) -> None:
        """Show user guide information."""
        try:
            guide_text = """
MEDIA ARCHIVE MANAGER - USER GUIDE

MAIN FEATURES:
• Manage media inventory with detailed information
• Organize media by storage locations
• Track expiration dates and status
• Search and filter media by various criteria
• Import/Export data from CSV files
• View comprehensive statistics

TABS:
1. Media Tab: View and manage all media items
2. Locations Tab: Manage storage locations
3. Search Tab: Search and filter media

KEYBOARD SHORTCUTS:
• Ctrl+N: Add new media
• Ctrl+E: Edit selected media
• Delete: Delete selected media
• Ctrl+L: Show locations
• Ctrl+F: Show search tab
• Ctrl+X: Show expired media
• Ctrl+I: Import data
• Ctrl+E: Export data
• F5: Refresh view
• F1: Show this help
• Ctrl+Q: Exit application

GETTING STARTED:
1. Create storage locations (Locations tab)
2. Add media items (Media tab)
3. Assign locations to media
4. Use search to find media
5. Export data for backup

For more information, see the documentation.
"""
            messagebox.showinfo("User Guide", guide_text)
        except Exception as e:
            logger.error(f"Error showing user guide: {e}")
            messagebox.showerror("Error", f"Failed to show user guide: {e}")

    def _perform_search(self) -> None:
        """Perform search based on search criteria."""
        try:
            # Clear existing results
            for item in self.search_tree.get_children():
                self.search_tree.delete(item)
            
            # Get search criteria from search panel
            criteria = self.search_panel.get_search_criteria()
            query = criteria["query"]
            type_filter = criteria["type_filter"]
            box_filter = criteria.get("box_filter", "All")
            place_filter = criteria.get("place_filter", "")
            show_expired = criteria["show_expired"]
            date_from = criteria["date_from"]
            date_to = criteria["date_to"]
            
            # Start with all media or search results
            if query:
                results = self.media_service.search_media_by_name(query)
            else:
                results = self.media_service.get_all_media()
            
            # Apply type filter
            if type_filter and type_filter != "All":
                results = [m for m in results if m.media_type == type_filter]
            
            # Apply box filter
            if box_filter and box_filter != "All":
                # Get locations with matching box
                locations = self.location_service.get_all_locations()
                location_ids = [loc.id for loc in locations if loc.box == box_filter]
                results = [m for m in results if m.location_id in location_ids]
            
            # Apply place filter (text search)
            if place_filter:
                locations = self.location_service.get_all_locations()
                # Find locations where place contains the search text (case-insensitive)
                location_ids = [loc.id for loc in locations if place_filter.lower() in loc.place.lower()]
                results = [m for m in results if m.location_id in location_ids]
            
            # Apply date range filter
            if date_from or date_to:
                try:
                    if date_from:
                        from_date = date.fromisoformat(date_from)
                        results = [m for m in results if m.creation_date and m.creation_date >= from_date]
                    if date_to:
                        to_date = date.fromisoformat(date_to)
                        results = [m for m in results if m.creation_date and m.creation_date <= to_date]
                except ValueError:
                    messagebox.showwarning("Date Error", "Invalid date format (use YYYY-MM-DD)")
                    return
            
            # Apply expired filter
            if show_expired:
                results = [m for m in results if m.valid_until_date and m.valid_until_date < date.today()]
            
            # Create location lookup for display
            locations = self.location_service.get_all_locations()
            location_map = {loc.id: loc for loc in locations}
            
            # Display results
            for media in results:
                number = media.number if media.number else "N/A"
                position = media.position if media.position else "N/A"
                
                # Get box and place from location table
                if media.location_id and media.location_id in location_map:
                    box = location_map[media.location_id].box
                    place = location_map[media.location_id].place
                else:
                    box = "N/A"
                    place = "N/A"
                
                self.search_tree.insert("", tk.END, values=(
                    number,
                    media.name,
                    media.media_type,
                    box,
                    position,
                    place
                ))
            
            self.status_var.set(f"Found {len(results)} results")
            logger.debug(f"Search completed: {len(results)} results")
        except Exception as e:
            logger.error(f"Search failed: {e}")
            messagebox.showerror("Error", f"Search failed: {e}")

    def _clear_search(self) -> None:
        """Clear search filters and results."""
        try:
            # Clear results
            for item in self.search_tree.get_children():
                self.search_tree.delete(item)
            
            self.status_var.set("Search cleared")
            logger.debug("Search cleared")
        except Exception as e:
            logger.error(f"Failed to clear search: {e}")

    def _filter_by_type(self, media_type: str) -> None:
        """Filter media by type."""
        try:
            self.notebook.select(2)  # Switch to search tab
            self.search_panel.clear_filters()
            self.search_panel.type_filter_var.set(media_type)
            self._perform_search()
            self.status_var.set(f"Filtered by type: {media_type}")
        except Exception as e:
            logger.error(f"Error filtering by type: {e}")
            messagebox.showerror("Error", f"Failed to filter by type: {e}")

    def _clear_all_filters(self) -> None:
        """Clear all filters."""
        try:
            self.search_panel.clear_filters()
            
            # Clear results
            for item in self.search_tree.get_children():
                self.search_tree.delete(item)
            
            self.status_var.set("All filters cleared")
            logger.debug("All filters cleared")
        except Exception as e:
            logger.error(f"Error clearing filters: {e}")

    def _show_all_media(self) -> None:
        """Show all media."""
        try:
            self.notebook.select(0)  # Switch to media tab
            self._refresh_media_list()
            self.status_var.set("Showing all media")
        except Exception as e:
            logger.error(f"Error showing all media: {e}")
            messagebox.showerror("Error", f"Failed to show all media: {e}")

    def _import_data(self) -> None:
        """Import data from CSV file."""
        try:
            # Get existing locations for Access format mapping
            locations = self.location_service.get_all_locations()
            
            dialog = ImportDialog(
                self.root,
                on_import=self._on_import_completed,
                locations=locations
            )
            result = dialog.show()
            
            if result:
                imported_data, import_type = result
                self._process_import(imported_data, import_type)
        except Exception as e:
            logger.error(f"Error importing data: {e}")
            messagebox.showerror("Error", f"Failed to import data: {e}")

    def _process_import(self, imported_data: list, import_type: str) -> None:
        """Process imported data.
        
        For media imports, implements two-phase strategy:
        1. First pass: Create media with temporary location references
        2. Second pass: Update media with actual database location IDs
        
        After import, runs location assignment to match media to locations by Box+Place.
        """
        try:
            if import_type == "media":
                count = 0
                # First pass: Create media items with temporary location references
                for media in imported_data:
                    try:
                        self.media_service.create_media(
                            name=media.name,
                            number=media.number,
                            media_type=media.media_type,
                            category=media.category,
                            content_description=media.content_description,
                            remarks=media.remarks,
                            creation_date=media.creation_date,
                            valid_until_date=media.valid_until_date,
                            company=media.company,
                            license_code=media.license_code,
                            location_id=media.location_id,
                            position=media.position,
                        )
                        count += 1
                    except Exception as e:
                        logger.warning(f"Failed to import media: {e}")
                
                # Run location assignment after media import
                try:
                    locations = self.location_service.get_all_locations()
                    if locations:
                        assignment_results = self.media_service.assign_locations_by_box_place(locations)
                        
                        # Show assignment results dialog
                        dialog = LocationAssignmentResultsDialog(self.root, assignment_results)
                        dialog.show()
                        
                        logger.info(f"Location assignment: {assignment_results['assigned']} assigned, {assignment_results['not_found']} not found")
                except Exception as e:
                    logger.warning(f"Location assignment failed: {e}")
                
                messagebox.showinfo("Import Complete", f"Successfully imported {count} media items")
                self._refresh_media_list()
                self.status_var.set(f"Imported {count} media items")
            
            else:  # locations
                count = 0
                # Create locations and store mapping of temporary IDs to database IDs
                location_id_map = {}
                for location in imported_data:
                    try:
                        # Check if location has a temporary ID (from Access import)
                        temp_id = location.id
                        
                        # Create location in database
                        created_location = self.location_service.create_location(
                            box=location.box,
                            place=location.place,
                            detail=location.detail,
                        )
                        
                        # Store mapping if temp ID exists
                        if temp_id is not None:
                            location_id_map[temp_id] = created_location.id
                            logger.debug(f"Location ID mapping: {temp_id} -> {created_location.id}")
                        
                        count += 1
                    except Exception as e:
                        logger.warning(f"Failed to import location: {e}")
                
                # If we have location ID mappings, update media with correct location IDs
                if location_id_map:
                    try:
                        all_media = self.media_service.get_all_media()
                        for media in all_media:
                            # Check if media has a temporary location ID that needs updating
                            if media.location_id in location_id_map:
                                new_location_id = location_id_map[media.location_id]
                                self.media_service.update_media(
                                    media_id=media.id,
                                    name=media.name,
                                    number=media.number,
                                    media_type=media.media_type,
                                    category=media.category,
                                    content_description=media.content_description,
                                    remarks=media.remarks,
                                    creation_date=media.creation_date,
                                    valid_until_date=media.valid_until_date,
                                    company=media.company,
                                    license_code=media.license_code,
                                    location_id=new_location_id,
                                )
                                logger.debug(f"Updated media {media.id} location: {media.location_id} -> {new_location_id}")
                    except Exception as e:
                        logger.warning(f"Failed to update media location IDs: {e}")
                
                # Run location assignment after location import
                try:
                    all_locations = self.location_service.get_all_locations()
                    assignment_results = self.media_service.assign_locations_by_box_place(all_locations)
                    
                    # Show assignment results dialog
                    dialog = LocationAssignmentResultsDialog(self.root, assignment_results)
                    dialog.show()
                    
                    logger.info(f"Location assignment: {assignment_results['assigned']} assigned, {assignment_results['not_found']} not found")
                except Exception as e:
                    logger.warning(f"Location assignment failed: {e}")
                
                messagebox.showinfo("Import Complete", f"Successfully imported {count} locations")
                self._refresh_locations_list()
                self._refresh_media_list()  # Refresh media to show updated locations
                self.status_var.set(f"Imported {count} locations")
            
            logger.info(f"Import completed: {count} {import_type} items")
            
        except Exception as e:
            logger.error(f"Error processing import: {e}")
            messagebox.showerror("Error", f"Failed to process import: {e}")

    def _on_import_completed(self, imported_data: list, import_type: str) -> None:
        """Callback when import is completed."""
        pass

    def _export_data(self) -> None:
        """Export data to CSV file."""
        try:
            media_list = self.media_service.get_all_media()
            location_list = self.location_service.get_all_locations()
            
            dialog = ExportDialog(
                self.root,
                media_list,
                location_list,
                on_export=self._on_export_completed
            )
            result = dialog.show()
            
            if result:
                file_path, export_type, options = result
                self.status_var.set(f"Exported {options['count']} {export_type} items")
        except Exception as e:
            logger.error(f"Error exporting data: {e}")
            messagebox.showerror("Error", f"Failed to export data: {e}")

    def _on_export_completed(self, file_path: str, export_type: str, options: dict) -> None:
        """Callback when export is completed."""
        pass

    def _assign_locations(self) -> None:
        """Manually assign locations to media based on Box+Place matching."""
        try:
            # Get all locations
            locations = self.location_service.get_all_locations()
            
            if not locations:
                messagebox.showwarning(
                    "No Locations",
                    "No storage locations found in database.\n\n"
                    "Please import or create locations first."
                )
                return
            
            # Run location assignment
            assignment_results = self.media_service.assign_locations_by_box_place(locations)
            
            # Show results dialog
            dialog = LocationAssignmentResultsDialog(self.root, assignment_results)
            dialog.show()
            
            # Refresh media list to show updated locations
            self._refresh_media_list()
            self.status_var.set(f"Location assignment complete: {assignment_results['assigned']} assigned")
            
            logger.info(f"Manual location assignment: {assignment_results['assigned']} assigned, {assignment_results['not_found']} not found")
        except Exception as e:
            logger.error(f"Error assigning locations: {e}")
            messagebox.showerror("Error", f"Failed to assign locations: {e}")

    def _on_media_double_click(self, event) -> None:
        """Handle double-click on media item to jump to location."""
        try:
            # Get selected media
            selection = self.media_tree.selection()
            if not selection:
                return
            
            # Get media ID from treeview item ID
            item = selection[0]
            media_id = int(item)
            
            # Get media details
            media = self.media_service.get_media(media_id)
            
            # If media has a location, jump to locations tab and select it
            if media.location_id:
                self.notebook.select(1)  # Switch to locations tab
                
                # Find and select the location in the tree (ID stored in iid)
                location_iid = str(media.location_id)
                if location_iid in self.location_tree.get_children():
                    self.location_tree.selection_set(location_iid)
                    self.location_tree.see(location_iid)
                
                self.status_var.set(f"Jumped to location for media {media.name}")
                logger.debug(f"Jumped to location {media.location_id} for media {media_id}")
            else:
                messagebox.showinfo("No Location", f"Media '{media.name}' has no assigned location")
        except Exception as e:
            logger.error(f"Error handling media double-click: {e}")

    def _backup_database(self) -> None:
        """Backup database file."""
        try:
            from tkinter import filedialog
            from datetime import datetime
            
            # Ask user for backup location
            backup_dir = filedialog.askdirectory(title="Select backup location")
            if not backup_dir:
                return
            
            # Create backup filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_filename = f"media_archive_backup_{timestamp}.db"
            backup_path = Path(backup_dir) / backup_filename
            
            # Copy database file
            db_path = Path(DB_PATH)
            if db_path.exists():
                shutil.copy2(db_path, backup_path)
                messagebox.showinfo(
                    "Backup Successful",
                    f"Database backed up to:\n{backup_path}"
                )
                self.status_var.set(f"Database backed up to {backup_path}")
                logger.info(f"Database backed up to {backup_path}")
            else:
                messagebox.showerror("Backup Error", "Database file not found")
        except Exception as e:
            logger.error(f"Error backing up database: {e}")
            messagebox.showerror("Error", f"Failed to backup database: {e}")

    def run(self) -> None:
        """Start the application."""
        logger.info("Starting application")
        self.root.mainloop()

    def close(self) -> None:
        """Close the application."""
        try:
            self.db.close()
            logger.info("Application closed")
        except Exception as e:
            logger.error(f"Error closing application: {e}")

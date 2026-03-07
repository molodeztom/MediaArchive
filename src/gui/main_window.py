"""Main application window for Media Archive Manager.

This module provides the main GUI window with menu bar, toolbar, and main content area.
"""

import logging
import tkinter as tk
from tkinter import ttk, messagebox
from pathlib import Path

from data.database import Database
from business.location_service import LocationService
from business.media_service import MediaService
from utils.config import APP_NAME, APP_VERSION, DB_PATH, WINDOW_WIDTH, WINDOW_HEIGHT
from gui.dialogs import AddMediaDialog, EditMediaDialog, DeleteConfirmDialog

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
        
        # Initialize database and services
        self._init_database()
        
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
        file_menu.add_command(label="Exit", command=self.root.quit)
        
        # Edit menu
        edit_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Edit", menu=edit_menu)
        edit_menu.add_command(label="Preferences", command=self._show_preferences)
        
        # View menu
        view_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="View", menu=view_menu)
        view_menu.add_command(label="Refresh", command=self._refresh_view)
        view_menu.add_separator()
        view_menu.add_command(label="Statistics", command=self._show_statistics)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self._show_about)
        
        logger.debug("Menu bar created")

    def _create_toolbar(self) -> None:
        """Create toolbar with action buttons."""
        toolbar = ttk.Frame(self.root)
        toolbar.pack(side=tk.TOP, fill=tk.X, padx=2, pady=2)
        
        # Buttons
        ttk.Button(toolbar, text="Add Media", command=self._add_media).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="Edit Media", command=self._edit_media).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="Delete Media", command=self._delete_media).pack(side=tk.LEFT, padx=2)
        ttk.Separator(toolbar, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=5)
        ttk.Button(toolbar, text="Locations", command=self._show_locations).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="Expired", command=self._show_expired).pack(side=tk.LEFT, padx=2)
        
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
        columns = ("ID", "Name", "Type", "Location", "Expires")
        self.media_tree = ttk.Treeview(frame, columns=columns, height=20)
        self.media_tree.column("#0", width=0, stretch=tk.NO)
        self.media_tree.column("ID", anchor=tk.W, width=50)
        self.media_tree.column("Name", anchor=tk.W, width=200)
        self.media_tree.column("Type", anchor=tk.W, width=100)
        self.media_tree.column("Location", anchor=tk.W, width=150)
        self.media_tree.column("Expires", anchor=tk.W, width=100)
        
        self.media_tree.heading("#0", text="", anchor=tk.W)
        self.media_tree.heading("ID", text="ID", anchor=tk.W)
        self.media_tree.heading("Name", text="Name", anchor=tk.W)
        self.media_tree.heading("Type", text="Type", anchor=tk.W)
        self.media_tree.heading("Location", text="Location", anchor=tk.W)
        self.media_tree.heading("Expires", text="Expires", anchor=tk.W)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=self.media_tree.yview)
        self.media_tree.configure(yscroll=scrollbar.set)
        
        self.media_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Load media
        self._refresh_media_list()
        
        logger.debug("Media tab created")

    def _create_locations_tab(self) -> None:
        """Create location management tab."""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Locations")
        
        # Create treeview for locations
        columns = ("ID", "Box", "Place", "Detail")
        self.location_tree = ttk.Treeview(frame, columns=columns, height=20)
        self.location_tree.column("#0", width=0, stretch=tk.NO)
        self.location_tree.column("ID", anchor=tk.W, width=50)
        self.location_tree.column("Box", anchor=tk.W, width=150)
        self.location_tree.column("Place", anchor=tk.W, width=150)
        self.location_tree.column("Detail", anchor=tk.W, width=200)
        
        self.location_tree.heading("#0", text="", anchor=tk.W)
        self.location_tree.heading("ID", text="ID", anchor=tk.W)
        self.location_tree.heading("Box", text="Box", anchor=tk.W)
        self.location_tree.heading("Place", text="Place", anchor=tk.W)
        self.location_tree.heading("Detail", text="Detail", anchor=tk.W)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=self.location_tree.yview)
        self.location_tree.configure(yscroll=scrollbar.set)
        
        self.location_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Load locations
        self._refresh_locations_list()
        
        logger.debug("Locations tab created")

    def _create_search_tab(self) -> None:
        """Create search and filter tab."""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Search")
        
        # Search frame
        search_frame = ttk.LabelFrame(frame, text="Search Media", padding=10)
        search_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(search_frame, text="Search by name:").pack(side=tk.LEFT, padx=5)
        self.search_entry = ttk.Entry(search_frame, width=30)
        self.search_entry.pack(side=tk.LEFT, padx=5)
        ttk.Button(search_frame, text="Search", command=self._perform_search).pack(side=tk.LEFT, padx=5)
        
        # Results frame
        results_frame = ttk.LabelFrame(frame, text="Search Results", padding=10)
        results_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        columns = ("ID", "Name", "Type", "Location")
        self.search_tree = ttk.Treeview(results_frame, columns=columns, height=15)
        self.search_tree.column("#0", width=0, stretch=tk.NO)
        self.search_tree.column("ID", anchor=tk.W, width=50)
        self.search_tree.column("Name", anchor=tk.W, width=200)
        self.search_tree.column("Type", anchor=tk.W, width=100)
        self.search_tree.column("Location", anchor=tk.W, width=150)
        
        self.search_tree.heading("#0", text="", anchor=tk.W)
        self.search_tree.heading("ID", text="ID", anchor=tk.W)
        self.search_tree.heading("Name", text="Name", anchor=tk.W)
        self.search_tree.heading("Type", text="Type", anchor=tk.W)
        self.search_tree.heading("Location", text="Location", anchor=tk.W)
        
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

    def _refresh_media_list(self) -> None:
        """Refresh media list in media tab."""
        try:
            # Clear existing items
            for item in self.media_tree.get_children():
                self.media_tree.delete(item)
            
            # Load media
            media_list = self.media_service.get_all_media()
            for media in media_list:
                expires = media.valid_until_date.isoformat() if media.valid_until_date else "N/A"
                self.media_tree.insert("", tk.END, values=(
                    media.id,
                    media.name,
                    media.media_type,
                    media.location_id or "N/A",
                    expires
                ))
            
            self.status_var.set(f"Loaded {len(media_list)} media items")
            logger.debug(f"Refreshed media list: {len(media_list)} items")
        except Exception as e:
            logger.error(f"Failed to refresh media list: {e}")
            messagebox.showerror("Error", f"Failed to load media: {e}")

    def _refresh_locations_list(self) -> None:
        """Refresh locations list in locations tab."""
        try:
            # Clear existing items
            for item in self.location_tree.get_children():
                self.location_tree.delete(item)
            
            # Load locations
            locations = self.location_service.get_all_locations()
            for loc in locations:
                self.location_tree.insert("", tk.END, values=(
                    loc.id,
                    loc.box,
                    loc.place,
                    loc.detail or ""
                ))
            
            self.status_var.set(f"Loaded {len(locations)} locations")
            logger.debug(f"Refreshed locations list: {len(locations)} items")
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
            
            # Create and show dialog
            dialog = AddMediaDialog(self.root, locations, on_save=self._on_media_added)
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
                media_type=media.media_type,
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
            
            # Get media ID from first column
            item = selection[0]
            values = self.media_tree.item(item, "values")
            media_id = int(values[0])
            
            # Get media details
            media = self.media_service.get_media(media_id)
            
            # Get available locations
            locations = self.location_service.get_all_locations()
            
            # Create and show dialog
            dialog = EditMediaDialog(self.root, media, locations, on_save=self._on_media_updated)
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
                media_type=media.media_type,
                content_description=media.content_description,
                remarks=media.remarks,
                creation_date=media.creation_date,
                valid_until_date=media.valid_until_date,
                company=media.company,
                license_code=media.license_code,
                location_id=media.location_id,
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
            
            # Get media ID from first column
            item = selection[0]
            values = self.media_tree.item(item, "values")
            media_id = int(values[0])
            
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

    def _show_locations(self) -> None:
        """Show locations tab."""
        self.notebook.select(1)

    def _show_expired(self) -> None:
        """Show expired media."""
        try:
            expired = self.media_service.get_expired_media()
            messagebox.showinfo("Expired Media", f"Found {len(expired)} expired media items")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to get expired media: {e}")

    def _show_statistics(self) -> None:
        """Show media statistics."""
        try:
            stats = self.media_service.get_media_statistics()
            message = f"""
Media Statistics:
- Total media: {stats['total_media']}
- Expired: {stats['expired_media']}
- Expiring soon: {stats['expiring_soon']}
- With location: {stats['media_with_location']}
- Without location: {stats['media_without_location']}

By type:
"""
            for media_type, count in stats['media_by_type'].items():
                message += f"  {media_type}: {count}\n"
            
            messagebox.showinfo("Statistics", message)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to get statistics: {e}")

    def _show_preferences(self) -> None:
        """Show preferences dialog."""
        messagebox.showinfo("Preferences", "Preferences dialog coming soon")

    def _show_about(self) -> None:
        """Show about dialog."""
        messagebox.showinfo(
            "About",
            f"{APP_NAME} v{APP_VERSION}\n\n"
            "Local desktop application for managing physical media inventory.\n\n"
            "Built with Python and tkinter"
        )

    def _perform_search(self) -> None:
        """Perform search based on search entry."""
        query = self.search_entry.get()
        if not query:
            messagebox.showwarning("Search", "Please enter a search query")
            return
        
        try:
            # Clear existing results
            for item in self.search_tree.get_children():
                self.search_tree.delete(item)
            
            # Search
            results = self.media_service.search_media_by_name(query)
            for media in results:
                self.search_tree.insert("", tk.END, values=(
                    media.id,
                    media.name,
                    media.media_type,
                    media.location_id or "N/A"
                ))
            
            self.status_var.set(f"Found {len(results)} results")
        except Exception as e:
            messagebox.showerror("Error", f"Search failed: {e}")

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

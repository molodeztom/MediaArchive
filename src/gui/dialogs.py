"""Dialog windows for Media Archive Manager GUI.

This module provides dialog windows for adding, editing, and deleting media items
with form validation and error handling.

History:
20260307  V1.0: Initial implementation with media dialogs
20260307  V1.1: Added location management dialogs
20260309  V1.2: Added LocationAssignmentResultsDialog for import results
20260309  V1.3: Increased DeleteConfirmDialog height to show buttons
20260309  V1.4: Added position and box fields to media dialogs
20260309  V1.5: Fixed EditMediaDialog grid layout - box/position now in correct rows
20260309  V1.6: Removed Storage Location dropdown - location determined by Box selection
20260309  V1.7: Pre-populate box dropdown in EditMediaDialog from location table via location_id
20260309  V1.8: Added read-only Place field to EditMediaDialog that updates with Box selection
20260309  V1.9: Changed Category field to editable combobox with existing values
20260309  V1.10: Added auto-numbering and DD.MM.YYYY date format support
20260309  V1.11: Updated date parsing to use parse_date() for DD.MM.YYYY format
20260309  V1.12: Updated DeleteConfirmDialog to explain soft delete behavior
"""

import logging
import tkinter as tk
from datetime import date
from tkinter import ttk, messagebox
from typing import Optional, Callable
from pathlib import Path
import sys

# Add src directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from models.media import Media
from models.location import StorageLocation
from models.enums import MediaType
from utils.exceptions import ValidationError, NotFoundError
from utils.config import MAX_BOX_LENGTH, MAX_PLACE_LENGTH, MAX_DETAIL_LENGTH
from utils.date_utils import format_date, parse_date

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


class AddMediaDialog(BaseDialog):
    """Dialog for adding new media items.
    
    Provides form fields for all media attributes with validation.
    """

    def __init__(
        self,
        parent: tk.Widget,
        locations: list[StorageLocation],
        categories: list[str],
        on_save: Optional[Callable[[Media], None]] = None,
        media_service = None,
    ) -> None:
        """Initialize add media dialog.
        
        Args:
            parent: Parent window.
            locations: List of available storage locations.
            categories: List of existing categories for dropdown.
            on_save: Optional callback when media is saved.
            media_service: Optional MediaService for auto-numbering.
        """
        super().__init__(parent, "Add New Media")
        self.locations = locations
        self.categories = categories
        self.on_save = on_save
        self.media_service = media_service
        self.result = None
        
        # Create form
        self._create_form()
        
        logger.debug("AddMediaDialog initialized")

    def _create_form(self) -> None:
        """Create form fields."""
        # Main frame with padding
        main_frame = ttk.Frame(self, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Name field
        ttk.Label(main_frame, text="Name *").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.name_var = tk.StringVar()
        name_entry = ttk.Entry(main_frame, textvariable=self.name_var, width=40)
        name_entry.grid(row=0, column=1, sticky=tk.EW, pady=5)
        
        # Number field (auto-populated if media_service provided)
        ttk.Label(main_frame, text="Number").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.number_var = tk.StringVar()
        # Auto-populate next number if media_service is available
        if self.media_service:
            try:
                next_num = self.media_service.get_next_number()
                self.number_var.set(next_num)
                logger.debug(f"Auto-populated number: {next_num}")
            except Exception as e:
                logger.warning(f"Failed to auto-populate number: {e}")
        number_entry = ttk.Entry(main_frame, textvariable=self.number_var, width=40)
        number_entry.grid(row=1, column=1, sticky=tk.EW, pady=5)
        
        # Box field (from storage_location table)
        ttk.Label(main_frame, text="Box").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.box_var = tk.StringVar()
        box_combo = ttk.Combobox(
            main_frame,
            textvariable=self.box_var,
            values=[loc.box for loc in self.locations],
            state="readonly",
            width=37
        )
        box_combo.grid(row=2, column=1, sticky=tk.EW, pady=5)
        
        # Position field (number within box)
        ttk.Label(main_frame, text="Position").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.position_var = tk.StringVar()
        position_entry = ttk.Entry(main_frame, textvariable=self.position_var, width=40)
        position_entry.grid(row=3, column=1, sticky=tk.EW, pady=5)
        
        # Media Type field
        ttk.Label(main_frame, text="Media Type").grid(row=4, column=0, sticky=tk.W, pady=5)
        self.media_type_var = tk.StringVar()
        type_combo = ttk.Combobox(
            main_frame,
            textvariable=self.media_type_var,
            values=MediaType.get_all_values(),
            state="readonly",
            width=37
        )
        type_combo.grid(row=4, column=1, sticky=tk.EW, pady=5)
        
        # Category field (editable combobox)
        ttk.Label(main_frame, text="Category").grid(row=5, column=0, sticky=tk.W, pady=5)
        self.category_var = tk.StringVar()
        category_combo = ttk.Combobox(
            main_frame,
            textvariable=self.category_var,
            values=self.categories,
            state="normal",  # Allows typing new values
            width=37
        )
        category_combo.grid(row=5, column=1, sticky=tk.EW, pady=5)
        
        # Company field
        ttk.Label(main_frame, text="Company").grid(row=6, column=0, sticky=tk.W, pady=5)
        self.company_var = tk.StringVar()
        company_entry = ttk.Entry(main_frame, textvariable=self.company_var, width=40)
        company_entry.grid(row=6, column=1, sticky=tk.EW, pady=5)
        
        # License Code field
        ttk.Label(main_frame, text="License Code").grid(row=7, column=0, sticky=tk.W, pady=5)
        self.license_var = tk.StringVar()
        license_entry = ttk.Entry(main_frame, textvariable=self.license_var, width=40)
        license_entry.grid(row=7, column=1, sticky=tk.EW, pady=5)
        
        # Creation Date field
        ttk.Label(main_frame, text="Creation Date").grid(row=8, column=0, sticky=tk.W, pady=5)
        self.creation_date_var = tk.StringVar()
        creation_date_entry = ttk.Entry(
            main_frame,
            textvariable=self.creation_date_var,
            width=40
        )
        creation_date_entry.grid(row=8, column=1, sticky=tk.EW, pady=5)
        ttk.Label(main_frame, text="(DD.MM.YYYY)", font=("TkDefaultFont", 8)).grid(
            row=8, column=2, sticky=tk.W, padx=5
        )
        
        # Valid Until Date field
        ttk.Label(main_frame, text="Valid Until Date").grid(row=9, column=0, sticky=tk.W, pady=5)
        self.valid_until_var = tk.StringVar()
        valid_until_entry = ttk.Entry(
            main_frame,
            textvariable=self.valid_until_var,
            width=40
        )
        valid_until_entry.grid(row=9, column=1, sticky=tk.EW, pady=5)
        ttk.Label(main_frame, text="(DD.MM.YYYY)", font=("TkDefaultFont", 8)).grid(
            row=9, column=2, sticky=tk.W, padx=5
        )
        
        # Content Description field
        ttk.Label(main_frame, text="Content Description").grid(row=10, column=0, sticky=tk.NW, pady=5)
        self.content_var = tk.StringVar()
        content_text = tk.Text(main_frame, height=4, width=40)
        content_text.grid(row=10, column=1, sticky=tk.EW, pady=5)
        self.content_text = content_text
        
        # Remarks field
        ttk.Label(main_frame, text="Remarks").grid(row=11, column=0, sticky=tk.NW, pady=5)
        self.remarks_var = tk.StringVar()
        remarks_text = tk.Text(main_frame, height=4, width=40)
        remarks_text.grid(row=11, column=1, sticky=tk.EW, pady=5)
        self.remarks_text = remarks_text
        
        # Configure grid weights
        main_frame.columnconfigure(1, weight=1)
        
        # Buttons frame
        button_frame = ttk.Frame(self)
        button_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Button(button_frame, text="Save", command=self._save).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=self._cancel).pack(side=tk.LEFT, padx=5)
        
        # Set minimum size - adjusted for fields
        self.geometry("500x700")

    def _save(self) -> None:
        """Save media and close dialog."""
        try:
            # Get values
            name = self.name_var.get().strip()
            number = self.number_var.get().strip() or None
            box = self.box_var.get().strip() or None
            position = self.position_var.get().strip() or None
            media_type = self.media_type_var.get().strip()
            category_value = self.category_var.get().strip() or None
            company = self.company_var.get().strip() or None
            license_code = self.license_var.get().strip() or None
            creation_date_str = self.creation_date_var.get().strip() or None
            valid_until_str = self.valid_until_var.get().strip() or None
            content_desc = self.content_text.get("1.0", tk.END).strip() or None
            remarks = self.remarks_text.get("1.0", tk.END).strip() or None
            
            # Validate required fields
            if not name:
                messagebox.showwarning("Validation Error", "Media name is required")
                return
            
            if not media_type:
                media_type = "Unknown"
            
            # Parse dates
            creation_date = None
            if creation_date_str:
                try:
                    creation_date = parse_date(creation_date_str)
                except ValueError as e:
                    messagebox.showerror("Date Error", str(e))
                    return
            
            valid_until_date = None
            if valid_until_str:
                try:
                    valid_until_date = parse_date(valid_until_str)
                except ValueError as e:
                    messagebox.showerror("Date Error", str(e))
                    return
            
            # Determine location_id from box selection
            location_id = None
            if box:
                # Find location with matching box
                for loc in self.locations:
                    if loc.box == box:
                        location_id = loc.id
                        break
            
            # Create media object
            media = Media(
                name=name,
                number=number,
                media_type=media_type,
                category=category_value,
                company=company,
                license_code=license_code,
                creation_date=creation_date,
                valid_until_date=valid_until_date,
                content_description=content_desc,
                remarks=remarks,
                location_id=location_id,
                box=box,
                position=position,
            )
            
            self.result = media
            
            if self.on_save:
                self.on_save(media)
            
            logger.info(f"Media added: {media}")
            self.destroy()
            
        except ValidationError as e:
            messagebox.showerror("Validation Error", str(e))
            logger.warning(f"Validation error in AddMediaDialog: {e}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save media: {e}")
            logger.error(f"Error in AddMediaDialog._save: {e}")

    def _cancel(self) -> None:
        """Cancel and close dialog."""
        self.result = None
        self.destroy()


class EditMediaDialog(BaseDialog):
    """Dialog for editing existing media items.
    
    Provides form fields pre-populated with current media data.
    """

    def __init__(
        self,
        parent: tk.Widget,
        media: Media,
        locations: list[StorageLocation],
        categories: list[str],
        on_save: Optional[Callable[[Media], None]] = None,
    ) -> None:
        """Initialize edit media dialog.
        
        Args:
            parent: Parent window.
            media: Media object to edit.
            locations: List of available storage locations.
            categories: List of existing categories for dropdown.
            on_save: Optional callback when media is saved.
        """
        super().__init__(parent, f"Edit Media: {media.name}")
        self.media = media
        self.locations = locations
        self.categories = categories
        self.on_save = on_save
        self.result = None
        
        # Create form
        self._create_form()
        
        logger.debug(f"EditMediaDialog initialized for media: {media.id}")

    def _create_form(self) -> None:
        """Create form fields with existing data."""
        # Main frame with padding
        main_frame = ttk.Frame(self, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Name field
        ttk.Label(main_frame, text="Name *").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.name_var = tk.StringVar(value=self.media.name)
        name_entry = ttk.Entry(main_frame, textvariable=self.name_var, width=40)
        name_entry.grid(row=0, column=1, sticky=tk.EW, pady=5)
        
        # Number field
        ttk.Label(main_frame, text="Number").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.number_var = tk.StringVar(value=self.media.number or "")
        number_entry = ttk.Entry(main_frame, textvariable=self.number_var, width=40)
        number_entry.grid(row=1, column=1, sticky=tk.EW, pady=5)
        
        # Box field (from storage_location table)
        # Pre-populate with box value from location table via location_id
        ttk.Label(main_frame, text="Box").grid(row=2, column=0, sticky=tk.W, pady=5)
        current_box = ""
        current_place = ""
        if self.media.location_id:
            # Find the location with matching ID and get its box and place values
            for loc in self.locations:
                if loc.id == self.media.location_id:
                    current_box = loc.box
                    current_place = loc.place
                    break
        self.box_var = tk.StringVar(value=current_box)
        box_combo = ttk.Combobox(
            main_frame,
            textvariable=self.box_var,
            values=[loc.box for loc in self.locations],
            state="readonly",
            width=37
        )
        box_combo.grid(row=2, column=1, sticky=tk.EW, pady=5)
        box_combo.bind("<<ComboboxSelected>>", self._on_box_changed)
        
        # Place field (read-only, shows place from location table)
        ttk.Label(main_frame, text="Place").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.place_display_var = tk.StringVar(value=current_place)
        place_entry = ttk.Entry(main_frame, textvariable=self.place_display_var, state="readonly", width=40)
        place_entry.grid(row=3, column=1, sticky=tk.EW, pady=5)
        
        # Position field (number within box)
        ttk.Label(main_frame, text="Position").grid(row=4, column=0, sticky=tk.W, pady=5)
        self.position_var = tk.StringVar(value=self.media.position or "")
        position_entry = ttk.Entry(main_frame, textvariable=self.position_var, width=40)
        position_entry.grid(row=4, column=1, sticky=tk.EW, pady=5)
        
        # Media Type field
        ttk.Label(main_frame, text="Media Type").grid(row=5, column=0, sticky=tk.W, pady=5)
        self.media_type_var = tk.StringVar(value=self.media.media_type)
        type_combo = ttk.Combobox(
            main_frame,
            textvariable=self.media_type_var,
            values=MediaType.get_all_values(),
            state="readonly",
            width=37
        )
        type_combo.grid(row=5, column=1, sticky=tk.EW, pady=5)
        
        # Category field (editable combobox)
        ttk.Label(main_frame, text="Category").grid(row=6, column=0, sticky=tk.W, pady=5)
        self.category_var = tk.StringVar(value=self.media.category or "")
        category_combo = ttk.Combobox(
            main_frame,
            textvariable=self.category_var,
            values=self.categories,
            state="normal",  # Allows typing new values
            width=37
        )
        category_combo.grid(row=6, column=1, sticky=tk.EW, pady=5)
        
        # Company field
        ttk.Label(main_frame, text="Company").grid(row=7, column=0, sticky=tk.W, pady=5)
        self.company_var = tk.StringVar(value=self.media.company or "")
        company_entry = ttk.Entry(main_frame, textvariable=self.company_var, width=40)
        company_entry.grid(row=7, column=1, sticky=tk.EW, pady=5)
        
        # License Code field
        ttk.Label(main_frame, text="License Code").grid(row=8, column=0, sticky=tk.W, pady=5)
        self.license_var = tk.StringVar(value=self.media.license_code or "")
        license_entry = ttk.Entry(main_frame, textvariable=self.license_var, width=40)
        license_entry.grid(row=8, column=1, sticky=tk.EW, pady=5)
        
        # Creation Date field
        ttk.Label(main_frame, text="Creation Date").grid(row=9, column=0, sticky=tk.W, pady=5)
        creation_date_str = format_date(self.media.creation_date) if self.media.creation_date else ""
        self.creation_date_var = tk.StringVar(value=creation_date_str)
        creation_date_entry = ttk.Entry(
            main_frame,
            textvariable=self.creation_date_var,
            width=40
        )
        creation_date_entry.grid(row=9, column=1, sticky=tk.EW, pady=5)
        ttk.Label(main_frame, text="(DD.MM.YYYY)", font=("TkDefaultFont", 8)).grid(
            row=9, column=2, sticky=tk.W, padx=5
        )
        
        # Valid Until Date field
        ttk.Label(main_frame, text="Valid Until Date").grid(row=10, column=0, sticky=tk.W, pady=5)
        valid_until_str = format_date(self.media.valid_until_date) if self.media.valid_until_date else ""
        self.valid_until_var = tk.StringVar(value=valid_until_str)
        valid_until_entry = ttk.Entry(
            main_frame,
            textvariable=self.valid_until_var,
            width=40
        )
        valid_until_entry.grid(row=10, column=1, sticky=tk.EW, pady=5)
        ttk.Label(main_frame, text="(DD.MM.YYYY)", font=("TkDefaultFont", 8)).grid(
            row=10, column=2, sticky=tk.W, padx=5
        )
        
        # Content Description field
        ttk.Label(main_frame, text="Content Description").grid(row=11, column=0, sticky=tk.NW, pady=5)
        content_text = tk.Text(main_frame, height=4, width=40)
        content_text.insert("1.0", self.media.content_description or "")
        content_text.grid(row=11, column=1, sticky=tk.EW, pady=5)
        self.content_text = content_text
        
        # Remarks field
        ttk.Label(main_frame, text="Remarks").grid(row=12, column=0, sticky=tk.NW, pady=5)
        remarks_text = tk.Text(main_frame, height=4, width=40)
        remarks_text.insert("1.0", self.media.remarks or "")
        remarks_text.grid(row=12, column=1, sticky=tk.EW, pady=5)
        self.remarks_text = remarks_text
        
        # Configure grid weights
        main_frame.columnconfigure(1, weight=1)
        
        # Buttons frame
        button_frame = ttk.Frame(self)
        button_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Button(button_frame, text="Save", command=self._save).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=self._cancel).pack(side=tk.LEFT, padx=5)
        
        # Set minimum size - adjusted for fields
        self.geometry("500x750")

    def _on_box_changed(self, event=None) -> None:
        """Update Place field when Box selection changes."""
        try:
            selected_box = self.box_var.get()
            # Find the location with matching box and update place display
            for loc in self.locations:
                if loc.box == selected_box:
                    self.place_display_var.set(loc.place)
                    return
            # If no match found, clear place
            self.place_display_var.set("")
        except Exception as e:
            logger.error(f"Error updating place display: {e}")

    def _save(self) -> None:
        """Save media changes and close dialog."""
        try:
            # Get values
            name = self.name_var.get().strip()
            number = self.number_var.get().strip() or None
            box = self.box_var.get().strip() or None
            position = self.position_var.get().strip() or None
            media_type = self.media_type_var.get().strip()
            category_value = self.category_var.get().strip() or None
            company = self.company_var.get().strip() or None
            license_code = self.license_var.get().strip() or None
            creation_date_str = self.creation_date_var.get().strip() or None
            valid_until_str = self.valid_until_var.get().strip() or None
            content_desc = self.content_text.get("1.0", tk.END).strip() or None
            remarks = self.remarks_text.get("1.0", tk.END).strip() or None
            
            # Validate required fields
            if not name:
                messagebox.showwarning("Validation Error", "Media name is required")
                return
            
            if not media_type:
                media_type = "Unknown"
            
            # Parse dates
            creation_date = None
            if creation_date_str:
                try:
                    creation_date = parse_date(creation_date_str)
                except ValueError as e:
                    messagebox.showerror("Date Error", str(e))
                    return
            
            valid_until_date = None
            if valid_until_str:
                try:
                    valid_until_date = parse_date(valid_until_str)
                except ValueError as e:
                    messagebox.showerror("Date Error", str(e))
                    return
            
            # Determine location_id from box selection
            location_id = None
            if box:
                # Find location with matching box
                for loc in self.locations:
                    if loc.box == box:
                        location_id = loc.id
                        break
            
            # Update media object
            self.media.name = name
            self.media.number = number
            self.media.box = box
            self.media.position = position
            self.media.media_type = media_type
            self.media.category = category_value
            self.media.company = company
            self.media.license_code = license_code
            self.media.creation_date = creation_date
            self.media.valid_until_date = valid_until_date
            self.media.content_description = content_desc
            self.media.remarks = remarks
            self.media.location_id = location_id
            
            self.result = self.media
            
            if self.on_save:
                self.on_save(self.media)
            
            logger.info(f"Media updated: {self.media.id}")
            self.destroy()
            
        except ValidationError as e:
            messagebox.showerror("Validation Error", str(e))
            logger.warning(f"Validation error in EditMediaDialog: {e}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save media: {e}")
            logger.error(f"Error in EditMediaDialog._save: {e}")

    def _cancel(self) -> None:
        """Cancel and close dialog."""
        self.result = None
        self.destroy()


class DeleteConfirmDialog(BaseDialog):
    """Dialog for confirming media deletion.
    
    Shows media details and asks for confirmation before deletion.
    """

    def __init__(
        self,
        parent: tk.Widget,
        media: Media,
        on_confirm: Optional[Callable[[Media], None]] = None,
    ) -> None:
        """Initialize delete confirmation dialog.
        
        Args:
            parent: Parent window.
            media: Media object to delete.
            on_confirm: Optional callback when deletion is confirmed.
        """
        super().__init__(parent, "Confirm Delete")
        self.media = media
        self.on_confirm = on_confirm
        self.result = None
        
        # Create content
        self._create_content()
        
        logger.debug(f"DeleteConfirmDialog initialized for media: {media.id}")

    def _create_content(self) -> None:
        """Create dialog content."""
        # Main frame with padding
        main_frame = ttk.Frame(self, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Info message about soft delete
        info_frame = ttk.Frame(main_frame)
        info_frame.pack(fill=tk.X, pady=(0, 15))
        
        info_label = ttk.Label(
            info_frame,
            text="ℹ️ Soft Delete: The item will be hidden but can be restored later.",
            foreground="blue",
            font=("Arial", 9, "italic")
        )
        info_label.pack(anchor=tk.W)
        
        # Media details
        details_frame = ttk.LabelFrame(main_frame, text="Media Details", padding=10)
        details_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
        
        ttk.Label(details_frame, text=f"Name: {self.media.name}", font=("Arial", 10, "bold")).pack(anchor=tk.W, pady=2)
        ttk.Label(details_frame, text=f"Type: {self.media.media_type}").pack(anchor=tk.W, pady=2)
        if self.media.number:
            ttk.Label(details_frame, text=f"Number: {self.media.number}").pack(anchor=tk.W, pady=2)
        
        # Warning message
        warning_label = ttk.Label(
            main_frame,
            text="Delete this media item?\n\nYou can restore it later from 'Show Deleted' view.",
            justify=tk.LEFT
        )
        warning_label.pack(pady=(0, 15))
        
        # Buttons frame
        button_frame = ttk.Frame(self)
        button_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Button(button_frame, text="Delete", command=self._confirm).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=self._cancel).pack(side=tk.LEFT, padx=5)
        
        # Set size - increased height to ensure buttons are visible
        self.geometry("400x380")

    def _confirm(self) -> None:
        """Confirm deletion and close dialog."""
        try:
            self.result = self.media
            
            if self.on_confirm:
                self.on_confirm(self.media)
            
            logger.info(f"Media deletion confirmed: {self.media.id}")
            self.destroy()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to delete media: {e}")
            logger.error(f"Error in DeleteConfirmDialog._confirm: {e}")

    def _cancel(self) -> None:
        """Cancel and close dialog."""
        self.result = None
        self.destroy()


class AddLocationDialog(BaseDialog):
    """Dialog for adding new storage locations.
    
    Provides form fields for location attributes with validation.
    """

    def __init__(
        self,
        parent: tk.Widget,
        on_save: Optional[Callable[[StorageLocation], None]] = None,
    ) -> None:
        """Initialize add location dialog.
        
        Args:
            parent: Parent window.
            on_save: Optional callback when location is saved.
        """
        super().__init__(parent, "Add New Location")
        self.on_save = on_save
        self.result = None
        
        # Create form
        self._create_form()
        
        logger.debug("AddLocationDialog initialized")

    def _create_form(self) -> None:
        """Create form fields."""
        # Main frame with padding
        main_frame = ttk.Frame(self, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Box field
        ttk.Label(main_frame, text="Box *").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.box_var = tk.StringVar()
        box_entry = ttk.Entry(main_frame, textvariable=self.box_var, width=40)
        box_entry.grid(row=0, column=1, sticky=tk.EW, pady=5)
        
        # Place field
        ttk.Label(main_frame, text="Place").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.place_var = tk.StringVar()
        place_entry = ttk.Entry(main_frame, textvariable=self.place_var, width=40)
        place_entry.grid(row=1, column=1, sticky=tk.EW, pady=5)
        
        # Detail field
        ttk.Label(main_frame, text="Detail").grid(row=2, column=0, sticky=tk.NW, pady=5)
        self.detail_var = tk.StringVar()
        detail_text = tk.Text(main_frame, height=4, width=40)
        detail_text.grid(row=2, column=1, sticky=tk.EW, pady=5)
        self.detail_text = detail_text
        
        # Configure grid weights
        main_frame.columnconfigure(1, weight=1)
        
        # Buttons frame
        button_frame = ttk.Frame(self)
        button_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Button(button_frame, text="Save", command=self._save).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=self._cancel).pack(side=tk.LEFT, padx=5)
        
        # Set minimum size
        self.geometry("400x250")

    def _save(self) -> None:
        """Save location and close dialog."""
        try:
            # Get values
            box = self.box_var.get().strip()
            place = self.place_var.get().strip()
            detail = self.detail_text.get("1.0", tk.END).strip() or None
            
            # Validate required fields
            if not box:
                messagebox.showwarning("Validation Error", "Box name is required")
                return
            
            # Place is optional - set to empty string if not provided
            if not place:
                place = ""
            
            # Validate lengths
            if len(box) > MAX_BOX_LENGTH:
                messagebox.showerror("Validation Error", f"Box name exceeds {MAX_BOX_LENGTH} characters")
                return
            
            if len(place) > MAX_PLACE_LENGTH:
                messagebox.showerror("Validation Error", f"Place exceeds {MAX_PLACE_LENGTH} characters")
                return
            
            if detail and len(detail) > MAX_DETAIL_LENGTH:
                messagebox.showerror("Validation Error", f"Detail exceeds {MAX_DETAIL_LENGTH} characters")
                return
            
            # Create location object
            location = StorageLocation(
                box=box,
                place=place,
                detail=detail,
            )
            
            self.result = location
            
            if self.on_save:
                self.on_save(location)
            
            logger.info(f"Location added: {location}")
            self.destroy()
            
        except ValidationError as e:
            messagebox.showerror("Validation Error", str(e))
            logger.warning(f"Validation error in AddLocationDialog: {e}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save location: {e}")
            logger.error(f"Error in AddLocationDialog._save: {e}")

    def _cancel(self) -> None:
        """Cancel and close dialog."""
        self.result = None
        self.destroy()


class EditLocationDialog(BaseDialog):
    """Dialog for editing existing storage locations.
    
    Provides form fields pre-populated with current location data.
    """

    def __init__(
        self,
        parent: tk.Widget,
        location: StorageLocation,
        on_save: Optional[Callable[[StorageLocation], None]] = None,
    ) -> None:
        """Initialize edit location dialog.
        
        Args:
            parent: Parent window.
            location: Location object to edit.
            on_save: Optional callback when location is saved.
        """
        super().__init__(parent, f"Edit Location: {location.box}")
        self.location = location
        self.on_save = on_save
        self.result = None
        
        # Create form
        self._create_form()
        
        logger.debug(f"EditLocationDialog initialized for location: {location.id}")

    def _create_form(self) -> None:
        """Create form fields with existing data."""
        # Main frame with padding
        main_frame = ttk.Frame(self, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Box field
        ttk.Label(main_frame, text="Box *").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.box_var = tk.StringVar(value=self.location.box)
        box_entry = ttk.Entry(main_frame, textvariable=self.box_var, width=40)
        box_entry.grid(row=0, column=1, sticky=tk.EW, pady=5)
        
        # Place field
        ttk.Label(main_frame, text="Place").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.place_var = tk.StringVar(value=self.location.place)
        place_entry = ttk.Entry(main_frame, textvariable=self.place_var, width=40)
        place_entry.grid(row=1, column=1, sticky=tk.EW, pady=5)
        
        # Detail field
        ttk.Label(main_frame, text="Detail").grid(row=2, column=0, sticky=tk.NW, pady=5)
        detail_text = tk.Text(main_frame, height=4, width=40)
        detail_text.insert("1.0", self.location.detail or "")
        detail_text.grid(row=2, column=1, sticky=tk.EW, pady=5)
        self.detail_text = detail_text
        
        # Configure grid weights
        main_frame.columnconfigure(1, weight=1)
        
        # Buttons frame
        button_frame = ttk.Frame(self)
        button_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Button(button_frame, text="Save", command=self._save).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=self._cancel).pack(side=tk.LEFT, padx=5)
        
        # Set minimum size
        self.geometry("400x250")

    def _save(self) -> None:
        """Save location changes and close dialog."""
        try:
            # Get values
            box = self.box_var.get().strip()
            place = self.place_var.get().strip()
            detail = self.detail_text.get("1.0", tk.END).strip() or None
            
            # Validate required fields
            if not box:
                messagebox.showwarning("Validation Error", "Box name is required")
                return
            
            # Place is optional - set to empty string if not provided
            if not place:
                place = ""
            
            # Validate lengths
            if len(box) > MAX_BOX_LENGTH:
                messagebox.showerror("Validation Error", f"Box name exceeds {MAX_BOX_LENGTH} characters")
                return
            
            if len(place) > MAX_PLACE_LENGTH:
                messagebox.showerror("Validation Error", f"Place exceeds {MAX_PLACE_LENGTH} characters")
                return
            
            if detail and len(detail) > MAX_DETAIL_LENGTH:
                messagebox.showerror("Validation Error", f"Detail exceeds {MAX_DETAIL_LENGTH} characters")
                return
            
            # Update location object
            self.location.box = box
            self.location.place = place
            self.location.detail = detail
            
            self.result = self.location
            
            if self.on_save:
                self.on_save(self.location)
            
            logger.info(f"Location updated: {self.location.id}")
            self.destroy()
            
        except ValidationError as e:
            messagebox.showerror("Validation Error", str(e))
            logger.warning(f"Validation error in EditLocationDialog: {e}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save location: {e}")
            logger.error(f"Error in EditLocationDialog._save: {e}")

    def _cancel(self) -> None:
        """Cancel and close dialog."""
        self.result = None
        self.destroy()


class LocationAssignmentResultsDialog(BaseDialog):
    """Dialog showing location assignment results after import.
    
    Displays statistics about how many media items were assigned locations.
    """

    def __init__(
        self,
        parent: tk.Widget,
        results: dict,
    ) -> None:
        """Initialize location assignment results dialog.
        
        Args:
            parent: Parent window.
            results: Assignment results dictionary with keys:
                - total_media: Total media items checked
                - assigned: Number newly assigned
                - already_assigned: Number already had locations
                - not_found: Number where location wasn't found
                - updated_media: List of updated media IDs
        """
        super().__init__(parent, "Location Assignment Results")
        self.results = results
        self.result = None
        
        # Create content
        self._create_content()
        
        logger.debug("LocationAssignmentResultsDialog initialized")

    def _create_content(self) -> None:
        """Create dialog content."""
        # Main frame with padding
        main_frame = ttk.Frame(self, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(
            main_frame,
            text="Location Assignment Complete",
            font=("TkDefaultFont", 12, "bold")
        )
        title_label.pack(pady=10)
        
        # Results frame
        results_frame = ttk.LabelFrame(main_frame, text="Assignment Results", padding=10)
        results_frame.pack(fill=tk.X, pady=10)
        
        # Format results
        results_text = f"""
Total media items checked: {self.results.get('total_media', 0)}
Media newly assigned locations: {self.results.get('assigned', 0)}
Media already had locations: {self.results.get('already_assigned', 0)}
Media where location not found: {self.results.get('not_found', 0)}
        """.strip()
        
        ttk.Label(results_frame, text=results_text, justify=tk.LEFT).pack(fill=tk.X)
        
        # Summary message
        assigned = self.results.get('assigned', 0)
        not_found = self.results.get('not_found', 0)
        
        if assigned > 0 and not_found == 0:
            summary_text = f"✓ Successfully assigned {assigned} media items to locations!"
            summary_color = "green"
        elif assigned > 0:
            summary_text = f"✓ Assigned {assigned} media items, but {not_found} could not be matched"
            summary_color = "orange"
        elif not_found > 0:
            summary_text = f"⚠ No media items could be assigned. {not_found} items have no matching locations."
            summary_color = "red"
        else:
            summary_text = "No media items needed location assignment"
            summary_color = "blue"
        
        summary_label = ttk.Label(
            main_frame,
            text=summary_text,
            foreground=summary_color,
            font=("TkDefaultFont", 10)
        )
        summary_label.pack(pady=10)
        
        # Buttons frame
        button_frame = ttk.Frame(self)
        button_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Button(button_frame, text="OK", command=self._ok).pack(side=tk.LEFT, padx=5)
        
        # Set size
        self.geometry("400x250")

    def _ok(self) -> None:
        """Close dialog."""
        self.result = self.results
        self.destroy()


class DeleteLocationConfirmDialog(BaseDialog):
    """Dialog for confirming location deletion.
    
    Shows location details and asks for confirmation before deletion.
    """

    def __init__(
        self,
        parent: tk.Widget,
        location: StorageLocation,
        media_count: int = 0,
        on_confirm: Optional[Callable[[StorageLocation], None]] = None,
    ) -> None:
        """Initialize delete confirmation dialog.
        
        Args:
            parent: Parent window.
            location: Location object to delete.
            media_count: Number of media items in this location.
            on_confirm: Optional callback when deletion is confirmed.
        """
        super().__init__(parent, "Confirm Delete Location")
        self.location = location
        self.media_count = media_count
        self.on_confirm = on_confirm
        self.result = None
        
        # Create content
        self._create_content()
        
        logger.debug(f"DeleteLocationConfirmDialog initialized for location: {location.id}")

    def _create_content(self) -> None:
        """Create dialog content."""
        # Main frame with padding
        main_frame = ttk.Frame(self, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Warning icon and message
        warning_frame = ttk.Frame(main_frame)
        warning_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(warning_frame, text="⚠", font=("TkDefaultFont", 24)).pack(side=tk.LEFT, padx=10)
        ttk.Label(
            warning_frame,
            text="Are you sure you want to delete this location?",
            font=("TkDefaultFont", 12, "bold")
        ).pack(side=tk.LEFT, padx=10)
        
        # Location details
        details_frame = ttk.LabelFrame(main_frame, text="Location Details", padding=10)
        details_frame.pack(fill=tk.X, pady=10)
        
        details_text = f"""
Box: {self.location.box}
Place: {self.location.place}
Detail: {self.location.detail or "N/A"}
Media items in location: {self.media_count}
        """.strip()
        
        ttk.Label(details_frame, text=details_text, justify=tk.LEFT).pack(fill=tk.X)
        
        # Warning message
        if self.media_count > 0:
            warning_label = ttk.Label(
                main_frame,
                text=f"Warning: This location contains {self.media_count} media item(s).\nDeleting this location will not delete the media items.",
                foreground="red",
                font=("TkDefaultFont", 10)
            )
        else:
            warning_label = ttk.Label(
                main_frame,
                text="This action cannot be undone.",
                foreground="red",
                font=("TkDefaultFont", 10)
            )
        warning_label.pack(pady=10)
        
        # Buttons frame
        button_frame = ttk.Frame(self)
        button_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Button(button_frame, text="Delete", command=self._confirm).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=self._cancel).pack(side=tk.LEFT, padx=5)
        
        # Set size
        self.geometry("450x300")

    def _confirm(self) -> None:
        """Confirm deletion and close dialog."""
        try:
            self.result = self.location
            
            if self.on_confirm:
                self.on_confirm(self.location)
            
            logger.info(f"Location deletion confirmed: {self.location.id}")
            self.destroy()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to delete location: {e}")
            logger.error(f"Error in DeleteLocationConfirmDialog._confirm: {e}")

    def _cancel(self) -> None:
        """Cancel and close dialog."""
        self.result = None
        self.destroy()

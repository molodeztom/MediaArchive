"""Dialog windows for Media Archive Manager GUI.

This module provides dialog windows for adding, editing, and deleting media items
with form validation and error handling.

History:
20260307  V1.0: Initial implementation with media dialogs
20260307  V1.1: Added location management dialogs
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
        on_save: Optional[Callable[[Media], None]] = None,
    ) -> None:
        """Initialize add media dialog.
        
        Args:
            parent: Parent window.
            locations: List of available storage locations.
            on_save: Optional callback when media is saved.
        """
        super().__init__(parent, "Add New Media")
        self.locations = locations
        self.on_save = on_save
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
        
        # Number field
        ttk.Label(main_frame, text="Number").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.number_var = tk.StringVar()
        number_entry = ttk.Entry(main_frame, textvariable=self.number_var, width=40)
        number_entry.grid(row=1, column=1, sticky=tk.EW, pady=5)
        
        # Media Type field
        ttk.Label(main_frame, text="Media Type").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.media_type_var = tk.StringVar()
        type_combo = ttk.Combobox(
            main_frame,
            textvariable=self.media_type_var,
            values=MediaType.get_all_values(),
            state="readonly",
            width=37
        )
        type_combo.grid(row=2, column=1, sticky=tk.EW, pady=5)
        
        # Category field
        ttk.Label(main_frame, text="Category").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.category_var = tk.StringVar()
        category_entry = ttk.Entry(main_frame, textvariable=self.category_var, width=40)
        category_entry.grid(row=3, column=1, sticky=tk.EW, pady=5)
        
        # Company field
        ttk.Label(main_frame, text="Company").grid(row=4, column=0, sticky=tk.W, pady=5)
        self.company_var = tk.StringVar()
        company_entry = ttk.Entry(main_frame, textvariable=self.company_var, width=40)
        company_entry.grid(row=4, column=1, sticky=tk.EW, pady=5)
        
        # License Code field
        ttk.Label(main_frame, text="License Code").grid(row=5, column=0, sticky=tk.W, pady=5)
        self.license_var = tk.StringVar()
        license_entry = ttk.Entry(main_frame, textvariable=self.license_var, width=40)
        license_entry.grid(row=5, column=1, sticky=tk.EW, pady=5)
        
        # Creation Date field
        ttk.Label(main_frame, text="Creation Date").grid(row=6, column=0, sticky=tk.W, pady=5)
        self.creation_date_var = tk.StringVar()
        creation_date_entry = ttk.Entry(
            main_frame,
            textvariable=self.creation_date_var,
            width=40
        )
        creation_date_entry.grid(row=6, column=1, sticky=tk.EW, pady=5)
        ttk.Label(main_frame, text="(YYYY-MM-DD)", font=("TkDefaultFont", 8)).grid(
            row=6, column=2, sticky=tk.W, padx=5
        )
        
        # Valid Until Date field
        ttk.Label(main_frame, text="Valid Until Date").grid(row=7, column=0, sticky=tk.W, pady=5)
        self.valid_until_var = tk.StringVar()
        valid_until_entry = ttk.Entry(
            main_frame,
            textvariable=self.valid_until_var,
            width=40
        )
        valid_until_entry.grid(row=7, column=1, sticky=tk.EW, pady=5)
        ttk.Label(main_frame, text="(YYYY-MM-DD)", font=("TkDefaultFont", 8)).grid(
            row=7, column=2, sticky=tk.W, padx=5
        )
        
        # Content Description field
        ttk.Label(main_frame, text="Content Description").grid(row=8, column=0, sticky=tk.NW, pady=5)
        self.content_var = tk.StringVar()
        content_text = tk.Text(main_frame, height=4, width=40)
        content_text.grid(row=8, column=1, sticky=tk.EW, pady=5)
        self.content_text = content_text
        
        # Remarks field
        ttk.Label(main_frame, text="Remarks").grid(row=9, column=0, sticky=tk.NW, pady=5)
        self.remarks_var = tk.StringVar()
        remarks_text = tk.Text(main_frame, height=4, width=40)
        remarks_text.grid(row=9, column=1, sticky=tk.EW, pady=5)
        self.remarks_text = remarks_text
        
        # Location field
        ttk.Label(main_frame, text="Storage Location").grid(row=10, column=0, sticky=tk.W, pady=5)
        self.location_var = tk.StringVar()
        location_values = [f"{loc.id}: {loc}" for loc in self.locations]
        location_combo = ttk.Combobox(
            main_frame,
            textvariable=self.location_var,
            values=location_values,
            state="readonly",
            width=37
        )
        location_combo.grid(row=10, column=1, sticky=tk.EW, pady=5)
        
        # Configure grid weights
        main_frame.columnconfigure(1, weight=1)
        
        # Buttons frame
        button_frame = ttk.Frame(self)
        button_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Button(button_frame, text="Save", command=self._save).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=self._cancel).pack(side=tk.LEFT, padx=5)
        
        # Set minimum size
        self.geometry("500x650")

    def _save(self) -> None:
        """Save media and close dialog."""
        try:
            # Get values
            name = self.name_var.get().strip()
            number = self.number_var.get().strip() or None
            media_type = self.media_type_var.get().strip()
            category_value = self.category_var.get().strip() or None
            company = self.company_var.get().strip() or None
            license_code = self.license_var.get().strip() or None
            creation_date_str = self.creation_date_var.get().strip() or None
            valid_until_str = self.valid_until_var.get().strip() or None
            content_desc = self.content_text.get("1.0", tk.END).strip() or None
            remarks = self.remarks_text.get("1.0", tk.END).strip() or None
            location_str = self.location_var.get().strip() or None
            
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
                    creation_date = date.fromisoformat(creation_date_str)
                except ValueError:
                    messagebox.showerror("Date Error", "Invalid creation date format (use YYYY-MM-DD)")
                    return
            
            valid_until_date = None
            if valid_until_str:
                try:
                    valid_until_date = date.fromisoformat(valid_until_str)
                except ValueError:
                    messagebox.showerror("Date Error", "Invalid valid until date format (use YYYY-MM-DD)")
                    return
            
            # Parse location ID
            location_id = None
            if location_str:
                try:
                    location_id = int(location_str.split(":")[0])
                except (ValueError, IndexError):
                    messagebox.showerror("Location Error", "Invalid location selected")
                    return
            
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
        on_save: Optional[Callable[[Media], None]] = None,
    ) -> None:
        """Initialize edit media dialog.
        
        Args:
            parent: Parent window.
            media: Media object to edit.
            locations: List of available storage locations.
            on_save: Optional callback when media is saved.
        """
        super().__init__(parent, f"Edit Media: {media.name}")
        self.media = media
        self.locations = locations
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
        
        # Media Type field
        ttk.Label(main_frame, text="Media Type").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.media_type_var = tk.StringVar(value=self.media.media_type)
        type_combo = ttk.Combobox(
            main_frame,
            textvariable=self.media_type_var,
            values=MediaType.get_all_values(),
            state="readonly",
            width=37
        )
        type_combo.grid(row=2, column=1, sticky=tk.EW, pady=5)
        
        # Category field
        ttk.Label(main_frame, text="Category").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.category_var = tk.StringVar(value=self.media.category or "")
        category_entry = ttk.Entry(main_frame, textvariable=self.category_var, width=40)
        category_entry.grid(row=3, column=1, sticky=tk.EW, pady=5)
        
        # Company field
        ttk.Label(main_frame, text="Company").grid(row=4, column=0, sticky=tk.W, pady=5)
        self.company_var = tk.StringVar(value=self.media.company or "")
        company_entry = ttk.Entry(main_frame, textvariable=self.company_var, width=40)
        company_entry.grid(row=4, column=1, sticky=tk.EW, pady=5)
        
        # License Code field
        ttk.Label(main_frame, text="License Code").grid(row=5, column=0, sticky=tk.W, pady=5)
        self.license_var = tk.StringVar(value=self.media.license_code or "")
        license_entry = ttk.Entry(main_frame, textvariable=self.license_var, width=40)
        license_entry.grid(row=5, column=1, sticky=tk.EW, pady=5)
        
        # Creation Date field
        ttk.Label(main_frame, text="Creation Date").grid(row=6, column=0, sticky=tk.W, pady=5)
        creation_date_str = self.media.creation_date.isoformat() if self.media.creation_date else ""
        self.creation_date_var = tk.StringVar(value=creation_date_str)
        creation_date_entry = ttk.Entry(
            main_frame,
            textvariable=self.creation_date_var,
            width=40
        )
        creation_date_entry.grid(row=6, column=1, sticky=tk.EW, pady=5)
        ttk.Label(main_frame, text="(YYYY-MM-DD)", font=("TkDefaultFont", 8)).grid(
            row=6, column=2, sticky=tk.W, padx=5
        )
        
        # Valid Until Date field
        ttk.Label(main_frame, text="Valid Until Date").grid(row=7, column=0, sticky=tk.W, pady=5)
        valid_until_str = self.media.valid_until_date.isoformat() if self.media.valid_until_date else ""
        self.valid_until_var = tk.StringVar(value=valid_until_str)
        valid_until_entry = ttk.Entry(
            main_frame,
            textvariable=self.valid_until_var,
            width=40
        )
        valid_until_entry.grid(row=7, column=1, sticky=tk.EW, pady=5)
        ttk.Label(main_frame, text="(YYYY-MM-DD)", font=("TkDefaultFont", 8)).grid(
            row=7, column=2, sticky=tk.W, padx=5
        )
        
        # Content Description field
        ttk.Label(main_frame, text="Content Description").grid(row=8, column=0, sticky=tk.NW, pady=5)
        content_text = tk.Text(main_frame, height=4, width=40)
        content_text.insert("1.0", self.media.content_description or "")
        content_text.grid(row=8, column=1, sticky=tk.EW, pady=5)
        self.content_text = content_text
        
        # Remarks field
        ttk.Label(main_frame, text="Remarks").grid(row=9, column=0, sticky=tk.NW, pady=5)
        remarks_text = tk.Text(main_frame, height=4, width=40)
        remarks_text.insert("1.0", self.media.remarks or "")
        remarks_text.grid(row=9, column=1, sticky=tk.EW, pady=5)
        self.remarks_text = remarks_text
        
        # Location field
        ttk.Label(main_frame, text="Storage Location").grid(row=10, column=0, sticky=tk.W, pady=5)
        self.location_var = tk.StringVar()
        location_values = [f"{loc.id}: {loc}" for loc in self.locations]
        if self.media.location_id:
            for val in location_values:
                if val.startswith(f"{self.media.location_id}:"):
                    self.location_var.set(val)
                    break
        location_combo = ttk.Combobox(
            main_frame,
            textvariable=self.location_var,
            values=location_values,
            state="readonly",
            width=37
        )
        location_combo.grid(row=10, column=1, sticky=tk.EW, pady=5)
        
        # Configure grid weights
        main_frame.columnconfigure(1, weight=1)
        
        # Buttons frame
        button_frame = ttk.Frame(self)
        button_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Button(button_frame, text="Save", command=self._save).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=self._cancel).pack(side=tk.LEFT, padx=5)
        
        # Set minimum size
        self.geometry("500x650")

    def _save(self) -> None:
        """Save media changes and close dialog."""
        try:
            # Get values
            name = self.name_var.get().strip()
            number = self.number_var.get().strip() or None
            media_type = self.media_type_var.get().strip()
            category_value = self.category_var.get().strip() or None
            company = self.company_var.get().strip() or None
            license_code = self.license_var.get().strip() or None
            creation_date_str = self.creation_date_var.get().strip() or None
            valid_until_str = self.valid_until_var.get().strip() or None
            content_desc = self.content_text.get("1.0", tk.END).strip() or None
            remarks = self.remarks_text.get("1.0", tk.END).strip() or None
            location_str = self.location_var.get().strip() or None
            
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
                    creation_date = date.fromisoformat(creation_date_str)
                except ValueError:
                    messagebox.showerror("Date Error", "Invalid creation date format (use YYYY-MM-DD)")
                    return
            
            valid_until_date = None
            if valid_until_str:
                try:
                    valid_until_date = date.fromisoformat(valid_until_str)
                except ValueError:
                    messagebox.showerror("Date Error", "Invalid valid until date format (use YYYY-MM-DD)")
                    return
            
            # Parse location ID
            location_id = None
            if location_str:
                try:
                    location_id = int(location_str.split(":")[0])
                except (ValueError, IndexError):
                    messagebox.showerror("Location Error", "Invalid location selected")
                    return
            
            # Update media object
            self.media.name = name
            self.media.number = number
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
        
        # Warning icon and message
        warning_frame = ttk.Frame(main_frame)
        warning_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(warning_frame, text="⚠", font=("TkDefaultFont", 24)).pack(side=tk.LEFT, padx=10)
        ttk.Label(
            warning_frame,
            text="Are you sure you want to delete this media?",
            font=("TkDefaultFont", 12, "bold")
        ).pack(side=tk.LEFT, padx=10)
        
        # Media details
        details_frame = ttk.LabelFrame(main_frame, text="Media Details", padding=10)
        details_frame.pack(fill=tk.X, pady=10)
        
        details_text = f"""
Name: {self.media.name}
Type: {self.media.media_type}
Company: {self.media.company or "N/A"}
License Code: {self.media.license_code or "N/A"}
Location: {self.media.location_id or "N/A"}
Created: {self.media.creation_date or "N/A"}
Expires: {self.media.valid_until_date or "N/A"}
        """.strip()
        
        ttk.Label(details_frame, text=details_text, justify=tk.LEFT).pack(fill=tk.X)
        
        # Warning message
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
        self.geometry("400x300")

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

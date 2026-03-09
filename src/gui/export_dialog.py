"""Export dialog for Media Archive Manager GUI.

This module provides a dialog for exporting media and locations to CSV files.

History:
20260307  V1.0: Initial export dialog implementation
20260307  V1.1: Added semicolon delimiter support for German/European locales
20260309  V1.2: Updated date export to use format_date() for DD.MM.YYYY format
20260309  V1.3: Phase 9A complete - auto-numbering and date format support
"""

import logging
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from typing import Optional, Callable, List
from pathlib import Path
import csv

from models.media import Media
from models.location import StorageLocation
from utils.date_utils import format_date

logger = logging.getLogger(__name__)


class ExportDialog(tk.Toplevel):
    """Dialog for exporting media and locations to CSV files.
    
    Provides export scope selection, file location selection, and options.
    """

    def __init__(
        self,
        parent: tk.Widget,
        media_list: List[Media],
        location_list: List[StorageLocation],
        on_export: Optional[Callable[[str, str, dict], None]] = None,
    ) -> None:
        """Initialize export dialog.
        
        Args:
            parent: Parent window.
            media_list: List of all media items.
            location_list: List of all locations.
            on_export: Optional callback when export is confirmed.
        """
        super().__init__(parent)
        self.title("Export Data")
        self.resizable(False, False)
        self.result = None
        self.on_export = on_export
        self.media_list = media_list
        self.location_list = location_list
        
        # Make dialog modal
        self.transient(parent)
        self.grab_set()
        
        # Create UI
        self._create_ui()
        
        logger.debug("ExportDialog initialized")

    def _create_ui(self) -> None:
        """Create dialog UI."""
        # Main frame
        main_frame = ttk.Frame(self, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Export type frame
        type_frame = ttk.LabelFrame(main_frame, text="Export Type", padding=10)
        type_frame.pack(fill=tk.X, pady=5)
        
        self.type_var = tk.StringVar(value="media")
        ttk.Radiobutton(
            type_frame,
            text="Media Items",
            variable=self.type_var,
            value="media",
            command=self._on_type_changed
        ).pack(anchor=tk.W, pady=5)
        ttk.Radiobutton(
            type_frame,
            text="Storage Locations",
            variable=self.type_var,
            value="locations",
            command=self._on_type_changed
        ).pack(anchor=tk.W, pady=5)
        
        # Export scope frame
        scope_frame = ttk.LabelFrame(main_frame, text="Export Scope", padding=10)
        scope_frame.pack(fill=tk.X, pady=5)
        
        self.scope_var = tk.StringVar(value="all")
        ttk.Radiobutton(
            scope_frame,
            text="All items",
            variable=self.scope_var,
            value="all"
        ).pack(anchor=tk.W, pady=5)
        ttk.Radiobutton(
            scope_frame,
            text="Filtered items (from current view)",
            variable=self.scope_var,
            value="filtered"
        ).pack(anchor=tk.W, pady=5)
        ttk.Radiobutton(
            scope_frame,
            text="Selected items",
            variable=self.scope_var,
            value="selected"
        ).pack(anchor=tk.W, pady=5)
        
        # Options frame
        options_frame = ttk.LabelFrame(main_frame, text="Options", padding=10)
        options_frame.pack(fill=tk.X, pady=5)
        
        # Delimiter selection
        delimiter_frame = ttk.Frame(options_frame)
        delimiter_frame.pack(anchor=tk.W, pady=5)
        ttk.Label(delimiter_frame, text="Delimiter:").pack(side=tk.LEFT, padx=5)
        self.delimiter_var = tk.StringVar(value=",")
        ttk.Radiobutton(
            delimiter_frame,
            text="Comma (,)",
            variable=self.delimiter_var,
            value=","
        ).pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(
            delimiter_frame,
            text="Semicolon (;)",
            variable=self.delimiter_var,
            value=";"
        ).pack(side=tk.LEFT, padx=5)
        
        self.include_header_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            options_frame,
            text="Include header row",
            variable=self.include_header_var
        ).pack(anchor=tk.W, pady=5)
        
        self.include_details_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            options_frame,
            text="Include location details (for media export)",
            variable=self.include_details_var
        ).pack(anchor=tk.W, pady=5)
        
        # File selection frame
        file_frame = ttk.LabelFrame(main_frame, text="Save Location", padding=10)
        file_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(file_frame, text="File:").pack(side=tk.LEFT, padx=5)
        self.file_var = tk.StringVar()
        file_entry = ttk.Entry(file_frame, textvariable=self.file_var, width=40)
        file_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        ttk.Button(file_frame, text="Browse", command=self._browse_file).pack(side=tk.LEFT, padx=5)
        
        # Status frame
        status_frame = ttk.Frame(main_frame)
        status_frame.pack(fill=tk.X, pady=5)
        
        self.status_var = tk.StringVar(value="Ready to export")
        ttk.Label(status_frame, textvariable=self.status_var).pack(anchor=tk.W)
        
        # Buttons frame
        button_frame = ttk.Frame(self)
        button_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Button(button_frame, text="Export", command=self._export).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=self._cancel).pack(side=tk.LEFT, padx=5)
        
        self.geometry("500x400")

    def _on_type_changed(self) -> None:
        """Handle export type change."""
        export_type = self.type_var.get()
        if export_type == "media":
            self.status_var.set(f"Ready to export {len(self.media_list)} media items")
        else:
            self.status_var.set(f"Ready to export {len(self.location_list)} locations")

    def _browse_file(self) -> None:
        """Browse for save location."""
        export_type = self.type_var.get()
        default_name = f"export_{export_type}.csv"
        
        file_path = filedialog.asksaveasfilename(
            title="Save CSV file",
            defaultextension=".csv",
            initialfile=default_name,
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        
        if file_path:
            self.file_var.set(file_path)

    def _export(self) -> None:
        """Export data to CSV file."""
        try:
            file_path = self.file_var.get()
            if not file_path:
                messagebox.showwarning("Validation Error", "Please select a save location")
                return
            
            export_type = self.type_var.get()
            scope = self.scope_var.get()
            include_header = self.include_header_var.get()
            include_details = self.include_details_var.get()
            delimiter = self.delimiter_var.get()
            
            # Prepare data based on type
            if export_type == "media":
                data = self._prepare_media_export(scope, include_details)
                headers = self._get_media_headers(include_details)
            else:
                data = self._prepare_location_export(scope)
                headers = self._get_location_headers()
            
            if not data:
                messagebox.showwarning("Export Error", "No data to export")
                return
            
            # Write to CSV file
            with open(file_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f, delimiter=delimiter)
                
                if include_header:
                    writer.writerow(headers)
                
                for row in data:
                    writer.writerow(row)
            
            # Show success message
            message = f"Successfully exported {len(data)} {export_type} items to:\n{file_path}"
            messagebox.showinfo("Export Successful", message)
            
            logger.info(f"Exported {len(data)} {export_type} items to {file_path}")
            
            self.result = (file_path, export_type, {
                'count': len(data),
                'include_header': include_header,
                'include_details': include_details,
            })
            
            if self.on_export:
                self.on_export(file_path, export_type, {'count': len(data)})
            
            self.destroy()
            
        except Exception as e:
            logger.error(f"Export failed: {e}")
            messagebox.showerror("Export Error", f"Failed to export data: {e}")

    def _prepare_media_export(self, scope: str, include_details: bool) -> list:
        """Prepare media data for export."""
        if scope == "all":
            media_to_export = self.media_list
        elif scope == "filtered":
            # In a real implementation, this would use filtered data from main window
            media_to_export = self.media_list
        else:  # selected
            # In a real implementation, this would use selected items from main window
            media_to_export = self.media_list
        
        data = []
        for media in media_to_export:
            row = [
                media.name,
                media.media_type or "Unknown",
                media.type or "",
                media.company or "",
                media.license_code or "",
                format_date(media.creation_date) if media.creation_date else "",
                format_date(media.valid_until_date) if media.valid_until_date else "",
                media.content_description or "",
                media.remarks or "",
                media.location_id or "",
            ]
            
            if include_details and media.location_id:
                # Find location details
                for loc in self.location_list:
                    if loc.id == media.location_id:
                        row.extend([loc.box, loc.place, loc.detail or ""])
                        break
            
            data.append(row)
        
        return data

    def _prepare_location_export(self, scope: str) -> list:
        """Prepare location data for export."""
        if scope == "all":
            locations_to_export = self.location_list
        elif scope == "filtered":
            # In a real implementation, this would use filtered data from main window
            locations_to_export = self.location_list
        else:  # selected
            # In a real implementation, this would use selected items from main window
            locations_to_export = self.location_list
        
        data = []
        for location in locations_to_export:
            row = [
                location.box,
                location.place,
                location.detail or "",
            ]
            data.append(row)
        
        return data

    def _get_media_headers(self, include_details: bool) -> list:
        """Get media export headers."""
        headers = [
            "Name",
            "Media Type",
            "Type",
            "Company",
            "License Code",
            "Creation Date",
            "Valid Until Date",
            "Content Description",
            "Remarks",
            "Location ID",
        ]
        
        if include_details:
            headers.extend(["Location Box", "Location Place", "Location Detail"])
        
        return headers

    def _get_location_headers(self) -> list:
        """Get location export headers."""
        return ["Box", "Place", "Detail"]

    def _cancel(self) -> None:
        """Cancel and close dialog."""
        self.result = None
        self.destroy()

    def show(self) -> Optional[tuple]:
        """Show dialog and wait for result.
        
        Returns:
            Tuple of (file_path, export_type, options) or None if cancelled.
        """
        self.update_idletasks()
        parent = self.master
        x = parent.winfo_x() + (parent.winfo_width() // 2) - (self.winfo_width() // 2)
        y = parent.winfo_y() + (parent.winfo_height() // 2) - (self.winfo_height() // 2)
        self.geometry(f"+{x}+{y}")
        
        self.wait_window()
        return self.result

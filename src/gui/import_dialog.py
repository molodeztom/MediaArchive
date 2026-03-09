"""Import dialog for Media Archive Manager GUI.

This module provides a dialog for importing media and locations from CSV files.

History:
20260307  V1.0: Initial import dialog implementation
20260307  V1.1: Added semicolon delimiter support for German/European locales
20260308  V1.2: Added encoding detection for Access CSV files
20260308  V1.3: Fixed dialog layout for button visibility
20260308  V1.4: Added Access CSV format support with mapper integration
20260308  V1.5: Set Access format as default, semicolon as default delimiter, resizable dialog, 15-row preview
20260309  V1.6: Updated date parsing to use parse_date() for DD.MM.YYYY format
20260309  V1.7: Phase 9A complete - auto-numbering and date format support
"""

import logging
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from typing import Optional, Callable
from pathlib import Path
import csv
from datetime import date

from models.media import Media
from models.location import StorageLocation
from models.enums import MediaType
from utils.exceptions import ValidationError
from utils.encoding_detector import EncodingDetector
from utils.date_utils import parse_date
from business.access_csv_mapper import AccessCSVMapper, AccessLocationMapper

logger = logging.getLogger(__name__)


class ImportDialog(tk.Toplevel):
    """Dialog for importing media and locations from CSV files.
    
    Provides file selection, import type selection, and preview functionality.
    """

    def __init__(
        self,
        parent: tk.Widget,
        on_import: Optional[Callable[[list, str], None]] = None,
        locations: Optional[list[StorageLocation]] = None,
    ) -> None:
        """Initialize import dialog.
        
        Args:
            parent: Parent window.
            on_import: Optional callback when import is confirmed.
            locations: Optional list of existing locations for Access format mapping.
        """
        super().__init__(parent)
        self.title("Import Data")
        self.resizable(True, True)
        self.result = None
        self.on_import = on_import
        self.imported_data = []
        self.import_type = "media"
        self.csv_format = "access"  # standard or access
        self.locations = locations or []  # For Access format mapping
        
        # Make dialog modal
        self.transient(parent)
        self.grab_set()
        
        # Create UI
        self._create_ui()
        
        logger.debug("ImportDialog initialized")

    def _create_ui(self) -> None:
        """Create dialog UI."""
        # Buttons frame FIRST - pack at bottom
        button_frame = ttk.Frame(self, padding=10)
        button_frame.pack(side=tk.BOTTOM, fill=tk.X)
        
        ttk.Button(button_frame, text="Import", command=self._import).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=self._cancel).pack(side=tk.LEFT, padx=5)
        
        # Separator
        ttk.Separator(self, orient=tk.HORIZONTAL).pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=5)
        
        # Main frame for content - pack AFTER buttons
        main_frame = ttk.Frame(self, padding=10)
        main_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        
        # File selection frame
        file_frame = ttk.LabelFrame(main_frame, text="Select File", padding=10)
        file_frame.pack(fill=tk.X, pady=(0, 5))
        
        ttk.Label(file_frame, text="File:").pack(side=tk.LEFT, padx=5)
        self.file_var = tk.StringVar()
        file_entry = ttk.Entry(file_frame, textvariable=self.file_var, width=40)
        file_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        ttk.Button(file_frame, text="Browse", command=self._browse_file).pack(side=tk.LEFT, padx=5)
        
        # Import type frame
        type_frame = ttk.LabelFrame(main_frame, text="Import Type", padding=10)
        type_frame.pack(fill=tk.X, pady=(0, 5))
        
        self.type_var = tk.StringVar(value="media")
        ttk.Radiobutton(
            type_frame,
            text="Media Items",
            variable=self.type_var,
            value="media",
            command=self._on_type_changed
        ).pack(anchor=tk.W, pady=2)
        ttk.Radiobutton(
            type_frame,
            text="Storage Locations",
            variable=self.type_var,
            value="locations",
            command=self._on_type_changed
        ).pack(anchor=tk.W, pady=2)
        
        # CSV Format frame
        format_frame = ttk.LabelFrame(main_frame, text="CSV Format", padding=10)
        format_frame.pack(fill=tk.X, pady=(0, 5))
        
        self.format_var = tk.StringVar(value="access")
        ttk.Radiobutton(
            format_frame,
            text="Standard Format",
            variable=self.format_var,
            value="standard"
        ).pack(anchor=tk.W, pady=2)
        ttk.Radiobutton(
            format_frame,
            text="Access Database Format",
            variable=self.format_var,
            value="access"
        ).pack(anchor=tk.W, pady=2)
        
        # Options frame
        options_frame = ttk.LabelFrame(main_frame, text="Options", padding=10)
        options_frame.pack(fill=tk.X, pady=(0, 5))
        
        # Delimiter selection
        delimiter_frame = ttk.Frame(options_frame)
        delimiter_frame.pack(anchor=tk.W, pady=2)
        ttk.Label(delimiter_frame, text="Delimiter:").pack(side=tk.LEFT, padx=5)
        self.delimiter_var = tk.StringVar(value=";")
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
        
        self.skip_header_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            options_frame,
            text="Skip header row",
            variable=self.skip_header_var
        ).pack(anchor=tk.W, pady=2)
        
        self.validate_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            options_frame,
            text="Validate data",
            variable=self.validate_var
        ).pack(anchor=tk.W, pady=2)
        
        self.update_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(
            options_frame,
            text="Update existing items",
            variable=self.update_var
        ).pack(anchor=tk.W, pady=2)
        
        # Preview frame
        preview_frame = ttk.LabelFrame(main_frame, text="Preview", padding=10)
        preview_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 5))
        
        # Preview tree
        columns = ("Column1", "Column2", "Column3", "Column4", "Column5")
        self.preview_tree = ttk.Treeview(preview_frame, columns=columns, height=15)
        self.preview_tree.column("#0", width=0, stretch=tk.NO)
        for col in columns:
            self.preview_tree.column(col, anchor=tk.W, width=80)
            self.preview_tree.heading(col, text=col, anchor=tk.W)
        
        scrollbar = ttk.Scrollbar(preview_frame, orient=tk.VERTICAL, command=self.preview_tree.yview)
        self.preview_tree.configure(yscroll=scrollbar.set)
        
        self.preview_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Status frame
        status_frame = ttk.Frame(main_frame)
        status_frame.pack(fill=tk.X, pady=(0, 0))
        
        self.status_var = tk.StringVar(value="Ready to import")
        ttk.Label(status_frame, textvariable=self.status_var).pack(anchor=tk.W)
        
        # Set resizable dialog size
        self.geometry("750x700")
        self.minsize(750, 600)

    def _browse_file(self) -> None:
        """Browse for CSV file."""
        file_path = filedialog.askopenfilename(
            title="Select CSV file",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        
        if file_path:
            self.file_var.set(file_path)
            self._load_preview(file_path)

    def _load_preview(self, file_path: str) -> None:
        """Load preview of CSV file."""
        try:
            # Clear existing preview
            for item in self.preview_tree.get_children():
                self.preview_tree.delete(item)
            
            # Get delimiter
            delimiter = self.delimiter_var.get()
            
            # Detect encoding and read CSV file
            encoding = EncodingDetector.detect_encoding(file_path)
            with open(file_path, 'r', encoding=encoding) as f:
                reader = csv.reader(f, delimiter=delimiter)
                rows = list(reader)
            
            if not rows:
                self.status_var.set("File is empty")
                return
            
            # Determine starting row
            start_row = 1 if self.skip_header_var.get() and len(rows) > 1 else 0
            
            # Get column headers
            if self.skip_header_var.get() and len(rows) > 0:
                headers = rows[0]
            else:
                headers = [f"Column{i+1}" for i in range(len(rows[0]) if rows else 0)]
            
            # Update tree columns
            columns = tuple(headers[:5])
            self.preview_tree.configure(columns=columns)
            for i, col in enumerate(columns):
                self.preview_tree.column(col, anchor=tk.W, width=100)
                self.preview_tree.heading(col, text=col, anchor=tk.W)
            
            # Load preview rows (max 10)
            for row in rows[start_row:start_row+10]:
                self.preview_tree.insert("", tk.END, values=row[:5])
            
            self.status_var.set(f"Loaded {len(rows)} rows from file")
            logger.debug(f"Preview loaded: {len(rows)} rows")
            
        except Exception as e:
            logger.error(f"Failed to load preview: {e}")
            self.status_var.set(f"Error loading file: {e}")
            messagebox.showerror("Error", f"Failed to load file: {e}")

    def _on_type_changed(self) -> None:
        """Handle import type change."""
        file_path = self.file_var.get()
        if file_path:
            self._load_preview(file_path)

    def _import(self) -> None:
        """Import data from CSV file."""
        try:
            file_path = self.file_var.get()
            if not file_path:
                messagebox.showwarning("Validation Error", "Please select a file")
                return
            
            if not Path(file_path).exists():
                messagebox.showerror("File Error", "File does not exist")
                return
            
            import_type = self.type_var.get()
            skip_header = self.skip_header_var.get()
            validate = self.validate_var.get()
            delimiter = self.delimiter_var.get()
            
            # Detect encoding and read CSV file
            encoding = EncodingDetector.detect_encoding(file_path)
            with open(file_path, 'r', encoding=encoding) as f:
                reader = csv.reader(f, delimiter=delimiter)
                rows = list(reader)
            
            if not rows:
                messagebox.showwarning("Import Error", "File is empty")
                return
            
            # Parse data based on format and type
            csv_format = self.format_var.get()
            
            if csv_format == "access":
                # Use Access CSV Mapper
                if import_type == "media":
                    media_list, errors = AccessCSVMapper.parse_media_rows(rows, self.locations, skip_header=skip_header)
                    self.imported_data = media_list
                    if errors:
                        error_msg = "Import completed with errors:\n\n" + "\n".join(errors[:10])
                        if len(errors) > 10:
                            error_msg += f"\n... and {len(errors) - 10} more errors"
                        messagebox.showwarning("Import Warnings", error_msg)
                else:
                    location_list, errors = AccessLocationMapper.parse_location_rows(rows, skip_header=skip_header, generate_internal_ids=True)
                    self.imported_data = location_list
                    if errors:
                        error_msg = "Import completed with errors:\n\n" + "\n".join(errors[:10])
                        if len(errors) > 10:
                            error_msg += f"\n... and {len(errors) - 10} more errors"
                        messagebox.showwarning("Import Warnings", error_msg)
            else:
                # Use standard format parser
                start_row = 1 if skip_header and len(rows) > 1 else 0
                data_rows = rows[start_row:]
                
                if import_type == "media":
                    self.imported_data = self._parse_media_rows(data_rows, validate)
                else:
                    self.imported_data = self._parse_location_rows(data_rows, validate)
            
            if not self.imported_data:
                messagebox.showwarning("Import Error", "No valid data to import")
                return
            
            # Show confirmation
            message = f"Ready to import {len(self.imported_data)} {import_type} items.\n\nContinue?"
            if messagebox.askyesno("Confirm Import", message):
                self.result = (self.imported_data, import_type)
                
                if self.on_import:
                    self.on_import(self.imported_data, import_type)
                
                logger.info(f"Imported {len(self.imported_data)} {import_type} items")
                self.destroy()
            
        except Exception as e:
            logger.error(f"Import failed: {e}")
            messagebox.showerror("Import Error", f"Failed to import data: {e}")

    def _parse_media_rows(self, rows: list, validate: bool = True) -> list[Media]:
        """Parse media rows from CSV.
        
        Expected columns: name, media_type, company, license_code, creation_date,
                         valid_until_date, content_description, remarks, location_id
        """
        media_list = []
        errors = []
        
        for i, row in enumerate(rows, start=1):
            try:
                if len(row) < 2:
                    errors.append(f"Row {i}: Insufficient columns")
                    continue
                
                name = row[0].strip() if len(row) > 0 else ""
                media_type = row[1].strip() if len(row) > 1 else ""
                company = row[2].strip() if len(row) > 2 else None
                license_code = row[3].strip() if len(row) > 3 else None
                creation_date_str = row[4].strip() if len(row) > 4 else None
                valid_until_str = row[5].strip() if len(row) > 5 else None
                content_desc = row[6].strip() if len(row) > 6 else None
                remarks = row[7].strip() if len(row) > 7 else None
                location_id_str = row[8].strip() if len(row) > 8 else None
                
                # Validate required fields
                if not name:
                    errors.append(f"Row {i}: Name is required")
                    continue
                
                if not media_type:
                    media_type = "Unknown"
                
                if validate and not MediaType.is_valid(media_type):
                    errors.append(f"Row {i}: Invalid media type: {media_type}")
                    continue
                
                # Parse dates
                creation_date = None
                if creation_date_str:
                    try:
                        creation_date = parse_date(creation_date_str)
                    except ValueError:
                        errors.append(f"Row {i}: Invalid creation date: {creation_date_str}")
                        continue
                
                valid_until_date = None
                if valid_until_str:
                    try:
                        valid_until_date = parse_date(valid_until_str)
                    except ValueError:
                        errors.append(f"Row {i}: Invalid valid until date: {valid_until_str}")
                        continue
                
                # Parse location ID
                location_id = None
                if location_id_str:
                    try:
                        location_id = int(location_id_str)
                    except ValueError:
                        errors.append(f"Row {i}: Invalid location ID: {location_id_str}")
                        continue
                
                # Create media object
                media = Media(
                    name=name,
                    media_type=media_type,
                    company=company or None,
                    license_code=license_code or None,
                    creation_date=creation_date,
                    valid_until_date=valid_until_date,
                    content_description=content_desc or None,
                    remarks=remarks or None,
                    location_id=location_id,
                )
                
                media_list.append(media)
                
            except Exception as e:
                errors.append(f"Row {i}: {str(e)}")
        
        # Show errors if any
        if errors:
            error_msg = "Import completed with errors:\n\n" + "\n".join(errors[:10])
            if len(errors) > 10:
                error_msg += f"\n... and {len(errors) - 10} more errors"
            messagebox.showwarning("Import Warnings", error_msg)
        
        return media_list

    def _parse_location_rows(self, rows: list, validate: bool = True) -> list[StorageLocation]:
        """Parse location rows from CSV.
        
        Expected columns: box, place, detail
        """
        location_list = []
        errors = []
        
        for i, row in enumerate(rows, start=1):
            try:
                if len(row) < 2:
                    errors.append(f"Row {i}: Insufficient columns")
                    continue
                
                box = row[0].strip() if len(row) > 0 else ""
                place = row[1].strip() if len(row) > 1 else ""
                detail = row[2].strip() if len(row) > 2 else None
                
                # Validate required fields
                if not box:
                    errors.append(f"Row {i}: Box is required")
                    continue
                
                # Place is optional - set to empty string if not provided
                if not place:
                    place = ""
                
                # Create location object
                location = StorageLocation(
                    box=box,
                    place=place,
                    detail=detail or None,
                )
                
                location_list.append(location)
                
            except Exception as e:
                errors.append(f"Row {i}: {str(e)}")
        
        # Show errors if any
        if errors:
            error_msg = "Import completed with errors:\n\n" + "\n".join(errors[:10])
            if len(errors) > 10:
                error_msg += f"\n... and {len(errors) - 10} more errors"
            messagebox.showwarning("Import Warnings", error_msg)
        
        return location_list

    def _cancel(self) -> None:
        """Cancel and close dialog."""
        self.result = None
        self.destroy()

    def show(self) -> Optional[tuple]:
        """Show dialog and wait for result.
        
        Returns:
            Tuple of (imported_data, import_type) or None if cancelled.
        """
        self.update_idletasks()
        parent = self.master
        x = parent.winfo_x() + (parent.winfo_width() // 2) - (self.winfo_width() // 2)
        y = parent.winfo_y() + (parent.winfo_height() // 2) - (self.winfo_height() // 2)
        self.geometry(f"+{x}+{y}")
        
        self.wait_window()
        return self.result

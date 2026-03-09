"""Preferences dialog for Media Archive Manager GUI.

This module provides a preferences dialog for managing application settings
including logging preferences.

History:
20260309  V1.0: Initial preferences dialog implementation
20260309  V1.1: Fixed logging preferences persistence - save directly to DB
20260309  V1.2: Phase 9F - Added maximum items limit setting (3000)
20260309  V1.3: Increased dialog height to 480px for better button visibility
20260309  V1.4: Load max_items from preferences on dialog init for persistence
"""

import logging
import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional, Callable

logger = logging.getLogger(__name__)


class PreferencesDialog(tk.Toplevel):
    """Dialog for managing application preferences.
    
    Provides settings for logging and other application preferences.
    """

    def __init__(
        self,
        parent: tk.Widget,
        preferences_repo = None,
        on_save: Optional[Callable] = None,
    ) -> None:
        """Initialize preferences dialog.
        
        Args:
            parent: Parent window.
            preferences_repo: PreferencesRepository instance.
            on_save: Optional callback when preferences are saved.
        """
        super().__init__(parent)
        self.title("Preferences")
        self.resizable(False, False)
        self.result = None
        self.preferences_repo = preferences_repo
        self.on_save = on_save
        
        # Make dialog modal
        self.transient(parent)
        self.grab_set()
        
        # Create form
        self._create_form()
        
        logger.debug("PreferencesDialog initialized")

    def _create_form(self) -> None:
        """Create preferences form."""
        # Main frame with padding
        main_frame = ttk.Frame(self, padding=15)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Logging section
        logging_frame = ttk.LabelFrame(main_frame, text="Logging Settings", padding=15)
        logging_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
        
        # Logging enabled checkbox
        self.logging_enabled_var = tk.BooleanVar(value=True)
        if self.preferences_repo:
            self.logging_enabled_var.set(self.preferences_repo.get_logging_enabled(default=True))
        
        logging_enabled_check = ttk.Checkbutton(
            logging_frame,
            text="Enable Logging",
            variable=self.logging_enabled_var
        )
        logging_enabled_check.pack(anchor=tk.W, pady=8)
        
        # Log level selection
        ttk.Label(logging_frame, text="Log Level:").pack(anchor=tk.W, pady=(15, 8))
        
        self.log_level_var = tk.StringVar(value="INFO")
        if self.preferences_repo:
            self.log_level_var.set(self.preferences_repo.get_logging_level(default="INFO"))
        
        log_level_combo = ttk.Combobox(
            logging_frame,
            textvariable=self.log_level_var,
            values=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
            state="readonly",
            width=20
        )
        log_level_combo.pack(anchor=tk.W, pady=(0, 8))
        
        # Info label
        info_label = ttk.Label(
            logging_frame,
            text="Changes take effect immediately without restart.",
            font=("TkDefaultFont", 9, "italic"),
            foreground="gray"
        )
        info_label.pack(anchor=tk.W, pady=(15, 0))
        
        # Performance section
        perf_frame = ttk.LabelFrame(main_frame, text="Performance Settings", padding=15)
        perf_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
        
        # Maximum items setting
        ttk.Label(perf_frame, text="Maximum Items to Load:").pack(anchor=tk.W, pady=(0, 8))
        
        self.max_items_var = tk.StringVar(value="3000")
        if self.preferences_repo:
            self.max_items_var.set(self.preferences_repo.get_preference("max_items", "3000"))
        
        max_items_spin = ttk.Spinbox(
            perf_frame,
            from_=100,
            to=10000,
            textvariable=self.max_items_var,
            width=10
        )
        max_items_spin.pack(anchor=tk.W, pady=(0, 8))
        
        # Info label for max items
        max_items_info = ttk.Label(
            perf_frame,
            text="Limits the number of items loaded to improve performance (100-10000).",
            font=("TkDefaultFont", 9, "italic"),
            foreground="gray"
        )
        max_items_info.pack(anchor=tk.W, pady=(0, 0))
        
        # Buttons frame - positioned at bottom
        button_frame = ttk.Frame(self)
        button_frame.pack(fill=tk.X, padx=15, pady=15, side=tk.BOTTOM)
        
        ttk.Button(button_frame, text="Save", command=self._save).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=self._cancel).pack(side=tk.LEFT, padx=5)
        
        # Set size - increased height to accommodate all elements and buttons
        self.geometry("450x480")

    def _save(self) -> None:
        """Save preferences and close dialog."""
        try:
            logging_enabled = self.logging_enabled_var.get()
            log_level = self.log_level_var.get()
            max_items_str = self.max_items_var.get()
            
            # Validate max_items
            try:
                max_items = int(max_items_str)
                if max_items < 100 or max_items > 10000:
                    messagebox.showerror("Validation Error", "Maximum items must be between 100 and 10000")
                    return
            except ValueError:
                messagebox.showerror("Validation Error", "Maximum items must be a valid number")
                return
            
            if self.preferences_repo:
                # Save logging preferences directly to database
                try:
                    self.preferences_repo.set_logging_enabled(logging_enabled)
                    logger.debug(f"Saved logging_enabled to DB: {logging_enabled}")
                except Exception as e:
                    logger.error(f"Failed to save logging_enabled: {e}")
                    raise
                
                try:
                    self.preferences_repo.set_logging_level(log_level)
                    logger.debug(f"Saved logging_level to DB: {log_level}")
                except Exception as e:
                    logger.error(f"Failed to save logging_level: {e}")
                    raise
                
                try:
                    self.preferences_repo.set_preference("max_items", str(max_items))
                    logger.debug(f"Saved max_items to DB: {max_items}")
                except Exception as e:
                    logger.error(f"Failed to save max_items: {e}")
                    raise
                
                logger.info(f"Preferences saved: logging_enabled={logging_enabled}, log_level={log_level}, max_items={max_items}")
            
            self.result = {
                "logging_enabled": logging_enabled,
                "log_level": log_level,
                "max_items": max_items,
            }
            
            if self.on_save:
                self.on_save(self.result)
            
            self.destroy()
            
        except Exception as e:
            logger.error(f"Error saving preferences: {e}")
            messagebox.showerror("Error", f"Failed to save preferences: {e}")

    def _cancel(self) -> None:
        """Cancel and close dialog."""
        self.result = None
        self.destroy()

    def show(self) -> Optional[dict]:
        """Show dialog and wait for result.
        
        Returns:
            Dictionary with preferences or None if cancelled.
        """
        self.update_idletasks()
        parent = self.master
        x = parent.winfo_x() + (parent.winfo_width() // 2) - (self.winfo_width() // 2)
        y = parent.winfo_y() + (parent.winfo_height() // 2) - (self.winfo_height() // 2)
        self.geometry(f"+{x}+{y}")
        
        self.wait_window()
        return self.result

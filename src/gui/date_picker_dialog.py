"""Date picker widget for Media Archive Manager GUI.

This module provides a date picker dialog for selecting dates in DD.MM.YYYY format.
Uses a simple calendar-based interface built with tkinter.

History:
20260309  V1.0: Initial date picker implementation with calendar widget
20260309  V1.1: Added error message for invalid date entry
20260309  V1.2: Added year/month selector for far-future dates, auto-save on selection
"""

import logging
import tkinter as tk
from datetime import date, timedelta
from tkinter import ttk, messagebox
from typing import Optional

from utils.date_utils import format_date, parse_date

logger = logging.getLogger(__name__)


class DatePickerDialog(tk.Toplevel):
    """Dialog for selecting a date using a calendar widget.
    
    Provides a calendar-based date picker with manual entry support.
    """

    def __init__(
        self,
        parent: tk.Widget,
        title: str = "Select Date",
        initial_date: Optional[date] = None,
    ) -> None:
        """Initialize date picker dialog.
        
        Args:
            parent: Parent window.
            title: Dialog window title.
            initial_date: Initial date to display (default: today).
        """
        super().__init__(parent)
        self.title(title)
        self.resizable(False, False)
        self.result = None
        
        # Make dialog modal
        self.transient(parent)
        self.grab_set()
        
        # Initialize date
        self.current_date = initial_date or date.today()
        self.selected_date = self.current_date
        
        # Create UI
        self._create_ui()
        
        logger.debug(f"DatePickerDialog initialized with date: {self.current_date}")

    def _create_ui(self) -> None:
        """Create the date picker UI."""
        # Main frame
        main_frame = ttk.Frame(self, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Navigation frame (month/year)
        nav_frame = ttk.Frame(main_frame)
        nav_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Button(nav_frame, text="◀", width=3, command=self._prev_month).pack(side=tk.LEFT, padx=2)
        
        self.month_year_var = tk.StringVar()
        self._update_month_year_display()
        month_year_label = ttk.Label(nav_frame, textvariable=self.month_year_var, font=("TkDefaultFont", 11, "bold"))
        month_year_label.pack(side=tk.LEFT, expand=True, padx=10)
        month_year_label.bind("<Button-1>", self._show_year_month_selector)
        
        ttk.Button(nav_frame, text="▶", width=3, command=self._next_month).pack(side=tk.LEFT, padx=2)
        
        # Calendar frame
        cal_frame = ttk.Frame(main_frame)
        cal_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Day headers
        days = ["Mo", "Tu", "We", "Th", "Fr", "Sa", "Su"]
        for i, day in enumerate(days):
            ttk.Label(cal_frame, text=day, font=("TkDefaultFont", 9, "bold")).grid(row=0, column=i, padx=2, pady=2)
        
        # Calendar buttons
        self.day_buttons = []
        for row in range(1, 7):
            for col in range(7):
                btn = tk.Button(
                    cal_frame,
                    text="",
                    width=3,
                    height=2,
                    command=lambda r=row, c=col: self._on_day_click(r, c),
                    relief=tk.RAISED,
                    bg="white",
                    font=("TkDefaultFont", 9)
                )
                btn.grid(row=row, column=col, padx=1, pady=1)
                self.day_buttons.append(btn)
        
        self._populate_calendar()
        
        # Manual entry frame
        entry_frame = ttk.Frame(main_frame)
        entry_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(entry_frame, text="Or enter date:").pack(side=tk.LEFT, padx=(0, 5))
        self.date_entry_var = tk.StringVar(value=format_date(self.current_date))
        date_entry = ttk.Entry(entry_frame, textvariable=self.date_entry_var, width=15)
        date_entry.pack(side=tk.LEFT, padx=2)
        ttk.Label(entry_frame, text="(DD.MM.YYYY)", font=("TkDefaultFont", 8)).pack(side=tk.LEFT, padx=2)
        
        # Buttons frame
        button_frame = ttk.Frame(self)
        button_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Button(button_frame, text="Cancel", command=self._cancel).pack(side=tk.LEFT, padx=5)
        
        # Set size
        self.geometry("280x350")

    def _update_month_year_display(self) -> None:
        """Update the month/year display."""
        month_names = [
            "January", "February", "March", "April", "May", "June",
            "July", "August", "September", "October", "November", "December"
        ]
        month_name = month_names[self.current_date.month - 1]
        self.month_year_var.set(f"{month_name} {self.current_date.year}")

    def _populate_calendar(self) -> None:
        """Populate calendar with days for current month."""
        # Get first day of month and number of days
        first_day = date(self.current_date.year, self.current_date.month, 1)
        # Monday = 0, Sunday = 6
        first_weekday = first_day.weekday()
        
        # Get number of days in month
        if self.current_date.month == 12:
            last_day = date(self.current_date.year + 1, 1, 1) - timedelta(days=1)
        else:
            last_day = date(self.current_date.year, self.current_date.month + 1, 1) - timedelta(days=1)
        
        num_days = last_day.day
        
        # Clear all buttons
        for btn in self.day_buttons:
            btn.config(text="", state=tk.DISABLED, bg="white")
        
        # Fill in days
        day = 1
        button_index = first_weekday
        
        while day <= num_days:
            if button_index < len(self.day_buttons):
                btn = self.day_buttons[button_index]
                btn.config(text=str(day), state=tk.NORMAL, bg="white")
                
                # Highlight today
                if (self.current_date.year == date.today().year and
                    self.current_date.month == date.today().month and
                    day == date.today().day):
                    btn.config(bg="lightblue")
                
                # Highlight selected date
                if (self.current_date.year == self.selected_date.year and
                    self.current_date.month == self.selected_date.month and
                    day == self.selected_date.day):
                    btn.config(bg="lightgreen")
                
                day += 1
            button_index += 1

    def _on_day_click(self, row: int, col: int) -> None:
        """Handle day button click."""
        button_index = (row - 1) * 7 + col
        if button_index < len(self.day_buttons):
            btn = self.day_buttons[button_index]
            day_text = btn.cget("text")
            if day_text:
                try:
                    day = int(day_text)
                    self.selected_date = date(self.current_date.year, self.current_date.month, day)
                    self.date_entry_var.set(format_date(self.selected_date))
                    self._populate_calendar()
                    # Auto-save and close dialog
                    self.result = self.selected_date
                    logger.debug(f"Date selected: {self.result}")
                    self.destroy()
                except ValueError:
                    pass

    def _prev_month(self) -> None:
        """Go to previous month."""
        if self.current_date.month == 1:
            self.current_date = date(self.current_date.year - 1, 12, 1)
        else:
            self.current_date = date(self.current_date.year, self.current_date.month - 1, 1)
        self._update_month_year_display()
        self._populate_calendar()

    def _next_month(self) -> None:
        """Go to next month."""
        if self.current_date.month == 12:
            self.current_date = date(self.current_date.year + 1, 1, 1)
        else:
            self.current_date = date(self.current_date.year, self.current_date.month + 1, 1)
        self._update_month_year_display()
        self._populate_calendar()

    def _validate_and_save_entry(self) -> None:
        """Validate manual date entry and save if valid."""
        try:
            date_str = self.date_entry_var.get().strip()
            if date_str:
                self.result = parse_date(date_str)
                logger.debug(f"Date selected from entry: {self.result}")
                self.destroy()
            else:
                messagebox.showwarning("Empty Date", "Please enter a date or select from calendar")
        except ValueError as e:
            logger.warning(f"Invalid date entered: {e}")
            messagebox.showerror("Invalid Date", f"Please enter a valid date in DD.MM.YYYY format.\n\nError: {e}")

    def _cancel(self) -> None:
        """Cancel date selection."""
        self.result = None
        self.destroy()

    def _show_year_month_selector(self, event=None) -> None:
        """Show a dialog to select year and month directly."""
        try:
            # Create a simple dialog for year/month selection
            selector = tk.Toplevel(self)
            selector.title("Select Year and Month")
            selector.resizable(False, False)
            selector.transient(self)
            selector.grab_set()
            
            # Main frame
            main_frame = ttk.Frame(selector, padding=15)
            main_frame.pack(fill=tk.BOTH, expand=True)
            
            # Year selection
            ttk.Label(main_frame, text="Year:", font=("TkDefaultFont", 10)).grid(row=0, column=0, sticky=tk.W, pady=10)
            year_var = tk.StringVar(value=str(self.current_date.year))
            year_spinbox = ttk.Spinbox(
                main_frame,
                from_=1900,
                to=2100,
                textvariable=year_var,
                width=12,
                font=("TkDefaultFont", 11)
            )
            year_spinbox.grid(row=0, column=1, sticky=tk.EW, pady=10, padx=10)
            
            # Month selection
            ttk.Label(main_frame, text="Month:", font=("TkDefaultFont", 10)).grid(row=1, column=0, sticky=tk.W, pady=10)
            month_names = [
                "January", "February", "March", "April", "May", "June",
                "July", "August", "September", "October", "November", "December"
            ]
            month_var = tk.StringVar(value=month_names[self.current_date.month - 1])
            month_combo = ttk.Combobox(
                main_frame,
                textvariable=month_var,
                values=month_names,
                state="readonly",
                width=18,
                font=("TkDefaultFont", 11)
            )
            month_combo.grid(row=1, column=1, sticky=tk.EW, pady=10, padx=10)
            
            # Configure column weights
            main_frame.columnconfigure(1, weight=1)
            
            # Buttons
            button_frame = ttk.Frame(selector)
            button_frame.pack(fill=tk.X, padx=10, pady=15)
            
            def apply_selection():
                try:
                    year = int(year_var.get())
                    month = month_names.index(month_var.get()) + 1
                    self.current_date = date(year, month, 1)
                    self._update_month_year_display()
                    self._populate_calendar()
                    selector.destroy()
                    logger.debug(f"Year/Month selected: {self.current_date}")
                except ValueError as e:
                    messagebox.showerror("Invalid Input", f"Please enter valid year and month: {e}")
            
            ttk.Button(button_frame, text="OK", command=apply_selection).pack(side=tk.LEFT, padx=5)
            ttk.Button(button_frame, text="Cancel", command=selector.destroy).pack(side=tk.LEFT, padx=5)
            
            selector.geometry("320x180")
            selector.update_idletasks()
            # Center on parent
            x = self.winfo_x() + (self.winfo_width() // 2) - (selector.winfo_width() // 2)
            y = self.winfo_y() + (self.winfo_height() // 2) - (selector.winfo_height() // 2)
            selector.geometry(f"+{x}+{y}")
        except Exception as e:
            logger.error(f"Error in year/month selector: {e}")
            messagebox.showerror("Error", f"Failed to open year/month selector: {e}")

    def show(self) -> Optional[date]:
        """Show dialog and wait for result.
        
        Returns:
            Selected date or None if cancelled.
        """
        self.update_idletasks()
        parent = self.master
        x = parent.winfo_x() + (parent.winfo_width() // 2) - (self.winfo_width() // 2)
        y = parent.winfo_y() + (parent.winfo_height() // 2) - (self.winfo_height() // 2)
        self.geometry(f"+{x}+{y}")
        
        self.wait_window()
        return self.result

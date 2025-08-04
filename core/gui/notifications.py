"""
Non-blocking notification system for NovelWriter.

Replaces blocking messagebox.showinfo calls with non-blocking notifications
that don't interrupt the workflow.
"""

import tkinter as tk
from tkinter import ttk
import threading
import time
from typing import Optional, Callable


class NotificationManager:
    """
    Manages non-blocking notifications that appear briefly and auto-dismiss.
    """
    
    def __init__(self, parent_window: tk.Tk):
        self.parent = parent_window
        self.notifications = []
        self.notification_counter = 0
    
    def show_success(self, title: str, message: str, duration: int = 3000, 
                    callback: Optional[Callable] = None):
        """Show a success notification that auto-dismisses."""
        self._show_notification(title, message, "success", duration, callback)
    
    def show_info(self, title: str, message: str, duration: int = 3000,
                 callback: Optional[Callable] = None):
        """Show an info notification that auto-dismisses."""
        self._show_notification(title, message, "info", duration, callback)
    
    def show_warning(self, title: str, message: str, duration: int = 4000,
                    callback: Optional[Callable] = None):
        """Show a warning notification that auto-dismisses."""
        self._show_notification(title, message, "warning", duration, callback)
    
    def show_error(self, title: str, message: str, duration: int = 5000,
                  callback: Optional[Callable] = None):
        """Show an error notification that auto-dismisses."""
        self._show_notification(title, message, "error", duration, callback)
    
    def _show_notification(self, title: str, message: str, notification_type: str,
                          duration: int, callback: Optional[Callable] = None):
        """Create and show a notification window."""
        
        # Create notification window
        notification = tk.Toplevel(self.parent)
        notification.title(title)
        
        # Configure window
        notification.resizable(False, False)
        notification.attributes('-topmost', True)
        
        # Position window (stack notifications)
        self.notification_counter += 1
        x_offset = 20
        y_offset = 20 + (self.notification_counter - 1) * 120
        
        # Get parent window position
        self.parent.update_idletasks()
        parent_x = self.parent.winfo_x()
        parent_y = self.parent.winfo_y()
        parent_width = self.parent.winfo_width()
        
        # Position notification in top-right of parent
        notification_x = parent_x + parent_width - 350 - x_offset
        notification_y = parent_y + y_offset
        
        notification.geometry(f"350x100+{notification_x}+{notification_y}")
        
        # Configure colors based on type
        colors = {
            "success": {"bg": "#d4edda", "fg": "#155724", "border": "#c3e6cb"},
            "info": {"bg": "#d1ecf1", "fg": "#0c5460", "border": "#bee5eb"},
            "warning": {"bg": "#fff3cd", "fg": "#856404", "border": "#ffeaa7"},
            "error": {"bg": "#f8d7da", "fg": "#721c24", "border": "#f5c6cb"}
        }
        
        color_scheme = colors.get(notification_type, colors["info"])
        
        # Configure notification window
        notification.configure(bg=color_scheme["border"])
        
        # Create main frame
        main_frame = tk.Frame(
            notification,
            bg=color_scheme["bg"],
            relief="solid",
            bd=1
        )
        main_frame.pack(fill="both", expand=True, padx=2, pady=2)
        
        # Add icon/symbol
        symbols = {
            "success": "✅",
            "info": "ℹ️",
            "warning": "⚠️",
            "error": "❌"
        }
        
        symbol = symbols.get(notification_type, "ℹ️")
        
        # Title frame
        title_frame = tk.Frame(main_frame, bg=color_scheme["bg"])
        title_frame.pack(fill="x", padx=10, pady=(10, 5))
        
        # Symbol and title
        tk.Label(
            title_frame,
            text=symbol,
            font=("Arial", 12),
            bg=color_scheme["bg"],
            fg=color_scheme["fg"]
        ).pack(side="left")
        
        tk.Label(
            title_frame,
            text=title,
            font=("Arial", 10, "bold"),
            bg=color_scheme["bg"],
            fg=color_scheme["fg"]
        ).pack(side="left", padx=(5, 0))
        
        # Message
        message_label = tk.Label(
            main_frame,
            text=message,
            font=("Arial", 9),
            bg=color_scheme["bg"],
            fg=color_scheme["fg"],
            wraplength=320,
            justify="left"
        )
        message_label.pack(fill="x", padx=10, pady=(0, 10))
        
        # Close button (optional - notification will auto-close)
        close_btn = tk.Button(
            main_frame,
            text="×",
            font=("Arial", 12, "bold"),
            bg=color_scheme["bg"],
            fg=color_scheme["fg"],
            relief="flat",
            bd=0,
            command=lambda: self._close_notification(notification),
            cursor="hand2"
        )
        close_btn.place(relx=1.0, rely=0.0, anchor="ne", x=-5, y=5)
        
        # Store notification reference
        self.notifications.append(notification)
        
        # Auto-close after duration
        def auto_close():
            time.sleep(duration / 1000.0)  # Convert ms to seconds
            try:
                if notification.winfo_exists():
                    self.parent.after(0, lambda: self._close_notification(notification))
                    if callback:
                        self.parent.after(0, callback)
            except tk.TclError:
                pass  # Window already destroyed
        
        # Run auto-close in background thread
        threading.Thread(target=auto_close, daemon=True).start()
        
        return notification
    
    def _close_notification(self, notification: tk.Toplevel):
        """Close a notification and clean up."""
        try:
            if notification in self.notifications:
                self.notifications.remove(notification)
            notification.destroy()
            self.notification_counter = max(0, self.notification_counter - 1)
        except tk.TclError:
            pass  # Window already destroyed
    
    def close_all(self):
        """Close all active notifications."""
        for notification in self.notifications.copy():
            self._close_notification(notification)


class ProgressNotification:
    """
    A persistent notification that shows progress and can be updated.
    """
    
    def __init__(self, parent_window: tk.Tk, title: str, initial_message: str = ""):
        self.parent = parent_window
        self.notification = None
        self.progress_var = None
        self.message_var = None
        self.progress_bar = None
        
        self._create_notification(title, initial_message)
    
    def _create_notification(self, title: str, initial_message: str):
        """Create the progress notification window."""
        
        self.notification = tk.Toplevel(self.parent)
        self.notification.title(title)
        self.notification.resizable(False, False)
        self.notification.attributes('-topmost', True)
        
        # Position window
        self.parent.update_idletasks()
        parent_x = self.parent.winfo_x()
        parent_y = self.parent.winfo_y()
        parent_width = self.parent.winfo_width()
        
        notification_x = parent_x + parent_width - 400 - 20
        notification_y = parent_y + 20
        
        self.notification.geometry(f"400x120+{notification_x}+{notification_y}")
        self.notification.configure(bg="#e3f2fd")
        
        # Main frame
        main_frame = tk.Frame(self.notification, bg="#e3f2fd", relief="solid", bd=1)
        main_frame.pack(fill="both", expand=True, padx=2, pady=2)
        
        # Title
        title_label = tk.Label(
            main_frame,
            text=f"🚀 {title}",
            font=("Arial", 11, "bold"),
            bg="#e3f2fd",
            fg="#1565c0"
        )
        title_label.pack(pady=(10, 5))
        
        # Message
        self.message_var = tk.StringVar(value=initial_message)
        message_label = tk.Label(
            main_frame,
            textvariable=self.message_var,
            font=("Arial", 9),
            bg="#e3f2fd",
            fg="#1565c0",
            wraplength=380
        )
        message_label.pack(pady=(0, 10))
        
        # Progress bar
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(
            main_frame,
            variable=self.progress_var,
            maximum=100,
            length=360,
            mode='determinate'
        )
        self.progress_bar.pack(pady=(0, 10))
    
    def update_progress(self, percentage: float, message: str = None):
        """Update the progress bar and optionally the message."""
        if self.notification and self.notification.winfo_exists():
            self.progress_var.set(percentage)
            if message:
                self.message_var.set(message)
            self.notification.update()
    
    def update_message(self, message: str):
        """Update just the message."""
        if self.notification and self.notification.winfo_exists():
            self.message_var.set(message)
            self.notification.update()
    
    def close(self):
        """Close the progress notification."""
        if self.notification:
            try:
                self.notification.destroy()
            except tk.TclError:
                pass


# Global notification manager (will be initialized by the main app)
_notification_manager: Optional[NotificationManager] = None


def init_notifications(parent_window: tk.Tk):
    """Initialize the global notification manager."""
    global _notification_manager
    _notification_manager = NotificationManager(parent_window)


def show_success(title: str, message: str, duration: int = 3000):
    """Show a non-blocking success notification."""
    if _notification_manager:
        _notification_manager.show_success(title, message, duration)


def show_info(title: str, message: str, duration: int = 3000):
    """Show a non-blocking info notification."""
    if _notification_manager:
        _notification_manager.show_info(title, message, duration)


def show_warning(title: str, message: str, duration: int = 4000):
    """Show a non-blocking warning notification."""
    if _notification_manager:
        _notification_manager.show_warning(title, message, duration)


def show_error(title: str, message: str, duration: int = 5000):
    """Show a non-blocking error notification."""
    if _notification_manager:
        _notification_manager.show_error(title, message, duration)


def create_progress_notification(title: str, initial_message: str = "") -> ProgressNotification:
    """Create a progress notification that can be updated."""
    if _notification_manager:
        return ProgressNotification(_notification_manager.parent, title, initial_message)
    return None

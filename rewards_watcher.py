# rewards_watcher.py
import logging
import platform
import subprocess
import threading
import time
import tkinter as tk
from enum import Enum
from typing import Optional

logger = logging.getLogger(__name__)

class WatcherState(Enum):
    """State machine for RewardsWatcher."""
    IDLE = "idle"
    MONITORING = "monitoring"
    SHUTDOWN_PENDING = "shutdown_pending"
    SHUTDOWN_CANCELLED = "shutdown_cancelled"

class RewardsWatcher(threading.Thread):
    def __init__(self, config, data_manager, gui=None):
        super().__init__(daemon=True)
        self.config = config
        self.data_manager = data_manager
        self.gui = gui
        self.logger = logging.getLogger(__name__)
        
        self.state = WatcherState.IDLE
        self._stop_event = threading.Event()
        self.running = False
        self.logger.info("RewardsWatcher initialized.")

    def run(self):
        """Main loop for monitoring and updating GUI with rewards data."""
        self.running = True
        self.state = WatcherState.MONITORING
        self.logger.info("RewardsWatcher started.")
        
        try:
            while self.running and not self._stop_event.is_set():
                if self.state == WatcherState.MONITORING:
                    rewards_complete = self.data_manager.rewards_completed
                    loop_complete = self.data_manager.loop_completed
                    shutdown_enabled = self.is_shutdown_enabled()
                    
                    self.logger.debug(
                        f"State: {self.state}, Rewards: {rewards_complete}, "
                        f"Loop: {loop_complete}, Shutdown Enabled: {shutdown_enabled}"
                    )
                    
                    if rewards_complete and loop_complete and shutdown_enabled:
                        self._transition_to_shutdown_pending()
                    elif self.gui:
                        counts = self.data_manager.get_current_counts()
                        self.gui.update_total_label(counts['total'])
                        self.gui.update_rewards_label(counts['rewards'])
                
                time.sleep(self.config.poll_interval)
        except Exception as e:
            self.logger.error(f"Error in RewardsWatcher: {e}", exc_info=True)
        finally:
            self.running = False
            self.logger.info("RewardsWatcher stopped.")

    def stop(self):
        """Gracefully stop the watcher."""
        self.logger.info("Stopping RewardsWatcher...")
        self.running = False
        self._stop_event.set()
        try:
            self.join(timeout=5)
        except KeyboardInterrupt:
            self.logger.warning("Interrupted while waiting for RewardsWatcher to stop.")

    def is_shutdown_enabled(self) -> bool:
        """Check if the GUI shutdown checkbox is enabled."""
        if self.gui and hasattr(self.gui, 'shutdown_var'):
            return self.gui.shutdown_var.get()
        return False

    def reset(self):
        """Reset the watcher state back to MONITORING for a new search session."""
        self.logger.info("Resetting watcher state to MONITORING.")
        self.state = WatcherState.MONITORING

    def _transition_to_shutdown_pending(self):
        """Transition to shutdown pending state and show dialog."""
        self.logger.info("Conditions met, transitioning to SHUTDOWN_PENDING.")
        self.state = WatcherState.SHUTDOWN_PENDING
        if hasattr(self.gui, "root"):
            self.gui.root.after(0, self._show_shutdown_dialog)
        else:
            self._execute_shutdown()

    def _show_shutdown_dialog(self):
        """Show shutdown dialog with 60-second countdown."""
        dialog = tk.Toplevel(self.gui.root)
        dialog.title("System Shutdown Scheduled")
        dialog.geometry("440x260")
        dialog.configure(bg="#f5f5f5")
        dialog.resizable(False, False)
        dialog.grab_set()
        dialog.protocol("WM_DELETE_WINDOW", lambda: None)

        # Header
        header = tk.Label(
            dialog,
            text="⚠️ Scheduled Shutdown",
            font=("Segoe UI", 16, "bold"),
            fg="#d9534f",
            bg="#f5f5f5"
        )
        header.pack(pady=(18, 6))

        # Message
        msg = tk.Label(
            dialog,
            text="Your system will automatically shutdown in 60 seconds.\nClick the button below to cancel.",
            font=("Segoe UI", 12),
            fg="#333",
            bg="#f5f5f5",
            justify="center"
        )
        msg.pack(pady=(0, 10))

        # Countdown display
        countdown_var = tk.StringVar(value="60")
        countdown_frame = tk.Frame(dialog, bg="#f5f5f5")
        countdown_frame.pack(pady=(0, 10))
        
        tk.Label(
            countdown_frame,
            text="Time remaining:",
            font=("Segoe UI", 11),
            fg="#555",
            bg="#f5f5f5"
        ).pack(side="left")
        tk.Label(
            countdown_frame,
            textvariable=countdown_var,
            font=("Segoe UI", 14, "bold"),
            fg="#d9534f",
            bg="#f5f5f5",
            width=4
        ).pack(side="left", padx=(8, 0))

        # Cancel button
        def cancel_shutdown():
            self.logger.info("Shutdown cancelled by user.")
            self.state = WatcherState.SHUTDOWN_CANCELLED
            dialog.destroy()
            # Reset state back to MONITORING so dialog can show again if conditions are met
            self.state = WatcherState.MONITORING

        cancel_btn = tk.Button(
            dialog,
            text="Cancel Shutdown",
            command=cancel_shutdown,
            font=("Segoe UI", 12, "bold"),
            bg="#5bc0de",
            fg="white",
            activebackground="#31b0d5",
            activeforeground="white",
            relief="raised",
            bd=2,
            cursor="hand2",
            width=20
        )
        cancel_btn.pack(pady=(18, 24))

        # Countdown timer
        def countdown(secs):
            if self.state != WatcherState.SHUTDOWN_PENDING:
                return
            countdown_var.set(str(secs))
            if secs > 0:
                dialog.after(1000, countdown, secs - 1)
            else:
                dialog.destroy()
                if self.state == WatcherState.SHUTDOWN_PENDING:
                    self._execute_shutdown()

        countdown(60)

    def _execute_shutdown(self):
        """Execute system shutdown command."""
        self.logger.info("Executing system shutdown.")
        system_name = platform.system().lower()
        try:
            if system_name.startswith("win"):
                subprocess.run(["shutdown", "/s", "/t", "0"], check=True)
            elif system_name.startswith("linux") or system_name.startswith("darwin"):
                subprocess.run(["sudo", "shutdown", "-h", "now"], check=True)
            else:
                self.logger.warning(f"Unsupported platform for shutdown: {system_name}")
        except Exception as e:
            self.logger.error(f"Failed to execute shutdown: {e}")

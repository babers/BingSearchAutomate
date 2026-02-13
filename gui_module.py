# gui_module.py - Tkinter-based GUI for Bing Search Automator

import tkinter as tk
from tkinter import ttk
import logging
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.ticker import MaxNLocator
from utils.elapsed_timer import get_elapsed, start as start_timer, stop as stop_timer
from utils.network import is_connected

class GUI:
    def __init__(self, config, data_manager, browser_controller, *args, **kwargs):
        self.config = config
        self.data_manager = data_manager
        self.browser_controller = browser_controller
        self.rewards_watcher = None

        if not hasattr(self, "root"):
            self.root = tk.Tk()

        self.logger = logging.getLogger(__name__)
        
        self.root.title("Bing Search Automator (Headless)")
        self.search_started = False
        self.setup_ui()
        self.schedule_update()
        
        self._pause_after_id = None
        self._remaining_pause_seconds = 0

    def setup_ui(self):
        """Setup the user interface."""
        main_frame = tk.Frame(self.root, padx=20, pady=20)
        main_frame.pack(expand=True, fill=tk.BOTH)

        # Stats Frame
        stats_frame = ttk.LabelFrame(main_frame, text="Current Status")
        stats_frame.pack(fill=tk.X, pady=5)

        self.total_label = ttk.Label(stats_frame, text="Total Searches: 0")
        self.total_label.pack(side=tk.LEFT, padx=10, pady=5)

        self.rewards_label = ttk.Label(stats_frame, text="Rewards Points: 0")
        self.rewards_label.pack(side=tk.LEFT, padx=10, pady=5)
        
        try:
            self.elapsed_label = ttk.Label(stats_frame, text="Elapsed: 00:00:00")
            self.elapsed_label.pack(side=tk.LEFT, padx=10, pady=5)
        except Exception:
            self.elapsed_label = tk.Label(stats_frame, text="Elapsed: 00:00:00")
            self.elapsed_label.pack(side=tk.LEFT, padx=10, pady=5)

        self.network_label = ttk.Label(stats_frame, text="Network: Unknown", foreground="gray")
        self.network_label.pack(side=tk.LEFT, padx=10, pady=5)

        # Control Frame
        control_frame = ttk.LabelFrame(main_frame, text="Controls")
        control_frame.pack(fill=tk.X, pady=5)

        self.start_btn = ttk.Button(control_frame, text="Start Searching", command=self.start_searching, width=15)
        self.start_btn.pack(side=tk.LEFT, padx=5, pady=5)

        self.stop_btn = ttk.Button(control_frame, text="Stop", command=self.stop_searching, state=tk.DISABLED, width=15)
        self.stop_btn.pack(side=tk.LEFT, padx=5, pady=5)

        # Topic Frame
        topic_frame = ttk.LabelFrame(main_frame, text="Current Topic")
        topic_frame.pack(fill=tk.X, pady=5)
        self.topic_label = ttk.Label(topic_frame, text="Topic: None")
        self.topic_label.pack(side=tk.LEFT, padx=10, pady=5)

        # Pause Timer Frame
        pause_frame = ttk.LabelFrame(main_frame, text="Pause Timer")
        pause_frame.pack(fill=tk.X, pady=5)
        self.pause_timer_label = ttk.Label(pause_frame, text="")
        self.pause_timer_label.pack(side=tk.LEFT, padx=10, pady=5)

        # Progress Frame with Graph
        progress_frame = ttk.LabelFrame(main_frame, text="Search Progress")
        progress_frame.pack(expand=True, fill=tk.BOTH, pady=5)

        # Create matplotlib figure and canvas
        self.figure = Figure(figsize=(8, 4), dpi=100)
        self.ax = self.figure.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.figure, master=progress_frame)
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

        # Initialize graph
        self._init_graph()

        # Shutdown checkbox
        self.shutdown_var = tk.BooleanVar(value=False)
        self.shutdown_checkbox = tk.Checkbutton(self.root, text="Shutdown PC when finished", variable=self.shutdown_var)
        self.shutdown_checkbox.pack(anchor="w", padx=8, pady=4)

        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)

    def _init_graph(self):
        """Initialize the graph with empty data."""
        self.ax.clear()
        self.ax.set_xlabel('Rewards Points')
        self.ax.set_ylabel('Search Number')
        self.ax.set_title('Rewards Points vs Searches')
        self.ax.grid(True, alpha=0.3)
        self.ax.xaxis.set_major_locator(MaxNLocator(integer=True))
        self.ax.yaxis.set_major_locator(MaxNLocator(integer=True))
        self.canvas.draw()

    def start_searching(self):
        """Start the search process."""
        if not self.search_started:
            self.logger.info("Start button clicked.")
            start_timer()
            self.data_manager.reset()
            # Reset watcher state to allow shutdown dialog to show again
            if hasattr(self, 'rewards_watcher') and self.rewards_watcher:
                self.rewards_watcher.reset()
            self.browser_controller.start_searching()
            self.search_started = True
            self.start_btn.config(state=tk.DISABLED)
            self.stop_btn.config(state=tk.NORMAL)

    def stop_searching(self):
        """Stop the search process."""
        if self.search_started:
            self.logger.info("Stop button clicked.")
            stop_timer()
            self.browser_controller.stop_searching()
            self.search_started = False
            self.start_btn.config(state=tk.NORMAL)
            self.stop_btn.config(state=tk.DISABLED)

    def update_total_label(self, total):
        """Update the total searches label (thread-safe)."""
        try:
            self.root.after(0, lambda: self.total_label.config(text=f"Total Searches: {total}"))
        except Exception as e:
            self.logger.warning(f"Could not update total label: {e}")

    def update_rewards_label(self, rewards):
        """Update the rewards points label (thread-safe)."""
        try:
            self.root.after(0, lambda: self.rewards_label.config(text=f"Rewards Points: {rewards}"))
        except Exception as e:
            self.logger.warning(f"Could not update rewards label: {e}")

    def set_current_topic(self, topic):
        """Set the current topic being searched (thread-safe)."""
        try:
            self.root.after(0, lambda: self.topic_label.config(text=f"Topic: {topic}"))
        except Exception as e:
            self.logger.warning(f"Could not update topic label: {e}")

    def set_pause_timer(self, seconds):
        """Start or reset the pause countdown safely."""
        def _start():
            try:
                if getattr(self, "_pause_after_id", None):
                    self.root.after_cancel(self._pause_after_id)
            except Exception:
                pass
            self._pause_after_id = None
            self._remaining_pause_seconds = int(max(0, seconds))
            self._tick_pause_timer()

        self.root.after(0, _start)

    def _tick_pause_timer(self):
        """Update the pause timer display and decrement."""
        if self._remaining_pause_seconds > 0:
            mins, secs = divmod(self._remaining_pause_seconds, 60)
            self.pause_timer_label.config(text=f"Paused: {mins:02d}:{secs:02d} remaining")
            self._remaining_pause_seconds -= 1
            self._pause_after_id = self.root.after(1000, self._tick_pause_timer)
        else:
            self.pause_timer_label.config(text="")

    def clear_pause_timer(self):
        """Clear the pause countdown and label safely."""
        def _clear():
            try:
                if getattr(self, "_pause_after_id", None):
                    self.root.after_cancel(self._pause_after_id)
            except Exception:
                pass
            self._pause_after_id = None
            self._remaining_pause_seconds = 0
            self.pause_timer_label.config(text="")

        self.root.after(0, _clear)

    def update_elapsed_time(self):
        """Update the elapsed time display (thread-safe)."""
        try:
            elapsed_seconds = int(get_elapsed())
            hours, remainder = divmod(elapsed_seconds, 3600)
            minutes, seconds = divmod(remainder, 60)
            time_str = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
            self.root.after(0, lambda: self.elapsed_label.config(text=f"Elapsed: {time_str}"))
        except Exception as e:
            self.logger.warning(f"Could not update elapsed time: {e}")

    def update_network_status(self):
        """Update the network status display (thread-safe)."""
        try:
            connected = is_connected()
            status = "Online" if connected else "Offline"
            color = "green" if connected else "red"
            def _update():
                try:
                    self.network_label.config(text=f"Network: {status}", foreground=color)
                except Exception:
                    pass
            self.root.after(0, _update)
        except Exception as e:
            self.logger.warning(f"Could not update network status: {e}")

    def update_graph(self):
        """Update the graph with current session data (thread-safe)."""
        try:
            def _update_graph():
                try:
                    self.ax.clear()
                    
                    # Get session search history from data_manager
                    session_history = getattr(self.data_manager, 'session_search_history', [])
                    
                    if session_history:
                        search_indices = [item[0] for item in session_history]
                        rewards_points = [item[1] for item in session_history]
                        
                        # Plot: X axis = rewards points, Y axis = search number
                        self.ax.plot(rewards_points, search_indices, marker='o', linestyle='-', color='b', linewidth=2, markersize=6)
                    
                    self.ax.set_xlabel('Rewards Points')
                    self.ax.set_ylabel('Search Number')
                    self.ax.set_title('Rewards Points vs Searches')
                    self.ax.grid(True, alpha=0.3)
                    self.ax.xaxis.set_major_locator(MaxNLocator(integer=True))
                    self.ax.yaxis.set_major_locator(MaxNLocator(integer=True))
                    self.canvas.draw()
                except Exception as e:
                    self.logger.warning(f"Error updating graph: {e}")
            
            self.root.after(0, _update_graph)
        except Exception as e:
            self.logger.warning(f"Could not update graph: {e}")

    def schedule_update(self):
        """Periodically update the GUI (for async operations)."""
        try:
            self.root.update()
            self.update_elapsed_time()
            self.update_network_status()
            self.update_graph()
        except Exception:
            pass
        self.root.after(1000, self.schedule_update)

    def start(self):
        """Start the GUI main loop."""
        self.root.mainloop()

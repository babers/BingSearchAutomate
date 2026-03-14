# gui_module.py - Tkinter-based GUI for Bing Search Automator

import tkinter as tk
from tkinter import ttk, messagebox
from tkinter import scrolledtext
import logging
import os
import webbrowser
from datetime import datetime
from typing import Optional
import yaml as pyyaml
try:
    import winsound
except ImportError:
    winsound = None
try:
    from ruamel.yaml import YAML
    from ruamel.yaml.comments import CommentedMap
except ImportError:
    YAML = None
    CommentedMap = dict
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.ticker import MaxNLocator
from config import deep_merge
from utils.elapsed_timer import get_elapsed, start as start_timer, stop as stop_timer
from utils.network import is_connected
from utils.metrics import MetricsCollector
from version import __version__

class GUI:
    def __init__(self, config, data_manager, browser_controller, *args, **kwargs):
        self.config = config
        self.data_manager = data_manager
        self.browser_controller = browser_controller
        self.rewards_watcher = None
        self.metrics_collector = MetricsCollector()

        if not hasattr(self, "root"):
            self.root = tk.Tk()

        self.logger = logging.getLogger(__name__)
        self._config_vars = {}
        self._config_widgets = {}
        self._profile_locked_widget_keys = []
        self._field_lock_labels = {}  # Track label widgets for badge updates
        self._profile_overrides = {}  # Map profile name to set of (section, key) that it overrides
        self._config_window = None
        self._config_profile_var = None
        self._profile_names = []
        self._config_data_snapshot = None
        self._completion_dialog_shown = False
        self._session_start_time = None
        self._session_completion_time = None
        self._yaml_rt = YAML() if YAML else None
        if self._yaml_rt:
            self._yaml_rt.preserve_quotes = True
            self._yaml_rt.indent(mapping=2, sequence=4, offset=2)
            self._yaml_rt.width = 120
        
        self.root.title(f"Bing Search Automator v{__version__}")
        self.search_started = False
        self.setup_ui()
        self.schedule_update()
        
        self._pause_after_id = None
        self._remaining_pause_seconds = 0

    def setup_ui(self):
        """Setup the user interface."""
        self._setup_menu()

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

        self.mode_label = ttk.Label(
            stats_frame,
            text=f"Selected Mode: {self._get_selected_mode_name()}"
        )
        self.mode_label.pack(side=tk.LEFT, padx=10, pady=5)

        self.status_label = ttk.Label(stats_frame, text="Status: Idle", foreground="gray")
        self.status_label.pack(side=tk.LEFT, padx=10, pady=5)

        self.network_label = ttk.Label(stats_frame, text="Network: Unknown", foreground="gray")
        self.network_label.pack(side=tk.LEFT, padx=10, pady=5)

        # Statistics Frame (NEW)
        metrics_frame = ttk.LabelFrame(main_frame, text="Session Statistics")
        metrics_frame.pack(fill=tk.X, pady=5)

        self.success_rate_label = ttk.Label(metrics_frame, text="Success Rate: N/A")
        self.success_rate_label.pack(side=tk.LEFT, padx=10, pady=5)

        self.searches_per_min_label = ttk.Label(metrics_frame, text="Searches/min: 0.0")
        self.searches_per_min_label.pack(side=tk.LEFT, padx=10, pady=5)

        self.points_per_search_label = ttk.Label(metrics_frame, text="Points/Search: 0.0")
        self.points_per_search_label.pack(side=tk.LEFT, padx=10, pady=5)

        self.eta_label = ttk.Label(metrics_frame, text="ETA: --:--:--")
        self.eta_label.pack(side=tk.LEFT, padx=10, pady=5)

        self.start_time_label = ttk.Label(metrics_frame, text="Start: --")
        self.start_time_label.pack(side=tk.LEFT, padx=10, pady=5)

        self.completion_time_label = ttk.Label(metrics_frame, text="Completed At: --")
        self.completion_time_label.pack(side=tk.LEFT, padx=10, pady=5)

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

    def _setup_menu(self):
        """Create top-level application menu."""
        menubar = tk.Menu(self.root)

        settings_menu = tk.Menu(menubar, tearoff=0)
        settings_menu.add_command(label="Config", command=self.open_config_settings)
        menubar.add_cascade(label="Settings", menu=settings_menu)

        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="About", command=self._show_about_dialog)
        help_menu.add_command(label="Documentation", command=self._show_documentation_window)
        menubar.add_cascade(label="Help", menu=help_menu)

        self.root.config(menu=menubar)

    def _show_about_dialog(self):
        """Show basic software information."""
        dialog = tk.Toplevel(self.root)
        dialog.title("About Bing Search Automator")
        dialog.geometry("560x330")
        dialog.configure(bg="#f7f9fc")
        dialog.resizable(False, False)
        dialog.transient(self.root)
        dialog.grab_set()

        self.root.update_idletasks()
        width, height = 560, 330
        x = self.root.winfo_rootx() + max(0, (self.root.winfo_width() - width) // 2)
        y = self.root.winfo_rooty() + max(0, (self.root.winfo_height() - height) // 2)
        dialog.geometry(f"{width}x{height}+{x}+{y}")

        tk.Label(
            dialog,
            text="Bing Search Automator",
            font=("Segoe UI", 18, "bold"),
            fg="#0b6e4f",
            bg="#f7f9fc"
        ).pack(pady=(22, 8))

        info_text = (
            f"Version: {__version__}\n"
            f"Author: Baber Saeed\n"
            f"Platform: Windows\n\n"
            "Automates Bing searches with configurable stealth settings,\n"
            "real-time metrics, and profile-based runtime behavior."
        )
        tk.Label(
            dialog,
            text=info_text,
            font=("Segoe UI", 11),
            fg="#1f2937",
            bg="#f7f9fc",
            justify="center"
        ).pack(pady=(0, 16))

        repo_label = tk.Label(
            dialog,
            text="Git Repository: https://github.com/babers/BingSearchAutomate",
            font=("Segoe UI", 10, "underline"),
            fg="#0b57d0",
            bg="#f7f9fc",
            cursor="hand2"
        )
        repo_label.pack(pady=(0, 14))
        repo_label.bind(
            "<Button-1>",
            lambda _e: webbrowser.open_new_tab("https://github.com/babers/BingSearchAutomate")
        )

        ttk.Button(dialog, text="Close", command=dialog.destroy).pack(pady=(0, 16))

    def _show_documentation_window(self):
        """Show a detailed in-app user manual for all UI options."""
        window = tk.Toplevel(self.root)
        window.title("Documentation - User Manual")
        window.geometry("960x720")
        window.transient(self.root)

        container = ttk.Frame(window, padding=10)
        container.pack(fill=tk.BOTH, expand=True)

        header = ttk.Label(
            container,
            text="Bing Search Automator - User Manual",
            font=("Segoe UI", 14, "bold")
        )
        header.pack(anchor='w', pady=(0, 8))

        manual_box = scrolledtext.ScrolledText(
            container,
            wrap=tk.WORD,
            font=("Consolas", 10),
            padx=10,
            pady=10
        )
        manual_box.pack(fill=tk.BOTH, expand=True)
        manual_box.insert('1.0', self._build_user_manual_text())
        manual_box.config(state=tk.DISABLED)

    def _build_user_manual_text(self) -> str:
        """Return detailed user manual text for all UI controls and options."""
        return (
            "BING SEARCH AUTOMATOR - USER MANUAL\n"
            "="
            "="
            "="
            "="
            "="
            "="
            "="
            "="
            "="
            "="
            "="
            "="
            "="
            "="
            "="
            "="
            "="
            "="
            "="
            "="
            "="
            "="
            "="
            "="
            "="
            "="
            "="
            "="
            "="
            "="
            "="
            "="
            "="
            "="
            "="
            "="
            "="
            "="
            "="
            "="
            "="
            "="
            "="
            "="
            "="
            "="
            "="
            "="
            "="
            "="
            "="
            "="
            "="
            "="
            "="
            "="
            "="
            "="
            "="
            "="
            "="
            "="
            "="
            "="
            "="
            "=\n\n"
            "1. CURRENT STATUS PANEL\n"
            "- Total Searches: Number of searches performed in current session.\n"
            "- Rewards Points: Current rewards points value from Bing.\n"
            "- Elapsed: Session runtime clock from start until stop/completion.\n"
            "- Selected Mode: Active profile name (or Custom).\n"
            "- Status: Idle, Running, Stopped, or Completed.\n"
            "- Network: Online/Offline connectivity indicator.\n\n"
            "2. SESSION STATISTICS PANEL\n"
            "- Success Rate: Percent of searches that gained points.\n"
            "- Searches/min: Search speed in current session.\n"
            "- Points/Search: Average points gain per search.\n"
            "- ETA: Estimated time remaining to target points.\n"
            "- Start: Actual system time when Start Searching is clicked.\n"
            "- Completed At: Actual system time when target points are reached.\n\n"
            "3. CONTROLS PANEL\n"
            "- Start Searching: Starts a new session and resets session counters.\n"
            "- Stop: Requests graceful stop of the running search loop.\n"
            "  Note: On completion, Start is re-enabled and Stop is disabled automatically.\n\n"
            "4. CURRENT TOPIC PANEL\n"
            "- Displays the current search topic used for automation.\n"
            "- In runtime mode, generated topics are also written to logging/topics.log.\n\n"
            "5. PAUSE TIMER PANEL\n"
            "- Shows adaptive pause countdown when no-gain threshold is reached.\n"
            "- Clears automatically when pause ends or when session stops.\n\n"
            "6. SEARCH PROGRESS PANEL\n"
            "- Live chart plotting rewards points by search number.\n"
            "- X-axis: Search Number, Y-axis: Rewards Points.\n\n"
            "7. SETTINGS > CONFIG\n"
            "Open via top menu: Settings > Config\n"
            "Tabs available:\n"
            "- Profiles: Select predefined profile or Custom mode.\n"
            "- Search: Target points, pauses, sleep times, polling, topic strategy.\n"
            "- Browser: Headless mode, slow motion, storage state, channel.\n"
            "- Proxy: Enable proxy, rotation strategy, proxy list.\n"
            "- Stealth: Typing mistakes, probability, mouse movements, scrolling.\n"
            "- Logging: Log level and log format.\n\n"
            "Profile behavior:\n"
            "- In predefined profiles, only overridden fields are locked (shown with lock icon).\n"
            "- Non-overridden fields remain editable.\n"
            "- In Custom mode, all editable fields are unlocked.\n"
            "- Saving applies settings immediately at runtime.\n\n"
            "8. HELP MENU\n"
            "- Help > About: software name, version, author information.\n"
            "- Help > Documentation: opens this detailed manual.\n\n"
            "9. COMPLETION BEHAVIOR\n"
            "- When target points are achieved:\n"
            "  * Status changes to Completed.\n"
            "  * Completion dialog appears centered in dashboard area.\n"
            "  * Audible completion chime is played.\n"
            "  * Dialog auto-closes after 60 seconds.\n\n"
            "10. LOG FILES\n"
            "- logging/app.log: Main application logs.\n"
            "- logging/topics.log: Runtime-generated search topics with timestamps.\n"
        )

    def _get_selected_mode_name(self):
        """Return a user-friendly mode name based on active profile."""
        active_profile = getattr(self.config, 'active_profile', None)
        if not active_profile:
            return "Custom"
        return str(active_profile).replace('_', ' ').title()

    def _get_config_file_path(self) -> str:
        """Resolve the writable config file path for UI edits."""
        cfg_path = getattr(self.config, 'source_config_path', 'config.yaml')
        if os.path.isfile(cfg_path):
            return cfg_path
        return 'config.yaml'

    def _load_config_dict(self):
        """Load raw YAML config as a dict for editing/saving."""
        config_path = self._get_config_file_path()
        with open(config_path, 'r', encoding='utf-8') as f:
            if self._yaml_rt:
                data = self._yaml_rt.load(f) or CommentedMap()
            else:
                data = pyyaml.safe_load(f) or {}
        return data, config_path

    def open_config_settings(self):
        """Open settings dialog for editable config sections."""
        if self._config_window and self._config_window.winfo_exists():
            self._config_window.lift()
            self._config_window.focus_force()
            return

        try:
            config_data, config_path = self._load_config_dict()
        except Exception as e:
            messagebox.showerror("Config Error", f"Failed to load config file:\n{e}")
            return

        window = tk.Toplevel(self.root)
        window.title("Configuration Settings")
        window.geometry("760x700")
        window.transient(self.root)
        window.grab_set()
        self._config_window = window

        container = ttk.Frame(window, padding=12)
        container.pack(fill=tk.BOTH, expand=True)

        note = ttk.Label(
            container,
            text=(
                "Editable sections: Search, Browser, Proxy, Stealth, and Logging. "
                "Settings are applied immediately after save."
            ),
            foreground="gray"
        )
        note.pack(anchor='w', pady=(0, 8))

        notebook = ttk.Notebook(container)
        notebook.pack(fill=tk.BOTH, expand=True)

        self._config_vars = {}
        self._config_widgets = {}
        self._field_lock_labels = {}
        self._profile_locked_widget_keys = []
        self._config_data_snapshot = config_data

        self._create_profiles_tab(notebook, config_data)

        self._create_search_settings_tab(notebook, config_data)
        self._create_browser_tab(notebook, config_data)
        self._create_proxy_tab(notebook, config_data)
        self._create_stealth_tab(notebook, config_data)
        self._create_logging_tab(notebook, config_data)

        self._apply_profile_ui_state()

        footer = ttk.Frame(container)
        footer.pack(fill=tk.X, pady=(10, 0))

        ttk.Label(footer, text=f"Config file: {config_path}", foreground="gray").pack(side=tk.LEFT)
        ttk.Button(footer, text="Defaults", command=self._set_defaults_in_form).pack(side=tk.RIGHT, padx=6)
        ttk.Button(footer, text="Save", command=lambda: self._save_config_from_ui(config_path)).pack(side=tk.RIGHT, padx=6)
        ttk.Button(footer, text="Cancel", command=window.destroy).pack(side=tk.RIGHT)

    def _create_section_frame(self, notebook, title):
        frame = ttk.Frame(notebook, padding=12)
        notebook.add(frame, text=title)
        return frame
    
    def _build_profile_overrides_map(self, config_data):
        """Build map of which fields each profile overrides."""
        self._profile_overrides = {}
        profiles = config_data.get('profiles', {})
        
        for profile_name, profile_data in profiles.items():
            overridden = set()
            for section in ('search_settings', 'stealth', 'browser', 'logging', 'proxy'):
                if section in profile_data:
                    for key in profile_data[section].keys():
                        overridden.add((section, key))
            self._profile_overrides[profile_name] = overridden

    def _add_row(self, parent, row, label, widget, section=None, key_param=None):
        label_text = self._prettify_label(label)
        label_widget = ttk.Label(parent, text=label_text, width=28)
        label_widget.grid(row=row, column=0, sticky='w', padx=(0, 10), pady=6)
        
        # Store label widget reference for dynamic badge updates
        if section and key_param:
            self._field_lock_labels[(section, key_param)] = (label_widget, label_text)
        
        widget.grid(row=row, column=1, sticky='ew', pady=6)
        parent.columnconfigure(1, weight=1)

    def _register_widget(self, section, key, widget):
        """Register a config widget. Profile locking is determined dynamically in _apply_profile_ui_state()."""
        self._config_widgets[(section, key)] = widget

    def _create_profiles_tab(self, notebook, config_data):
        frame = self._create_section_frame(notebook, "Profiles")
        profiles = config_data.get('profiles', {})
        self._profile_names = sorted(list(profiles.keys()))
        self._build_profile_overrides_map(config_data)

        current_profile = config_data.get('active_profile') or getattr(self.config, 'active_profile', None)
        profile_options = ['Custom'] + self._profile_names
        if current_profile not in self._profile_names:
            current_profile = 'Custom'

        self._config_profile_var = tk.StringVar(value=current_profile if current_profile else 'Custom')
        profile_combo = ttk.Combobox(frame, textvariable=self._config_profile_var, values=profile_options, state='readonly')
        self._add_row(frame, 0, 'selected_profile', profile_combo)
        profile_combo.bind('<<ComboboxSelected>>', lambda _e: self._apply_profile_ui_state())

        note = ttk.Label(
            frame,
            text=(
                "Predefined: only profile-overridden fields are locked (marked with 🔒). Base fields remain editable. "
                "Custom: all fields editable."
            ),
            foreground='gray',
            wraplength=400
        )
        note.grid(row=1, column=0, columnspan=2, sticky='w', pady=(8, 0))

    def _apply_profile_ui_state(self):
        """Apply field-level locking based on which fields the selected profile actually overrides."""
        if not self._config_profile_var or not self._config_data_snapshot:
            return

        selected = self._config_profile_var.get()
        is_custom = selected == 'Custom'
        
        # Get which fields this profile overrides (if not Custom)
        profile_overrides = self._profile_overrides.get(selected, set()) if not is_custom else set()
        
        # Update all field states and labels
        for (section, key), widget in self._config_widgets.items():
            is_overridden = (section, key) in profile_overrides
            should_lock = is_overridden and not is_custom
            
            # Update widget state
            state = 'disabled' if should_lock else 'normal'
            try:
                widget.configure(state=state)
            except Exception:
                pass
            
            # Update label with badge or clear it
            if (section, key) in self._field_lock_labels:
                label_widget, base_text = self._field_lock_labels[(section, key)]
                if should_lock:
                    label_widget.config(text=f"{base_text} 🔒")
                else:
                    label_widget.config(text=base_text)
        
        # Update widget values to show profile overrides (preview)
        if not is_custom:
            profile_data = self._config_data_snapshot.get('profiles', {}).get(selected, {})
            for section_name in ('search_settings', 'browser', 'proxy', 'stealth', 'logging'):
                section_overrides = profile_data.get(section_name, {})
                for key, value in section_overrides.items():
                    var_info = self._config_vars.get((section_name, key))
                    if not var_info:
                        continue
                    widget_var, value_type = var_info
                    if value_type is list:
                        widget_var.delete('1.0', 'end')
                        widget_var.insert('1.0', '\n'.join(value))
                    else:
                        widget_var.set(value)

    def _prettify_label(self, key):
        """Convert config keys into user-friendly field labels."""
        custom = {
            'slow_mo_ms': 'Slow Motion (ms)',
            'poll_interval': 'Poll Interval (s)',
            'min_sleep_seconds': 'Min Sleep Seconds',
            'max_sleep_seconds': 'Max Sleep Seconds',
            'pause_duration_minutes': 'Pause Duration Minutes',
            'topic_generator': 'Topic Generator',
        }
        if key in custom:
            return custom[key]
        return str(key).replace('_', ' ').title()

    def _create_search_settings_tab(self, notebook, config_data):
        frame = self._create_section_frame(notebook, "Search")
        section = config_data.get('search_settings', {})

        fields = [
            ('target_points', int, section.get('target_points', 90)),
            ('searches_before_pause', int, section.get('searches_before_pause', 10)),
            ('pause_duration_minutes', float, section.get('pause_duration_minutes', 1)),
            ('min_sleep_seconds', int, section.get('min_sleep_seconds', 15)),
            ('max_sleep_seconds', int, section.get('max_sleep_seconds', 20)),
            ('poll_interval', int, section.get('poll_interval', 5)),
        ]

        for idx, (key, value_type, value) in enumerate(fields):
            var = tk.StringVar(value=str(value))
            self._config_vars[('search_settings', key)] = (var, value_type)
            entry = ttk.Entry(frame, textvariable=var)
            self._add_row(frame, idx, key, entry, section='search_settings', key_param=key)
            self._register_widget('search_settings', key, entry)

        topic_var = tk.StringVar(value=str(section.get('topic_generator', 'runtime')))
        self._config_vars[('search_settings', 'topic_generator')] = (topic_var, str)
        topic_combo = ttk.Combobox(frame, textvariable=topic_var, values=['runtime', 'daily'], state='readonly')
        self._add_row(frame, len(fields), 'topic_generator', topic_combo, section='search_settings', key_param='topic_generator')
        self._register_widget('search_settings', 'topic_generator', topic_combo)

    def _create_browser_tab(self, notebook, config_data):
        frame = self._create_section_frame(notebook, "Browser")
        section = config_data.get('browser', {})

        headless_var = tk.BooleanVar(value=bool(section.get('headless', True)))
        self._config_vars[('browser', 'headless')] = (headless_var, bool)
        headless_cb = ttk.Checkbutton(frame, variable=headless_var)
        self._add_row(frame, 0, 'headless', headless_cb, section='browser', key_param='headless')
        self._register_widget('browser', 'headless', headless_cb)

        slow_mo_var = tk.StringVar(value=str(section.get('slow_mo_ms', 0)))
        self._config_vars[('browser', 'slow_mo_ms')] = (slow_mo_var, int)
        slowmo_entry = ttk.Entry(frame, textvariable=slow_mo_var)
        self._add_row(frame, 1, 'slow_mo_ms', slowmo_entry, section='browser', key_param='slow_mo_ms')
        self._register_widget('browser', 'slow_mo_ms', slowmo_entry)

    def _create_proxy_tab(self, notebook, config_data):
        frame = self._create_section_frame(notebook, "Proxy")
        section = config_data.get('proxy', {})

        enabled_var = tk.BooleanVar(value=bool(section.get('enabled', False)))
        self._config_vars[('proxy', 'enabled')] = (enabled_var, bool)
        enabled_cb = ttk.Checkbutton(frame, variable=enabled_var)
        self._add_row(frame, 0, 'enabled', enabled_cb, section='proxy', key_param='enabled')
        self._register_widget('proxy', 'enabled', enabled_cb)

        strategy_var = tk.StringVar(value=str(section.get('rotation_strategy', 'random')))
        self._config_vars[('proxy', 'rotation_strategy')] = (strategy_var, str)
        strategy_combo = ttk.Combobox(frame, textvariable=strategy_var, values=['random', 'round_robin', 'sequential'], state='readonly')
        self._add_row(frame, 1, 'rotation_strategy', strategy_combo, section='proxy', key_param='rotation_strategy')
        self._register_widget('proxy', 'rotation_strategy', strategy_combo)

        proxies = section.get('proxies') or []
        proxies_text = tk.Text(frame, height=8, width=60)
        proxies_text.insert('1.0', '\n'.join(proxies))
        ttk.Label(frame, text='proxies (one per line)', width=28).grid(row=2, column=0, sticky='nw', padx=(0, 10), pady=6)
        proxies_text.grid(row=2, column=1, sticky='ew', pady=6)
        self._config_vars[('proxy', 'proxies')] = (proxies_text, list)
        self._register_widget('proxy', 'proxies', proxies_text)

    def _create_stealth_tab(self, notebook, config_data):
        frame = self._create_section_frame(notebook, "Stealth")
        section = config_data.get('stealth', {})

        bool_fields = [
            ('simulate_mistakes', section.get('simulate_mistakes', True)),
            ('typing_speed_variance', section.get('typing_speed_variance', True)),
            ('random_mouse_movements', section.get('random_mouse_movements', True)),
            ('random_scrolling', section.get('random_scrolling', False)),
        ]

        row = 0
        for key, value in bool_fields:
            var = tk.BooleanVar(value=bool(value))
            self._config_vars[('stealth', key)] = (var, bool)
            cb = ttk.Checkbutton(frame, variable=var)
            self._add_row(frame, row, key, cb, section='stealth', key_param=key)
            self._register_widget('stealth', key, cb)
            row += 1

        mistake_var = tk.StringVar(value=str(section.get('mistake_probability', 0.05)))
        self._config_vars[('stealth', 'mistake_probability')] = (mistake_var, float)
        mistake_entry = ttk.Entry(frame, textvariable=mistake_var)
        self._add_row(frame, row, 'mistake_probability', mistake_entry, section='stealth', key_param='mistake_probability')
        self._register_widget('stealth', 'mistake_probability', mistake_entry)

    def _create_logging_tab(self, notebook, config_data):
        frame = self._create_section_frame(notebook, "Logging")
        section = config_data.get('logging', {})

        level_var = tk.StringVar(value=str(section.get('level', 'INFO')))
        self._config_vars[('logging', 'level')] = (level_var, str)
        level_combo = ttk.Combobox(
            frame,
            textvariable=level_var,
            values=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
            state='readonly'
        )
        self._add_row(frame, 0, 'level', level_combo, section='logging', key_param='level')
        self._register_widget('logging', 'level', level_combo)

        format_var = tk.StringVar(value=str(section.get('format', '%(asctime)s - %(name)s - %(levelname)s - %(message)s')))
        self._config_vars[('logging', 'format')] = (format_var, str)
        format_entry = ttk.Entry(frame, textvariable=format_var)
        self._add_row(frame, 1, 'format', format_entry, section='logging', key_param='format')
        self._register_widget('logging', 'format', format_entry)

    def _cast_value(self, raw_value, expected_type):
        if expected_type is bool:
            return bool(raw_value)
        if expected_type is int:
            return int(raw_value)
        if expected_type is float:
            return float(raw_value)
        if expected_type is list:
            lines = raw_value.splitlines()
            return [line.strip() for line in lines if line.strip()]
        return str(raw_value).strip()

    def _default_editable_config(self):
        """Default values for sections editable through UI."""
        return {
            'search_settings': {
                'target_points': 90,
                'searches_before_pause': 10,
                'pause_duration_minutes': 1.0,
                'min_sleep_seconds': 15,
                'max_sleep_seconds': 20,
                'poll_interval': 5,
                'topic_generator': 'runtime',
            },
            'browser': {
                'headless': True,
                'slow_mo_ms': 0,
            },
            'proxy': {
                'enabled': False,
                'rotation_strategy': 'random',
                'proxies': [],
            },
            'stealth': {
                'simulate_mistakes': True,
                'mistake_probability': 0.05,
                'typing_speed_variance': True,
                'random_mouse_movements': True,
                'random_scrolling': False,
            },
            'logging': {
                'level': 'DEBUG',
                'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            },
        }

    def _set_defaults_in_form(self):
        """Reset form fields to default editable values (not saved until Save)."""
        defaults = self._default_editable_config()
        for (section, key), (widget_var, value_type) in self._config_vars.items():
            if section not in defaults or key not in defaults[section]:
                continue

            default_value = defaults[section][key]
            if value_type is list:
                widget_var.delete('1.0', 'end')
                widget_var.insert('1.0', '\n'.join(default_value))
            else:
                widget_var.set(default_value)

    def _save_config_from_ui(self, config_path):
        """Validate form values, save editable sections, and sync runtime config."""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                if self._yaml_rt:
                    data = self._yaml_rt.load(f) or CommentedMap()
                else:
                    data = pyyaml.safe_load(f) or {}

            selected_profile = self._config_profile_var.get() if self._config_profile_var else 'Custom'
            data['active_profile'] = None if selected_profile == 'Custom' else selected_profile

            for (section, key), (widget_var, value_type) in self._config_vars.items():
                if section not in data or not isinstance(data.get(section), dict):
                    data[section] = CommentedMap() if self._yaml_rt else {}

                if value_type is list:
                    raw = widget_var.get('1.0', 'end')
                else:
                    raw = widget_var.get()

                data[section][key] = self._cast_value(raw, value_type)

            with open(config_path, 'w', encoding='utf-8') as f:
                if self._yaml_rt:
                    self._yaml_rt.dump(data, f)
                else:
                    f.write(self._render_config_yaml(data))

            effective_data = data
            if selected_profile != 'Custom':
                profiles = data.get('profiles', {})
                if selected_profile in profiles:
                    effective_data = deep_merge(data, profiles[selected_profile])

            self._sync_runtime_config(effective_data)

            self.config.active_profile = None if selected_profile == 'Custom' else selected_profile
            if hasattr(self, 'mode_label'):
                self.mode_label.config(text=f"Selected Mode: {self._get_selected_mode_name()}")

            messagebox.showinfo(
                "Config Saved",
                "Configuration updated successfully and applied immediately."
            )
            if self._config_window and self._config_window.winfo_exists():
                self._config_window.destroy()
        except ValueError as e:
            messagebox.showerror("Validation Error", f"Invalid value: {e}")
        except Exception as e:
            self.logger.error(f"Failed to save config: {e}", exc_info=True)
            messagebox.showerror("Save Error", f"Failed to save config:\n{e}")

    def _render_config_yaml(self, data):
        """Render config YAML with stable indentation and readable section spacing."""
        yaml_text = pyyaml.safe_dump(
            data,
            sort_keys=False,
            default_flow_style=False,
            indent=2,
            width=120,
            allow_unicode=False,
        )

        lines = yaml_text.splitlines()
        formatted_lines = []
        saw_first_top_level = False

        for line in lines:
            stripped = line.strip()
            is_top_level_section = bool(stripped) and not line.startswith(' ') and stripped.endswith(':')

            if is_top_level_section and saw_first_top_level and (formatted_lines and formatted_lines[-1] != ''):
                formatted_lines.append('')

            formatted_lines.append(line.rstrip())

            if is_top_level_section:
                saw_first_top_level = True

        return '\n'.join(formatted_lines) + '\n'

    def _sync_runtime_config(self, data):
        """Update in-memory config object so UI and runtime remain consistent."""
        search_settings = data.get('search_settings', {})
        browser = data.get('browser', {})
        proxy = data.get('proxy', {})
        stealth = data.get('stealth', {})
        logging_cfg = data.get('logging', {})

        self.config.target_points = search_settings.get('target_points', self.config.target_points)
        self.config.searches_before_pause = search_settings.get('searches_before_pause', self.config.searches_before_pause)
        self.config.pause_duration_minutes = search_settings.get('pause_duration_minutes', self.config.pause_duration_minutes)
        self.config.min_sleep_seconds = search_settings.get('min_sleep_seconds', self.config.min_sleep_seconds)
        self.config.max_sleep_seconds = search_settings.get('max_sleep_seconds', self.config.max_sleep_seconds)
        self.config.poll_interval = search_settings.get('poll_interval', self.config.poll_interval)
        self.config.topic_generator_type = search_settings.get('topic_generator', self.config.topic_generator_type)

        self.config.headless = browser.get('headless', self.config.headless)
        self.config.slow_mo_ms = browser.get('slow_mo_ms', self.config.slow_mo_ms)
        self.config.storage_state_path = browser.get('storage_state_path', self.config.storage_state_path)
        self.config.playwright_channel = browser.get('channel', self.config.playwright_channel)

        self.config.proxy_enabled = proxy.get('enabled', self.config.proxy_enabled)
        self.config.proxy_rotation_strategy = proxy.get('rotation_strategy', self.config.proxy_rotation_strategy)
        self.config.proxy_list = proxy.get('proxies', self.config.proxy_list)

        self.config.simulate_mistakes = stealth.get('simulate_mistakes', self.config.simulate_mistakes)
        self.config.mistake_probability = stealth.get('mistake_probability', self.config.mistake_probability)
        self.config.typing_speed_variance = stealth.get('typing_speed_variance', self.config.typing_speed_variance)
        self.config.random_mouse_movements = stealth.get('random_mouse_movements', self.config.random_mouse_movements)
        self.config.random_scrolling = stealth.get('random_scrolling', self.config.random_scrolling)

        self.config.log_level = logging_cfg.get('level', self.config.log_level)
        self.config.log_format = logging_cfg.get('format', self.config.log_format)

        # Apply derived runtime settings immediately (typing/proxy/topic provider).
        if hasattr(self.browser_controller, 'apply_runtime_config'):
            self.browser_controller.apply_runtime_config()

    def _init_graph(self):
        """Initialize the graph with empty data."""
        self.ax.clear()
        self.ax.set_xlabel('Search Number')
        self.ax.set_ylabel('Rewards Points')
        self.ax.set_title('Rewards Points Progress')
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
            self._completion_dialog_shown = False
            self._session_start_time = datetime.now()
            self._session_completion_time = None
            self.start_time_label.config(text=f"Start: {self._session_start_time.strftime('%Y-%m-%d %H:%M:%S')}")
            self.completion_time_label.config(text="Completed At: --")
            # Reset metrics for new session
            self.metrics_collector.reset()
            # Reset watcher state to allow shutdown dialog to show again
            if hasattr(self, 'rewards_watcher') and self.rewards_watcher:
                self.rewards_watcher.reset()
            self.browser_controller.start_searching()
            self.search_started = True
            self.start_btn.config(state=tk.DISABLED)
            self.stop_btn.config(state=tk.NORMAL)
            self.status_label.config(text="Status: Running", foreground="#1f6feb")

    def stop_searching(self):
        """Stop the search process."""
        if self.search_started:
            self.logger.info("Stop button clicked.")
            stop_timer()
            self.browser_controller.stop_searching()
            self.clear_pause_timer()
            self.search_started = False
            self.start_btn.config(state=tk.NORMAL)
            self.stop_btn.config(state=tk.DISABLED)
            if not self.data_manager.rewards_completed:
                self.status_label.config(text="Status: Stopped", foreground="#a04d00")

    def _play_completion_sound(self):
        """Play an audible cue when session completes."""
        try:
            if winsound:
                # Distinct but short completion chime.
                winsound.MessageBeep(winsound.MB_ICONASTERISK)
                winsound.Beep(1200, 180)
                winsound.Beep(1500, 220)
            else:
                self.root.bell()
        except Exception:
            try:
                self.root.bell()
            except Exception:
                pass

    def _show_completion_dialog(self):
        """Show a styled completion dialog when target points are achieved."""
        dialog = tk.Toplevel(self.root)
        dialog.title("Session Complete")
        dialog.geometry("520x300")
        dialog.configure(bg="#f7f9fc")
        dialog.resizable(False, False)
        dialog.transient(self.root)
        dialog.grab_set()

        # Center dialog over the main dashboard area.
        self.root.update_idletasks()
        width, height = 520, 300
        root_x = self.root.winfo_rootx()
        root_y = self.root.winfo_rooty()
        root_w = self.root.winfo_width()
        root_h = self.root.winfo_height()
        pos_x = root_x + max(0, (root_w - width) // 2)
        pos_y = root_y + max(0, (root_h - height) // 2)
        dialog.geometry(f"{width}x{height}+{pos_x}+{pos_y}")

        header = tk.Label(
            dialog,
            text="Session Completed",
            font=("Segoe UI", 20, "bold"),
            fg="#0b6e4f",
            bg="#f7f9fc"
        )
        header.pack(pady=(24, 8))

        points = self.data_manager.rewards_points
        total = self.data_manager.total_searches_session
        message = (
            f"Target points achieved successfully.\n\n"
            f"Points: {points} / {self.config.target_points}\n"
            f"Searches this session: {total}"
        )
        body = tk.Label(
            dialog,
            text=message,
            font=("Segoe UI", 12),
            fg="#1f2937",
            bg="#f7f9fc",
            justify="center"
        )
        body.pack(pady=(0, 20))

        close_in_var = tk.StringVar(value="Auto close in 60s")
        close_label = tk.Label(
            dialog,
            textvariable=close_in_var,
            font=("Segoe UI", 10),
            fg="#4b5563",
            bg="#f7f9fc"
        )
        close_label.pack(pady=(0, 8))

        ttk.Button(dialog, text="Great", command=dialog.destroy).pack(pady=(0, 18))

        def _countdown(secs):
            if not dialog.winfo_exists():
                return
            close_in_var.set(f"Auto close in {secs}s")
            if secs > 0:
                dialog.after(1000, _countdown, secs - 1)
            else:
                try:
                    dialog.destroy()
                except Exception:
                    pass

        _countdown(60)

    def _check_completion_state(self):
        """Update completion status and show completion dialog once."""
        if self.data_manager.rewards_completed:
            self.status_label.config(text="Status: Completed", foreground="#0b6e4f")
            self.search_started = False
            self.start_btn.config(state=tk.NORMAL)
            self.stop_btn.config(state=tk.DISABLED)
            if not self._completion_dialog_shown:
                self._completion_dialog_shown = True
                self._session_completion_time = datetime.now()
                self.completion_time_label.config(
                    text=f"Completed At: {self._session_completion_time.strftime('%Y-%m-%d %H:%M:%S')}"
                )
                self._play_completion_sound()
                self._show_completion_dialog()

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

    def update_statistics(self) -> None:
        """Update the statistics display with current metrics (thread-safe)."""
        try:
            metrics = self.metrics_collector.get_metrics()
            current_points = self.data_manager.rewards_points
            target_points = self.config.target_points
            
            # Calculate statistics
            success_rate = metrics.get_success_rate()
            searches_per_min = metrics.get_searches_per_minute()
            points_per_search = metrics.get_points_per_search()
            eta_seconds = metrics.estimate_time_to_target(current_points, target_points)
            
            # Format ETA
            if eta_seconds is not None and eta_seconds > 0:
                eta_minutes, eta_secs = divmod(int(eta_seconds), 60)
                eta_hours, eta_minutes = divmod(eta_minutes, 60)
                eta_str = f"{eta_hours:02d}:{eta_minutes:02d}:{eta_secs:02d}"
            else:
                eta_str = "--:--:--"
            
            def _update():
                try:
                    self.success_rate_label.config(text=f"Success Rate: {success_rate:.1f}%")
                    self.searches_per_min_label.config(text=f"Searches/min: {searches_per_min:.1f}")
                    self.points_per_search_label.config(text=f"Points/Search: {points_per_search:.1f}")
                    self.eta_label.config(text=f"ETA: {eta_str}")
                except Exception:
                    pass
            
            self.root.after(0, _update)
        except Exception as e:
            self.logger.warning(f"Could not update statistics: {e}")

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
                        
                        # Plot: X axis = search number, Y axis = rewards points
                        self.ax.plot(search_indices, rewards_points, marker='o', linestyle='-', color='b', linewidth=2, markersize=6)
                    
                    self.ax.set_xlabel('Search Number')
                    self.ax.set_ylabel('Rewards Points')
                    self.ax.set_title('Rewards Points Progress')
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
            self.update_statistics()
            self.update_graph()
            self._check_completion_state()
        except Exception:
            pass
        self.root.after(1000, self.schedule_update)

    def start(self):
        """Start the GUI main loop."""
        self.root.mainloop()

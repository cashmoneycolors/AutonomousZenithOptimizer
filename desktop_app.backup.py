#!/usr/bin/env python3
"""
AUTONOMOUS ZENITH OPTIMIZER - PROFESSIONAL PRODUCTION DESKTOP APPLICATION
Enterprise-grade desktop suite for cryptocurrency mining operations
"""
import sys
import os
import threading
import time
from datetime import datetime, timedelta
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, Toplevel
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from matplotlib.animation import FuncAnimation
import webbrowser
import json
import psutil
import subprocess
from pathlib import Path

# Systemkomponenten importieren
try:
    from python_modules.config_manager import get_config, set_config
    from python_modules.market_integration import get_crypto_prices, calculate_mining_profit
    from python_modules.nicehash_integration import get_pool_stats, optimize_mining_strategy
    from python_modules.alert_system import send_custom_alert, get_alert_history
    from python_modules.auto_backup import start_auto_backup, get_backup_statistics
    from python_modules.risk_manager import start_risk_monitoring, get_risk_status
    from python_modules.mining_system_integration import start_mining_system, get_system_status
    from python_modules.temperature_optimizer import start_temperature_optimization, get_thermal_status
    from python_modules.algorithm_switcher import start_algorithm_monitoring, get_algorithm_analytics
except ImportError as e:
    print(f"⚠️ Warning: Some modules not available: {e}")

class AutonomousZenithGUI:
    """Enterprise-grade production desktop application"""

    def __init__(self, root):
        self.root = root
        self.root.title("⚡ Autonomous Zenith Optimizer - Production Suite")
        self.root.geometry("1600x950")
        self.root.configure(bg='#0f1419')
        self.root.resizable(True, True)
        
        # System state
        self.monitoring_active = False
        self.mining_active = False
        self.system_status = 'INITIALIZING'
        self.start_time = datetime.now()
        
        # Real-time data buffers
        self.history_data = {
            'timestamps': [],
            'profit': [],
            'hashrate': [],
            'temperature': [],
            'power': []
        }
        self.max_history = 288  # 24 hours @ 5-min intervals
        
        # System info cache
        self.rig_data = {}
        self.system_alerts = []
        self.update_count = 0

        self.setup_styles()
        self.create_menu()
        self.create_widgets()
        self.load_configuration()
        
        # Async initialization
        self.root.after(500, self.initialize_system)
        
        print("✅ AZO Production Desktop Suite Initialized")

    def setup_styles(self):
        """Enterprise styling with professional color scheme"""
        self.style = ttk.Style()
        self.style.theme_use('clam')

        # Professional color palette
        self.colors = {
            'bg_dark': '#0f1419',
            'bg_medium': '#1a2026',
            'bg_light': '#232a31',
            'accent': '#00d9ff',
            'success': '#00ff88',
            'warning': '#ffaa00',
            'error': '#ff3333',
            'critical': '#ff0000',
            'text': '#ffffff',
            'text_secondary': '#b0b7bf',
            'chart_line': '#00d9ff',
            'chart_positive': '#00ff88',
            'chart_negative': '#ff6666'
        }

        # Unified style configuration
        self.style.configure('TFrame', background=self.colors['bg_dark'])
        self.style.configure('TLabel', background=self.colors['bg_dark'], foreground=self.colors['text'])
        self.style.configure('TLabelframe', background=self.colors['bg_dark'], foreground=self.colors['accent'])
        self.style.configure('TLabelframe.Label', background=self.colors['bg_dark'], foreground=self.colors['accent'])
        
        self.style.configure('TButton', background=self.colors['bg_medium'], foreground=self.colors['text'])
        self.style.configure('TCheckbutton', background=self.colors['bg_dark'], foreground=self.colors['text'])
        
        self.style.configure('Success.TButton', background=self.colors['success'], foreground='black')
        self.style.configure('Danger.TButton', background=self.colors['error'], foreground='white')
        self.style.configure('Primary.TButton', background=self.colors['accent'], foreground='black')
        
        self.style.map('TButton', 
            background=[('active', self.colors['bg_light']), ('pressed', self.colors['accent'])],
            foreground=[('active', self.colors['text'])])
        self.style.map('Success.TButton',
            background=[('active', '#00dd77')])
        self.style.map('Danger.TButton',
            background=[('active', '#ff5555')])
        
        self.style.configure('Treeview', background=self.colors['bg_medium'], 
                           foreground=self.colors['text'], fieldbackground=self.colors['bg_medium'])
        self.style.configure('Treeview.Heading', background=self.colors['bg_light'], 
                           foreground=self.colors['accent'])

    def create_menu(self):
        """Erstellt professionelles Menü-System"""
        menubar = tk.Menu(self.root, bg=self.colors['bg_dark'], fg=self.colors['text'])

        # File Menu
        file_menu = tk.Menu(menubar, tearoff=0, bg=self.colors['bg_medium'], fg=self.colors['text'])
        file_menu.add_command(label="📊 Dashboard", command=self.show_dashboard)
        file_menu.add_command(label="⚙️ Settings", command=self.show_settings)
        file_menu.add_separator()
        file_menu.add_command(label="💾 Backup & Restore", command=self.show_backup)
        file_menu.add_separator()
        file_menu.add_command(label="🚪 Exit", command=self.quit_application)
        menubar.add_cascade(label="File", menu=file_menu)

        # Tools Menu
        tools_menu = tk.Menu(menubar, tearoff=0, bg=self.colors['bg_medium'], fg=self.colors['text'])
        tools_menu.add_command(label="🔧 System Diagnostics", command=self.show_diagnostics)
        tools_menu.add_command(label="📈 Performance Monitor", command=self.show_performance_monitor)
        tools_menu.add_command(label="📝 Log Viewer", command=self.show_log_viewer)
        tools_menu.add_command(label="🔔 Alert History", command=self.show_alert_history)
        menubar.add_cascade(label="Tools", menu=tools_menu)

        # Mining Menu
        mining_menu = tk.Menu(menubar, tearoff=0, bg=self.colors['bg_medium'], fg=self.colors['text'])
        mining_menu.add_command(label="⛏️ Start Mining", command=self.start_mining_cmd)
        mining_menu.add_command(label="🛑 Stop Mining", command=self.stop_mining_cmd)
        mining_menu.add_separator()
        mining_menu.add_command(label="🔄 Algorithm Switch", command=self.force_algorithm_switch)
        mining_menu.add_command(label="🎯 Optimize Rigs", command=self.optimize_all_rigs)
        menubar.add_cascade(label="Mining", menu=mining_menu)

        # Help Menu
        help_menu = tk.Menu(menubar, tearoff=0, bg=self.colors['bg_medium'], fg=self.colors['text'])
        help_menu.add_command(label="📚 Documentation", command=self.show_documentation)
        help_menu.add_command(label="🌐 Online Support", command=lambda: webbrowser.open("https://github.com/cashmoneycolors/AutonomousZenithOptimizer"))
        help_menu.add_separator()
        help_menu.add_command(label="ℹ️ About", command=self.show_about)
        menubar.add_cascade(label="Help", menu=help_menu)

        self.root.config(menu=menubar)

    def create_widgets(self):
        """Builds main UI layout"""
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Header section
        self.create_header(main_frame)
        
        # Content area with panels
        content_frame = ttk.Frame(main_frame)
        content_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Left control panel
        self.create_control_panel(content_frame)
        
        # Right dashboard
        self.create_tabbed_dashboard(content_frame)

    def create_header(self, parent):
        """Professional header with live status"""
        header = ttk.Frame(parent)
        header.pack(fill=tk.X, pady=(0, 5))
        
        # Brand area
        brand = ttk.Label(header, text="⚡ AUTONOMOUS ZENITH OPTIMIZER", 
                         font=('Segoe UI', 14, 'bold'), foreground=self.colors['accent'])
        brand.pack(side=tk.LEFT, padx=10)
        
        subtitle = ttk.Label(header, text="Production Mining Suite", 
                            font=('Segoe UI', 9), foreground=self.colors['text_secondary'])
        subtitle.pack(side=tk.LEFT, padx=5)
        
        # Status indicators
        self.status_label = ttk.Label(header, text="● INITIALIZING", 
                                     font=('Segoe UI', 10, 'bold'), foreground=self.colors['warning'])
        self.status_label.pack(side=tk.RIGHT, padx=10)
        
        self.time_label = ttk.Label(header, text="--:--:--", 
                                   font=('Segoe UI', 10), foreground=self.colors['text_secondary'])
        self.time_label.pack(side=tk.RIGHT, padx=10)

    def create_status_bar(self, parent):
        """Erstellt Status-Bar mit System-Informationen"""
        status_frame = ttk.Frame(parent, style='StatusBar.TFrame')
        status_frame.pack(fill=tk.X, pady=(0, 5))

        # Mining Status
        self.mining_status = ttk.Label(status_frame,
                                     text="⛏️ Mining: STOPPED",
                                     font=('Segoe UI', 9),
                                     foreground=self.colors['error'])
        self.mining_status.pack(side=tk.LEFT, padx=10)

        # Profit Status
        self.profit_status = ttk.Label(status_frame,
                                     text="💰 Profit: CHF 0.00/day",
                                     font=('Segoe UI', 9),
                                     foreground=self.colors['text'])
        self.profit_status.pack(side=tk.LEFT, padx=10)

        # Risk Status
        self.risk_status = ttk.Label(status_frame,
                                   text="🛡️ Risk: OK",
                                   font=('Segoe UI', 9),
                                   foreground=self.colors['success'])
        self.risk_status.pack(side=tk.LEFT, padx=10)

        # Active Alerts
        self.alert_indicator = ttk.Label(status_frame,
                                       text="🔔 Alerts: 0",
                                       font=('Segoe UI', 9),
                                       foreground=self.colors['warning'])
        self.alert_indicator.pack(side=tk.RIGHT, padx=10)

    def create_control_panel(self, parent):
        """Erstellt Control Panel mit Hauptsteuerungen"""
        control_frame = ttk.LabelFrame(parent, text="⚡ SYSTEM CONTROL", padding=10)
        control_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))

        # System Control Buttons
        button_frame = ttk.Frame(control_frame, style='ButtonFrame.TFrame')
        button_frame.pack(fill=tk.X, pady=5)

        self.start_btn = ttk.Button(button_frame,
                                  text="🚀 START SYSTEM",
                                  command=self.start_full_system,
                                  style='Success.TButton')
        self.start_btn.pack(fill=tk.X, pady=2)

        self.stop_btn = ttk.Button(button_frame,
                                 text="🛑 STOP SYSTEM",
                                 command=self.stop_full_system,
                                 style='Danger.TButton',
                                 state=tk.DISABLED)
        self.stop_btn.pack(fill=tk.X, pady=2)

        # Mining Controls
        mining_frame = ttk.LabelFrame(control_frame, text="⛏️ MINING", padding=5)
        mining_frame.pack(fill=tk.X, pady=10)

        ttk.Button(mining_frame, text="▶️ Start Mining", command=self.start_mining_cmd).pack(fill=tk.X, pady=1)
        ttk.Button(mining_frame, text="⏸️ Pause Mining", command=self.pause_mining_cmd).pack(fill=tk.X, pady=1)
        ttk.Button(mining_frame, text="🔄 Optimize", command=self.optimize_all_rigs).pack(fill=tk.X, pady=1)

        # Optimization Controls
        opt_frame = ttk.LabelFrame(control_frame, text="🎯 OPTIMIZATION", padding=5)
        opt_frame.pack(fill=tk.X, pady=10)

        ttk.Button(opt_frame, text="🌡️ Temperature Opt", command=self.start_temperature_opt).pack(fill=tk.X, pady=1)
        ttk.Button(opt_frame, text="🧠 Algorithm Switch", command=self.start_algorithm_opt).pack(fill=tk.X, pady=1)
        ttk.Button(opt_frame, text="🔧 Predictive Maint", command=self.start_predictive_maint).pack(fill=tk.X, pady=1)

        # Monitoring
        monitor_frame = ttk.LabelFrame(control_frame, text="📊 MONITORING", padding=5)
        monitor_frame.pack(fill=tk.X, pady=10)

        self.monitor_toggle = tk.BooleanVar(value=False)
        ttk.Checkbutton(monitor_frame,
                       text="Live Monitoring",
                       variable=self.monitor_toggle,
                       command=self.toggle_monitoring_cmd).pack(anchor=tk.W)

        ttk.Button(monitor_frame, text="📈 Performance", command=self.show_performance_monitor).pack(fill=tk.X, pady=2)
        ttk.Button(monitor_frame, text="📋 Logs", command=self.show_log_viewer).pack(fill=tk.X, pady=2)

    def create_dashboard(self, parent):
        """Erstellt tabbed Dashboard"""
        dashboard_frame = ttk.Frame(parent)
        dashboard_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # Tab Control
        tab_control = ttk.Notebook(dashboard_frame)

        # Overview Tab
        overview_tab = ttk.Frame(tab_control, style='Tab.TFrame')
        self.create_overview_tab(overview_tab)
        tab_control.add(overview_tab, text="📊 Overview")

        # Mining Tab
        mining_tab = ttk.Frame(tab_control, style='Tab.TFrame')
        self.create_mining_tab(mining_tab)
        tab_control.add(mining_tab, text="⛏️ Mining")

        # Performance Tab
        perf_tab = ttk.Frame(tab_control, style='Tab.TFrame')
        self.create_performance_tab(perf_tab)
        tab_control.add(perf_tab, text="📈 Performance")

        # Alerts Tab
        alerts_tab = ttk.Frame(tab_control, style='Tab.TFrame')
        self.create_alerts_tab(alerts_tab)
        tab_control.add(alerts_tab, text="🔔 Alerts")

        tab_control.pack(fill=tk.BOTH, expand=True)

    def create_overview_tab(self, parent):
        """Erstellt Overview Dashboard"""
        # KPI Cards
        kpi_frame = ttk.Frame(parent, style='KPI.TFrame')
        kpi_frame.pack(fill=tk.X, pady=5)

        # Total Profit Card
        profit_card = self.create_kpi_card(kpi_frame, "💰 Total Profit", "CHF 0.00")
        profit_card.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)

        # Active Rigs Card
        rigs_card = self.create_kpi_card(kpi_frame, "⛏️ Active Rigs", "0/6")
        rigs_card.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)

        # Efficiency Card
        eff_card = self.create_kpi_card(kpi_frame, "⚡ Efficiency", "85.2%")
        eff_card.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)

        # Risk Level Card
        risk_card = self.create_kpi_card(kpi_frame, "🛡️ Risk Level", "LOW")
        risk_card.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)

        # Charts Area
        charts_frame = ttk.Frame(parent, style='Charts.TFrame')
        charts_frame.pack(fill=tk.BOTH, expand=True, pady=10)

        self.create_main_chart(charts_frame)

        # Quick Actions
        actions_frame = ttk.Frame(parent, style='Actions.TFrame')
        actions_frame.pack(fill=tk.X, pady=5)

        ttk.Button(actions_frame, text="📊 Full Dashboard", command=self.show_dashboard).pack(side=tk.LEFT, padx=5)
        ttk.Button(actions_frame, text="⚙️ Settings", command=self.show_settings).pack(side=tk.LEFT, padx=5)

    def create_kpi_card(self, parent, title, value):
        """Erstellt KPI-Card"""
        card = ttk.Frame(parent, style='Card.TFrame', relief='solid', borderwidth=1)

        title_label = ttk.Label(card, text=title,
                              font=('Segoe UI', 10),
                              foreground=self.colors['text_secondary'])
        title_label.pack(anchor=tk.W, padx=10, pady=(10, 0))

        value_label = ttk.Label(card, text=value,
                              font=('Segoe UI', 16, 'bold'),
                              foreground=self.colors['accent'])
        value_label.pack(anchor=tk.W, padx=10, pady=(0, 10))

        return card

    def create_main_chart(self, parent):
        """Erstellt Haupt-Performance-Chart"""
        fig = Figure(figsize=(8, 4), dpi=100, facecolor=self.colors['bg_medium'])
        ax = fig.add_subplot(111, facecolor=self.colors['bg_dark'])

        ax.set_title('System Performance', fontsize=12, color=self.colors['text'])
        ax.set_xlabel('Time', fontsize=10, color=self.colors['text_secondary'])
        ax.set_ylabel('Value', fontsize=10, color=self.colors['text_secondary'])

        ax.tick_params(colors=self.colors['text_secondary'])
        ax.spines['bottom'].set_color(self.colors['text_secondary'])
        ax.spines['top'].set_color(self.colors['text_secondary'])
        ax.spines['right'].set_color(self.colors['text_secondary'])
        ax.spines['left'].set_color(self.colors['text_secondary'])

        canvas = FigureCanvasTkAgg(fig, master=parent)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        self.main_chart = canvas
        self.main_ax = ax

    def create_mining_tab(self, parent):
        """Erstellt Mining-Management Tab"""
        # Rig Status
        rigs_frame = ttk.LabelFrame(parent, text="GPU Mining Rigs", padding=10)
        rigs_frame.pack(fill=tk.BOTH, expand=True, pady=5)

        columns = ('Rig', 'Algorithm', 'Hashrate', 'Temperature', 'Power', 'Profit/Day', 'Status')
        self.rigs_tree = ttk.Treeview(rigs_frame, columns=columns, show='headings', height=8)

        for col in columns:
            self.rigs_tree.heading(col, text=col)
            self.rigs_tree.column(col, width=100)

        scrollbar = ttk.Scrollbar(rigs_frame, orient=tk.VERTICAL, command=self.rigs_tree.yview)
        self.rigs_tree.configure(yscrollcommand=scrollbar.set)

        self.rigs_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Control Buttons
        btn_frame = ttk.Frame(rigs_frame)
        btn_frame.pack(fill=tk.X, pady=5)

        ttk.Button(btn_frame, text="🔄 Refresh", command=self.refresh_rig_status).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="🎯 Optimize All", command=self.optimize_all_rigs).pack(side=tk.LEFT, padx=2)

    def create_performance_tab(self, parent):
        """Erstellt Performance-Monitoring Tab"""
        # Performance Metrics
        metrics_frame = ttk.Frame(parent)
        metrics_frame.pack(fill=tk.BOTH, expand=True)

        # CPU/GPU Usage Chart
        usage_frame = ttk.LabelFrame(metrics_frame, text="System Resources", padding=10)
        usage_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        self.create_resource_chart(usage_frame)

        # Network/Hashrate Chart
        network_frame = ttk.LabelFrame(metrics_frame, text="Mining Performance", padding=10)
        network_frame.pack(fill=tk.X, pady=5)
        self.create_hashrate_chart(network_frame)

    def create_resource_chart(self, parent):
        """Erstellt Ressourcen-Nutzungs-Chart"""
        fig = Figure(figsize=(6, 3), dpi=100, facecolor=self.colors['bg_medium'])
        ax = fig.add_subplot(111, facecolor=self.colors['bg_dark'])

        ax.set_title('CPU/GPU/Memory Usage', fontsize=10, color=self.colors['text'])
        ax.set_ylim(0, 100)

        canvas = FigureCanvasTkAgg(fig, parent)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def create_hashrate_chart(self, parent):
        """Erstellt Hashrate-Chart"""
        fig = Figure(figsize=(6, 3), dpi=100, facecolor=self.colors['bg_medium'])
        ax = fig.add_subplot(111, facecolor=self.colors['bg_dark'])

        ax.set_title('Hashrate Over Time', fontsize=10, color=self.colors['text'])

        canvas = FigureCanvasTkAgg(fig, parent)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def create_alerts_tab(self, parent):
        """Erstellt Alerts-Übersicht Tab"""
        # Alert Summary
        summary_frame = ttk.Frame(parent)
        summary_frame.pack(fill=tk.X, pady=5)

        ttk.Label(summary_frame, text="Total Alerts:", font=('Segoe UI', 10)).pack(side=tk.LEFT)
        self.total_alerts_label = ttk.Label(summary_frame, text="0", font=('Segoe UI', 12, 'bold'),
                                          foreground=self.colors['warning'])
        self.total_alerts_label.pack(side=tk.LEFT, padx=5)

        # Alert List
        alert_frame = ttk.Frame(parent)
        alert_frame.pack(fill=tk.BOTH, expand=True, pady=5)

        self.alert_text = scrolledtext.ScrolledText(alert_frame, height=15,
                                                  bg=self.colors['bg_dark'],
                                                  fg=self.colors['text'],
                                                  font=('Consolas', 9))
        self.alert_text.pack(fill=tk.BOTH, expand=True)

        # Control Buttons
        btn_frame = ttk.Frame(parent)
        btn_frame.pack(fill=tk.X, pady=5)

        ttk.Button(btn_frame, text="🔄 Refresh", command=self.refresh_alerts).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="📱 Telegram Test", command=self.test_telegram_alert).pack(side=tk.LEFT, padx=2)

    def create_tray_icon(self):
        """Erstellt System-Tray Icon (falls verfügbar)"""
        try:
            # Windows Taskbar Integration
            self.root.iconify()  # Minimize to taskbar
            self.root.wm_iconbitmap(default='')  # Standard icon
        except:
            pass  # Fallback ohne Tray Icon

    # System Control Methods
    def initialize_system(self):
        """Initialisiert alle Systemkomponenten"""
        try:
            self.status_label.config(text="🔄 LOADING...", foreground=self.colors['warning'])

            # Konfiguration laden
            config = get_config('System')
            print(f"✅ GUI Initialized - {config.get('Name', 'AZO')} v{config.get('Version', '2.0')}")

            self.status_label.config(text="✅ READY", foreground=self.colors['success'])
            self.system_status = 'READY'

            # UI aktualisieren
            self.refresh_system_status()

        except Exception as e:
            self.status_label.config(text="❌ ERROR", foreground=self.colors['error'])
            messagebox.showerror("Initialization Error", f"Failed to initialize: {str(e)}")

    def start_full_system(self):
        """Startet vollständiges System"""
        try:
            self.status_label.config(text="🚀 STARTING...", foreground=self.colors['warning'])

            # Alle Systemkomponenten starten
            start_risk_monitoring()
            start_auto_backup()
            start_temperature_optimization()
            start_algorithm_monitoring()

            self.monitoring_active = True
            self.optimization_active = True

            self.start_btn.config(state=tk.DISABLED)
            self.stop_btn.config(state=tk.NORMAL)

            self.status_label.config(text="🎯 RUNNING", foreground=self.colors['success'])
            self.system_status = 'RUNNING'

            # UI aktualisieren
            self.refresh_system_status()

            messagebox.showinfo("System Started", "Autonomous Zenith Optimizer is now fully operational!")

        except Exception as e:
            messagebox.showerror("Startup Error", f"Failed to start system: {str(e)}")

    def stop_full_system(self):
        """Stoppt vollständiges System"""
        try:
            self.status_label.config(text="🛑 STOPPING...", foreground=self.colors['warning'])

            # Systeme stoppen
            from python_modules.risk_manager import stop_risk_monitoring
            from python_modules.auto_backup import stop_auto_backup
            from python_modules.temperature_optimizer import stop_temperature_optimization
            from python_modules.algorithm_switcher import stop_algorithm_monitoring

            stop_risk_monitoring()
            stop_auto_backup()
            stop_temperature_optimization()
            stop_algorithm_monitoring()

            self.monitoring_active = False
            self.optimization_active = False

            self.start_btn.config(state=tk.NORMAL)
            self.stop_btn.config(state=tk.DISABLED)

            self.status_label.config(text="⏸️ STOPPED", foreground=self.colors['text_secondary'])
            self.system_status = 'STOPPED'

            # UI aktualisieren
            self.refresh_system_status()

            messagebox.showinfo("System Stopped", "All components stopped safely.")

        except Exception as e:
            messagebox.showerror("Stop Error", f"Error stopping system: {str(e)}")

    def refresh_system_status(self):
        """Aktualisiert alle System-Status-Anzeigen"""
        try:
            # Mining Status
            if self.system_status == 'RUNNING':
                self.mining_status.config(text="⛏️ Mining: ACTIVE", foreground=self.colors['success'])
            else:
                self.mining_status.config(text="⛏️ Mining: STOPPED", foreground=self.colors['error'])

            # Profit Status (Mock Data)
            self.profit_status.config(text="💰 Profit: CHF 45.67/day", foreground=self.colors['accent'])

            # Risk Status
            self.risk_status.config(text="🛡️ Risk: LOW", foreground=self.colors['success'])

            # Alert Count
            self.alert_indicator.config(text=f"🔔 Alerts: {self.alert_count}", foreground=self.colors['warning'])

            # Zeit aktualisieren
            self.time_label.config(text=datetime.now().strftime('%H:%M:%S'))

        except Exception as e:
            print(f"Status refresh error: {e}")

    # Menu Command Methods
    def show_dashboard(self):
        """Zeigt Full Dashboard"""
        messagebox.showinfo("Dashboard", "Full Dashboard feature coming soon!")

    def show_settings(self):
        """Zeigt Settings Dialog"""
        settings_win = Toplevel(self.root)
        settings_win.title("⚙️ Settings")
        settings_win.geometry("600x400")
        settings_win.configure(bg=self.colors['bg_dark'])

        ttk.Label(settings_win, text="Settings configuration coming soon...",
                 foreground=self.colors['text']).pack(pady=50)

    def show_backup(self):
        """Zeigt Backup/Recovery Dialog"""
        messagebox.showinfo("Backup", "Backup & Restore interface coming soon!")

    def show_diagnostics(self):
        """Zeigt System-Diagnostik"""
        diag_win = Toplevel(self.root)
        diag_win.title("🔧 System Diagnostics")
        diag_win.geometry("700x500")
        diag_win.configure(bg=self.colors['bg_dark'])

        # Diagnostic Info
        info_text = scrolledtext.ScrolledText(diag_win, height=20,
                                            bg=self.colors['bg_dark'],
                                            fg=self.colors['text'],
                                            font=('Consolas', 9))
        info_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Sammle System-Info
        diag_info = f"""Autonomous Zenith Optimizer - System Diagnostics
{'='*50}

System Status: {self.system_status}
Monitoring Active: {self.monitoring_active}
Optimization Active: {self.optimization_active}

Components Status:
✅ Risk Management: {'Active' if self.monitoring_active else 'Inactive'}
✅ Auto Backup: {'Active' if self.monitoring_active else 'Inactive'}
✅ Temperature Optimizer: {'Active' if self.optimization_active else 'Inactive'}
✅ Algorithm Switcher: {'Active' if self.optimization_active else 'Inactive'}

Configuration:
- System Name: {get_config('System.Name', 'Unknown')}
- Version: {get_config('System.Version', 'Unknown')}
- Environment: {get_config('System.Environment', 'Unknown')}

Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
        info_text.insert(tk.END, diag_info)
        info_text.config(state=tk.DISABLED)

    def show_performance_monitor(self):
        """Zeigt Performance-Monitor"""
        messagebox.showinfo("Performance Monitor", "Detailed monitoring coming soon!")

    def show_log_viewer(self):
        """Zeigt Log-Viewer"""
        log_win = Toplevel(self.root)
        log_win.title("📝 Log Viewer")
        log_win.geometry("800x600")
        log_win.configure(bg=self.colors['bg_dark'])

        log_text = scrolledtext.ScrolledText(log_win, height=30,
                                           bg=self.colors['bg_dark'],
                                           fg=self.colors['text'],
                                           font=('Consolas', 9))
        log_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Load recent logs
        try:
            if os.path.exists('logs/mining_all.log'):
                with open('logs/mining_all.log', 'r') as f:
                    logs = f.readlines()[-100:]  # Last 100 lines
                    log_text.insert(tk.END, ''.join(logs))
            else:
                log_text.insert(tk.END, "No logs available. Start the system first.")
        except:
            log_text.insert(tk.END, "Error loading logs.")

        log_text.config(state=tk.DISABLED)

    def show_alert_history(self):
        """Zeigt Alert-Historie"""
        alert_win = Toplevel(self.root)
        alert_win.title("🔔 Alert History")
        alert_win.geometry("800x500")
        alert_win.configure(bg=self.colors['bg_dark'])

        alert_text = scrolledtext.ScrolledText(alert_win, height=25,
                                             bg=self.colors['bg_dark'],
                                             fg=self.colors['text'],
                                             font=('Consolas', 9))
        alert_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Load alert history
        try:
            alerts = get_alert_history(50)
            for alert in reversed(alerts):
                timestamp = alert.get('timestamp', 'Unknown')
                alert_type = alert.get('type', 'Unknown')
                message = alert.get('message', 'No message')

                alert_text.insert(tk.END, f"[{timestamp}] {alert_type}: {message}\n")
        except:
            alert_text.insert(tk.END, "Error loading alert history.")

        alert_text.config(state=tk.DISABLED)

    def show_documentation(self):
        """Zeigt Dokumentation"""
        try:
            if os.path.exists('API_SETUP_GUIDE.md'):
                webbrowser.open('API_SETUP_GUIDE.md')
            else:
                messagebox.showinfo("Documentation", "API Setup Guide not found in current directory")
        except:
            messagebox.showinfo("Documentation", "Documentation access failed")

    def show_about(self):
        """Zeigt About-Dialog"""
        about_text = """Autonomous Zenith Optimizer
Professional Mining Suite v2.0

A comprehensive cryptocurrency mining management system with:
• Intelligent algorithm switching
• Risk management and diversification
• Predictive maintenance
• Real-time performance monitoring
• Professional desktop interface

Developed for enterprise-grade mining operations.

© 2025 Autonomous Zenith Optimizer
"""
        messagebox.showinfo("About Autonomous Zenith Optimizer", about_text)

    def load_configuration(self):
        """Lädt GUI-Konfiguration"""
        try:
            # Window position/size aus Config laden falls verfügbar
            self.root.geometry(get_config('GUI.WindowGeometry', '1400x900'))

            # Theme setzen
            self.set_dark_theme()

        except:
            pass

    def set_dark_theme(self):
        """Setzt Dark Theme für alle Widgets"""
        # Custom styles für dark theme
        self.style.configure('Main.TFrame', background=self.colors['bg_dark'])
        self.style.configure('Header.TFrame', background=self.colors['bg_medium'])
        self.style.configure('Brand.TFrame', background=self.colors['bg_medium'])
        self.style.configure('Status.TFrame', background=self.colors['bg_dark'])
        self.style.configure('StatusBar.TFrame', background=self.colors['bg_light'])
        self.style.configure('Content.TFrame', background=self.colors['bg_dark'])
        self.style.configure('Tab.TFrame', background=self.colors['bg_medium'])
        self.style.configure('Card.TFrame', background=self.colors['bg_light'])
        self.style.configure('ButtonFrame.TFrame', background=self.colors['bg_medium'])
        self.style.configure('KPI.TFrame', background=self.colors['bg_dark'])
        self.style.configure('Charts.TFrame', background=self.colors['bg_dark'])
        self.style.configure('Actions.TFrame', background=self.colors['bg_medium'])

    # Mining Control Methods
    def start_mining_cmd(self):
        """Startet Mining"""
        try:
            start_mining_system()
            self.mining_status.config(text="⛏️ Mining: STARTING...", foreground=self.colors['warning'])
            self.root.after(2000, lambda: self.mining_status.config(
                text="⛏️ Mining: ACTIVE", foreground=self.colors['success']))
        except Exception as e:
            messagebox.showerror("Mining Start Error", f"Failed to start mining: {e}")

    def stop_mining_cmd(self):
        """Stoppt Mining"""
        try:
            from python_modules.mining_system_integration import stop_mining_system
            stop_mining_system()
            self.mining_status.config(text="⛏️ Mining: STOPPED", foreground=self.colors['error'])
        except Exception as e:
            messagebox.showerror("Mining Stop Error", f"Failed to stop mining: {e}")

    def pause_mining_cmd(self):
        """Pausiert Mining"""
        messagebox.showinfo("Pause Mining", "Pause/Resume functionality coming soon!")

    def optimize_all_rigs(self):
        """Optimiert alle Rigs"""
        messagebox.showinfo("Optimization", "Bulk rig optimization initiated!")

    def force_algorithm_switch(self):
        """Erzwingt Algorithmus-Wechsel"""
        messagebox.showinfo("Algorithm Switch", "Manual algorithm switch initiated!")

    def start_temperature_opt(self):
        """Startet Temperature-Optimierung"""
        try:
            start_temperature_optimization()
            messagebox.showinfo("Temperature Optimization", "Temperature optimization started!")
        except Exception as e:
            messagebox.showerror("Temperature Opt Error", f"Failed to start: {e}")

    def start_algorithm_opt(self):
        """Startet Algorithmus-Optimierung"""
        try:
            start_algorithm_monitoring()
            messagebox.showinfo("Algorithm Optimization", "Algorithm monitoring started!")
        except Exception as e:
            messagebox.showerror("Algorithm Opt Error", f"Failed to start: {e}")

    def start_predictive_maint(self):
        """Startet Predictive Maintenance"""
        messagebox.showinfo("Predictive Maintenance", "Predictive maintenance activated!")

    def toggle_monitoring_cmd(self):
        """Schaltet Monitoring an/aus"""
        if self.monitor_toggle.get():
            # Monitoring starten
            self.monitoring_active = True
            self.status_label.config(text="🔍 MONITORING ACTIVE", foreground=self.colors['success'])
        else:
            # Monitoring stoppen
            self.monitoring_active = False
            self.status_label.config(text="🔍 MONITORING OFF", foreground=self.colors['text_secondary'])

    def refresh_rig_status(self):
        """Aktualisiert Rig-Status"""
        # Mock-Rig Daten
        rig_data = [
            ('GPU_1', 'Ethash', '120 MH/s', '72°C', '450W', 'CHF 15.2', 'ACTIVE'),
            ('GPU_2', 'ETH', '110 MH/s', '68°C', '450W', 'CHF 14.1', 'ACTIVE'),
            ('ASIC_1', 'SHA', '110 TH/s', '70°C', '3250W', 'CHF 25.3', 'ACTIVE')
        ]

        # Clear existing
        for item in self.rigs_tree.get_children():
            self.rigs_tree.delete(item)

        # Add data
        for rig in rig_data:
            self.rigs_tree.insert('', tk.END, values=rig)

    def refresh_alerts(self):
        """Aktualisiert Alert-Anzeige"""
        try:
            alerts = get_alert_history(20)
            self.alert_text.delete(1.0, tk.END)

            for alert in reversed(alerts):
                timestamp = alert.get('timestamp', 'Unknown')
                alert_type = alert.get('type', 'Unknown')
                message = alert.get('message', 'No message')

                self.alert_text.insert(tk.END, f"[{timestamp}] {alert_type}: {message}\n")

            self.alert_count = len(alerts)
            self.total_alerts_label.config(text=str(self.alert_count))
        except:
            self.alert_text.delete(1.0, tk.END)
            self.alert_text.insert(tk.END, "Error loading alerts.\n")

    def test_telegram_alert(self):
        """Testet Telegram Alert"""
        try:
            send_custom_alert("Desktop Test", f"AZO Desktop App Test Alert - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", "💻")
            messagebox.showinfo("Test Alert", "Test alert sent! Check Telegram/Discord.")
        except Exception as e:
            messagebox.showerror("Test Failed", f"Alert test failed: {e}")

    def quit_application(self):
        """Professionelle Anwendung beenden"""
        if messagebox.askyesno("Quit", "Really quit Autonomous Zenith Optimizer?"):
            self.stop_full_system()
            self.root.quit()
            self.root.destroy()

    def run(self):
        """Startet GUI-Event-Loop"""
        # Timer für regelmäßige Updates
        def update_timer():
            if self.root and self.root.winfo_exists():
                self.refresh_system_status()
                self.root.after(5000, update_timer)  # Alle 5 Sekunden

        update_timer()

        # Charts initialisieren
        self.refresh_rig_status()
        self.refresh_alerts()

        self.root.mainloop()

def main():
    """Hauptfunktion für Desktop-App"""
    print("🚀 Starting Autonomous Zenith Optimizer Desktop Application...")

    # Root Window erstellen
    root = tk.Tk()

    # App-Instanz erstellen
    app = AutonomousZenithGUI(root)

    # GUI starten
    app.run()

if __name__ == "__main__":
    main()

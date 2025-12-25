#!/usr/bin/env python3
"""
AUTONOMOUS ZENITH OPTIMIZER - DESKTOP APP INSTALLER
Professioneller Installer für HP Laptops und Desktop-Systeme
"""
import os
import sys
import subprocess
import platform
import shutil
from pathlib import Path
from tkinter import Tk, messagebox, ttk, filedialog
import tkinter as tk

class AZOInstaller:
    """Professioneller Installer für Autonomous Zenith Optimizer"""

    def __init__(self):
        self.install_dir = None
        self.python_path = None
        self.system = platform.system().lower()

        # GUI setup
        self.root = Tk()
        self.root.title("🦾 AZO Desktop App Installer")
        self.root.geometry("600x500")
        self.root.configure(bg='#0f1419')
        self.root.resizable(False, False)

        # Status variables
        self.install_progress = tk.StringVar(value="Ready to install")
        self.progress_value = tk.IntVar(value=0)

    def check_requirements(self):
        """Überprüft Systemanforderungen"""
        requirements = {}

        # Python Version
        python_version = sys.version_info
        requirements['python_version'] = python_version >= (3, 8)
        requirements['python_path'] = sys.executable

        # Erforderliche Module
        required_modules = [
            'tkinter', 'matplotlib', 'requests', 'json', 'threading',
            'datetime', 'pathlib', 'subprocess', 'platform'
        ]

        missing_modules = []
        installed_modules = []

        for module in required_modules:
            try:
                __import__(module)
                installed_modules.append(module)
            except ImportError:
                missing_modules.append(module)

        requirements['modules_ok'] = len(missing_modules) == 0
        requirements['missing_modules'] = missing_modules
        requirements['installed_modules'] = installed_modules

        # Speicherplatz
        try:
            total, used, free = shutil.disk_usage(".")
            requirements['disk_space_mb'] = free // (1024 * 1024)
            requirements['disk_ok'] = free > (500 * 1024 * 1024)  # 500MB mindestens
        except:
            requirements['disk_space_mb'] = 0
            requirements['disk_ok'] = False

        return requirements

    def create_installer_gui(self):
        """Erstellt die Installer-GUI"""
        # Header
        header = ttk.Frame(self.root, style='Header.TFrame')
        header.pack(fill=tk.X, pady=10)

        ttk.Label(header,
                 text="🦾 Autonomous Zenith Optimizer",
                 font=('Segoe UI', 16, 'bold'),
                 foreground='#00d9ff').pack()

        ttk.Label(header,
                 text="Professional Mining Suite v2.0 Setup",
                 font=('Segoe UI', 10),
                 foreground='#b0b7bf').pack()

        # Content
        content = ttk.Frame(self.root, style='Content.TFrame')
        content.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        # Requirements Check
        req_frame = ttk.LabelFrame(content, text="📋 System Requirements", padding=10)
        req_frame.pack(fill=tk.X, pady=5)

        self.req_text = tk.Text(req_frame, height=8, width=60,
                               bg='#1a2026', fg='#ffffff', font=('Consolas', 9))
        self.req_text.pack(fill=tk.BOTH)

        # Install Directory
        dir_frame = ttk.LabelFrame(content, text="📁 Installation Directory", padding=10)
        dir_frame.pack(fill=tk.X, pady=5)

        self.dir_entry = ttk.Entry(dir_frame, width=50)
        self.dir_entry.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(0, 5))

        # Default install dir
        default_dir = self.get_default_install_dir()
        self.dir_entry.insert(0, default_dir)

        ttk.Button(dir_frame, text="📂 Browse", command=self.browse_install_dir).pack(side=tk.RIGHT)

        # Options
        options_frame = ttk.LabelFrame(content, text="⚙️ Installation Options", padding=10)
        options_frame.pack(fill=tk.X, pady=5)

        self.create_desktop_shortcut = tk.BooleanVar(value=True)
        self.autostart = tk.BooleanVar(value=True)
        self.add_to_path = tk.BooleanVar(value=False)

        ttk.Checkbutton(options_frame,
                       text="Create desktop shortcut",
                       variable=self.create_desktop_shortcut).pack(anchor=tk.W)
        ttk.Checkbutton(options_frame,
                       text="Add to Windows Start menu",
                       variable=self.autostart).pack(anchor=tk.W)
        ttk.Checkbutton(options_frame,
                       text="Add application to PATH",
                       variable=self.add_to_path).pack(anchor=tk.W)

        # Progress
        progress_frame = ttk.Frame(content)
        progress_frame.pack(fill=tk.X, pady=10)

        self.progress = ttk.Progressbar(progress_frame,
                                      variable=self.progress_value,
                                      maximum=100)
        self.progress.pack(fill=tk.X, pady=2)

        self.progress_label = ttk.Label(progress_frame,
                                      textvariable=self.install_progress,
                                      font=('Segoe UI', 9))
        self.progress_label.pack()

        # Buttons
        button_frame = ttk.Frame(content)
        button_frame.pack(fill=tk.X, pady=10)

        ttk.Button(button_frame, text="🔍 Check Requirements",
                  command=self.run_requirements_check).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="🚀 Install",
                  command=self.start_installation).pack(side=tk.RIGHT, padx=5)

        # Footer
        footer = ttk.Frame(self.root, style='Footer.TFrame')
        footer.pack(fill=tk.X, pady=5)

        ttk.Label(footer,
                 text="© 2025 Autonomous Zenith Optimizer - Enterprise Mining Solutions",
                 font=('Segoe UI', 8),
                 foreground='#666666').pack()

        # Styling
        self.setup_styles()

        # Initial check
        self.root.after(1000, self.run_requirements_check)

    def setup_styles(self):
        """Setup dark theme styles"""
        style = ttk.Style()
        style.configure('Header.TFrame', background='#0f1419')
        style.configure('Content.TFrame', background='#0f1419')
        style.configure('Footer.TFrame', background='#0f1419')

    def get_default_install_dir(self):
        """Bestimmt Standard-Installationsverzeichnis"""
        if self.system == 'windows':
            return str(Path.home() / 'AppData' / 'Local' / 'Programs' / 'AutonomousZenithOptimizer')
        elif self.system == 'darwin':  # macOS
            return str(Path.home() / 'Applications' / 'AutonomousZenithOptimizer')
        else:  # Linux
            return str(Path.home() / 'opt' / 'autonomous-zenith-optimizer')

    def browse_install_dir(self):
        """Browse für Installationsverzeichnis"""
        dir_path = filedialog.askdirectory(title="Choose installation directory")
        if dir_path:
            self.dir_entry.delete(0, tk.END)
            self.dir_entry.insert(0, dir_path)

    def run_requirements_check(self):
        """Führt Anforderungsprüfung durch"""
        self.install_progress.set("Checking system requirements...")
        self.root.update()

        requirements = self.check_requirements()

        self.req_text.delete(1.0, tk.END)

        # Python Version
        self.req_text.insert(tk.END, f"🐍 Python Version: {sys.version}")
        if requirements['python_version']:
            self.req_text.insert(tk.END, " ✅\n")
        else:
            self.req_text.insert(tk.END, " ❌ (Require Python 3.8+)\n")

        # Modules
        self.req_text.insert(tk.END, f"📦 Python Modules: {len(requirements['installed_modules'])}/{len(requirements['installed_modules']) + len(requirements['missing_modules'])} installed\n")
        if requirements['modules_ok']:
            self.req_text.insert(tk.END, " ✅ All required modules installed\n")
        else:
            self.req_text.insert(tk.END, f" ❌ Missing: {', '.join(requirements['missing_modules'])}\n")

        # Disk Space
        self.req_text.insert(tk.END, f"💾 Disk Space: {requirements['disk_space_mb']}MB available")
        if requirements['disk_ok']:
            self.req_text.insert(tk.END, " ✅\n")
        else:
            self.req_text.insert(tk.END, " ❌ (Require 500MB)\n")

        # Operating System
        self.req_text.insert(tk.END, f"🖥️ Operating System: {platform.system()} {platform.release()}\n")

        # Overall Status
        all_ok = all([requirements['python_version'],
                     requirements['modules_ok'],
                     requirements['disk_ok']])

        if all_ok:
            self.req_text.insert(tk.END, "\n🎉 System meets all requirements!")
            self.install_progress.set("Ready to install!")
        else:
            self.req_text.insert(tk.END, "\n⚠️ System does not meet requirements!")
            self.install_progress.set("Cannot proceed with installation")

        self.req_text.see(tk.END)

    def start_installation(self):
        """Startet die Installation"""
        # Get install directory
        install_dir = self.dir_entry.get().strip()

        if not install_dir:
            messagebox.showerror("Error", "Please select an installation directory")
            return

        # Confirm installation
        if not messagebox.askyesno("Confirm Installation",
                                  f"Install Autonomous Zenith Optimizer to:\n{install_dir}\n\nContinue?"):
            return

        # Start installation in background thread
        import threading
        install_thread = threading.Thread(target=self.perform_installation, args=(install_dir,))
        install_thread.daemon = True
        install_thread.start()

    def perform_installation(self, install_dir):
        """Führt die eigentliche Installation durch"""
        try:
            self.progress_value.set(0)
            self.install_progress.set("Preparing installation...")

            # Check if directory exists
            if os.path.exists(install_dir):
                if not messagebox.askyesno("Directory exists",
                                          f"Directory {install_dir} already exists.\n\nContinue and overwrite?"):
                    return

            # Create installation directory
            os.makedirs(install_dir, exist_ok=True)
            self.progress_value.set(10)
            self.install_progress.set("Creating installation directory...")

            # Copy application files
            source_dir = os.path.dirname(__file__)
            self.progress_value.set(20)
            self.install_progress.set("Copying application files...")

            files_to_copy = [
                'desktop_app.py',
                'settings.json',
                '.env',
                'API_SETUP_GUIDE.md'
            ]

            # Copy main files
            for file in files_to_copy:
                src = os.path.join(source_dir, file)
                if os.path.exists(src):
                    shutil.copy2(src, install_dir)

            # Copy python_modules directory if it exists
            modules_src = os.path.join(source_dir, 'python_modules')
            if os.path.exists(modules_src):
                modules_dst = os.path.join(install_dir, 'python_modules')
                shutil.copytree(modules_src, modules_dst, dirs_exist_ok=True)

            self.progress_value.set(50)
            self.install_progress.set("Creating shortcuts and configuration...")

            # Create desktop shortcut
            if self.create_desktop_shortcut.get():
                self.create_desktop_shortcut_file(install_dir)

            # Create start menu entry
            if self.autostart.get():
                self.create_start_menu_entry(install_dir)

            # Create uninstaller
            self.create_uninstaller(install_dir)

            self.progress_value.set(80)
            self.install_progress.set("Finalizing installation...")

            # Create configuration file
            config_file = os.path.join(install_dir, 'install_config.json')
            with open(config_file, 'w') as f:
                import json
                json.dump({
                    'install_dir': install_dir,
                    'python_path': sys.executable,
                    'created_shortcuts': self.create_desktop_shortcut.get(),
                    'added_to_start_menu': self.autostart.get(),
                    'added_to_path': self.add_to_path.get()
                }, f, indent=2)

            self.progress_value.set(90)
            self.install_progress.set("Creating launcher...")

            # Create launcher script
            launcher_path = os.path.join(install_dir, 'AZO_Launcher.exe' if self.system == 'windows' else 'AZO_Launcher.sh')

            if self.system == 'windows':
                self.create_windows_launcher(install_dir, launcher_path)
            else:
                self.create_unix_launcher(install_dir, launcher_path)

            self.progress_value.set(100)
            self.install_progress.set("Installation completed successfully!")

            # Success message
            messagebox.showinfo("Installation Complete",
                              f"Autonomous Zenith Optimizer has been installed to:\n{install_dir}\n\n"
                              "You can now run the application using the desktop shortcut or start menu entry.")

            if messagebox.askyesno("Launch Application", "Would you like to launch the application now?"):
                self.launch_application(install_dir)

        except Exception as e:
            messagebox.showerror("Installation Failed", f"An error occurred during installation:\n\n{str(e)}")
            self.install_progress.set("Installation failed")

    def create_desktop_shortcut_file(self, install_dir):
        """Erstellt Desktop-Shortcut"""
        try:
            if self.system == 'windows':
                import winshell

                desktop = winshell.desktop()
                shortcut_path = os.path.join(desktop, 'Autonomous Zenith Optimizer.lnk')

                target = os.path.join(install_dir, 'AZO_Launcher.exe')
                winshell.CreateShortcut(
                    Path=shortcut_path,
                    Target=target,
                    Icon=(target, 0),
                    Description='Autonomous Zenith Optimizer - Professional Mining Suite'
                )
            elif self.system == 'linux':
                desktop_dir = os.path.expanduser('~/Desktop')
                if not os.path.exists(desktop_dir):
                    os.makedirs(desktop_dir)

                desktop_file = os.path.join(desktop_dir, 'AutonomousZenithOptimizer.desktop')
                with open(desktop_file, 'w') as f:
                    f.write(f"""[Desktop Entry]
Version=2.0
Name=Autonomous Zenith Optimizer
Comment=Professional Mining Suite
Exec={os.path.join(install_dir, 'AZO_Launcher.sh')}
Icon={os.path.join(install_dir, 'icon.png')}
Terminal=false
Type=Application
Categories=Utility;
""")
                os.chmod(desktop_file, 0o755)

        except Exception as e:
            print(f"Failed to create desktop shortcut: {e}")

    def create_start_menu_entry(self, install_dir):
        """Erstellt Startmenü-Eintrag"""
        try:
            if self.system == 'windows':
                import winshell
                start_menu = winshell.programs()

                shortcut_path = os.path.join(start_menu, 'Autonomous Zenith Optimizer.lnk')
                target = os.path.join(install_dir, 'AZO_Launcher.exe')

                winshell.CreateShortcut(
                    Path=shortcut_path,
                    Target=target,
                    Icon=(target, 0),
                    Description='Autonomous Zenith Optimizer - Professional Mining Suite'
                )
        except Exception as e:
            print(f"Failed to create start menu entry: {e}")

    def create_uninstaller(self, install_dir):
        """Erstellt Deinstallations-Script"""
        uninstaller_path = os.path.join(install_dir, 'uninstall.py')

        uninstaller_code = f'''#!/usr/bin/env python3
"""
AZO Uninstaller
"""
import os
import shutil
import json

def main():
    install_config = json.load(open('install_config.json'))

    print("🗑️ Uninstalling Autonomous Zenith Optimizer...")

    # Remove files
    install_dir = install_config['install_dir']
    shutil.rmtree(install_dir, ignore_errors=True)

    print(f"✅ Successfully uninstalled from {{install_dir}}")

if __name__ == "__main__":
    main()
'''

        with open(uninstaller_path, 'w') as f:
            f.write(uninstaller_code)

        if self.system != 'windows':
            os.chmod(uninstaller_path, 0o755)

    def create_windows_launcher(self, install_dir, launcher_path):
        """Erstellt Windows-Launcher"""
        launcher_code = f'''@echo off
echo Starting Autonomous Zenith Optimizer...
cd /d "{install_dir}"
"{sys.executable}" desktop_app.py
'''

        with open(launcher_path, 'w') as f:
            f.write(launcher_code)

    def create_unix_launcher(self, install_dir, launcher_path):
        """Erstellt Unix-Launcher (Linux/Mac)"""
        launcher_code = f'''#!/bin/bash
echo "Starting Autonomous Zenith Optimizer..."
cd "{install_dir}"
exec "{sys.executable}" desktop_app.py
'''

        with open(launcher_path, 'w') as f:
            f.write(launcher_code)

        os.chmod(launcher_path, 0o755)

    def launch_application(self, install_dir):
        """Startet die installierte Anwendung"""
        try:
            if self.system == 'windows':
                launcher = os.path.join(install_dir, 'AZO_Launcher.exe')
                subprocess.Popen([launcher])
            else:
                launcher = os.path.join(install_dir, 'AZO_Launcher.sh')
                subprocess.Popen(['bash', launcher])

        except Exception as e:
            messagebox.showerror("Launch Failed", f"Failed to launch application:\n\n{str(e)}")

    def run(self):
        """Startet den Installer"""
        self.create_installer_gui()
        self.root.mainloop()

def main():
    """Hauptfunktion"""
    installer = AZOInstaller()
    installer.run()

if __name__ == "__main__":
    main()

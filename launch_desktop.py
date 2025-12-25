#!/usr/bin/env python3
"""
Launcher for Autonomous Zenith Optimizer Desktop Application
Handles initialization and graceful startup
"""
import sys
import os
from pathlib import Path

# Ensure proper working directory
os.chdir(Path(__file__).parent)
sys.path.insert(0, str(Path(__file__).parent))

print("""
╔══════════════════════════════════════════════════════════════╗
║      ⚡ AUTONOMOUS ZENITH OPTIMIZER v3.0                    ║
║      Production Desktop Suite Launcher                       ║
╚══════════════════════════════════════════════════════════════╝
""")

try:
    print("📋 Initializing system components...")
    
    # Import desktop app
    from desktop_app import ProductionDesktopApp
    import tkinter as tk
    
    print("✅ All components loaded successfully")
    print("\n🚀 Launching Production Desktop Interface...")
    print("   • Press Ctrl+C to gracefully shutdown")
    print("   • Use File → Exit menu for clean termination\n")
    
    # Create and run
    root = tk.Tk()
    app = ProductionDesktopApp(root)
    root.mainloop()
    
    print("\n✅ Application terminated gracefully")
    
except ImportError as e:
    print(f"❌ Import Error: {e}")
    print("   Ensure all dependencies are installed:")
    print("   pip install -r requirements.txt")
    sys.exit(1)
    
except Exception as e:
    print(f"❌ Fatal Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

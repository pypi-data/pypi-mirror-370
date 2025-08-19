#!/usr/bin/env python3
"""
GUI Launcher for Emailer Simple Tool
Simplified launcher that handles dependencies and setup
"""

import sys
import subprocess
import os
from pathlib import Path

def check_pyside6():
    """Check if PySide6 is installed"""
    try:
        import PySide6
        return True
    except ImportError:
        return False

def install_pyside6():
    """Install PySide6 using pip"""
    print("📦 Installing PySide6...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "PySide6"])
        print("✅ PySide6 installed successfully!")
        return True
    except subprocess.CalledProcessError:
        print("❌ Failed to install PySide6")
        return False

def launch_gui():
    """Launch the GUI application"""
    # Import all the GUI components
    import sys
    import os
    import csv
    from pathlib import Path
    from typing import Optional

    from PySide6.QtWidgets import (
        QApplication, QMainWindow, QTabWidget, QWidget, QVBoxLayout, 
        QHBoxLayout, QLabel, QPushButton, QLineEdit, QTextEdit, 
        QTableWidget, QTableWidgetItem, QFileDialog, QMessageBox,
        QProgressBar, QStatusBar, QGroupBox, QFormLayout, QCheckBox,
        QComboBox, QSpinBox, QSplitter, QTreeWidget, QTreeWidgetItem,
        QScrollArea
    )
    from PySide6.QtCore import Qt, QThread, QTimer, Signal
    from PySide6.QtGui import QFont, QIcon, QPixmap

    # Import the GUI classes from our files
    current_dir = Path(__file__).parent
    sys.path.insert(0, str(current_dir))
    
    # Execute the GUI components
    exec(open(current_dir / 'gui_tabs.py').read())
    exec(open(current_dir / 'gui_tabs_part2.py').read())
    
    # Create the main application
    app = QApplication(sys.argv)
    app.setApplicationName("Emailer Simple Tool")
    app.setApplicationVersion("4.1.0")
    app.setApplicationDisplayName("Emailer Simple Tool - GUI Prototype")
    
    # Import and create the main window from gui_complete.py
    exec(open(current_dir / 'gui_complete.py').read())
    
    return 0

def main():
    """Main entry point"""
    print("🚀 Emailer Simple Tool - GUI Launcher")
    print("=" * 50)
    
    # Check if PySide6 is available
    if not check_pyside6():
        print("❌ PySide6 not found")
        response = input("📦 Would you like to install PySide6? (y/n): ").lower().strip()
        
        if response in ['y', 'yes']:
            if not install_pyside6():
                print("❌ Installation failed. Please install manually:")
                print("   pip install PySide6")
                return 1
        else:
            print("❌ PySide6 is required for the GUI")
            print("📦 Install with: pip install PySide6")
            return 1
    
    print("✅ PySide6 is available")
    print("🎨 Launching GUI...")
    
    try:
        # Launch the GUI by running the complete GUI file
        current_dir = Path(__file__).parent
        gui_file = current_dir / 'gui_complete.py'
        
        if gui_file.exists():
            subprocess.run([sys.executable, str(gui_file)])
        else:
            print("❌ GUI files not found")
            return 1
            
    except Exception as e:
        print(f"❌ Error launching GUI: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())

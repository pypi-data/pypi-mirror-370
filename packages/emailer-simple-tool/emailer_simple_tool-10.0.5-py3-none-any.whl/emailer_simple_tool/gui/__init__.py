"""
GUI module for Emailer Simple Tool
Provides graphical user interface using PySide6
"""

__version__ = "1.0.0"

# Check if PySide6 is available
try:
    import PySide6
    GUI_AVAILABLE = True
except ImportError:
    GUI_AVAILABLE = False

def check_gui_dependencies():
    """Check if GUI dependencies are available"""
    if not GUI_AVAILABLE:
        raise ImportError(
            "GUI dependencies not available. Install with: "
            "pip install emailer-simple-tool[gui]"
        )
    return True

def launch_gui():
    """Launch the GUI application"""
    check_gui_dependencies()
    
    from .main_window import main
    return main()

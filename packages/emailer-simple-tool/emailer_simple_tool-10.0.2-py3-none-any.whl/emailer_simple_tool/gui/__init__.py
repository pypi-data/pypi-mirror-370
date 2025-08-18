"""
GUI module for Emailer Simple Tool
Provides graphical user interface using PySide6 or PySide2
"""

__version__ = "1.0.0"

# Try PySide6 first, fallback to PySide2
try:
    import PySide6
    from PySide6.QtWidgets import QSizePolicy
    from PySide6.QtCore import QRegularExpression
    from PySide6.QtGui import QRegularExpressionValidator
    
    GUI_AVAILABLE = True
    PYSIDE_VERSION = 6
    
    # PySide6 compatibility layer
    SizePolicy = QSizePolicy.Policy
    RegExpClass = QRegularExpression
    RegExpValidator = QRegularExpressionValidator
    
except ImportError:
    try:
        import PySide2
        from PySide2.QtWidgets import QSizePolicy
        from PySide2.QtCore import QRegExp
        from PySide2.QtGui import QRegExpValidator
        
        GUI_AVAILABLE = True
        PYSIDE_VERSION = 2
        
        # PySide2 compatibility layer
        SizePolicy = QSizePolicy
        RegExpClass = QRegExp
        RegExpValidator = QRegExpValidator
        
    except ImportError:
        GUI_AVAILABLE = False
        PYSIDE_VERSION = None

def get_pyside_version():
    """Get the PySide version being used"""
    return PYSIDE_VERSION

def check_gui_dependencies():
    """Check if GUI dependencies are available"""
    if not GUI_AVAILABLE:
        raise ImportError(
            "GUI dependencies not available. Install with: "
            "pip install emailer-simple-tool[gui] (PySide6 for Python 3.11+) or "
            "pip install PySide2 (for Python 3.10 and below)"
        )
    return True

def launch_gui():
    """Launch the GUI application"""
    check_gui_dependencies()
    
    print(f"🎨 Using PySide{PYSIDE_VERSION} for GUI")
    
    from .main_window import main
    return main()

# gui package for Baker Management System

# Try to import GUI modules
try:
    from .pos_dashboard import POSApplication, POSMainWindow, LoginWindow
except ImportError:
    POSApplication = None
    POSMainWindow = None
    LoginWindow = None

try:
    from .app import BakerGuiApp
except ImportError:
    BakerGuiApp = None

__all__ = ['POSApplication', 'POSMainWindow', 'LoginWindow', 'BakerGuiApp']

import sys
from PyQt6.QtWidgets import QApplication

# Updated imports to reflect the new structure
from documind.ui.main_window import DocuMindApp
from documind.ui.theme_manager import ThemeManager
# from documind.core.ai_core import AICore # We will use this later

def run():
    """Initializes and runs the DocuMind application."""
    app = QApplication(sys.argv)
    
    # This is the corrected line: pass the 'app' object to the ThemeManager
    theme_manager = ThemeManager(app)
    theme_manager.apply_theme(theme_manager.current_theme)
    
    # ai_core = AICore() # We will pass this to the window later

    window = DocuMindApp(theme_manager) # Pass instances to the window
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    run()
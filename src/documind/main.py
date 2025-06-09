import sys
from PyQt6.QtWidgets import QApplication

from documind.ui.main_window import DocuMindApp
from documind.ui.theme_manager import ThemeManager
from documind.core.ai_core import AICore

def run():
    """Initializes and runs the DocuMind application."""
    app = QApplication(sys.argv)
    
    theme_manager = ThemeManager(app)
    theme_manager.apply_theme(theme_manager.current_theme)
    
    # Instantiate the AI Core
    ai_core = AICore()

    # This is the corrected line: pass BOTH the theme_manager and ai_core
    window = DocuMindApp(theme_manager, ai_core)
    
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    run()
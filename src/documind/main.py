import sys
import pathlib
from PyQt6.QtCore import QThread
from PyQt6.QtWidgets import QApplication

from documind.ui.main_window import DocuMindApp
from documind.ui.theme_manager import ThemeManager
from documind.ui.splash_screen import SplashScreen, AppInitializer

def run():
    """Initializes and runs the DocuMind application with a splash screen."""
    app = QApplication(sys.argv)
    
    # --- Splash Screen Setup ---
    assets_path = pathlib.Path(__file__).parent / "assets"
    splash = SplashScreen(assets_path / "splash.png")
    splash.show()
    
    # --- Background Initialization ---
    thread = QThread()
    initializer = AppInitializer()
    initializer.moveToThread(thread)

    initializer.progress.connect(splash.showMessage)
    thread.started.connect(initializer.run)
    
    # --- Main Application Setup (happens after initialization) ---
    main_window = [None] # Use a list to allow modification inside the lambda
    
    def on_init_finished(ai_core_instance):
        theme_manager = ThemeManager(app)
        theme_manager.apply_theme(theme_manager.current_theme)

        main_window[0] = DocuMindApp(theme_manager, ai_core_instance)
        main_window[0].show()
        
        splash.close()
        thread.quit()
        thread.wait()

    initializer.finished.connect(on_init_finished)
    thread.start()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    run()
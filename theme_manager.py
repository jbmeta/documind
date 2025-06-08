import pathlib
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import QSettings

# Define a robust path to the assets directory
ASSETS_PATH = pathlib.Path(__file__).parent / "assets"

class ThemeManager:
    """Manages the application's visual themes and settings."""

    def __init__(self, app):
        self.app = app
        # QSettings automatically finds the best place to store settings on Win/Mac/Linux
        self.settings = QSettings("DocuMind", "DocuMindApp")
        
        # Define themes
        self.themes = {
            "dark": {
                "stylesheet": ASSETS_PATH / "style.qss",
                "icons": {
                    "add": ASSETS_PATH / "plus-square-light.svg",
                    "send": ASSETS_PATH / "send-light.svg",
                    "toggle": ASSETS_PATH / "sun.svg",
                }
            },
            "light": {
                "stylesheet": ASSETS_PATH / "light_style.qss",
                "icons": {
                    "add": ASSETS_PATH / "plus-square-dark.svg",
                    "send": ASSETS_PATH / "send-dark.svg",
                    "toggle": ASSETS_PATH / "moon.svg",
                }
            }
        }
        
        self.current_theme = self.settings.value("theme", "dark") # Default to dark

    def apply_theme(self, theme_name):
        """Applies a specified theme to the application."""
        if theme_name not in self.themes:
            print(f"Theme '{theme_name}' not found. Defaulting to dark.")
            theme_name = "dark"

        self.current_theme = theme_name
        self.settings.setValue("theme", theme_name)
        
        theme_data = self.themes[theme_name]
        stylesheet_path = theme_data["stylesheet"]

        try:
            with open(stylesheet_path, "r") as f:
                self.app.setStyleSheet(f.read())
            print(f"Applied {theme_name} theme.")
        except FileNotFoundError:
            print(f"Stylesheet not found for {theme_name} theme.")
            
    def get_current_theme_icons(self):
        """Returns the icon set for the current theme."""
        return self.themes[self.current_theme]["icons"]

    def get_icon(self, icon_name):
        """Gets a specific QIcon for the current theme."""
        icons = self.get_current_theme_icons()
        path = icons.get(icon_name)
        if path:
            return QIcon(str(path))
        return QIcon() # Return an empty icon if not found

    def toggle_theme(self):
        """Switches to the other theme."""
        new_theme = "light" if self.current_theme == "dark" else "dark"
        self.apply_theme(new_theme)
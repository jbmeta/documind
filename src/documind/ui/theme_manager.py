import pathlib
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import QSettings

ASSETS_PATH = pathlib.Path(__file__).parent.parent / "assets"

class ThemeManager:
    """Manages the application's visual themes and settings."""
    def __init__(self, app):
        self.app = app
        self.settings = QSettings("DocuMind", "DocuMindApp")
        
        self.themes = {
            "dark": {
                "stylesheet": ASSETS_PATH / "dark_style.qss",
                "icons": {
                    "add": ASSETS_PATH / "plus-square-light.svg",
                    "send": ASSETS_PATH / "send-light.svg",
                    "toggle": ASSETS_PATH / "sun.svg",
                    "document": ASSETS_PATH / "file-text-light.svg", # <-- New Icon
                }
            },
            "light": {
                "stylesheet": ASSETS_PATH / "light_style.qss",
                "icons": {
                    "add": ASSETS_PATH / "plus-square-dark.svg",
                    "send": ASSETS_PATH / "send-dark.svg",
                    "toggle": ASSETS_PATH / "moon.svg",
                    "document": ASSETS_PATH / "file-text-dark.svg", # <-- New Icon
                }
            }
        }
        
        self.current_theme = self.settings.value("theme", "dark")

    def apply_theme(self, theme_name):
        if theme_name not in self.themes:
            theme_name = "dark"
        self.current_theme = theme_name
        self.settings.setValue("theme", theme_name)
        stylesheet_path = self.themes[theme_name]["stylesheet"]
        try:
            with open(stylesheet_path, "r") as f:
                self.app.setStyleSheet(f.read())
            print(f"Successfully applied {theme_name} theme.")
        except FileNotFoundError:
            print(f"Stylesheet not found for {theme_name} theme at {stylesheet_path}")
            
    def get_icon(self, icon_name):
        path = self.themes[self.current_theme]["icons"].get(icon_name)
        if path and path.exists():
            return QIcon(str(path))
        return QIcon()

    def toggle_theme(self):
        new_theme = "light" if self.current_theme == "dark" else "dark"
        self.apply_theme(new_theme)
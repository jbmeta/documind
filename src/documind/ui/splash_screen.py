import time
import pathlib
from PyQt6.QtCore import Qt, QObject, QThread, pyqtSignal
from PyQt6.QtGui import QPixmap, QFont
from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout, QFrame, QApplication

from documind.core.ai_core import AICore

# --- Worker for background initialization ---
class AppInitializer(QObject):
    """Performs heavy initialization in the background."""
    finished = pyqtSignal(AICore)
    progress = pyqtSignal(str)

    def run(self):
        """The main work of the thread."""
        def status_update(message):
            self.progress.emit(message)
            # A tiny sleep gives the UI time to redraw the message
            time.sleep(1.2)

        ai_core = AICore(status_callback=status_update)
        
        status_update("Unfolding knowledge... Almost there!")
        time.sleep(1) # A brief moment for the user to see the final message

        self.finished.emit(ai_core)


# --- The Custom Splash Screen Widget ---
class SplashScreen(QWidget):
    """A custom splash screen with background, image, and text."""
    def __init__(self, image_path):
        super().__init__()
        self.setWindowFlags(Qt.WindowType.SplashScreen | Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        layout = QVBoxLayout(self)
        self.setLayout(layout)

        self.background_frame = QFrame(self)
        self.background_frame.setObjectName("backgroundFrame")
        layout.addWidget(self.background_frame)

        content_layout = QVBoxLayout(self.background_frame)
        content_layout.setContentsMargins(70, 70, 70, 70)

        # Image
        pixmap = QPixmap(str(image_path))
        image_label = QLabel()
        image_label.setPixmap(pixmap.scaled(128, 128, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        content_layout.addWidget(image_label)
        
        # Main Title
        title_label = QLabel("DocuMind")
        title_font = QFont()
        title_font.setPointSize(32)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        content_layout.addWidget(title_label)
        
        # Subtitle/Status Label
        self.status_label = QLabel("Reticulating splines...")
        status_font = QFont()
        status_font.setPointSize(12)
        self.status_label.setFont(status_font)
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        content_layout.addWidget(self.status_label)
        
        self.setStyleSheet("""
            #backgroundFrame {
                background-color: #2e2e2e;
                color: #e0e0e0;
                border-radius: 15px;
            }
            QLabel {
                background-color: transparent;
                color: #e0e0e0;
            }
        """)

    def showMessage(self, message):
        """Public method to update the status message."""
        self.status_label.setText(message)
        QApplication.processEvents()
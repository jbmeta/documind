import sys
import pathlib
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QListWidget, QLineEdit, QTextEdit, QLabel, QSplitter,
    QFileDialog
)
# Note the updated import path
from documind.ui.theme_manager import ThemeManager

class DocuMindApp(QMainWindow):
    def __init__(self, theme_manager):
        super().__init__()
        self.theme_manager = theme_manager
        
        self.setWindowTitle("DocuMind")
        self.setGeometry(100, 100, 1200, 800)
        self.setAcceptDrops(True)
        
        # --- THIS IS THE CORRECTED LINE ---
        # Since this file is in 'ui', we go up two levels (.parent.parent) 
        # to reach the 'documind' directory where 'assets' is located.
        self.assets_path = pathlib.Path(__file__).parent.parent / "assets"
        
        self.splitter = QSplitter(Qt.Orientation.Horizontal)
        self.setCentralWidget(self.splitter)

        self.setup_left_pane()
        self.setup_right_pane()
        self.splitter.setSizes([300, 900])
        self.update_icons()
    
    # ... (all other methods like setup_left_pane, setup_right_pane, update_icons, etc., remain exactly the same as the last version) ...
    # The only change needed inside this class is the self.assets_path line above.
    # For completeness, here are the rest of the methods again without changes.

    def setup_left_pane(self):
        left_pane = QWidget()
        left_layout = QVBoxLayout(left_pane)
        left_layout.setContentsMargins(10, 10, 10, 10)
        self.add_files_button = QPushButton("Add Documents...")
        self.add_files_button.setIconSize(QSize(18, 18))
        self.add_files_button.clicked.connect(self.open_file_dialog)
        left_layout.addWidget(self.add_files_button)
        left_layout.addWidget(QLabel("Documents"))
        self.file_list_widget = QListWidget()
        left_layout.addWidget(self.file_list_widget)
        self.theme_toggle_button = QPushButton("Toggle Theme")
        self.theme_toggle_button.setIconSize(QSize(18, 18))
        self.theme_toggle_button.clicked.connect(self.toggle_theme)
        left_layout.addWidget(self.theme_toggle_button, alignment=Qt.AlignmentFlag.AlignBottom)
        self.splitter.addWidget(left_pane)

    def setup_right_pane(self):
        right_pane = QWidget()
        right_layout = QVBoxLayout(right_pane)
        right_layout.setContentsMargins(10, 10, 10, 10)
        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        right_layout.addWidget(self.chat_display)
        question_layout = QHBoxLayout()
        self.question_input = QLineEdit()
        self.question_input.setPlaceholderText("Ask a question about your documents...")
        self.ask_button = QPushButton("Ask")
        self.ask_button.setIconSize(QSize(18, 18))
        question_layout.addWidget(self.question_input)
        question_layout.addWidget(self.ask_button)
        right_layout.addLayout(question_layout)
        self.splitter.addWidget(right_pane)

    def update_icons(self):
        self.add_files_button.setIcon(self.theme_manager.get_icon("add"))
        self.ask_button.setIcon(self.theme_manager.get_icon("send"))
        self.theme_toggle_button.setIcon(self.theme_manager.get_icon("toggle"))

    def toggle_theme(self):
        self.theme_manager.toggle_theme()
        self.update_icons()

    def open_file_dialog(self):
        file_paths, _ = QFileDialog.getOpenFileNames(
            self, "Select PDF Files", "", "PDF Files (*.pdf)"
        )
        if file_paths:
            self.handle_files(file_paths)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            event.ignore()

    def dropEvent(self, event):
        if event.mimeData().hasUrls():
            file_paths = [url.toLocalFile() for url in event.mimeData().urls()]
            self.handle_files(file_paths)
        else:
            event.ignore()

    def handle_files(self, file_paths: list[str]):
        pdf_paths = [path for path in file_paths if path.lower().endswith('.pdf')]
        if pdf_paths:
            for path in pdf_paths:
                self.file_list_widget.addItem(pathlib.Path(path).name)
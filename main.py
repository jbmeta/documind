import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QListWidget, QLineEdit, QTextEdit, QLabel
)

class DocuMindApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("DocuMind")
        self.setGeometry(100, 100, 800, 600)

        # Main container widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # --- UI Widgets ---

        # 1. Folder Selection Button
        self.select_folder_button = QPushButton("Select PDF Folder")
        main_layout.addWidget(self.select_folder_button)

        # 2. Indexed Files List
        main_layout.addWidget(QLabel("Indexed Files:"))
        self.file_list_widget = QListWidget()
        main_layout.addWidget(self.file_list_widget)

        # 3. Question Input and Submit Button (in a horizontal layout)
        question_layout = QHBoxLayout()
        self.question_input = QLineEdit()
        self.question_input.setPlaceholderText("Ask a question about your documents...")
        self.ask_button = QPushButton("Ask")
        
        question_layout.addWidget(self.question_input)
        question_layout.addWidget(self.ask_button)
        
        main_layout.addLayout(question_layout)

        # 4. Answer Display Area
        main_layout.addWidget(QLabel("Answer:"))
        self.answer_display = QTextEdit()
        self.answer_display.setReadOnly(True) # User should not be able to type here
        main_layout.addWidget(self.answer_display)


# This is the standard entry point for a Python script
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = DocuMindApp()
    window.show()
    sys.exit(app.exec())
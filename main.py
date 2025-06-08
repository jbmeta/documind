import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QListWidget, QLineEdit, QTextEdit, QLabel,
    QFileDialog  # <-- New import
)

class DocuMindApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("DocuMind")
        self.setGeometry(100, 100, 800, 600)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # --- UI Widgets ---

        # 1. Folder Selection Button
        self.select_folder_button = QPushButton("Select PDF Folder")
        self.select_folder_button.clicked.connect(self.select_folder)  # <-- Connect signal to slot
        main_layout.addWidget(self.select_folder_button)

        # 2. Indexed Files List
        main_layout.addWidget(QLabel("Indexed Files:"))
        self.file_list_widget = QListWidget()
        main_layout.addWidget(self.file_list_widget)

        # 3. Question Input and Submit Button
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
        self.answer_display.setReadOnly(True)
        main_layout.addWidget(self.answer_display)

    # v-- This is our new slot method --v
    def select_folder(self):
        """Opens a dialog to select a folder and prints the path."""
        folder_path = QFileDialog.getExistingDirectory(self, "Select Folder")
        
        if folder_path:
            print(f"Folder selected: {folder_path}")
            # In the next steps, we will add the logic here to
            # find all PDFs in this folder and process them.
            # For now, we'll just update the UI a little.
            self.answer_display.setText(f"Selected folder: {folder_path}\n\nReady to process files...")
    # ^-- End of new slot method --^

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = DocuMindApp()
    window.show()
    sys.exit(app.exec())
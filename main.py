import sys
import os # <-- New import
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QListWidget, QLineEdit, QTextEdit, QLabel,
    QFileDialog
)
# v-- New import for our backend functions --v
from document_processor import find_pdf_files, extract_text_from_pdf

class DocuMindApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("DocuMind")
        self.setGeometry(100, 100, 800, 600)

        # We'll store the list of PDF file paths here
        self.pdf_files = []

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # --- UI Widgets (no changes here) ---
        self.select_folder_button = QPushButton("Select PDF Folder")
        self.select_folder_button.clicked.connect(self.select_folder)
        main_layout.addWidget(self.select_folder_button)
        main_layout.addWidget(QLabel("Indexed Files:"))
        self.file_list_widget = QListWidget()
        main_layout.addWidget(self.file_list_widget)
        question_layout = QHBoxLayout()
        self.question_input = QLineEdit()
        self.question_input.setPlaceholderText("Ask a question about your documents...")
        self.ask_button = QPushButton("Ask")
        question_layout.addWidget(self.question_input)
        question_layout.addWidget(self.ask_button)
        main_layout.addLayout(question_layout)
        main_layout.addWidget(QLabel("Answer:"))
        self.answer_display = QTextEdit()
        self.answer_display.setReadOnly(True)
        main_layout.addWidget(self.answer_display)

    def select_folder(self):
        folder_path = QFileDialog.getExistingDirectory(self, "Select Folder")
        
        if folder_path:
            # Update the UI to show we're working
            self.answer_display.setText(f"Scanning folder: {folder_path}...")
            self.file_list_widget.clear()
            QApplication.processEvents() # Force UI update

            # Call our new backend function
            self.pdf_files = find_pdf_files(folder_path)
            
            if not self.pdf_files:
                self.answer_display.append("\nNo PDF files found in this folder.")
                return

            self.answer_display.append(f"\nFound {len(self.pdf_files)} PDF file(s).")

            # Populate the file list widget in the UI
            for pdf_path in self.pdf_files:
                self.file_list_widget.addItem(pdf_path.name)
            
            # --- Verification Step ---
            # For now, let's just process the first file to test our pipeline
            first_pdf_path = self.pdf_files[0]
            print(f"--- Extracting text from: {first_pdf_path.name} ---")
            
            text = extract_text_from_pdf(first_pdf_path)
            
            print(text) # Print extracted text to the console
            print("--- End of extracted text ---")
            
            self.answer_display.append("\nReady to answer questions.")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = DocuMindApp()
    window.show()
    sys.exit(app.exec())
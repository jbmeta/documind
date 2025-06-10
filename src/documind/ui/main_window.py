import sys
import pathlib
import traceback
from PyQt6.QtCore import Qt, QSize, QObject, QThread, pyqtSignal
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QListWidget, QLineEdit, QTextEdit, QLabel, QSplitter,
    QFileDialog, QProgressBar, QMessageBox
)
from documind.ui.theme_manager import ThemeManager
from documind.core.ai_core import AICore
from documind.core.document_processor import process_document

# Worker class for background processing
class ProcessingWorker(QObject):
    finished = pyqtSignal()
    progress = pyqtSignal(int, str)
    error = pyqtSignal(str)
    document_processed = pyqtSignal(str) 

    def __init__(self, file_paths: list[str], ai_core: AICore):
        super().__init__()
        self.file_paths = file_paths
        self.ai_core = ai_core
        self.is_running = True

    def run(self):
        try:
            total_files = len(self.file_paths)
            for i, path_str in enumerate(self.file_paths):
                if not self.is_running:
                    break
                pdf_path = pathlib.Path(path_str)
                self.progress.emit(int((i / total_files) * 100), f"Processing: {pdf_path.name}")
                if not self.ai_core.has_document(pdf_path):
                    process_document(pdf_path, self.ai_core)
                    self.document_processed.emit(pdf_path.name)
                else:
                    self.progress.emit(int((i / total_files) * 100), f"Skipping existing file: {pdf_path.name}")

            if self.is_running:
                self.progress.emit(100, "Processing complete.")
        except Exception as e:
            error_traceback = traceback.format_exc()
            self.error.emit(f"An error occurred in the processing thread:\n\n{error_traceback}")
        finally:
            self.finished.emit()

    def stop(self):
        self.is_running = False

# Main Window Class
class DocuMindApp(QMainWindow):
    def __init__(self, theme_manager: ThemeManager, ai_core: AICore):
        super().__init__()
        
        self.assets_path = pathlib.Path(__file__).parent.parent / "assets"
        self.theme_manager = theme_manager
        self.ai_core = ai_core
        self.thread = None
        self.worker = None

        self.setWindowTitle("DocuMind")
        
        self.setWindowIcon(QIcon(str(self.assets_path / "app_icon.png")))

        self.setGeometry(100, 100, 1200, 800)
        self.setAcceptDrops(True)
        
        self.splitter = QSplitter(Qt.Orientation.Horizontal)
        self.setCentralWidget(self.splitter)

        self.setup_left_pane()
        self.setup_right_pane()
        self.setup_status_bar()
        self.splitter.setSizes([300, 900])
        self.update_icons()
        self.populate_document_list_from_library()

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
        
    def setup_status_bar(self):
        self.status_bar = self.statusBar()
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.status_bar.addPermanentWidget(self.progress_bar)

    def populate_document_list_from_library(self):
        self.file_list_widget.clear()
        doc_names = self.ai_core.get_document_list()
        self.file_list_widget.addItems(doc_names)
        
    def add_document_to_list(self, doc_name: str):
        self.file_list_widget.addItem(doc_name)

    def handle_files(self, file_paths: list[str]):
        pdf_paths = [path for path in file_paths if path.lower().endswith('.pdf')]
        if not pdf_paths: return

        self.add_files_button.setEnabled(False)
        self.progress_bar.setValue(0)
        self.progress_bar.setVisible(True)

        self.thread = QThread()
        self.worker = ProcessingWorker(pdf_paths, self.ai_core)
        self.worker.moveToThread(self.thread)

        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.on_processing_finished)
        self.worker.progress.connect(self.update_progress)
        self.worker.error.connect(self.on_processing_error)
        self.worker.document_processed.connect(self.add_document_to_list)

        self.thread.start()

    def update_progress(self, value: int, text: str):
        self.progress_bar.setValue(value)
        self.statusBar().showMessage(text)

    def on_processing_finished(self):
        self.statusBar().showMessage("Ready.", 5000)
        self.add_files_button.setEnabled(True)
        self.progress_bar.setVisible(False)
        if self.thread:
            self.thread.quit()
            self.thread.wait()
            self.thread = None
            self.worker = None

    def on_processing_error(self, error_message):
        self.statusBar().showMessage("An error occurred during processing.")
        error_dialog = QMessageBox(self)
        error_dialog.setIcon(QMessageBox.Icon.Critical)
        error_dialog.setText("Processing Error")
        error_dialog.setInformativeText("A critical error occurred while processing the documents.")
        error_dialog.setDetailedText(error_message)
        error_dialog.setStandardButtons(QMessageBox.StandardButton.Ok)
        error_dialog.exec()

    def closeEvent(self, event):
        if self.worker:
            self.worker.stop()
        if self.thread:
            self.thread.quit()
            self.thread.wait()
        event.accept()

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
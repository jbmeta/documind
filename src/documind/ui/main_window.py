import sys
import pathlib
import traceback
import asyncio
import markdown
from PyQt6.QtCore import Qt, QSize, QObject, QThread, pyqtSignal
from PyQt6.QtGui import QIcon, QFont
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QListWidget, QListWidgetItem, QLineEdit, QLabel, QSplitter,
    QFileDialog, QProgressBar, QMessageBox, QListView
)
from documind.ui.theme_manager import ThemeManager
from documind.core.ai_core import AICore
from documind.core.document_processor import process_document
from documind.ui.custom_widgets import DocumentListItemWidget
from documind.ui.chat_model import ChatModel
from documind.ui.chat_delegate import ChatDelegate

# ... (Worker classes are unchanged) ...
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
                if not self.is_running: break
                pdf_path = pathlib.Path(path_str)
                self.progress.emit(int((i / total_files) * 100), f"Processing: {pdf_path.name}")
                if not self.ai_core.is_file_processed(pdf_path):
                    process_document(pdf_path, self.ai_core)
                    self.document_processed.emit(pdf_path.name)
                else:
                    self.progress.emit(int((i / total_files) * 100), f"Skipping existing file: {pdf_path.name}")
            if self.is_running: self.progress.emit(100, "Processing complete.")
        except Exception as e:
            self.error.emit(f"An error occurred in the processing thread:\n\n{traceback.format_exc()}")
        finally:
            self.finished.emit()
    def stop(self): self.is_running = False

class QueryWorker(QObject):
    finished = pyqtSignal(str)
    def __init__(self, question: str, ai_core: AICore):
        super().__init__()
        self.question = question
        self.ai_core = ai_core
        self.is_cancelled = False
    def run(self):
        if self.is_cancelled:
            self.finished.emit("Query cancelled.")
            return
        context = self.ai_core.query(self.question)
        if self.is_cancelled:
            self.finished.emit("Query cancelled.")
            return
        answer = self.ai_core.generate_response(self.question, context)
        if not self.is_cancelled:
            self.finished.emit(answer)
    def stop(self): self.is_cancelled = True

class DocuMindApp(QMainWindow):
    # ... (The rest of this file is unchanged from the last version) ...
    def __init__(self, theme_manager: ThemeManager, ai_core: AICore):
        super().__init__()
        self.theme_manager = theme_manager
        self.ai_core = ai_core
        self.processing_thread, self.query_thread = None, None
        self.processing_worker, self.query_worker = None, None
        self.document_widgets = {}
        self.setWindowTitle("DocuMind")
        self.setWindowIcon(QIcon(str(pathlib.Path(__file__).parent.parent / "assets" / "app_icon.png")))
        self.setGeometry(100, 100, 1200, 800)
        self.setAcceptDrops(True)
        self.splitter = QSplitter(Qt.Orientation.Horizontal)
        self.setCentralWidget(self.splitter)
        self.setup_left_pane()
        self.setup_right_pane()
        self.setup_status_bar()
        self.splitter.setSizes([350, 850])
        self.update_icons()
        self.populate_document_list_from_library()

    def setup_right_pane(self):
        right_pane_container = QWidget()
        right_layout = QVBoxLayout(right_pane_container)
        right_layout.setContentsMargins(10, 10, 10, 10)
        self.chat_view = QListView()
        self.chat_model = ChatModel()
        self.chat_view.setModel(self.chat_model)
        self.chat_delegate = ChatDelegate(self.chat_view, self.theme_manager)
        self.chat_view.setItemDelegate(self.chat_delegate)
        self.chat_view.setStyleSheet("background-color: transparent; border: none;")
        self.chat_view.setWordWrap(True)
        self.chat_view.setSelectionMode(QListView.SelectionMode.NoSelection)
        self.chat_view.setVerticalScrollMode(QListView.ScrollMode.ScrollPerPixel)
        self.chat_view.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        right_layout.addWidget(self.chat_view)
        question_layout = QHBoxLayout()
        self.question_input = QLineEdit()
        self.question_input.setPlaceholderText("Ask a question about your documents...")
        self.question_input.returnPressed.connect(self.handle_ask_question)
        question_layout.addWidget(self.question_input)
        self.ask_button = QPushButton("Ask")
        self.ask_button.setIconSize(QSize(18, 18))
        self.ask_button.clicked.connect(self.handle_ask_question)
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.cancel_query)
        self.cancel_button.setVisible(False)
        question_layout.addWidget(self.ask_button)
        question_layout.addWidget(self.cancel_button)
        right_layout.addLayout(question_layout)
        self.splitter.addWidget(right_pane_container)

    def add_message(self, text: str, role: str):
        self.chat_model.add_message(role=role, text=text)
        self.chat_view.scrollToBottom()

    def handle_ask_question(self):
        question = self.question_input.text().strip()
        if not question or self.query_thread is not None: return
        self.add_message(question, "user")
        self.question_input.clear()
        self.ask_button.setVisible(False)
        self.cancel_button.setVisible(True)
        self.question_input.setEnabled(False)
        self.statusBar().showMessage("Thinking...")
        self.query_thread = QThread()
        self.query_worker = QueryWorker(question, self.ai_core)
        self.query_worker.moveToThread(self.query_thread)
        self.query_worker.finished.connect(self.on_query_finished)
        self.query_thread.started.connect(self.query_worker.run)
        self.query_thread.start()

    def on_query_finished(self, answer):
        if not self.query_worker: return
        if self.query_worker.is_cancelled: answer = "Query cancelled by user."
        self.add_message(answer, "ai")
        self.ask_button.setVisible(True)
        self.cancel_button.setVisible(False)
        self.ask_button.setEnabled(True)
        self.question_input.setEnabled(True)
        self.statusBar().showMessage("Ready.", 5000)
        if self.query_thread: self.query_thread.quit(); self.query_thread.wait()
        self.query_thread = None
        self.query_worker = None
    
    def setup_status_bar(self):
        self.status_bar = self.statusBar()
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.status_bar.addPermanentWidget(self.progress_bar)
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
        # Apply stylesheet to remove default item borders and padding
        self.file_list_widget.setStyleSheet("""
            QListWidget::item {
                border: none;
                padding: 0px; 
                background-color: transparent; /* Ensure item background doesn't interfere */
            }
        """)
        left_layout.addWidget(self.file_list_widget)
        self.theme_toggle_button = QPushButton("Toggle Theme")
        self.theme_toggle_button.setIconSize(QSize(18, 18))
        self.theme_toggle_button.clicked.connect(self.toggle_theme)
        left_layout.addWidget(self.theme_toggle_button, alignment=Qt.AlignmentFlag.AlignBottom)
        self.splitter.addWidget(left_pane)
    def populate_document_list_from_library(self):
        self.file_list_widget.clear()
        self.document_widgets.clear()
        doc_names = self.ai_core.get_processed_files()
        for name in doc_names:
            self.add_document_to_list(name, status="Ready")
    def add_document_to_list(self, doc_name: str, status: str = "Queued"):
        if doc_name in self.document_widgets: return
        icon = self.theme_manager.get_icon("document")
        custom_widget = DocumentListItemWidget(doc_name, icon, status)
        list_item = QListWidgetItem(self.file_list_widget)
        list_item.setSizeHint(custom_widget.sizeHint())
        self.file_list_widget.setItemWidget(list_item, custom_widget)
        self.document_widgets[doc_name] = custom_widget
    def update_document_status(self, doc_name: str, status: str, color: str = "#888"):
        if doc_name in self.document_widgets:
            self.document_widgets[doc_name].set_status(status, color)
    def handle_files(self, file_paths: list[str]):
        pdf_paths = [pathlib.Path(p) for p in file_paths if p.lower().endswith('.pdf')]
        new_files_to_process = [p for p in pdf_paths if not self.ai_core.is_file_processed(p)]
        if not new_files_to_process:
            self.statusBar().showMessage("All selected files have already been processed.", 5000)
            return
        for p in new_files_to_process:
            self.add_document_to_list(p.name, status="Queued")
        self.add_files_button.setEnabled(False)
        self.progress_bar.setValue(0)
        self.progress_bar.setVisible(True)
        self.processing_thread = QThread()
        self.processing_worker = ProcessingWorker([str(p) for p in new_files_to_process], self.ai_core)
        self.processing_worker.moveToThread(self.processing_thread)
        self.processing_thread.started.connect(self.processing_worker.run)
        self.processing_worker.finished.connect(self.on_processing_finished)
        self.processing_worker.progress.connect(self.update_progress_status)
        self.processing_worker.error.connect(self.on_processing_error)
        self.processing_worker.document_processed.connect(lambda name: self.update_document_status(name, "Ready", "#2ecc71"))
        self.processing_thread.start()
    def update_progress_status(self, value: int, text: str):
        self.progress_bar.setValue(value)
        self.statusBar().showMessage(text)
        if text.startswith("Processing: "):
            doc_name = text.split("Processing: ", 1)[1]
            self.update_document_status(doc_name, "Processing...", "#3498db")
    def update_icons(self):
        self.add_files_button.setIcon(self.theme_manager.get_icon("add"))
        self.ask_button.setIcon(self.theme_manager.get_icon("send"))
        self.theme_toggle_button.setIcon(self.theme_manager.get_icon("toggle"))
        if hasattr(self, 'document_widgets'):
            for widget in self.document_widgets.values():
                widget.icon_label.setPixmap(self.theme_manager.get_icon("document").pixmap(QSize(18, 18)))
    def toggle_theme(self):
        self.theme_manager.toggle_theme()
        self.chat_view.viewport().update()
        self.update_icons()
    def open_file_dialog(self):
        file_paths, _ = QFileDialog.getOpenFileNames( self, "Select PDF Files", "", "PDF Files (*.pdf)")
        if file_paths: self.handle_files(file_paths)
    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls(): event.acceptProposedAction()
        else: event.ignore()
    def dropEvent(self, event):
        if event.mimeData().hasUrls():
            file_paths = [url.toLocalFile() for url in event.mimeData.urls()]
            self.handle_files(file_paths)
        else: event.ignore()
    def cancel_query(self):
        print("[LOG] UI: Cancel button clicked.")
        if self.query_worker: self.query_worker.stop()
        self.on_query_finished("Query cancelled by user.")
    def on_processing_finished(self):
        self.statusBar().showMessage("Ready.", 5000)
        self.add_files_button.setEnabled(True)
        self.progress_bar.setVisible(False)
        if self.processing_thread:
            self.processing_thread.quit()
            self.processing_thread.wait()
            self.processing_thread = None
            self.processing_worker = None
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
        if self.processing_worker: self.processing_worker.stop()
        if self.processing_thread: self.processing_thread.quit(); self.processing_thread.wait()
        if self.query_worker: self.query_worker.stop()
        if self.query_thread: self.query_thread.quit(); self.query_thread.wait()
        event.accept()
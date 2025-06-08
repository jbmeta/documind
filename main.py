import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget

class DocuMindApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("DocuMind")
        self.setGeometry(100, 100, 800, 600) # x, y, width, height

        # The central widget will hold our layout and other UI elements
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

# This is the standard entry point for a Python script
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = DocuMindApp()
    window.show()
    sys.exit(app.exec())
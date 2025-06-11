from PyQt6.QtWidgets import QWidget, QHBoxLayout, QLabel, QSizePolicy
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import QSize, Qt

class DocumentListItemWidget(QWidget):
    """A custom widget for an item in the document list."""
    def __init__(self, file_name: str, icon: QIcon, status: str = "Ready"):
        super().__init__()

        layout = QHBoxLayout()
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(10)

        self.icon_label = QLabel()
        self.icon_label.setPixmap(icon.pixmap(QSize(18, 18)))
        layout.addWidget(self.icon_label)

        # Filename Label
        self.name_label = QLabel(file_name)
        self.name_label.setToolTip(file_name)
        # Let the name label expand horizontally
        self.name_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        self.name_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        layout.addWidget(self.name_label)

        # Status Label
        self.status_label = QLabel(status)
        self.status_label.setStyleSheet("color: #888;")
        self.status_label.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Preferred)
        layout.addWidget(self.status_label)

        self.setLayout(layout)

    def set_status(self, status: str, color: str = "#888"):
        """Updates the text and color of the status label."""
        self.status_label.setText(status)
        self.status_label.setStyleSheet(f"color: {color};")
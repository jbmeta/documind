from PyQt6.QtCore import QAbstractListModel, QModelIndex, Qt, QObject
from dataclasses import dataclass, field

@dataclass
class ChatMessage:
    """A simple data class to hold message information."""
    text: str
    role: str
    
class ChatModel(QAbstractListModel):
    """The data model for the chat conversation."""
    def __init__(self, parent: QObject | None = None):
        super().__init__(parent)
        self._messages: list[ChatMessage] = []

    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:
        return len(self._messages)

    def data(self, index: QModelIndex, role: int = Qt.ItemDataRole.DisplayRole):
        if not index.isValid() or not (0 <= index.row() < self.rowCount()):
            return None
        
        if role == Qt.ItemDataRole.DisplayRole:
            return self._messages[index.row()]
        
        return None

    def add_message(self, role: str, text: str):
        """Adds a new message to the end of the model."""
        self.beginInsertRows(QModelIndex(), self.rowCount(), self.rowCount())
        self._messages.append(ChatMessage(text=text, role=role))
        self.endInsertRows()
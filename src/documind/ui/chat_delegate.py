import markdown
from PyQt6.QtWidgets import QStyledItemDelegate, QStyleOptionViewItem
from PyQt6.QtGui import QPainter, QFontMetrics, QColor # <-- Import QColor
from PyQt6.QtCore import QRect, QPoint, Qt, QModelIndex, QSize

from .chat_model import ChatMessage

class ChatDelegate(QStyledItemDelegate):
    """A delegate for drawing chat message bubbles."""
    def __init__(self, parent, theme_manager):
        super().__init__(parent)
        self.theme_manager = theme_manager

    def paint(self, painter: QPainter, option: QStyleOptionViewItem, index: QModelIndex):
        """Draws the chat bubble for each item."""
        message: ChatMessage = index.data(Qt.ItemDataRole.DisplayRole)
        if not message:
            return

        painter.save()
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # --- THIS IS THE FIX ---
        # Get theme-specific colors and wrap them in QColor objects
        is_dark = self.theme_manager.current_theme == "dark"
        if message.role == "user":
            bg_color = QColor("#007ACC")
            text_color = QColor(Qt.GlobalColor.white)
            alignment = Qt.AlignmentFlag.AlignRight
        else: # AI
            bg_color = QColor("#4A4D4F") if is_dark else QColor("#F0F0F0")
            text_color = QColor("#DDDDDD") if is_dark else QColor("#333333")
            alignment = Qt.AlignmentFlag.AlignLeft
        # --- END OF FIX ---

        item_rect = option.rect
        plain_text = message.text
        rich_text = markdown.markdown(message.text).strip()

        # Calculate the required rectangle for the wrapped text
        text_rect = self.getTextRect(item_rect, plain_text, painter.font())
        
        bubble_x = item_rect.right() - text_rect.width() - 18 if alignment == Qt.AlignmentFlag.AlignRight else item_rect.left() + 18
        bubble_y = item_rect.top() + 8
        bubble_rect = QRect(bubble_x, bubble_y, text_rect.width(), text_rect.height())

        # Now, painter.setBrush receives the correct QColor type
        painter.setBrush(bg_color)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(bubble_rect, 15, 15)
        
        painter.setPen(text_color)
        painter.drawText(bubble_rect, Qt.TextFlag.TextWordWrap | Qt.AlignmentFlag.AlignVCenter, plain_text)

        painter.restore()

    def sizeHint(self, option: QStyleOptionViewItem, index: QModelIndex) -> QSize:
        """Provides the required size for each item."""
        message: ChatMessage = index.data(Qt.ItemDataRole.DisplayRole)
        if not message:
            return QSize()
            
        text_rect = self.getTextRect(option.rect, message.text, option.font)
        return QSize(text_rect.width() + 20, text_rect.height() + 10)

    def getTextRect(self, rect: QRect, text: str, font) -> QRect:
        """Calculates the bounding rectangle needed for the wrapped text."""
        # Use a slightly larger portion of the width
        text_width = rect.width() * 0.75
        
        metrics = QFontMetrics(font)
        # Calculate bounding rect with padding considered
        text_rect = metrics.boundingRect(QRect(0, 0, int(text_width - 36), 10000), Qt.TextFlag.TextWordWrap, text)
        
        # Add padding back to the final calculated rect for correct sizing
        text_rect.setWidth(text_rect.width() + 36)
        text_rect.setHeight(text_rect.height() + 36)
        return text_rect

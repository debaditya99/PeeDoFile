from PyQt5.QtWidgets import (QWidget, QTextEdit, QToolBar, QAction,
                           QFontComboBox, QSpinBox, QComboBox)
from PyQt5.QtGui import (QTextCharFormat, QFont, QTextCursor, QPalette, QColor,
                       QPainter, QPen)
from PyQt5.QtCore import Qt, pyqtSignal, QSize

class PDFTextEditor(QWidget):
    textEditingStarted = pyqtSignal()
    textEditingFinished = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.text_boxes = []
        self.current_text_box = None
        self.setup_format_toolbar()
        
        # Make the widget transparent for overlaying
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.pdf_rect = None

    def set_pdf_rect(self, rect):
        """Set the rectangle that represents the PDF boundaries"""
        self.pdf_rect = rect
        self.setGeometry(rect)

    def setup_format_toolbar(self):
        """Create text formatting toolbar"""
        self.format_toolbar = QToolBar()
        self.format_toolbar.setIconSize(QSize(16, 16))

        # Font family
        self.font_family = QFontComboBox()
        self.font_family.currentFontChanged.connect(self.font_family_changed)
        self.format_toolbar.addWidget(self.font_family)

        # Font size
        self.font_size = QSpinBox()
        self.font_size.setMinimum(8)
        self.font_size.setMaximum(72)
        self.font_size.setValue(12)
        self.font_size.valueChanged.connect(self.font_size_changed)
        self.format_toolbar.addWidget(self.font_size)

        self.format_toolbar.addSeparator()

        # Bold
        self.bold_action = QAction('Bold', self)
        self.bold_action.setCheckable(True)
        self.bold_action.triggered.connect(self.text_bold)
        self.format_toolbar.addAction(self.bold_action)

        # Italic
        self.italic_action = QAction('Italic', self)
        self.italic_action.setCheckable(True)
        self.italic_action.triggered.connect(self.text_italic)
        self.format_toolbar.addAction(self.italic_action)

        # Underline
        self.underline_action = QAction('Underline', self)
        self.underline_action.setCheckable(True)
        self.underline_action.triggered.connect(self.text_underline)
        self.format_toolbar.addAction(self.underline_action)

        # Strikethrough
        self.strike_action = QAction('Strikethrough', self)
        self.strike_action.setCheckable(True)
        self.strike_action.triggered.connect(self.text_strike)
        self.format_toolbar.addAction(self.strike_action)

        self.format_toolbar.addSeparator()

        # Alignment
        self.align_left_action = QAction('Left', self)
        self.align_left_action.setCheckable(True)
        self.align_left_action.triggered.connect(lambda: self.text_align(Qt.AlignLeft))
        self.format_toolbar.addAction(self.align_left_action)

        self.align_center_action = QAction('Center', self)
        self.align_center_action.setCheckable(True)
        self.align_center_action.triggered.connect(lambda: self.text_align(Qt.AlignCenter))
        self.format_toolbar.addAction(self.align_center_action)

        self.align_right_action = QAction('Right', self)
        self.align_right_action.setCheckable(True)
        self.align_right_action.triggered.connect(lambda: self.text_align(Qt.AlignRight))
        self.format_toolbar.addAction(self.align_right_action)

        self.align_justify_action = QAction('Justify', self)
        self.align_justify_action.setCheckable(True)
        self.align_justify_action.triggered.connect(lambda: self.text_align(Qt.AlignJustify))
        self.format_toolbar.addAction(self.align_justify_action)

        # Hide toolbar initially
        self.format_toolbar.hide()

    def create_text_box(self, pos):
        """Create a new text box at the given position"""
        if not self.pdf_rect:
            return None
            
        # Create text box
        text_box = TextBox(self)
        text_box.setFont(self.font_family.currentFont())
        text_box.setFontPointSize(self.font_size.value())
        text_box.textChanged.connect(self.text_box_changed)
        text_box.focusReceived.connect(self.text_box_focused)
        text_box.resizeStarted.connect(lambda: self.textEditingStarted.emit())
        text_box.resizeFinished.connect(lambda: self.textEditingFinished.emit())
        
        # Set initial size and position
        width, height = 200, 100
        x = max(0, min(pos.x() - width/2, self.pdf_rect.width() - width))
        y = max(0, min(pos.y() - height/2, self.pdf_rect.height() - height))
        text_box.setGeometry(int(x), int(y), width, height)
        
        text_box.show()
        text_box.raise_()  # Ensure it's on top
        self.text_boxes.append(text_box)
        self.current_text_box = text_box
        self.textEditingStarted.emit()
        return text_box

    def text_box_changed(self):
        """Handle text box content changes"""
        if self.current_text_box:
            cursor = self.current_text_box.textCursor()
            self.update_format_buttons(cursor)

    def text_box_focused(self, text_box):
        """Handle text box focus changes"""
        self.current_text_box = text_box
        self.textEditingStarted.emit()
        self.format_toolbar.show()

    def update_format_buttons(self, cursor):
        """Update format buttons based on current cursor position"""
        if not cursor:
            return

        format = cursor.charFormat()
        self.bold_action.setChecked(format.fontWeight() == QFont.Bold)
        self.italic_action.setChecked(format.fontItalic())
        self.underline_action.setChecked(format.fontUnderline())
        self.strike_action.setChecked(format.fontStrikeOut())

        block_format = cursor.blockFormat()
        alignment = block_format.alignment()
        self.align_left_action.setChecked(alignment == Qt.AlignLeft)
        self.align_center_action.setChecked(alignment == Qt.AlignCenter)
        self.align_right_action.setChecked(alignment == Qt.AlignRight)
        self.align_justify_action.setChecked(alignment == Qt.AlignJustify)

    def font_family_changed(self, font):
        if self.current_text_box:
            self.current_text_box.setCurrentFont(font)

    def font_size_changed(self, size):
        if self.current_text_box:
            self.current_text_box.setFontPointSize(size)

    def text_bold(self):
        if self.current_text_box:
            fmt = QTextCharFormat()
            fmt.setFontWeight(QFont.Bold if self.bold_action.isChecked() else QFont.Normal)
            self.merge_format(fmt)

    def text_italic(self):
        if self.current_text_box:
            fmt = QTextCharFormat()
            fmt.setFontItalic(self.italic_action.isChecked())
            self.merge_format(fmt)

    def text_underline(self):
        if self.current_text_box:
            fmt = QTextCharFormat()
            fmt.setFontUnderline(self.underline_action.isChecked())
            self.merge_format(fmt)

    def text_strike(self):
        if self.current_text_box:
            fmt = QTextCharFormat()
            fmt.setFontStrikeOut(self.strike_action.isChecked())
            self.merge_format(fmt)

    def text_align(self, alignment):
        if self.current_text_box:
            self.current_text_box.setAlignment(alignment)

    def merge_format(self, format):
        if self.current_text_box:
            cursor = self.current_text_box.textCursor()
            cursor.mergeCharFormat(format)
            self.current_text_box.mergeCurrentCharFormat(format)

    def get_toolbar(self):
        """Return the formatting toolbar"""
        return self.format_toolbar

    def clear_text_boxes(self):
        """Remove all text boxes"""
        for text_box in self.text_boxes:
            text_box.deleteLater()
        self.text_boxes.clear()
        self.current_text_box = None


class TextBox(QTextEdit):
    focusReceived = pyqtSignal(object)
    resizeStarted = pyqtSignal()
    resizeFinished = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFrameStyle(0)  # No frame
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        
        # Set transparent background with slight opacity
        palette = self.palette()
        palette.setColor(QPalette.Base, QColor(255, 255, 255, 180))
        self.setPalette(palette)

        # For resizing
        self.resizing = False
        self.resize_edge = None
        self.resize_start_pos = None
        self.resize_start_geometry = None
        self.min_size = QSize(50, 30)  # Minimum size for text box
        self.setMouseTracking(True)  # Track mouse movements for cursor changes
        
        # Edges and corners for resizing (in pixels)
        self.edge_size = 6

    def get_resize_edge(self, pos):
        """Determine which edge or corner the mouse is on"""
        rect = self.rect()
        x, y = pos.x(), pos.y()
        
        # Check corners first (they take priority)
        if x <= self.edge_size:
            if y <= self.edge_size:
                return 'top-left'
            elif y >= rect.height() - self.edge_size:
                return 'bottom-left'
        elif x >= rect.width() - self.edge_size:
            if y <= self.edge_size:
                return 'top-right'
            elif y >= rect.height() - self.edge_size:
                return 'bottom-right'
                
        # Then check edges
        if x <= self.edge_size:
            return 'left'
        elif x >= rect.width() - self.edge_size:
            return 'right'
        elif y <= self.edge_size:
            return 'top'
        elif y >= rect.height() - self.edge_size:
            return 'bottom'
            
        return None

    def get_cursor_for_edge(self, edge):
        """Return the appropriate cursor for the given edge"""
        if edge in ['top-left', 'bottom-right']:
            return Qt.SizeFDiagCursor
        elif edge in ['top-right', 'bottom-left']:
            return Qt.SizeBDiagCursor
        elif edge in ['left', 'right']:
            return Qt.SizeHorCursor
        elif edge in ['top', 'bottom']:
            return Qt.SizeVerCursor
        return Qt.ArrowCursor

    def mouseMoveEvent(self, event):
        if self.resizing and self.resize_edge and self.resize_start_pos:
            # Handle resizing
            pos = event.globalPos()
            diff = pos - self.resize_start_pos
            new_geometry = self.resize_start_geometry
            
            if 'right' in self.resize_edge:
                new_width = max(self.min_size.width(), new_geometry.width() + diff.x())
                new_geometry.setWidth(new_width)
            elif 'left' in self.resize_edge:
                max_x_diff = new_geometry.width() - self.min_size.width()
                x_diff = min(diff.x(), max_x_diff)
                new_geometry.setX(self.resize_start_geometry.x() + x_diff)
                new_geometry.setWidth(self.resize_start_geometry.width() - x_diff)

            if 'bottom' in self.resize_edge:
                new_height = max(self.min_size.height(), new_geometry.height() + diff.y())
                new_geometry.setHeight(new_height)
            elif 'top' in self.resize_edge:
                max_y_diff = new_geometry.height() - self.min_size.height()
                y_diff = min(diff.y(), max_y_diff)
                new_geometry.setY(self.resize_start_geometry.y() + y_diff)
                new_geometry.setHeight(self.resize_start_geometry.height() - y_diff)

            self.setGeometry(new_geometry)
        else:
            # Update cursor based on position
            edge = self.get_resize_edge(event.pos())
            if edge:
                self.setCursor(self.get_cursor_for_edge(edge))
            else:
                self.setCursor(Qt.IBeamCursor)
                super().mouseMoveEvent(event)

    def mousePressEvent(self, event):
        edge = self.get_resize_edge(event.pos())
        if edge:
            self.resizing = True
            self.resize_edge = edge
            self.resize_start_pos = event.globalPos()
            self.resize_start_geometry = self.geometry()
            self.resizeStarted.emit()
        else:
            super().mousePressEvent(event)
            self.focusReceived.emit(self)

    def mouseReleaseEvent(self, event):
        if self.resizing:
            self.resizing = False
            self.resize_edge = None
            self.resize_start_pos = None
            self.resize_start_geometry = None
            self.resizeFinished.emit()
        else:
            super().mouseReleaseEvent(event)

    def focusInEvent(self, event):
        super().focusInEvent(event)
        self.focusReceived.emit(self)
        
    def paintEvent(self, event):
        super().paintEvent(event)
        # Draw resize handles
        if self.hasFocus():
            p = QPainter(self)
            p.setPen(QPen(QColor(0, 120, 215), 1))  # Windows-style blue handles
            rect = self.rect()
            
            # Draw corner handles
            handle_size = self.edge_size
            p.drawRect(0, 0, handle_size, handle_size)  # Top-left
            p.drawRect(rect.right() - handle_size, 0, handle_size, handle_size)  # Top-right
            p.drawRect(0, rect.bottom() - handle_size, handle_size, handle_size)  # Bottom-left
            p.drawRect(rect.right() - handle_size, rect.bottom() - handle_size, handle_size, handle_size)  # Bottom-right

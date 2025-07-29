from PyQt5.QtWidgets import QHBoxLayout, QPushButton, QLabel, QWidget, QStyle
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QImage, QPixmap, QIcon
import fitz

class PDFZoomHandler:
    def __init__(self, parent=None):
        self.parent = parent
        self.zoom_factor = 1.0
        self.min_zoom = 0.25
        self.max_zoom = 5.0
        self.zoom_step = 0.25

        # Create widget to hold zoom controls
        self.zoom_widget = QWidget()
        self.zoom_layout = QHBoxLayout(self.zoom_widget)
        self.zoom_layout.setContentsMargins(0, 0, 0, 0)
        self.zoom_layout.setSpacing(2)
        
        # Create zoom controls with icons
        self.zoom_out_btn = QPushButton()
        self.zoom_out_btn.setIcon(parent.style().standardIcon(QStyle.SP_MediaVolumeMuted))  # Using minus-like icon
        self.zoom_out_btn.setIconSize(QSize(16, 16))
        self.zoom_out_btn.setFixedSize(24, 24)
        
        self.zoom_label = QLabel("100%")
        self.zoom_label.setFixedWidth(50)
        self.zoom_label.setAlignment(Qt.AlignCenter)
        
        self.zoom_in_btn = QPushButton()
        self.zoom_in_btn.setIcon(parent.style().standardIcon(QStyle.SP_MediaVolume))  # Using plus-like icon
        self.zoom_in_btn.setIconSize(QSize(16, 16))
        self.zoom_in_btn.setFixedSize(24, 24)
        
        self.zoom_layout.addWidget(self.zoom_out_btn)
        self.zoom_layout.addWidget(self.zoom_label)
        self.zoom_layout.addWidget(self.zoom_in_btn)

        # Connect button signals
        self.zoom_out_btn.clicked.connect(lambda: self.zoom_pdf(-self.zoom_step))
        self.zoom_in_btn.clicked.connect(lambda: self.zoom_pdf(self.zoom_step))

    def get_layout(self):
        return self.zoom_layout

    def get_widget(self):
        return self.zoom_widget

    def zoom_pdf(self, delta):
        """
        Adjust zoom level by delta amount while maintaining aspect ratio
        """
        # Calculate new zoom factor
        new_zoom = self.zoom_factor + delta
        new_zoom = max(self.min_zoom, min(new_zoom, self.max_zoom))
        
        if new_zoom != self.zoom_factor:
            self.zoom_factor = new_zoom
            self.zoom_label.setText(f"{int(self.zoom_factor * 100)}%")
            
            if self.parent and hasattr(self.parent, 'update_display'):
                self.parent.update_display()

    def handle_wheel_event(self, event):
        """
        Handle mouse wheel events for zooming
        """
        if event.modifiers() == Qt.ControlModifier:
            # Calculate zoom step based on wheel direction
            delta = event.angleDelta().y()
            zoom_delta = self.zoom_step if delta > 0 else -self.zoom_step
            self.zoom_pdf(zoom_delta)
            return True
        return False

    def reset_zoom(self):
        """
        Reset zoom to default value (100%)
        """
        self.zoom_factor = 1.0
        self.zoom_label.setText("100%")

    def get_zoomed_pixmap(self, page):
        """
        Get a zoomed pixmap from a PDF page
        """
        zoom_matrix = fitz.Matrix(self.zoom_factor * 2, self.zoom_factor * 2)  # Base resolution multiplier of 2
        pix = page.get_pixmap(matrix=zoom_matrix)
        img = QImage(pix.samples, pix.width, pix.height, pix.stride, QImage.Format_RGB888)
        return QPixmap.fromImage(img)

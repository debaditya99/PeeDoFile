from PyQt5.QtWidgets import QWidget, QPushButton, QColorDialog, QHBoxLayout, QFrame
from PyQt5.QtGui import QPainter, QPen, QColor, QPalette
from PyQt5.QtCore import Qt, QPoint, QSize
import fitz
import os
import tempfile
import shutil
import time

class ControlFrame(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFrameStyle(QFrame.Panel | QFrame.Raised)
        self.setStyleSheet("""
            QPushButton {
                min-width: 60px;
                padding: 5px;
                background-color: #f0f0f0;
                border: 1px solid #ccc;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #e0e0e0;
            }
        """)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)
        
        self.color_button = QPushButton("Color")
        self.clear_button = QPushButton("Clear")
        
        layout.addWidget(self.color_button)
        layout.addWidget(self.clear_button)
        
        # Set fixed size for the frame
        self.setFixedHeight(50)
        self.adjustSize()

class PDFAnnotator(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.drawing = False
        self.last_point = QPoint()
        self.current_color = QColor(Qt.red)
        self.line_width = 2
        self.annotations = []
        self.pdf_rect = None
        
        # Make the widget transparent
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setup_ui()

    def setup_ui(self):
        # Create control frame with buttons
        self.control_frame = ControlFrame(self)
        
        # Connect button signals
        self.control_frame.color_button.clicked.connect(self.choose_color)
        self.control_frame.clear_button.clicked.connect(self.clear_annotations)
        
        # Update color button background
        self.update_color_button()

    def update_color_button(self):
        self.control_frame.color_button.setStyleSheet(
            f"background-color: {self.current_color.name()}; color: {'white' if sum(self.current_color.getRgb()[:3]) < 380 else 'black'}"
        )

    def resizeEvent(self, event):
        super().resizeEvent(event)
        # Position the control frame in the top-right corner
        frame_width = self.control_frame.sizeHint().width()
        self.control_frame.move(self.width() - frame_width - 10, 10)

    def choose_color(self):
        color = QColorDialog.getColor(self.current_color)
        if color.isValid():
            self.current_color = color
            self.update_color_button()

    def clear_annotations(self):
        self.annotations.clear()
        self.update()

    def set_pdf_rect(self, rect):
        """Set the rectangle that represents the PDF boundaries"""
        self.pdf_rect = rect
        self.update()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton and not self.control_frame.geometry().contains(event.pos()):
            self.drawing = True
            self.last_point = event.pos()

    def mouseMoveEvent(self, event):
        if self.drawing and not self.control_frame.geometry().contains(event.pos()):
            current_point = event.pos()
            self.annotations.append({
                'start': self.last_point,
                'end': current_point,
                'color': self.current_color,
                'width': self.line_width
            })
            self.last_point = current_point
            self.update()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drawing = False

    def paintEvent(self, event):
        if not self.pdf_rect:
            return
            
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Set composition mode for proper overlay
        painter.setCompositionMode(QPainter.CompositionMode_SourceOver)
        
        for annotation in self.annotations:
            pen = QPen(annotation['color'], annotation['width'], Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)
            painter.setPen(pen)
            painter.drawLine(annotation['start'], annotation['end'])

    def normalize_color(self, color):
        """Convert RGB values from 0-255 to 0-1 range"""
        r, g, b, _ = color.getRgb()
        return (r / 255.0, g / 255.0, b / 255.0)

    def save_annotations(self, pdf_path, output_path):
        try:
            if not self.pdf_rect:
                return False

            # Create a temporary file
            temp_fd, temp_path = tempfile.mkstemp(suffix='.pdf')
            os.close(temp_fd)  # Close the file descriptor

            try:
                # Copy original file to temp location first
                shutil.copy2(pdf_path, temp_path)
                
                # Small delay to ensure file operations are complete
                time.sleep(0.1)
                
                # Open the temporary file and modify it
                doc = fitz.open(temp_path)
                page = doc[0]  # Currently working with first page only
                
                # Calculate scaling factors
                scale_x = page.rect.width / self.pdf_rect.width()
                scale_y = page.rect.height / self.pdf_rect.height()
                
                for annotation in self.annotations:
                    # Convert Qt coordinates to PDF coordinates
                    start = annotation['start']
                    end = annotation['end']
                    
                    # Adjust coordinates relative to PDF rectangle
                    start_x = (start.x() - self.pdf_rect.left()) * scale_x
                    start_y = (start.y() - self.pdf_rect.top()) * scale_y
                    end_x = (end.x() - self.pdf_rect.left()) * scale_x
                    end_y = (end.y() - self.pdf_rect.top()) * scale_y
                    
                    # Normalize color values to 0-1 range
                    normalized_color = self.normalize_color(annotation['color'])
                    
                    # Create annotation on PDF
                    page.draw_line(
                        (start_x, start_y),
                        (end_x, end_y),
                        color=normalized_color,
                        width=annotation['width']
                    )
                
                # Save to a second temporary file
                final_temp_fd, final_temp_path = tempfile.mkstemp(suffix='.pdf')
                os.close(final_temp_fd)
                doc.save(final_temp_path)
                doc.close()

                # Small delay to ensure file operations are complete
                time.sleep(0.1)

                # If the output path exists, try to remove it
                try:
                    if os.path.exists(output_path):
                        os.remove(output_path)
                except Exception:
                    time.sleep(0.2)  # Wait a bit longer if file is still locked
                    if os.path.exists(output_path):
                        os.remove(output_path)

                # Move temporary file to final destination
                shutil.move(final_temp_path, output_path)
                
                # Clean up the first temporary file
                if os.path.exists(temp_path):
                    os.remove(temp_path)
                
                return True

            except Exception as e:
                # Clean up temporary files in case of error
                for path in [temp_path, final_temp_path]:
                    if os.path.exists(path):
                        try:
                            os.remove(path)
                        except Exception:
                            pass
                raise e

        except Exception as e:
            print(f"Error saving annotations: {str(e)}")
            return False

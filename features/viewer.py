import sys
import os
from PyQt5.QtWidgets import (QApplication, QMainWindow, QFileDialog, QAction, 
                            QLabel, QVBoxLayout, QWidget, QScrollArea, QMessageBox)
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtCore import Qt, QRect

import fitz  # PyMuPDF
from .annotator import PDFAnnotator

class PDFViewer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PDF Viewer")
        self.setGeometry(100, 100, 800, 600)
        self.current_file_path = None

        # Create central widget
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)

        # Create scroll area
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        
        # Create container widget for PDF and annotator
        self.container = QWidget()
        self.container_layout = QVBoxLayout(self.container)
        self.container_layout.setContentsMargins(0, 0, 0, 0)
        
        # Create the PDF display label
        self.label = QLabel("Open a PDF file to view.")
        self.label.setAlignment(Qt.AlignCenter)
        self.container_layout.addWidget(self.label)
        
        # Create and add annotator widget
        self.annotator = PDFAnnotator(self.container)
        self.annotator.hide()  # Initially hidden
        
        # Set up scroll area
        self.scroll_area.setWidget(self.container)
        self.main_layout.addWidget(self.scroll_area)
        
        # Create menu bar
        self.create_menu_bar()

        # Initialize variables
        self.current_doc = None
        self.annotation_mode = False
        self.pdf_pixmap = None

    def create_menu_bar(self):
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("&File")
        
        open_action = QAction("&Open PDF", self)
        open_action.setShortcut("Ctrl+O")
        open_action.triggered.connect(self.open_pdf)
        file_menu.addAction(open_action)

        save_action = QAction("&Save As...", self)
        save_action.setShortcut("Ctrl+S")
        save_action.triggered.connect(self.save_pdf)
        file_menu.addAction(save_action)

        # Tools menu
        tools_menu = menubar.addMenu("&Tools")
        
        self.toggle_annotate_action = QAction("Toggle &Annotation Mode", self)
        self.toggle_annotate_action.setShortcut("Ctrl+A")
        self.toggle_annotate_action.setCheckable(True)
        self.toggle_annotate_action.triggered.connect(self.toggle_annotation_mode)
        tools_menu.addAction(self.toggle_annotate_action)

    def toggle_annotation_mode(self):
        if not self.current_file_path:
            QMessageBox.warning(self, "Warning", "Please open a PDF file first.")
            self.toggle_annotate_action.setChecked(False)
            return

        self.annotation_mode = not self.annotation_mode
        self.annotator.setVisible(self.annotation_mode)
        
        if self.annotation_mode:
            # Update annotator geometry and set PDF boundaries
            self.update_annotator_geometry()

    def update_annotator_geometry(self):
        if self.pdf_pixmap and self.annotation_mode:
            # Get the geometry of the label with the PDF
            pdf_rect = self.label.geometry()
            # Set the annotator to cover exactly the same area as the PDF
            self.annotator.setGeometry(pdf_rect)
            # Update the PDF boundaries in the annotator
            self.annotator.set_pdf_rect(pdf_rect)
            # Ensure annotator is on top
            self.annotator.raise_()

    def save_pdf_to_path(self, source_path, new_path=None):
        """Save PDF to the specified path or generate a new path with '_modified' suffix"""
        try:
            if not new_path:
                # Get directory of source file
                directory = os.path.dirname(source_path)
                # Get filename without extension
                filename = os.path.splitext(os.path.basename(source_path))[0]
                # Create new filename
                new_path = os.path.join(directory, f"{filename}_modified.pdf")

            # Copy the PDF
            doc = fitz.open(source_path)
            doc.save(new_path)
            doc.close()
            return new_path
        except Exception as e:
            print(f"Error saving PDF: {str(e)}")
            return None

    def save_pdf(self):
        if not self.current_file_path:
            QMessageBox.warning(self, "Warning", "Please open a PDF file first.")
            return

        if self.annotator.annotations:
            # Save with annotations
            file_path, _ = QFileDialog.getSaveFileName(
                self,
                "Save PDF File",
                "",
                "PDF Files (*.pdf)"
            )
            if file_path:
                # Close the current document before saving
                if self.current_doc:
                    self.current_doc.close()
                    self.current_doc = None

                if self.annotator.save_annotations(self.current_file_path, file_path):
                    QMessageBox.information(self, "Success", "PDF saved successfully with annotations!")
                    # If we saved to the current file, reload it
                    if file_path == self.current_file_path:
                        self.display_pdf(file_path)
                    else:
                        # Reopen the original file
                        self.display_pdf(self.current_file_path)
                else:
                    QMessageBox.warning(self, "Error", "Failed to save PDF with annotations.")
                    # Reopen the original file
                    self.display_pdf(self.current_file_path)
        else:
            # Save without annotations
            file_path, _ = QFileDialog.getSaveFileName(
                self,
                "Save PDF File",
                "",
                "PDF Files (*.pdf)"
            )
            if file_path:
                saved_path = self.save_pdf_to_path(self.current_file_path, file_path)
                if saved_path:
                    QMessageBox.information(self, "Success", "PDF saved successfully!")

    def open_pdf(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, 
            "Open PDF File", 
            "", 
            "PDF Files (*.pdf)"
        )
        if file_path:
            self.current_file_path = file_path
            self.display_pdf(file_path)

    def display_pdf(self, file_path):
        try:
            # Close previous document if exists
            if self.current_doc:
                self.current_doc.close()
                self.current_doc = None

            self.current_doc = fitz.open(file_path)
            if self.current_doc.page_count > 0:
                page = self.current_doc.load_page(0)
                pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))  # Zoom factor 2 for better resolution
                
                # Convert PyMuPDF pixmap to Qt image
                img = QImage(pix.samples, pix.width, pix.height, pix.stride, QImage.Format_RGB888)
                self.pdf_pixmap = QPixmap.fromImage(img)
                
                # Update label with new pixmap
                self.label.setPixmap(self.pdf_pixmap)
                self.label.setScaledContents(True)
                
                # Update window title with filename
                self.setWindowTitle(f"PDF Viewer - {file_path}")
                
                # Reset annotator and update its size
                self.annotator.clear_annotations()
                if self.annotation_mode:
                    self.update_annotator_geometry()
                
            else:
                self.label.setText("This PDF file appears to be empty.")
                self.pdf_pixmap = None
        except Exception as e:
            self.label.setText(f"Error loading PDF: {str(e)}")
            self.pdf_pixmap = None
            print(f"Error: {str(e)}")

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.update_annotator_geometry()

    def closeEvent(self, event):
        # Clean up resources when closing
        if self.current_doc:
            self.current_doc.close()
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    viewer = PDFViewer()
    viewer.show()
    sys.exit(app.exec_())
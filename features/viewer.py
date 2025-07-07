from PyQt5.QtWidgets import (QApplication, QMainWindow, QFileDialog, QAction, 
                            QLabel, QVBoxLayout, QWidget, QScrollArea, QMessageBox,
                            QToolBar, QStyle, QColorDialog)
from PyQt5.QtGui import QPixmap, QImage, QIcon
from PyQt5.QtCore import Qt, QRect, QSize
import os
from PyQt5.QtWidgets import (QApplication, QMainWindow, QFileDialog, QAction, 
                            QLabel, QVBoxLayout, QWidget, QScrollArea, QMessageBox,
                            QToolBar, QStyle)
from PyQt5.QtGui import QPixmap, QImage, QIcon, QCursor
from PyQt5.QtCore import Qt, QRect, QSize

import fitz  # PyMuPDF
from .annotator import PDFAnnotator
from .zoom import PDFZoomHandler
from .texteditor import PDFTextEditor
from .recentfiles import RecentFilesManager

class PDFViewer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PDF Viewer")
        self.setGeometry(100, 100, 800, 600)
        self.current_file_path = None
        
        # Initialize recent files manager
        self.recent_files_manager = RecentFilesManager()

        # Initialize variables
        self.current_doc = None
        self.annotation_mode = False
        self.text_mode = False
        self.pdf_pixmap = None

        # Create central widget
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)

        # Initialize zoom handler
        self.zoom_handler = PDFZoomHandler(self)

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
        
        # Initialize text editor
        self.text_editor = PDFTextEditor(self.container)
        self.text_editor.textEditingStarted.connect(self.on_text_editing_started)
        self.text_editor.textEditingFinished.connect(self.on_text_editing_finished)
        self.text_editor.hide()  # Initially hidden
        
        # Create and add annotator widget
        self.annotator = PDFAnnotator(self.container)
        self.annotator.hide()  # Initially hidden
        
        # Set up scroll area
        self.scroll_area.setWidget(self.container)
        self.main_layout.addWidget(self.scroll_area)

        # Install event filter for text editing
        self.container.installEventFilter(self)
        
        # Create menu bar
        self.create_menu_bar()

    def create_menu_bar(self):
        # Create menu bar
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("&File")
        
        # Create actions
        self.open_action = QAction("&Open PDF", self)
        self.open_action.setShortcut("Ctrl+O")
        self.open_action.setIcon(self.style().standardIcon(QStyle.SP_DialogOpenButton))
        self.open_action.triggered.connect(self.open_pdf)
        
        self.save_action = QAction("&Save As...", self)
        self.save_action.setShortcut("Ctrl+S")
        self.save_action.setIcon(self.style().standardIcon(QStyle.SP_DialogSaveButton))
        self.save_action.triggered.connect(self.save_pdf)
        
        # Add actions to File menu
        file_menu.addAction(self.open_action)
        file_menu.addAction(self.save_action)
        
        # Add recent files menu
        self.recent_files_menu = file_menu.addMenu("Recent Files")
        self.update_recent_files_menu()
        
        # Add clear recent files action
        file_menu.addSeparator()
        clear_recent_action = QAction("Clear Recent Files", self)
        clear_recent_action.triggered.connect(self.clear_recent_files)
        file_menu.addAction(clear_recent_action)

        # Create toolbar
        toolbar = QToolBar()
        toolbar.setIconSize(QSize(24, 24))
        self.addToolBar(toolbar)

        # Add file operations to toolbar
        toolbar.addAction(self.open_action)
        toolbar.addAction(self.save_action)
        toolbar.addSeparator()

        # Add annotation tools to toolbar
        self.toggle_annotate_action = QAction("Toggle &Annotation Mode", self)
        self.toggle_annotate_action.setShortcut("Ctrl+A")
        self.toggle_annotate_action.setCheckable(True)
        self.toggle_annotate_action.setIcon(self.style().standardIcon(QStyle.SP_DialogHelpButton))  # Using a pen-like icon
        self.toggle_annotate_action.triggered.connect(self.toggle_annotation_mode)
        toolbar.addAction(self.toggle_annotate_action)
        
        # Add annotation color button to toolbar
        self.color_action = QAction("Color", self)
        self.color_action.setIcon(self.style().standardIcon(QStyle.SP_DialogHelpButton))
        self.color_action.triggered.connect(self.choose_annotation_color)
        toolbar.addAction(self.color_action)
        
        # Add clear annotations action to toolbar
        self.clear_annotations_action = QAction("Clear Annotations", self)
        self.clear_annotations_action.setIcon(self.style().standardIcon(QStyle.SP_DialogResetButton))
        self.clear_annotations_action.triggered.connect(lambda: self.annotator.clear_annotations())
        toolbar.addAction(self.clear_annotations_action)
        toolbar.addSeparator()

        # Add text editor toggle to toolbar
        self.toggle_text_action = QAction("Add Text", self)
        self.toggle_text_action.setCheckable(True)
        self.toggle_text_action.setIcon(self.style().standardIcon(QStyle.SP_FileDialogDetailedView))
        self.toggle_text_action.triggered.connect(self.toggle_text_mode)
        toolbar.addAction(self.toggle_text_action)

        # Add text formatting toolbar (hidden by default)
        self.format_toolbar = self.text_editor.get_toolbar()
        self.format_toolbar.hide()
        toolbar.addSeparator()
        toolbar.addWidget(self.format_toolbar)
        toolbar.addSeparator()

        # Add zoom controls to toolbar
        toolbar.addWidget(self.zoom_handler.get_widget())

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

    def open_pdf(self, file_path=None):
        if not file_path:
            file_path, _ = QFileDialog.getOpenFileName(
                self, 
                "Open PDF File", 
                "", 
                "PDF Files (*.pdf)"
            )
        if file_path and os.path.exists(file_path):
            self.current_file_path = file_path
            self.display_pdf(file_path)
            # Add to recent files
            self.recent_files_manager.add_recent_file(file_path)
            self.update_recent_files_menu()
            
    def display_pdf(self, file_path):
        if self.current_doc:
            self.current_doc.close()
            self.current_doc = None

        try:
            self.current_doc = fitz.open(file_path)
            if self.current_doc.page_count > 0:
                page = self.current_doc.load_page(0)
                
                if hasattr(self, 'zoom_handler'):
                    pixmap = self.zoom_handler.get_zoomed_pixmap(page)
                else:
                    # Default zoom factor 2 for better resolution if zoom handler not available
                    pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))
                    img = QImage(pix.samples, pix.width, pix.height, pix.stride, QImage.Format_RGB888)
                    pixmap = QPixmap.fromImage(img)
                
                self.pdf_pixmap = pixmap
                
                # Update label with new pixmap
                self.label.setPixmap(self.pdf_pixmap)
                self.label.setScaledContents(False)  # Changed to False to prevent stretching
                self.label.setAlignment(Qt.AlignCenter)
                
                # Update window title with filename
                self.setWindowTitle(f"PDF Viewer - {file_path}")
                
                # Reset annotator and update its size
                self.annotator.clear_annotations()
                self.text_editor.clear_text_boxes()
                if self.annotation_mode:
                    self.update_annotator_geometry()
                if self.text_mode:
                    self.update_text_editor_geometry()
                
            else:
                self.label.setText("This PDF file appears to be empty.")
                self.pdf_pixmap = None
        except Exception as e:
            self.label.setText(f"Error loading PDF: {str(e)}")
            self.pdf_pixmap = None
            print(f"Error: {str(e)}")
            if self.current_doc:
                self.current_doc.close()
                self.current_doc = None

    def wheelEvent(self, event):
        if not self.zoom_handler.handle_wheel_event(event):
            # If zoom handler didn't handle it, pass to parent for normal scrolling
            super().wheelEvent(event)

    def toggle_text_mode(self):
        """Toggle text input mode"""
        if not self.current_file_path:
            QMessageBox.warning(self, "Warning", "Please open a PDF file first.")
            self.toggle_text_action.setChecked(False)
            return

        self.text_mode = not self.text_mode
        if self.text_mode:
            # Disable annotation mode if it's active
            if self.annotation_mode:
                self.toggle_annotate_action.setChecked(False)
                self.toggle_annotation_mode()
            self.container.setCursor(Qt.IBeamCursor)
            self.text_editor.show()
            self.update_text_editor_geometry()
        else:
            self.container.setCursor(Qt.ArrowCursor)
            self.format_toolbar.hide()
            self.text_editor.hide()

    def update_text_editor_geometry(self):
        """Update text editor overlay geometry to match PDF"""
        if self.pdf_pixmap and self.text_mode:
            # Get the geometry of the label with the PDF
            pdf_rect = self.label.geometry()
            # Set the text editor to cover exactly the same area as the PDF
            self.text_editor.set_pdf_rect(pdf_rect)
            # Ensure text editor is on top
            self.text_editor.raise_()

    def eventFilter(self, obj, event):
        """Event filter to handle mouse events on the container"""
        if obj == self.container:
            if event.type() == event.MouseButtonPress and self.text_mode and event.button() == Qt.LeftButton:
                # Convert position relative to container
                pos = self.container.mapFromGlobal(event.globalPos())
                if not self.label.geometry().contains(pos):
                    return False
                self.text_editor.create_text_box(pos)
                return True
        return super().eventFilter(obj, event)

    def mousePressEvent(self, event):
        """Handle mouse press events"""
        super().mousePressEvent(event)

    def on_text_editing_started(self):
        """Show text formatting toolbar when text editing starts"""
        self.format_toolbar.show()

    def on_text_editing_finished(self):
        """Hide text formatting toolbar when text editing ends"""
        self.format_toolbar.hide()

    def choose_annotation_color(self):
        """Open color dialog for annotation color selection"""
        color = QColorDialog.getColor(self.annotator.current_color)
        if color.isValid():
            self.annotator.current_color = color
            # Update the color button icon/style if needed
            icon_pixmap = QPixmap(16, 16)
            icon_pixmap.fill(color)
            self.color_action.setIcon(QIcon(icon_pixmap))

    def update_recent_files_menu(self):
        """Update the recent files menu with the latest list of files"""
        self.recent_files_menu.clear()
        recent_files = self.recent_files_manager.get_recent_files()
        
        for file_path in recent_files:
            action = QAction(os.path.basename(file_path), self)
            action.setData(file_path)
            action.setToolTip(file_path)
            action.triggered.connect(lambda checked, path=file_path: self.open_pdf(path))
            self.recent_files_menu.addAction(action)
            
        if not recent_files:
            no_files_action = QAction("No Recent Files", self)
            no_files_action.setEnabled(False)
            self.recent_files_menu.addAction(no_files_action)

    def clear_recent_files(self):
        """Clear the recent files list"""
        self.recent_files_manager.clear_recent_files()
        self.update_recent_files_menu()

    def update_display(self):
        """
        Update the PDF display with current zoom factor
        """
        if not self.current_file_path or not hasattr(self, 'zoom_handler'):
            return

        doc = None
        try:
            doc = fitz.open(self.current_file_path)
            page = doc[0]  # For now, we're only showing the first page
            
            # Get zoomed pixmap from zoom handler
            pixmap = self.zoom_handler.get_zoomed_pixmap(page)
            self.label.setPixmap(pixmap)
            
            # Ensure the label maintains aspect ratio
            self.label.setScaledContents(False)
            self.label.setAlignment(Qt.AlignCenter)
            
            # Update scroll area size
            self.scroll_area.setMinimumSize(1, 1)  # Reset minimum size
            
            # If we have an annotation overlay, update it
            if self.annotation_mode and self.annotator:
                # Get the geometry of the label with the PDF
                pdf_rect = self.label.geometry()
                # Update the annotator size and position
                self.annotator.setGeometry(pdf_rect)
                self.annotator.set_pdf_rect(pdf_rect)
                self.annotator.raise_()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error updating PDF display: {str(e)}")
        finally:
            if doc:
                doc.close()

    def open_file(self, file_path=None):
        # ...existing code...
        if file_path:
            self.current_file_path = file_path
            self.zoom_factor = 1.0  # Reset zoom when opening new file
            self.zoom_label.setText("100%")
            self.update_display()

    def init_ui(self):
        # Create menu bar
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu('File')
        
        # Open action
        open_action = QAction('Open', self)
        open_action.triggered.connect(self.open_file)
        file_menu.addAction(open_action)
        
        # Add Annotate menu
        annotate_menu = menubar.addMenu('Annotate')
        
        # Toggle annotation mode
        toggle_annotation_action = QAction('Toggle Annotation Mode', self)
        toggle_annotation_action.triggered.connect(self.toggle_annotation_mode)
        annotate_menu.addAction(toggle_annotation_action)
        
        # Clear annotations
        clear_annotations_action = QAction('Clear Annotations', self)
        clear_annotations_action.triggered.connect(self.clear_annotations)
        annotate_menu.addAction(clear_annotations_action)
        
        # Save annotated PDF
        save_action = QAction('Save with Annotations', self)
        save_action.triggered.connect(self.save_with_annotations)
        annotate_menu.addAction(save_action)
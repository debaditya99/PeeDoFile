import features.viewer as viewer
import sys

app = viewer.QApplication(sys.argv)  # Create QApplication first
pdf_viewer = viewer.PDFViewer()      # Then create widgets
pdf_viewer.show()
sys.exit(app.exec_())
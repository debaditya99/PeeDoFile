from PyQt5.QtCore import QSettings
import os

class RecentFilesManager:
    def __init__(self, max_files=5):
        self.settings = QSettings('PeeDoFile', 'PDFViewer')
        self.max_files = max_files

    def add_recent_file(self, file_path):
        """Add a file to recent files list"""
        recent_files = self.get_recent_files()
        
        # Remove file_path if it already exists
        if file_path in recent_files:
            recent_files.remove(file_path)
            
        # Add to the beginning of the list
        recent_files.insert(0, file_path)
        
        # Keep only max_files entries
        recent_files = recent_files[:self.max_files]
        
        # Save the list
        self.settings.setValue('recentFiles', recent_files)

    def get_recent_files(self):
        """Get list of recent files"""
        files = self.settings.value('recentFiles', [])
        # Filter out files that no longer exist
        return [f for f in files if os.path.exists(f)] if files else []

    def clear_recent_files(self):
        """Clear the recent files list"""
        self.settings.setValue('recentFiles', [])

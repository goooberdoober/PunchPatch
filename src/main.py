from PyQt5.QtWidgets import QMainWindow, QApplication, QFileDialog, QPushButton, QTextEdit, QVBoxLayout, QHBoxLayout, QFileSystemModel, QTreeView, QSplashScreen, QGraphicsOpacityEffect, QMessageBox, QWidget, QLineEdit
from PyQt5.QtCore import Qt, QTimer, QPropertyAnimation, pyqtProperty, QModelIndex
from PyQt5.QtGui import QPalette, QColor, QPixmap, QIcon
import sys
import mimetypes
import os

class FadeSplashScreen(QSplashScreen):
    def __init__(self, pixmap):
        super().__init__(pixmap)
        self.opacity_effect = QGraphicsOpacityEffect()
        self.setGraphicsEffect(self.opacity_effect)
        self._opacity = 0
        self.opacity_effect.setOpacity(self._opacity)

    @pyqtProperty(float)
    def opacity(self):
        return self._opacity

    @opacity.setter
    def opacity(self, value):
        self._opacity = value
        self.opacity_effect.setOpacity(self._opacity)

    def fade_in(self, duration=1000):
        self.animation = QPropertyAnimation(self, b"opacity")
        self.animation.setDuration(duration)
        self.animation.setStartValue(0)
        self.animation.setEndValue(1)
        self.animation.start()

    def fade_out(self, duration=1000):
        self.animation = QPropertyAnimation(self, b"opacity")
        self.animation.setDuration(duration)
        self.animation.setStartValue(1)
        self.animation.setEndValue(0)
        self.animation.finished.connect(self.close)
        self.animation.start()


class PunchPatchApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Punch Patch")
        self.setGeometry(300, 300, 800, 600)

        # Set background color and palette (dark gradient)
        palette = QPalette()
        palette.setColor(QPalette.Background, QColor(40, 40, 50))  # Dark background
        self.setPalette(palette)

        # Set window icon
        self.setWindowIcon(QIcon('assets/logo.png'))

        # Directory and file viewer model
        self.model = QFileSystemModel()
        self.model.setRootPath("")  # Set to empty to start at system root

        # Directory viewer as a tree view
        self.tree = QTreeView()
        self.tree.setModel(self.model)
        self.tree.setRootIndex(self.model.index(""))  # Start at system root
        self.tree.clicked.connect(self.open_selected_file)

        # Make sure the column is wide enough to display file/folder names
        self.tree.resizeColumnToContents(0)  # Resize the first column (file names)
        self.tree.setColumnWidth(0, 250)  # Set a minimum width for the file column if necessary
        self.tree.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)

        # Directory path input field for pasting paths
        self.directory_paste = QLineEdit()
        self.directory_paste.setPlaceholderText("Paste directory path here...")
        self.directory_paste.setStyleSheet("background-color: white; font-size: 14px;")
        self.directory_paste.returnPressed.connect(self.change_directory)

        # Main layout with directory viewer and editor
        main_layout = QHBoxLayout()

        # Left panel: directory viewer
        main_layout.addWidget(self.tree)

        # Right panel: file editor and buttons
        right_panel = QVBoxLayout()

        # Decompile button
        self.decompile_button = QPushButton("Decompile Assets")
        self.decompile_button.setStyleSheet("background-color: #2d98f0; color: white; font-weight: bold;")
        self.decompile_button.clicked.connect(self.decompile_assets)
        right_panel.addWidget(self.decompile_button)

        # Open button for opening files
        self.open_button = QPushButton("Open Game Asset")
        self.open_button.setStyleSheet("background-color: #2d98f0; color: white; font-weight: bold;")
        self.open_button.clicked.connect(self.open_file)
        right_panel.addWidget(self.open_button)

        # Text area for editing files
        self.text_edit = QTextEdit()
        self.text_edit.setStyleSheet("background-color: #333333; color: white; font-size: 14px;")
        right_panel.addWidget(self.text_edit)

        # Save button for saving changes
        self.save_button = QPushButton("Save Changes")
        self.save_button.setStyleSheet("background-color: #2d98f0; color: white; font-weight: bold;")
        self.save_button.clicked.connect(self.save_file)
        right_panel.addWidget(self.save_button)

        # Add directory paste and right panel to main layout
        right_panel.addWidget(self.directory_paste)
        main_layout.addLayout(right_panel)

        # Add right panel to main layout
        main_layout.addLayout(right_panel)

        # Central widget setup
        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

    def open_selected_file(self, index: QModelIndex):
        """Open file from directory viewer when clicked."""
        file_path = self.model.filePath(index)
        mime_type, _ = mimetypes.guess_type(file_path)

        # If it's a text file, open it in the editor
        if mime_type and mime_type.startswith("text"):
            try:
                with open(file_path, 'r') as file:
                    content = file.read()
                    self.text_edit.setText(content)
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Could not open file: {e}")
        else:
            # Show error message for unsupported file types
            QMessageBox.warning(self, "Unsupported File Type", "This file type is not supported for editing.")

    def open_file(self):
        """Open file from a file dialog and display content."""
        file_path, _ = QFileDialog.getOpenFileName(self, "Open File", "", "All Files (*.*)")
        if file_path:
            mime_type, _ = mimetypes.guess_type(file_path)

            try:
                # If it's a text file
                if mime_type and mime_type.startswith("text"):
                    with open(file_path, 'r') as file:
                        content = file.read()
                        self.text_edit.setText(content)
                else:
                    # Show error message for unsupported binary files
                    QMessageBox.warning(self, "Unsupported File Type", "This file type is not supported for editing.")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"An error occurred: {e}")

    def save_file(self):
        """Save changes to a new file from the text editor."""
        file_path, _ = QFileDialog.getSaveFileName(self, "Save File", "", "All Files (*.*)")
        if file_path:
            with open(file_path, 'w') as file:
                content = self.text_edit.toPlainText()
                file.write(content)

    def decompile_assets(self):
        """Placeholder for decompile function."""
        QMessageBox.information(self, "Decompile", "Decompile Assets functionality will go here.")

    def recompile_assets(self):
        """Placeholder for recompile function."""
        QMessageBox.information(self, "Recompile", "Recompile Assets functionality will go here.")

    def change_directory(self):
        """Change the directory in the tree view based on the pasted path."""
        path = self.directory_paste.text().strip()
        if os.path.exists(path) and os.path.isdir(path):
            self.model.setRootPath(path)
            self.tree.setRootIndex(self.model.index(path))  # Update the tree view with the new directory
        else:
            QMessageBox.warning(self, "Invalid Path", "The directory path you pasted is invalid.")


if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Load the splash screen with fade-in effect
    splash_pixmap = QPixmap("assets/logo.png")  # Replace with your logo path
    splash = FadeSplashScreen(splash_pixmap)
    splash.show()
    splash.fade_in(duration=500)  # Fade in over 1.5 seconds

    # Delay to keep the splash screen visible
    QTimer.singleShot(3000, lambda: splash.fade_out(duration=200))  # Fade out over 1.5 seconds after 3 seconds

    # Initialize the main window after splash screen closes
    window = PunchPatchApp()

    # Show the main window after splash screen is fully faded out
    QTimer.singleShot(4500, window.show)  # Adjust based on fade-out timing

    sys.exit(app.exec_())

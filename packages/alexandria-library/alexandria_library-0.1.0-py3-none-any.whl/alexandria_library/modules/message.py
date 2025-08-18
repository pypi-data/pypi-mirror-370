from PyQt5.QtWidgets import QDialog, QVBoxLayout, QTextEdit, QScrollArea, QPushButton, QApplication, QHBoxLayout
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon

class MessageDialog(QDialog):
    """Display a message with copyable text and configurable buttons"""
    def __init__(self, message, width=600, height=300, parent=None, read_only=False, ok_label='OK', title="Message", show_close_button=False):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.resize(width, height)
        
        # Create layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Create text view for displaying the message
        self.text_edit = QTextEdit()
        self.text_edit.setPlainText(message)
        self.text_edit.setReadOnly(read_only)
        self.text_edit.setLineWrapMode(QTextEdit.WidgetWidth)
        
        # Add text view to a scroll area
        scroll_area = QScrollArea()
        scroll_area.setWidget(self.text_edit)
        scroll_area.setWidgetResizable(True)
        layout.addWidget(scroll_area)
        
        # Create a horizontal layout for buttons
        button_layout = QHBoxLayout()
        
        # Copy to clipboard Button
        copy_button = QPushButton("Copy to clipboard")
        copy_button.setIcon(QIcon.fromTheme("edit-copy"))
        copy_button.clicked.connect(self.copy_to_clipboard)
        button_layout.addWidget(copy_button)
        
        # OK Button
        ok_button = QPushButton(ok_label)
        ok_button.setIcon(QIcon.fromTheme("emblem-default"))
        ok_button.clicked.connect(self.accept)
        button_layout.addWidget(ok_button)
        
        # Close Button (optional)
        if show_close_button:
            close_button = QPushButton("Close")
            close_button.setIcon(QIcon.fromTheme("window-close"))
            close_button.clicked.connect(self.reject)
            button_layout.addWidget(close_button)
        
        # Add button layout to main layout
        layout.addLayout(button_layout)
    
    def copy_to_clipboard(self):
        """Copy the text from the text edit to clipboard"""
        clipboard = QApplication.clipboard()
        clipboard.setText(self.text_edit.toPlainText())

def show_message(   message, 
                    width=600, 
                    height=300, 
                    read_only=False, 
                    ok_label='OK', 
                    title="Message", 
                    show_close_button=False):
    dialog = MessageDialog( message, 
                            width, 
                            height, 
                            read_only=read_only, 
                            ok_label=ok_label, 
                            title=title, 
                            show_close_button=show_close_button)
    result = dialog.exec_()
    
    # If Close button is pressed (rejected), return empty string
    # If OK button is pressed (accepted), return the text
    if result == QDialog.Rejected:
        return ""
    return dialog.text_edit.toPlainText()

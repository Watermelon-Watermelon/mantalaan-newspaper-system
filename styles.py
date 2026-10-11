# Path: styles.py
# Centralized application stylesheets and global fixes

GLOBAL_FIX_STYLESHEET = """
/* Standard Buttons Fix across all Dialogs & Popups */
QDialog QPushButton, 
QMessageBox QPushButton {
    background-color: #0b2545 !important;
    color: #ffffff !important;
    border: none !important;
    border-radius: 4px !important;
    padding: 6px 18px !important;
    font-weight: bold !important;
    font-size: 12px !important;
    min-width: 65px !important;
    min-height: 24px !important;
}

QDialog QPushButton:hover, 
QMessageBox QPushButton:hover {
    background-color: #1a5b9e !important;
}

QDialog QPushButton:pressed, 
QMessageBox QPushButton:pressed {
    background-color: #05162d !important;
}

/* Fix QMessageBox Container & Label */
QMessageBox {
    background-color: #ffffff !important;
}

QMessageBox QLabel {
    color: #2c3e50 !important;
    font-size: 13px !important;
    background-color: transparent !important;
}

/* Global Form Input and Combo Box Fixes */
QLineEdit, QComboBox, QTextEdit {
    border: 1px solid #dcdfe6; 
    border-radius: 5px; 
    padding: 8px; 
    background-color: #ffffff; 
    color: #2c3e50; 
    font-size: 12px;
}
QLineEdit:focus, QComboBox:focus, QTextEdit:focus { 
    border: 1.5px solid #0b3c5d; 
}

/* Fix QComboBox Popup Menu Items Text & Background Color */
QComboBox QAbstractItemView {
    color: #2c3e50;
    background-color: #ffffff;
    selection-background-color: #0b3c5d;
    selection-color: #ffffff;
    border: 1px solid #dcdfe6;
    outline: none;
}

/* Global Table Styling Fixes */
QTableWidget {
    background-color: #ffffff;
    color: #2c3e50;
    gridline-color: #e2e8f0;
}

QHeaderView::section {
    background-color: #f1f5f9;
    color: #1e293b;
    font-weight: bold;
    padding: 6px;
    border: 1px solid #e2e8f0;
}

QTableWidget::item {
    color: #2c3e50;
}
"""

FORM_INPUT_STYLE = """
QLineEdit, QComboBox, QTextEdit {
    border: 1px solid #dcdfe6; 
    border-radius: 5px; 
    padding: 8px; 
    background-color: #ffffff; 
    color: #2c3e50; 
    font-size: 12px;
}
QLineEdit:focus, QComboBox:focus, QTextEdit:focus { 
    border: 1.5px solid #0b3c5d; 
}

QComboBox QAbstractItemView {
    color: #2c3e50;
    background-color: #ffffff;
    selection-background-color: #0b3c5d;
    selection-color: #ffffff;
    border: 1px solid #dcdfe6;
    outline: none;
}
"""
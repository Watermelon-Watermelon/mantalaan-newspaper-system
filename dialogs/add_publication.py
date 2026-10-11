# Path: dialogs/add_publication.py
import re
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QTextEdit, QComboBox, QPushButton, QMessageBox, QDateEdit, QSpinBox
)
from PyQt6.QtCore import Qt, QDate
from PyQt6.QtGui import QFont

from db import get_clients_for_combo, add_publication_to_db, update_publication_in_db, get_connection

class AddPublicationDialog(QDialog):
    def __init__(self, parent=None, pub_data=None):
        super().__init__(parent)
        self.pub_data = pub_data
        self.is_edit_mode = pub_data is not None
        self.clients_list = []
        self.init_ui()

    def init_ui(self):
        title_text = "Edit Publication" if self.is_edit_mode else "Add New Publication"
        self.setWindowTitle(title_text)
        self.setFixedWidth(650)

        self.setStyleSheet("""
            QDialog {
                background-color: #ffffff;
            }
            QLabel {
                color: #0b2545 !important;
                font-weight: bold;
                font-size: 13px;
                background-color: transparent;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(14)
        layout.setContentsMargins(20, 20, 20, 20)

        title = QLabel(title_text)
        title.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        title.setStyleSheet("color: #0b2545; margin-bottom: 5px;")
        layout.addWidget(title)

        input_style = """
            QLineEdit, QComboBox, QDateEdit, QSpinBox, QTextEdit { 
                padding: 8px; 
                border: 1px solid #dcdfe6; 
                border-radius: 4px; 
                color: #2c3e50 !important; 
                background-color: #ffffff;
                font-size: 13px;
            }
            QLineEdit::placeholder, QTextEdit::placeholder {
                color: #8c98a4;
            }
            QComboBox QAbstractItemView {
                background-color: #ffffff;
                color: #2c3e50;
                selection-background-color: #e8f4f8;
                selection-color: #0b2545;
            }
            QCalendarWidget QWidget {
                background-color: #ffffff;
                color: #2c3e50;
            }
            QCalendarWidget QWidget#qt_calendar_navigationbar {
                background-color: #f4f6f9;
            }
            QCalendarWidget QToolButton {
                color: #2c3e50;
                background-color: transparent;
                font-weight: bold;
            }
            QCalendarWidget QToolButton:hover {
                background-color: #dcdfe6;
                border-radius: 3px;
            }
            QCalendarWidget QAbstractItemView:enabled {
                color: #2c3e50;
                selection-background-color: #0b2545;
                selection-color: #ffffff;
            }
            QCalendarWidget QSpinBox {
                color: #2c3e50;
                background-color: #ffffff;
            }
            QCalendarWidget QMenu {
                background-color: #ffffff;
                color: #2c3e50;
            }
        """

        form_layout = QHBoxLayout()
        form_layout.setSpacing(20)

        left_col = QVBoxLayout()
        left_col.setSpacing(10)

        right_col = QVBoxLayout()
        right_col.setSpacing(10)

        left_col.addWidget(QLabel("Client *"))
        self.client_combo = QComboBox()
        self.client_combo.setStyleSheet(input_style)
        self.load_clients()
        left_col.addWidget(self.client_combo)

        left_col.addWidget(QLabel("Case Number *"))
        self.case_input = QLineEdit()
        self.case_input.setPlaceholderText("Enter case number (letters, numbers, . - _ ,)")
        self.case_input.setStyleSheet(input_style)
        left_col.addWidget(self.case_input)

        left_col.addWidget(QLabel("Publication Type *"))
        self.type_combo = QComboBox()
        self.type_combo.addItems([
            "Select type",
            "Extrajudicial Settlement", 
            "Court Order", 
            "Obituary", 
            "Ordinance", 
            "LCR Notice / Change of Name", 
            "Foreclosure", 
            "Other Legal Notice"
        ])
        self.type_combo.setStyleSheet(input_style)
        left_col.addWidget(self.type_combo)

        left_col.addWidget(QLabel("Date Received *"))
        self.date_input = QDateEdit()
        self.date_input.setCalendarPopup(True)
        self.date_input.setDate(QDate.currentDate())
        self.date_input.setStyleSheet(input_style)
        
        calendar = self.date_input.calendarWidget()
        calendar.setNavigationBarVisible(True)
        left_col.addWidget(self.date_input)

        right_col.addWidget(QLabel("Required Issues *"))
        self.issues_spin = QSpinBox()
        self.issues_spin.setRange(1, 52)
        self.issues_spin.setValue(3)
        self.issues_spin.setStyleSheet(input_style)
        right_col.addWidget(self.issues_spin)

        right_col.addWidget(QLabel("Legal Description / Details"))
        self.details_input = QTextEdit()
        self.details_input.setPlaceholderText("Enter details...")
        self.details_input.setMaximumHeight(75)
        self.details_input.setStyleSheet(input_style)
        right_col.addWidget(self.details_input)

        right_col.addWidget(QLabel("Notes"))
        self.notes_input = QTextEdit()
        self.notes_input.setPlaceholderText("Add notes (optional)")
        self.notes_input.setMaximumHeight(65)
        self.notes_input.setStyleSheet(input_style)
        right_col.addWidget(self.notes_input)

        if self.is_edit_mode:
            right_col.addWidget(QLabel("Status"))
            self.status_combo = QComboBox()
            self.status_combo.addItems(["In Progress", "Scheduled", "Completed", "Cancelled"])
            self.status_combo.setStyleSheet(input_style)
            right_col.addWidget(self.status_combo)

        form_layout.addLayout(left_col, 1)
        form_layout.addLayout(right_col, 1)
        layout.addLayout(form_layout)

        if self.is_edit_mode:
            curr_client_id = self.pub_data.get("client_id")
            for idx, c in enumerate(self.clients_list):
                if c["client_id"] == curr_client_id:
                    self.client_combo.setCurrentIndex(idx + 1)
                    break

            self.case_input.setText(self.pub_data.get("case_number", ""))
            
            pub_type = self.pub_data.get("publication_type", "")
            type_idx = self.type_combo.findText(pub_type)
            if type_idx >= 0:
                self.type_combo.setCurrentIndex(type_idx)

            d_str = str(self.pub_data.get("date_received", ""))
            if d_str:
                parsed_date = QDate.fromString(d_str, "yyyy-MM-dd")
                if parsed_date.isValid():
                    self.date_input.setDate(parsed_date)

            self.issues_spin.setValue(self.pub_data.get("required_issues", 3))
            self.details_input.setText(self.pub_data.get("legal_description", ""))
            self.notes_input.setText(self.pub_data.get("notes", ""))

            status_val = self.pub_data.get("status", "In Progress")
            status_idx = self.status_combo.findText(status_val)
            if status_idx >= 0:
                self.status_combo.setCurrentIndex(status_idx)

        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        cancel_btn = QPushButton("Cancel")
        cancel_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        cancel_btn.setStyleSheet("""
            QPushButton {
                padding: 8px 18px; 
                border: 1px solid #dcdfe6; 
                border-radius: 4px; 
                color: #2c3e50;
                background-color: #f8f9fa;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #e9ecef;
            }
        """)
        cancel_btn.clicked.connect(self.reject)

        save_btn = QPushButton
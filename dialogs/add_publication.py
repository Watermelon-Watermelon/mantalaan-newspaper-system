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

        save_btn = QPushButton("Update Publication" if self.is_edit_mode else "Save Publication")
        save_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        save_btn.setStyleSheet("""
            QPushButton {
                padding: 8px 18px; 
                background-color: #0b2545; 
                color: white; 
                border-radius: 4px; 
                border: none;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #134e75;
            }
        """)
        save_btn.clicked.connect(self.handle_save)

        btn_layout.addWidget(cancel_btn)
        btn_layout.addWidget(save_btn)
        layout.addLayout(btn_layout)

    def load_clients(self):
        raw_clients = get_clients_for_combo()
        self.clients_list = [
            c for c in raw_clients 
            if str(c.get("status", "Active")).lower() != "inactive"
        ]
        
        self.client_combo.clear()
        self.client_combo.addItem("Select client", None)
        
        for c in self.clients_list:
            self.client_combo.addItem(c["client_name"], c["client_id"])

    def handle_save(self):
        if self.client_combo.currentIndex() <= 0 or self.client_combo.currentData() is None:
            QMessageBox.warning(self, "Input Error", "Please select a valid client.")
            return

        client_id = self.client_combo.currentData()
        case_no = self.case_input.text().strip()
        pub_type = self.type_combo.currentText()
        date_rec = self.date_input.date().toString("yyyy-MM-dd")
        req_issues = self.issues_spin.value()
        details = self.details_input.toPlainText().strip()
        notes = self.notes_input.toPlainText().strip()

        if not case_no:
            QMessageBox.warning(self, "Input Error", "Case number is required.")
            return

        if not re.match(r'^[a-zA-Z0-9\.\-\_\,\s]+$', case_no):
            QMessageBox.warning(
                self, 
                "Invalid Input", 
                "Case Number can only contain letters, numbers, spaces, and the following special characters: . - _ ,"
            )
            return

        if pub_type == "Select type" or not pub_type:
            QMessageBox.warning(self, "Input Error", "Please select a valid publication type.")
            return

        # Duplicate case number check
        conn = get_connection()
        if not conn:
            QMessageBox.critical(self, "Database Error", "Failed to connect to the database.")
            return

        cursor = None
        try:
            cursor = conn.cursor()
            if self.is_edit_mode:
                pub_id = self.pub_data.get("publication_id")
                dup_query = """
                    SELECT COUNT(*) as cnt FROM publication 
                    WHERE LOWER(case_number) = LOWER(%s) AND publication_id != %s
                """
                cursor.execute(dup_query, (case_no, pub_id))
            else:
                dup_query = """
                    SELECT COUNT(*) as cnt FROM publication 
                    WHERE LOWER(case_number) = LOWER(%s)
                """
                cursor.execute(dup_query, (case_no,))
            
            result = cursor.fetchone()
            count = int(list(result.values())[0]) if isinstance(result, dict) else int(result[0])

            if count > 0:
                QMessageBox.warning(
                    self, 
                    "Duplicate Case Number", 
                    "A publication with this case number already exists."
                )
                return
        except Exception as e:
            QMessageBox.critical(self, "Database Error", f"Error verifying case number: {e}")
            return
        finally:
            if cursor:
                cursor.close()
            if conn and conn.open:
                conn.close()

        if self.is_edit_mode:
            pub_id = self.pub_data.get("publication_id")
            status = self.status_combo.currentText()
            success = update_publication_in_db(pub_id, client_id, case_no, pub_type, date_rec, req_issues, details, notes, status)
        else:
            success = add_publication_to_db(client_id, case_no, pub_type, date_rec, req_issues, details, notes, "In Progress")

        if success:
            self.accept()
        else:
            QMessageBox.critical(self, "Database Error", "Failed to save publication details.")
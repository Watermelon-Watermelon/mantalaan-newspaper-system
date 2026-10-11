# Path: dialogs/add_client.py
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QComboBox, QPushButton, QMessageBox, QScrollArea, QWidget
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

from db import get_connection

class AddClientDialog(QDialog):
    def __init__(self, parent=None, client_data=None):
        super().__init__(parent)
        self.client_data = client_data
        self.is_edit_mode = client_data is not None
        
        self.setWindowTitle("Edit Client" if self.is_edit_mode else "Add New Client")
        self.setFixedSize(450, 520)
        self.setStyleSheet("background-color: #ffffff;")
        
        self.init_ui()
        if self.is_edit_mode:
            self.populate_fields()

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")
        
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(25, 25, 25, 25)
        layout.setSpacing(12)

        title_label = QLabel("Edit Client Details" if self.is_edit_mode else "Add New Client")
        title_label.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        title_label.setStyleSheet("color: #2c3e50; margin-bottom: 5px;")
        layout.addWidget(title_label)

        def create_label(text, required=False):
            lbl = QLabel(text + (" *" if required else ""))
            lbl.setFont(QFont("Arial", 9, QFont.Weight.Bold))
            lbl.setStyleSheet("color: #2c3e50;")
            return lbl

        input_style = """
            QLineEdit, QComboBox {
                padding: 9px 12px;
                border: 1px solid #dcdfe6;
                border-radius: 5px;
                background-color: #ffffff;
                color: #2c3e50;
                font-size: 13px;
            }
            QLineEdit:focus, QComboBox:focus {
                border: 1px solid #0b2545;
            }
        """

        layout.addWidget(create_label("Client Name", required=True))
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Enter full name")
        self.name_input.setStyleSheet(input_style)
        layout.addWidget(self.name_input)

        layout.addWidget(create_label("Contact Number", required=True))
        self.contact_input = QLineEdit()
        self.contact_input.setPlaceholderText("Enter contact number")
        self.contact_input.setStyleSheet(input_style)
        layout.addWidget(self.contact_input)

        layout.addWidget(create_label("Email"))
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("Enter email address")
        self.email_input.setStyleSheet(input_style)
        layout.addWidget(self.email_input)

        layout.addWidget(create_label("Address"))
        self.address_input = QLineEdit()
        self.address_input.setPlaceholderText("Enter complete address")
        self.address_input.setStyleSheet(input_style)
        layout.addWidget(self.address_input)

        layout.addWidget(create_label("Status"))
        self.status_combo = QComboBox()
        self.status_combo.addItems(["Active", "Completed", "Inactive"])
        self.status_combo.setStyleSheet(input_style)
        layout.addWidget(self.status_combo)

        scroll.setWidget(container)
        main_layout.addWidget(scroll)

        btn_layout = QHBoxLayout()
        btn_layout.setContentsMargins(25, 10, 25, 20)
        btn_layout.setSpacing(10)

        cancel_btn = QPushButton("Cancel")
        cancel_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        cancel_btn.setStyleSheet("""
            QPushButton { background-color: #f3f4f6; color: #4b5563; border-radius: 5px; padding: 10px; border: 1px solid #dcdfe6; font-weight: bold; }
            QPushButton:hover { background-color: #e5e7eb; }
        """)
        cancel_btn.clicked.connect(self.reject)

        save_btn = QPushButton("Save Client")
        save_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        save_btn.setStyleSheet("""
            QPushButton { background-color: #0b2545; color: white; border-radius: 5px; padding: 10px; font-weight: bold; border: none; }
            QPushButton:hover { background-color: #134e75; }
        """)
        save_btn.clicked.connect(self.save_client)

        btn_layout.addWidget(cancel_btn)
        btn_layout.addWidget(save_btn)
        main_layout.addLayout(btn_layout)

    def populate_fields(self):
        if not self.client_data:
            return
        self.name_input.setText(str(self.client_data.get("client_name", "")))
        self.contact_input.setText(str(self.client_data.get("contact_number", "")))
        self.email_input.setText(str(self.client_data.get("email", "")))
        self.address_input.setText(str(self.client_data.get("address", "")))
        
        status = str(self.client_data.get("status", "Active"))
        index = self.status_combo.findText(status)
        if index >= 0:
            self.status_combo.setCurrentIndex(index)

    def save_client(self):
        name = self.name_input.text().strip()
        contact = self.contact_input.text().strip()
        email = self.email_input.text().strip()
        address = self.address_input.text().strip()
        status = self.status_combo.currentText()

        if not name or not contact:
            QMessageBox.warning(self, "Validation Error", "Client Name and Contact Number are required fields.")
            return

        conn = get_connection()
        if not conn:
            QMessageBox.critical(self, "Database Error", "Failed to connect to the database.")
            return

        cursor = None
        try:
            cursor = conn.cursor()
            
            # Check for duplicate client (case-insensitive name or matching contact)
            if self.is_edit_mode:
                client_id = self.client_data.get("client_id")
                dup_query = """
                    SELECT COUNT(*) as cnt FROM client 
                    WHERE (LOWER(client_name) = LOWER(%s) OR contact_number = %s) AND client_id != %s
                """
                cursor.execute(dup_query, (name, contact, client_id))
            else:
                dup_query = """
                    SELECT COUNT(*) as cnt FROM client 
                    WHERE LOWER(client_name) = LOWER(%s) OR contact_number = %s
                """
                cursor.execute(dup_query, (name, contact))
            
            result = cursor.fetchone()
            
            count = 0
            if result:
                if isinstance(result, dict):
                    count = int(list(result.values())[0])
                elif isinstance(result, (list, tuple)):
                    count = int(result[0])

            if count > 0:
                QMessageBox.warning(
                    self, 
                    "Duplicate Client", 
                    "Duplicate client! A client with this name or contact number already exists."
                )
                return

            if self.is_edit_mode:
                query = """
                    UPDATE client 
                    SET client_name = %s, contact_number = %s, email = %s, address = %s, status = %s
                    WHERE client_id = %s
                """
                cursor.execute(query, (name, contact, email, address, status, client_id))
            else:
                query = """
                    INSERT INTO client (client_name, contact_number, email, address, status)
                    VALUES (%s, %s, %s, %s, %s)
                """
                cursor.execute(query, (name, contact, email, address, status))
            
            conn.commit()
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Database Error", f"An error occurred while saving: {e}")
        finally:
            if cursor:
                cursor.close()
            if conn and conn.open:
                conn.close()
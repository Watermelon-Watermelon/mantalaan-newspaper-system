# Path: views/profile_view.py
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QPushButton, QFrame, QTabWidget, QFormLayout, QMessageBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
import db  # Your database connection module


class ProfileView(QWidget):
    def __init__(self, current_user):
        super().__init__()
        self.current_user = current_user
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(25, 25, 25, 25)
        layout.setSpacing(20)

        # --- Top Header ---
        title = QLabel("My Profile")
        title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        title.setStyleSheet("color: #0b2545;")
        layout.addWidget(title)

        # --- User Header Card ---
        user_card = QFrame()
        user_card.setStyleSheet("QFrame { background-color: white; border-radius: 8px; border: 1px solid #e0e0e0; }")
        user_card_layout = QHBoxLayout(user_card)
        user_card_layout.setContentsMargins(20, 20, 20, 20)
        user_card_layout.setSpacing(15)

        # Circle Avatar Placeholder
        avatar = QLabel("👤")
        avatar.setFont(QFont("Arial", 28))
        avatar.setAlignment(Qt.AlignmentFlag.AlignCenter)
        avatar.setFixedSize(60, 60)
        avatar.setStyleSheet("""
            QLabel {
                background-color: #0b2545;
                color: white;
                border-radius: 30px;
            }
        """)

        # User Name & Role Label
        user_info_box = QVBoxLayout()
        user_info_box.setSpacing(2)

        self.header_name_label = QLabel(self.current_user.get("full_name", "User Name"))
        self.header_name_label.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        self.header_name_label.setStyleSheet("color: #0b2545;")

        role_label = QLabel(self.current_user.get("role_name", "Office-in-Charge"))
        role_label.setFont(QFont("Arial", 10))
        role_label.setStyleSheet("color: #7f8c8d;")

        user_info_box.addWidget(self.header_name_label)
        user_info_box.addWidget(role_label)

        user_card_layout.addWidget(avatar)
        user_card_layout.addLayout(user_info_box)
        user_card_layout.addStretch()

        layout.addWidget(user_card)

        # --- Main Tab Container ---
        tab_widget = QTabWidget()
        tab_widget.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #e0e0e0;
                background: white;
                border-radius: 8px;
                top: -1px;
            }
            QTabBar::tab {
                background: #f4f6f9;
                color: #2c3e50;
                padding: 10px 20px;
                font-weight: bold;
                border: 1px solid #e0e0e0;
                border-bottom: none;
                border-top-left-radius: 6px;
                border-top-right-radius: 6px;
                margin-right: 4px;
            }
            QTabBar::tab:selected {
                background: white;
                color: #0b2545;
                border-bottom: 2px solid #0b2545;
            }
        """)

        # Tab 1: Account Information
        account_tab = QWidget()
        account_layout = QVBoxLayout(account_tab)
        account_layout.setContentsMargins(25, 25, 25, 25)

        form_layout = QFormLayout()
        form_layout.setSpacing(15)
        form_layout.setLabelAlignment(Qt.AlignmentFlag.AlignLeft)

        input_style = """
            QLineEdit {
                padding: 8px 12px;
                border: 1px solid #dcdfe6;
                border-radius: 6px;
                background-color: white;
                font-size: 13px;
                min-width: 300px;
            }
            QLineEdit:focus { border: 1px solid #1a5b9e; }
            QLineEdit:disabled { background-color: #f8f9fa; color: #7f8c8d; }
        """

        self.full_name_input = QLineEdit(self.current_user.get("full_name", ""))
        self.full_name_input.setStyleSheet(input_style)

        self.username_input = QLineEdit(self.current_user.get("username", ""))
        self.username_input.setStyleSheet(input_style)

        self.email_input = QLineEdit(self.current_user.get("email", ""))
        self.email_input.setStyleSheet(input_style)

        self.role_input = QLineEdit(self.current_user.get("role_name", "Office-in-Charge"))
        self.role_input.setStyleSheet(input_style)
        self.role_input.setEnabled(False)

        def make_label(text):
            lbl = QLabel(text)
            lbl.setFont(QFont("Arial", 9, QFont.Weight.Bold))
            lbl.setStyleSheet("color: #2c3e50;")
            return lbl

        form_layout.addRow(make_label("Full Name"), self.full_name_input)
        form_layout.addRow(make_label("Username"), self.username_input)
        form_layout.addRow(make_label("Email Address"), self.email_input)
        form_layout.addRow(make_label("Role"), self.role_input)

        account_layout.addLayout(form_layout)
        account_layout.addSpacing(15)

        update_btn_layout = QHBoxLayout()
        update_btn_layout.addStretch()

        update_profile_btn = QPushButton("Update Profile")
        update_profile_btn.setFont(QFont("Arial", 9, QFont.Weight.Bold))
        update_profile_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        update_profile_btn.setStyleSheet("""
            QPushButton {
                background-color: #0b2545;
                color: white;
                padding: 10px 24px;
                border-radius: 6px;
                border: none;
            }
            QPushButton:hover { background-color: #1a5b9e; }
        """)
        update_profile_btn.clicked.connect(self.handle_update_profile)
        update_btn_layout.addWidget(update_profile_btn)

        account_layout.addLayout(update_btn_layout)

        # Tab 2: Change Password
        password_tab = QWidget()
        password_layout = QVBoxLayout(password_tab)
        password_layout.setContentsMargins(25, 25, 25, 25)

        pass_form = QFormLayout()
        pass_form.setSpacing(15)

        self.current_pass_input = QLineEdit()
        self.current_pass_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.current_pass_input.setStyleSheet(input_style)

        self.new_pass_input = QLineEdit()
        self.new_pass_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.new_pass_input.setStyleSheet(input_style)

        self.confirm_pass_input = QLineEdit()
        self.confirm_pass_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.confirm_pass_input.setStyleSheet(input_style)

        pass_form.addRow(make_label("Current Password"), self.current_pass_input)
        pass_form.addRow(make_label("New Password"), self.new_pass_input)
        pass_form.addRow(make_label("Confirm Password"), self.confirm_pass_input)

        password_layout.addLayout(pass_form)
        password_layout.addSpacing(15)

        pass_btn_layout = QHBoxLayout()
        pass_btn_layout.addStretch()

        change_pass_btn = QPushButton("Change Password")
        change_pass_btn.setFont(QFont("Arial", 9, QFont.Weight.Bold))
        change_pass_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        change_pass_btn.setStyleSheet("""
            QPushButton {
                background-color: #0b2545;
                color: white;
                padding: 10px 24px;
                border-radius: 6px;
                border: none;
            }
            QPushButton:hover { background-color: #1a5b9e; }
        """)
        change_pass_btn.clicked.connect(self.handle_change_password)
        pass_btn_layout.addWidget(change_pass_btn)

        password_layout.addLayout(pass_btn_layout)

        tab_widget.addTab(account_tab, "Account Information")
        tab_widget.addTab(password_tab, "Change Password")

        layout.addWidget(tab_widget)

    def handle_update_profile(self):
        """Updates full_name, username, and email in the 'user' table."""
        new_name = self.full_name_input.text().strip()
        new_user = self.username_input.text().strip()
        new_email = self.email_input.text().strip()
        user_id = self.current_user.get("user_id")

        if not new_name or not new_user:
            QMessageBox.warning(self, "Validation Error", "Full Name and Username cannot be empty.")
            return

        try:
            conn = db.get_connection()
            cursor = conn.cursor()
            
            # Exact columns: full_name, username, email, user_id
            query = "UPDATE user SET full_name = %s, username = %s, email = %s WHERE user_id = %s"
            cursor.execute(query, (new_name, new_user, new_email, user_id))
            conn.commit()

            # Update session variables
            self.current_user["full_name"] = new_name
            self.current_user["username"] = new_user
            self.current_user["email"] = new_email
            self.header_name_label.setText(new_name)

            cursor.close()
            conn.close()

            QMessageBox.information(self, "Success", "Profile updated successfully!")
        except Exception as e:
            QMessageBox.critical(self, "Database Error", f"Failed to update profile:\n{str(e)}")

    def handle_change_password(self):
        """Verifies current password and updates to new password in the 'user' table."""
        curr_pass = self.current_pass_input.text().strip()
        new_pass = self.new_pass_input.text().strip()
        confirm_pass = self.confirm_pass_input.text().strip()
        user_id = self.current_user.get("user_id")

        if not curr_pass or not new_pass or not confirm_pass:
            QMessageBox.warning(self, "Validation Error", "Please fill in all password fields.")
            return

        if new_pass != confirm_pass:
            QMessageBox.warning(self, "Validation Error", "New passwords do not match.")
            return

        try:
            conn = db.get_connection()
            cursor = conn.cursor()

            query = "SELECT password FROM user WHERE user_id = %s"
            cursor.execute(query, (user_id,))
            record = cursor.fetchone()

            if not record:
                QMessageBox.warning(self, "Error", "User account was not found.")
                cursor.close()
                conn.close()
                return

            # Fetched using key 'password' from dictionary
            db_password = str(record["password"]).strip()

            if db_password != curr_pass:
                QMessageBox.warning(self, "Security Error", "Current password is incorrect.")
                cursor.close()
                conn.close()
                return

            # Update database
            update_query = "UPDATE user SET password = %s WHERE user_id = %s"
            cursor.execute(update_query, (new_pass, user_id))
            conn.commit()

            cursor.close()
            conn.close()

            QMessageBox.information(self, "Success", "Password updated successfully!")
            self.current_pass_input.clear()
            self.new_pass_input.clear()
            self.confirm_pass_input.clear()

        except Exception as e:
            QMessageBox.critical(self, "Database Error", f"Failed to change password:\n{str(e)}")
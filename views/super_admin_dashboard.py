# Path: views/super_admin_dashboard.py
import sys
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QStackedWidget, QTableWidget, QTableWidgetItem, 
    QLineEdit, QComboBox, QHeaderView, QFrame, QDialog, QFormLayout, 
    QMessageBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

from db import (
    get_all_users, get_all_roles, add_user_to_db, 
    update_user_in_db
)


class UserDialog(QDialog):
    """Dialog modal for Creating and Editing Users."""
    def __init__(self, parent=None, user_data=None):
        super().__init__(parent)
        self.user_data = user_data
        self.is_edit = user_data is not None

        self.setWindowTitle("Edit User Account" if self.is_edit else "Add New User")
        self.setFixedWidth(420)
        self.setStyleSheet("""
            QDialog { background-color: #ffffff; }
            QLabel { font-weight: bold; color: #0b2545; }
            QLineEdit, QComboBox {
                border: 1px solid #ced4da;
                border-radius: 5px;
                padding: 6px 10px;
                background-color: #ffffff;
            }
            QPushButton {
                padding: 6px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setSpacing(15)

        form = QFormLayout()
        form.setSpacing(10)

        self.input_username = QLineEdit()
        self.input_password = QLineEdit()
        if self.is_edit:
            self.input_password.setPlaceholderText("(Leave blank to keep unchanged)")
        else:
            self.input_password.setEchoMode(QLineEdit.EchoMode.Password)

        self.input_fullname = QLineEdit()
        self.input_email = QLineEdit()

        self.combo_role = QComboBox()
        self.roles_list = get_all_roles()
        for role in self.roles_list:
            self.combo_role.addItem(role.get("role_name", ""), role.get("role_id"))

        self.combo_status = QComboBox()
        self.combo_status.addItems(["Active", "Inactive"])

        form.addRow("Username *:", self.input_username)
        form.addRow("Password" + ("" if self.is_edit else " *") + ":", self.input_password)
        form.addRow("Full Name *:", self.input_fullname)
        form.addRow("Email:", self.input_email)
        form.addRow("Role *:", self.combo_role)
        form.addRow("Status:", self.combo_status)

        layout.addLayout(form)

        # Pre-fill details if in Edit mode
        if self.is_edit:
            self.input_username.setText(str(user_data.get("username") or ""))
            self.input_fullname.setText(str(user_data.get("full_name") or ""))
            self.input_email.setText(str(user_data.get("email") or ""))
            
            # Match role
            role_id = user_data.get("role_id")
            for idx, r in enumerate(self.roles_list):
                if r.get("role_id") == role_id:
                    self.combo_role.setCurrentIndex(idx)
                    break
            
            # Match status
            status = user_data.get("status", "Active")
            self.combo_status.setCurrentText(status)

        # Action Buttons
        btn_box = QHBoxLayout()
        btn_box.addStretch()

        cancel_btn = QPushButton("Cancel")
        cancel_btn.setStyleSheet("background-color: #6c757d; color: white; border: none;")
        cancel_btn.clicked.connect(self.reject)

        save_btn = QPushButton("Save User" if self.is_edit else "Create User")
        save_btn.setStyleSheet("background-color: #0b2545; color: white; border: none;")
        save_btn.clicked.connect(self.save_user)

        btn_box.addWidget(cancel_btn)
        btn_box.addWidget(save_btn)

        layout.addLayout(btn_box)

    def save_user(self):
        username = self.input_username.text().strip()
        password = self.input_password.text().strip()
        fullname = self.input_fullname.text().strip()
        email = self.input_email.text().strip()
        role_id = self.combo_role.currentData()
        status = self.combo_status.currentText()

        if not username or not fullname:
            QMessageBox.warning(self, "Validation Error", "Username and Full Name are required.")
            return

        if not self.is_edit and not password:
            QMessageBox.warning(self, "Validation Error", "Password is required for new users.")
            return

        if self.is_edit:
            user_id = self.user_data.get("user_id")
            success, msg = update_user_in_db(user_id, username, password, fullname, email, role_id, status)
        else:
            success, msg = add_user_to_db(username, password, fullname, email, role_id, status)

        if success:
            QMessageBox.information(self, "Success", msg)
            self.accept()
        else:
            QMessageBox.critical(self, "Error", f"Failed to save user: {msg}")


class SuperAdminDashboard(QMainWindow):
    def __init__(self, user_info=None, on_logout_callback=None):
        super().__init__()
        self.user_info = user_info or {"full_name": "Super Admin", "role_name": "Super Admin"}
        self.on_logout_callback = on_logout_callback
        self.setWindowTitle("Mantalaan Newspaper System - Super Admin")
        
        # Open maximized to cover the whole screen
        self.showMaximized()

        self.all_users_cache = []
        
        self.init_ui()
        self.load_users_from_db()

    def init_ui(self):
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        
        main_layout = QHBoxLayout(main_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # ---------------- SIDEBAR ----------------
        sidebar = QFrame()
        sidebar.setFixedWidth(240)
        sidebar.setStyleSheet("""
            QFrame { background-color: #0b2545; border: none; }
            QPushButton {
                background-color: transparent;
                color: #a0aec0;
                text-align: left;
                padding: 12px 20px;
                font-size: 14px;
                font-weight: bold;
                border: none;
                border-radius: 6px;
            }
            QPushButton:hover { background-color: #13325b; color: #ffffff; }
            QPushButton:checked { background-color: #e2b93b; color: #0b2545; }
        """)

        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(15, 20, 15, 20)
        sidebar_layout.setSpacing(10)

        brand_label = QLabel("MANTALAAN\nNEWSPAPER")
        brand_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        brand_label.setStyleSheet("color: #ffffff; margin-bottom: 20px;")
        brand_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sidebar_layout.addWidget(brand_label)

        self.btn_dashboard = QPushButton("  Dashboard")
        self.btn_dashboard.setCheckable(True)

        self.btn_user_mgmt = QPushButton("  User Management")
        self.btn_user_mgmt.setCheckable(True)
        self.btn_user_mgmt.setChecked(True)

        self.nav_buttons = [self.btn_dashboard, self.btn_user_mgmt]
        
        self.btn_dashboard.clicked.connect(lambda: self.switch_page(0))
        self.btn_user_mgmt.clicked.connect(lambda: self.switch_page(1))

        sidebar_layout.addWidget(self.btn_dashboard)
        sidebar_layout.addWidget(self.btn_user_mgmt)

        sidebar_layout.addStretch()

        logout_btn = QPushButton("  Logout")
        logout_btn.setStyleSheet("""
            QPushButton { color: #e63946; text-align: left; padding: 10px 20px; font-weight: bold; }
            QPushButton:hover { background-color: #13325b; }
        """)
        logout_btn.clicked.connect(self.handle_logout)
        sidebar_layout.addWidget(logout_btn)

        main_layout.addWidget(sidebar)

        # ---------------- CONTENT AREA ----------------
        content_container = QWidget()
        content_layout = QVBoxLayout(content_container)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)

        top_bar = QFrame()
        top_bar.setFixedHeight(60)
        top_bar.setStyleSheet("background-color: #ffffff; border-bottom: 1px solid #e9ecef;")
        top_layout = QHBoxLayout(top_bar)
        top_layout.setContentsMargins(20, 0, 20, 0)
        top_layout.addStretch()

        display_name = self.user_info.get("full_name") or self.user_info.get("username") or "System Administrator"
        user_profile_lbl = QLabel(f"👤 {display_name}")
        user_profile_lbl.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        user_profile_lbl.setStyleSheet("color: #212529;")
        top_layout.addWidget(user_profile_lbl)

        content_layout.addWidget(top_bar)

        self.pages_widget = QStackedWidget()
        self.page_dashboard = self.create_dashboard_page()
        self.page_user_mgmt = self.create_user_mgmt_page()

        self.pages_widget.addWidget(self.page_dashboard)
        self.pages_widget.addWidget(self.page_user_mgmt)
        self.pages_widget.setCurrentIndex(1)

        content_layout.addWidget(self.pages_widget)
        main_layout.addWidget(content_container)

    def switch_page(self, index):
        for i, btn in enumerate(self.nav_buttons):
            btn.setChecked(i == index)
        self.pages_widget.setCurrentIndex(index)

    def create_dashboard_page(self):
        page = QWidget()
        page.setStyleSheet("background-color: #f8f9fa;")
        layout = QHBoxLayout(page)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)

        left_col = QVBoxLayout()
        title_lbl = QLabel("Dashboard")
        title_lbl.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        title_lbl.setStyleSheet("color: #0b2545;")
        
        sub_lbl = QLabel("Welcome, Super Admin!\nHere's an overview of the system.")
        sub_lbl.setStyleSheet("color: #6c757d; font-size: 13px; margin-bottom: 15px;")

        left_col.addWidget(title_lbl)
        left_col.addWidget(sub_lbl)

        total_users_card = QFrame()
        total_users_card.setStyleSheet("background-color: #ffffff; border-radius: 8px; border: 1px solid #e9ecef;")
        card_layout = QHBoxLayout(total_users_card)
        card_layout.setContentsMargins(20, 20, 20, 20)

        icon_lbl = QLabel("👥")
        icon_lbl.setFont(QFont("Arial", 28))
        
        stats_text_layout = QVBoxLayout()
        stat_title = QLabel("Total Users")
        stat_title.setStyleSheet("color: #6c757d; font-size: 12px; font-weight: bold;")
        
        self.lbl_total_users_count = QLabel("0")
        self.lbl_total_users_count.setFont(QFont("Arial", 20, QFont.Weight.Bold))
        self.lbl_total_users_count.setStyleSheet("color: #0b2545;")
        
        stat_sub = QLabel("Manage user accounts")
        stat_sub.setStyleSheet("color: #adb5bd; font-size: 11px;")

        stats_text_layout.addWidget(stat_title)
        stats_text_layout.addWidget(self.lbl_total_users_count)
        stats_text_layout.addWidget(stat_sub)

        card_layout.addWidget(icon_lbl)
        card_layout.addLayout(stats_text_layout)
        card_layout.addStretch()

        left_col.addWidget(total_users_card)
        left_col.addStretch()

        layout.addLayout(left_col, stretch=2)
        return page

    def create_user_mgmt_page(self):
        page = QWidget()
        page.setStyleSheet("background-color: #f8f9fa;")
        layout = QVBoxLayout(page)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(15)

        header_layout = QHBoxLayout()
        titles = QVBoxLayout()
        title_lbl = QLabel("User Management")
        title_lbl.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        title_lbl.setStyleSheet("color: #0b2545;")
        
        sub_lbl = QLabel("Manage system user accounts and their roles.")
        sub_lbl.setStyleSheet("color: #6c757d; font-size: 13px;")

        titles.addWidget(title_lbl)
        titles.addWidget(sub_lbl)

        add_user_btn = QPushButton("+ Add User")
        add_user_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        add_user_btn.setStyleSheet("""
            QPushButton {
                background-color: #0b2545;
                color: #ffffff;
                padding: 8px 18px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #1a5b9e; }
        """)
        add_user_btn.clicked.connect(self.open_add_user_dialog)

        header_layout.addLayout(titles)
        header_layout.addStretch()
        header_layout.addWidget(add_user_btn)
        layout.addLayout(header_layout)

        filter_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍  Search by name, email, or role...")
        self.search_input.setStyleSheet("background-color: #ffffff; border: 1px solid #ced4da; border-radius: 5px; padding: 6px 12px; font-size: 13px;")
        self.search_input.textChanged.connect(self.filter_users)

        self.role_filter = QComboBox()
        self.role_filter.addItem("All Roles")
        for r in get_all_roles():
            self.role_filter.addItem(r.get("role_name", ""))
        self.role_filter.setStyleSheet("background-color: #ffffff; border: 1px solid #ced4da; border-radius: 5px; padding: 6px 12px; min-width: 120px;")
        self.role_filter.currentIndexChanged.connect(self.filter_users)

        filter_layout.addWidget(self.search_input, stretch=3)
        filter_layout.addWidget(self.role_filter, stretch=1)
        layout.addLayout(filter_layout)

        self.user_table = QTableWidget()
        self.user_table.setColumnCount(6)
        self.user_table.setHorizontalHeaderLabels(["#", "Name", "Email", "Role", "Status", "Actions"])
        self.user_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.user_table.verticalHeader().setVisible(False)
        self.user_table.verticalHeader().setDefaultSectionSize(55)
        self.user_table.setStyleSheet("""
            QTableWidget { background-color: #ffffff; border: 1px solid #e9ecef; border-radius: 6px; gridline-color: #f1f3f5; }
            QHeaderView::section { background-color: #f8f9fa; color: #495057; font-weight: bold; border: none; padding: 10px; }
        """)

        layout.addWidget(self.user_table)
        return page

    def load_users_from_db(self):
        self.all_users_cache = get_all_users()
        self.lbl_total_users_count.setText(str(len(self.all_users_cache)))
        self.populate_user_table(self.all_users_cache)

    def filter_users(self):
        query = self.search_input.text().lower().strip()
        selected_role = self.role_filter.currentText()

        filtered = []
        for u in self.all_users_cache:
            name = str(u.get("full_name") or "").lower()
            email = str(u.get("email") or "").lower()
            role = str(u.get("role_name") or "").lower()
            username = str(u.get("username") or "").lower()

            matches_search = query in name or query in email or query in role or query in username
            matches_role = (selected_role == "All Roles") or (role == selected_role.lower())

            if matches_search and matches_role:
                filtered.append(u)

        self.populate_user_table(filtered)

    def populate_user_table(self, users):
        self.user_table.setRowCount(len(users))
        for row_idx, u in enumerate(users):
            user_id = str(u.get("user_id", ""))
            full_name = str(u.get("full_name") or u.get("username") or "")
            email = str(u.get("email") or "")
            role_name = str(u.get("role_name") or "N/A")
            status = str(u.get("status") or "Active")

            self.user_table.setItem(row_idx, 0, self.create_item(user_id, True))
            self.user_table.setItem(row_idx, 1, self.create_item(full_name, False))
            self.user_table.setItem(row_idx, 2, self.create_item(email, False))
            self.user_table.setItem(row_idx, 3, self.create_item(role_name, True))
            self.user_table.setItem(row_idx, 4, self.create_item(status, True))

            actions_widget = QWidget()
            actions_layout = QHBoxLayout(actions_widget)
            actions_layout.setContentsMargins(0, 0, 0, 0)
            actions_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

            edit_btn = QPushButton("✏️")
            edit_btn.setToolTip("Edit User")
            edit_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            edit_btn.setStyleSheet("border: none; background: transparent; font-size: 14px;")
            edit_btn.clicked.connect(lambda _, user_dict=u: self.open_edit_user_dialog(user_dict))

            actions_layout.addWidget(edit_btn)

            self.user_table.setCellWidget(row_idx, 5, actions_widget)

    def create_item(self, text, align_center=False):
        item = QTableWidgetItem(text)
        if align_center:
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        else:
            item.setTextAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        return item

    def open_add_user_dialog(self):
        dialog = UserDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.load_users_from_db()

    def open_edit_user_dialog(self, user_dict):
        dialog = UserDialog(self, user_data=user_dict)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.load_users_from_db()

    def handle_logout(self):
        self.close()
        if self.on_logout_callback:
            self.on_logout_callback()
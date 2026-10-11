# Path: views/clients_view.py
import math
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QPushButton, QTableWidget, QTableWidgetItem, QHeaderView, 
    QDialog, QMenu, QMessageBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QColor, QAction

from db import get_all_clients
from dialogs.add_client import AddClientDialog

class ClientsView(QWidget):
    def __init__(self):
        super().__init__()
        self.all_clients_data = []      # Full loaded/filtered list
        self.current_page = 1
        self.items_per_page = 10        # Displays 10 clients per page
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 25, 30, 25)
        layout.setSpacing(15)

        # Header Row
        top_row = QHBoxLayout()

        title = QLabel("Clients")
        title.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        title.setStyleSheet("color: #2c3e50;")

        add_btn = QPushButton("+ Add Client")
        add_btn.setFont(QFont("Arial", 9, QFont.Weight.Bold))
        add_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        add_btn.setStyleSheet("""
            QPushButton { background-color: #0b2545; color: white; padding: 10px 18px; border-radius: 5px; border: none; }
            QPushButton:hover { background-color: #134e75; }
        """)
        add_btn.clicked.connect(self.open_add_client_dialog)

        top_row.addWidget(title)
        top_row.addStretch()
        top_row.addWidget(add_btn)

        layout.addLayout(top_row)

        # Search Bar
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 Search client name, email, or contact...")
        self.search_input.setStyleSheet("""
            QLineEdit { padding: 10px 14px; border: 1px solid #dcdfe6; border-radius: 6px; background-color: #ffffff; color: #2c3e50; font-size: 13px; }
        """)
        self.search_input.textChanged.connect(self.filter_clients)
        layout.addWidget(self.search_input)

        # Clients Table
        self.table = QTableWidget()
        self.table.verticalHeader().setVisible(False)  # Hides default vertical numbers column
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels(["No.", "Client Name", "Contact Number", "Email", "Publications", "Status", "Actions"])
        
        self.table.setStyleSheet("""
            QTableWidget { 
                border: 1px solid #e0e0e0; 
                border-radius: 6px; 
                gridline-color: #f0f0f0; 
                background-color: #ffffff; 
                color: #2c3e50;
                font-size: 13px;
            }
            QTableWidget::item { color: #2c3e50; padding: 8px; }
            QTableWidget::item:selected { background-color: #e8f4f8; color: #0b2545; }
            QHeaderView::section {
                background-color: #f8f9fa; color: #2c3e50; padding: 10px; font-weight: bold; font-size: 12px; border: none; border-bottom: 2px solid #e0e0e0;
            }
        """)
        
        # Column Resizing Configurations
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents) # No.
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents) # Publications
        header.setSectionResizeMode(6, QHeaderView.ResizeMode.ResizeToContents) # Actions
        
        # Give Status column an explicit minimum width so the pill never clips
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.Interactive)
        self.table.setColumnWidth(5, 130)

        layout.addWidget(self.table)

        # Pagination Layout Container
        self.pagination_layout = QHBoxLayout()
        self.pagination_layout.addStretch()
        layout.addLayout(self.pagination_layout)

        self.load_clients_from_db()

    def load_clients_from_db(self):
        self.all_clients_data = get_all_clients()
        self.current_page = 1
        self.render_current_page()

    def filter_clients(self, query):
        query = query.lower().strip()
        all_records = get_all_clients()
        if not query:
            self.all_clients_data = all_records
        else:
            self.all_clients_data = [
                c for c in all_records 
                if query in str(c.get("client_name", "")).lower() or 
                   query in str(c.get("email", "")).lower() or 
                   query in str(c.get("contact_number", "")).lower()
            ]
        self.current_page = 1
        self.render_current_page()

    def render_current_page(self):
        total_items = len(self.all_clients_data)
        total_pages = max(1, math.ceil(total_items / self.items_per_page))

        if self.current_page > total_pages:
            self.current_page = total_pages

        start_idx = (self.current_page - 1) * self.items_per_page
        end_idx = start_idx + self.items_per_page
        page_data = self.all_clients_data[start_idx:end_idx]

        self.populate_table(page_data, start_idx)
        self.update_pagination_controls(total_pages)

    def populate_table(self, data, start_index=0):
        self.table.setRowCount(len(data))
        text_color = QColor("#2c3e50")

        for row, client in enumerate(data):
            self.table.setRowHeight(row, 45)

            def create_item(text):
                item = QTableWidgetItem(str(text if text is not None else ""))
                item.setForeground(text_color)
                return item

            self.table.setItem(row, 0, create_item(start_index + row + 1))
            self.table.setItem(row, 1, create_item(client.get("client_name", "")))
            self.table.setItem(row, 2, create_item(client.get("contact_number", "")))
            self.table.setItem(row, 3, create_item(client.get("email", "")))
            self.table.setItem(row, 4, create_item(client.get("publication_count", 0)))

            # Status Badge Pill with comfortable fixed width
            status_str = client.get("status", "Active") or "Active"
            status_label = QLabel(status_str)
            status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            status_label.setFont(QFont("Arial", 8, QFont.Weight.Bold))
            status_label.setFixedSize(95, 24)

            if status_str.lower() == "active":
                status_style = "QLabel { background-color: #d1fae5; color: #065f46; border-radius: 12px; }"
            elif status_str.lower() == "completed":
                status_style = "QLabel { background-color: #e0f2fe; color: #075985; border-radius: 12px; }"
            else:
                status_style = "QLabel { background-color: #f3f4f6; color: #4b5563; border-radius: 12px; }"

            status_label.setStyleSheet(status_style)

            status_container = QWidget()
            status_container.setStyleSheet("background: transparent;")
            status_layout = QHBoxLayout(status_container)
            status_layout.setContentsMargins(0, 0, 0, 0)
            status_layout.setSpacing(0)
            status_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
            status_layout.addWidget(status_label)
            
            self.table.setCellWidget(row, 5, status_container)

            # Actions Menu Button (Edit Only)
            action_btn = QPushButton("⋮")
            action_btn.setStyleSheet("border: none; font-size: 16px; font-weight: bold; color: #2c3e50; background: transparent;")
            action_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            action_btn.clicked.connect(lambda _, c=client, b=action_btn: self.show_action_menu(c, b))
            self.table.setCellWidget(row, 6, action_btn)

    def update_pagination_controls(self, total_pages):
        while self.pagination_layout.count() > 0:
            item = self.pagination_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        self.pagination_layout.addStretch()

        active_style = """
            QPushButton {
                background-color: #0b2545; color: white; border-radius: 4px;
                font-weight: bold; min-width: 28px; max-width: 28px; height: 28px; border: none;
            }
        """
        inactive_style = """
            QPushButton {
                background-color: transparent; color: #555555; border-radius: 4px;
                border: 1px solid #dcdfe6; min-width: 28px; max-width: 28px; height: 28px;
            }
            QPushButton:hover { background-color: #f0f4f8; }
        """

        prev_btn = QPushButton("<")
        prev_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        prev_btn.setStyleSheet(inactive_style)
        prev_btn.setEnabled(self.current_page > 1)
        prev_btn.clicked.connect(lambda: self.change_page(self.current_page - 1))
        self.pagination_layout.addWidget(prev_btn)

        for p in range(1, total_pages + 1):
            btn = QPushButton(str(p))
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setStyleSheet(active_style if p == self.current_page else inactive_style)
            btn.clicked.connect(lambda _, page=p: self.change_page(page))
            self.pagination_layout.addWidget(btn)

        next_btn = QPushButton(">")
        next_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        next_btn.setStyleSheet(inactive_style)
        next_btn.setEnabled(self.current_page < total_pages)
        next_btn.clicked.connect(lambda: self.change_page(self.current_page + 1))
        self.pagination_layout.addWidget(next_btn)

    def change_page(self, page_number):
        self.current_page = page_number
        self.render_current_page()

    def show_action_menu(self, client_data, button):
        menu = QMenu(self)
        menu.setStyleSheet("""
            QMenu { background-color: #ffffff; border: 1px solid #dcdfe6; border-radius: 4px; padding: 4px; }
            QMenu::item { padding: 6px 20px; color: #2c3e50; border-radius: 3px; }
            QMenu::item:selected { background-color: #f0f4f8; color: #0b2545; }
        """)

        edit_action = QAction("✏️ Edit Client", self)
        edit_action.triggered.connect(lambda: self.edit_client(client_data))
        menu.addAction(edit_action)
        
        menu.exec(button.mapToGlobal(button.rect().bottomLeft()))

    def edit_client(self, client_data):
        dialog = AddClientDialog(self, client_data=client_data)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.load_clients_from_db()

    def open_add_client_dialog(self):
        dialog = AddClientDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.load_clients_from_db()
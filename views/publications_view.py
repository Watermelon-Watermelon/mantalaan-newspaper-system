# Path: views/publications_view.py
import math
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QPushButton, QTableWidget, QTableWidgetItem, QHeaderView, 
    QDialog, QMenu, QMessageBox
)
from PyQt6.QtCore import Qt, QDate
from PyQt6.QtGui import QFont, QColor, QAction

from db import get_all_publications, soft_delete_publication_in_db
from dialogs.add_publication import AddPublicationDialog

class PublicationsView(QWidget):
    def __init__(self, on_view_details=None):
        super().__init__()
        self.on_view_details = on_view_details
        self.all_pubs_data = []
        self.current_page = 1
        self.items_per_page = 10
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 25, 30, 25)
        layout.setSpacing(15)

        # Header Row
        top_row = QHBoxLayout()

        title = QLabel("Publications")
        title.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        title.setStyleSheet("color: #2c3e50;")

        add_btn = QPushButton("+ Add Publication")
        add_btn.setFont(QFont("Arial", 9, QFont.Weight.Bold))
        add_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        add_btn.setStyleSheet("""
            QPushButton { background-color: #0b2545; color: white; padding: 10px 18px; border-radius: 5px; border: none; }
            QPushButton:hover { background-color: #134e75; }
        """)
        add_btn.clicked.connect(self.open_add_publication_dialog)

        top_row.addWidget(title)
        top_row.addStretch()
        top_row.addWidget(add_btn)

        layout.addLayout(top_row)

        # Search Bar
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 Search by client name, case number, or type...")
        self.search_input.setStyleSheet("""
            QLineEdit { padding: 10px 14px; border: 1px solid #dcdfe6; border-radius: 6px; background-color: #ffffff; color: #2c3e50; font-size: 13px; }
        """)
        self.search_input.textChanged.connect(self.filter_publications)
        layout.addWidget(self.search_input)

        # Table
        self.table = QTableWidget()
        self.table.verticalHeader().setVisible(False)
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels(["No.", "Case No.", "Client Name", "Type", "Date Received", "Status", "Actions"])
        
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
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents) # Date Received
        header.setSectionResizeMode(6, QHeaderView.ResizeMode.ResizeToContents) # Actions
        
        # Give Status column an explicit minimum width so the pill never clips
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.Interactive)
        self.table.setColumnWidth(5, 140)
        
        # Connect double-click to view details
        self.table.doubleClicked.connect(self.on_row_double_click)

        layout.addWidget(self.table)

        # Pagination Container
        self.pagination_layout = QHBoxLayout()
        self.pagination_layout.addStretch()
        layout.addLayout(self.pagination_layout)

        self.load_publications_from_db()

    def load_publications_from_db(self):
        self.all_pubs_data = get_all_publications()
        self.current_page = 1
        self.render_current_page()

    def filter_publications(self, query):
        query = query.lower().strip()
        if not query:
            self.all_pubs_data = get_all_publications()
        else:
            all_records = get_all_publications()
            self.all_pubs_data = [
                p for p in all_records 
                if query in str(p.get("client_name", "")).lower() or 
                   query in str(p.get("case_number", "")).lower() or 
                   query in str(p.get("publication_type", "")).lower()
            ]
        self.current_page = 1
        self.render_current_page()

    def render_current_page(self):
        total_items = len(self.all_pubs_data)
        total_pages = max(1, math.ceil(total_items / self.items_per_page))

        if self.current_page > total_pages:
            self.current_page = total_pages

        start_idx = (self.current_page - 1) * self.items_per_page
        end_idx = start_idx + self.items_per_page
        page_data = self.all_pubs_data[start_idx:end_idx]

        self.populate_table(page_data, start_idx)
        self.update_pagination_controls(total_pages)

    def populate_table(self, data, start_index=0):
        self.table.setRowCount(len(data))
        text_color = QColor("#2c3e50")

        for row, pub in enumerate(data):
            self.table.setRowHeight(row, 45)

            def create_item(text):
                item = QTableWidgetItem(str(text if text is not None else ""))
                item.setForeground(text_color)
                item.setData(Qt.ItemDataRole.UserRole, pub.get("publication_id"))
                return item

            raw_date = str(pub.get("date_received", ""))
            formatted_date = raw_date
            if raw_date:
                qdate = QDate.fromString(raw_date, "yyyy-MM-dd")
                if qdate.isValid():
                    formatted_date = qdate.toString("MMM d, yyyy")

            self.table.setItem(row, 0, create_item(start_index + row + 1))
            self.table.setItem(row, 1, create_item(pub.get("case_number", "")))
            self.table.setItem(row, 2, create_item(pub.get("client_name", "")))
            self.table.setItem(row, 3, create_item(pub.get("publication_type", "")))
            self.table.setItem(row, 4, create_item(formatted_date))

            # Status Badge Pill with comfortable fixed width
            status_str = pub.get("status", "In Progress") or "In Progress"
            status_label = QLabel(status_str)
            status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            status_label.setFont(QFont("Arial", 8, QFont.Weight.Bold))
            status_label.setFixedSize(110, 24)

            s_lower = status_str.lower()
            if "progress" in s_lower:
                status_style = "QLabel { background-color: #fef3c7; color: #d97706; border-radius: 12px; }"
            elif "scheduled" in s_lower:
                status_style = "QLabel { background-color: #e0f2fe; color: #0284c7; border-radius: 12px; }"
            elif "completed" in s_lower:
                status_style = "QLabel { background-color: #d1fae5; color: #059669; border-radius: 12px; }"
            elif "inactive" in s_lower:
                status_style = "QLabel { background-color: #fee2e2; color: #dc2626; border-radius: 12px; }"
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

            # Actions Menu Button
            action_btn = QPushButton("⋮")
            action_btn.setStyleSheet("border: none; font-size: 16px; font-weight: bold; color: #2c3e50; background: transparent;")
            action_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            action_btn.clicked.connect(lambda _, p=pub, b=action_btn: self.show_action_menu(p, b))
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

    def view_details(self, pub_id):
        if self.on_view_details:
            self.on_view_details(pub_id)

    def on_row_double_click(self, index):
        row = index.row()
        item = self.table.item(row, 0)
        if item:
            pub_id = item.data(Qt.ItemDataRole.UserRole)
            if pub_id:
                self.view_details(pub_id)

    def show_action_menu(self, pub_data, button):
        menu = QMenu(self)
        menu.setStyleSheet("""
            QMenu { background-color: #ffffff; border: 1px solid #dcdfe6; border-radius: 4px; padding: 4px; }
            QMenu::item { padding: 6px 20px; color: #2c3e50; border-radius: 3px; }
            QMenu::item:selected { background-color: #f0f4f8; color: #0b2545; }
        """)

        view_action = QAction("👁️ View Details", self)
        edit_action = QAction("✏️ Edit Publication", self)
        deactivate_action = QAction("🗑️ Deactivate Publication", self)

        pub_id = pub_data.get("publication_id")
        view_action.triggered.connect(lambda: self.view_details(pub_id))
        edit_action.triggered.connect(lambda: self.edit_publication(pub_data))
        deactivate_action.triggered.connect(lambda: self.deactivate_publication(pub_data))

        menu.addAction(view_action)
        menu.addAction(edit_action)
        menu.addAction(deactivate_action)
        
        menu.exec(button.mapToGlobal(button.rect().bottomLeft()))

    def edit_publication(self, pub_data):
        dialog = AddPublicationDialog(self, pub_data=pub_data)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.load_publications_from_db()

    def deactivate_publication(self, pub_data):
        case_no = pub_data.get("case_number", "this publication")
        pub_id = pub_data.get("publication_id")

        msg = QMessageBox(self)
        msg.setWindowTitle("Confirm Deactivation")
        msg.setText(f"Are you sure you want to deactivate publication for Case '{case_no}'? It will be marked as Inactive.")
        msg.setIcon(QMessageBox.Icon.Question)
        
        yes_btn = msg.addButton(QMessageBox.StandardButton.Yes)
        no_btn = msg.addButton(QMessageBox.StandardButton.No)
        msg.setDefaultButton(no_btn)

        msg.setStyleSheet("""
            QMessageBox { background-color: #ffffff; }
            QLabel { color: #2c3e50; font-size: 13px; }
            QPushButton { 
                background-color: #0b2545; 
                color: #ffffff; 
                border-radius: 4px; 
                padding: 6px 16px; 
                min-width: 60px;
            }
            QPushButton:hover { background-color: #134e75; }
        """)

        msg.exec()

        if msg.clickedButton() == yes_btn:
            if soft_delete_publication_in_db(pub_id):
                self.load_publications_from_db()
            else:
                QMessageBox.critical(self, "Error", "Failed to deactivate publication record.")

    def open_add_publication_dialog(self):
        dialog = AddPublicationDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.load_publications_from_db()
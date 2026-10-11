# Path: views/publication_details_view.py
from datetime import date
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, 
    QPushButton, QTableWidget, QTableWidgetItem, QHeaderView,
    QDialog, QDialogButtonBox, QDateEdit, QFormLayout, QMessageBox, QMenu
)
from PyQt6.QtCore import Qt, QDate
from PyQt6.QtGui import QFont, QAction

from db import (
    get_publication_details, get_publication_issues, 
    add_issue_to_db, update_issue_in_db, delete_issue_from_db
)


class AddEditIssueDialog(QDialog):
    """Dialog for adding or editing an issue date."""
    def __init__(self, parent=None, issue_title="Add Issue", initial_date=None):
        super().__init__(parent)
        self.setWindowTitle(issue_title)
        self.setFixedWidth(320)
        
        self.setStyleSheet("""
            QDialog {
                background-color: #ffffff;
            }
            QLabel {
                color: #2c3e50;
                font-size: 13px;
                font-weight: bold;
            }
            QDateEdit {
                background-color: #ffffff;
                color: #2c3e50;
                border: 1px solid #cccccc;
                border-radius: 4px;
                padding: 5px;
                font-size: 13px;
            }
            QDateEdit::drop-down {
                border: none;
            }
            QPushButton {
                background-color: #0b2545;
                color: white;
                border-radius: 4px;
                padding: 6px 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #134e75;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        form_layout = QFormLayout()

        self.date_edit = QDateEdit()
        self.date_edit.setCalendarPopup(True)
        if initial_date:
            qdate = QDate.fromString(str(initial_date), "yyyy-MM-dd")
            self.date_edit.setDate(qdate if qdate.isValid() else QDate.currentDate())
        else:
            self.date_edit.setDate(QDate.currentDate())
        self.date_edit.setDisplayFormat("MMM d, yyyy")

        form_layout.addRow("Publication Date:", self.date_edit)
        layout.addLayout(form_layout)

        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

    def get_selected_date(self):
        return self.date_edit.date().toString("yyyy-MM-dd")


class PublicationDetailsView(QWidget):
    def __init__(self, publication_id, on_back):
        super().__init__()
        self.publication_id = publication_id
        self.on_back = on_back
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(25, 20, 25, 20)
        layout.setSpacing(15)

        # 1. Navigation Header
        back_btn = QPushButton("← Back to Publications")
        back_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        back_btn.setStyleSheet("""
            QPushButton {
                border: none; color: #1a5b9e; font-size: 13px; font-weight: bold; background: transparent; text-align: left;
            }
            QPushButton:hover { color: #0b2545; text-decoration: underline; }
        """)
        back_btn.clicked.connect(self.on_back)
        layout.addWidget(back_btn)

        title = QLabel("Publication Details")
        title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        title.setStyleSheet("color: #0b2545;")
        layout.addWidget(title)

        self.pub = get_publication_details(self.publication_id) or {}

        # 2. Details Card
        card = QFrame()
        card.setStyleSheet("QFrame { background-color: white; border-radius: 8px; border: 1px solid #e0e0e0; }")
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(25, 20, 25, 20)
        card_layout.setSpacing(15)

        # Row 1: Case No & Date Received
        row1 = QHBoxLayout()
        raw_date = str(self.pub.get("date_received", ""))
        formatted_received = raw_date
        if raw_date:
            qdate = QDate.fromString(raw_date, "yyyy-MM-dd")
            if qdate.isValid():
                formatted_received = qdate.toString("MMM d, yyyy")

        row1.addWidget(self._make_field("Case No.", self.pub.get("case_number", "N/A")), 1)
        row1.addWidget(self._make_field("Date Received", formatted_received), 1)
        card_layout.addLayout(row1)

        # Row 2: Client & Required Issues
        row2 = QHBoxLayout()
        self.req_issues_lbl = QLabel(str(self.pub.get("required_issues", 0)))
        self.req_issues_lbl.setStyleSheet("color: #2c3e50; font-size: 14px; font-weight: bold; background: transparent; border: none;")
        
        row2.addWidget(self._make_field("Client", self.pub.get("client_name", "N/A")), 1)
        
        req_widget = QWidget()
        req_widget.setStyleSheet("background: transparent; border: none;")
        req_l = QVBoxLayout(req_widget)
        req_l.setContentsMargins(0, 0, 0, 0)
        req_l.setSpacing(2)
        lbl_req = QLabel("Required Issues")
        lbl_req.setStyleSheet("color: #7f8c8d; font-size: 11px; background: transparent; border: none;")
        req_l.addWidget(lbl_req)
        req_l.addWidget(self.req_issues_lbl)
        row2.addWidget(req_widget, 1)
        card_layout.addLayout(row2)

        # Row 3: Publication Type & Status
        row3 = QHBoxLayout()
        row3.addWidget(self._make_field("Publication Type", self.pub.get("publication_type", "N/A")), 1)
        row3.addWidget(self._make_field("Status", self.pub.get("status", "In Progress"), is_status=True), 1)
        card_layout.addLayout(row3)

        # Row 4: Legal Description / Details (Full Width)
        card_layout.addWidget(self._make_field("Legal Description / Details", self.pub.get("legal_description", "None provided")))

        # Row 5: Notes (Full Width)
        card_layout.addWidget(self._make_field("Notes", self.pub.get("notes", "No notes added")))

        layout.addWidget(card)

        # 3. Schedule Section Header + Add Issue Button
        issues_header_layout = QHBoxLayout()
        issues_title = QLabel("Publication Schedule")
        issues_title.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        issues_title.setStyleSheet("color: #0b2545;")

        add_issue_btn = QPushButton("+ Add Issue")
        add_issue_btn.setFont(QFont("Arial", 9, QFont.Weight.Bold))
        add_issue_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        add_issue_btn.setStyleSheet("""
            QPushButton { 
                background-color: #0b2545; 
                color: white; 
                padding: 6px 14px; 
                border-radius: 5px; 
                border: none; 
            }
            QPushButton:hover { background-color: #134e75; }
        """)
        add_issue_btn.clicked.connect(self.open_add_issue_dialog)

        issues_header_layout.addWidget(issues_title)
        issues_header_layout.addStretch()
        issues_header_layout.addWidget(add_issue_btn)
        layout.addLayout(issues_header_layout)

        # 4. Schedule Table
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["Issue", "Scheduled Date", "Status", "Actions"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setStyleSheet("""
            QTableWidget { background-color: white; border: 1px solid #e0e0e0; border-radius: 6px; gridline-color: #f0f0f0; }
            QHeaderView::section { background-color: #f8f9fa; color: #2c3e50; font-weight: bold; border: none; padding: 10px; }
            QTableWidget::item { padding: 8px; color: #2c3e50; }
        """)

        layout.addWidget(self.table)
        self.load_issues_table()

    def load_issues_table(self):
        """Loads and populates issues from the database into the table."""
        self.issues = get_publication_issues(self.publication_id) or []
        self.table.setRowCount(len(self.issues))

        self.req_issues_lbl.setText(str(len(self.issues)))
        today_str = str(date.today())

        for row, issue in enumerate(self.issues):
            self.table.setRowHeight(row, 40)

            issue_num = issue.get("issue_number", row + 1)
            self.table.setItem(row, 0, QTableWidgetItem(f"Issue {issue_num}"))

            issue_raw_date = str(issue.get("publication_date", ""))
            formatted_issue_date = issue_raw_date
            if issue_raw_date:
                qdate = QDate.fromString(issue_raw_date, "yyyy-MM-dd")
                if qdate.isValid():
                    formatted_issue_date = qdate.toString("MMM d, yyyy")

            self.table.setItem(row, 1, QTableWidgetItem(formatted_issue_date))

            # Status Pill (automatically Published if date has passed)
            status_str = "Published" if (issue_raw_date and issue_raw_date < today_str) else issue.get("status", "Scheduled")
            status_label = QLabel(status_str)
            status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            status_label.setFont(QFont("Arial", 8, QFont.Weight.Bold))
            status_label.setFixedSize(90, 24)
            
            if status_str == "Published":
                status_label.setStyleSheet("QLabel { background-color: #d1fae5; color: #047857; border-radius: 12px; }")
            else:
                status_label.setStyleSheet("QLabel { background-color: #e0f2fe; color: #0284c7; border-radius: 12px; }")

            # Transparent container
            status_container = QWidget()
            status_container.setStyleSheet("background: transparent; border: none;")
            status_layout = QHBoxLayout(status_container)
            status_layout.setContentsMargins(0, 0, 0, 0)
            status_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
            status_layout.addWidget(status_label)
            self.table.setCellWidget(row, 2, status_container)

            # Actions Button with Context Menu
            action_btn = QPushButton("⋮")
            action_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            action_btn.setStyleSheet("border: none; font-size: 16px; color: #2c3e50; background: transparent;")
            action_btn.clicked.connect(lambda _, i=issue: self.show_action_menu(action_btn, i))
            self.table.setCellWidget(row, 3, action_btn)

    def show_action_menu(self, button, issue):
        """Displays update/delete menu when clicking the triple dots."""
        menu = QMenu(self)
        menu.setStyleSheet("""
            QMenu { background-color: white; border: 1px solid #dcdcdc; border-radius: 4px; padding: 4px; }
            QMenu::item { padding: 6px 20px; color: #2c3e50; font-size: 12px; }
            QMenu::item:selected { background-color: #f0f4f8; color: #0b2545; }
        """)

        edit_action = QAction("Edit Date", self)
        toggle_status_action = QAction(f"Mark as {'Published' if issue.get('status') == 'Scheduled' else 'Scheduled'}", self)
        delete_action = QAction("Delete Issue", self)

        edit_action.triggered.connect(lambda: self.edit_issue_date(issue))
        toggle_status_action.triggered.connect(lambda: self.toggle_issue_status(issue))
        delete_action.triggered.connect(lambda: self.delete_issue(issue))

        menu.addAction(edit_action)
        menu.addAction(toggle_status_action)
        menu.addSeparator()
        menu.addAction(delete_action)

        menu.exec(button.mapToGlobal(button.rect().bottomLeft()))

    def edit_issue_date(self, issue):
        dialog = AddEditIssueDialog(self, issue_title=f"Edit Issue {issue.get('issue_number')}", initial_date=issue.get('publication_date'))
        if dialog.exec() == QDialog.DialogCode.Accepted:
            new_date = dialog.get_selected_date()
            if update_issue_in_db(issue.get("issue_id"), new_date, issue.get("status", "Scheduled")):
                self.load_issues_table()
            else:
                QMessageBox.critical(self, "Error", "Failed to update issue date.")

    def toggle_issue_status(self, issue):
        new_status = "Published" if issue.get("status") == "Scheduled" else "Scheduled"
        if update_issue_in_db(issue.get("issue_id"), issue.get("publication_date"), new_status):
            self.load_issues_table()

    def delete_issue(self, issue):
        confirm = QMessageBox.question(
            self, "Confirm Delete", 
            f"Are you sure you want to delete Issue {issue.get('issue_number')}?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if confirm == QMessageBox.StandardButton.Yes:
            if delete_issue_from_db(issue.get("issue_id"), self.publication_id):
                self.load_issues_table()
            else:
                QMessageBox.critical(self, "Error", "Failed to delete issue.")

    def open_add_issue_dialog(self):
        next_num = len(self.issues) + 1
        dialog = AddEditIssueDialog(self, issue_title=f"Add Issue {next_num}")
        
        if dialog.exec() == QDialog.DialogCode.Accepted:
            selected_date = dialog.get_selected_date()
            if add_issue_to_db(self.publication_id, next_num, selected_date):
                self.load_issues_table()
            else:
                QMessageBox.critical(self, "Error", "Failed to add issue record to database.")

    def _make_field(self, label, value, is_status=False):
        widget = QWidget()
        widget.setStyleSheet("background: transparent; border: none;")
        l = QVBoxLayout(widget)
        l.setContentsMargins(0, 0, 0, 0)
        l.setSpacing(2)

        lbl = QLabel(label)
        lbl.setStyleSheet("color: #7f8c8d; font-size: 11px; background: transparent; border: none;")

        if is_status:
            val = QLabel(str(value))
            val.setAlignment(Qt.AlignmentFlag.AlignCenter)
            val.setFont(QFont("Arial", 9, QFont.Weight.Bold))
            val.setFixedSize(110, 26)
            
            if str(value).lower() in ["published", "completed"]:
                val.setStyleSheet("QLabel { background-color: #d1fae5; color: #047857; border-radius: 13px; }")
            else:
                val.setStyleSheet("QLabel { background-color: #fef9e7; color: #f39c12; border-radius: 13px; }")
        else:
            val = QLabel(str(value) if value else "N/A")
            val.setStyleSheet("color: #2c3e50; font-size: 14px; font-weight: bold; background: transparent; border: none;")

        l.addWidget(lbl)
        l.addWidget(val)
        return widget
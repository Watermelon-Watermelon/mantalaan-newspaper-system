# Path: views/publication_schedule_view.py
import os
import tempfile
from datetime import date
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QLineEdit, QScrollArea, QTableWidget, QTableWidgetItem, QHeaderView,
    QPushButton, QFileDialog, QMessageBox
)
from PyQt6.QtCore import Qt, QDate
from PyQt6.QtGui import QFont

from db import (
    get_all_publication_schedules, 
    save_monday_pdf_to_db, 
    get_monday_pdf_from_db,
    delete_monday_pdf_from_db
)


class PublicationScheduleView(QWidget):
    def __init__(self):
        super().__init__()
        self.all_schedules = []
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(25, 20, 25, 20)
        layout.setSpacing(20)

        # 1. Page Header Title
        header_layout = QHBoxLayout()
        title_icon = QLabel("📅")
        title_icon.setStyleSheet("font-size: 20px;")
        
        title = QLabel("Publication Schedule")
        title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        title.setStyleSheet("color: #0b2545;")

        header_layout.addWidget(title_icon)
        header_layout.addWidget(title)
        header_layout.addStretch()
        layout.addLayout(header_layout)

        # 2. Search Bar
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search by client or case number...")
        self.search_input.setStyleSheet("""
            QLineEdit {
                background-color: white;
                border: 1px solid #dcdcdc;
                border-radius: 6px;
                padding: 8px 14px;
                font-size: 13px;
                color: #2c3e50;
            }
            QLineEdit:focus {
                border: 1px solid #0b2545;
            }
        """)
        self.search_input.textChanged.connect(self.filter_schedules)
        search_layout.addWidget(self.search_input)
        layout.addLayout(search_layout)

        # 3. Scroll Area for Grouped Date Sections
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
            }
        """)

        self.container_widget = QWidget()
        self.container_widget.setStyleSheet("background-color: transparent;")
        self.container_layout = QVBoxLayout(self.container_widget)
        self.container_layout.setContentsMargins(0, 0, 18, 0)
        self.container_layout.setSpacing(20)
        self.container_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.scroll_area.setWidget(self.container_widget)
        layout.addWidget(self.scroll_area)
        
        self.load_schedule_data()

    def load_schedule_data(self):
        self.all_schedules = get_all_publication_schedules() or []
        self.populate_schedule(self.all_schedules)

    def populate_schedule(self, data):
        while self.container_layout.count():
            child = self.container_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        if not data:
            no_data_lbl = QLabel("No publication schedules found.")
            no_data_lbl.setStyleSheet("color: #7f8c8d; font-size: 13px; font-style: italic;")
            self.container_layout.addWidget(no_data_lbl)
            return

        grouped_data = {}
        for item in data:
            raw_date = str(item.get("publication_date", "Unscheduled"))
            grouped_data.setdefault(raw_date, []).append(item)

        sorted_dates = sorted(grouped_data.keys())
        today_str = str(date.today())

        for raw_date in sorted_dates:
            issues = grouped_data[raw_date]

            display_date = raw_date
            qdate = QDate.fromString(raw_date, "yyyy-MM-dd")
            if qdate.isValid():
                display_date = qdate.toString("MMMM d, yyyy (dddd)")

            # --- Monday Section Header Layout ---
            date_bar_layout = QHBoxLayout()
            date_bar_layout.setContentsMargins(0, 5, 0, 0)

            date_header = QLabel(display_date)
            date_header.setFont(QFont("Arial", 13, QFont.Weight.Bold))
            date_header.setStyleSheet("color: #2c3e50;")
            date_bar_layout.addWidget(date_header)

            # Check PDF record and determine status badge
            pdf_record = get_monday_pdf_from_db(raw_date)
            
            # Determine Status Badge & Colors
            if raw_date < today_str:
                status_text = "Published"
                badge_bg, badge_fg = "#d1fae5", "#047857"
            elif not pdf_record:
                status_text = "Not Uploaded"
                badge_bg, badge_fg = "#f3f4f6", "#4b5563"
            else:
                review_status = pdf_record.get("review_status", "Pending")
                if review_status == "Approved":
                    status_text = "Approved"
                    badge_bg, badge_fg = "#d1fae5", "#047857"
                elif review_status == "Rejected":
                    status_text = "Rejected"
                    badge_bg, badge_fg = "#fee2e2", "#b91c1c"
                else:
                    status_text = "For Review"
                    badge_bg, badge_fg = "#fef9e7", "#f39c12"

            status_badge = QLabel(status_text)
            status_badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
            status_badge.setFont(QFont("Arial", 8, QFont.Weight.Bold))
            status_badge.setFixedSize(100, 24)
            status_badge.setStyleSheet(f"QLabel {{ background-color: {badge_bg}; color: {badge_fg}; border-radius: 12px; }}")
            date_bar_layout.addWidget(status_badge)
            date_bar_layout.addStretch()

            # Upload / View Button Logic
            upload_btn = QPushButton()
            upload_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            
            is_rejected = pdf_record and pdf_record.get("review_status") == "Rejected"
            if pdf_record and not is_rejected:
                file_name = pdf_record.get("file_name", "document.pdf")
                upload_btn.setText(f"📄 {file_name} (View/Replace)")
                upload_btn.setStyleSheet("""
                    QPushButton {
                        background-color: #047857;
                        color: white;
                        border-radius: 5px;
                        padding: 6px 14px;
                        font-size: 11px;
                        font-weight: bold;
                    }
                    QPushButton:hover { background-color: #065f46; }
                """)
            else:
                upload_btn.setText("📤 Upload PDF")
                upload_btn.setStyleSheet("""
                    QPushButton {
                        background-color: #0b2545;
                        color: white;
                        border-radius: 5px;
                        padding: 6px 14px;
                        font-size: 11px;
                        font-weight: bold;
                    }
                    QPushButton:hover { background-color: #13325b; }
                """)

            upload_btn.clicked.connect(lambda _, d=raw_date, rec=pdf_record: self.handle_pdf_action(d, rec))
            date_bar_layout.addWidget(upload_btn)

            self.container_layout.addLayout(date_bar_layout)

            # --- Table for Issues on this Date ---
            table = QTableWidget()
            table.setColumnCount(4)
            table.setHorizontalHeaderLabels(["Case No.", "Client", "Issue", "Status"])
            table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
            table.setStyleSheet("""
                QTableWidget {
                    background-color: white;
                    border: 1px solid #e0e0e0;
                    border-radius: 6px;
                    gridline-color: #f0f0f0;
                }
                QHeaderView::section {
                    background-color: #f8f9fa;
                    color: #7f8c8d;
                    font-weight: bold;
                    border: none;
                    padding: 10px;
                    font-size: 11px;
                }
                QTableWidget::item {
                    padding: 8px;
                    color: #2c3e50;
                }
            """)
            table.setFocusPolicy(Qt.FocusPolicy.NoFocus)
            table.setRowCount(len(issues))
            table.setFixedHeight(len(issues) * 45 + 40)

            for row, item in enumerate(issues):
                table.setRowHeight(row, 45)

                # Case No.
                table.setItem(row, 0, QTableWidgetItem(str(item.get("case_number", "N/A"))))

                # Client
                table.setItem(row, 1, QTableWidgetItem(str(item.get("client_name", "N/A"))))

                # Issue label formatting
                issue_num = item.get("issue_number", 1)
                req_issues = item.get("required_issues")
                if not req_issues or int(req_issues) <= 1:
                    pub_id = item.get("publication_id")
                    if pub_id:
                        matching_issues = [s for s in self.all_schedules if s.get("publication_id") == pub_id]
                        req_issues = len(matching_issues)
                    else:
                        req_issues = 1

                table.setItem(row, 2, QTableWidgetItem(f"{issue_num} of {req_issues}"))

                # Status Pill
                status_str = "Published" if raw_date < today_str else item.get("status", "Scheduled")
                status_label = QLabel(status_str)
                status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                status_label.setFont(QFont("Arial", 8, QFont.Weight.Bold))
                status_label.setFixedSize(90, 24)

                if status_str == "Published":
                    status_label.setStyleSheet("QLabel { background-color: #d1fae5; color: #047857; border-radius: 12px; }")
                else:
                    status_label.setStyleSheet("QLabel { background-color: #e0f2fe; color: #0284c7; border-radius: 12px; }")

                status_container = QWidget()
                status_container.setStyleSheet("background: transparent; border: none;")
                status_layout = QHBoxLayout(status_container)
                status_layout.setContentsMargins(0, 0, 0, 0)
                status_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
                status_layout.addWidget(status_label)
                table.setCellWidget(row, 3, status_container)

            self.container_layout.addWidget(table)

    def handle_pdf_action(self, publication_date, existing_record):
        if existing_record and existing_record.get("review_status") != "Rejected":
            msg_box = QMessageBox(self)
            msg_box.setWindowTitle("Manage PDF for " + publication_date)
            msg_box.setText(f"A PDF ('{existing_record.get('file_name')}') is stored for this date.")
            msg_box.setInformativeText("What would you like to do?")
            
            view_btn = msg_box.addButton("Open / Save PDF", QMessageBox.ButtonRole.AcceptRole)
            upload_new_btn = msg_box.addButton("Upload New PDF", QMessageBox.ButtonRole.ActionRole)
            remove_btn = msg_box.addButton("Remove PDF", QMessageBox.ButtonRole.DestructiveRole)
            cancel_btn = msg_box.addButton("Cancel", QMessageBox.ButtonRole.RejectRole)
            
            msg_box.setStyleSheet("""
                QMessageBox { background-color: #ffffff; min-width: 520px; }
                QMessageBox QLabel { color: #2c3e50; font-size: 13px; background-color: transparent; }
                QPushButton { background-color: #0b2545; color: white; border-radius: 5px; padding: 8px 16px; font-weight: bold; min-width: 110px; }
                QPushButton:hover { background-color: #13325b; }
            """)
            msg_box.exec()

            clicked = msg_box.clickedButton()
            if clicked == view_btn:
                self.open_stored_pdf(existing_record)
                return
            elif clicked == remove_btn:
                success, msg = delete_monday_pdf_from_db(publication_date)
                if success:
                    self.load_schedule_data()
                return
            elif clicked != upload_new_btn:
                return

        # Open file dialog to upload PDF
        file_path, _ = QFileDialog.getOpenFileName(self, "Select PDF Publication", "", "PDF Files (*.pdf)")
        if file_path:
            try:
                with open(file_path, "rb") as f:
                    binary_data = f.read()
                
                file_name = os.path.basename(file_path)
                success, msg = save_monday_pdf_to_db(publication_date, file_name, binary_data)
                if success:
                    self.load_schedule_data()
            except Exception as e:
                QMessageBox.critical(self, "File Error", f"Could not read file: {e}")

    def open_stored_pdf(self, record):
        try:
            file_name = record.get("file_name", "document.pdf")
            binary_data = record.get("file_data")
            temp_path = os.path.join(tempfile.gettempdir(), file_name)
            with open(temp_path, "wb") as f:
                f.write(binary_data)
            os.startfile(temp_path)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not open PDF file: {e}")

    def filter_schedules(self, text):
        query = text.lower().strip()
        if not query:
            self.populate_schedule(self.all_schedules)
            return

        filtered = [
            item for item in self.all_schedules
            if query in str(item.get("client_name", "")).lower() or 
               query in str(item.get("case_number", "")).lower()
        ]
        self.populate_schedule(filtered)
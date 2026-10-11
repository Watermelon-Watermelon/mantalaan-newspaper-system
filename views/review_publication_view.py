# Path: views/review_publication_view.py
import os
import subprocess
import platform
import tempfile
from datetime import datetime, date
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QPushButton, 
    QScrollArea, QMessageBox, QTabWidget, QTableWidget, QTableWidgetItem,
    QHeaderView, QAbstractItemView
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
import db

class ReviewPublicationView(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.load_pending_data()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)

        # Page Title & Description
        title_layout = QVBoxLayout()
        title_lbl = QLabel("Review Publication")
        title_lbl.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        title_lbl.setStyleSheet("color: #0b2545;")
        
        desc_lbl = QLabel("View and approve publication PDFs uploaded by the OIC in the Publication Schedule.")
        desc_lbl.setStyleSheet("color: #64748b; font-size: 13px;")
        
        title_layout.addWidget(title_lbl)
        title_layout.addWidget(desc_lbl)
        layout.addLayout(title_layout)

        # Tabs for Pending vs Reviewed
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet("""
            QTabWidget::pane { border: 1px solid #dcdde1; background: white; border-radius: 6px; }
            QTabBar::tab { background: #f1f2f6; padding: 10px 20px; margin-right: 2px; border-top-left-radius: 4px; border-top-right-radius: 4px; color: #2f3640; font-weight: bold; }
            QTabBar::tab:selected { background: #0b2545; color: white; }
        """)

        # Tab 1: Pending Review Container
        self.pending_container = QWidget()
        self.pending_layout = QVBoxLayout(self.pending_container)
        self.pending_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        self.pending_scroll = QScrollArea()
        self.pending_scroll.setWidgetResizable(True)
        self.pending_scroll.setWidget(self.pending_container)
        self.pending_scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")

        # Tab 2: Reviewed Container
        self.reviewed_container = QWidget()
        self.reviewed_layout = QVBoxLayout(self.reviewed_container)
        self.reviewed_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        self.reviewed_scroll = QScrollArea()
        self.reviewed_scroll.setWidgetResizable(True)
        self.reviewed_scroll.setWidget(self.reviewed_container)
        self.reviewed_scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")

        self.tabs.addTab(self.pending_scroll, "Pending Review (0)")
        self.tabs.addTab(self.reviewed_scroll, "Reviewed (0)")

        layout.addWidget(self.tabs)

    def load_pending_data(self):
        """Fetches scheduled publications with uploaded PDFs from database, groups rows by upload/date, and categorizes into Pending vs Reviewed."""
        while self.pending_layout.count():
            child = self.pending_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        while self.reviewed_layout.count():
            child = self.reviewed_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        schedules = []
        try:
            schedules = db.get_scheduled_publications_with_pdfs()
        except Exception as e:
            print(f"Error fetching scheduled publications: {e}")

        pdf_records = [s for s in schedules if s.get('file_name')]

        grouped_data = {}
        for r in pdf_records:
            key = (
                r.get('schedule_id'), 
                r.get('publication_date'), 
                r.get('file_name'), 
                str(r.get('review_status', 'Pending'))
            )
            if key not in grouped_data:
                grouped_data[key] = []
            grouped_data[key].append({
                'case_number': r.get('case_number'),
                'client_name': r.get('client_name'),
                'issue_number': r.get('issue_number')
            })

        pending_groups = []
        reviewed_groups = []

        for key, rows in grouped_data.items():
            schedule_id, pub_date, file_name, review_status = key
            master_record = {
                'schedule_id': schedule_id,
                'publication_date': pub_date,
                'file_name': file_name,
                'review_status': review_status,
                'rows': rows
            }
            if review_status in ['Pending', '', 'None']:
                pending_groups.append(master_record)
            else:
                reviewed_groups.append(master_record)

        # Populate Pending Tab
        if not pending_groups:
            empty_lbl = QLabel("No pending publication reviews at this time.")
            empty_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            empty_lbl.setStyleSheet("color: #94a3b8; font-size: 14px; margin-top: 50px;")
            self.pending_layout.addWidget(empty_lbl)
        else:
            for record in pending_groups:
                card = self.create_publication_card(record, is_pending=True)
                self.pending_layout.addWidget(card)

        self.pending_layout.addStretch(1)

        # Populate Reviewed Tab
        if not reviewed_groups:
            empty_reviewed_lbl = QLabel("No reviewed publications yet.")
            empty_reviewed_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            empty_reviewed_lbl.setStyleSheet("color: #94a3b8; font-size: 14px; margin-top: 50px;")
            self.reviewed_layout.addWidget(empty_reviewed_lbl)
        else:
            for record in reviewed_groups:
                card = self.create_publication_card(record, is_pending=False)
                self.reviewed_layout.addWidget(card)

        self.reviewed_layout.addStretch(1)

        self.tabs.setTabText(0, f"Pending Review ({len(pending_groups)})")
        self.tabs.setTabText(1, f"Reviewed ({len(reviewed_groups)})")

    def create_publication_card(self, record, is_pending=True):
        """Creates a sleek, compact UI card with a scrollable table for 4+ rows."""
        card = QFrame()
        card.setSizePolicy(card.sizePolicy().Policy.Expanding, card.sizePolicy().Policy.Maximum)
        card.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #e2e8f0;
                border-radius: 6px;
                margin-bottom: 8px;
            }
        """)
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(15, 12, 15, 12)
        card_layout.setSpacing(10)

        # Header Row: Date & PDF File Name
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(0, 0, 0, 0)

        schedule_date = record.get('publication_date')
        if isinstance(schedule_date, (datetime, date)):
            date_str = f"{schedule_date.strftime('%B %d')} Issues"
        elif schedule_date:
            try:
                dt = datetime.strptime(str(schedule_date), '%Y-%m-%d')
                date_str = f"{dt.strftime('%B %d')} Issues"
            except ValueError:
                date_str = f"{schedule_date} Issues"
        else:
            date_str = "N/A Issues"

        date_lbl = QLabel(f"<b>{date_str}</b>")
        date_lbl.setStyleSheet("color: #0b2545; font-size: 13px; border: none;")
        header_layout.addWidget(date_lbl)

        header_layout.addStretch()

        file_name = record.get('file_name') or 'No PDF attached'
        path_lbl = QLabel(f"PDF File: {file_name}")
        path_lbl.setStyleSheet("color: #0284c7; font-size: 11px; font-style: italic; border: none;")
        header_layout.addWidget(path_lbl)

        card_layout.addLayout(header_layout)

        # Main Content Row: Scrollable Table + Actions Side-by-Side
        content_layout = QHBoxLayout()
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(15)

        # Inner Table Widget
        rows = record.get('rows', [])
        table = QTableWidget()
        table.setColumnCount(3)
        table.setHorizontalHeaderLabels(["Case No.", "Client", "Issue"])
        table.setRowCount(len(rows))
        table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        table.verticalHeader().setVisible(False)
        
        # Enable vertical scrollbar if rows exceed 3
        if len(rows) > 3:
            table.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        else:
            table.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        table.setStyleSheet("""
            QTableWidget {
                background-color: transparent;
                border: 1px solid #f1f2f6;
                border-radius: 4px;
                gridline-color: #f1f2f6;
            }
            QHeaderView::section {
                background-color: #f8fafc;
                color: #475569;
                font-weight: bold;
                font-size: 11px;
                padding: 6px;
                border: none;
                border-bottom: 1px solid #e2e8f0;
            }
            QTableWidgetItem {
                padding: 6px;
                color: #1e293b;
                border: none;
            }
        """)

        for row_idx, row_data in enumerate(rows):
            table.setItem(row_idx, 0, QTableWidgetItem(str(row_data.get('case_number', 'N/A'))))
            table.setItem(row_idx, 1, QTableWidgetItem(str(row_data.get('client_name', 'N/A'))))
            table.setItem(row_idx, 2, QTableWidgetItem(str(row_data.get('issue_number', 'N/A'))))

        # Adjusted height calculation so 3 rows fit comfortably without getting cut off
        row_height = 30
        header_height = 30
        display_rows = min(max(len(rows), 1), 3)
        total_height = header_height + (display_rows * row_height) + 8
        table.setFixedHeight(total_height)
        table.setMinimumHeight(total_height)
        table.setMaximumHeight(total_height)

        content_layout.addWidget(table, 1)

        # Action Buttons Layout
        btn_layout = QHBoxLayout()
        btn_layout.setAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignRight)
        btn_layout.setContentsMargins(0, 0, 0, 0)
        btn_layout.setSpacing(6)

        view_btn = QPushButton("View PDF")
        view_btn.setStyleSheet("background-color: #0b2545; color: white; padding: 6px 12px; border-radius: 4px; font-size: 12px; font-weight: bold;")
        view_btn.clicked.connect(lambda checked=False, r=record: self.open_document_file(r))
        btn_layout.addWidget(view_btn)

        if is_pending:
            approve_btn = QPushButton("Accept")
            approve_btn.setStyleSheet("background-color: #16a34a; color: white; padding: 6px 12px; border-radius: 4px; font-size: 12px; font-weight: bold;")
            approve_btn.clicked.connect(lambda checked=False, r=record: self.update_review_status(r, 'Approved'))

            reject_btn = QPushButton("Reject")
            reject_btn.setStyleSheet("background-color: #dc2626; color: white; padding: 6px 12px; border-radius: 4px; font-size: 12px; font-weight: bold;")
            reject_btn.clicked.connect(lambda checked=False, r=record: self.update_review_status(r, 'Rejected'))

            btn_layout.addWidget(approve_btn)
            btn_layout.addWidget(reject_btn)
        else:
            status_text = record.get('review_status', 'Approved')
            status_color = "#dc2626" if status_text.lower() == "rejected" else "#16a34a"
            status_lbl = QLabel(f"Status: <b style='color: {status_color};'>{status_text}</b>")
            status_lbl.setStyleSheet(f"color: {status_color}; font-size: 12px; margin-left: 8px; border: none;")
            btn_layout.addWidget(status_lbl)

        content_layout.addLayout(btn_layout)
        card_layout.addLayout(content_layout)

        return card

    def open_document_file(self, record):
        """Extracts stored PDF blob from DB and opens it locally using OS application."""
        pub_date = record.get('publication_date')
        pdf_data = db.get_monday_pdf_from_db(pub_date)
        
        if not pdf_data or not pdf_data.get('file_data'):
            QMessageBox.warning(self, "PDF Not Found", "The PDF file data could not be found in the database.")
            return

        try:
            file_name = pdf_data.get('file_name', 'publication.pdf')
            temp_path = os.path.join(tempfile.gettempdir(), file_name)
            
            with open(temp_path, 'wb') as f:
                f.write(pdf_data['file_data'])

            if platform.system() == 'Windows':
                os.startfile(temp_path)
            elif platform.system() == 'Darwin':  # macOS
                subprocess.call(('open', temp_path))
            else:  # Linux
                subprocess.call(('xdg-open', temp_path))
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to open PDF file: {str(e)}")

    def update_review_status(self, record, new_status):
        schedule_id = record.get('schedule_id')
        
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("Confirm Action")
        msg_box.setText(f"Are you sure you want to mark this scheduled publication PDF as {new_status}?")
        msg_box.setIcon(QMessageBox.Icon.Question)
        msg_box.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        msg_box.setStyleSheet("""
            QMessageBox {
                background-color: #ffffff;
            }
            QLabel {
                color: #0b2545;
                font-size: 13px;
            }
            QPushButton {
                background-color: #0b2545;
                color: white;
                padding: 6px 16px;
                border-radius: 4px;
                font-weight: bold;
                min-width: 70px;
            }
            QPushButton:hover {
                background-color: #133863;
            }
        """)
        
        confirm = msg_box.exec()
        if confirm == QMessageBox.StandardButton.Yes:
            success, msg = db.update_publication_schedule_status(schedule_id, new_status)
            if success:
                success_box = QMessageBox(self)
                success_box.setWindowTitle("Success")
                success_box.setText(f"Publication PDF has been {new_status.lower()}!")
                success_box.setIcon(QMessageBox.Icon.Information)
                success_box.setStandardButtons(QMessageBox.StandardButton.Ok)
                success_box.setStyleSheet("""
                    QMessageBox {
                        background-color: #ffffff;
                    }
                    QLabel {
                        color: #0b2545;
                        font-size: 13px;
                    }
                    QPushButton {
                        background-color: #0b2545;
                        color: white;
                        padding: 6px 16px;
                        border-radius: 4px;
                        font-weight: bold;
                        min-width: 70px;
                    }
                    QPushButton:hover {
                        background-color: #133863;
                    }
                """)
                success_box.exec()
                self.load_pending_data()
            else:
                QMessageBox.critical(self, "Error", msg)
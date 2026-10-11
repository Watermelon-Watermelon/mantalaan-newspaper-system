# Path: views/publication_status_view.py
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QTableWidget, QTableWidgetItem, QHeaderView, QComboBox, QDateEdit, QPushButton
)
from PyQt6.QtCore import Qt, QDate
from PyQt6.QtGui import QFont, QColor
import db

class PublicationStatusView(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.load_publications()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(25, 20, 25, 20)
        layout.setSpacing(15)

        title = QLabel("Publication Status")
        title.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        title.setStyleSheet("color: #0b2545;")  
        
        subtitle = QLabel("Track the status of all publications.")
        subtitle.setStyleSheet("color: #64748b; font-size: 13px;")

        layout.addWidget(title)
        layout.addWidget(subtitle)

        # Filters Bar
        filter_hbox = QHBoxLayout()
        filter_hbox.setSpacing(10)

        self.status_combo = QComboBox()
        self.status_combo.addItems(["All Status", "In Progress", "Published", "Pending"])
        self.status_combo.setFixedWidth(130)
        self.status_combo.setStyleSheet("""
            QComboBox {
                padding: 6px; 
                background-color: white; 
                border: 1px solid #cbd5e1; 
                border-radius: 4px; 
                color: #1e293b;
            }
            QComboBox::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 20px;
                border-left-width: 0px;
            }
            QComboBox QAbstractItemView {
                background-color: white;
                color: #1e293b;
                selection-background-color: #0284c7;
                selection-color: white;
            }
        """)

        date_edit_style = """
            QDateEdit {
                padding: 6px;
                background-color: white;
                border: 1px solid #cbd5e1;
                border-radius: 4px;
                color: #1e293b;
            }
            QDateEdit::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 20px;
                border-left: 1px solid #cbd5e1;
                border-top-right-radius: 4px;
                border-bottom-right-radius: 4px;
                background: #f8fafc;
            }
            QCalendarWidget QWidget {
                background-color: white;
                color: #1e293b;
            }
            QCalendarWidget QToolButton {
                color: #0b2545;
                font-weight: bold;
                background-color: #f8fafc;
                margin: 2px;
                border-radius: 4px;
            }
            QCalendarWidget QToolButton:hover {
                background-color: #e2e8f0;
            }
            QCalendarWidget QMenu {
                background-color: white;
                color: #1e293b;
            }
            QCalendarWidget QSpinBox {
                color: #1e293b;
                background-color: white;
            }
            QCalendarWidget QAbstractItemView:enabled {
                color: #1e293b;
                background-color: white;
                selection-background-color: #0284c7;
                selection-color: white;
            }
            QCalendarWidget QAbstractItemView:disabled {
                color: #cbd5e1;
            }
        """

        self.start_date = QDateEdit(QDate.currentDate().addDays(-30))
        self.start_date.setCalendarPopup(True)
        self.start_date.setStyleSheet(date_edit_style)

        self.end_date = QDateEdit(QDate.currentDate().addDays(30))
        self.end_date.setCalendarPopup(True)
        self.end_date.setStyleSheet(date_edit_style)

        filter_btn = QPushButton("Filter")
        filter_btn.setStyleSheet("background-color: #0b2545; color: white; padding: 6px 16px; border-radius: 4px; font-weight: bold;")
        filter_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        filter_btn.clicked.connect(self.load_publications)

        filter_hbox.addWidget(self.status_combo)
        filter_hbox.addWidget(self.start_date)
        filter_hbox.addWidget(self.end_date)
        filter_hbox.addWidget(filter_btn)
        filter_hbox.addStretch()

        layout.addLayout(filter_hbox)

        # Table with Scheduled Date Column
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["Case No.", "Client Name", "Type", "Issues", "Scheduled Date", "Status"])
        
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        
        self.table.verticalHeader().setVisible(False)
        self.table.setShowGrid(False)
        self.table.setStyleSheet("""
            QTableWidget { 
                background-color: #ffffff; 
                border: 1px solid #e2e8f0; 
                border-radius: 8px; 
                color: #1e293b; 
                gridline-color: transparent;
            }
            QHeaderView::section { 
                background-color: #f8fafc; 
                font-weight: bold; 
                border: none; 
                border-bottom: 2px solid #e2e8f0;
                padding: 10px; 
                color: #0b2545; 
                font-size: 12px; 
            }
            QTableWidget::item { 
                padding: 10px; 
                border-bottom: 1px solid #f1f5f9; 
            }
        """)

        layout.addWidget(self.table)

    def load_publications(self):
        selected_status = self.status_combo.currentText()
        
        pubs = db.get_all_publications() or []
        
        # Filter publications based on selected status
        filtered_pubs = []
        for p in pubs:
            st = str(p.get('status', 'Pending'))
            if selected_status != "All Status" and st != selected_status:
                continue
            filtered_pubs.append(p)

        self.table.setRowCount(len(filtered_pubs))
        for row, p in enumerate(filtered_pubs):
            self.table.setItem(row, 0, QTableWidgetItem(str(p.get('case_number', 'N/A'))))
            self.table.setItem(row, 1, QTableWidgetItem(str(p.get('client_name', 'N/A'))))
            self.table.setItem(row, 2, QTableWidgetItem(str(p.get('publication_type', 'N/A'))))
            
            # Format issues like "3 of 3"
            current_issue = p.get('current_issue', 1)
            required_issues = p.get('required_issues', 1)
            issues_text = f"{current_issue} of {required_issues}"
            issue_item = QTableWidgetItem(issues_text)
            issue_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(row, 3, issue_item)

            # Scheduled Date formatted as "Oct 5 2026"
            raw_date = str(p.get('scheduled_date', '2026-10-05'))
            formatted_date_str = raw_date
            try:
                qdate = QDate.fromString(raw_date, "yyyy-MM-dd")
                if qdate.isValid():
                    formatted_date_str = qdate.toString("MMM d yyyy")  # e.g., "Oct 5 2026"
            except Exception:
                pass

            date_item = QTableWidgetItem(formatted_date_str)
            date_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(row, 4, date_item)
            
            # Status Badge
            st = str(p.get('status', 'Pending'))
            status_item = QTableWidgetItem(st)
            status_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            
            if st == "Published":
                status_item.setBackground(QColor("#dcfce7"))
                status_item.setForeground(QColor("#16a34a"))
            elif st == "In Progress":
                status_item.setBackground(QColor("#fef3c7"))
                status_item.setForeground(QColor("#d97706"))
            else:
                status_item.setBackground(QColor("#e0f2fe"))
                status_item.setForeground(QColor("#0284c7"))
            
            self.table.setItem(row, 5, status_item)
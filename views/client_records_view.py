# Path: views/client_records_view.py
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QLineEdit, QTableWidget, QTableWidgetItem, QHeaderView
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QColor
import db

class ClientRecordsView(QWidget):
    def __init__(self, main_window=None):
        super().__init__()
        self.main_window = main_window
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(25, 20, 25, 20)
        layout.setSpacing(15)

        title = QLabel("Clients")
        title.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        title.setStyleSheet("color: #0b2545;")
        
        subtitle = QLabel("View and manage client information.")
        subtitle.setStyleSheet("color: #64748b; font-size: 13px;")

        layout.addWidget(title)
        layout.addWidget(subtitle)

        # Search Bar Header
        search_hbox = QHBoxLayout()
        search_input = QLineEdit()
        search_input.setPlaceholderText("Search client name, email, or contact...")
        search_input.setStyleSheet("padding: 8px; border: 1px solid #cbd5e1; border-radius: 4px; background-color: white;")
        search_hbox.addWidget(search_input)

        layout.addLayout(search_hbox)

        # Client Records Table Setup (No Actions column)
        table = QTableWidget()
        table.setColumnCount(6)
        table.setHorizontalHeaderLabels(["No.", "Client Name", "Contact Number", "Email", "Publications", "Status"])

        table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        table.verticalHeader().setVisible(False)
        table.setShowGrid(False)
        table.setStyleSheet("""
            QTableWidget { 
                background-color: #ffffff; 
                border: 1px solid #e2e8f0; 
                border-radius: 6px; 
                color: #1e293b;
            }
            QHeaderView::section { 
                background-color: #f8fafc; 
                font-weight: bold; 
                border: none; 
                padding: 8px; 
                color: #64748b; 
                font-size: 11px;
            }
            QTableWidget::item {
                padding: 8px;
                border-bottom: 1px solid #f1f5f9;
            }
        """)

        db_clients = db.get_all_clients()
        if db_clients:
            table.setRowCount(len(db_clients))
            for row, c in enumerate(db_clients):
                table.setItem(row, 0, QTableWidgetItem(str(row + 1)))
                table.setItem(row, 1, QTableWidgetItem(str(c.get('client_name', ''))))
                table.setItem(row, 2, QTableWidgetItem(str(c.get('contact_number', ''))))
                table.setItem(row, 3, QTableWidgetItem(str(c.get('email', 'N/A'))))
                table.setItem(row, 4, QTableWidgetItem(str(c.get('publication_count', '0'))))
                
                status_str = str(c.get('status', 'Active'))
                st_item = QTableWidgetItem(status_str)
                st_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                if status_str.lower() == "active":
                    st_item.setBackground(QColor("#dcfce7"))
                    st_item.setForeground(QColor("#16a34a"))
                else:
                    st_item.setBackground(QColor("#f1f5f9"))
                    st_item.setForeground(QColor("#64748b"))
                table.setItem(row, 5, st_item)
        else:
            table.setRowCount(0)

        layout.addWidget(table)
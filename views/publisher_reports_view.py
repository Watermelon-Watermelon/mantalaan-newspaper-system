# Path: views/publisher_reports_view.py
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QFrame, QTableWidget, QTableWidgetItem, QHeaderView
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from views.reports_view import ReportsView, ReportPreviewDialog
import db

class PublisherReportsView(QWidget):
    def __init__(self):
        super().__init__()
        self.current_report_type = "Publication Report"
        self.init_ui()
        self.load_report_archive(self.current_report_type)

    def init_ui(self):
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)

        # Left Sidebar: Publisher Reports Navigation Frame
        sidebar_frame = QFrame()
        sidebar_frame.setFixedWidth(240)
        sidebar_frame.setStyleSheet("""
            QFrame {
                background-color: #ffffff;
                border: 1px solid #e2e8f0;
                border-radius: 8px;
            }
        """)
        sidebar_layout = QVBoxLayout(sidebar_frame)
        sidebar_layout.setContentsMargins(12, 15, 12, 15)
        sidebar_layout.setSpacing(8)

        lbl_title = QLabel("Publisher Reports")
        lbl_title.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        lbl_title.setStyleSheet("color: #0f172a; border: none; background: transparent; padding-bottom: 5px;")
        sidebar_layout.addWidget(lbl_title)

        # Report navigation buttons
        self.nav_buttons = {}
        report_types = [
            ("Publication Report", "Publication Report"),
            ("Client Report", "Client Summary Report"),
            ("Payment Report", "Payment Report"),
            ("Release Report", "Releases Report")
        ]

        for display_name, r_type in report_types:
            btn = QPushButton(display_name)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setStyleSheet("""
                QPushButton {
                    text-align: left;
                    padding: 10px 14px;
                    border: none;
                    border-radius: 6px;
                    font-size: 13px;
                    font-weight: bold;
                    color: #475569;
                    background-color: transparent;
                }
                QPushButton:hover {
                    background-color: #f1f5f9;
                    color: #0f172a;
                }
                QPushButton[active="true"] {
                    background-color: #0b2545;
                    color: #ffffff;
                }
            """)
            btn.setProperty("active", "false")
            btn.clicked.connect(lambda checked, t=r_type, b=btn: self.switch_report(t, b))
            sidebar_layout.addWidget(btn)
            self.nav_buttons[r_type] = btn

        sidebar_layout.addStretch()
        main_layout.addWidget(sidebar_frame)

        # Right Content Area: Report Archive Table List
        content_frame = QFrame()
        content_frame.setStyleSheet("""
            QFrame {
                background-color: #ffffff;
                border: 1px solid #e2e8f0;
                border-radius: 8px;
            }
        """)
        content_layout = QVBoxLayout(content_frame)
        content_layout.setContentsMargins(20, 20, 20, 20)
        content_layout.setSpacing(15)

        self.header_label = QLabel("Publication Report")
        self.header_label.setFont(QFont("Arial", 15, QFont.Weight.Bold))
        self.header_label.setStyleSheet("color: #0b2545; border: none; background: transparent;")
        content_layout.addWidget(self.header_label)

        # Archive Table for the selected report type
        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["Report Name", "Date Generated", "Action"])
        self.table.setStyleSheet("""
            QTableWidget {
                border: 1px solid #e2e8f0;
                gridline-color: #f1f5f9;
                selection-background-color: #f4f6f9;
                selection-color: #2c3e50;
                background-color: #ffffff;
            }
            QHeaderView::section {
                background-color: #f8fafc;
                color: #0b2545;
                font-weight: bold;
                padding: 10px;
                border: none;
                border-bottom: 2px solid #e2e8f0;
            }
            QTableWidget::item {
                padding: 8px;
                color: #1e293b;
                border-bottom: 1px solid #f1f5f9;
            }
        """)

        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Fixed)
        self.table.setColumnWidth(2, 110) # Fixed comfortable width for the View button

        self.table.verticalHeader().setVisible(False)
        self.table.setAlternatingRowColors(True)
        content_layout.addWidget(self.table)

        main_layout.addWidget(content_frame, stretch=1)

        # Set default active button
        if "Publication Report" in self.nav_buttons:
            self.switch_report("Publication Report", self.nav_buttons["Publication Report"])

    def switch_report(self, report_type, clicked_btn):
        self.current_report_type = report_type
        self.header_label.setText(clicked_btn.text())

        # Update button active states
        for r_type, btn in self.nav_buttons.items():
            if r_type == report_type:
                btn.setProperty("active", "true")
            else:
                btn.setProperty("active", "false")
            btn.style().unpolish(btn)
            btn.style().polish(btn)

        self.load_report_archive(report_type)

    def load_report_archive(self, report_type):
        logs = []
        try:
            conn = db.get_connection()
            cursor = conn.cursor()
            query = """
                SELECT report_id, report_name, report_type, date_generated, start_date, end_date
                FROM report_log 
                WHERE report_type = %s
                ORDER BY date_generated DESC
            """
            cursor.execute(query, (report_type,))
            rows = cursor.fetchall()

            for row in rows:
                if isinstance(row, dict):
                    logs.append({
                        "id": row["report_id"], "name": row["report_name"],
                        "type": row["report_type"], "date_generated": str(row["date_generated"]),
                        "start_date": str(row["start_date"]), "end_date": str(row["end_date"])
                    })
                else:
                    logs.append({
                        "id": row[0], "name": row[1], "type": row[2],
                        "date_generated": str(row[3]), "start_date": str(row[4]), "end_date": str(row[5])
                    })
            cursor.close()
            conn.close()
        except Exception as e:
            print("Failed to fetch report logs:", e)

        self.table.setRowCount(0)

        for item in logs:
            row = self.table.rowCount()
            self.table.insertRow(row)
            self.table.setRowHeight(row, 48)

            name_item = QTableWidgetItem(item["name"])
            date_item = QTableWidgetItem(item["date_generated"])
            date_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

            self.table.setItem(0 if False else row, 0, name_item)
            self.table.setItem(row, 1, date_item)

            # Action widget with a well-sized, readable View button
            action_widget = QWidget()
            action_layout = QHBoxLayout(action_widget)
            action_layout.setContentsMargins(10, 4, 10, 4)
            action_layout.setSpacing(0)
            action_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

            view_btn = QPushButton("View")
            view_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            view_btn.setMinimumWidth(80)
            view_btn.setStyleSheet("""
                QPushButton { 
                    background-color: #0b2545; 
                    color: #ffffff; 
                    border: none; 
                    border-radius: 4px; 
                    padding: 6px 14px; 
                    font-size: 13px; 
                    font-weight: bold; 
                }
                QPushButton:hover { 
                    background-color: #133863; 
                }
            """)
            view_btn.clicked.connect(lambda checked, r=item: self.view_report_details(r))
            action_layout.addWidget(view_btn)

            self.table.setCellWidget(row, 2, action_widget)

    def view_report_details(self, report_item):
        temp_view = ReportsView()
        headers, rows = temp_view.fetch_report_data(
            report_item["type"], 
            report_item["start_date"], 
            report_item["end_date"]
        )
        date_range_str = f"{report_item['start_date']} — {report_item['end_date']}"
        dialog = ReportPreviewDialog(
            self, 
            report_title=report_item["type"], 
            date_range_str=date_range_str, 
            headers=headers, 
            rows=rows
        )
        dialog.exec()
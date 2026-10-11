# Path: views/reports_view.py
import sys
import os
import csv
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QPushButton, QTableWidget, QTableWidgetItem, QHeaderView, 
    QFrame, QComboBox, QDateEdit, QFileDialog, QMessageBox, QDialog
)
from PyQt6.QtCore import Qt, QDate
from PyQt6.QtGui import QFont

import db

def show_alert(parent, title, message, icon=QMessageBox.Icon.Information):
    msg = QMessageBox(parent)
    msg.setIcon(icon)
    msg.setWindowTitle(title)
    msg.setText(message)
    msg.setStyleSheet("""
        QMessageBox { background-color: #ffffff; }
        QLabel { color: #2c3e50; font-size: 13px; background: transparent; border: none; }
        QPushButton {
            background-color: #0b2545; color: white; border: none;
            border-radius: 4px; padding: 6px 18px; font-weight: bold;
        }
        QPushButton:hover { background-color: #1a5b9e; }
    """)
    return msg.exec()


class ReportPreviewDialog(QDialog):
    """Modal dialog to preview dynamic tabular report data with date range subtitle."""
    def __init__(self, parent=None, report_title="Report Preview", date_range_str="", headers=None, rows=None):
        super().__init__(parent)
        self.setWindowTitle(report_title)
        self.resize(780, 520)
        self.setStyleSheet("QDialog { background-color: #ffffff; }")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        header_layout = QHBoxLayout()
        
        title_lbl = QLabel(report_title)
        title_lbl.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        title_lbl.setStyleSheet("color: #0b2545; background: transparent; border: none;")
        header_layout.addWidget(title_lbl)

        header_layout.addStretch()

        if date_range_str:
            date_lbl = QLabel(f"Date Range: {date_range_str}")
            date_lbl.setFont(QFont("Arial", 11, QFont.Weight.Bold))
            date_lbl.setStyleSheet("color: #495057; background: #f8f9fa; border: 1px solid #ced4da; border-radius: 4px; padding: 5px 10px;")
            header_layout.addWidget(date_lbl)

        layout.addLayout(header_layout)

        table = QTableWidget()
        headers = headers or []
        rows = rows or []

        table.setColumnCount(len(headers))
        table.setHorizontalHeaderLabels(headers)
        table.setRowCount(len(rows))

        table.setStyleSheet("""
            QTableWidget {
                border: 1px solid #e0e0e0;
                gridline-color: #f0f0f0;
                color: #2c3e50;
                background-color: #ffffff;
            }
            QHeaderView::section {
                background-color: #f8f9fa;
                color: #0b2545;
                font-weight: bold;
                padding: 8px;
                border: none;
                border-bottom: 2px solid #e0e0e0;
            }
        """)

        header = table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        table.verticalHeader().setVisible(False)

        for r_idx, row in enumerate(rows):
            for c_idx, val in enumerate(row):
                item = QTableWidgetItem(str(val if val is not None else ""))
                table.setItem(r_idx, c_idx, item)

        layout.addWidget(table)

        close_btn = QPushButton("Close")
        close_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: #0b2545; color: white; border-radius: 5px;
                padding: 8px 20px; font-weight: bold; border: none;
            }
            QPushButton:hover { background-color: #1a5b9e; }
        """)
        close_btn.clicked.connect(self.accept)

        btn_box = QHBoxLayout()
        btn_box.addStretch()
        btn_box.addWidget(close_btn)
        layout.addLayout(btn_box)


class ReportsView(QWidget):
    def __init__(self, preset_report_type=None, preset_start_date=None, preset_end_date=None, parent=None):
        super().__init__(parent)
        self.preset_report_type = preset_report_type
        self.preset_start_date = preset_start_date
        self.preset_end_date = preset_end_date
        
        self.init_ui()
        self.populate_reports_table()

        if self.preset_report_type:
            idx = self.report_type_combo.findText(self.preset_report_type)
            if idx >= 0:
                self.report_type_combo.setCurrentIndex(idx)
        if self.preset_start_date:
            self.start_date_edit.setDate(QDate.fromString(self.preset_start_date, "yyyy-MM-dd"))
        if self.preset_end_date:
            self.end_date_edit.setDate(QDate.fromString(self.preset_end_date, "yyyy-MM-dd"))

    def init_ui(self):
        self.setStyleSheet("""
            ReportsView QLabel {
                color: #0b2545;
                font-weight: bold;
                font-size: 13px;
                background-color: transparent;
                border: none;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(25, 25, 25, 25)
        layout.setSpacing(20)

        # Page Header
        title = QLabel("Reports Management")
        title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        title.setStyleSheet("color: #0b2545; background: transparent; border: none;")
        layout.addWidget(title)

        # Filter Frame
        filter_card = QFrame()
        filter_card.setObjectName("filterCard")
        filter_card.setStyleSheet("""
            QFrame#filterCard { 
                background-color: #ffffff; 
                border-radius: 8px; 
                border: 1px solid #e0e0e0; 
            }
            QFrame#filterCard QLabel {
                background-color: transparent;
                border: none;
            }
        """)
        
        filter_layout = QVBoxLayout(filter_card)
        filter_layout.setContentsMargins(20, 20, 20, 20)

        inputs_layout = QHBoxLayout()
        inputs_layout.setSpacing(15)

        input_style = """
            QComboBox, QDateEdit {
                padding: 8px 10px;
                border: 1px solid #ced4da;
                border-radius: 5px;
                background-color: #ffffff;
                color: #212529 !important;
                font-size: 13px;
            }
            QComboBox:focus, QDateEdit:focus {
                border: 1px solid #0b2545;
            }
        """

        calendar_style = """
            QCalendarWidget { background-color: #ffffff; }
            QCalendarWidget QWidget#qt_calendar_navigationbar { background-color: #f8f9fa; border-bottom: 1px solid #e0e0e0; }
            QCalendarWidget QToolButton { color: #0b2545; background-color: transparent; font-weight: bold; border: none; margin: 2px; }
            QCalendarWidget QToolButton:hover { background-color: #e9ecef; border-radius: 4px; }
            QCalendarWidget QMenu { background-color: #ffffff; color: #0b2545; }
            QCalendarWidget QSpinBox { color: #0b2545; background-color: #ffffff; }
            QCalendarWidget QAbstractItemView:enabled { color: #212529; background-color: #ffffff; selection-background-color: #0b2545; selection-color: #ffffff; }
            QCalendarWidget QAbstractItemView:disabled { color: #adb5bd; }
        """

        # Column 1: Report Type
        type_col = QVBoxLayout()
        type_col.setSpacing(6)
        type_lbl = QLabel("Report Type")
        self.report_type_combo = QComboBox()
        self.report_type_combo.addItems([
            "Publication Report",
            "Payment Report",
            "Client Summary Report",
            "Releases Report"
        ])
        self.report_type_combo.setStyleSheet(input_style)
        type_col.addWidget(type_lbl)
        type_col.addWidget(self.report_type_combo)

        # Column 2: Date Range
        date_col = QVBoxLayout()
        date_col.setSpacing(6)
        date_lbl = QLabel("Date Range")

        date_range_layout = QHBoxLayout()
        date_range_layout.setSpacing(10)

        self.start_date_edit = QDateEdit()
        self.start_date_edit.setCalendarPopup(True)
        self.start_date_edit.setDate(QDate(2026, 9, 1))
        self.start_date_edit.setStyleSheet(input_style)
        self.start_date_edit.calendarWidget().setStyleSheet(calendar_style)

        dash_lbl = QLabel("—")
        dash_lbl.setStyleSheet("color: #6c757d; font-size: 14px; background: transparent; border: none;")

        self.end_date_edit = QDateEdit()
        self.end_date_edit.setCalendarPopup(True)
        self.end_date_edit.setDate(QDate.currentDate())
        self.end_date_edit.setStyleSheet(input_style)
        self.end_date_edit.calendarWidget().setStyleSheet(calendar_style)

        date_range_layout.addWidget(self.start_date_edit)
        date_range_layout.addWidget(dash_lbl)
        date_range_layout.addWidget(self.end_date_edit)

        date_col.addWidget(date_lbl)
        date_col.addLayout(date_range_layout)

        # Column 3: Action Button
        btn_col = QVBoxLayout()
        btn_col.setSpacing(6)
        dummy_lbl = QLabel("")
        dummy_lbl.setStyleSheet("background: transparent; border: none;")
        
        generate_btn = QPushButton("Generate Report")
        generate_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        generate_btn.setStyleSheet("""
            QPushButton {
                background-color: #0b2545; color: #ffffff;
                padding: 9px 20px; border-radius: 5px; font-weight: bold; border: none;
            }
            QPushButton:hover { background-color: #1a5b9e; }
        """)
        generate_btn.clicked.connect(self.generate_report)

        btn_col.addWidget(dummy_lbl)
        btn_col.addWidget(generate_btn)

        inputs_layout.addLayout(type_col, stretch=2)
        inputs_layout.addLayout(date_col, stretch=3)
        inputs_layout.addLayout(btn_col, stretch=1)

        filter_layout.addLayout(inputs_layout)
        layout.addWidget(filter_card)

        # Generated Reports Table Frame
        sub_title = QLabel("Generated Reports Archive")
        sub_title.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        sub_title.setStyleSheet("color: #0b2545; margin-top: 10px; background: transparent; border: none;")
        layout.addWidget(sub_title)

        table_card = QFrame()
        table_card.setObjectName("tableCard")
        table_card.setStyleSheet("QFrame#tableCard { background-color: #ffffff; border-radius: 8px; border: 1px solid #e0e0e0; }")
        table_layout = QVBoxLayout(table_card)
        table_layout.setContentsMargins(15, 15, 15, 15)

        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["Report Name", "Date Generated", "Action"])

        self.table.setStyleSheet("""
            QTableWidget { border: none; gridline-color: #f0f0f0; selection-background-color: #f4f6f9; selection-color: #2c3e50; background-color: #ffffff; }
            QHeaderView::section { background-color: #ffffff; color: #2c3e50; font-weight: bold; padding: 10px; border: none; border-bottom: 2px solid #e0e0e0; }
            QTableWidget::item { padding: 8px; border-bottom: 1px solid #f0f0f0; color: #2c3e50; }
        """)

        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)

        self.table.verticalHeader().setVisible(False)
        self.table.setAlternatingRowColors(True)

        table_layout.addWidget(self.table)
        layout.addWidget(table_card)

    def fetch_report_logs_from_db(self):
        logs = []
        try:
            conn = db.get_connection()
            cursor = conn.cursor()
            
            if self.preset_report_type:
                query = """
                    SELECT report_id, report_name, report_type, date_generated, start_date, end_date
                    FROM report_log 
                    WHERE report_type = %s AND start_date >= %s AND end_date <= %s
                    ORDER BY date_generated DESC
                """
                cursor.execute(query, (self.preset_report_type, self.preset_start_date, self.preset_end_date))
            else:
                query = """
                    SELECT report_id, report_name, report_type, date_generated, start_date, end_date
                    FROM report_log 
                    ORDER BY date_generated DESC
                """
                cursor.execute(query)

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
            print("Failed to fetch report logs from DB:", e)

        return logs

    def populate_reports_table(self):
        reports = self.fetch_report_logs_from_db()
        self.table.setRowCount(0)

        for item in reports:
            row = self.table.rowCount()
            self.table.insertRow(row)
            self.table.setRowHeight(row, 42)

            name_item = QTableWidgetItem(item["name"])
            date_item = QTableWidgetItem(item["date_generated"])
            date_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

            self.table.setItem(row, 0, name_item)
            self.table.setItem(row, 1, date_item)

            action_widget = QWidget()
            action_layout = QHBoxLayout(action_widget)
            action_layout.setContentsMargins(5, 4, 5, 4)
            action_layout.setSpacing(8)
            action_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

            view_btn = QPushButton("View")
            view_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            view_btn.setStyleSheet("""
                QPushButton { background-color: #ffffff; color: #0b2545; border: 1px solid #ced4da; border-radius: 4px; padding: 4px 12px; font-size: 12px; font-weight: bold; }
                QPushButton:hover { background-color: #f1f3f5; }
            """)
            view_btn.clicked.connect(lambda checked, r=item: self.view_report_details(r))

            download_btn = QPushButton("Download")
            download_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            download_btn.setStyleSheet("""
                QPushButton { background-color: #0b2545; color: #ffffff; border: none; border-radius: 4px; padding: 4px 12px; font-size: 12px; font-weight: bold; }
                QPushButton:hover { background-color: #1a5b9e; }
            """)
            download_btn.clicked.connect(lambda checked, r=item: self.download_report_file(r))

            delete_btn = QPushButton("Delete")
            delete_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            delete_btn.setStyleSheet("""
                QPushButton { background-color: #dc3545; color: #ffffff; border: none; border-radius: 4px; padding: 4px 10px; font-size: 12px; font-weight: bold; }
                QPushButton:hover { background-color: #bb2d3b; }
            """)
            delete_btn.clicked.connect(lambda checked, r=item: self.delete_report_log(r["id"]))

            action_layout.addWidget(view_btn)
            action_layout.addWidget(download_btn)
            action_layout.addWidget(delete_btn)

            self.table.setCellWidget(row, 2, action_widget)

    def fetch_report_data(self, report_type, start_date, end_date):
        headers = []
        rows = []

        try:
            conn = db.get_connection()
            cursor = conn.cursor()

            if report_type == "Publication Report":
                headers = ["Case No.", "Client Name", "Type", "Date Received", "Status"]
                query = """
                    SELECT p.case_number, c.client_name, p.publication_type, p.date_received, p.status 
                    FROM publication p
                    LEFT JOIN client c ON p.client_id = c.client_id
                    WHERE p.date_received BETWEEN %s AND %s 
                    ORDER BY p.date_received DESC
                """
                cursor.execute(query, (start_date, end_date))
                raw_rows = cursor.fetchall()

            elif report_type == "Payment Report":
                headers = ["OR Number", "Client Name", "Amount", "Payment Date", "Method"]
                query = """
                    SELECT pay.or_number, c.client_name, pay.amount, pay.payment_date, pay.payment_method 
                    FROM payment pay
                    LEFT JOIN publication p ON pay.publication_id = p.publication_id
                    LEFT JOIN client c ON p.client_id = c.client_id
                    WHERE pay.payment_date BETWEEN %s AND %s 
                    ORDER BY pay.payment_date DESC
                """
                cursor.execute(query, (start_date, end_date))
                raw_rows = cursor.fetchall()

            elif report_type == "Client Summary Report":
                headers = ["Client Name", "Contact", "Email", "Status"]
                query = "SELECT client_name, contact_number, email, status FROM client ORDER BY client_name ASC"
                cursor.execute(query)
                raw_rows = cursor.fetchall()

            else:  # Releases Report
                headers = ["Client", "Release Date", "Released To", "Status"]
                query = """
                    SELECT client_name, release_date, released_to, status 
                    FROM release_record 
                    WHERE release_date BETWEEN %s AND %s 
                    ORDER BY release_date DESC
                """
                cursor.execute(query, (start_date, end_date))
                raw_rows = cursor.fetchall()

            for row in raw_rows:
                if isinstance(row, dict):
                    rows.append(list(row.values()))
                else:
                    rows.append(list(row))

            cursor.close()
            conn.close()

        except Exception as e:
            print(f"DB Fetch Error for {report_type}:", e)

        return headers, rows

    def generate_report(self):
        rep_type = self.report_type_combo.currentText()
        start_date = self.start_date_edit.date().toString("yyyy-MM-dd")
        end_date = self.end_date_edit.date().toString("yyyy-MM-dd")

        report_name = f"{rep_type} ({start_date} to {end_date})"

        try:
            conn = db.get_connection()
            cursor = conn.cursor()
            query = """
                INSERT INTO report_log (report_name, report_type, date_generated, start_date, end_date)
                VALUES (%s, %s, NOW(), %s, %s)
            """
            cursor.execute(query, (report_name, rep_type, start_date, end_date))
            conn.commit()
            cursor.close()
            conn.close()

            self.populate_reports_table()
            show_alert(self, "Success", f"'{report_name}' generated and saved to database!", QMessageBox.Icon.Information)

        except Exception as e:
            show_alert(self, "Database Error", f"Failed to save report log:\n{str(e)}", QMessageBox.Icon.Critical)

    def delete_report_log(self, report_id):
        reply = QMessageBox.question(
            self, "Confirm Delete", 
            "Are you sure you want to delete this report record?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            try:
                conn = db.get_connection()
                cursor = conn.cursor()
                cursor.execute("DELETE FROM report_log WHERE report_id = %s", (report_id,))
                conn.commit()
                cursor.close()
                conn.close()

                self.populate_reports_table()
                show_alert(self, "Deleted", "Report record removed successfully.", QMessageBox.Icon.Information)
            except Exception as e:
                show_alert(self, "Database Error", f"Failed to delete report log:\n{str(e)}", QMessageBox.Icon.Critical)

    def view_report_details(self, report_item):
        headers, rows = self.fetch_report_data(
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

    def download_report_file(self, report_item):
        headers, rows = self.fetch_report_data(
            report_item["type"], 
            report_item["start_date"], 
            report_item["end_date"]
        )

        safe_name = f"{report_item['type'].replace(' ', '_')}_{report_item['start_date']}_to_{report_item['end_date']}"
        file_path, _ = QFileDialog.getSaveFileName(
            self, 
            "Save Report", 
            f"{safe_name}.csv", 
            "CSV Files (*.csv);;Text Files (*.txt)"
        )

        if file_path:
            try:
                with open(file_path, mode="w", newline="", encoding="utf-8") as file:
                    writer = csv.writer(file)
                    writer.writerow(headers)
                    writer.writerows(rows)

                show_alert(self, "Download Complete", f"Report saved successfully to:\n{file_path}", QMessageBox.Icon.Information)
            except Exception as e:
                show_alert(self, "File Error", f"Failed to save file:\n{str(e)}", QMessageBox.Icon.Critical)
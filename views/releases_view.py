# Path: views/releases_view.py
import sys
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QPushButton, QTableWidget, QTableWidgetItem, QHeaderView, 
    QFrame, QDialog, QFormLayout, QComboBox, QDateEdit, QTextEdit, QMessageBox
)
from PyQt6.QtCore import Qt, QDate
from PyQt6.QtGui import QFont
from datetime import datetime
import db  # Database handler module


def show_alert(parent, title, message, icon=QMessageBox.Icon.Information, buttons=QMessageBox.StandardButton.Ok):
    """Custom styled alert popup to guarantee high-contrast, visible buttons."""
    msg = QMessageBox(parent)
    msg.setIcon(icon)
    msg.setWindowTitle(title)
    msg.setText(message)
    msg.setStandardButtons(buttons)
    msg.setStyleSheet("""
        QMessageBox { background-color: #ffffff; }
        QLabel { color: #2c3e50; font-size: 13px; background-color: transparent; }
        QPushButton {
            background-color: #0b2545 !important;
            color: #ffffff !important;
            border: none !important;
            border-radius: 4px;
            padding: 6px 18px;
            font-weight: bold;
            min-width: 65px;
            min-height: 24px;
        }
        QPushButton:hover { background-color: #1a5b9e !important; }
        QPushButton:pressed { background-color: #05162d !important; }
    """)
    return msg.exec()


class RecordReleaseDialog(QDialog):
    """Dialog to record a new release or edit an existing release selecting a publication case number."""
    def __init__(self, parent=None, record_data=None):
        super().__init__(parent)
        self.record_data = record_data
        self.setWindowTitle("Edit Release Record" if record_data else "Record New Release")
        self.setFixedSize(460, 420)
        self.setStyleSheet("QDialog { background-color: #f8f9fa; }")
        
        self.init_ui()
        self.load_publications()

        if self.record_data:
            self.populate_existing_data()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(25, 25, 25, 25)
        layout.setSpacing(15)

        form = QFormLayout()
        form.setSpacing(12)

        input_style = """
            QLineEdit, QComboBox, QDateEdit, QTextEdit {
                padding: 8px 10px;
                border: 1px solid #ced4da;
                border-radius: 5px;
                background-color: white;
                color: #212529;
                font-size: 13px;
            }
            QLineEdit:focus, QComboBox:focus, QDateEdit:focus, QTextEdit:focus {
                border: 1px solid #0b2545;
            }
        """

        self.publication_combo = QComboBox()
        self.publication_combo.setStyleSheet(input_style)

        self.release_date_input = QDateEdit()
        self.release_date_input.setCalendarPopup(True)
        self.release_date_input.setDate(QDate.currentDate())
        self.release_date_input.setStyleSheet(input_style)

        calendar_popup = self.release_date_input.calendarWidget()
        calendar_popup.setStyleSheet("""
            QCalendarWidget QAbstractItemView:enabled {
                color: #212529; background-color: #ffffff;
                selection-background-color: #0b2545; selection-color: #ffffff;
            }
            QCalendarWidget QWidget#qt_calendar_navigationbar { background-color: #0b2545; }
            QCalendarWidget QToolButton { color: #ffffff; background-color: transparent; font-weight: bold; border: none; margin: 2px; padding: 4px; }
            QCalendarWidget QToolButton:hover { background-color: #1a5b9e; border-radius: 4px; }
        """)

        self.released_to_combo = QComboBox()
        self.released_to_combo.addItems(["Client", "Authorized Representative", "Courier", "Other"])
        self.released_to_combo.setEditable(True)
        self.released_to_combo.setStyleSheet(input_style)

        self.status_combo = QComboBox()
        self.status_combo.addItems(["Released", "Pending Pickup", "Awaiting Payment", "Cancelled", "In Progress"])
        self.status_combo.setStyleSheet(input_style)

        self.remarks_input = QTextEdit()
        self.remarks_input.setPlaceholderText("Optional notes or tracking info...")
        self.remarks_input.setFixedHeight(60)
        self.remarks_input.setStyleSheet(input_style)

        def make_label(text):
            lbl = QLabel(text)
            lbl.setFont(QFont("Arial", 9, QFont.Weight.Bold))
            lbl.setStyleSheet("color: #0b2545;")
            return lbl

        form.addRow(make_label("Publication (Case No.):"), self.publication_combo)
        form.addRow(make_label("Release Date:"), self.release_date_input)
        form.addRow(make_label("Released To:"), self.released_to_combo)
        form.addRow(make_label("Status:"), self.status_combo)
        form.addRow(make_label("Remarks:"), self.remarks_input)

        layout.addLayout(form)
        layout.addStretch()

        btn_box = QHBoxLayout()
        btn_box.addStretch()

        cancel_btn = QPushButton("Cancel")
        cancel_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        cancel_btn.setStyleSheet("QPushButton { padding: 8px 18px; border: 1px solid #ced4da; border-radius: 5px; background-color: white; color: #495057; font-weight: bold; } QPushButton:hover { background-color: #f1f3f5; }")
        cancel_btn.clicked.connect(self.reject)

        save_btn = QPushButton("Update Record" if self.record_data else "Save Record")
        save_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        save_btn.setStyleSheet("QPushButton { background-color: #0b2545; color: #ffffff; padding: 8px 20px; border-radius: 5px; font-weight: bold; border: none; } QPushButton:hover { background-color: #1a5b9e; }")
        save_btn.clicked.connect(self.save_release)

        btn_box.addWidget(cancel_btn)
        btn_box.addWidget(save_btn)
        layout.addLayout(btn_box)

    def load_publications(self):
        try:
            conn = db.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("SELECT case_number, publication_type FROM publication ORDER BY publication_id DESC")
            rows = cursor.fetchall()

            self.publication_combo.clear()
            for row in rows:
                if isinstance(row, dict):
                    case_no = row.get("case_number", "")
                    pub_type = row.get("publication_type", "")
                else:
                    case_no = row[0]
                    pub_type = row[1] if len(row) > 1 else ""
                
                display_text = f"{case_no} — {pub_type}" if pub_type else str(case_no)
                self.publication_combo.addItem(display_text, userData=case_no)

            cursor.close()
            conn.close()
        except Exception as e:
            show_alert(self, "Database Error", f"Failed to fetch publications list:\n{str(e)}", QMessageBox.Icon.Warning)

    def populate_existing_data(self):
        existing_case = str(self.record_data.get("case_number", ""))
        for i in range(self.publication_combo.count()):
            if self.publication_combo.itemData(i) == existing_case or existing_case in self.publication_combo.itemText(i):
                self.publication_combo.setCurrentIndex(i)
                break

        r_date = str(self.record_data.get("release_date", ""))
        if r_date:
            qdate = QDate.fromString(r_date, "yyyy-MM-dd")
            if qdate.isValid():
                self.release_date_input.setDate(qdate)

        self.released_to_combo.setCurrentText(str(self.record_data.get("released_to", "Client")))
        self.status_combo.setCurrentText(str(self.record_data.get("status", "Released")))
        self.remarks_input.setPlainText(str(self.record_data.get("remarks", "")))

    def save_release(self):
        full_text = self.publication_combo.currentText().strip()
        case_number = full_text.split("—")[0].strip() if "—" in full_text else full_text
        
        release_date = self.release_date_input.date().toString("yyyy-MM-dd")
        released_to = self.released_to_combo.currentText().strip()
        status = self.status_combo.currentText()
        remarks = self.remarks_input.toPlainText().strip()

        if not case_number:
            show_alert(self, "Validation Error", "Please select a publication case number.", QMessageBox.Icon.Warning)
            return

        try:
            conn = db.get_connection()
            cursor = conn.cursor()

            if self.record_data:
                release_id = self.record_data.get("release_id")
                query = """
                    UPDATE release_record 
                    SET case_number = %s, release_date = %s, released_to = %s, status = %s, remarks = %s
                    WHERE release_id = %s
                """
                cursor.execute(query, (case_number, release_date, released_to, status, remarks, release_id))
                msg = "Release record updated successfully!"
            else:
                query = """
                    INSERT INTO release_record (case_number, release_date, released_to, status, remarks)
                    VALUES (%s, %s, %s, %s, %s)
                """
                cursor.execute(query, (case_number, release_date, released_to, status, remarks))
                msg = "Release recorded successfully!"

            conn.commit()
            cursor.close()
            conn.close()

            show_alert(self, "Success", msg, QMessageBox.Icon.Information)
            self.accept()
        except Exception as e:
            show_alert(self, "Database Error", f"Failed to save release record:\n{str(e)}", QMessageBox.Icon.Critical)


class ReleasesView(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.load_releases()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(25, 25, 25, 25)
        layout.setSpacing(20)

        header_layout = QHBoxLayout()
        title = QLabel("Releases")
        title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        title.setStyleSheet("color: #0b2545;")

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search by case number, client, or recipient...")
        self.search_input.setFixedWidth(320)
        self.search_input.setStyleSheet("QLineEdit { padding: 8px 12px; border: 1px solid #dcdfe6; border-radius: 6px; background-color: white; color: #2c3e50; }")
        self.search_input.textChanged.connect(self.filter_releases)

        record_btn = QPushButton("+ Record Release")
        record_btn.setFont(QFont("Arial", 9, QFont.Weight.Bold))
        record_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        record_btn.setStyleSheet("QPushButton { background-color: #0b2545; color: white; padding: 9px 18px; border-radius: 6px; border: none; } QPushButton:hover { background-color: #1a5b9e; }")
        record_btn.clicked.connect(self.open_add_dialog)

        header_layout.addWidget(title)
        header_layout.addSpacing(20)
        header_layout.addWidget(self.search_input)
        header_layout.addStretch()
        header_layout.addWidget(record_btn)
        layout.addLayout(header_layout)

        card_frame = QFrame()
        card_frame.setStyleSheet("QFrame { background-color: white; border-radius: 8px; border: 1px solid #e0e0e0; }")
        card_layout = QVBoxLayout(card_frame)
        card_layout.setContentsMargins(15, 15, 15, 15)

        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels([
            "No.", "Case No.", "Client", "Release Date", "Released To", "Status", "Actions"
        ])
        self.table.setStyleSheet("QTableWidget { border: none; gridline-color: #f0f0f0; background-color: white; } QHeaderView::section { background-color: #ffffff; color: #2c3e50; font-weight: bold; padding: 10px; border-bottom: 2px solid #e0e0e0; } QTableWidget::item { padding: 8px 8px; color: #2c3e50; }")

        # Compact 'No.' column and give extra proportional stretch weight to Status & Client columns
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Interactive)

        self.table.setColumnWidth(0, 45)   # No. (made much shorter)
        self.table.setColumnWidth(1, 130)  # Case No.
        self.table.setColumnWidth(2, 190)  # Client
        self.table.setColumnWidth(3, 120)  # Release Date
        self.table.setColumnWidth(4, 130)  # Released To
        self.table.setColumnWidth(5, 175)  # Status (expanded to fit "Awaiting Payment" easily)
        self.table.setColumnWidth(6, 110)  # Actions

        # Make Status and Client stretch to fill any remaining container width
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.Stretch)

        self.table.verticalHeader().setVisible(False)
        self.table.verticalHeader().setDefaultSectionSize(55)
        card_layout.addWidget(self.table)
        layout.addWidget(card_frame)

    def load_releases(self):
        try:
            conn = db.get_connection()
            cursor = conn.cursor()

            query = """
                SELECT r.release_id, r.case_number, r.release_date, r.released_to, r.status, r.remarks,
                       COALESCE(c.client_name, '—') AS client_name
                FROM release_record r
                LEFT JOIN publication p ON r.case_number COLLATE utf8mb4_unicode_ci = p.case_number COLLATE utf8mb4_unicode_ci
                LEFT JOIN client c ON p.client_id = c.client_id
                ORDER BY r.release_id DESC
            """
            cursor.execute(query)
            records = cursor.fetchall()

            cursor.close()
            conn.close()

            self.populate_table(records)
        except Exception as e:
            try:
                conn = db.get_connection()
                cursor = conn.cursor()
                cursor.execute("SELECT release_id, case_number, release_date, released_to, status, remarks FROM release_record ORDER BY release_id DESC")
                records = cursor.fetchall()
                cursor.close()
                conn.close()
                self.populate_table(records)
            except Exception as inner_e:
                show_alert(self, "Database Error", f"Failed to load release records:\n{str(inner_e)}", QMessageBox.Icon.Critical)

    def populate_table(self, records):
        self.table.setRowCount(0)

        for index, row in enumerate(records):
            if isinstance(row, dict):
                r_id = row.get("release_id")
                case_number = str(row.get("case_number", ""))
                r_date_raw = str(row.get("release_date", ""))
                released_to = str(row.get("released_to", "Client"))
                status = str(row.get("status", "Released"))
                remarks = str(row.get("remarks", ""))
                client_name = str(row.get("client_name", "—"))
            else:
                r_id = row[0]
                case_number = str(row[1])
                r_date_raw = str(row[2])
                released_to = str(row[3])
                status = str(row[4])
                remarks = str(row[5]) if len(row) > 5 and row[5] else ""
                client_name = str(row[6]) if len(row) > 6 and row[6] else "—"

            formatted_date = r_date_raw
            try:
                dt = datetime.strptime(r_date_raw.split(" ")[0], "%Y-%m-%d")
                formatted_date = dt.strftime("%b %d, %Y")
            except Exception:
                pass

            row_position = self.table.rowCount()
            self.table.insertRow(row_position)

            no_item = QTableWidgetItem(str(index + 1))
            no_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

            case_item = QTableWidgetItem(case_number)
            case_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

            client_item = QTableWidgetItem(client_name)
            client_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

            date_item = QTableWidgetItem(formatted_date)
            date_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

            released_to_item = QTableWidgetItem(released_to)
            released_to_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

            # Status Pill
            status_widget = QWidget()
            status_widget.setStyleSheet("background: transparent;")
            status_layout = QHBoxLayout(status_widget)
            status_layout.setContentsMargins(4, 4, 4, 4)
            status_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

            status_label = QLabel(status)
            status_label.setFont(QFont("Arial", 9, QFont.Weight.Bold))
            status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            
            status_lower = status.lower()
            if status_lower == "released":
                bg_color, text_color = "#e6f4ea", "#137333"
            elif status_lower in ["pending pickup", "in progress", "awaiting payment"]:
                bg_color, text_color = "#fff3cd", "#b06000"
            elif status_lower == "cancelled":
                bg_color, text_color = "#fce8e6", "#c5221f"
            else:
                bg_color, text_color = "#e8eaed", "#3c4043"

            status_label.setStyleSheet(f"background-color: {bg_color}; color: {text_color}; border-radius: 12px; padding: 6px 14px;")
            status_layout.addWidget(status_label)

            self.table.setItem(row_position, 0, no_item)
            self.table.setItem(row_position, 1, case_item)
            self.table.setItem(row_position, 2, client_item)
            self.table.setItem(row_position, 3, date_item)
            self.table.setItem(row_position, 4, released_to_item)
            self.table.setCellWidget(row_position, 5, status_widget)

            # Actions
            actions_widget = QWidget()
            actions_widget.setStyleSheet("background: transparent;")
            actions_layout = QHBoxLayout(actions_widget)
            actions_layout.setContentsMargins(4, 4, 4, 4)
            actions_layout.setSpacing(12)
            actions_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

            record_dict = {
                "release_id": r_id,
                "case_number": case_number,
                "release_date": r_date_raw,
                "released_to": released_to,
                "status": status,
                "remarks": remarks
            }

            edit_btn = QPushButton("Edit")
            edit_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            edit_btn.setStyleSheet("QPushButton { color: #1a5b9e; border: none; background: transparent; font-weight: bold; padding: 4px 6px; } QPushButton:hover { text-decoration: underline; }")
            edit_btn.clicked.connect(lambda checked, d=record_dict: self.open_edit_dialog(d))

            delete_btn = QPushButton("Delete")
            delete_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            delete_btn.setStyleSheet("QPushButton { color: #e74c3c; border: none; background: transparent; font-weight: bold; padding: 4px 6px; } QPushButton:hover { text-decoration: underline; }")
            delete_btn.clicked.connect(lambda checked, id_val=r_id: self.delete_release(id_val))

            actions_layout.addWidget(edit_btn)
            actions_layout.addWidget(delete_btn)
            self.table.setCellWidget(row_position, 6, actions_widget)

    def filter_releases(self):
        search_text = self.search_input.text().lower()
        for row in range(self.table.rowCount()):
            case_no = self.table.item(row, 1).text().lower() if self.table.item(row, 1) else ""
            client_name = self.table.item(row, 2).text().lower() if self.table.item(row, 2) else ""
            released_to = self.table.item(row, 4).text().lower() if self.table.item(row, 4) else ""
            match = search_text in case_no or search_text in client_name or search_text in released_to
            self.table.setRowHidden(row, not match)

    def open_add_dialog(self):
        dialog = RecordReleaseDialog(self)
        if dialog.exec():
            self.load_releases()

    def open_edit_dialog(self, record_data):
        dialog = RecordReleaseDialog(self, record_data=record_data)
        if dialog.exec():
            self.load_releases()

    def delete_release(self, release_id):
        confirm = show_alert(
            self, "Confirm Delete", "Are you sure you want to delete this release record?", 
            QMessageBox.Icon.Question, QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if confirm == QMessageBox.StandardButton.Yes:
            try:
                conn = db.get_connection()
                cursor = conn.cursor()
                cursor.execute("DELETE FROM release_record WHERE release_id = %s", (release_id,))
                conn.commit()
                cursor.close()
                conn.close()
                self.load_releases()
            except Exception as e:
                show_alert(self, "Database Error", f"Failed to delete release record:\n{str(e)}", QMessageBox.Icon.Critical)
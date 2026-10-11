# Path: views/billing_payments_view.py
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, 
    QFrame, QTableWidget, QTableWidgetItem, QPushButton, 
    QHeaderView, QDialog, QLineEdit, QFormLayout, QMessageBox, QButtonGroup
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QColor, QDoubleValidator
from datetime import datetime

import db

class RecordPaymentDialog(QDialog):
    def __init__(self, parent=None, default_method="Cash", initial_data=None):
        super().__init__(parent)
        self.is_edit = initial_data is not None
        self.setWindowTitle("Edit Payment" if self.is_edit else "Record New Payment")
        self.resize(380, 260)
        self.selected_method = default_method
        self.initial_data = initial_data or {}
        self.init_ui()

    def init_ui(self):
        self.setStyleSheet("""
            QDialog {
                background-color: #f8fafc;
            }
            QLabel {
                color: #2c3e50;
                font-weight: 600;
                font-size: 13px;
            }
            QLineEdit, QComboBox {
                background-color: #ffffff;
                color: #2c3e50;
                border: 1px solid #cbd5e1;
                border-radius: 5px;
                padding: 6px 10px;
                font-size: 13px;
            }
            QLineEdit:focus, QComboBox:focus {
                border: 1.5px solid #0b2545;
            }
            QComboBox QAbstractItemView {
                background-color: #ffffff;
                color: #2c3e50;
                selection-background-color: #0b2545;
                selection-color: #ffffff;
                border: 1px solid #cbd5e1;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        form_layout = QFormLayout()
        form_layout.setSpacing(10)
        
        self.amount_input = QLineEdit()
        self.amount_input.setPlaceholderText("0.00")
        
        validator = QDoubleValidator(0.0, 999999999.0, 2, self)
        validator.setNotation(QDoubleValidator.Notation.StandardNotation)
        self.amount_input.setValidator(validator)
        
        self.method_combo = QComboBox()
        self.method_combo.addItems(["Cash", "Bank", "GCash", "Check"])
        
        initial_method = self.initial_data.get('payment_method', self.selected_method)
        self.method_combo.setCurrentText(initial_method)

        self.or_input = QLineEdit()
        self.or_input.setPlaceholderText("e.g. OR-00123")

        if self.is_edit:
            self.amount_input.setText(str(self.initial_data.get('amount', '')))
            self.or_input.setText(str(self.initial_data.get('or_number', '')))

        form_layout.addRow("Amount (₱):", self.amount_input)
        form_layout.addRow("Payment Method:", self.method_combo)
        form_layout.addRow("OR No.:", self.or_input)

        layout.addLayout(form_layout)

        btn_box = QHBoxLayout()
        save_btn = QPushButton("Update Payment" if self.is_edit else "Save Payment")
        save_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        save_btn.setStyleSheet("""
            QPushButton {
                background-color: #0b2545; 
                color: #ffffff; 
                padding: 8px 16px; 
                font-weight: bold; 
                border-radius: 4px;
                border: none;
            }
            QPushButton:hover {
                background-color: #1a5b9e;
            }
        """)
        save_btn.clicked.connect(self.accept)

        cancel_btn = QPushButton("Cancel")
        cancel_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #ffffff;
                color: #475569;
                padding: 8px 16px; 
                border: 1px solid #cbd5e1; 
                border-radius: 4px;
                font-weight: 500;
            }
            QPushButton:hover {
                background-color: #f1f5f9;
            }
        """)
        cancel_btn.clicked.connect(self.reject)

        btn_box.addWidget(cancel_btn)
        btn_box.addWidget(save_btn)
        layout.addLayout(btn_box)

    def get_data(self):
        return {
            "amount": self.amount_input.text().strip(),
            "method": self.method_combo.currentText(),
            "or_number": self.or_input.text().strip()
        }


class SetBillingTotalDialog(QDialog):
    def __init__(self, parent=None, current_total=3000.00):
        super().__init__(parent)
        self.setWindowTitle("Edit Billing Total Amount")
        self.resize(340, 180)
        self.current_total = current_total
        self.init_ui()

    def init_ui(self):
        self.setStyleSheet("""
            QDialog { background-color: #f8fafc; }
            QLabel { color: #2c3e50; font-weight: 600; font-size: 13px; }
            QLineEdit {
                background-color: #ffffff; color: #2c3e50; border: 1px solid #cbd5e1;
                border-radius: 5px; padding: 6px 10px; font-size: 13px;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        form_layout = QFormLayout()
        self.total_input = QLineEdit()
        self.total_input.setText(f"{self.current_total:.2f}")

        validator = QDoubleValidator(0.0, 999999999.0, 2, self)
        validator.setNotation(QDoubleValidator.Notation.StandardNotation)
        self.total_input.setValidator(validator)

        form_layout.addRow("Total Amount (₱):", self.total_input)
        layout.addLayout(form_layout)

        btn_box = QHBoxLayout()
        save_btn = QPushButton("Save Total")
        save_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        save_btn.setStyleSheet("""
            QPushButton {
                background-color: #0b2545; color: #ffffff; padding: 8px 16px; 
                font-weight: bold; border-radius: 4px; border: none;
            }
            QPushButton:hover { background-color: #1a5b9e; }
        """)
        save_btn.clicked.connect(self.accept)

        cancel_btn = QPushButton("Cancel")
        cancel_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #ffffff; color: #475569; padding: 8px 16px; 
                border: 1px solid #cbd5e1; border-radius: 4px; font-weight: 500;
            }
            QPushButton:hover { background-color: #f1f5f9; }
        """)
        cancel_btn.clicked.connect(self.reject)

        btn_box.addWidget(cancel_btn)
        btn_box.addWidget(save_btn)
        layout.addLayout(btn_box)

    def get_total(self):
        return self.total_input.text().strip()


class ViewAllPublicationsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("All Publications Payment Status")
        self.resize(750, 450)
        self.init_ui()
        self.load_data("All")

    def init_ui(self):
        self.setStyleSheet("""
            QDialog { background-color: #f8fafc; }
            QLabel { color: #2c3e50; font-weight: 600; font-size: 13px; }
            QComboBox {
                background-color: #ffffff; color: #2c3e50; border: 1px solid #cbd5e1;
                border-radius: 5px; padding: 5px 10px; font-size: 13px;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # Top filter bar
        filter_layout = QHBoxLayout()
        filter_lbl = QLabel("Filter by Payment Status:")
        self.filter_combo = QComboBox()
        self.filter_combo.addItems(["All", "Paid", "Unpaid / Not Paid"])
        self.filter_combo.currentIndexChanged.connect(self.on_filter_changed)

        filter_layout.addWidget(filter_lbl)
        filter_layout.addWidget(self.filter_combo)
        filter_layout.addStretch()
        layout.addLayout(filter_layout)

        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["Case No.", "Client Name", "Total Amount", "Amount Paid", "Balance", "Status"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.verticalHeader().setVisible(False)
        self.table.setAlternatingRowColors(True)
        self.table.setStyleSheet("""
            QTableWidget { 
                border: 1px solid #cbd5e1; 
                background-color: #ffffff; 
                color: #2c3e50;
                gridline-color: #f0f0f0;
                border-radius: 4px;
            }
            QHeaderView::section { 
                background-color: #f1f5f9; 
                color: #2c3e50;
                font-weight: bold; 
                border: 1px solid #cbd5e1; 
                padding: 6px; 
            }
            QTableWidget::item { color: #2c3e50; padding: 4px; }
        """)
        layout.addWidget(self.table)

        # Close button
        btn_box = QHBoxLayout()
        btn_box.addStretch()
        close_btn = QPushButton("Close")
        close_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: #0b2545; color: #ffffff; padding: 8px 20px; 
                font-weight: bold; border-radius: 4px; border: none;
            }
            QPushButton:hover { background-color: #1a5b9e; }
        """)
        close_btn.clicked.connect(self.accept)
        btn_box.addWidget(close_btn)
        layout.addLayout(btn_box)

    def load_data(self, filter_type):
        all_pubs = db.get_all_publications_with_billing_status()
        self.table.setRowCount(0)

        filtered_pubs = []
        for pub in all_pubs:
            balance = float(pub.get('balance', 0.0))
            is_paid = (balance == 0.0)

            if filter_type == "Paid" and not is_paid:
                continue
            if filter_type == "Unpaid / Not Paid" and is_paid:
                continue
            filtered_pubs.append(pub)

        for row_idx, pub in enumerate(filtered_pubs):
            self.table.insertRow(row_idx)

            case_str = str(pub.get('case_number', 'N/A'))
            client_str = str(pub.get('client_name', 'N/A'))
            total_str = f"₱ {float(pub.get('total_amount', 3000.0)):,.2f}"
            paid_str = f"₱ {float(pub.get('amount_paid', 0.0)):,.2f}"
            bal_str = f"₱ {float(pub.get('balance', 0.0)):,.2f}"
            status_str = "Paid" if float(pub.get('balance', 0.0)) == 0.0 else "Unpaid"

            item_case = QTableWidgetItem(case_str)
            item_client = QTableWidgetItem(client_str)
            item_total = QTableWidgetItem(total_str)
            item_paid = QTableWidgetItem(paid_str)
            item_bal = QTableWidgetItem(bal_str)
            item_status = QTableWidgetItem(status_str)

            if status_str == "Paid":
                item_status.setForeground(QColor("#16a34a")) # Green
            else:
                item_status.setForeground(QColor("#dc2626")) # Red

            for itm in (item_case, item_client, item_total, item_paid, item_bal):
                itm.setForeground(QColor("#2c3e50"))

            self.table.setItem(row_idx, 0, item_case)
            self.table.setItem(row_idx, 1, item_client)
            self.table.setItem(row_idx, 2, item_total)
            self.table.setItem(row_idx, 3, item_paid)
            self.table.setItem(row_idx, 4, item_bal)
            self.table.setItem(row_idx, 5, item_status)

    def on_filter_changed(self):
        selected_filter = self.filter_combo.currentText()
        self.load_data(selected_filter)


class BillingPaymentsView(QWidget):
    def __init__(self):
        super().__init__()
        self.publications_map = {}
        self.selected_payment_method = "Cash"
        self.current_billing_total = 3000.00
        self.init_ui()
        self.load_publication_combo()

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(25, 20, 25, 20)
        main_layout.setSpacing(20)

        # Top header layout with Title and View All button on the right
        header_layout = QHBoxLayout()
        title_label = QLabel("Billing & Payment")
        title_label.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        title_label.setStyleSheet("color: #2c3e50;")
        header_layout.addWidget(title_label)
        header_layout.addStretch()

        view_all_btn = QPushButton("View All Publications")
        view_all_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        view_all_btn.setStyleSheet("""
            QPushButton {
                background-color: #f1f5f9; color: #0b2545; border: 1px solid #cbd5e1;
                border-radius: 6px; padding: 6px 14px; font-weight: bold; font-size: 12px;
            }
            QPushButton:hover { background-color: #e2e8f0; }
        """)
        view_all_btn.clicked.connect(self.open_view_all_dialog)
        header_layout.addWidget(view_all_btn)

        main_layout.addLayout(header_layout)

        select_card = QFrame()
        select_card.setStyleSheet("background-color: white; border-radius: 8px; border: 1px solid #e0e0e0;")
        select_layout = QVBoxLayout(select_card)
        select_layout.setContentsMargins(15, 12, 15, 12)

        combo_lbl = QLabel("Select Publication")
        combo_lbl.setFont(QFont("Arial", 9, QFont.Weight.Bold))
        combo_lbl.setStyleSheet("color: #7f8c8d; border: none;")

        self.pub_combo = QComboBox()
        self.pub_combo.setStyleSheet("""
            QComboBox {
                padding: 8px; 
                border: 1px solid #bdc3c7; 
                border-radius: 4px; 
                background-color: #fafafa;
                color: #2c3e50;
                font-size: 13px;
            }
            QComboBox QAbstractItemView {
                background-color: #ffffff;
                color: #2c3e50;
                selection-background-color: #0b2545;
                selection-color: #ffffff;
                border: 1px solid #bdc3c7;
                outline: none;
            }
        """)
        self.pub_combo.currentIndexChanged.connect(self.on_publication_changed)

        select_layout.addWidget(combo_lbl)
        select_layout.addWidget(self.pub_combo)
        main_layout.addWidget(select_card)

        details_layout = QHBoxLayout()
        details_layout.setSpacing(20)

        billing_card = QFrame()
        billing_card.setStyleSheet("background-color: white; border-radius: 8px; border: 1px solid #e0e0e0;")
        billing_vbox = QVBoxLayout(billing_card)
        billing_vbox.setContentsMargins(20, 15, 20, 15)

        billing_header = QHBoxLayout()
        billing_title = QLabel("Billing Details")
        billing_title.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        billing_title.setStyleSheet("color: #2c3e50; border: none;")
        billing_header.addWidget(billing_title)
        billing_header.addStretch()

        edit_total_btn = QPushButton("Edit Total")
        edit_total_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        edit_total_btn.setStyleSheet("""
            QPushButton {
                background-color: #f1f5f9; color: #0b2545; border: 1px solid #cbd5e1;
                border-radius: 4px; padding: 4px 10px; font-weight: bold; font-size: 11px;
            }
            QPushButton:hover { background-color: #e2e8f0; }
        """)
        edit_total_btn.clicked.connect(self.open_edit_billing_total_dialog)
        billing_header.addWidget(edit_total_btn)

        billing_vbox.addLayout(billing_header)
        billing_vbox.addSpacing(10)

        self.lbl_total = QLabel("₱ 0.00")
        self.lbl_paid = QLabel("₱ 0.00")
        self.lbl_balance = QLabel("₱ 0.00")

        row_total = QHBoxLayout()
        lbl_t = QLabel("Total Amount")
        lbl_t.setFont(QFont("Arial", 10))
        lbl_t.setStyleSheet("color: #7f8c8d; border: none;")
        self.lbl_total.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        self.lbl_total.setStyleSheet("color: #2c3e50; border: none;")
        self.lbl_total.setAlignment(Qt.AlignmentFlag.AlignRight)
        row_total.addWidget(lbl_t)
        row_total.addStretch()
        row_total.addWidget(self.lbl_total)
        billing_vbox.addLayout(row_total)

        billing_vbox.addSpacing(10)

        row_paid = QHBoxLayout()
        lbl_p = QLabel("Amount Paid")
        lbl_p.setFont(QFont("Arial", 10))
        lbl_p.setStyleSheet("color: #7f8c8d; border: none;")
        self.lbl_paid.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        self.lbl_paid.setStyleSheet("color: #2c3e50; border: none;")
        self.lbl_paid.setAlignment(Qt.AlignmentFlag.AlignRight)
        row_paid.addWidget(lbl_p)
        row_paid.addStretch()
        row_paid.addWidget(self.lbl_paid)
        billing_vbox.addLayout(row_paid)

        billing_vbox.addStretch()

        row_balance = QHBoxLayout()
        lbl_b = QLabel("Balance")
        lbl_b.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        lbl_b.setStyleSheet("color: #7f8c8d; border: none;")
        self.lbl_balance.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        self.lbl_balance.setStyleSheet("color: #e74c3c; border: none;")
        self.lbl_balance.setAlignment(Qt.AlignmentFlag.AlignRight)
        row_balance.addWidget(lbl_b)
        row_balance.addStretch()
        row_balance.addWidget(self.lbl_balance)
        billing_vbox.addLayout(row_balance)

        details_layout.addWidget(billing_card, 1)

        history_card = QFrame()
        history_card.setStyleSheet("background-color: white; border-radius: 8px; border: 1px solid #e0e0e0;")
        history_vbox = QVBoxLayout(history_card)
        history_vbox.setContentsMargins(20, 15, 20, 15)

        history_title = QLabel("Payment History")
        history_title.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        history_title.setStyleSheet("color: #2c3e50; border: none; margin-bottom: 10px;")
        history_vbox.addWidget(history_title)

        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["Date", "Amount", "Method", "OR No.", "Actions"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.verticalHeader().setVisible(False)
        self.table.setAlternatingRowColors(True)
        self.table.setStyleSheet("""
            QTableWidget { 
                border: none; 
                background-color: #ffffff; 
                color: #2c3e50;
                gridline-color: #f0f0f0;
            }
            QHeaderView::section { 
                background-color: #f8f9fa; 
                color: #2c3e50;
                font-weight: bold; 
                border: 1px solid #e0e0e0; 
                padding: 6px; 
            }
            QTableWidget::item {
                color: #2c3e50;
            }
        """)
        history_vbox.addWidget(self.table)

        details_layout.addWidget(history_card, 2)
        main_layout.addLayout(details_layout)

        method_card = QFrame()
        method_card.setStyleSheet("background-color: white; border-radius: 8px; border: 1px solid #e0e0e0;")
        method_vbox = QVBoxLayout(method_card)
        method_vbox.setContentsMargins(20, 15, 20, 15)

        method_title = QLabel("Payment Method")
        method_title.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        method_title.setStyleSheet("color: #2c3e50; border: none; margin-bottom: 5px;")
        method_vbox.addWidget(method_title)

        methods_hbox = QHBoxLayout()
        methods_hbox.setSpacing(15)

        self.btn_group = QButtonGroup(self)
        self.method_buttons = {}

        methods = ["Cash", "Bank", "GCash", "Check"]
        for idx, m in enumerate(methods):
            btn = QPushButton(m)
            btn.setCheckable(True)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setStyleSheet("""
                QPushButton {
                    border: 1px solid #bdc3c7; 
                    border-radius: 6px; 
                    padding: 12px; 
                    background-color: #f8f9fa; 
                    font-weight: bold; 
                    color: #2c3e50;
                }
                QPushButton:checked {
                    border: 2px solid #1a5b9e; 
                    background-color: #eef5fc; 
                    color: #1a5b9e;
                }
            """)
            if idx == 0:
                btn.setChecked(True)
            self.btn_group.addButton(btn, idx)
            self.method_buttons[m] = btn
            methods_hbox.addWidget(btn)

        self.btn_group.idClicked.connect(self.on_method_selected)
        method_vbox.addLayout(methods_hbox)
        main_layout.addWidget(method_card)

        action_layout = QHBoxLayout()
        action_layout.addStretch()

        record_btn = QPushButton("Record Payment")
        record_btn.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        record_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        record_btn.setStyleSheet("""
            QPushButton {
                background-color: #0b2545; color: white; border: none; border-radius: 4px; padding: 10px 20px;
            }
            QPushButton:hover { background-color: #1a5b9e; }
        """)
        record_btn.clicked.connect(self.open_record_payment_dialog)
        action_layout.addWidget(record_btn)

        main_layout.addLayout(action_layout)

    def load_publication_combo(self):
        self.pub_combo.blockSignals(True)
        self.pub_combo.clear()
        self.publications_map.clear()

        publications = db.get_publications_for_billing()
        for pub in publications:
            display_text = f"{pub['case_number']} - {pub['client_name'] or 'N/A'}"
            self.pub_combo.addItem(display_text, pub['publication_id'])
            self.publications_map[pub['publication_id']] = pub

        self.pub_combo.blockSignals(False)

        if publications:
            self.load_billing_and_payments()
        else:
            self.lbl_total.setText("₱ 0.00")
            self.lbl_paid.setText("₱ 0.00")
            self.lbl_balance.setText("₱ 0.00")
            self.table.setRowCount(0)

    def get_selected_pub_id(self):
        return self.pub_combo.currentData()

    def on_publication_changed(self):
        self.load_billing_and_payments()

    def on_method_selected(self, btn_id):
        selected_btn = self.btn_group.button(btn_id)
        if selected_btn:
            self.selected_payment_method = selected_btn.text()

    def load_billing_and_payments(self):
        pub_id = self.get_selected_pub_id()
        if not pub_id:
            self.lbl_total.setText("₱ 0.00")
            self.lbl_paid.setText("₱ 0.00")
            self.lbl_balance.setText("₱ 0.00")
            self.table.setRowCount(0)
            return

        summary = db.get_billing_details_by_pub(pub_id)
        
        if not summary:
            total = 0.0
            paid = 0.0
            balance = 0.0
        else:
            total = float(summary.get('total_amount', 0.0) or 0.0)
            paid = float(summary.get('amount_paid', 0.0) or 0.0)
            balance = max(0.0, total - paid)

        self.current_billing_total = total
        self.lbl_total.setText(f"₱ {total:,.2f}")
        self.lbl_paid.setText(f"₱ {paid:,.2f}")
        self.lbl_balance.setText(f"₱ {balance:,.2f}")

        history = db.get_payment_history_by_pub(pub_id)
        self.table.setRowCount(0)

        for row_idx, item in enumerate(history):
            self.table.insertRow(row_idx)

            date_str = str(item['payment_date']) if item.get('payment_date') else "N/A"
            amount_str = f"₱ {float(item.get('amount', 0)):,.2f}"
            method_str = str(item.get('payment_method', 'N/A'))
            or_str = str(item.get('or_number', 'N/A'))

            item_date = QTableWidgetItem(date_str)
            item_amount = QTableWidgetItem(amount_str)
            item_method = QTableWidgetItem(method_str)
            item_or = QTableWidgetItem(or_str)

            dark_color = QColor("#2c3e50")
            for table_item in (item_date, item_amount, item_method, item_or):
                table_item.setForeground(dark_color)

            self.table.setItem(row_idx, 0, item_date)
            self.table.setItem(row_idx, 1, item_amount)
            self.table.setItem(row_idx, 2, item_method)
            self.table.setItem(row_idx, 3, item_or)

            action_widget = QWidget()
            action_layout = QHBoxLayout(action_widget)
            action_layout.setContentsMargins(4, 2, 4, 2)
            action_layout.setSpacing(6)

            edit_btn = QPushButton("Edit")
            edit_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            edit_btn.setStyleSheet("""
                QPushButton {
                    background-color: #e2e8f0; color: #1e293b; border: none;
                    border-radius: 3px; padding: 3px 8px; font-size: 11px; font-weight: bold;
                }
                QPushButton:hover { background-color: #cbd5e1; }
            """)
            edit_btn.clicked.connect(lambda _, p=item: self.open_edit_payment_dialog(p))

            del_btn = QPushButton("Delete")
            del_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            del_btn.setStyleSheet("""
                QPushButton {
                    background-color: #fee2e2; color: #991b1b; border: none;
                    border-radius: 3px; padding: 3px 8px; font-size: 11px; font-weight: bold;
                }
                QPushButton:hover { background-color: #fca5a5; }
            """)
            del_btn.clicked.connect(lambda _, p_id=item['payment_id']: self.handle_delete_payment(p_id))

            action_layout.addWidget(edit_btn)
            action_layout.addWidget(del_btn)
            action_layout.addStretch()

            self.table.setCellWidget(row_idx, 4, action_widget)

    def open_view_all_dialog(self):
        dialog = ViewAllPublicationsDialog(self)
        dialog.exec()
        # Refresh combo in case payments changed status elsewhere
        self.load_publication_combo()

    def open_edit_billing_total_dialog(self):
        pub_id = self.get_selected_pub_id()
        if not pub_id:
            QMessageBox.warning(self, "Warning", "Please select a publication first.")
            return

        dialog = SetBillingTotalDialog(self, current_total=self.current_billing_total)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            try:
                new_total = float(dialog.get_total())
                if new_total < 0:
                    raise ValueError
            except ValueError:
                QMessageBox.critical(self, "Invalid Input", "Please enter a valid billing amount.")
                return

            success, msg = db.set_or_update_billing_amount(pub_id, new_total)
            if success:
                QMessageBox.information(self, "Success", msg)
                self.load_billing_and_payments()
                self.load_publication_combo()
            else:
                QMessageBox.critical(self, "Error", msg)

    def open_record_payment_dialog(self):
        pub_id = self.get_selected_pub_id()
        if not pub_id:
            QMessageBox.warning(self, "Warning", "Please select a publication first.")
            return

        dialog = RecordPaymentDialog(self, default_method=self.selected_payment_method)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            data = dialog.get_data()
            
            try:
                amount = float(data['amount'])
                if amount <= 0:
                    raise ValueError
            except ValueError:
                QMessageBox.critical(self, "Invalid Input", "Please enter a valid numeric payment amount.")
                return

            success, msg = db.record_payment_in_db(
                pub_id=pub_id,
                amount=amount,
                payment_method=data['method'],
                or_number=data['or_number']
            )

            if success:
                QMessageBox.information(self, "Success", msg)
                self.load_billing_and_payments()
                self.load_publication_combo()
            else:
                QMessageBox.critical(self, "Error", msg)

    def open_edit_payment_dialog(self, payment_item):
        pub_id = self.get_selected_pub_id()
        if not pub_id:
            return

        dialog = RecordPaymentDialog(self, initial_data=payment_item)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            data = dialog.get_data()
            
            try:
                amount = float(data['amount'])
                if amount <= 0:
                    raise ValueError
            except ValueError:
                QMessageBox.critical(self, "Invalid Input", "Please enter a valid numeric payment amount.")
                return

            success, msg = db.update_payment_in_db(
                payment_id=payment_item['payment_id'],
                pub_id=pub_id,
                amount=amount,
                payment_method=data['method'],
                or_number=data['or_number']
            )

            if success:
                QMessageBox.information(self, "Success", msg)
                self.load_billing_and_payments()
                self.load_publication_combo()
            else:
                QMessageBox.critical(self, "Error", msg)

    def handle_delete_payment(self, payment_id):
        pub_id = self.get_selected_pub_id()
        if not pub_id:
            return

        reply = QMessageBox.question(
            self, "Confirm Deletion",
            "Are you sure you want to delete this payment record?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            success, msg = db.delete_payment_from_db(payment_id, pub_id)
            if success:
                QMessageBox.information(self, "Success", msg)
                self.load_billing_and_payments()
                self.load_publication_combo()
            else:
                QMessageBox.critical(self, "Error", msg)
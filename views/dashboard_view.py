# Path: views/dashboard_view.py
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QFrame, QTableWidget, QTableWidgetItem, QHeaderView, QPushButton, QSizePolicy
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QColor
from datetime import datetime, date

import db

class MetricCard(QFrame):
    """Custom Metric Card with top border accent line matching reference mockups."""
    def __init__(self, title, count_text, subtext, accent_color="#0b2545"):
        super().__init__()
        self.setStyleSheet(f"""
            QFrame {{
                background-color: #ffffff;
                border-radius: 8px;
                border: 1px solid #e2e8f0;
                border-top: 4px solid {accent_color};
            }}
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 14, 16, 14)
        layout.setSpacing(6)

        title_lbl = QLabel(title)
        title_lbl.setFont(QFont("Arial", 9, QFont.Weight.Bold))
        title_lbl.setStyleSheet("color: #64748b; border: none;")

        self.count_lbl = QLabel(str(count_text))
        self.count_lbl.setFont(QFont("Arial", 20, QFont.Weight.Bold))
        self.count_lbl.setStyleSheet("color: #1e293b; border: none; margin: 2px 0px;")

        self.sub_lbl = QLabel(subtext)
        self.sub_lbl.setFont(QFont("Arial", 8))
        self.sub_lbl.setStyleSheet("color: #94a3b8; border: none;")

        layout.addWidget(title_lbl)
        layout.addWidget(self.count_lbl)
        layout.addWidget(self.sub_lbl)

    def update_values(self, count_text, subtext=None):
        self.count_lbl.setText(str(count_text))
        if subtext:
            self.sub_lbl.setText(subtext)


class DashboardView(QWidget):
    def __init__(self, main_window=None):
        super().__init__()
        self.main_window = main_window
        self.init_ui()
        self.load_dashboard_data()

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(25, 20, 25, 20)
        main_layout.setSpacing(20)

        # Header Section
        header_vbox = QVBoxLayout()
        header_vbox.setSpacing(4)

        title_label = QLabel("System Dashboard")
        title_label.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        title_label.setStyleSheet("color: #1e293b;")

        subtitle_label = QLabel("Welcome back! Here is today's publication overview.")
        subtitle_label.setFont(QFont("Arial", 10))
        subtitle_label.setStyleSheet("color: #64748b;")

        header_vbox.addWidget(title_label)
        header_vbox.addWidget(subtitle_label)
        main_layout.addLayout(header_vbox)

        # Metrics Cards Grid Layout
        metrics_layout = QHBoxLayout()
        metrics_layout.setSpacing(15)

        self.card_pending = MetricCard("Pending Layout Verification", "0", "Notices to check", "#f59e0b")
        self.card_upcoming = MetricCard("Upcoming Publications", "0", "Scheduled for next issue", "#3b82f6")
        self.card_unreleased = MetricCard("Unreleased Documents", "0", "Awaiting pickup/payment", "#ef4444")
        self.card_collections = MetricCard("Total Collections Today", "₱ 0.00", "0 payments recorded", "#10b981")

        metrics_layout.addWidget(self.card_pending)
        metrics_layout.addWidget(self.card_upcoming)
        metrics_layout.addWidget(self.card_unreleased)
        metrics_layout.addWidget(self.card_collections)

        main_layout.addLayout(metrics_layout)

        # Lower Content Section
        content_layout = QHBoxLayout()
        content_layout.setSpacing(20)

        # Check current user role
        role_name = ""
        if self.main_window and hasattr(self.main_window, 'current_user'):
            role_name = str(self.main_window.current_user.get("role_name", "")).lower()

        is_publisher = "publisher" in role_name or "editor" in role_name

        # Active Multi-Issue Publication Table Panel
        table_card = QFrame()
        table_card.setStyleSheet("background-color: #ffffff; border-radius: 8px; border: 1px solid #e2e8f0;")
        table_vbox = QVBoxLayout(table_card)
        table_vbox.setContentsMargins(18, 16, 18, 16)

        table_header = QHBoxLayout()
        table_title = QLabel("Active Multi-Issue Publication Schedules")
        table_title.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        table_title.setStyleSheet("color: #1e293b; border: none;")
        table_header.addWidget(table_title)
        table_header.addStretch()

        # Only show 'View All' if not a publisher/editor
        if not is_publisher:
            view_all_btn = QPushButton("View All")
            view_all_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            view_all_btn.setStyleSheet("""
                QPushButton {
                    background: transparent; color: #2563eb; border: none;
                    font-weight: bold; font-size: 11px;
                }
                QPushButton:hover { text-decoration: underline; }
            """)
            view_all_btn.clicked.connect(self.navigate_to_schedules)
            table_header.addWidget(view_all_btn)

        table_vbox.addLayout(table_header)
        table_vbox.addSpacing(10)

        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["Case / Ref No.", "Client Name", "Type", "Current Run", "Next Date"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.verticalHeader().setVisible(False)
        self.table.setAlternatingRowColors(True)
        self.table.setShowGrid(False)
        self.table.setStyleSheet("""
            QTableWidget { 
                border: none; 
                background-color: #ffffff; 
                color: #1e293b;
                gridline-color: #f1f5f9;
            }
            QHeaderView::section { 
                background-color: #f8fafc; 
                color: #64748b;
                font-weight: bold; 
                border: none; 
                padding: 8px; 
                font-size: 11px;
            }
            QTableWidget::item {
                padding: 6px;
                border-bottom: 1px solid #f1f5f9;
            }
        """)
        table_vbox.addWidget(self.table)
        
        # Add table card with full width if publisher, otherwise share space with Quick Actions
        content_layout.addWidget(table_card, 3 if not is_publisher else 1)

        # Quick Actions Side Panel Layout (Only shown for OIC / non-publishers)
        if not is_publisher:
            actions_card = QFrame()
            actions_card.setStyleSheet("background-color: #ffffff; border-radius: 8px; border: 1px solid #e2e8f0;")
            actions_card.setFixedWidth(280)
            
            actions_vbox = QVBoxLayout(actions_card)
            actions_vbox.setContentsMargins(18, 20, 18, 20)
            actions_vbox.setSpacing(14)

            actions_title = QLabel("Quick Actions")
            actions_title.setFont(QFont("Arial", 11, QFont.Weight.Bold))
            actions_title.setStyleSheet("color: #1e293b; border: none;")
            actions_vbox.addWidget(actions_title)
            actions_vbox.addSpacing(4)

            btn_new_pub = QPushButton("+ New Publication")
            btn_record_pay = QPushButton("Record Payment (OR)")
            btn_gen_docs = QPushButton("Generate Documents")

            button_style = """
                QPushButton {
                    color: white; 
                    font-weight: bold; 
                    font-size: 13px;
                    border-radius: 6px; 
                    border: none;
                    padding: 15px;
                }
                QPushButton:hover {
                    opacity: 0.9;
                }
            """

            btn_new_pub.setStyleSheet("background-color: #2563eb;" + button_style)
            btn_record_pay.setStyleSheet("background-color: #10b981;" + button_style)
            btn_gen_docs.setStyleSheet("background-color: #d97706;" + button_style)

            # Pass action parameters to navigate_to
            btn_new_pub.clicked.connect(lambda: self.navigate_to("Publications", "add_publication"))
            btn_record_pay.clicked.connect(lambda: self.navigate_to("Billing and Payments", "record_payment"))
            btn_gen_docs.clicked.connect(lambda: self.navigate_to("Documents", "generate_documents"))

            for btn in (btn_new_pub, btn_record_pay, btn_gen_docs):
                btn.setCursor(Qt.CursorShape.PointingHandCursor)
                btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
                actions_vbox.addWidget(btn)

            content_layout.addWidget(actions_card, 1)

        main_layout.addLayout(content_layout)

    def load_dashboard_data(self):
        """Fetch metrics and update active runs table dynamically."""
        metrics = db.get_dashboard_metrics()
        
        self.card_pending.update_values(metrics["pending_layout"])
        self.card_upcoming.update_values(metrics["upcoming_publications"])
        self.card_unreleased.update_values(metrics["unreleased_documents"])
        
        col_text = f"₱ {metrics['total_collections_today']:,.2f}"
        pay_cnt_text = f"{metrics['payments_today_count']} payment{'s' if metrics['payments_today_count'] != 1 else ''} recorded"
        self.card_collections.update_values(col_text, pay_cnt_text)

        schedules = db.get_active_publication_schedules_dashboard(limit=6)
        self.table.setRowCount(0)

        if not schedules:
            self.table.setRowCount(1)
            empty_item = QTableWidgetItem("No active publication schedules found.")
            empty_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            empty_item.setForeground(QColor("#94a3b8"))
            self.table.setItem(0, 0, empty_item)
            self.table.setSpan(0, 0, 1, 5)
            return

        for row_idx, item in enumerate(schedules):
            self.table.insertRow(row_idx)

            case_no = str(item.get('case_number') or 'N/A')
            client_name = str(item.get('client_name') or 'N/A')
            pub_type = str(item.get('publication_type') or 'N/A')
            
            curr_issue = item.get('current_issue_num') or 1
            total_req = item.get('required_issues') or 1
            current_run = f"Issue {curr_issue} of {total_req}"

            next_date_val = item.get('next_date')
            if isinstance(next_date_val, (datetime, date)):
                next_date = next_date_val.strftime("%b %d, %Y")
            elif next_date_val:
                next_date = str(next_date_val)
            else:
                next_date = "Completed"

            it_case = QTableWidgetItem(case_no)
            it_client = QTableWidgetItem(client_name)
            it_type = QTableWidgetItem(pub_type)
            it_run = QTableWidgetItem(current_run)
            it_date = QTableWidgetItem(next_date)

            it_run.setForeground(QColor("#2563eb"))
            it_run.setFont(QFont("Arial", 9, QFont.Weight.Bold))

            dark_color = QColor("#1e293b")
            for table_item in (it_case, it_client, it_type, it_date):
                table_item.setForeground(dark_color)

            self.table.setItem(row_idx, 0, it_case)
            self.table.setItem(row_idx, 1, it_client)
            self.table.setItem(row_idx, 2, it_type)
            self.table.setItem(row_idx, 3, it_run)
            self.table.setItem(row_idx, 4, it_date)

    def navigate_to_schedules(self):
        self.navigate_to("Publication Schedule")

    def navigate_to(self, view_name, action=None):
        if self.main_window and hasattr(self.main_window, 'navigate_to'):
            self.main_window.navigate_to(view_name, action)
# Path: views/dashboard_window.py
from PyQt6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QPushButton, QScrollArea
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont

from views.dashboard_view import DashboardView
from views.clients_view import ClientsView
from views.publications_view import PublicationsView
from views.publication_details_view import PublicationDetailsView
from views.publication_schedule_view import PublicationScheduleView
from views.billing_payments_view import BillingPaymentsView
from views.documents_view import DocumentsView
from views.releases_view import ReleasesView
from views.reports_view import ReportsView
from views.profile_view import ProfileView

# New Publisher Views
from views.review_publication_view import ReviewPublicationView
from views.publication_status_view import PublicationStatusView
from views.client_records_view import ClientRecordsView
from views.publisher_reports_view import PublisherReportsView


class DashboardWindow(QMainWindow):
    def __init__(self, current_user, on_logout):
        super().__init__()
        self.current_user = current_user
        self.on_logout = on_logout
        self.nav_buttons = {}
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Mantalaan Newspaper - Publication and Record Management System")
        
        # Open maximized instead of fixed resize
        self.showMaximized()

        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QHBoxLayout(main_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Sidebar Navigation
        sidebar = QFrame()
        sidebar.setStyleSheet("background-color: #0b2545; min-width: 220px; max-width: 220px;")
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(10, 20, 10, 20)

        app_title = QLabel("MANTALAAN\nNEWSPAPER")
        app_title.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        app_title.setStyleSheet("color: white; margin-bottom: 20px;")
        app_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sidebar_layout.addWidget(app_title)

        role_name = str(self.current_user.get("role_name", "")).lower()

        if "publisher" in role_name or "editor" in role_name:
            nav_items = [
                "Dashboard",
                "Review Publication",
                "Publication Status",
                "Client Records",
                "Publisher Reports"
            ]
        else:
            nav_items = [
                "Dashboard",
                "Clients",
                "Publications",
                "Publication Schedule",
                "Billing and Payments",
                "Documents",
                "Releases",
                "Reports"
            ]

        for item in nav_items:
            btn = QPushButton(f"  {item}")
            btn.setFont(QFont("Arial", 9))
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.clicked.connect(lambda _, name=item: self.navigate_to(name))
            sidebar_layout.addWidget(btn)
            self.nav_buttons[item] = btn

        sidebar_layout.addStretch()

        # Profile Button
        profile_btn = QPushButton("  👤  Profile")
        profile_btn.setFont(QFont("Arial", 9))
        profile_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        profile_btn.clicked.connect(lambda: self.navigate_to("Profile"))
        sidebar_layout.addWidget(profile_btn)
        self.nav_buttons["Profile"] = profile_btn

        # Logout Button
        logout_btn = QPushButton("  Logout")
        logout_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        logout_btn.setStyleSheet("""
            QPushButton { color: #e74c3c; text-align: left; padding: 10px; border: none; font-weight: bold; background: transparent; }
            QPushButton:hover { background-color: #1a5b9e; color: white; }
        """)
        logout_btn.clicked.connect(self.on_logout)
        sidebar_layout.addWidget(logout_btn)

        # Content Area
        content_area = QFrame()
        content_area.setStyleSheet("background-color: #f4f6f9;")
        content_layout = QVBoxLayout(content_area)
        content_layout.setContentsMargins(0, 0, 0, 0)

        # Header
        header = QFrame()
        header.setStyleSheet("background-color: white; border-bottom: 1px solid #e0e0e0; min-height: 50px;")
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(20, 0, 25, 0)
        
        user_info = QLabel(f"Logged in as: <b>{self.current_user['full_name']}</b> ({self.current_user['role_name']})")
        user_info.setStyleSheet("color: #2c3e50; font-size: 13px;")

        header_layout.addStretch()
        header_layout.addWidget(user_info)

        content_layout.addWidget(header)

        # Scrollable View Container
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setStyleSheet("QScrollArea { border: none; }")

        content_layout.addWidget(self.scroll_area, 1)

        main_layout.addWidget(sidebar)
        main_layout.addWidget(content_area, 1)

        # Initial View
        self.navigate_to("Dashboard")

    def open_publication_details(self, pub_id):
        """Switches the view container to display PublicationDetailsView."""
        view = PublicationDetailsView(
            publication_id=pub_id, 
            on_back=lambda: self.navigate_to("Publications")
        )
        self.scroll_area.setWidget(view)

    def navigate_to(self, page_name, action=None):
        role_name = str(self.current_user.get("role_name", "")).lower()
        publisher_only_views = ["Review Publication", "Publication Status", "Publisher Reports", "Client Records"]
        
        if page_name in publisher_only_views and not ("publisher" in role_name or "editor" in role_name):
            return

        default_style = """
            QPushButton {
                color: #ecf0f1; text-align: left; padding: 10px; border: none; border-radius: 4px; background: transparent;
            }
            QPushButton:hover { background-color: #1a5b9e; }
        """
        active_style = """
            QPushButton {
                color: #ffffff; text-align: left; padding: 10px; border: none; border-radius: 4px; background-color: #1a5b9e; font-weight: bold;
            }
        """

        for name, btn in self.nav_buttons.items():
            if name in self.nav_buttons:
                btn.setStyleSheet(active_style if name == page_name else default_style)

        if page_name == "Dashboard":
            view = DashboardView(self)
        elif page_name == "Review Publication":
            view = ReviewPublicationView()
        elif page_name == "Publication Status":
            view = PublicationStatusView()
        elif page_name == "Client Records":
            view = ClientRecordsView()
        elif page_name == "Publication Records":
            view = PublicationsView(on_view_details=self.open_publication_details)
        elif page_name == "Publisher Reports":
            view = PublisherReportsView()
        elif page_name == "Clients":
            view = ClientsView()
        elif page_name == "Publications":
            view = PublicationsView(on_view_details=self.open_publication_details)
        elif page_name == "Publication Schedule":
            view = PublicationScheduleView()
        elif page_name in ("Billing & Payments", "Billing Payments", "Billing and Payments"):
            view = BillingPaymentsView()
        elif page_name == "Documents":
            view = DocumentsView()
        elif page_name == "Releases":
            view = ReleasesView()
        elif page_name == "Reports":
            view = ReportsView()
        elif page_name == "Profile":
            view = ProfileView(self.current_user)
        else:
            view = QWidget()
            layout = QVBoxLayout(view)
            lbl = QLabel(f"{page_name} module coming soon!")
            lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            lbl.setFont(QFont("Arial", 14))
            lbl.setStyleSheet("color: #7f8c8d;")
            layout.addWidget(lbl)

        self.scroll_area.setWidget(view)

        if action:
            QTimer.singleShot(60, lambda: self._trigger_view_action(view, action))

    def _trigger_view_action(self, view, action):
        if action == "add_publication":
            if hasattr(view, 'open_add_dialog'):
                view.open_add_dialog()
            elif hasattr(view, 'add_btn'):
                view.add_btn.click()
        elif action == "record_payment":
            if hasattr(view, 'open_record_dialog'):
                view.open_record_dialog()
            elif hasattr(view, 'record_btn'):
                view.record_btn.click()
        elif action == "generate_documents":
            if hasattr(view, 'open_generate_dialog'):
                view.open_generate_dialog()
            elif hasattr(view, 'generate_btn'):
                view.generate_btn.click()
# Path: main.py
import sys
from PyQt6.QtWidgets import QApplication

from styles import GLOBAL_FIX_STYLESHEET
from views.login_window import LoginWindow
from views.dashboard_window import DashboardWindow
from views.super_admin_dashboard import SuperAdminDashboard

class AppController:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.app.setStyleSheet(GLOBAL_FIX_STYLESHEET)
        self.login_win = None
        self.dash_win = None

    def run(self):
        self.show_login()
        sys.exit(self.app.exec())

    def show_login(self):
        if self.dash_win:
            self.dash_win.close()
        self.login_win = LoginWindow(self.show_dashboard)
        self.login_win.show()

    def show_dashboard(self, user):
        if self.login_win:
            self.login_win.close()

        role_id = user.get("role_id")
        role_str = str(user.get("role_name") or user.get("role") or "").lower().strip()

        is_super_admin = (role_id == 1) or ("super admin" in role_str) or (role_str == "admin")

        if is_super_admin:
            self.dash_win = SuperAdminDashboard(user, self.show_login)
        else:
            self.dash_win = DashboardWindow(user, self.show_login)

        self.dash_win.show()

if __name__ == "__main__":
    controller = AppController()
    controller.run()
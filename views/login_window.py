# Path: views/login_window.py
import os
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QFrame, QMessageBox
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont, QPixmap, QPainter, QPainterPath, QColor

from db import authenticate_user

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

class LeftPanel(QFrame):
    """Custom frame to render a swerved background split between two shades of blue."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("LeftPanel")

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        width = self.width()
        height = self.height()
        
        painter.fillRect(0, 0, width, height, QColor("#0d2847"))
        
        path = QPainterPath()
        path.moveTo(0, height)
        path.lineTo(0, height * 0.52)
        
        path.cubicTo(
            width * 0.35, height * 0.40,
            width * 0.65, height * 0.68,
            width, height * 0.46
        )
        path.lineTo(width, height)
        path.closeSubpath()
        
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor("#143c66"))
        painter.drawPath(path)
        
        super().paintEvent(event)


class LoginWindow(QWidget):
    def __init__(self, on_login_success):
        super().__init__()
        self.on_login_success = on_login_success
        self.init_ui()
        
        # Guarantee maximized state upon creation and after returning from logout
        self.showMaximized()
        QTimer.singleShot(10, self.showMaximized)

    def init_ui(self):
        self.setWindowTitle("Mantalaan Newspaper - Login")
        
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Left Panel (Branding / Slogan with Swerved Background)
        left_panel = LeftPanel()
        
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(60, 60, 60, 60)
        left_layout.addStretch()

        quote_box = QFrame()
        quote_box.setStyleSheet("QFrame { border: none; border-left: 5px solid #63b3ed; background: transparent; }")
        quote_layout = QVBoxLayout(quote_box)
        quote_layout.setContentsMargins(20, 0, 0, 0)
        quote_layout.setSpacing(12)

        slogan_style = "color: #ffffff; background: transparent; border: none;"

        slogan1 = QLabel("Trusted News.")
        slogan1.setFont(QFont("Georgia", 28, QFont.Weight.Bold))
        slogan1.setStyleSheet(slogan_style)

        slogan2 = QLabel("Informed Citizens.")
        slogan2.setFont(QFont("Georgia", 28, QFont.Weight.Bold))
        slogan2.setStyleSheet(slogan_style)

        slogan3 = QLabel("A Stronger Community.")
        slogan3.setFont(QFont("Georgia", 28, QFont.Weight.Bold))
        slogan3.setStyleSheet(slogan_style)

        quote_layout.addWidget(slogan1)
        quote_layout.addWidget(slogan2)
        quote_layout.addWidget(slogan3)

        left_layout.addWidget(quote_box)

        # Right Panel (Form)
        right_panel = QFrame()
        right_panel.setStyleSheet("background-color: #ffffff;")
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(100, 50, 100, 30)
        right_layout.addStretch()

        logo_label = QLabel()
        logo_path_png = os.path.join(BASE_DIR, "assets", "logo.png")
        logo_path_jpg = os.path.join(BASE_DIR, "assets", "logo.jpg")

        # Upscaled width from 280 to 380
        if os.path.exists(logo_path_png):
            pixmap = QPixmap(logo_path_png)
            logo_label.setPixmap(pixmap.scaledToWidth(450, Qt.TransformationMode.SmoothTransformation))
        elif os.path.exists(logo_path_jpg):
            pixmap = QPixmap(logo_path_jpg)
            logo_label.setPixmap(pixmap.scaledToWidth(450, Qt.TransformationMode.SmoothTransformation))
        else:
            logo_label.setText("MANTALAAN NEWSPAPER")
            logo_label.setFont(QFont("Arial", 26, QFont.Weight.Bold))
            logo_label.setStyleSheet("color: #0b3c5d;")

        logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        subtitle = QLabel("Publication and Record Management System")
        subtitle.setFont(QFont("Arial", 11))
        subtitle.setStyleSheet("color: #6c757d; margin-top: 8px; margin-bottom: 30px;")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)

        welcome_label = QLabel("Welcome Back!")
        welcome_label.setFont(QFont("Arial", 22, QFont.Weight.Bold))
        welcome_label.setStyleSheet("color: #1a252f;")
        welcome_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        sub_label = QLabel("Please sign in to your account")
        sub_label.setFont(QFont("Arial", 12))
        sub_label.setStyleSheet("color: #8d99ae; margin-bottom: 25px;")
        sub_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        input_style = """
            QLineEdit {
                padding: 14px 16px;
                border: 1.5px solid #dcdfe6;
                border-radius: 8px;
                background-color: #ffffff;
                color: #2c3e50;
                font-size: 14px;
            }
            QLineEdit:focus { border: 2px solid #0b3c5d; }
        """

        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Username or Email")
        self.username_input.setStyleSheet(input_style)
        self.username_input.returnPressed.connect(self.handle_login)

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Password")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setStyleSheet(input_style)
        self.password_input.returnPressed.connect(self.handle_login)

        login_btn = QPushButton("Login")
        login_btn.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        login_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        login_btn.setStyleSheet("""
            QPushButton {
                background-color: #0b3c5d; 
                color: white; 
                padding: 14px; 
                border-radius: 8px;
            }
            QPushButton:hover { background-color: #134e75; }
        """)
        login_btn.clicked.connect(self.handle_login)

        right_layout.addWidget(logo_label)
        right_layout.addWidget(subtitle)
        right_layout.addWidget(welcome_label)
        right_layout.addWidget(sub_label)
        right_layout.addWidget(self.username_input)
        right_layout.addSpacing(14)
        right_layout.addWidget(self.password_input)
        right_layout.addSpacing(20)
        right_layout.addWidget(login_btn)
        right_layout.addStretch()

        footer_label = QLabel("© 1997 Mantalaan Newspaper. All rights reserved.")
        footer_label.setFont(QFont("Arial", 9))
        footer_label.setStyleSheet("color: #b0b5c0;")
        footer_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        right_layout.addWidget(footer_label)

        main_layout.addWidget(left_panel, 1)
        main_layout.addWidget(right_panel, 1)

    def handle_login(self):
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()

        if not username or not password:
            QMessageBox.warning(self, "Input Error", "Please enter both username and password.")
            return

        user = authenticate_user(username, password)

        if user:
            self.on_login_success(user)
        else:
            QMessageBox.warning(self, "Login Failed", "Invalid username or password.")
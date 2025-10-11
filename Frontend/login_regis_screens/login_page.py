from PyQt6.QtWidgets import (
    QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout,
    QMessageBox, QMenu
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QIntValidator

from db.db_operations import DatabaseOperations

class LoginPage(QWidget):
    def __init__(self, stacked_widget):
        super().__init__()
        self.stacked_widget = stacked_widget
        self.user_data = None  # To store logged-in user data

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)

        # ===== NAVIGATION BAR =====
        nav_widget = QWidget()
        nav_widget.setStyleSheet("background-color: #1E4D7B;")
        nav_bar = QHBoxLayout(nav_widget)
        nav_bar.setContentsMargins(20, 10, 20, 10)

        logo_text = QLabel("InfoChan - Library Information System")
        logo_text.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        logo_text.setStyleSheet("color: white;")

        btn_home = QPushButton("HOME")
        btn_register = QPushButton("REGISTER")
        btn_login = QPushButton("USER LOGIN")

        # Connect navigation buttons
        btn_home.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(0))
        btn_register.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(1))
        btn_login.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(2))

        for btn in [btn_home, btn_register, btn_login]:
            btn.setStyleSheet("""
                QPushButton {
                    color: white;
                    background: transparent;
                    border: none;
                    font-weight: bold;
                    font-size: 12pt;
                }
                QPushButton:hover {
                    text-decoration: underline;
                }
            """)

        nav_bar.addWidget(logo_text)
        nav_bar.addStretch()
        nav_bar.addWidget(btn_home)
        nav_bar.addWidget(btn_register)
        nav_bar.addWidget(btn_login)

        layout.addWidget(nav_widget)

        # ===== FORM LAYOUT =====
        form_layout = QVBoxLayout()
        form_layout.setContentsMargins(150, 60, 150, 60)
        form_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # ===== TITLE =====
        title = QLabel("USER LOGIN")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-size: 20pt; font-weight: bold; color: #1E4D7B;")
        form_layout.addWidget(title)
        form_layout.addSpacing(20)

        # ===== USERTYPE BUTTON WITH MENU =====
        self.role_btn = QPushButton("Usertype")
        self.role_btn.setStyleSheet("max-width: 300px; padding: 8px; font-size: 11pt; font-weight: bold; border: 2px solid #D1D5DB; border-radius: 8px;")
        form_layout.addWidget(self.role_btn)
        form_layout.addSpacing(15)

        role_menu = QMenu()
        role_menu.addAction("Student", lambda: self.set_role("Student"))
        role_menu.addAction("Instructor", lambda: self.set_role("Instructor"))
        role_menu.addAction("Admin", lambda: self.set_role("Admin"))
        self.role_btn.setMenu(role_menu)

        # ===== ID NUMBER =====
        self.id_input = QLineEdit()
        self.id_input.setPlaceholderText("Enter 6-digit ID Number")
        self.id_input.setValidator(QIntValidator(0, 999999))
        self.id_input.setMaxLength(6)
        self.id_input.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.id_input.setStyleSheet("max-width: 300px; padding: 8px; border: 2px solid #D1D5DB; border-radius: 8px;")
        form_layout.addWidget(self.id_input)
        form_layout.addSpacing(15)

        # ===== PASSWORD =====
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Enter Password")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.password_input.setStyleSheet("max-width: 300px; padding: 8px; border: 2px solid #D1D5DB; border-radius: 8px;")
        form_layout.addWidget(self.password_input)
        form_layout.addSpacing(15)

        # ===== LOGIN BUTTON =====
        login_btn = QPushButton("LOGIN")
        login_btn.setStyleSheet("background-color: #1E4D7B; color: white; font-weight: bold; padding: 8px; max-width: 300px; border-radius: 8px;")
        login_btn.clicked.connect(self.login_user)
        form_layout.addWidget(login_btn)
        form_layout.addSpacing(20)

        # ===== REGISTER LINK =====
        register_btn = QPushButton("Don’t have an account? Register here")
        register_btn.setStyleSheet("background: transparent; color: #1E4D7B; text-decoration: underline; border: none; max-width: 350px;")
        register_btn.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(1))
        form_layout.addWidget(register_btn)

        layout.addLayout(form_layout)
        layout.addStretch(1)  # Add stretch to center the form vertically

        self.setLayout(layout)

        # Track selected role
        self.selected_role = None

    def set_role(self, role):
        """Set the role when selected from the menu"""
        self.selected_role = role
        self.role_btn.setText(role)

    def login_user(self):
        """Handle login validation with database"""
        user_id = self.id_input.text().strip()
        password = self.password_input.text().strip()

        # === Validation ===
        if not self.selected_role:
            QMessageBox.warning(self, "Error", "Please select a user type (Student, Instructor, or Admin).")
            return
        if not user_id.isdigit() or len(user_id) != 6:
            QMessageBox.warning(self, "Error", "ID number must be exactly 6 digits.")
            return
        if not password:
            QMessageBox.warning(self, "Error", "Please enter your password.")
            return

        # === Database Check ===
        db = DatabaseOperations()
        try:
            self.user_data = db.login_user(self.selected_role, user_id, password)
            if self.user_data:
                QMessageBox.information(self, "Success", f"Welcome {self.selected_role}! You logged in successfully.")
                if self.selected_role == "Admin":
                    self.stacked_widget.setCurrentIndex(8)  # Admin Dashboard
                else:
                    self.stacked_widget.setCurrentIndex(4)  # Student Dashboard
            else:
                QMessageBox.warning(self, "Login Failed", "Invalid ID number or password.")
        except Exception as e:
            QMessageBox.critical(self, "Database Error", f"An error occurred:\n{e}")
        finally:
            db.close_connection()
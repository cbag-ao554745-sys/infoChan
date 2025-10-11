from PyQt6.QtWidgets import (
    QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout,
    QComboBox, QMessageBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QIntValidator

from db.db_operations import DatabaseOperations

class RegisterPage(QWidget):
    def __init__(self, stacked_widget):
        super().__init__()
        self.stacked_widget = stacked_widget

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

        # ===== FORM =====
        form_layout = QVBoxLayout()
        form_layout.setContentsMargins(150, 60, 150, 60)
        form_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        title = QLabel("REGISTER FORM")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-size: 20pt; font-weight: bold; color: #1E4D7B;")
        form_layout.addWidget(title)
        form_layout.addSpacing(20)

        # Role dropdown
        self.role_dropdown = QComboBox()
        self.role_dropdown.addItems(["Select Role", "Student", "Instructor"])
        self.role_dropdown.setStyleSheet("max-width: 300px; padding: 8px; border: 2px solid #D1D5DB; border-radius: 8px;")
        form_layout.addWidget(self.role_dropdown)
        form_layout.addSpacing(15)

        # Name
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Last name, First name, MI")
        self.name_input.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.name_input.setStyleSheet("max-width: 300px; padding: 8px; border: 2px solid #D1D5DB; border-radius: 8px;")
        form_layout.addWidget(self.name_input)
        form_layout.addSpacing(15)

        # Strand
        self.department_dropdown = QComboBox()
        self.department_dropdown.addItems(["Strand", "STEM", "ABM", "HUMSS", "GAS"])
        self.department_dropdown.setStyleSheet("max-width: 300px; padding: 8px; border: 2px solid #D1D5DB; border-radius: 8px;")
        form_layout.addWidget(self.department_dropdown)
        form_layout.addSpacing(15)

        # Grade Level
        self.year_dropdown = QComboBox()
        self.year_dropdown.addItems([
            "Grade Level", "Grade 7", "Grade 8", "Grade 9",
            "Grade 10", "Grade 11", "Grade 12", "None"
        ])
        self.year_dropdown.setStyleSheet("max-width: 300px; padding: 8px; border: 2px solid #D1D5DB; border-radius: 8px;")
        form_layout.addWidget(self.year_dropdown)
        form_layout.addSpacing(15)

        # ID Number (6 digits)
        self.id_input = QLineEdit()
        self.id_input.setPlaceholderText("Enter 6-digit ID number")
        self.id_input.setValidator(QIntValidator(0, 999999))
        self.id_input.setMaxLength(6)
        self.id_input.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.id_input.setStyleSheet("max-width: 300px; padding: 8px; border: 2px solid #D1D5DB; border-radius: 8px;")
        form_layout.addWidget(self.id_input)
        form_layout.addSpacing(15)

        # Password
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Enter password")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.password_input.setStyleSheet("max-width: 300px; padding: 8px; border: 2px solid #D1D5DB; border-radius: 8px;")
        form_layout.addWidget(self.password_input)
        form_layout.addSpacing(15)

        # Register Button
        register_btn = QPushButton("REGISTER")
        register_btn.setStyleSheet("background-color: #1E4D7B; color: white; font-weight: bold; padding: 8px; max-width: 300px; border-radius: 8px;")
        register_btn.clicked.connect(self.register_user)
        form_layout.addWidget(register_btn)

        layout.addLayout(form_layout)
        layout.addStretch(1)  # Add stretch to center the form vertically

        self.setLayout(layout)

    def register_user(self):
        """Register user with database"""
        name = self.name_input.text().strip()
        role = self.role_dropdown.currentText()
        strand = self.department_dropdown.currentText()
        grade = self.year_dropdown.currentText()
        user_id = self.id_input.text().strip()
        password = self.password_input.text().strip()

        # ==== Validation ====
        if role == "Select Role":
            QMessageBox.warning(self, "Error", "Please select a valid role.")
            return
        if role == "Student" and strand == "Strand":
            QMessageBox.warning(self, "Error", "Please select a valid strand.")
            return
        if grade == "Grade Level":
            QMessageBox.warning(self, "Error", "Please select a valid grade level.")
            return
        if not name or not user_id or not password:
            QMessageBox.warning(self, "Error", "All fields must be filled.")
            return
        if not user_id.isdigit() or len(user_id) != 6:
            QMessageBox.warning(self, "Error", "ID must be exactly 6 digits.")
            return

        # ==== Database Insertion ====
        db = DatabaseOperations()
        try:
            success = db.register_user(role, name, user_id, password, strand, grade)
            if success:
                QMessageBox.information(self, "Success", f"{role} '{name}' registered successfully!")
                self.clear_fields()
                self.stacked_widget.setCurrentIndex(2)  # Go to Login page
            else:
                QMessageBox.critical(self, "Error", "Failed to register user.")
        finally:
            db.close_connection()

    def clear_fields(self):
        """Reset all form fields"""
        self.name_input.clear()
        self.id_input.clear()
        self.password_input.clear()
        self.role_dropdown.setCurrentIndex(0)
        self.department_dropdown.setCurrentIndex(0)
        self.year_dropdown.setCurrentIndex(0)
import bcrypt
from PyQt6.QtWidgets import QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QMessageBox
from PyQt6.QtCore import Qt

from db.db_operations import DatabaseOperations


class ForgotPasswordPage(QWidget):
    def __init__(self, stacked_widget):
        super().__init__()
        self.stacked_widget = stacked_widget

        layout = QVBoxLayout()
        layout.setContentsMargins(150, 60, 150, 60)

        # ===== TITLE =====
        title = QLabel("FORGOT PASSWORD")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-size: 20pt; font-weight: bold; color: #1E4D7B;")
        layout.addWidget(title)

        # ===== EMAIL / ID FIELD =====
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("Enter your registered Email or ID Number")
        self.email_input.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.email_input)

        # ===== RESET BUTTON =====
        reset_btn = QPushButton("RESET PASSWORD")
        reset_btn.setStyleSheet("background-color: #1E4D7B; color: white; font-weight: bold; padding: 8px;")
        reset_btn.clicked.connect(self.reset_password)
        layout.addWidget(reset_btn)

        # ===== BACK TO LOGIN =====
        back_btn = QPushButton("Back to Login")
        back_btn.setStyleSheet("background: transparent; color: #1E4D7B; text-decoration: underline; border: none;")
        back_btn.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(2))  # back to login page
        layout.addWidget(back_btn, alignment=Qt.AlignmentFlag.AlignCenter)

        self.setLayout(layout)

    def reset_password(self):
        """Handle password reset"""
        email_or_id = self.email_input.text().strip()
        if not email_or_id:
            QMessageBox.warning(self, "Error", "Please enter your email or ID number.")
            return
        # Implement actual reset logic (e.g., send email or update password)
        # For now, simulate
        db = DatabaseOperations()
        try:
            # Assume we update password to a new one (in real, send reset link)
            new_password = "newpass123"  # Placeholder; implement properly
            # Update based on id_number (assume it's ID)
            cursor = db.conn.cursor()
            query = "UPDATE students SET password = %s WHERE id_number = %s"  # Adjust table
            hashed_pw = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            cursor.execute(query, (hashed_pw, email_or_id))
            db.conn.commit()
            if cursor.rowcount > 0:
                QMessageBox.information(self, "Reset Success", "Your password has been reset to 'newpass123'. Please change it after login.")
            else:
                QMessageBox.warning(self, "Error", "ID not found.")
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))
        finally:
            db.close_connection()
        self.email_input.clear()
        self.stacked_widget.setCurrentIndex(2)  # Back to login
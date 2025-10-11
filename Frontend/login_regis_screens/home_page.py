import sys, os
from PyQt6.QtWidgets import QApplication, QStackedWidget, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton
from PyQt6.QtGui import QFont, QPixmap
from PyQt6.QtCore import Qt

from Frontend.admin_Dashboard.admin_Add import AdminAddBook
from Frontend.admin_Dashboard.admin_Dashboard import AdminDashboard
from Frontend.admin_Dashboard.admin_Update import AdminUpdateBook
from Frontend.admin_Dashboard.admin_ViewAllBooks import AdminViewAllBooks
from Frontend.admin_Dashboard.admin_viewUsers import AdminViewUsers
from Frontend.admin_Dashboard.AdminBorrowingHistory import AdminBorrowingHistory
from Frontend.login_regis_screens.change_password_page import ForgotPasswordPage
from Frontend.login_regis_screens.login_page import LoginPage
from Frontend.login_regis_screens.registration_page import RegisterPage
from Frontend.student_Dashboard.StudentBorrowBook import StudentBorrowBook
from Frontend.student_Dashboard.student_borrowHistory import StudentBorrowHistory
from Frontend.student_Dashboard.student_dashboard import StudentDashboard
from Frontend.student_Dashboard.studentsBorrowed_book import StudentsBorrowedBook

# ===== FIX IMPORT PATH =====
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.append(project_root)

# ===== HOME PAGE =====
class HomePage(QWidget):
    def __init__(self, stacked_widget):
        super().__init__()
        self.stacked_widget = stacked_widget
        self.setWindowTitle("Library Information System")

        # ====== MAIN LAYOUT ======
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)

        # ====== NAVIGATION BAR ======
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

        main_layout.addWidget(nav_widget)

        # ====== BODY LAYOUT ======
        body_layout = QVBoxLayout()
        body_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # ====== LOGO ======
        logo_label = QLabel()
        pixmap = QPixmap(os.path.join(project_root, "login_regis_screens", "Infochan.png"))
        scaled_pixmap = pixmap.scaled(150, 150, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        logo_label.setPixmap(scaled_pixmap)
        logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # ====== TITLE ======
        title = QLabel("InfoChan")
        title.setFont(QFont("Times New Roman", 24, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # ====== SUBTITLE ======
        subtitle = QLabel(
            "A computer-based system that helps the librarian manage books\n"
            "and provides users easy access to library resources."
        )
        subtitle.setFont(QFont("Arial", 12))
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Add widgets to the layout
        body_layout.addWidget(logo_label)
        body_layout.addSpacing(10)
        body_layout.addWidget(title)
        body_layout.addWidget(subtitle)
        body_layout.addStretch()

        # Add stretch before and after body_layout for vertical centering
        main_layout.addStretch(1)
        main_layout.addLayout(body_layout)
        main_layout.addStretch(1)

        self.setLayout(main_layout)

# ====== MAIN APP ======
class MainApp(QStackedWidget):
    def __init__(self):
        super().__init__()

        # Create page instances
        self.home_page = HomePage(self)
        self.register_page = RegisterPage(self)
        self.login_page = LoginPage(self)
        self.forgot_page = ForgotPasswordPage(self)
        self.student_dashboard = StudentDashboard(self)
        self.student_borrow = StudentBorrowBook(self)
        self.student_borrowed = StudentsBorrowedBook(self)
        self.student_history = StudentBorrowHistory(self)
        self.admin_dashboard = AdminDashboard(self)
        self.admin_add = AdminAddBook(self)
        self.admin_update = AdminUpdateBook(self)
        self.admin_view_books = AdminViewAllBooks(self)
        self.admin_view_users = AdminViewUsers(self)
        self.admin_borrowing_history = AdminBorrowingHistory(self)

        # Add to stacked widget
        self.addWidget(self.home_page)              # index 0
        self.addWidget(self.register_page)          # index 1
        self.addWidget(self.login_page)             # index 2
        self.addWidget(self.forgot_page)            # index 3
        self.addWidget(self.student_dashboard)      # index 4
        self.addWidget(self.student_borrow)         # index 5
        self.addWidget(self.student_borrowed)       # index 6
        self.addWidget(self.student_history)        # index 7
        self.addWidget(self.admin_dashboard)        # index 8
        self.addWidget(self.admin_add)              # index 9
        self.addWidget(self.admin_update)           # index 10
        self.addWidget(self.admin_view_books)       # index 11
        self.addWidget(self.admin_view_users)       # index 12
        self.addWidget(self.admin_borrowing_history)  # index 13

        self.setCurrentIndex(0)

# ====== APP ENTRY POINT ======
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainApp()
    window.setWindowTitle("Library Information System")
    window.showMaximized()
    sys.exit(app.exec())
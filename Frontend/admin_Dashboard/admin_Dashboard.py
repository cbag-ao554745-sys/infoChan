from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QFrame, QLabel, QSpacerItem, QSizePolicy, QGridLayout
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from db.db_operations import DatabaseOperations

class ColorScheme:
    PRIMARY_GRADIENT = ("#667eea", "#764ba2")
    SUCCESS_GRADIENT = ("#10b981", "#059669")
    WARNING_GRADIENT = ("#f59e0b", "#d97706")
    INFO_GRADIENT = ("#3b82f6", "#2563eb")
    PURPLE_GRADIENT = ("#8b5cf6", "#7c3aed")
    DANGER_GRADIENT = ("#ef4444", "#dc2626")
    DARK_GRADIENT = ("#4b5563", "#1f2937")
    STUDENT_GRADIENT = ("#f87171", "#dc2626")
    INSTRUCTOR_GRADIENT = ("#60a5fa", "#2563eb")
    TEAL_GRADIENT = ("#14b8a6", "#0f766e")
    CATEGORY_COLORS = [
        ("#f59e0b", "#d97706"),  # Fiction
        ("#10b981", "#059669"),  # Science
        ("#8b5cf6", "#7c3aed"),  # History
        ("#ec4899", "#be185d"),  # Technology
        ("#3b82f6", "#1d4ed8"),  # Arts
        ("#14b8a6", "#0f766e"),  # Education
    ]

class AdminDashboard(QWidget):
    def __init__(self, stacked_widget):
        super().__init__()
        self.stacked_widget = stacked_widget
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)

        # Header Row
        header_frame = QFrame()
        header_layout = QHBoxLayout(header_frame)
        header_layout.setContentsMargins(0, 0, 0, 0)

        header = QLabel("📚 InfoChan")
        header.setStyleSheet("font-size: 28px; font-weight: bold; color: #2d3748;")
        header_layout.addWidget(header, alignment=Qt.AlignmentFlag.AlignLeft)

        header_layout.addItem(QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))

        logout_btn = QPushButton("🚪 LOGOUT")
        logout_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        logout_btn.setStyleSheet(self._button_style(ColorScheme.DANGER_GRADIENT))
        logout_btn.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(0))
        header_layout.addWidget(logout_btn)

        layout.addWidget(header_frame)

        # Navigation Buttons
        nav_frame = QFrame()
        nav_layout = QHBoxLayout(nav_frame)
        nav_layout.setSpacing(20)

        nav_items = [
            ("📊 DASHBOARD", ColorScheme.PRIMARY_GRADIENT, 8),
            ("➕ ADD BOOK", ColorScheme.SUCCESS_GRADIENT, 9),
            ("✏️ UPDATE BOOK", ColorScheme.WARNING_GRADIENT, 10),
            ("📖 VIEW ALL BOOKS", ColorScheme.INFO_GRADIENT, 11),
            ("👥 VIEW USERS", ColorScheme.PURPLE_GRADIENT, 12),
            ("📜 BORROWING HISTORY", ColorScheme.TEAL_GRADIENT, 13),
        ]

        for text, color, idx in nav_items:
            btn = QPushButton(text)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setStyleSheet(self._button_style(ColorScheme.PRIMARY_GRADIENT) if idx == 8 else self._button_style(color))
            btn.clicked.connect(lambda checked, i=idx: self.stacked_widget.setCurrentIndex(i))
            nav_layout.addWidget(btn)

        layout.addWidget(nav_frame)

        # Stats Section
        stats_frame = QFrame()
        stats_layout = QGridLayout(stats_frame)
        stats_layout.setSpacing(20)

        self.total_books = self._stat_box("Total Books", "0", ColorScheme.PRIMARY_GRADIENT)
        self.borrowed_books = self._stat_box("Borrowed Books", "0", ColorScheme.WARNING_GRADIENT)
        self.users_box = self._stat_box("Total Users", "0", ColorScheme.STUDENT_GRADIENT)
        self.student_box = self._stat_box("Students", "0", ColorScheme.STUDENT_GRADIENT)
        self.instructor_box = self._stat_box("Instructors", "0", ColorScheme.INSTRUCTOR_GRADIENT)

        stats_layout.addWidget(self.total_books, 0, 0)
        stats_layout.addWidget(self.borrowed_books, 0, 1)
        stats_layout.addWidget(self.users_box, 0, 2)
        stats_layout.addWidget(self.student_box, 1, 0)
        stats_layout.addWidget(self.instructor_box, 1, 1)

        self.category_boxes = []
        categories = ["Fiction", "Science", "History", "Technology", "Arts", "Education"]
        for i, (cat, color) in enumerate(zip(categories, ColorScheme.CATEGORY_COLORS)):
            box = self._stat_box(f"{cat} Borrowed", "0", color)
            stats_layout.addWidget(box, 2 + i // 3, i % 3)
            self.category_boxes.append(box)

        layout.addWidget(stats_frame)

    def showEvent(self, event):
        """Load statistics when the widget is shown."""
        super().showEvent(event)
        self.load_stats()

    def load_stats(self):
        """Fetch and update statistics."""
        db = DatabaseOperations()
        cursor = db.conn.cursor()
        try:
            # Total Books
            cursor.execute("SELECT COUNT(*) FROM books")
            total_books = cursor.fetchone()[0]
            self.total_books.layout().itemAt(1).widget().setText(str(total_books))

            # Borrowed Books
            cursor.execute("SELECT COUNT(*) FROM borrowing_history WHERE return_status IN ('Active', 'Overdue')")
            borrowed_books = cursor.fetchone()[0]
            self.borrowed_books.layout().itemAt(1).widget().setText(str(borrowed_books))

            # Total Users
            cursor.execute("SELECT (SELECT COUNT(*) FROM students) + (SELECT COUNT(*) FROM instructors) + (SELECT COUNT(*) FROM admins)")
            total_users = cursor.fetchone()[0]
            self.users_box.layout().itemAt(1).widget().setText(str(total_users))

            # Students
            cursor.execute("SELECT COUNT(*) FROM students")
            students = cursor.fetchone()[0]
            self.student_box.layout().itemAt(1).widget().setText(str(students))

            # Instructors
            cursor.execute("SELECT COUNT(*) FROM instructors")
            instructors = cursor.fetchone()[0]
            self.instructor_box.layout().itemAt(1).widget().setText(str(instructors))

            # Categories borrowed
            categories = ["Fiction", "Science", "History", "Technology", "Arts", "Education"]
            for i, cat in enumerate(categories):
                cursor.execute(
                    "SELECT COUNT(*) FROM borrowing_history bh JOIN books b ON bh.book_id = b.id WHERE b.category = %s AND bh.return_status IN ('Active', 'Overdue')",
                    (cat,)
                )
                count = cursor.fetchone()[0]
                self.category_boxes[i].layout().itemAt(1).widget().setText(str(count))
        finally:
            cursor.close()
            db.close_connection()

    def _button_style(self, color):
        return f"""
            QPushButton {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 {color[0]}, stop:1 {color[1]});
                color: white;
                font-weight: bold;
                font-size: 14px;
                padding: 12px 24px;
                border-radius: 8px;
            }}
            QPushButton:hover {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 {color[1]}, stop:1 {color[0]});
            }}
        """

    def _stat_box(self, title, value, color):
        box = QFrame()
        box.setStyleSheet(f"""
            QFrame {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 {color[0]}, stop:1 {color[1]});
                border-radius: 12px;
            }}
        """)
        layout = QVBoxLayout(box)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(10)

        title_label = QLabel(title)
        title_label.setStyleSheet("color: white; font-size: 16px; font-weight: bold;")

        value_label = QLabel(str(value))
        value_label.setStyleSheet("color: white; font-size: 24px; font-weight: bold;")

        layout.addWidget(title_label)
        layout.addWidget(value_label)
        return box
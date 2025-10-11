from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QFrame, QLabel, QSpacerItem, QSizePolicy, QTableWidget,
    QTableWidgetItem, QHeaderView
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
    STUDENT_GRADIENT = ("#f87171", "#dc2626")


class StudentDashboard(QWidget):
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

        header = QLabel("📚 InfoChan - Student Portal")
        header.setStyleSheet("font-size: 28px; font-weight: bold; color: #2d3748;")
        header_layout.addWidget(header, alignment=Qt.AlignmentFlag.AlignLeft)

        header_layout.addItem(QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))

        self.student_info = QLabel("👨‍🎓 Loading...")
        self.student_info.setStyleSheet("font-size: 14px; font-weight: bold; color: #4b5563;")
        header_layout.addWidget(self.student_info)

        logout_btn = QPushButton("🚪 LOGOUT")
        logout_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        logout_btn.setStyleSheet(self._button_style(ColorScheme.DANGER_GRADIENT))
        logout_btn.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(2))
        header_layout.addWidget(logout_btn)

        layout.addWidget(header_frame)

        # Navigation Buttons
        nav_frame = QFrame()
        nav_layout = QHBoxLayout(nav_frame)
        nav_layout.setSpacing(20)

        nav_items = [
            ("📊 DASHBOARD", ColorScheme.PRIMARY_GRADIENT, 4),
            ("📖 BORROW BOOKS", ColorScheme.SUCCESS_GRADIENT, 5),
            ("📚 MY BORROWED BOOKS", ColorScheme.WARNING_GRADIENT, 6),
            ("📜 BORROWING HISTORY", ColorScheme.INFO_GRADIENT, 7),
        ]

        for text, color, idx in nav_items:
            btn = QPushButton(text)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setStyleSheet(
                self._button_style(ColorScheme.PRIMARY_GRADIENT) if idx == 4 else self._button_style(color))
            btn.clicked.connect(lambda checked, i=idx: self.stacked_widget.setCurrentIndex(i))
            nav_layout.addWidget(btn)

        layout.addWidget(nav_frame)

        # Info Boxes
        info_frame = QFrame()
        info_layout = QHBoxLayout(info_frame)
        info_layout.setSpacing(20)

        self.books_borrowed = self._info_box("Books Borrowed", "0", ColorScheme.SUCCESS_GRADIENT)
        self.books_due = self._info_box("Books Due", "0", ColorScheme.WARNING_GRADIENT)
        self.available_slots = self._info_box("Available Slots", "5", ColorScheme.INFO_GRADIENT)

        info_layout.addWidget(self.books_borrowed)
        info_layout.addWidget(self.books_due)
        info_layout.addWidget(self.available_slots)
        layout.addWidget(info_frame)

        # Borrowed Books Table
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["Book Title", "Category", "Borrowed Date", "Return Date"])
        self.table.setStyleSheet("""
            QTableWidget {
                background-color: white;
                gridline-color: #E5E7EB;
                border: 1px solid #D1D5DB;
                border-radius: 8px;
            }
            QHeaderView::section {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #667eea, stop:1 #764ba2);
                color: white;
                padding: 12px;
                border: none;
                font-weight: bold;
                font-size: 12pt;
            }
            QTableWidget::item {
                padding: 10px;
                color: #374151;
                font-size: 11pt;
            }
            QTableWidget::item:selected {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0.5,
                    stop:0 #DBEAFE, stop:1 #BFDBFE);
                color: #1e40af;
            }
        """)
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.verticalHeader().setVisible(False)
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        layout.addWidget(self.table)

    def showEvent(self, event):
        super().showEvent(event)
        self.load_student_data()

    def load_student_data(self):
        db = DatabaseOperations()
        try:
            # Get user data from login page
            login_page = self.stacked_widget.widget(2)
            user_id = login_page.user_data['id']
            role = login_page.selected_role

            # Get student details for display
            if role == "Student":
                cursor = db.conn.cursor()
                cursor.execute("SELECT full_name, grade_level, strand FROM students WHERE id = %s", (user_id,))
                student_result = cursor.fetchone()
                if student_result:
                    full_name, grade_level, strand = student_result
                    self.student_info.setText(f"👨‍🎓 {full_name} - {grade_level} {strand}")
                cursor.close()

            # Get borrowing history
            history = db.get_borrowing_history(user_id, role)

            # Filter for currently borrowed books (Active or Overdue)
            current_books = [book for book in history if book[7] in ["Active", "Overdue"]]
            total_borrowed = len(current_books)
            books_due = sum(1 for book in current_books if book[7] == "Overdue")

            # Calculate available slots (maximum 5 books)
            available_slots_count = max(0, 5 - total_borrowed)

            # Update info boxes
            self.populate_table(current_books)
            self.books_borrowed.layout().itemAt(1).widget().setText(str(total_borrowed))
            self.books_due.layout().itemAt(1).widget().setText(str(books_due))
            self.available_slots.layout().itemAt(1).widget().setText(str(available_slots_count))

        except Exception as e:
            print(f"Error loading student data: {e}")
            # Set default values in case of error
            self.books_borrowed.layout().itemAt(1).widget().setText("0")
            self.books_due.layout().itemAt(1).widget().setText("0")
            self.available_slots.layout().itemAt(1).widget().setText("5")
            self.student_info.setText("👨‍🎓 Error loading user info")
        finally:
            db.close_connection()

    def populate_table(self, books):
        """Populate table with currently borrowed books (Active or Overdue)"""
        self.table.setRowCount(len(books))
        for row, book in enumerate(books):
            self.table.setItem(row, 0, QTableWidgetItem(book[4]))  # title
            self.table.setItem(row, 1, QTableWidgetItem(book[10]))  # category
            self.table.setItem(row, 2, QTableWidgetItem(str(book[5])))  # borrowed_date
            return_date = book[6] if book[6] else "Not Returned"
            if book[7] == "Active":
                return_date = "Due Soon"
            elif book[7] == "Overdue":
                return_date = "OVERDUE"
            self.table.setItem(row, 3, QTableWidgetItem(str(return_date)))

            # Center align all items
            for col in range(4):
                item = self.table.item(row, col)
                if item:
                    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

            # Style overdue items
            if book[7] == "Overdue":
                for col in range(4):
                    item = self.table.item(row, col)
                    if item:
                        item.setBackground(Qt.GlobalColor.red)
                        item.setForeground(Qt.GlobalColor.white)

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
                min-width: 180px;
            }}
            QPushButton:hover {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 {color[1]}, stop:1 {color[0]});
                transform: scale(1.05);
            }}
        """

    def _info_box(self, title, value, color):
        box = QFrame()
        box.setStyleSheet(f"""
            QFrame {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 {color[0]}, stop:1 {color[1]});
                border-radius: 12px;
                min-width: 200px;
            }}
        """)
        layout = QVBoxLayout(box)
        layout.setContentsMargins(20, 15, 20, 15)
        layout.setSpacing(8)

        title_label = QLabel(title)
        title_label.setStyleSheet("color: white; font-size: 14px; font-weight: bold;")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        value_label = QLabel(str(value))
        value_label.setStyleSheet("color: white; font-size: 28px; font-weight: bold;")
        value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout.addWidget(title_label)
        layout.addWidget(value_label)
        return box
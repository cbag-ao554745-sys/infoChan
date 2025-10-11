import pymysql
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QFrame, QLabel, QSpacerItem, QSizePolicy, QTableWidget,
    QTableWidgetItem, QHeaderView, QComboBox, QLineEdit, QMessageBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from datetime import datetime, timedelta
from db.db_operations import DatabaseOperations

class ColorScheme:
    PRIMARY_GRADIENT = ("#667eea", "#764ba2")
    SUCCESS_GRADIENT = ("#10b981", "#059669")
    WARNING_GRADIENT = ("#f59e0b", "#d97706")
    INFO_GRADIENT = ("#3b82f6", "#2563eb")
    PURPLE_GRADIENT = ("#8b5cf6", "#7c3aed")
    DANGER_GRADIENT = ("#ef4444", "#dc2626")
    TEAL_GRADIENT = ("#14b8a6", "#0f766e")
    PINK_GRADIENT = ("#ec4899", "#be185d")

class StudentsBorrowedBook(QWidget):
    def __init__(self, stacked_widget):
        super().__init__()
        self.stacked_widget = stacked_widget
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)

        # Header
        header_frame = QFrame()
        header_layout = QHBoxLayout(header_frame)
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(15)

        back_btn = QPushButton("⬅️ Back")
        back_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        back_btn.setStyleSheet(self._small_button_style(ColorScheme.PURPLE_GRADIENT))
        back_btn.clicked.connect(self.go_back)
        header_layout.addWidget(back_btn)

        title_label = QLabel("📚 InfoChan - My Borrowed Books")
        title_label.setStyleSheet("font-size: 28px; font-weight: bold; color: #2d3748;")
        header_layout.addWidget(title_label, alignment=Qt.AlignmentFlag.AlignLeft)

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

        # Navigation
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
            btn.setStyleSheet(self._button_style(ColorScheme.WARNING_GRADIENT) if idx == 6 else self._button_style(color))
            btn.clicked.connect(lambda checked, i=idx: self.stacked_widget.setCurrentIndex(i))
            nav_layout.addWidget(btn)

        layout.addWidget(nav_frame)

        # Filter Section
        filter_frame = QFrame()
        filter_layout = QHBoxLayout(filter_frame)
        filter_layout.setSpacing(15)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 Search by title...")
        self.search_input.setStyleSheet(self._input_style())
        self.search_input.textChanged.connect(self.filter_books)
        filter_layout.addWidget(self.search_input)

        self.category_combo = QComboBox()
        self.category_combo.addItems(["All Categories", "Fiction", "Science", "History", "Technology", "Arts", "Education"])
        self.category_combo.setStyleSheet(self._combo_style())
        self.category_combo.currentTextChanged.connect(self.filter_books)
        filter_layout.addWidget(self.category_combo)

        layout.addWidget(filter_frame)

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
        self.table.setColumnCount(10)
        self.table.setHorizontalHeaderLabels([
            "No.", "Book Title", "Author", "Category", "ISBN",
            "Borrow Date", "Borrow Time", "Return Date", "Return Time", "Days Left"
        ])
        self.table.setStyleSheet(self._table_style())
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
            user_id = self.stacked_widget.widget(2).user_data['id']
            role = self.stacked_widget.widget(2).selected_role
            history = db.get_borrowing_history(user_id, role)
            total_borrowed = sum(1 for record in history if record[7] in ["Active", "Overdue"])
            books_due = sum(1 for record in history if record[7] == "Overdue")
            self.books_borrowed.layout().itemAt(1).widget().setText(str(total_borrowed))
            self.books_due.layout().itemAt(1).widget().setText(str(books_due))
            self.available_slots.layout().itemAt(1).widget().setText(str(5 - total_borrowed))
            self.student_info.setText(f"👨‍🎓 {self.stacked_widget.widget(2).user_data['full_name']} - Grade 11 STEM")
            self.fetch_and_populate_books()
        finally:
            db.close_connection()

    def go_back(self):
        self.stacked_widget.setCurrentIndex(4)

    def get_book_details(self, book_id):
        db = DatabaseOperations()
        try:
            cursor = db.conn.cursor()
            cursor.execute("SELECT id, category, title, author, edition, isbn, publication, status FROM books WHERE id = %s", (book_id,))
            return cursor.fetchone()
        finally:
            cursor.close()
            db.close_connection()

    def calculate_days_left(self, borrow_date, return_date, return_status):
        if return_status in ["Returned", "Returned Late"]:
            return "-"
        due_date = borrow_date + timedelta(days=7)  # Assume 7-day borrowing period
        days_left = (due_date - datetime.now()).days
        return max(0, days_left) if days_left > 0 else "Overdue"

    def filter_books(self):
        search_text = self.search_input.text().strip().lower()
        category = self.category_combo.currentText()
        self.fetch_and_populate_books(search_text, category)

    def fetch_and_populate_books(self, search_text="", category="All Categories"):
        db = DatabaseOperations()
        try:
            user_id = self.stacked_widget.widget(2).user_data['id']
            role = self.stacked_widget.widget(2).selected_role
            history = db.get_borrowing_history(user_id, role)
            filtered_books = []
            for record in history:
                if record[7] not in ["Returned", "Returned Late"]:  # Show only returned books
                    continue
                if search_text and search_text not in record[4].lower():
                    continue
                if category != "All Categories" and category and record[10] != category:
                    continue
                filtered_books.append(record)
            self.populate_table(filtered_books)
        finally:
            db.close_connection()

    def populate_table(self, books):
        self.table.setRowCount(len(books))
        for row, record in enumerate(books):
            book_details = self.get_book_details(record[3])
            if not book_details:
                continue
            self.table.setItem(row, 0, QTableWidgetItem(str(row + 1)))
            self.table.setItem(row, 1, QTableWidgetItem(record[4]))
            self.table.setItem(row, 2, QTableWidgetItem(book_details[3]))
            self.table.setItem(row, 3, QTableWidgetItem(record[10]))
            self.table.setItem(row, 4, QTableWidgetItem(book_details[5]))
            borrow_date = record[5]
            self.table.setItem(row, 5, QTableWidgetItem(borrow_date.strftime("%Y-%m-%d")))
            self.table.setItem(row, 6, QTableWidgetItem(borrow_date.strftime("%H:%M:%S")))
            return_date = record[6]
            self.table.setItem(row, 7, QTableWidgetItem(return_date.strftime("%Y-%m-%d") if return_date else "Not Returned"))
            self.table.setItem(row, 8, QTableWidgetItem(return_date.strftime("%H:%M:%S") if return_date else "Not Returned"))
            days_left = self.calculate_days_left(record[5], record[6], record[7])
            self.table.setItem(row, 9, QTableWidgetItem(str(days_left)))
            for col in range(10):
                item = self.table.item(row, col)
                if item:
                    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

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
            }}
        """

    def _small_button_style(self, color):
        return f"""
            QPushButton {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 {color[0]}, stop:1 {color[1]});
                color: white;
                font-weight: bold;
                font-size: 12px;
                padding: 8px 16px;
                border-radius: 8px;
                min-width: 110px;
            }}
            QPushButton:hover {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 {color[1]}, stop:1 {color[0]});
            }}
        """

    def _input_style(self):
        return """
            QLineEdit {
                background-color: white;
                border: 2px solid #D1D5DB;
                border-radius: 8px;
                padding: 8px 15px;
                font-size: 13px;
            }
            QLineEdit:focus {
                border: 2px solid #f59e0b;
            }
        """

    def _combo_style(self):
        return """
            QComboBox {
                background-color: white;
                border: 2px solid #D1D5DB;
                border-radius: 8px;
                padding: 8px 15px;
                font-size: 13px;
            }
            QComboBox::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 20px;
                border-left: 1px solid #D1D5DB;
            }
        """

    def _table_style(self):
        return """
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
        """

    def _info_box(self, title, value, color):
        box = QFrame()
        box.setStyleSheet(f"""
            QFrame {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 {color[0]}, stop:1 {color[1]});
                border-radius: 12px;
                padding: 20px;
            }}
        """)
        layout = QVBoxLayout(box)
        title_lbl = QLabel(title)
        title_lbl.setStyleSheet("font-size: 16px; color: white; font-weight: bold;")
        value_lbl = QLabel(value)
        value_lbl.setStyleSheet("font-size: 28px; color: white; font-weight: bold;")
        layout.addWidget(title_lbl)
        layout.addWidget(value_lbl)
        return box
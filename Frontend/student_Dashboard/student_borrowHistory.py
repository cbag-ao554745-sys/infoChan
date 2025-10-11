import pymysql
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QFrame, QLabel, QSpacerItem, QSizePolicy, QTableWidget,
    QTableWidgetItem, QHeaderView, QComboBox, QLineEdit
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
    TEAL_GRADIENT = ("#14b8a6", "#0f766e")
    INDIGO_GRADIENT = ("#6366f1", "#4f46e5")

class StudentBorrowHistory(QWidget):
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

        header = QLabel("📚 InfoChan - Borrowing History")
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
            btn.setStyleSheet(self._button_style(ColorScheme.INFO_GRADIENT) if idx == 7 else self._button_style(color))
            btn.clicked.connect(lambda checked, i=idx: self.stacked_widget.setCurrentIndex(i))
            nav_layout.addWidget(btn)

        layout.addWidget(nav_frame)

        # Filter Section
        filter_frame = QFrame()
        filter_layout = QHBoxLayout(filter_frame)
        filter_layout.setSpacing(15)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 Search by book title...")
        self.search_input.setStyleSheet(self._input_style())
        self.search_input.textChanged.connect(self.filter_history)
        filter_layout.addWidget(self.search_input)

        self.category_combo = QComboBox()
        self.category_combo.addItems(["All Categories", "Fiction", "Science", "History", "Technology", "Arts", "Education"])
        self.category_combo.setStyleSheet(self._combo_style())
        self.category_combo.currentTextChanged.connect(self.filter_history)
        filter_layout.addWidget(self.category_combo)

        layout.addWidget(filter_frame)

        # History Table
        self.table = QTableWidget()
        self.table.setColumnCount(9)
        self.table.setHorizontalHeaderLabels([
            "No.", "Book Title", "Author", "Category", "Borrow Date", "Return Date", "Status", "Condition", "Fine"
        ])
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
            user_id = self.stacked_widget.widget(2).user_data['id']
            role = self.stacked_widget.widget(2).selected_role
            self.student_info.setText(f"👨‍🎓 {self.stacked_widget.widget(2).user_data['full_name']} - Grade 11 STEM")
            self.fetch_and_populate_history()
        finally:
            db.close_connection()

    def get_book_details(self, book_id):
        db = DatabaseOperations()
        try:
            cursor = db.conn.cursor()
            cursor.execute("SELECT id, category, title, author, edition, isbn, publication, status FROM books WHERE id = %s", (book_id,))
            return cursor.fetchone()
        finally:
            cursor.close()
            db.close_connection()

    def filter_history(self):
        search_text = self.search_input.text().strip().lower()
        category = self.category_combo.currentText()
        self.fetch_and_populate_history(search_text, category)

    def fetch_and_populate_history(self, search_text="", category="All Categories"):
        db = DatabaseOperations()
        try:
            user_id = self.stacked_widget.widget(2).user_data['id']
            role = self.stacked_widget.widget(2).selected_role
            history = db.get_borrowing_history(user_id, role)
            filtered_history = []
            for record in history:
                title = record[4].lower()
                cat = record[10]
                if search_text and search_text not in title:
                    continue
                if category != "All Categories" and category and cat != category:
                    continue
                filtered_history.append(record)
            self.populate_table(filtered_history)
        finally:
            db.close_connection()

    def populate_table(self, history):
        self.table.setRowCount(len(history))
        for row, record in enumerate(history):
            book_details = self.get_book_details(record[3])
            if not book_details:
                continue
            self.table.setItem(row, 0, QTableWidgetItem(str(row + 1)))
            self.table.setItem(row, 1, QTableWidgetItem(record[4]))
            self.table.setItem(row, 2, QTableWidgetItem(book_details[3]))
            self.table.setItem(row, 3, QTableWidgetItem(record[10]))
            self.table.setItem(row, 4, QTableWidgetItem(str(record[5])))
            self.table.setItem(row, 5, QTableWidgetItem(str(record[6]) if record[6] else "Not Yet Returned"))
            status_item = QTableWidgetItem(record[7])
            if record[7] == "Returned":
                status_item.setForeground(Qt.GlobalColor.darkGreen)
            elif record[7] == "Active":
                status_item.setForeground(Qt.GlobalColor.darkBlue)
            elif record[7] == "Overdue":
                status_item.setForeground(Qt.GlobalColor.darkRed)
            elif record[7] == "Returned Late":
                status_item.setForeground(Qt.GlobalColor.darkYellow)
            self.table.setItem(row, 6, status_item)
            condition_item = QTableWidgetItem(record[8])
            self.table.setItem(row, 7, condition_item)
            fine_item = QTableWidgetItem(f"₱{record[9]:.2f}")
            if record[9] > 0:
                fine_item.setForeground(Qt.GlobalColor.darkRed)
            else:
                fine_item.setForeground(Qt.GlobalColor.darkGreen)
            self.table.setItem(row, 8, fine_item)
            for col in range(9):
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

    def _active_button_style(self, color):
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
                border: 3px solid white;
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
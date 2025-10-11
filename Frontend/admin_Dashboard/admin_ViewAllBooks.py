from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QComboBox, QTableWidget, QTableWidgetItem,
    QFrame, QHeaderView, QMessageBox, QSpacerItem, QSizePolicy
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
import os

from db.db_operations import DatabaseOperations

class ColorScheme:
    PRIMARY_GRADIENT = ("#667eea", "#764ba2")
    SUCCESS_GRADIENT = ("#10b981", "#059669")
    WARNING_GRADIENT = ("#f59e0b", "#d97706")
    INFO_GRADIENT = ("#3b82f6", "#2563eb")
    PURPLE_GRADIENT = ("#8b5cf6", "#7c3aed")
    DANGER_GRADIENT = ("#ef4444", "#dc2626")
    TEAL_GRADIENT = ("#14b8a6", "#0f766e")

class AdminViewAllBooks(QWidget):
    def __init__(self, stacked_widget):
        super().__init__()
        self.stacked_widget = stacked_widget
        self._setup_ui()
        self.view_all_books()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)

        # --- HEADER ROW ---
        header_frame = QFrame()
        header_layout = QHBoxLayout(header_frame)
        header_layout.setContentsMargins(0, 0, 0, 0)

        header = QLabel("📚 InfoChan - View All Books")
        header.setStyleSheet("font-size: 28px; font-weight: bold; color: #2d3748;")
        header_layout.addWidget(header, alignment=Qt.AlignmentFlag.AlignLeft)

        header_layout.addItem(QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))

        admin_info = QLabel("👩‍💼 Admin User")
        admin_info.setStyleSheet("font-size: 14px; font-weight: bold; color: #4b5563;")
        header_layout.addWidget(admin_info)

        logout_btn = QPushButton("🚪 LOGOUT")
        logout_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        logout_btn.setStyleSheet(self._button_style(ColorScheme.DANGER_GRADIENT))
        logout_btn.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(2))  # Updated to index 2 (LoginPage)
        header_layout.addWidget(logout_btn)

        layout.addWidget(header_frame)

        # --- NAVIGATION BUTTONS ---
        nav_frame = QFrame()
        nav_layout = QHBoxLayout(nav_frame)
        nav_layout.setSpacing(15)
        nav_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

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
            btn.setStyleSheet(self._active_button_style(ColorScheme.INFO_GRADIENT) if idx == 11 else self._button_style(color))
            btn.clicked.connect(lambda checked, i=idx: self.stacked_widget.setCurrentIndex(i))
            nav_layout.addWidget(btn)

        layout.addWidget(nav_frame)

        # --- SEARCH SECTION ---
        search_frame = QFrame()
        search_layout = QHBoxLayout(search_frame)
        search_layout.setContentsMargins(0, 0, 0, 0)
        search_layout.setSpacing(10)

        self.category_combo = QComboBox()
        self.category_combo.addItems(["Select Category", "Fiction", "Science", "History", "Technology", "Arts", "Education"])
        self.category_combo.setStyleSheet("""
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
        """)
        self.category_combo.currentTextChanged.connect(self.search_books)
        search_layout.addWidget(self.category_combo)

        view_all_btn = QPushButton("VIEW ALL")
        view_all_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #10b981, stop:1 #059669);
                color: white;
                font-weight: bold;
                padding: 10px 20px;
                border-radius: 8px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #059669, stop:1 #10b981);
            }
        """)
        view_all_btn.clicked.connect(self.view_all_books)
        search_layout.addWidget(view_all_btn)

        search_layout.addStretch()
        layout.addWidget(search_frame)

        # --- TABLE ---
        self.table = QTableWidget()
        self.table.setColumnCount(10)
        self.table.setHorizontalHeaderLabels([
            "No.", "Category", "Title", "Author", "Edition", "ISBN", "Publication", "Status", "Edit", "View"
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
                padding: 10px;
                border: none;
                font-weight: bold;
                font-size: 11pt;
            }
            QTableWidget::item {
                padding: 8px;
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

    def _button_style(self, color):
        return f"""
            QPushButton {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 {color[0]}, stop:1 {color[1]});
                color: white;
                font-weight: bold;
                font-size: 14px;
                padding: 10px 18px;
                border-radius: 8px;
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
                padding: 10px 18px;
                border-radius: 8px;
                border: 2px solid #1e40af;
            }}
            QPushButton:hover {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 {color[1]}, stop:1 {color[0]});
            }}
        """

    def view_all_books(self):
        self.category_combo.setCurrentIndex(0)
        db = DatabaseOperations()
        try:
            books = db.get_all_books()
            self.populate_table(books)
        finally:
            db.close_connection()

    def search_books(self):
        category = self.category_combo.currentText()
        if category == "Select Category":
            self.view_all_books()
            return
        db = DatabaseOperations()
        try:
            books = db.search_books_by_category(category)
            self.populate_table(books)
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to search books: {str(e)}")
        finally:
            db.close_connection()

    def populate_table(self, books):
        self.table.setRowCount(len(books))
        for row, book in enumerate(books):
            self.table.setRowHeight(row, 50)  # Increase row height for better visibility
            self.table.setItem(row, 0, QTableWidgetItem(str(row + 1)))
            self.table.setItem(row, 1, QTableWidgetItem(book[1]))  # category
            self.table.setItem(row, 2, QTableWidgetItem(book[2]))  # title
            self.table.setItem(row, 3, QTableWidgetItem(book[4]))  # author
            self.table.setItem(row, 4, QTableWidgetItem(book[3]))  # edition
            self.table.setItem(row, 5, QTableWidgetItem(book[5]))  # isbn
            self.table.setItem(row, 6, QTableWidgetItem(book[6]))  # publication
            self.table.setItem(row, 7, QTableWidgetItem(book[7]))  # status

            # Edit button
            edit_btn = QPushButton("Edit")
            edit_btn.setStyleSheet(self._button_style(ColorScheme.WARNING_GRADIENT))
            edit_btn.clicked.connect(lambda _, b=book[0]: self.edit_book(b))

            # View button
            view_btn = QPushButton("View")
            view_btn.setStyleSheet(self._button_style(ColorScheme.INFO_GRADIENT))
            view_btn.clicked.connect(lambda _, b=book: self.view_book(b))

            self.table.setCellWidget(row, 8, edit_btn)
            self.table.setCellWidget(row, 9, view_btn)

            # Center align all cells
            for col in range(8):
                item = self.table.item(row, col)
                if item:
                    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

    def edit_book(self, book_id):
        # Load book data in update page
        self.stacked_widget.widget(10).load_book_data(book_id)
        self.stacked_widget.setCurrentIndex(10)  # Go to update page

    def view_book(self, book):
        # Show book information in a message box
        info = f"Category: {book[1]}\nTitle: {book[2]}\nAuthor: {book[4]}\nEdition: {book[3]}\nISBN: {book[5]}\nPublication: {book[6]}\nStatus: {book[7]}\nReason PDF: {book[8] if len(book) > 8 else 'None'}"
        QMessageBox.information(self, "Book Information", info)
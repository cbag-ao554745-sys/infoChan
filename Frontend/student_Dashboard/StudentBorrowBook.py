import os
from datetime import datetime
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QFrame,
    QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox
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

class StudentBorrowBook(QWidget):
    def __init__(self, stacked_widget):
        super().__init__()
        self.stacked_widget = stacked_widget
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 20, 40, 20)
        layout.setSpacing(20)

        # Back Button
        back_btn = QPushButton("⬅ Back")
        back_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        back_btn.setFixedWidth(100)
        back_btn.setStyleSheet(self._button_style(ColorScheme.DARK_GRADIENT))
        back_btn.clicked.connect(self.go_back)
        layout.addWidget(back_btn, alignment=Qt.AlignmentFlag.AlignLeft)

        # Title
        header = QLabel("📚 InfoChan - Borrow Books")
        header.setStyleSheet("font-size: 24px; font-weight: bold; color: #2d3748;")
        layout.addWidget(header, alignment=Qt.AlignmentFlag.AlignCenter)

        # Available Books Header
        books_header = QLabel("📚 Available Books to Borrow")
        books_header.setStyleSheet("font-size: 20px; font-weight: bold; color: #2d3748; margin-top: 10px;")
        layout.addWidget(books_header, alignment=Qt.AlignmentFlag.AlignLeft)

        # Available Books Table
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["No.", "Title", "Author", "Category", "ISBN", "Action"])
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
        """Load available books when the widget is shown."""
        super().showEvent(event)
        self.load_available_books()

    def go_back(self):
        """Go to the student dashboard."""
        self.stacked_widget.setCurrentIndex(4)

    def load_available_books(self):
        """Fetch and display available books from the database."""
        db = DatabaseOperations()
        try:
            query = "SELECT id, title, author, category, isbn FROM books WHERE status = 'Available'"
            cursor = db.conn.cursor()
            cursor.execute(query)
            books = cursor.fetchall()
            self.populate_table(books)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load books: {str(e)}")
        finally:
            cursor.close()
            db.close_connection()

    def populate_table(self, books):
        """Populate the table with available books and Borrow buttons."""
        self.table.setRowCount(len(books))
        for row, book in enumerate(books):
            book_id, title, author, category, isbn = book
            self.table.setRowHeight(row, 55)  # Increase row height for better visibility
            self.table.setItem(row, 0, QTableWidgetItem(str(row + 1)))
            self.table.setItem(row, 1, QTableWidgetItem(title))
            self.table.setItem(row, 2, QTableWidgetItem(author))
            self.table.setItem(row, 3, QTableWidgetItem(category))
            self.table.setItem(row, 4, QTableWidgetItem(isbn))

            # Borrow button
            borrow_btn = QPushButton("📖 Borrow")
            borrow_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            borrow_btn.setStyleSheet(self._button_style(ColorScheme.SUCCESS_GRADIENT))
            borrow_btn.clicked.connect(lambda checked, bid=book_id, ttl=title: self.borrow_book(bid, ttl))
            self.table.setCellWidget(row, 5, borrow_btn)

            # Center align all cells
            for col in range(5):
                item = self.table.item(row, col)
                if item:
                    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

    def borrow_book(self, book_id, title):
        """Handle borrowing a book."""
        if not self.stacked_widget.widget(2).user_data:
            QMessageBox.warning(self, "Not Logged In", "Please log in to borrow a book.")
            return

        user_id = self.stacked_widget.widget(2).user_data['id']
        db = DatabaseOperations()
        try:
            # Check borrowing limit
            history = db.get_borrowing_history(user_id, self.stacked_widget.widget(2).selected_role)
            active_books = [record for record in history if record[7] in ["Active", "Overdue"]]
            if len(active_books) >= 5:
                QMessageBox.warning(self, "Limit Reached", "You cannot borrow more than 5 books at a time.")
                return

            # Borrow the book
            success, message = db.borrow_book(user_id, "student", book_id, datetime.now())
            if success:
                QMessageBox.information(self, "Success", f"Book '{title}' borrowed successfully!")
                self.load_available_books()  # Refresh table
            else:
                QMessageBox.critical(self, "Error", f"Failed to borrow the book: {message}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error borrowing book: {str(e)}")
        finally:
            db.close_connection()

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
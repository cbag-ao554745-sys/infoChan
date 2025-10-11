from datetime import datetime

import pymysql
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QFrame,
    QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox, QSpacerItem, QSizePolicy
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

class AdminBorrowingHistory(QWidget):
    def __init__(self, stacked_widget):
        super().__init__()
        self.stacked_widget = stacked_widget
        self._setup_ui()
        self.load_borrowing_history()

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

        admin_info = QLabel("👩‍💼 Admin User")
        admin_info.setStyleSheet("font-size: 14px; font-weight: bold; color: #4b5563;")
        header_layout.addWidget(admin_info)

        logout_btn = QPushButton("🚪 LOGOUT")
        logout_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        logout_btn.setStyleSheet(self._button_style(ColorScheme.DANGER_GRADIENT))
        logout_btn.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(2))  # Updated to index 2 (LoginPage)
        header_layout.addWidget(logout_btn)

        layout.addWidget(header_frame)

        # Navigation Buttons
        nav_frame = QFrame()
        nav_layout = QHBoxLayout(nav_frame)
        nav_layout.setSpacing(15)
        nav_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)  # Center navigation buttons

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
            btn.setStyleSheet(self._button_style(ColorScheme.TEAL_GRADIENT) if idx == 13 else self._button_style(color))
            btn.clicked.connect(lambda checked, i=idx: self.stacked_widget.setCurrentIndex(i))
            nav_layout.addWidget(btn)

        layout.addWidget(nav_frame)

        # Borrowing History Table
        self.table = QTableWidget()
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels([
            "No.", "User ID", "User Type", "Book Title", "Category", "Borrow Date", "Status", "Action"
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

        # Configure Table Behavior
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.verticalHeader().setVisible(False)
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)

        layout.addWidget(self.table)

    def load_borrowing_history(self):
        """Load borrowing history from database."""
        db = DatabaseOperations()
        try:
            history = db.get_borrowing_history()
            self.populate_table(history)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load borrowing history: {str(e)}")
        finally:
            db.close_connection()

    def populate_table(self, history):
        """Populate the table with borrowing history."""
        self.table.setRowCount(len(history))
        for row, record in enumerate(history):
            self.table.setRowHeight(row, 55)  # Increase row height for better visibility
            self.table.setItem(row, 0, QTableWidgetItem(str(row + 1)))
            self.table.setItem(row, 1, QTableWidgetItem(str(record[1])))  # user_id
            self.table.setItem(row, 2, QTableWidgetItem(record[2]))  # user_type
            self.table.setItem(row, 3, QTableWidgetItem(record[4]))  # title
            self.table.setItem(row, 4, QTableWidgetItem(record[10]))  # category
            self.table.setItem(row, 5, QTableWidgetItem(str(record[5])))  # date_borrowed
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

            # Return button (only for Active or Overdue)
            if record[7] in ["Active", "Overdue"]:
                return_btn = QPushButton("Return")
                return_btn.setStyleSheet(self._button_style(ColorScheme.SUCCESS_GRADIENT))
                return_btn.clicked.connect(lambda checked, rid=record[0], bid=record[3]: self.return_book(rid, bid))
                self.table.setCellWidget(row, 7, return_btn)

            # Center align all cells
            for col in range(7):
                item = self.table.item(row, col)
                if item:
                    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

    def return_book(self, record_id, book_id):
        """Mark a book as returned."""
        db = DatabaseOperations()
        try:
            cursor = db.conn.cursor()
            cursor.execute(
                "UPDATE borrowing_history SET return_status = 'Returned', date_returned = %s WHERE id = %s",
                (datetime.now(), record_id)
            )
            cursor.execute("UPDATE books SET status = 'Available' WHERE id = %s", (book_id,))
            db.conn.commit()
            QMessageBox.information(self, "Success", "Book marked as returned.")
            self.load_borrowing_history()  # Refresh table
        except pymysql.Error as e:
            QMessageBox.critical(self, "Error", f"Failed to return book: {str(e)}")
            db.conn.rollback()
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
                padding: 10px 18px;
                border-radius: 8px;
            }}
            QPushButton:hover {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 {color[1]}, stop:1 {color[0]});
            }}
        """
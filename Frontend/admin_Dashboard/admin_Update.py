from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QFrame, QComboBox, QLineEdit,
    QMessageBox, QFormLayout
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


class AdminUpdateBook(QWidget):
    def __init__(self, stacked_widget):
        super().__init__()
        self.stacked_widget = stacked_widget
        self.book_id = None  # To store selected book ID for update
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 20, 40, 20)
        layout.setSpacing(20)

        # Header
        header = QLabel("✏️ Update Book")
        header.setStyleSheet("font-size: 24px; font-weight: bold; color: #2d3748;")
        layout.addWidget(header, alignment=Qt.AlignmentFlag.AlignCenter)

        # Frame for form
        form_frame = QFrame()
        form_frame.setStyleSheet("""
            QFrame {
                background: white;
                border-radius: 12px;
                border: 1px solid #ddd;
            }
        """)
        form_layout = QFormLayout(form_frame)
        form_layout.setContentsMargins(30, 30, 30, 30)
        form_layout.setSpacing(15)

        # Category
        self.category_combo = QComboBox()
        self.category_combo.addItems(["Fiction", "Science", "History", "Technology", "Arts", "Education"])
        form_layout.addRow("📂 Category:", self.category_combo)

        # Title
        self.title_input = QLineEdit()
        self.title_input.setPlaceholderText("Enter book title")
        form_layout.addRow("📖 Title:", self.title_input)

        # Edition
        self.edition_input = QLineEdit()
        self.edition_input.setPlaceholderText("Enter edition")
        form_layout.addRow("🔢 Edition:", self.edition_input)

        # Publication
        self.publication_input = QLineEdit()
        self.publication_input.setPlaceholderText("Enter publication")
        form_layout.addRow("🏛 Publication:", self.publication_input)

        # Author
        self.author_input = QLineEdit()
        self.author_input.setPlaceholderText("Lastname, Firstname")
        form_layout.addRow("✍️ Author:", self.author_input)

        # ISBN
        self.isbn_input = QLineEdit()
        self.isbn_input.setPlaceholderText("Only numbers, no spaces")
        form_layout.addRow("🔑 ISBN:", self.isbn_input)

        layout.addWidget(form_frame)

        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(20)

        update_btn = QPushButton("✅ Update Book")
        update_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        update_btn.setStyleSheet(self._button_style(ColorScheme.SUCCESS_GRADIENT))
        update_btn.clicked.connect(self.update_book)
        btn_layout.addWidget(update_btn)

        clear_btn = QPushButton("🧹 Clear All")
        clear_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        clear_btn.setStyleSheet(self._button_style(ColorScheme.DANGER_GRADIENT))
        clear_btn.clicked.connect(self.confirm_clear)
        btn_layout.addWidget(clear_btn)

        back_btn = QPushButton("🔙 Back")
        back_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        back_btn.setStyleSheet(self._button_style(ColorScheme.DANGER_GRADIENT))
        back_btn.clicked.connect(self.go_back)
        btn_layout.addWidget(back_btn)

        layout.addLayout(btn_layout)

    def load_book_data(self, book_id):
        self.book_id = book_id
        db = DatabaseOperations()
        try:
            cursor = db.conn.cursor()
            query = "SELECT category, title, edition, publication, author, isbn FROM books WHERE id = %s"
            cursor.execute(query, (book_id,))
            book = cursor.fetchone()
            if book:
                self.category_combo.setCurrentText(book[0])
                self.title_input.setText(book[1])
                self.edition_input.setText(book[2])
                self.publication_input.setText(book[3])
                self.author_input.setText(book[4])
                self.isbn_input.setText(book[5])
        finally:
            db.close_connection()

    def update_book(self):
        if not self.book_id:
            QMessageBox.warning(self, "Error", "No book selected for update.")
            return

        category = self.category_combo.currentText()
        title = self.title_input.text().strip()
        edition = self.edition_input.text().strip()
        publication = self.publication_input.text().strip()
        author = self.author_input.text().strip()
        isbn = self.isbn_input.text().strip()

        if not title or not isbn:
            QMessageBox.warning(self, "Input Error", "All fields are required.")
            return
        if not isbn.isdigit():
            QMessageBox.warning(self, "Invalid ISBN", "ISBN must only contain numbers with no spaces.")
            return

        db = DatabaseOperations()
        try:
            success = db.update_book(self.book_id, category, title, edition, publication, author, isbn)
            if success:
                QMessageBox.information(self, "Book Updated", f"Book '{title}' has been updated successfully!")
                self.clear_fields()
            else:
                QMessageBox.warning(self, "Error", "Failed to update book.")
        finally:
            db.close_connection()

    def confirm_clear(self):
        reply = QMessageBox.question(
            self,
            "Clear Confirmation",
            "Are you sure you want to clear all fields?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.clear_fields()

    def clear_fields(self):
        self.category_combo.setCurrentIndex(0)
        self.title_input.clear()
        self.edition_input.clear()
        self.publication_input.clear()
        self.author_input.clear()
        self.isbn_input.clear()

    def go_back(self):
        """Go back to the previous screen in the stacked widget."""
        if self.stacked_widget is not None:
            self.stacked_widget.setCurrentIndex(8)
        else:
            QMessageBox.information(self, "Navigation", "No previous screen found.")

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
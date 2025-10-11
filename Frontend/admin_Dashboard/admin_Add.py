import os
import shutil
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QFrame, QComboBox, QLineEdit,
    QFileDialog, QMessageBox, QFormLayout
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


class AdminAddBook(QWidget):
    def __init__(self, stacked_widget):
        super().__init__()
        self.stacked_widget = stacked_widget
        self.file_path = None
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 20, 40, 20)
        layout.setSpacing(20)

        # ---------------- TITLE ----------------
        header = QLabel("➕ Add a New Book")
        header.setStyleSheet("font-size: 24px; font-weight: bold; color: #2d3748;")
        layout.addWidget(header, alignment=Qt.AlignmentFlag.AlignCenter)

        # ---------------- FORM ----------------
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

        # Upload Reason (PDF)
        self.upload_btn = QPushButton("📂 Upload Reason (PDF only)")
        self.upload_btn.clicked.connect(self.upload_file)
        self.uploaded_file = QLabel("No file selected")
        self.uploaded_file.setStyleSheet("color: gray; font-size: 12px;")
        upload_layout = QVBoxLayout()
        upload_layout.addWidget(self.upload_btn)
        upload_layout.addWidget(self.uploaded_file)
        upload_frame = QFrame()
        upload_frame.setLayout(upload_layout)
        form_layout.addRow("📝 Reason:", upload_frame)

        # Author
        self.author_input = QLineEdit()
        self.author_input.setPlaceholderText("Lastname, Firstname")
        form_layout.addRow("✍️ Author:", self.author_input)

        # ISBN
        self.isbn_input = QLineEdit()
        self.isbn_input.setPlaceholderText("Only numbers, no spaces")
        form_layout.addRow("🔑 ISBN:", self.isbn_input)

        layout.addWidget(form_frame)

        # Action Buttons (Save + Clear)
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(20)

        save_btn = QPushButton("✅ Save Book")
        save_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        save_btn.setStyleSheet(self._button_style(ColorScheme.SUCCESS_GRADIENT))
        save_btn.clicked.connect(self.save_book)
        btn_layout.addWidget(save_btn)

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

    def upload_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Upload Reason", "", "PDF Files (*.pdf)")
        if file_path:
            if not file_path.lower().endswith(".pdf"):
                QMessageBox.warning(self, "Invalid File", "Only PDF files are allowed.")
                return
            self.file_path = file_path
            self.uploaded_file.setText(os.path.basename(file_path))
            self.uploaded_file.setStyleSheet("color: green; font-size: 12px;")

    def save_book(self):
        category = self.category_combo.currentText()
        title = self.title_input.text().strip()
        edition = self.edition_input.text().strip()
        publication = self.publication_input.text().strip()
        author = self.author_input.text().strip()
        isbn = self.isbn_input.text().strip()

        # Validation
        if not title or not edition or not publication or not author or not isbn:
            QMessageBox.warning(self, "Input Error", "All fields are required.")
            return

        if not isbn.isdigit():
            QMessageBox.warning(self, "Invalid ISBN", "ISBN must only contain numbers with no spaces.")
            return

        if self.uploaded_file.text() == "No file selected":
            QMessageBox.warning(self, "File Missing", "Please upload a reason in PDF format.")
            return

        # Save PDF to uploads folder
        upload_dir = "uploads"
        os.makedirs(upload_dir, exist_ok=True)
        pdf_name = self.uploaded_file.text()
        dest_path = os.path.join(upload_dir, pdf_name)
        shutil.copy(self.file_path, dest_path)

        db = DatabaseOperations()
        try:
            success = db.add_book(category, title, edition, publication, author, isbn, dest_path)
            if success:
                QMessageBox.information(
                    self,
                    "Book Saved",
                    f"Book '{title}' has been added successfully!\n"
                    f"Category: {category}\nEdition: {edition}\nPublication: {publication}\n"
                    f"Author: {author}\nISBN: {isbn}\nReason: {self.uploaded_file.text()}"
                )
                self.clear_fields()
        finally:
            db.close_connection()

    # ---------------- CLEAR FIELDS ----------------
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
        self.uploaded_file.setText("No file selected")
        self.uploaded_file.setStyleSheet("color: gray; font-size: 12px;")

    # ---------------- BACK FUNCTION ----------------
    def go_back(self):
        """Return to admin dashboard."""
        if self.stacked_widget is not None:
            self.stacked_widget.setCurrentIndex(8)  # Go back to admin dashboard (index 8)
        else:
            QMessageBox.information(self, "Navigation", "Back navigation unavailable.")
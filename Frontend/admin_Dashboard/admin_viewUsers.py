from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QTableWidget, QTableWidgetItem,
    QComboBox, QHeaderView, QLabel, QSpacerItem, QSizePolicy, QFrame
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

class AdminViewUsers(QWidget):
    def __init__(self, stacked_widget):
        super().__init__()
        self.stacked_widget = stacked_widget
        self.init_ui()
        self.load_all_users()

    def init_ui(self):
        # --- Main Layout ---
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)

        # --- HEADER ROW ---
        header_frame = QFrame()
        header_layout = QHBoxLayout(header_frame)
        header_layout.setContentsMargins(0, 0, 0, 0)

        header = QLabel("📚 InfoChan - View All Users")
        header.setStyleSheet("font-size: 28px; font-weight: bold; color: #2d3748;")
        header_layout.addWidget(header, alignment=Qt.AlignmentFlag.AlignLeft)

        header_layout.addItem(QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))

        # Admin info
        admin_info = QLabel("👩‍💼 Admin User")
        admin_info.setStyleSheet("font-size: 14px; font-weight: bold; color: #4b5563;")
        header_layout.addWidget(admin_info)

        logout_btn = QPushButton("🚪 LOGOUT")
        logout_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        logout_btn.setStyleSheet(self._button_style(ColorScheme.DANGER_GRADIENT))
        logout_btn.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(2))  # LoginPage
        header_layout.addWidget(logout_btn)

        main_layout.addWidget(header_frame)

        # --- Navigation Buttons ---
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
            btn.setStyleSheet(self._active_button_style(ColorScheme.PURPLE_GRADIENT) if idx == 12 else self._button_style(color))
            btn.clicked.connect(lambda checked, i=idx: self.stacked_widget.setCurrentIndex(i))
            nav_layout.addWidget(btn)

        main_layout.addWidget(nav_frame)

        # --- FILTER SECTION ---
        filter_frame = QFrame()
        filter_layout = QHBoxLayout(filter_frame)
        filter_layout.setContentsMargins(0, 0, 0, 0)
        filter_layout.setSpacing(10)

        self.user_type_combo = QComboBox()
        self.user_type_combo.addItems(["All Users", "Student", "Instructor"])
        self.user_type_combo.setStyleSheet("""
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
        self.user_type_combo.currentTextChanged.connect(self.filter_by_user_type)
        filter_layout.addWidget(self.user_type_combo)

        filter_layout.addStretch()
        main_layout.addWidget(filter_frame)

        # --- TABLE ---
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["No.", "User Type", "Name", "Course", "Year", "ID"])
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

        main_layout.addWidget(self.table)

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
                border: 2px solid #1e40af;
            }}
            QPushButton:hover {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 {color[1]}, stop:1 {color[0]});
            }}
        """

    def load_all_users(self):
        """Load all users into the table"""
        self.user_type_combo.setCurrentIndex(0)  # Reset to "All Users"
        db = DatabaseOperations()
        try:
            users = db.get_all_users()
            self.populate_table(users)
        finally:
            db.close_connection()

    def filter_by_user_type(self):
        """Filter users based on selected user type"""
        user_type = self.user_type_combo.currentText()
        db = DatabaseOperations()
        try:
            users = db.get_all_users()
            if user_type != "All Users":
                filtered_users = [user for user in users if user.get("type", "").lower() == user_type.lower()]
            else:
                filtered_users = users
            self.populate_table(filtered_users)
        finally:
            db.close_connection()

    def populate_table(self, users):
        """Populate table with user data"""
        self.table.setRowCount(len(users))

        for row, user in enumerate(users):
            self.table.setItem(row, 0, QTableWidgetItem(str(user.get("no", row + 1))))
            self.table.setItem(row, 1, QTableWidgetItem(user.get("type", "")))
            self.table.setItem(row, 2, QTableWidgetItem(user.get("name", "")))
            self.table.setItem(row, 3, QTableWidgetItem(user.get("course", "")))
            self.table.setItem(row, 4, QTableWidgetItem(user.get("year", "")))
            self.table.setItem(row, 5, QTableWidgetItem(user.get("id", "")))

            # Center align all cells
            for col in range(6):
                item = self.table.item(row, col)
                if item:
                    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
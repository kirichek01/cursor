import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame, QLineEdit, QListWidget, QListWidgetItem, QSizePolicy, QSpacerItem, QGridLayout
)
from PyQt6.QtGui import QFont, QIcon, QColor, QPixmap
from PyQt6.QtCore import Qt

class DashboardWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('WasteBank Dashboard')
        self.setGeometry(100, 100, 1280, 860)
        self.setStyleSheet("background-color: #23243A;")
        self.initUI()

    def initUI(self):
        main_widget = QWidget()
        main_layout = QHBoxLayout(main_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        self.setCentralWidget(main_widget)

        # Боковое меню
        sidebar = self.create_sidebar()
        main_layout.addWidget(sidebar)

        # Центральная часть (Dashboard)
        dashboard = self.create_dashboard()
        main_layout.addWidget(dashboard)
        main_layout.setStretch(0, 1)
        main_layout.setStretch(1, 4)

    def create_sidebar(self):
        sidebar = QFrame()
        sidebar.setFixedWidth(220)
        sidebar.setStyleSheet("background-color: #23243A; border-top-left-radius: 20px; border-bottom-left-radius: 20px;")
        layout = QVBoxLayout()
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(18)
        # Логотип
        logo = QLabel("WasteBank")
        logo.setFont(QFont('Montserrat', 18, QFont.Weight.Bold))
        logo.setStyleSheet("color: #fff;")
        layout.addWidget(logo)
        # Меню
        menu_items = [
            ("Dashboard", True),
            ("Customer", False),
            ("Catagory", False),
            ("Transaction", False),
            ("Pick-up", False),
            ("Stock", False),
            ("Financial", False),
            ("Raport", False),
        ]
        for name, active in menu_items:
            btn = QPushButton(name)
            btn.setFont(QFont('Montserrat', 12))
            if active:
                btn.setStyleSheet("color: #fff; background: #3a3b5a; border-radius: 8px; padding: 10px 16px; text-align: left;")
            else:
                btn.setStyleSheet("color: #bfc9da; background: transparent; text-align: left; padding: 10px 16px; border: none;")
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setFixedHeight(40)
            layout.addWidget(btn)
        layout.addStretch()
        # Профиль/подвал
        profile = QLabel("WB Bersinar")
        profile.setFont(QFont('Montserrat', 10))
        profile.setStyleSheet("color: #bfc9da; background: #2a2b45; border-radius: 12px; padding: 10px 16px;")
        layout.addWidget(profile)
        sidebar.setLayout(layout)
        return sidebar

    def create_dashboard(self):
        dashboard = QFrame()
        dashboard.setStyleSheet("background: transparent;")
        layout = QVBoxLayout()
        layout.setContentsMargins(32, 24, 32, 24)
        layout.setSpacing(18)
        dashboard.setLayout(layout)

        # Верхняя панель (Overview, поиск, профиль)
        top_panel = QHBoxLayout()
        title = QLabel("Overview")
        title.setFont(QFont('Montserrat', 20, QFont.Weight.Bold))
        title.setStyleSheet("color: #fff;")
        top_panel.addWidget(title)
        top_panel.addStretch()
        search = QLineEdit()
        search.setPlaceholderText("Search 'waste in'")
        search.setFixedWidth(260)
        search.setStyleSheet("background: #23243A; color: #bfc9da; border-radius: 12px; padding: 8px 16px; border: 1px solid #35365c;")
        top_panel.addWidget(search)
        # Профиль справа
        profile_box = QFrame()
        profile_box.setStyleSheet("background: #23243A; border-radius: 16px; padding: 8px 18px;")
        profile_layout = QHBoxLayout()
        profile_label = QLabel("Ceptari Tyas")
        profile_label.setFont(QFont('Montserrat', 12, QFont.Weight.Bold))
        profile_label.setStyleSheet("color: #fff;")
        profile_layout.addWidget(profile_label)
        # Аватар (заглушка)
        avatar = QLabel()
        avatar.setFixedSize(36, 36)
        avatar.setStyleSheet("background: #3a3b5a; border-radius: 18px;")
        profile_layout.addWidget(avatar)
        profile_box.setLayout(profile_layout)
        top_panel.addWidget(profile_box)
        layout.addLayout(top_panel)

        # Карточки Overview (Customer, Employees, Request)
        cards_layout = QHBoxLayout()
        for icon, label, value, color in [
            (None, "Customer", "1,300", "#a259ff"),
            (None, "Employees", "42", "#fbc858"),
            (None, "Request", "128", "#ff6a6a"),
        ]:
            card = QFrame()
            card.setFixedSize(180, 80)
            card.setStyleSheet(f"background: #28294a; border-radius: 16px;")
            card_layout = QVBoxLayout()
            card_layout.setContentsMargins(16, 10, 16, 10)
            card_layout.setSpacing(2)
            label_widget = QLabel(label)
            label_widget.setFont(QFont('Montserrat', 11))
            label_widget.setStyleSheet("color: #bfc9da;")
            value_widget = QLabel(value)
            value_widget.setFont(QFont('Montserrat', 20, QFont.Weight.Bold))
            value_widget.setStyleSheet(f"color: {color};")
            card_layout.addWidget(label_widget)
            card_layout.addWidget(value_widget)
            card.setLayout(card_layout)
            cards_layout.addWidget(card)
        cards_layout.addStretch()
        layout.addLayout(cards_layout)

        # Средний блок: Pie chart + Total category waste + Customer based region
        mid_layout = QHBoxLayout()
        # Pie chart и Customer based region
        left_mid = QFrame()
        left_mid.setStyleSheet("background: #28294a; border-radius: 20px;")
        left_mid.setFixedSize(340, 220)
        left_mid_layout = QVBoxLayout()
        left_mid_layout.setContentsMargins(18, 18, 18, 18)
        left_mid_layout.setSpacing(8)
        left_mid_layout.addWidget(QLabel("Customer based region"))
        # Заглушка под pie chart
        pie = QLabel("Pie Chart")
        pie.setAlignment(Qt.AlignmentFlag.AlignCenter)
        pie.setStyleSheet("color: #bfc9da; font-size: 16px;")
        left_mid_layout.addWidget(pie)
        left_mid.setLayout(left_mid_layout)
        mid_layout.addWidget(left_mid)
        # Total category waste
        right_mid = QFrame()
        right_mid.setStyleSheet("background: #28294a; border-radius: 20px;")
        right_mid.setFixedSize(220, 220)
        right_mid_layout = QVBoxLayout()
        right_mid_layout.setContentsMargins(18, 18, 18, 18)
        right_mid_layout.setSpacing(8)
        right_mid_layout.addWidget(QLabel("Total category waste"))
        right_mid_layout.addWidget(QLabel("20"))
        right_mid_layout.addWidget(QLabel("Total waste in"))
        right_mid_layout.addWidget(QLabel("564 kg"))
        right_mid_layout.addWidget(QLabel("Total waste out"))
        right_mid_layout.addWidget(QLabel("1205 kg"))
        right_mid.setLayout(right_mid_layout)
        mid_layout.addWidget(right_mid)
        mid_layout.addStretch()
        layout.addLayout(mid_layout)

        # Нижний блок: Waste In & Out (график) + Last Transaction
        bottom_layout = QHBoxLayout()
        # Waste In & Out (график)
        chart_frame = QFrame()
        chart_frame.setStyleSheet("background: #28294a; border-radius: 20px;")
        chart_frame.setFixedSize(540, 220)
        chart_layout = QVBoxLayout()
        chart_layout.setContentsMargins(18, 18, 18, 18)
        chart_layout.setSpacing(8)
        chart_layout.addWidget(QLabel("Waste In & Out"))
        # Заглушка под график
        chart = QLabel("Line Chart")
        chart.setAlignment(Qt.AlignmentFlag.AlignCenter)
        chart.setStyleSheet("color: #bfc9da; font-size: 16px;")
        chart_layout.addWidget(chart)
        chart_frame.setLayout(chart_layout)
        bottom_layout.addWidget(chart_frame)
        # Last Transaction
        last_frame = QFrame()
        last_frame.setStyleSheet("background: #28294a; border-radius: 20px;")
        last_frame.setFixedSize(320, 220)
        last_layout = QVBoxLayout()
        last_layout.setContentsMargins(18, 18, 18, 18)
        last_layout.setSpacing(8)
        last_layout.addWidget(QLabel("Last Transaction"))
        # Список транзакций (заглушка)
        for i in range(5):
            tx = QLabel(f"Deposit Waste   $2{i}1")
            tx.setStyleSheet("color: #bfc9da; font-size: 14px;")
            last_layout.addWidget(tx)
        last_frame.setLayout(last_layout)
        bottom_layout.addWidget(last_frame)
        bottom_layout.addStretch()
        layout.addLayout(bottom_layout)

        return dashboard

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = DashboardWindow()
    window.show()
    sys.exit(app.exec()) 
# --- Цвета и Градиенты ---
MAIN_BACKGROUND_COLOR = "#0F172A"
SIDEBAR_COLOR = "#131B2B"
CARD_BG_COLOR = "#1E1E2F"
CARD_BORDER_COLOR = "rgba(255, 255, 255, 0.1)"
ACCENT_COLOR = "#6C5ECF"

# Градиент для карточки баланса в правой колонке
BALANCE_CARD_START = "#E91E63"
BALANCE_CARD_END = "#9C27B0"

# Цвета текста
TEXT_PRIMARY = "#FFFFFF"
TEXT_SECONDARY = "#A0A0B0"

# --- Стили QSS ---
STYLESHEET = f"""
    /* --- ОСНОВНЫЕ ОКНА --- */
    #AppWindow {{
        background-color: {MAIN_BACKGROUND_COLOR};
    }}
    QFrame#sidebar, QFrame#rightColumn {{
        background-color: {SIDEBAR_COLOR};
        border: none;
    }}

    /* --- БОКОВАЯ ПАНЕЛЬ --- */
    QPushButton#navButton {{
        background-color: transparent;
        color: {TEXT_SECONDARY};
        border: none;
        text-align: left;
        padding: 12px 0px;
        font-size: 15px;
        border-radius: 8px;
    }}
    QPushButton#navButton:hover {{
        background-color: #1A2436;
    }}
    QPushButton#navButton:checked {{
        color: {TEXT_PRIMARY};
        font-weight: bold;
    }}
    QLabel#logo {{
        font-size: 22px;
        font-weight: bold;
        color: {TEXT_PRIMARY};
    }}

    /* --- УНИВЕРСАЛЬНАЯ КАРТОЧКА --- */
    .CardWidget {{
        background-color: {CARD_BG_COLOR};
        border: 1px solid {CARD_BORDER_COLOR};
        border-radius: 16px;
    }}
    .CardTitle {{
        font-size: 13px;
        color: {TEXT_SECONDARY};
        text-transform: uppercase;
    }}
    .CardValue {{
        font-size: 26px;
        font-weight: bold;
        color: {TEXT_PRIMARY};
    }}
    
    /* --- ПРАВАЯ КОЛОНКА --- */
    #RightBalanceCard {{
        border: none;
        background: qlineargradient(
            spread:pad, x1:0, y1:0, x2:1, y2:1,
            stop:0 {BALANCE_CARD_START}, stop:1 {BALANCE_CARD_END}
        );
    }}
    #RightBalanceCard QLabel {{
        background: transparent;
        color: white;
    }}
    #RecentSignalsList QLabel {{
        font-size: 14px;
    }}
"""
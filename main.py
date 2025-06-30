import os
# Явно указываем Qt-биндинг, чтобы pyqtgraph не переключился на PyQt5
os.environ['QT_API'] = 'pyside6'

import sys
from PySide6.QtWidgets import QApplication
import pyqtgraph as pg
import qdarkstyle

# (Необязательно) отключаем аппаратный OpenGL, если есть зависания
pg.setConfigOption('useOpenGL', False)
pg.setConfigOption('enableExperimental', True)

# Импортируем наше новое главное окно из правильного места
from ui.windows.main_window import MainWindow


def main() -> None:
    """Точка входа приложения."""
    app = QApplication(sys.argv)          # <‑‑ обязательно до создания виджетов!
    
    try:
        # Попытка применить стиль QDarkStyle
        app.setStyleSheet(qdarkstyle.load_stylesheet(qt_api='pyside6'))
    except (ImportError, FileNotFoundError):
        # Если не удалось, применяем стиль из нашего theme.py
        try:
            from ui.theme import STYLESHEET
            app.setStyleSheet(STYLESHEET)
        except ImportError:
            print("Could not load any stylesheet.")

    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
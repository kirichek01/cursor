import os
# Явно указываем Qt-биндинг, чтобы pyqtgraph не переключился на PyQt5
os.environ['QT_API'] = 'pyside6'

import sys
from PySide6.QtWidgets import QApplication
import pyqtgraph as pg

# (Необязательно) отключаем аппаратный OpenGL, если есть зависания
pg.setConfigOption('useOpenGL', False)
pg.setConfigOption('enableExperimental', True)

from ui.main_window import MainWindow


def main() -> None:
    """Точка входа приложения."""
    app = QApplication(sys.argv)          # <‑‑ обязательно до создания виджетов!
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
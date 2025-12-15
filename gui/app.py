import sys
from PyQt5.QtWidgets import QApplication
from qfluentwidgets import setTheme, Theme

from gui.main_window import MainWindow


def run():
    app = QApplication(sys.argv)

    # Tema inicial (oscuro por defecto)
    setTheme(Theme.DARK)

    window = MainWindow()
    window.show()

    sys.exit(app.exec_())


if __name__ == "__main__":
    run()

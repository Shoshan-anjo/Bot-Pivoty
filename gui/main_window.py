# gui/main_window.py

from qfluentwidgets import (
    FluentWindow,
    FluentIcon,
    NavigationItemPosition,
    NavigationToolButton,
    setTheme,
    Theme
)

from gui.excel_manager_gui import ExcelManagerView


class MainWindow(FluentWindow):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("BotExcel")
        self.resize(800, 600)

        # -------------------------
        # Vista principal
        # -------------------------
        self.excel_view = ExcelManagerView(self)
        self.excel_view.setObjectName("excel_manager")

        self.addSubInterface(
            self.excel_view,
            FluentIcon.DOCUMENT,
            "Excels",
            position=NavigationItemPosition.TOP
        )

        # -------------------------
        # Botón de tema (sidebar abajo)
        # -------------------------
        self.theme_button = NavigationToolButton(
            FluentIcon.CONSTRACT,
            self
        )
        self.theme_button.setText("Tema: Claro")
        self.theme_button.clicked.connect(self.toggle_theme)

        self.navigationInterface.addWidget(
            widget=self.theme_button,
            routeKey="theme_switch",
            position=NavigationItemPosition.BOTTOM
        )

        # -------------------------
        # Tema inicial
        # -------------------------
        self.current_theme = Theme.LIGHT
        setTheme(self.current_theme)

    # -------------------------
    # Toggle tema
    # -------------------------
    def toggle_theme(self):
        if self.current_theme == Theme.LIGHT:
            self.current_theme = Theme.DARK
            self.theme_button.setText("Tema: Oscuro")
        else:
            self.current_theme = Theme.LIGHT
            self.theme_button.setText("Tema: Claro")

        setTheme(self.current_theme)

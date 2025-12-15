from PyQt5.QtWidgets import QWidget
from qfluentwidgets import (
    FluentWindow,
    FluentIcon,
    NavigationItemPosition,
    NavigationToolButton,
    setTheme,
    Theme
)
from dotenv import load_dotenv, dotenv_values, set_key
import os

from gui.excel_manager_gui import ExcelManagerView

class MainWindow(FluentWindow):
    def __init__(self):
        super().__init__()

        # -------------------------
        # Cargar variables de entorno
        # -------------------------
        load_dotenv()
        self.env_path = ".env"
        self.current_theme = os.getenv("THEME", "light").lower()
        self._apply_theme(self.current_theme)

        # -------------------------
        # Configuración de ventana
        # -------------------------
        self.setWindowTitle("BotExcel")
        self.resize(1200, 750)

        # -------------------------
        # Vista principal Excel
        # -------------------------
        self.excel_view = ExcelManagerView(self)
        self.excel_view.setObjectName("excel_manager")

        # Añadir la vista Excel a la navegación superior
        self.addSubInterface(
            self.excel_view,
            FluentIcon.DOCUMENT,
            "Excels",
            position=NavigationItemPosition.TOP
        )

        # -------------------------
        # Botón de cambio de tema (sidebar abajo)
        # -------------------------
        try:
            self.theme_button = NavigationToolButton(self)
            self._update_theme_text()
            self.theme_button.setIcon(FluentIcon.CONSTRACT)
            self.theme_button.clicked.connect(self.toggle_theme)

            # Añadir correctamente el widget a la interfaz de navegación
            self.navigationInterface.addWidget(
                widget=self.theme_button,
                routeKey="theme_switch",
                position=NavigationItemPosition.BOTTOM
            )
        except Exception as e:
            print(f"Error al agregar botón de tema: {e}")

    # -------------------------
    # Aplicar tema
    # -------------------------
    def _apply_theme(self, theme_name):
        if theme_name.lower() == "light":
            setTheme(Theme.LIGHT)
        else:
            setTheme(Theme.DARK)

    # -------------------------
    # Actualizar texto del botón de tema
    # -------------------------
    def _update_theme_text(self):
        if hasattr(self, 'theme_button'):
            self.theme_button.setText(f"Tema: {self.current_theme.capitalize()}")

    # -------------------------
    # Cambiar tema
    # -------------------------
    def toggle_theme(self):
        if self.current_theme == "light":
            self.current_theme = "dark"
        else:
            self.current_theme = "light"
        self._apply_theme(self.current_theme)
        self._update_theme_text()
        self._save_theme_env()

    # -------------------------
    # Guardar tema en .env sin eliminar otras variables
    # -------------------------
    def _save_theme_env(self):
        env_vars = dotenv_values(self.env_path)
        env_vars["THEME"] = self.current_theme
        with open(self.env_path, "w") as f:
            for k, v in env_vars.items():
                f.write(f"{k}={v}\n")

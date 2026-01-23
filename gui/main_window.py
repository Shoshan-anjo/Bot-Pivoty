from PyQt5.QtWidgets import QSystemTrayIcon, QMenu, QAction
from PyQt5.QtGui import QIcon

from qfluentwidgets import (
    FluentWindow,
    FluentIcon,
    NavigationItemPosition,
    NavigationToolButton,
    setTheme,
    Theme,
    InfoBar,
    InfoBarPosition
)
from PyQt5.QtCore import QObject, pyqtSignal, Qt

from dotenv import load_dotenv, dotenv_values
import os

from gui.excel_manager_gui import ExcelManagerView
from gui.mail_settings_view import MailSettingsView
from infrastructure.scheduler_service import SchedulerService
from infrastructure.logger_service import LoggerService
from application.execute_refresh_uc import execute_refresh
from core.utils import resource_path




class StatusCommunicator(QObject):
    """Clase para comunicar hilos secundarios con la GUI principal de forma segura."""
    notify_signal = pyqtSignal(str, str)


class MainWindow(FluentWindow):

    def __init__(self):
        super().__init__()

        # -------------------------
        # Cargar variables de entorno
        # -------------------------
        load_dotenv()
        self.env_path = ".env"
        self.env = dotenv_values(self.env_path)

        # Comunicador de hilos
        self.communicator = StatusCommunicator()
        self.communicator.notify_signal.connect(self._safe_notify_job_status)


        # -------------------------
        # Tema
        # -------------------------
        self.current_theme = self.env.get("THEME", "light").lower()
        self._apply_theme(self.current_theme)

        # -------------------------
        # Configuración de ventana
        # -------------------------
        self.setWindowTitle("Pivoty")
        self.setWindowIcon(QIcon(resource_path("assets/LogoIconoDino.ico")))
        self.resize(1200, 750)



        # -------------------------
        # Vistas principales
        # -------------------------
        self.excel_view = ExcelManagerView(self)
        self.excel_view.setObjectName("excel_manager")

        self.mail_view = MailSettingsView(self)
        self.mail_view.setObjectName("mail_settings")

        # -------------------------
        # Navegación lateral
        # -------------------------
        self.addSubInterface(
            self.excel_view,
            FluentIcon.DOCUMENT,
            "Excels",
            position=NavigationItemPosition.TOP
        )

        self.addSubInterface(
            self.mail_view,
            FluentIcon.MAIL,
            "Correo",
            position=NavigationItemPosition.TOP
        )

        # -------------------------
        # Botón de cambio de tema (barra lateral abajo)
        # -------------------------
        self.theme_button = NavigationToolButton(self)
        self.theme_button.setIcon(FluentIcon.CONSTRACT)
        self.theme_button.clicked.connect(self.toggle_theme)
        self._update_theme_text()

        self.navigationInterface.addWidget(
            widget=self.theme_button,
            routeKey="theme_switch",
            position=NavigationItemPosition.BOTTOM
        )

        # -------------------------
        # Scheduler (Servicio de fondo)
        # -------------------------
        self._init_scheduler()
        self._init_tray()

    def _init_scheduler(self):
        logger_service = LoggerService(
            log_level=self.env.get("LOG_LEVEL", "INFO"),
            log_dir=self.env.get("LOG_DIR", "logs"),
            log_name=self.env.get("LOG_FILE", "pivoty.log")
        )
        self.logger = logger_service.get_logger()
        
        self.scheduler = SchedulerService(
            logger=self.logger,
            execute_fn=execute_refresh,
            status_callback=self.communicator.notify_signal.emit
        )

        self.scheduler.start_in_thread()
        self.logger.info("Scheduler iniciado correctamente desde la GUI (hilo separado).")

    def _init_tray(self):
        self.tray_icon = QSystemTrayIcon(self)
        # Usamos el logo personalizado para el tray
        self.tray_icon.setIcon(QIcon(resource_path("assets/LogoIconoDino.ico")))
        self.tray_icon.setToolTip("Pivoty - Automatización Activa")



        # Menú contextual del Tray
        tray_menu = QMenu()
        
        show_action = QAction("Abrir Panel", self)
        show_action.triggered.connect(self.showNormal)
        
        exit_action = QAction("Salir Completamente", self)
        exit_action.triggered.connect(self._force_quit)
        
        tray_menu.addAction(show_action)
        tray_menu.addSeparator()
        tray_menu.addAction(exit_action)
        
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.activated.connect(self._on_tray_activated)
        self.tray_icon.show()

    def _on_tray_activated(self, reason):
        if reason == QSystemTrayIcon.Trigger: # Click izquierdo
            if self.isVisible():
                self.hide()
            else:
                self.showNormal()
                self.activateWindow()

    def _force_quit(self):
        """Salida completa y limpia del programa."""
        if hasattr(self, 'scheduler'):
            self.scheduler.stop()
        
        if hasattr(self, 'tray_icon'):
            self.tray_icon.hide()
            self.tray_icon.deleteLater()
            
        from PyQt5.QtWidgets import QApplication
        QApplication.quit()
        # Forzar el fin del proceso si queda algún hilo rebelde
        import os
        os._exit(0)

    def closeEvent(self, event):
        """Sobrescribir el cierre para minimizar al tray."""
        if self.tray_icon.isVisible():
            self.hide()
            self.tray_icon.showMessage(
                "Pivoty",
                "El bot sigue funcionando en segundo plano.",
                QSystemTrayIcon.Information,
                3000
            )
            event.ignore()
        else:
            event.accept()

    def notify_job_status(self, title, message):
        """Deprecated: Use self.communicator.notify_signal.emit instead."""
        self.communicator.notify_signal.emit(title, message)

    def _safe_notify_job_status(self, title, message):
        """Método ejecutado SIEMPRE en el hilo principal de la GUI."""
        if hasattr(self, 'tray_icon') and self.tray_icon.isVisible():
            self.tray_icon.showMessage(title, message, QSystemTrayIcon.Information, 5000)
        
        # También mostrar en la vista actual si está abierta
        InfoBar.info(
            title=title,
            content=message,
            position=InfoBarPosition.TOP,
            parent=self.excel_view,
            duration=3000
        )


    # -------------------------
    # Aplicar tema
    # -------------------------
    def _apply_theme(self, theme_name):
        if theme_name == "light":
            setTheme(Theme.LIGHT)
        else:
            setTheme(Theme.DARK)

    # -------------------------
    # Actualizar texto del botón de tema
    # -------------------------
    def _update_theme_text(self):
        self.theme_button.setText(f"Tema: {self.current_theme.capitalize()}")

    # -------------------------
    # Cambiar tema
    # -------------------------
    def toggle_theme(self):
        self.current_theme = "dark" if self.current_theme == "light" else "light"
        self._apply_theme(self.current_theme)
        self._update_theme_text()
        self._save_theme_env()

    # -------------------------
    # Guardar tema en .env sin eliminar otras variables
    # -------------------------
    def _save_theme_env(self):
        env_vars = dotenv_values(self.env_path)
        env_vars["THEME"] = self.current_theme
        try:
            import ctypes
            # Remover atributo oculto si existe para poder escribir
            if os.path.exists(self.env_path):
                ctypes.windll.kernel32.SetFileAttributesW(self.env_path, 128) # 128 = Normal

            with open(self.env_path, "w", encoding="utf-8") as f:
                for k, v in env_vars.items():
                    if v is not None:
                        f.write(f"{k}={v}\n")
            
            # Restaurar atributo oculto
            ctypes.windll.kernel32.SetFileAttributesW(self.env_path, 2) # 2 = Hidden
        except Exception as e:
            print(f"No se pudo guardar el tema en .env: {e}")


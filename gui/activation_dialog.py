from PyQt5.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel
from PyQt5.QtGui import QIcon
from qfluentwidgets import (
    LineEdit, PushButton, TitleLabel, BodyLabel, 
    CaptionLabel, InfoBar, InfoBarPosition, SubtitleLabel,
    IndeterminateProgressRing, setTheme, Theme
)
from PyQt5.QtCore import Qt
from infrastructure.cloud_validator import CloudValidator
from core.utils import resource_path

class ActivationDialog(QDialog):
    def __init__(self, supabase_url, supabase_key, current_theme="dark", parent=None):
        super().__init__(parent)
        # Aplicar el tema actual del programa
        theme = Theme.DARK if current_theme.lower() == "dark" else Theme.LIGHT
        setTheme(theme)
        
        self.validator = CloudValidator(supabase_url, supabase_key)
        self.setWindowTitle("Activación de Pivoty")
        self.setWindowIcon(QIcon(resource_path("assets/LogoIconoDino.ico")))
        self.setFixedSize(450, 300)
        self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)

        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(30, 30, 30, 30)
        self.layout.setSpacing(15)

        # Encabezado
        self.title = TitleLabel("Activar Producto")
        self.layout.addWidget(self.title)

        self.desc = BodyLabel("Ingresa tu clave de licencia para empezar a usar Pivoty.")
        self.desc.setTextColor("#666666", "#aaaaaa")
        self.layout.addWidget(self.desc)

        # Campo de Clave
        self.key_input = LineEdit()
        self.key_input.setPlaceholderText("XXXX-XXXX-XXXX-XXXX")
        self.key_input.setFixedHeight(40)
        self.layout.addWidget(self.key_input)

        # Indicador de carga
        self.progress = IndeterminateProgressRing(self)
        self.progress.setVisible(False)
        self.progress.setFixedSize(30, 30)
        self.layout.addWidget(self.progress, alignment=Qt.AlignCenter)

        # Botones
        btn_layout = QHBoxLayout()
        self.btn_activate = PushButton("Activar Ahora")
        self.btn_activate.setFixedWidth(150)
        self.btn_activate.clicked.connect(self.attempt_activation)
        
        btn_layout.addStretch()
        btn_layout.addWidget(self.btn_activate)
        self.layout.addLayout(btn_layout)

        self.activated_key = None

    def attempt_activation(self):
        key = self.key_input.text().strip()
        if not key:
            InfoBar.warning(
                title="Clave vacía",
                content="Por favor ingresa una clave.",
                position=InfoBarPosition.TOP,
                parent=self
            )
            return

        self.btn_activate.setEnabled(False)
        self.progress.setVisible(True)

        # Validación remota
        success, message = self.validator.validate_key(key)

        self.progress.setVisible(False)
        self.btn_activate.setEnabled(True)

        if success:
            self.activated_key = key
            InfoBar.success(
                title="¡Activado!",
                content=message,
                position=InfoBarPosition.TOP,
                parent=self,
                duration=2000
            )
            # Esperar un poco para cerrar
            from PyQt5.QtCore import QTimer
            QTimer.singleShot(1500, self.accept)
        else:
            InfoBar.error(
                title="Error de Activación",
                content=message,
                position=InfoBarPosition.TOP,
                parent=self
            )

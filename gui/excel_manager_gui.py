from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QFileDialog, QHeaderView, QLabel
)
from PyQt5.QtGui import QFont, QRegExpValidator
from PyQt5.QtCore import QRegExp, QTimer, Qt
from qfluentwidgets import (
    TableWidget, PushButton,
    LineEdit, InfoBar, InfoBarPosition,
    FluentIcon, SwitchButton, PlainTextEdit,
    TitleLabel, SubtitleLabel, BodyLabel
)
import json
import os

CONFIG_PATH = "config/excels.json"

class ExcelManagerView(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)

        # -------------------------
        # Fuente amigable
        # -------------------------
        font = QFont("Segoe UI", 10)
        font.setStyleStrategy(QFont.PreferAntialias)
        self.setFont(font)

        self.layout = QVBoxLayout(self)
        self.layout.setSpacing(15)
        self.layout.setContentsMargins(30, 20, 30, 20)

        # -------------------------
        # Encabezado
        # -------------------------
        header_layout = QVBoxLayout()
        self.title_label = TitleLabel("Tus Archivos de Excel")
        
        self.subtitle_label = SubtitleLabel("Lista de archivos que el bot actualizará automáticamente.")
        self.subtitle_label.setTextColor("#808080", "#a0a0a0") # Light/Dark grey
        
        header_layout.addWidget(self.title_label)
        header_layout.addWidget(self.subtitle_label)
        self.layout.addLayout(header_layout)

        # -------------------------
        # Tabla
        # -------------------------
        self.table = TableWidget(self)
        self.table.setBorderVisible(True)
        self.table.setBorderRadius(8)
        self.table.setWordWrap(False)
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels([
            "Excel",
            "Backup",
            "Horario (HH:MM)",
            "Activo"
        ])
        
        # Ajustar columnas
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        
        self.layout.addWidget(self.table)

        # -------------------------
        # Botones
        # -------------------------
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)
        self.btn_add = PushButton("Añadir archivo", self, FluentIcon.ADD)
        self.btn_backup = PushButton("Asignar Backup", self, FluentIcon.FOLDER)
        self.btn_del = PushButton("Quitar de la lista", self, FluentIcon.DELETE)
        
        self.btn_save = PushButton("Guardar cambios", self, FluentIcon.SAVE)
        self.btn_save.setFixedWidth(180)

        self.btn_add.clicked.connect(self.add_excel)
        self.btn_backup.clicked.connect(self.assign_backup)
        self.btn_del.clicked.connect(self.delete_row)
        self.btn_save.clicked.connect(self.save)

        btn_layout.addWidget(self.btn_add)
        btn_layout.addWidget(self.btn_backup)
        btn_layout.addWidget(self.btn_del)
        btn_layout.addStretch()
        btn_layout.addWidget(self.btn_save)
        self.layout.addLayout(btn_layout)
        self.layout.addSpacing(10)

        self.load_data()

    # -------------------------
    # Cargar datos
    # -------------------------
    def load_data(self):
        self.table.setRowCount(0)
        if not os.path.exists(CONFIG_PATH):
            return

        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            excels = json.load(f).get("excels", [])

        for excel in excels:
            self.add_row(
                excel.get("path", ""),
                excel.get("backup", ""),
                excel.get("horario", ""),
                excel.get("activo", True)
            )

    # -------------------------
    # Agregar fila
    # -------------------------
    def add_row(self, path, backup, horario, activo):
        row = self.table.rowCount()
        self.table.insertRow(row)

        self.table.setItem(row, 0, self._item(path))
        self.table.setItem(row, 1, self._item(backup))

        # Horario como LineEdit con validador de HH:MM
        horario_edit = LineEdit()
        horario_edit.setPlaceholderText("HH:MM")
        horario_edit.setInputMask("99:99") # Obliga al formato HH:MM de forma amigable
        horario_edit.setText(horario)
        self.table.setCellWidget(row, 2, horario_edit)


        # Activo como SwitchButton
        toggle = SwitchButton(self)
        toggle.setChecked(activo)
        self.table.setCellWidget(row, 3, toggle)

    def _item(self, text):
        from PyQt5.QtWidgets import QTableWidgetItem
        item = QTableWidgetItem(text)
        item.setFlags(item.flags())  # no editable
        return item

    # -------------------------
    # Acciones
    # -------------------------
    def add_excel(self):
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Seleccionar Excel",
            "",
            "Excel (*.xlsx *.xlsm)"
        )
        if path:
            self.add_row(path, "", "", True)

    def assign_backup(self):
        row = self.table.currentRow()
        if row < 0:
            return

        path, _ = QFileDialog.getOpenFileName(
            self,
            "Seleccionar Backup",
            "",
            "Excel (*.xlsx *.xlsm)"
        )
        if path:
            self.table.item(row, 1).setText(path)

    def delete_row(self):
        row = self.table.currentRow()
        if row < 0:
            InfoBar.warning(
                title="Aviso",
                content="Por favor, selecciona una fila para eliminar",
                position=InfoBarPosition.TOP,
                parent=self
            )
            return
        
        self.table.removeRow(row)

    # -------------------------
    # Guardar configuración
    # -------------------------
    def save(self):
        excels = []

        for row in range(self.table.rowCount()):
            horario_widget = self.table.cellWidget(row, 2)
            excels.append({
                "path": self.table.item(row, 0).text(),
                "backup": self.table.item(row, 1).text(),
                "horario": horario_widget.text() if horario_widget else "",
                "activo": self.table.cellWidget(row, 3).isChecked()
            })

        try:
            os.makedirs("config", exist_ok=True)
            with open(CONFIG_PATH, "w", encoding="utf-8") as f:
                json.dump({"excels": excels}, f, indent=4)
        except Exception as e:
            InfoBar.error(
                title="Error de Guardado",
                content=f"No se pudo guardar en {CONFIG_PATH}. Verifique los permisos.",
                position=InfoBarPosition.TOP,
                parent=self
            )
            return


        # Notificar al scheduler de los cambios si estamos en MainWindow
        parent_window = self.window()
        if hasattr(parent_window, 'scheduler'):
            parent_window.scheduler.reload_jobs()

        InfoBar.success(
            title="Guardado",
            content="Configuración guardada y programador actualizado",
            position=InfoBarPosition.TOP,
            parent=self
        )

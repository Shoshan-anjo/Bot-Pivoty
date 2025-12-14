from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QFileDialog, QMessageBox
)
from qfluentwidgets import (
    TableWidget, PushButton,
    LineEdit, InfoBar, InfoBarPosition,
    FluentIcon, SwitchButton  # Cambiado ToggleSwitch a SwitchButton
)
import json
import os

CONFIG_PATH = "config/excels.json"


class ExcelManagerView(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)

        self.layout = QVBoxLayout(self)

        # Tabla
        self.table = TableWidget(self)
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels([
            "Excel",
            "Backup",
            "Horario",
            "Activo"
        ])

        self.layout.addWidget(self.table)

        # Botones
        btn_layout = QHBoxLayout()

        self.btn_add = PushButton("Agregar Excel", self, FluentIcon.ADD)
        self.btn_backup = PushButton("Asignar Backup", self, FluentIcon.FOLDER)
        self.btn_save = PushButton("Guardar", self, FluentIcon.SAVE)

        self.btn_add.clicked.connect(self.add_excel)
        self.btn_backup.clicked.connect(self.assign_backup)
        self.btn_save.clicked.connect(self.save)

        btn_layout.addWidget(self.btn_add)
        btn_layout.addWidget(self.btn_backup)
        btn_layout.addWidget(self.btn_save)

        self.layout.addLayout(btn_layout)

        self.load_data()

    # ------------------------
    # Datos
    # ------------------------
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

    def add_row(self, path, backup, horario, activo):
        row = self.table.rowCount()
        self.table.insertRow(row)

        self.table.setItem(row, 0, self._item(path))
        self.table.setItem(row, 1, self._item(backup))
        self.table.setItem(row, 2, self._item(horario))

        # Activo como SwitchButton
        toggle = SwitchButton(self)
        toggle.setChecked(activo)
        self.table.setCellWidget(row, 3, toggle)

    def _item(self, text):
        from PyQt5.QtWidgets import QTableWidgetItem
        item = QTableWidgetItem(text)
        item.setFlags(item.flags())  # no editable
        return item

    # ------------------------
    # Acciones
    # ------------------------
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

    def save(self):
        excels = []

        for row in range(self.table.rowCount()):
            excels.append({
                "path": self.table.item(row, 0).text(),
                "backup": self.table.item(row, 1).text(),
                "horario": self.table.item(row, 2).text(),
                "activo": self.table.cellWidget(row, 3).isChecked()
            })

        os.makedirs("config", exist_ok=True)
        with open(CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump({"excels": excels}, f, indent=4)

        InfoBar.success(
            title="Guardado",
            content="Configuración guardada correctamente",
            position=InfoBarPosition.TOP,
            parent=self
        )

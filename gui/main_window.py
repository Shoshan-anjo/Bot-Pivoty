from qfluentwidgets import (
    FluentWindow,
    NavigationItemPosition,
    FluentIcon
)

from gui.excel_manager_gui import ExcelManagerView


class MainWindow(FluentWindow):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("BotExcel")
        self.resize(1100, 700)

        self.excel_view = ExcelManagerView(self)

        # 🔴 ESTO ES CLAVE
        self.excel_view.setObjectName("excel_manager")

        self.addSubInterface(
            self.excel_view,
            FluentIcon.DOCUMENT,
            "Excels",
            position=NavigationItemPosition.TOP
        )

import os
import sys
import winreg

class StartupManager:
    """Gestiona el inicio automático de la aplicación en Windows mediante el Registro."""
    
    REG_KEY_PATH = r"Software\Microsoft\Windows\CurrentVersion\Run"
    APP_NAME = "BotExcel"

    @staticmethod
    def get_app_command():
        # Obtener la ruta del ejecutable de Python (venv) y el script principal
        python_exe = sys.executable
        # Asumimos que el script principal es 'gui.app' ejecutado vía modulo
        return f'"{python_exe}" -m gui.app'

    def set_startup(self, enable: bool):
        """Activa o desactiva el inicio con Windows."""
        try:
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER, 
                self.REG_KEY_PATH, 
                0, 
                winreg.KEY_SET_VALUE
            )
            
            if enable:
                command = self.get_app_command()
                winreg.SetValueEx(key, self.APP_NAME, 0, winreg.REG_SZ, command)
            else:
                try:
                    winreg.DeleteValue(key, self.APP_NAME)
                except FileNotFoundError:
                    pass # Ya estaba borrado
                    
            winreg.CloseKey(key)
            return True
        except Exception as e:
            print(f"Error al configurar inicio automático: {e}")
            return False

    def is_startup_enabled(self) -> bool:
        """Verifica si el inicio automático está activo en el Registro."""
        try:
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER, 
                self.REG_KEY_PATH, 
                0, 
                winreg.KEY_READ
            )
            try:
                value, _ = winreg.QueryValueEx(key, self.APP_NAME)
                winreg.CloseKey(key)
                return True
            except FileNotFoundError:
                winreg.CloseKey(key)
                return False
        except Exception:
            return False

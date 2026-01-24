# main.py

import sys
import os
import ctypes

from application.execute_refresh_uc import execute_refresh
from infrastructure.config_loader import ConfigLoader
from infrastructure.logger_service import LoggerService
from infrastructure.scheduler_service import SchedulerService
from infrastructure.cloud_validator import CloudValidator
from gui.activation_dialog import ActivationDialog

def main():
    # --- CHECK DE SEGURIDAD (FASE 1) ---
    if not os.path.exists(".env"):
        ctypes.windll.user32.MessageBoxW(
            0, 
            "⚠️ Error de Activación: No se encontró tu llave de acceso (.env).\n\n"
            "Por favor, contacta con Shohan para recibir tu archivo de activación de Pivoty.", 
            "Pivoty - Necesitas Activar", 
            0x10 | 0x0  # Icono de Error + Botón OK
        )
        sys.exit(1)

    config = ConfigLoader()

    logger = LoggerService(
        log_level=config.get("LOG_LEVEL", "INFO"),
        log_dir=config.get("LOG_DIR", "logs"),
        log_name=config.get("LOG_FILE", "pivoty.log")
    ).get_logger()

    if "--scheduler" in sys.argv:
        # ... (scheduler logic)
        pass
    
    # --- VALIDACIÓN DE NUBE (FASE 2) ---
    supabase_url = config.get("SUPABASE_URL")
    supabase_key = config.get("SUPABASE_KEY")
    current_license = config.get("ACTIVATION_KEY")

    if not supabase_url or not supabase_key:
        # Si no hay config de nube, no podemos validar (posible error de instalación)
        ctypes.windll.user32.MessageBoxW(0, "Error de Configuración: Faltan parámetros de conexión con el servidor.", "Pivoty", 0x10)
        sys.exit(1)

    validator = CloudValidator(supabase_url, supabase_key)
    is_valid = False
    
    if current_license:
        is_valid, msg = validator.validate_key(current_license)
    
    if not is_valid:
        # Si la validación falla (vencida, incorrecta o falta), mostramos la ventana elegante
        from gui.app import QApplication
        
        # Necesitamos una instancia de app para el diálogo
        app_instance = QApplication.instance()
        if not app_instance:
            app_instance = QApplication(sys.argv)
            
        current_theme = config.get("THEME", "dark")
        dialog = ActivationDialog(supabase_url, supabase_key, current_theme=current_theme)
        # Informar al usuario por qué salió la ventana (opcional)
        if current_license:
            dialog.desc.setText("Tu licencia ha expirado o es inválida. Ingresa una nueva.")
            dialog.desc.setStyleSheet("color: #e74c3c;") # Rojo suave

        if dialog.exec():
            _save_key_to_env(dialog.activated_key)
        else:
            sys.exit(0) 

    # --- INICIO NORMAL ---
    if "--scheduler" in sys.argv:
        # (Este bloque se repite para mantener la lógica de hilos pero ahora validado)
        scheduler = SchedulerService(config=config, logger=logger, execute_fn=execute_refresh)
        scheduler.start()
    elif "--refresh" in sys.argv:
        execute_refresh()
    else:
        from gui.app import run
        run()

def _save_key_to_env(key):
    """Guarda la clave de activación en el archivo .env manejando atributos ocultos."""
    import os
    import ctypes
    from dotenv import dotenv_values
    path = ".env"
    env_vars = dotenv_values(path)
    env_vars["ACTIVATION_KEY"] = key
    
    try:
        if os.path.exists(path):
            ctypes.windll.kernel32.SetFileAttributesW(path, 128) # Normal
        with open(path, "w", encoding="utf-8") as f:
            for k, v in env_vars.items():
                if v is not None: f.write(f"{k}={v}\n")
        ctypes.windll.kernel32.SetFileAttributesW(path, 2) # Hidden
    except:
        pass

if __name__ == "__main__":
    main()

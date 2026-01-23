# infrastructure/scheduler_service.py

import os
import time

import threading
from datetime import datetime
import schedule
from application.scheduler_uc import SchedulerUseCase
from application.execute_refresh_uc import execute_refresh
from infrastructure.logger_service import LoggerService
from infrastructure.config_loader import ConfigLoader

class SchedulerService:
    """
    Servicio que ejecuta los Excel según los horarios configurados
    en excels.json (SchedulerUseCase).
    """

    def __init__(self, config=None, logger=None, execute_fn=None, status_callback=None):
        self.config = config or ConfigLoader()
        self.logger = logger or LoggerService(self.config.get("LOG_LEVEL", "INFO")).get_logger()
        self.execute_fn = execute_fn or execute_refresh
        self.status_callback = status_callback
        self.scheduler_uc = SchedulerUseCase()
        self.jobs_threads = []
        self.is_running = False
        self._stop_event = threading.Event()

    # --------------------------
    # Registrar jobs en schedule
    # --------------------------
    def _register_jobs(self):
        active_jobs = self.scheduler_uc.get_active_jobs()

        if not active_jobs:
            self.logger.warning("No tienes archivos marcados como activos para actualizar.")
            return

        for job in active_jobs:
            excel_path = job.get("path") or job.get("excel_path")
            horario = job.get("horario")
            backup_path = job.get("backup") or job.get("backup_path")

            self.logger.info(f"Tarea programada: {excel_path} a las {horario}")

            # schedule.every().day.at(horario) ejecuta execute_refresh
            schedule.every().day.at(horario).do(self._run_job_threaded, excel_path=excel_path, backup_path=backup_path)

    # --------------------------
    # Ejecutar job en hilo separado
    # --------------------------
    def _run_job_threaded(self, excel_path, backup_path=None):
        def task():
            try:
                self.logger.info(f"=== INICIO DE TAREA AUTOMÁTICA: {excel_path} ===")
                file_name = os.path.basename(excel_path)
                
                if self.status_callback:
                    self.status_callback("Actualizando Datos", f"Procesando: {file_name}. Por favor, no abras el Excel.")

                # Pass the specific file to only refresh this one
                self.execute_fn(files=[excel_path])
                
                if self.status_callback:
                    self.status_callback("Excel Actualizado", f"Tarea completada: {file_name}")
                
                self.logger.info(f"=== FIN JOB PROGRAMADO: {excel_path} ===")
            except Exception as e:
                self.logger.error(f"FALLO CRÍTICO en hilo de ejecución {excel_path}: {str(e)}")
                if self.status_callback:
                    self.status_callback("Aviso de Error", f"No se pudo completar {os.path.basename(excel_path)}: {str(e)}")


        t = threading.Thread(target=task)
        t.start()
        self.jobs_threads.append(t)

    # --------------------------
    # Iniciar el scheduler
    # --------------------------
    def start(self):
        self.logger.info("El reloj de tareas está ENCENDIDO")
        self._register_jobs()
        self.is_running = True

        while not self._stop_event.is_set():
            schedule.run_pending()
            time.sleep(1)
        
        self.logger.info("El reloj de tareas se ha DETENIDO limpiamente.")
        self.is_running = False

    def stop(self):
        """Detiene el bucle del scheduler."""
        self.logger.info("Solicitando detención del scheduler...")
        self._stop_event.set()

    # --------------------------
    # Método para ejecutar desde GUI (no bloqueante)
    # --------------------------
    def start_in_thread(self):
        t = threading.Thread(target=self.start, daemon=True)
        t.start()
        return t

    def reload_jobs(self):
        """Limpia los jobs actuales y vuelve a cargar desde el archivo."""
        self.logger.info("Actualizando tus horarios de actualización...")
        schedule.clear()
        self.scheduler_uc = SchedulerUseCase() # Forzar recarga de disco
        self._register_jobs()
        self.logger.info("Scheduler recargado correctamente.")


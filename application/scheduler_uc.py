# application/scheduler_uc.py

import os
import json
from datetime import datetime, time
from domain.exceptions import ConfigError, RefreshJobError

SCHEDULE_FILE = "config/excels.json"

class SchedulerUseCase:
    """
    Casos de uso del Scheduler:
    - Agregar, eliminar, modificar jobs
    - Validar horarios
    - Guardar/leer excels.json
    """

    def __init__(self, schedule_file=None):
        self.schedule_file = schedule_file or SCHEDULE_FILE
        self.jobs = self._load_jobs()

    # --------------------------
    # Cargar jobs desde archivo
    # --------------------------
    def _load_jobs(self):
        if not os.path.exists(self.schedule_file):
            return []

        try:
            with open(self.schedule_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                # Soportar tanto lista directa como envoltorio "excels"
                if isinstance(data, dict) and "excels" in data:
                    return data["excels"]
                return data if isinstance(data, list) else []
        except json.JSONDecodeError:
            raise ConfigError(f"Archivo de configuración inválido: {self.schedule_file}")

    # --------------------------
    # Guardar jobs al archivo
    # --------------------------
    def _save_jobs(self):
        os.makedirs(os.path.dirname(self.schedule_file), exist_ok=True)
        with open(self.schedule_file, "w", encoding="utf-8") as f:
            json.dump({"excels": self.jobs}, f, indent=4, ensure_ascii=False)

    # --------------------------
    # Validar formato de hora HH:MM
    # --------------------------
    def _validate_time(self, horario_str):
        try:
            h, m = map(int, horario_str.split(":"))
            return time(hour=h, minute=m)
        except Exception:
            raise ValueError(f"Horario inválido: {horario_str}. Formato esperado HH:MM")

    # --------------------------
    # Agregar job
    # --------------------------
    def add_job(self, excel_path, horario, backup_path=None):
        if not os.path.exists(excel_path):
            raise RefreshJobError(f"Archivo no existe: {excel_path}")

        self._validate_time(horario)

        job = {
            "path": excel_path,
            "backup": backup_path,
            "horario": horario,
            "activo": True
        }

        self.jobs.append(job)
        self._save_jobs()
        return job

    # --------------------------
    # Eliminar job
    # --------------------------
    def remove_job(self, excel_path):
        inicial_count = len(self.jobs)
        self.jobs = [j for j in self.jobs if (j.get("path") or j.get("excel_path")) != excel_path]
        if len(self.jobs) == inicial_count:
            raise RefreshJobError(f"No se encontró job para: {excel_path}")
        self._save_jobs()

    # --------------------------
    # Activar/Desactivar job
    # --------------------------
    def set_job_active(self, excel_path, activo=True):
        found = False
        for j in self.jobs:
            path = j.get("path") or j.get("excel_path")
            if path == excel_path:
                j["activo"] = activo
                found = True
                break
        if not found:
            raise RefreshJobError(f"No se encontró job para: {excel_path}")
        self._save_jobs()

    # --------------------------
    # Listar jobs activos
    # --------------------------
    def get_active_jobs(self):
        return [j for j in self.jobs if j.get("activo", True)]

    # --------------------------
    # Buscar job por ruta
    # --------------------------
    def get_job(self, excel_path):
        for j in self.jobs:
            if j["excel_path"] == excel_path:
                return j
        return None

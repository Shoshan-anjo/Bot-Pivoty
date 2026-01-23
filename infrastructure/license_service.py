import subprocess
import hashlib

class LicenseService:
    @staticmethod
    def get_hwid():
        """ Obtiene un identificador único basado en el hardware de la PC (Motherboard Serial). """
        try:
            # Intentamos obtener el serial de la placa base (BaseBoard)
            cmd = 'wmic baseboard get serialnumber'
            output = subprocess.check_output(cmd, shell=True).decode().split('\n')
            serial = output[1].strip()
            
            if not serial or "To be filled" in serial:
                # Si falla o es genérico, intentamos el UUID del sistema
                cmd = 'wmic csproduct get uuid'
                output = subprocess.check_output(cmd, shell=True).decode().split('\n')
                serial = output[1].strip()

            # Hash para que no sea un serial crudo (más profesional)
            hwid = hashlib.sha256(serial.encode()).hexdigest().upper()[:16]
            # Formato: XXXX-XXXX-XXXX-XXXX
            formatted_hwid = "-".join([hwid[i:i+4] for i in range(0, len(hwid), 4)])
            return formatted_hwid
        except Exception as e:
            return "ERROR-GENERATING-ID"

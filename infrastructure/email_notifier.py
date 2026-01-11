# infrastructure/email_notifier.py
import os
import smtplib
from email.message import EmailMessage
import pythoncom
from dotenv import load_dotenv, dotenv_values
import win32com.client as win32


class EmailNotifier:
    def __init__(self, logger, config):
        self.logger = logger
        self.config = config

    def _get_log_snippet(self, lines=20):
        try:
            # Recargar para asegurar la ruta correcta
            load_dotenv(override=True)
            env = dotenv_values(".env")
            log_dir = env.get("LOG_DIR", "logs")
            log_file = env.get("LOG_FILE", "pivoty.log")
            log_path = os.path.abspath(os.path.join(log_dir, log_file))
            if os.path.exists(log_path):
                with open(log_path, "r", encoding="utf-8") as f:
                    content = f.readlines()
                    return "".join(content[-lines:])
        except:
            pass
        return "No se pudo recuperar el fragmento del log."


    def send_email(self, subject, body, attachments=None):
        # Recargar .env para asegurar que tenemos los destinatarios actualizados
        load_dotenv(override=True)
        env = dotenv_values(".env")

        mail_enabled = env.get("MAIL_ENABLED", "false").lower() in ("true", "1", "yes")
        use_outlook = env.get("USE_OUTLOOK_DESKTOP", "true").lower() in ("true", "1", "yes")


        if not mail_enabled:
            self.logger.info("MAIL_ENABLED=false → correo deshabilitado.")
            return

        to_addrs = [addr.strip() for addr in env.get("MAIL_TO", "").split(",") if addr.strip()]
        from_addr = env.get("MAIL_FROM")
        attach_logs = env.get("ATTACH_LOG_ON_ERROR", "false").lower() in ("true", "1", "yes")
        send_attachment = env.get("MAIL_SEND_ATTACHMENT", "true").lower() in ("true", "1", "yes")

        include_screenshots = env.get("MAIL_INCLUDE_SCREENSHOTS", "true").lower() in ("true", "1", "yes")
        include_log_snippet = env.get("MAIL_INCLUDE_LOG_SNIPPET", "true").lower() in ("true", "1", "yes")


        if not to_addrs:
            self.logger.warning("MAIL_TO vacío → no se enviará correo.")
            return

        # Enriquecer el cuerpo si hay error y está habilitado el snippet
        if include_log_snippet and ("ERROR" in subject.upper() or "FALLÓ" in body.upper()):
            body += "\n\n--- ÚLTIMAS LÍNEAS DEL REGISTRO ---\n"
            body += self._get_log_snippet()

        # Preparar adjuntos finales basados en la configuración actual
        final_attachments = []
        
        # 1. Excel (solo si MAIL_SEND_ATTACHMENT es true)
        if send_attachment and attachments:
            final_attachments.extend(attachments)

        # 2. Capturas de pantalla
        if include_screenshots:
            screenshot_dir = env.get("LOG_DIR", "logs") + "/screenshots"
            if os.path.exists(screenshot_dir):
                try:
                    screenshots = [os.path.join(screenshot_dir, f) for f in os.listdir(screenshot_dir) if f.endswith(".png")]
                    if screenshots:
                        screenshots.sort(key=os.path.getmtime, reverse=True)
                        final_attachments.extend(screenshots[:2])
                except:
                    pass

        # 3. Logs (solo en error y si ATTACH_LOG_ON_ERROR es true)
        if attach_logs and ("ERROR" in subject.upper() or "FALLÓ" in body.upper()):
            log_dir = env.get("LOG_DIR", "logs")
            log_file = env.get("LOG_FILE", "pivoty.log")
            log_path = os.path.abspath(os.path.join(log_dir, log_file))
            if os.path.exists(log_path):
                final_attachments.append(log_path)
            else:
                self.logger.warning(f"No existe el log para adjuntar: {log_path}")


        if use_outlook:
            # Enviar usando Outlook Desktop
            try:
                pythoncom.CoInitialize()
                outlook = win32.Dispatch("Outlook.Application")
                mail = outlook.CreateItem(0)
                mail.Subject = subject
                mail.Body = body
                mail.To = ";".join(to_addrs)
                if from_addr:
                    mail.SentOnBehalfOfName = from_addr

                # Usar conjunto para evitar duplicados
                for path in set(final_attachments):
                    try:
                        mail.Attachments.Add(path)
                        self.logger.info(f"Adjuntando archivo: {path}")
                    except Exception as e:
                        self.logger.warning(f"No se pudo adjuntar {path}: {e}")

                mail.Send()
                self.logger.info("Correo enviado correctamente vía Outlook Desktop.")
            except Exception as e:
                self.logger.warning(f"Fallo al enviar correo vía Outlook Desktop: {e}")
            finally:
                try:
                    pythoncom.CoUninitialize()
                except Exception:
                    pass
        else:
            # Enviar usando SMTP
            smtp_server = self.config.get("MAIL_SMTP_SERVER")
            smtp_port = int(self.config.get("MAIL_SMTP_PORT", 587))
            username = self.config.get("MAIL_FROM")
            password = self.config.get("MAIL_PASSWORD")
            use_tls = self.config.get_bool("MAIL_USE_TLS", True)

            msg = EmailMessage()
            msg["Subject"] = subject
            msg["From"] = from_addr
            msg["To"] = ", ".join(to_addrs)
            msg.set_content(body)

            for path in set(final_attachments):
                try:
                    with open(path, "rb") as f:
                        data = f.read()
                        filename = os.path.basename(path)
                        msg.add_attachment(data, maintype="application", subtype="octet-stream", filename=filename)
                    self.logger.info(f"Adjuntando archivo: {path}")
                except Exception as e:
                    self.logger.warning(f"No se pudo adjuntar {path}: {e}")

            try:
                server = smtplib.SMTP(smtp_server, smtp_port)
                if use_tls:
                    server.starttls()
                server.login(username, password)
                server.send_message(msg)
                server.quit()
                self.logger.info("Correo enviado correctamente vía SMTP.")
            except Exception as e:
                self.logger.warning(f"Error enviando correo vía SMTP: {e}")

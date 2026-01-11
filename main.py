# main.py

import sys
from application.execute_refresh_uc import execute_refresh
from infrastructure.config_loader import ConfigLoader
from infrastructure.logger_service import LoggerService
from infrastructure.scheduler_service import SchedulerService

def main():
    config = ConfigLoader()
    logger = LoggerService(
        log_level=config.get("LOG_LEVEL", "INFO"),
        log_dir=config.get("LOG_DIR", "logs"),
        log_name=config.get("LOG_FILE", "pivoty.log")
    ).get_logger()

    if "--scheduler" in sys.argv:
        scheduler = SchedulerService(
            config=config,
            logger=logger,
            execute_fn=execute_refresh
        )

        scheduler.start()
    elif "--refresh" in sys.argv:
        execute_refresh()
    else:
        from gui.app import run
        run()

if __name__ == "__main__":
    main()

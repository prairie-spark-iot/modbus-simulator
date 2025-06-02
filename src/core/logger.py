import logging
import sys
import os
from datetime import datetime
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path

from rich.console import Console
from rich.logging import RichHandler
from rich.traceback import install

# Install rich exception handler
install(show_locals=True)
console = Console()


class Logger:
    """Logger manager"""

    def __init__(self):
        self._loggers = {}
        self._setup_logging()

    def _setup_logging(self):
        """Setup logging configuration"""
        # Create logs directory in project root
        log_dir = Path(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))) / "logs"
        log_dir.mkdir(exist_ok=True)

        # Set log format
        log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        date_format = "%Y-%m-%d %H:%M:%S"

        # Create main log file handler
        main_handler = TimedRotatingFileHandler(
            filename=log_dir / "main.log",
            when="midnight",
            interval=1,
            backupCount=30,
            encoding="utf-8"
        )
        main_handler.setFormatter(logging.Formatter(log_format, date_format))

        # Create Modbus log file handler
        modbus_handler = TimedRotatingFileHandler(
            filename=log_dir / "modbus.log",
            when="midnight",
            interval=1,
            backupCount=30,
            encoding="utf-8"
        )
        modbus_handler.setFormatter(logging.Formatter(log_format, date_format))

        # Create Web log file handler
        web_handler = TimedRotatingFileHandler(
            filename=log_dir / "web.log",
            when="midnight",
            interval=1,
            backupCount=30,
            encoding="utf-8"
        )
        web_handler.setFormatter(logging.Formatter(log_format, date_format))

        # Create error log file handler
        error_handler = TimedRotatingFileHandler(
            filename=log_dir / "error.log",
            when="midnight",
            interval=1,
            backupCount=30,
            encoding="utf-8"
        )
        error_handler.setFormatter(logging.Formatter(log_format, date_format))
        error_handler.setLevel(logging.ERROR)

        # Configure root logger
        root_logger = logging.getLogger()
        root_logger.setLevel(logging.INFO)
        root_logger.addHandler(RichHandler(rich_tracebacks=True, console=console))
        root_logger.addHandler(main_handler)
        root_logger.addHandler(error_handler)

        # Configure Modbus logger
        modbus_logger = logging.getLogger("modbus")
        modbus_logger.setLevel(logging.INFO)
        modbus_logger.addHandler(modbus_handler)
        modbus_logger.addHandler(error_handler)

        # Configure Web logger
        web_logger = logging.getLogger("web")
        web_logger.setLevel(logging.INFO)
        web_logger.addHandler(web_handler)
        web_logger.addHandler(error_handler)

    def get_main_logger(self) -> logging.Logger:
        """Get main program logger"""
        if "main" not in self._loggers:
            self._loggers["main"] = logging.getLogger("main")
        return self._loggers["main"]

    def get_modbus_logger(self) -> logging.Logger:
        """Get Modbus logger"""
        if "modbus" not in self._loggers:
            self._loggers["modbus"] = logging.getLogger("modbus")
        return self._loggers["modbus"]

    def get_web_logger(self) -> logging.Logger:
        """Get Web logger"""
        if "web" not in self._loggers:
            self._loggers["web"] = logging.getLogger("web")
        return self._loggers["web"]

    def set_log_level(self, module: str, level: int):
        """Set log level for specified module"""
        if module in self._loggers:
            logger = self._loggers[module]
            logger.setLevel(level)
            self._log_level_change(module, level)

    def get_log_level(self, module: str) -> int:
        """Get log level for specified module"""
        return self._loggers.get(module, logging.INFO)

    def _log_level_change(self, module: str, level: int):
        """Log level change notification"""
        level_name = logging.getLevelName(level)
        logger = self._loggers[module]
        logger.info(f"Log level changed to: {level_name}")

    def setup_exception_hook(self):
        """Setup global exception handler hook"""

        def exception_hook(exc_type, exc_value, exc_traceback):
            self.get_main_logger().error(
                "Uncaught exception",
                exc_info=(exc_type, exc_value, exc_traceback)
            )
            sys.__excepthook__(exc_type, exc_value, exc_traceback)

        sys.excepthook = exception_hook

    def cleanup_old_logs(self, days: int = 30):
        """Clean up old log files"""
        log_dir = Path(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))) / "logs"
        current_time = datetime.now()

        for log_file in log_dir.glob("*.log*"):
            try:
                file_time = datetime.fromtimestamp(log_file.stat().st_mtime)
                if (current_time - file_time).days > days:
                    log_file.unlink()
                    self.get_main_logger().info(f"Deleted old log file: {log_file}")
            except Exception as e:
                self.get_main_logger().error(f"Error cleaning up log file: {str(e)}")


# Create logger manager instance
logger = Logger()

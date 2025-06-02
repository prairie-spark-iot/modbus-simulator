import asyncio
import signal
import sys
import threading
import time
from typing import Optional, Any

from rich.console import Console
from rich.traceback import install

from src.modbus.modbus_simulator import ModbusSimulator
from src.core.config import shared_state, BASE_CONFIG
from src.core.logger import logger
from src.web.web_monitor import run_web_monitor, app

# Install rich exception handler
install(show_locals=True)
console = Console()

# Get logger
log = logger.get_main_logger()


class Application:
    """
    Main application class
    
    Responsible for managing the lifecycle of Modbus simulator and web server,
    handling system signals and error recovery.
    """

    def __init__(self):
        """
        Initialize application
        
        Set initial state and component references.
        """
        self.simulator: Optional[ModbusSimulator] = None
        self.web_thread: Optional[threading.Thread] = None
        self.running = False
        self._shutdown_event = threading.Event()
        self._log = logger.get_main_logger()
        self._startup_lock = asyncio.Lock()
        self._error_count = 0
        self._max_errors = BASE_CONFIG.get("MAX_RETRIES", 3)
        self._error_reset_interval = 60  # Error count reset interval (seconds)
        self._last_error_reset = time.time()

    async def start(self) -> None:
        """
        Start the application
        
        Start Modbus simulator and web server in sequence, ensuring proper initialization.
        If errors occur during startup, cleanup will be performed and exceptions will be raised.
        """
        async with self._startup_lock:
            try:
                self.running = True
                self.simulator = ModbusSimulator()

                # Create Modbus simulator task
                modbus_task = asyncio.create_task(self.simulator.start())

                # Wait for Modbus simulator to start
                self._log.info("Waiting for Modbus simulator to start...")
                await asyncio.sleep(5)

                # Check if Modbus server is running
                if not shared_state.modbus_running:
                    raise Exception("Modbus server failed to start")

                self._log.info("Modbus simulator started, starting web server...")

                # Run web server in a separate thread
                self.web_thread = threading.Thread(target=self._run_web_monitor)
                self.web_thread.daemon = True
                self.web_thread.start()

                # Wait for Modbus simulator task
                await modbus_task

            except Exception as e:
                error_msg = f"Error starting application: {str(e)}"
                self._log.error(error_msg)
                shared_state.set_error(error_msg)
                await self.stop()
                raise

    def _run_web_monitor(self) -> None:
        """
        Run web server in a separate thread
        
        Handle web server startup and operation, catch and log any errors.
        """
        try:
            run_web_monitor()
        except Exception as e:
            error_msg = f"Error running web server: {str(e)}"
            self._log.error(error_msg)
            shared_state.set_error(error_msg)
            self._shutdown_event.set()

    async def stop(self) -> None:
        """
        Stop the application
        
        Stop all components in sequence, ensuring proper resource cleanup.
        """
        self.running = False
        self._shutdown_event.set()

        if self.simulator:
            try:
                await self.simulator.stop()
            except Exception as e:
                self._log.error(f"Error stopping Modbus simulator: {str(e)}")
            finally:
                self.simulator = None

        if self.web_thread and self.web_thread.is_alive():
            try:
                self.web_thread.join(timeout=5)
            except Exception as e:
                self._log.error(f"Error waiting for web server thread to end: {str(e)}")
            finally:
                self.web_thread = None

        self._log.info("Application stopped")

    async def _handle_error(self, error: Exception) -> None:
        """
        Handle errors
        
        Args:
            error: Error object
        """
        current_time = time.time()

        # Reset error count
        if current_time - self._last_error_reset >= self._error_reset_interval:
            self._error_count = 0
            self._last_error_reset = current_time
            shared_state.clear_error()
            self._log.debug("Error count reset")

        # Increment error count
        self._error_count += 1

        # Log error
        error_msg = f"Application error: {str(error)}"
        self._log.error(error_msg)
        shared_state.set_error(error_msg)

        # If error count exceeds limit, stop application
        if self._error_count >= self._max_errors:
            self._log.error(f"Error count exceeded maximum limit ({self._max_errors}), stopping application")
            await self.stop()
            raise Exception(f"Error count exceeded maximum limit ({self._max_errors})")


def handle_signal(signum: int, frame: Any) -> None:
    """
    Handle system signals
    
    Args:
        signum: Signal number
        frame: Current stack frame
    """
    log.info(f"Received signal {signum}, stopping application...")
    asyncio.create_task(app.stop())


async def main() -> None:
    """
    Main function
    
    Set up signal handlers, create and start application instance.
    Handle keyboard interrupts and exceptions.
    """
    try:
        # Register signal handlers
        signal.signal(signal.SIGINT, handle_signal)
        signal.signal(signal.SIGTERM, handle_signal)

        app = Application()
        try:
            await app.start()
        except KeyboardInterrupt:
            log.info("Received keyboard interrupt signal")
        except Exception as e:
            await app._handle_error(e)
            sys.exit(1)
        finally:
            await app.stop()
    except Exception as e:
        log.error(f"Program exited with error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        log.info("Program stopped")
    except Exception as e:
        log.error(f"Program exited with error: {str(e)}")
        sys.exit(1)

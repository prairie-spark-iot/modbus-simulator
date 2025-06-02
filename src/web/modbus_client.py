import asyncio
from typing import Optional

from pymodbus.client import AsyncModbusTcpClient

from src.core.config import BASE_CONFIG, shared_state
from src.core.logger import logger


class ModbusClientManager:
    """Modbus client manager"""

    def __init__(self):
        """Initialize Modbus client manager"""
        self._client: Optional[AsyncModbusTcpClient] = None
        self._lock = asyncio.Lock()
        self._connection_attempts = 0
        self._log = logger.get_web_logger()
        self._running = False

    async def start(self) -> None:
        """Start Modbus client manager"""
        self._running = True
        self._log.info("Starting Modbus client...")
        try:
            # Try to establish initial connection
            await self.get_client()
        except Exception as e:
            self._log.error(f"Failed to establish initial Modbus connection: {str(e)}")
            raise

    async def stop(self) -> None:
        """Stop Modbus client manager"""
        self._running = False
        await self.close()
        self._log.info("Modbus client stopped")

    async def get_client(self) -> AsyncModbusTcpClient:
        """Get or create Modbus client"""
        async with self._lock:
            if self._client is None or not self._client.connected:
                if self._connection_attempts >= BASE_CONFIG.get("MAX_RETRIES", 3):
                    raise Exception(
                        f"Failed to connect to Modbus server after {BASE_CONFIG.get('MAX_RETRIES', 3)} attempts")

                self._client = AsyncModbusTcpClient(
                    BASE_CONFIG["MODBUS_HOST"],
                    port=BASE_CONFIG["MODBUS_PORT"],
                    timeout=BASE_CONFIG.get("READ_TIMEOUT", 1.0),
                    retries=BASE_CONFIG.get("MAX_RETRIES", 3),
                    reconnect_delay=2.0,
                )
                try:
                    await self._client.connect()
                    shared_state.clear_error()
                    self._connection_attempts = 0
                    self._log.info("Successfully connected to Modbus server")
                except Exception as e:
                    error_msg = f"Failed to connect to Modbus server (attempt {self._connection_attempts + 1}/{BASE_CONFIG.get('MAX_RETRIES', 3)}): {str(e)}"
                    shared_state.set_error(error_msg)
                    self._connection_attempts += 1
                    self._log.warning(error_msg)
                    await asyncio.sleep(BASE_CONFIG.get("RETRY_INTERVAL", 5))
                    raise
            return self._client

    async def close(self) -> None:
        """Close Modbus client"""
        if self._client is not None:
            await self._client.close()
            self._client = None


# Create Modbus client manager instance
modbus_client_manager = ModbusClientManager()

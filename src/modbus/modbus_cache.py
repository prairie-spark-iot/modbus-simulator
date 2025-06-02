import asyncio
import time
from typing import Dict, List, Optional, Tuple

from src.core.logger import logger


class ModbusCache:
    """Modbus data cache manager"""

    def __init__(self, timeout: int = 5):
        """
        Initialize cache manager
        
        Args:
            timeout: Cache timeout in seconds
        """
        self._data_cache: Dict[str, Tuple[List[Dict], float]] = {}
        self._cache_timeout = timeout
        self._last_cache_cleanup = time.time()
        self._cache_cleanup_interval = 300  # Cache cleanup interval (seconds)
        self._cache_lock = asyncio.Lock()
        self._log = logger.get_modbus_logger()

    async def get(self, slave_id: int) -> Optional[List[Dict]]:
        """
        Get cached data
        
        Args:
            slave_id: Slave ID
            
        Returns:
            Optional[List[Dict]]: Cached data list, returns None if cache doesn't exist or expired
        """
        async with self._cache_lock:
            current_time = time.time()
            cache_key = f"slave_{slave_id}"

            if cache_key in self._data_cache:
                data, timestamp = self._data_cache[cache_key]
                if current_time - timestamp <= self._cache_timeout:
                    return data

            return None

    async def set(self, slave_id: int, data: List[Dict]) -> None:
        """
        Update data cache
        
        Args:
            slave_id: Slave ID
            data: Data list to cache
        """
        async with self._cache_lock:
            cache_key = f"slave_{slave_id}"
            self._data_cache[cache_key] = (data, time.time())

    async def cleanup(self) -> None:
        """
        Clean up expired cache
        
        Delete data that exceeds cache timeout.
        """
        async with self._cache_lock:
            current_time = time.time()
            if current_time - self._last_cache_cleanup < self._cache_cleanup_interval:
                return

            expired_keys = []
            for key, (data, timestamp) in self._data_cache.items():
                if current_time - timestamp > self._cache_timeout:
                    expired_keys.append(key)

            for key in expired_keys:
                del self._data_cache[key]

            if expired_keys:
                self._log.debug(f"Cleaned up {len(expired_keys)} expired cache entries")

            self._last_cache_cleanup = current_time

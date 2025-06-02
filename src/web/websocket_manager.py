import asyncio
import time
from datetime import datetime
from typing import Dict, Optional, Set

import orjson
from fastapi import WebSocket

from src.core.config import BASE_CONFIG, shared_state
from src.core.logger import logger


class ConnectionManager:
    """Base connection manager class"""

    def __init__(self, max_connections: int = 100):
        self.connections: Set[WebSocket] = set()
        self._lock = asyncio.Lock()
        self._max_connections = max_connections
        self._last_heartbeat: Dict[WebSocket, float] = {}
        self._heartbeat_timeout = BASE_CONFIG["HEARTBEAT_TIMEOUT"]
        self._log = logger.get_web_logger()

    async def connect(self, websocket: WebSocket) -> None:
        """Add new WebSocket connection"""
        async with self._lock:
            if len(self.connections) >= self._max_connections:
                raise Exception("Maximum connection limit reached")
            await websocket.accept()
            self.connections.add(websocket)
            self._last_heartbeat[websocket] = time.time()
            self._log.info(f"New WebSocket connection established, current connections: {len(self.connections)}")

    async def disconnect(self, websocket: WebSocket) -> None:
        """Remove WebSocket connection"""
        async with self._lock:
            if websocket in self.connections:
                self.connections.remove(websocket)
                self._log.info(f"WebSocket connection closed, current connections: {len(self.connections)}")
            else:
                self._log.warning("Attempting to disconnect non-existent WebSocket connection")
            if websocket in self._last_heartbeat:
                del self._last_heartbeat[websocket]

    async def update_heartbeat(self, websocket: WebSocket) -> None:
        """Update connection heartbeat time"""
        async with self._lock:
            self._last_heartbeat[websocket] = time.time()

    async def check_heartbeats(self) -> None:
        """Check heartbeat status for all connections"""
        try:
            current_time = time.time()
            disconnected = []

            async with self._lock:
                for websocket in self.connections:
                    last_heartbeat = self._last_heartbeat.get(websocket)
                    if last_heartbeat is None or current_time - last_heartbeat > self._heartbeat_timeout:
                        self._log.warning("Connection heartbeat timeout, disconnecting")
                        disconnected.append(websocket)

            for websocket in disconnected:
                await self.disconnect(websocket)

            if disconnected:
                self._log.info(f"Disconnected {len(disconnected)} timeout connections")

        except Exception as e:
            self._log.error(f"Error checking heartbeats: {str(e)}")


class DeviceConnectionManager(ConnectionManager):
    """Device connection manager"""

    def __init__(self):
        super().__init__()
        self._device_states: Dict[str, Dict] = {}
        self._last_update_time: Dict[str, str] = {}

    async def connect(self, websocket: WebSocket) -> None:
        """Add new device WebSocket connection"""
        await super().connect(websocket)
        # Send initial device status
        initial_data = {
            "type": "device_status",
            "timestamp": datetime.now().isoformat(),
            "devices": self._device_states
        }
        await websocket.send_text(orjson.dumps(initial_data).decode())

    async def broadcast(self, message: str) -> None:
        """Broadcast message to all connected clients"""
        async with self._lock:
            disconnected = []
            for connection in self.connections:
                try:
                    self._log.debug(f"Broadcasting message to connection: {message[:100]}...")
                    await connection.send_text(message)
                except Exception as e:
                    self._log.error(f"Error sending WebSocket message: {str(e)}")
                    disconnected.append(connection)

            for connection in disconnected:
                await self.disconnect(connection)

    async def update_device_state(self, device_id: str, device_data: Dict) -> None:
        """Update device state"""
        try:
            async with self._lock:
                self._device_states[device_id] = device_data
                self._last_update_time[device_id] = datetime.now().isoformat()
                self._log.debug(f"Device {device_id} state updated")
        except Exception as e:
            self._log.error(f"Error updating device {device_id} state: {str(e)}")


class SystemConnectionManager(ConnectionManager):
    """System status connection manager"""

    def __init__(self):
        super().__init__()
        self._broadcast_queue = asyncio.Queue()
        self._broadcast_task: Optional[asyncio.Task] = None

    async def connect(self, websocket: WebSocket) -> None:
        """Add new system status WebSocket connection"""
        await super().connect(websocket)
        # Send initial system status
        initial_data = await self._prepare_system_status()
        await websocket.send_text(orjson.dumps(initial_data).decode())

    async def start(self) -> None:
        """Start broadcast task"""
        self._broadcast_task = asyncio.create_task(self._process_broadcast_queue())

    async def stop(self) -> None:
        """Stop broadcast task"""
        if self._broadcast_task:
            self._broadcast_task.cancel()
            try:
                await self._broadcast_task
            except asyncio.CancelledError:
                pass

    async def _process_broadcast_queue(self) -> None:
        """Process messages in broadcast queue"""
        while True:
            try:
                message = await self._broadcast_queue.get()
                await self._broadcast_message(message)
                self._broadcast_queue.task_done()
            except asyncio.CancelledError:
                break
            except Exception as e:
                self._log.error(f"Error processing system status broadcast queue: {str(e)}")
                await asyncio.sleep(1)

    async def _broadcast_message(self, message: str) -> None:
        """Broadcast system status message to all system status connections"""
        async with self._lock:
            disconnected = []
            for connection in self.connections:
                try:
                    await connection.send_text(message)
                except Exception as e:
                    self._log.error(f"Error sending system status WebSocket message: {str(e)}")
                    disconnected.append(connection)

            for connection in disconnected:
                await self.disconnect(connection)

    async def broadcast_system_status(self, message: str) -> None:
        """Add system status message to broadcast queue"""
        await self._broadcast_queue.put(message)

    async def _prepare_system_status(self) -> dict:
        """Prepare system status data"""
        return {
            "type": "system_status",
            "timestamp": datetime.now().isoformat(),
            "modbus_running": shared_state.modbus_running,
            "web_running": shared_state.web_running
        }


class WebSocketManager:
    """WebSocket manager"""

    def __init__(self):
        self.device_manager = DeviceConnectionManager()
        self.system_manager = SystemConnectionManager()
        self._message_handlers = {
            'heartbeat': self._handle_heartbeat,
            'request_data': self._handle_data_request,
            'control': self._handle_control
        }
        self._heartbeat_task: Optional[asyncio.Task] = None

    async def connect(self, websocket: WebSocket, is_system: bool = False) -> None:
        """Add new WebSocket connection"""
        if is_system:
            await self.system_manager.connect(websocket)
        else:
            await self.device_manager.connect(websocket)

    async def disconnect(self, websocket: WebSocket) -> None:
        """Remove WebSocket connection"""
        await self.device_manager.disconnect(websocket)
        await self.system_manager.disconnect(websocket)

    async def update_heartbeat(self, websocket: WebSocket) -> None:
        """Update connection heartbeat time"""
        if websocket in self.device_manager.connections:
            await self.device_manager.update_heartbeat(websocket)
        if websocket in self.system_manager.connections:
            await self.system_manager.update_heartbeat(websocket)

    async def broadcast(self, message: str) -> None:
        """Broadcast message to all device connections"""
        await self.device_manager.broadcast(message)

    async def broadcast_system_status(self, message: str) -> None:
        """Add system status message to broadcast queue"""
        await self.system_manager.broadcast_system_status(message)

    async def _handle_heartbeat(self, websocket: WebSocket, message: Dict) -> None:
        """Handle heartbeat message"""
        await self.update_heartbeat(websocket)

    async def _handle_data_request(self, websocket: WebSocket, message: Dict) -> None:
        """Handle data request message"""
        device_id = message.get("deviceId")
        request_type = message.get("requestType", "all")
        log = logger.get_web_logger()
        try:
            log.debug(f"Processing data request: deviceId={device_id}, requestType={request_type}")
            if device_id:
                device_status = shared_state.get_device_status(int(device_id))
                if device_status:
                    await self.device_manager.update_device_state(device_id, device_status)
                    # Send single device status
                    response = {
                        "type": "device_update",
                        "device_id": device_id,
                        "data": device_status,
                        "timestamp": datetime.now().isoformat()
                    }
                    await websocket.send_text(orjson.dumps(response).decode())
            else:
                all_devices = shared_state.get_all_device_status()
                for device_id, status in all_devices.items():
                    await self.device_manager.update_device_state(str(device_id), status)
                # Send complete device status
                response = {
                    "type": "device_status",
                    "timestamp": datetime.now().isoformat(),
                    "devices": {str(k): v for k, v in all_devices.items()}
                }
                await websocket.send_text(orjson.dumps(response).decode())

            status_update = await self.system_manager._prepare_system_status()
            await websocket.send_text(orjson.dumps(status_update).decode())

        except Exception as e:
            log.error(f"Error processing data request: {str(e)}")

    async def _handle_control(self, websocket: WebSocket, message: Dict) -> None:
        """Handle control command message"""
        device_id = message.get("deviceId")
        register_type = message.get("registerType")
        address = message.get("address")
        value = message.get("value")

        if all([device_id, register_type, address, value is not None]):
            try:
                from src.web.modbus_client import modbus_client_manager
                client = await modbus_client_manager.get_client()
                if register_type == "CO":
                    await client.write_coil(address, bool(value), unit=int(device_id))
                elif register_type == "HR":
                    await client.write_register(address, int(value), unit=int(device_id))

                device_status = shared_state.get_device_status(int(device_id))
                if device_status:
                    await self.device_manager.update_device_state(device_id, device_status)

                self.device_manager._log.info(
                    f"Control command executed: device={device_id}, type={register_type}, address={address}, value={value}")
            except Exception as e:
                self.device_manager._log.error(f"Error executing control command: {str(e)}")

    async def _check_heartbeats(self) -> None:
        """Periodically check heartbeats"""
        while True:
            try:
                await self.device_manager.check_heartbeats()
                await self.system_manager.check_heartbeats()
                await asyncio.sleep(30)  # Check every 30 seconds
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.device_manager._log.error(f"Error checking heartbeats: {str(e)}")
                await asyncio.sleep(5)

    async def start(self) -> None:
        """Start heartbeat check task"""
        self._heartbeat_task = asyncio.create_task(self._check_heartbeats())

    async def stop(self) -> None:
        """Stop heartbeat check task"""
        if self._heartbeat_task:
            self._heartbeat_task.cancel()
            try:
                await self._heartbeat_task
            except asyncio.CancelledError:
                pass


# Create WebSocket manager instance
ws_manager = WebSocketManager()

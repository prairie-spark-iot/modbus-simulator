import asyncio
from datetime import datetime

import orjson

from src.core.config import BASE_CONFIG, shared_state
from src.core.logger import logger
from src.web.modbus_client import modbus_client_manager
from src.web.websocket_manager import ws_manager


async def poll_and_emit_modbus_data():
    """Poll Modbus data and emit via WebSocket"""
    while True:
        try:
            # If Modbus server is running, get device data
            if shared_state.modbus_running:
                try:
                    client = await modbus_client_manager.get_client()
                    device_status = shared_state.get_all_device_status()

                    # Convert device IDs to strings
                    devices_dict = {str(device_id): status for device_id, status in device_status.items()}

                    # Send individual update messages for each device
                    for device_id, status in devices_dict.items():
                        device_update = {
                            "type": "device_update",
                            "device_id": device_id,
                            "data": status,
                            "timestamp": datetime.now().isoformat()
                        }
                        logger.get_web_logger().debug(f"Sending device {device_id} update: {device_update}")
                        await ws_manager.broadcast(orjson.dumps(device_update).decode())

                    # Also send complete device status
                    device_data = {
                        "type": "device_status",
                        "timestamp": datetime.now().isoformat(),
                        "devices": devices_dict
                    }
                    logger.get_web_logger().debug(f"Sending complete device status: {device_data}")
                    await ws_manager.broadcast(orjson.dumps(device_data).decode())

                except Exception as e:
                    error_msg = f"Error getting Modbus data: {str(e)}"
                    logger.get_web_logger().error(error_msg)
                    shared_state.set_error(error_msg)
            else:
                logger.get_web_logger().warning("Modbus server not running, skipping data push")

        except Exception as e:
            error_msg = f"Error polling Modbus data: {str(e)}"
            logger.get_web_logger().error(error_msg)
            shared_state.set_error(error_msg)

        await asyncio.sleep(3)  # Push data every 3 seconds


async def poll_and_emit_system_status():
    """Poll system status and emit via WebSocket"""
    while True:
        try:
            # Prepare system status data to send
            system_data = {
                "type": "system_status",
                "timestamp": datetime.now().isoformat(),
                "modbus_running": shared_state.modbus_running,
                "web_running": shared_state.web_running,
                "error": shared_state.last_error,
                "error_time": shared_state.last_error_time.isoformat() if shared_state.last_error_time else None
            }

            # Send system status to all system status connections
            await ws_manager.broadcast_system_status(orjson.dumps(system_data).decode())

        except Exception as e:
            error_msg = f"Error polling system status: {str(e)}"
            logger.get_web_logger().error(error_msg)
            shared_state.set_error(error_msg)

        await asyncio.sleep(BASE_CONFIG["WS_PUSH_INTERVAL"])


async def start_background_tasks():
    """Start background tasks"""
    asyncio.create_task(poll_and_emit_modbus_data())
    asyncio.create_task(poll_and_emit_system_status())
    asyncio.create_task(ws_manager._check_heartbeats())

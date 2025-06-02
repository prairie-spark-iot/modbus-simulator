from fastapi import APIRouter, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from src.core.config import shared_state
from src.core.logger import logger
from src.web.websocket_manager import ws_manager

# Create router and templates
router = APIRouter()
templates = Jinja2Templates(directory="templates")
log = logger.get_web_logger()


@router.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """Return home page"""
    return templates.TemplateResponse(
        "index.html",
        {"request": request, "devices": shared_state.get_all_device_status()}
    )


@router.get("/api/status")
async def get_status():
    """Get system status"""
    devices_status = shared_state.get_all_device_status()
    # Ensure returned data includes CO data
    for device in devices_status:
        device['co_data'] = shared_state.get_co_data(device['id'])
    return {
        "modbus_running": shared_state.modbus_running,
        "web_running": shared_state.web_running,
        "last_error": shared_state.last_error,
        "last_error_time": shared_state.last_error_time,
        "devices": devices_status
    }


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint - Device status updates"""
    await ws_manager.connect(websocket)
    try:
        while True:
            try:
                data = await websocket.receive_json()
                if data.get("type") == "heartbeat":
                    await ws_manager.update_heartbeat(websocket)
            except WebSocketDisconnect:
                break
            except Exception as e:
                log.error(f"Error processing WebSocket message: {str(e)}")
    finally:
        await ws_manager.disconnect(websocket)


@router.websocket("/ws/system")
async def system_websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint - System status updates"""
    await ws_manager.connect(websocket, is_system=True)
    try:
        while True:
            try:
                data = await websocket.receive_json()
                if data.get("type") == "heartbeat":
                    await ws_manager.update_heartbeat(websocket)
            except WebSocketDisconnect:
                break
            except Exception as e:
                log.error(f"Error processing system status WebSocket message: {str(e)}")
    finally:
        await ws_manager.disconnect(websocket)

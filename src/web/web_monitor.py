import sys
import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.staticfiles import StaticFiles

from src.core.config import BASE_CONFIG, shared_state
from src.core.logger import logger
from src.web.modbus_client import modbus_client_manager
from src.web.routes import router
from src.web.tasks import start_background_tasks
from src.web.websocket_manager import ws_manager

# Create FastAPI application
app = FastAPI(
    title="Modbus Web Monitor",
    description="Real-time Web application for monitoring Modbus device status",
    version="1.0.0",
    docs_url="/docs" if BASE_CONFIG["DEBUG"] else None,
    redoc_url="/redoc" if BASE_CONFIG["DEBUG"] else None
)

# Add middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Mount static files
static_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "static")
app.mount("/static", StaticFiles(directory=static_dir), name="static")

# Register routes
app.include_router(router)


@app.on_event("startup")
async def startup_event():
    """Handle application startup"""
    shared_state.web_running = True
    await ws_manager.start()
    await start_background_tasks()


@app.on_event("shutdown")
async def shutdown_event():
    """Handle application shutdown"""
    shared_state.web_running = False
    await ws_manager.stop()
    await modbus_client_manager.close()


def run_web_monitor():
    """Run web monitor"""
    import uvicorn
    host = "0.0.0.0"
    port = BASE_CONFIG["WEB_PORT"]
    log = logger.get_web_logger()
    log.info(f"Starting Web server - Address: {host}, Port: {port}")
    log.info(f"Web server access URL: http://localhost:{port}")
    uvicorn.run(
        app,
        host=host,
        port=port,
        log_level="info" if BASE_CONFIG["DEBUG"] else "error"
    )


if __name__ == "__main__":
    try:
        run_web_monitor()
    except KeyboardInterrupt:
        logger.get_web_logger().info("Web monitor service stopped")
    except Exception as e:
        logger.get_web_logger().error(f"Program exited with error: {str(e)}")
        sys.exit(1)

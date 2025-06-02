import asyncio
import sys
import time
from typing import Optional

from pymodbus.datastore import ModbusSequentialDataBlock, ModbusSlaveContext, ModbusServerContext
from pymodbus.server import StartAsyncTcpServer

from src.core.config import BASE_CONFIG, DEVICES, shared_state
from src.core.logger import logger
from src.modbus.modbus_cache import ModbusCache
from src.modbus.modbus_data_generator import ModbusDataGenerator


class ModbusSimulator:
    """Modbus simulator"""

    def __init__(self, host: str = BASE_CONFIG["MODBUS_HOST"], port: int = BASE_CONFIG["MODBUS_PORT"]):
        """
        Initialize Modbus simulator
        
        Args:
            host: Modbus server host address
            port: Modbus server port
        """
        self.host = host
        self.port = port
        self.context = None
        self.running = False
        self._update_task: Optional[asyncio.Task] = None
        self._error_count = 0
        self._max_errors = BASE_CONFIG["MAX_RETRIES"]
        self._error_reset_interval = 60  # Error count reset interval (seconds)
        self._log = logger.get_modbus_logger()

        # Use device configuration from shared config
        self.slaves = DEVICES

        # Initialize data generator and cache
        self._data_generator = ModbusDataGenerator()
        self._cache = ModbusCache(timeout=5)

        # Device update frequency configuration (seconds)
        self._update_intervals = {
            1: 1.0,  # Temperature and Humidity Sensor
            2: 0.5,  # Power Meter
            3: 2.0,  # AC Controller
            4: 1.0,  # Air Quality Sensor
            5: 0.2,  # PLC/IO Module
            6: 1.0,  # Smart Light Controller
            7: 0.5  # Smart Plug
        }

    def _init_datastore(self) -> None:
        """Initialize Modbus data store"""
        self.context = {}
        for slave_id in self.slaves:
            # Create slave context
            store = ModbusSlaveContext(
                di=ModbusSequentialDataBlock(0, [0] * 100),  # Discrete Input
                co=ModbusSequentialDataBlock(0, [0] * 100),  # Coil
                hr=ModbusSequentialDataBlock(0, [0] * 100),  # Holding Register
                ir=ModbusSequentialDataBlock(0, [0] * 100)  # Input Register
            )
            self.context[slave_id] = store

    async def _update_slave_data(self, slave_id: int, slave_info: dict, current_time: float) -> None:
        """
        Update data for a single slave
        
        Args:
            slave_id: Slave ID
            slave_info: Slave configuration info
            current_time: Current timestamp
        """
        try:
            context = self.context[slave_id]

            # Check cache
            cached_data = await self._cache.get(slave_id)
            if cached_data is not None:
                simulated_data = cached_data
            else:
                # Generate new simulated data
                simulated_data = self._data_generator.generate_simulated_data(slave_id)
                await self._cache.set(slave_id, simulated_data)

            # Update data to Modbus registers
            for data_item in simulated_data:
                if data_item['type'] == 'IR':
                    context.setValues(3, data_item['address'], [data_item['value']])
                elif data_item['type'] == 'HR':
                    context.setValues(4, data_item['address'], [data_item['value']])
                elif data_item['type'] == 'CO':
                    context.setValues(1, data_item['address'], [data_item['value']])
                elif data_item['type'] == 'DI':
                    context.setValues(2, data_item['address'], [data_item['value']])

            # Update shared state
            shared_state.update_device_status(slave_id, {
                'name': slave_info['name'],
                'data': simulated_data,
                'last_update': current_time
            })

            self._log.debug(f"Slave {slave_id} ({slave_info['name']}) data updated")

        except Exception as e:
            error_msg = f"Error updating slave {slave_id} data: {str(e)}"
            self._log.error(error_msg)
            shared_state.set_error(error_msg)
            self._error_count += 1
            if self._error_count >= self._max_errors:
                raise Exception(f"Error count exceeded maximum limit ({self._max_errors})")

    async def _handle_write(self, slave_id: int, register_type: int, address: int, value: int) -> None:
        """
        Handle write operation
        
        Args:
            slave_id: Slave ID
            register_type: Register type (1=coil, 4=holding register)
            address: Register address
            value: Value to write
        """
        try:
            # Update shared state
            device_status = shared_state.get_device_status(slave_id)
            if device_status:
                # Find and update corresponding data item
                for data_item in device_status['data']:
                    if (data_item['type'] == 'CO' and register_type == 1) or \
                            (data_item['type'] == 'HR' and register_type == 4):
                        if data_item['address'] == address:
                            data_item['value'] = value
                            break
                # Update device status
                shared_state.update_device_status(slave_id, device_status)
                self._log.info(f"Slave {slave_id} register type {register_type} address {address} updated to {value}")
        except Exception as e:
            self._log.error(f"Error handling write operation: {str(e)}")

    async def _update_values(self) -> None:
        """Periodically update data for all slaves"""
        last_error_reset = time.time()
        last_updates = {slave_id: time.time() for slave_id in self.slaves}

        while self.running:
            try:
                current_time = time.time()

                # Clean up expired cache
                await self._cache.cleanup()

                # Reset error count
                if current_time - last_error_reset >= self._error_reset_interval:
                    self._error_count = 0
                    last_error_reset = current_time
                    shared_state.clear_error()
                    self._log.debug("Error count reset")

                # Update data for each slave
                for slave_id, slave_info in self.slaves.items():
                    update_interval = self._update_intervals.get(slave_id, 1.0)
                    if current_time - last_updates[slave_id] >= update_interval:
                        await self._update_slave_data(slave_id, slave_info, current_time)
                        last_updates[slave_id] = current_time

                await asyncio.sleep(0.1)  # Avoid high CPU usage

            except Exception as e:
                error_msg = f"Error updating data: {str(e)}"
                self._log.error(error_msg)
                shared_state.set_error(error_msg)
                if self._error_count >= self._max_errors:
                    self.running = False
                    raise
                await asyncio.sleep(1)

    async def start(self) -> None:
        """Start Modbus simulator"""
        try:
            self._init_datastore()
            self.running = True
            shared_state.modbus_running = True

            # Create server context
            server_context = ModbusServerContext(slaves=self.context, single=False)

            # Start update task
            self._update_task = asyncio.create_task(self._update_values())

            # Start Modbus server
            self._log.info(f"Starting Modbus server - Address: {self.host}, Port: {self.port}")
            await StartAsyncTcpServer(
                context=server_context,
                address=(self.host, self.port)
            )

        except Exception as e:
            error_msg = f"Error starting Modbus simulator: {str(e)}"
            self._log.error(error_msg)
            shared_state.set_error(error_msg)
            await self.stop()
            raise

    async def stop(self) -> None:
        """Stop Modbus simulator"""
        self.running = False
        shared_state.modbus_running = False

        if self._update_task:
            self._update_task.cancel()
            try:
                await self._update_task
            except asyncio.CancelledError:
                pass

        self._log.info("Modbus simulator stopped")


async def run_modbus_simulator():
    """Run Modbus simulator"""
    simulator = ModbusSimulator()
    try:
        await simulator.start()
    except KeyboardInterrupt:
        await simulator.stop()
    except Exception as e:
        logger.get_modbus_logger().error(f"Modbus simulator error: {str(e)}")
        raise


if __name__ == "__main__":
    try:
        asyncio.run(run_modbus_simulator())
    except KeyboardInterrupt:
        logger.get_main_logger().info("Program stopped")
    except Exception as e:
        logger.get_main_logger().error(f"Program exited with error: {str(e)}")
        sys.exit(1)

import random
from typing import List, Dict


class ModbusDataGenerator:
    """Modbus data generator"""

    @staticmethod
    def generate_simulated_data(slave_id: int) -> List[Dict]:
        """
        Generate simulated data based on slave ID
        
        Args:
            slave_id: Slave ID
            
        Returns:
            List[Dict]: List of simulated data
        """
        generators = {
            1: ModbusDataGenerator._generate_temperature_humidity_data,
            2: ModbusDataGenerator._generate_power_meter_data,
            3: ModbusDataGenerator._generate_ac_controller_data,
            4: ModbusDataGenerator._generate_air_quality_data,
            5: ModbusDataGenerator._generate_plc_io_data,
            6: ModbusDataGenerator._generate_light_controller_data,
            7: ModbusDataGenerator._generate_smart_plug_data
        }

        generator = generators.get(slave_id)
        if generator:
            return generator()
        return []

    @staticmethod
    def _generate_temperature_humidity_data() -> List[Dict]:
        """Generate temperature and humidity sensor data"""
        return [
            {
                'type': 'IR',
                'address': 0,
                'value': random.randint(150, 350)  # 15.0-35.0°C
            },
            {
                'type': 'IR',
                'address': 1,
                'value': random.randint(300, 800)  # 30.0-80.0%
            },
            {
                'type': 'IR',
                'address': 2,
                'value': random.randint(0, 100)  # Battery level 0-100%
            }
        ]

    @staticmethod
    def _generate_power_meter_data() -> List[Dict]:
        """Generate power meter data"""
        return [
            {
                'type': 'IR',
                'address': 0,
                'value': random.randint(2200, 2400)  # 220.0-240.0V
            },
            {
                'type': 'IR',
                'address': 1,
                'value': random.randint(0, 1000)  # 0.00-10.00A
            },
            {
                'type': 'IR',
                'address': 2,
                'value': random.randint(0, 24000)  # 0-2400W
            },
            {
                'type': 'IR',
                'address': 3,
                'value': random.randint(0, 10000)  # 0-1000kWh
            },
            {
                'type': 'IR',
                'address': 4,
                'value': random.randint(4900, 5100)  # 49.00-51.00Hz
            }
        ]

    @staticmethod
    def _generate_ac_controller_data() -> List[Dict]:
        """Generate AC controller data"""
        return [
            {
                'type': 'IR',
                'address': 0,
                'value': random.randint(150, 350)  # 15.0-35.0°C
            },
            {
                'type': 'HR',
                'address': 50,
                'value': random.randint(160, 300)  # 16.0-30.0°C
            },
            {
                'type': 'HR',
                'address': 51,
                'value': random.randint(0, 2)  # 0:Off 1:Cool 2:Heat
            },
            {
                'type': 'CO',
                'address': 0,
                'value': 0  # 0:Off 1:On
            }
        ]

    @staticmethod
    def _generate_air_quality_data() -> List[Dict]:
        """Generate air quality sensor data"""
        return [
            {
                'type': 'IR',
                'address': 0,
                'value': random.randint(0, 1000)  # 0-1000ppm CO2
            },
            {
                'type': 'IR',
                'address': 1,
                'value': random.randint(0, 500)  # 0-500ppm TVOC
            },
            {
                'type': 'IR',
                'address': 2,
                'value': random.randint(0, 100)  # 0-100% PM2.5
            }
        ]

    @staticmethod
    def _generate_plc_io_data() -> List[Dict]:
        """Generate PLC/IO module data"""
        return [
            {
                'type': 'DI',
                'address': 0,
                'value': random.randint(0, 1)  # Digital input 0/1
            },
            {
                'type': 'DI',
                'address': 1,
                'value': random.randint(0, 1)  # Digital input 0/1
            },
            {
                'type': 'CO',
                'address': 0,
                'value': random.randint(0, 1)  # Digital output 0/1
            },
            {
                'type': 'CO',
                'address': 1,
                'value': random.randint(0, 1)  # Digital output 0/1
            }
        ]

    @staticmethod
    def _generate_light_controller_data() -> List[Dict]:
        """Generate smart light controller data"""
        return [
            {
                'type': 'CO',
                'address': 0,
                'value': random.randint(0, 1)  # Power 0/1
            },
            {
                'type': 'HR',
                'address': 0,
                'value': random.randint(0, 100)  # Brightness 0-100%
            },
            {
                'type': 'HR',
                'address': 1,
                'value': random.randint(2700, 6500)  # Color temperature 2700K-6500K
            }
        ]

    @staticmethod
    def _generate_smart_plug_data() -> List[Dict]:
        """Generate smart plug data"""
        return [
            {
                'type': 'IR',
                'address': 0,
                'value': random.randint(2200, 2400)  # 220.0-240.0V
            },
            {
                'type': 'IR',
                'address': 1,
                'value': random.randint(0, 1000)  # 0.00-10.00A
            },
            {
                'type': 'CO',
                'address': 0,
                'value': 0  # Power 0/1
            }
        ]

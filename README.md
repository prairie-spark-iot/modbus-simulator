# Modbus Device Simulator 🏭

<div align="left">

![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Modbus](https://img.shields.io/badge/Modbus-TCP-orange.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=flat&logo=fastapi&logoColor=white)
![WebSocket](https://img.shields.io/badge/WebSocket-000000?style=flat&logo=websocket&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-2496ED?style=flat&logo=docker&logoColor=white)

[English](README.md) | [中文](README_CN.md)

[![Star](https://img.shields.io/github/stars/prairie-spark-iot/modbus-simulator?style=social)](https://github.com/prairie-spark-iot/modbus-simulator)
[![Fork](https://img.shields.io/github/forks/prairie-spark-iot/modbus-simulator?style=social)](https://github.com/prairie-spark-iot/modbus-simulator)

<img src="https://img.shields.io/badge/Windows-0078D6?style=for-the-badge&logo=windows&logoColor=white" alt="Windows">
<img src="https://img.shields.io/badge/Linux-FCC624?style=for-the-badge&logo=linux&logoColor=black" alt="Linux">
<img src="https://img.shields.io/badge/macOS-000000?style=for-the-badge&logo=macos&logoColor=white" alt="macOS">

</div>

---

## 📋 Project Introduction

A powerful Modbus device simulator designed for industrial automation testing, teaching demonstrations, and system integration testing. This project provides a complete solution including Modbus server, Web monitoring interface, and real-time data updates.

<div align="left">
<img src="https://img.shields.io/badge/Industrial_Automation-FF6B6B?style=for-the-badge" alt="Industrial Automation">
<img src="https://img.shields.io/badge/Teaching_Demo-4ECDC4?style=for-the-badge" alt="Teaching Demo">
<img src="https://img.shields.io/badge/System_Integration-45B7D1?style=for-the-badge" alt="System Integration">
</div>

## ✨ Key Features

<div align="left">

| Feature | Description | Icon |
|---------|-------------|------|
| 🚀 High Performance | Async IO implementation, high concurrency support | ⚡ |
| 🔄 Real-time | WebSocket data push, millisecond updates | 🕒 |
| 📊 Visualization | Intuitive Web interface, real-time data display | 📈 |
| 🔌 Multi-device | Support for 7 common industrial devices | 🏭 |
| 🛠 Extensible | Modular design, easy to add new devices | 🔧 |
| 🐳 Docker Support | Supports Docker deployment, one-click startup | 🐳 |

</div>

### Core Features

<details>
<summary>🚀 High Performance</summary>

- Async IO implementation
- High concurrency support
- Low latency data updates
- Optimized data processing
</details>

<details>
<summary>🔄 Real-time</summary>

- WebSocket real-time data push
- Millisecond-level updates
- Multi-client synchronization
- Reliable data transmission
</details>

<details>
<summary>📊 Visualization</summary>

- Intuitive Web interface
- Real-time data display
- Device status monitoring
- Data trend analysis
</details>

<details>
<summary>🐳 Docker Support</summary>

- One-click deployment
- Environment isolation
- Quick startup
- Easy maintenance
</details>

## 🚀 Quick Start

### Requirements

<div align="left">

| Requirement | Description |
|-------------|-------------|
| Python | 3.8+ |
| OS | Windows/Linux/MacOS |
| Network | TCP/IP support |
| Memory | 2GB+ recommended |
| Storage | 1GB+ recommended |
| Docker | Optional, for containerized deployment |

</div>

### Installation

#### Method 1: Direct Run

1. **Clone the repository**
```bash
git clone https://github.com/prairie-spark-iot/modbus-simulator.git
cd modbus-simulator
```

2. **Create virtual environment**
```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# Linux/MacOS
python -m venv .venv
source .venv/bin/activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Run the project**
```bash
python -m src.main
```

#### Method 2: Docker Deployment

1. **Clone the repository**
```bash
git clone https://github.com/prairie-spark-iot/modbus-simulator.git
cd modbus-simulator
```

2. **Build and start container**
```bash
# Using docker-compose (recommended)
docker-compose up -d

# Or using docker commands
docker build -t modbus-simulator .
docker run -d -p 8000:8000 -p 502:502 --name modbus-simulator modbus-simulator
```

3. **Check container status**
```bash
docker-compose ps
# or
docker ps
```

4. **View logs**
```bash
docker-compose logs -f
# or
docker logs -f modbus-simulator
```

5. **Stop service**
```bash
docker-compose down
# or
docker stop modbus-simulator
```

### Access

<div align="left">

| Service | Address | Description |
|---------|---------|-------------|
| 🌐 Web Interface | http://localhost:8000 | Device monitoring interface |
| 📡 Modbus Server | localhost:502 | Modbus communication service |
| 📚 API Docs | http://localhost:8000/docs | API documentation |

</div>

## 📦 Device Support

<div align="left">

| Device Type | Slave ID | Main Features | Icon |
|-------------|----------|---------------|------|
| Temperature & Humidity Sensor | 1 | Temperature, humidity data | 🌡️ |
| Energy Meter | 2 | Voltage, current, power, energy | ⚡ |
| AC Controller | 3 | Temperature, mode, switch status | ❄️ |
| Air Quality Sensor | 4 | PM2.5, CO2, TVOC data | 🌫️ |
| PLC/IO Module | 5 | Digital/Analog I/O | 🔌 |
| Smart Light Controller | 6 | Brightness, color temp, switch | 💡 |
| Smart Socket | 7 | Power, switch status, timing | 🔋 |

</div>

## 🏗 System Architecture

### Tech Stack

<div align="left">

| Layer | Technology | Description |
|-------|------------|-------------|
| Backend | Python 3.8+ | Core language |
| Backend | pymodbus | Modbus implementation |
| Backend | FastAPI | Web framework |
| Backend | WebSocket | Real-time communication |
| Backend | asyncio | Async processing |
| Frontend | HTML5/CSS3 | Interface structure |
| Frontend | JavaScript | Interaction logic |
| Frontend | Bootstrap 5 | UI framework |
| Frontend | Chart.js | Data visualization |

</div>

### System Layers

<details>
<summary>1. Modbus Server Layer</summary>

- Modbus protocol communication
- Device data management
- Read/write request handling
- Data validation
</details>

<details>
<summary>2. Data Management Layer</summary>

- Data generation and simulation
- Cache mechanism
- State management
- Data persistence
</details>

<details>
<summary>3. Web Service Layer</summary>

- RESTful API
- WebSocket service
- Static resource service
- Security authentication
</details>

<details>
<summary>4. Frontend Layer</summary>

- Real-time data display
- Device control interface
- Status monitoring
- Data visualization
</details>

## 📚 Development Documentation

### Project Structure
```
modbus-simulator/
├── src/                    # Source code directory
│   ├── core/              # Core functionality modules
│   │   ├── config.py      # Configuration management
│   │   └── logger.py      # Logging management
│   ├── modbus/            # Modbus related modules
│   │   ├── modbus_cache.py        # Data caching
│   │   └── modbus_data_generator.py # Data generation
│   ├── web/               # Web related modules
│   │   ├── modbus_client.py      # Modbus client
│   │   ├── routes.py             # Route definitions
│   │   ├── tasks.py              # Background tasks
│   │   └── websocket_manager.py  # WebSocket management
│   ├── __init__.py        # Package initialization
│   └── main.py            # Main program entry
├── static/                # Static resources
│   ├── css/              # CSS style files
│   │   └── style.css     # Main style file
│   └── js/               # JavaScript files
│       └── app.js        # Main script file
├── templates/             # Template files
│   └── index.html        # Main page template
├── logs/                  # Log directory
├── docs/                  # Documentation directory
├── .editorconfig         # Editor configuration
├── .gitignore            # Git ignore file
├── .dockerignore         # Docker ignore file
├── .pre-commit-config.yaml # Pre-commit hooks configuration
├── docker-compose.yml    # Docker compose configuration
├── Dockerfile            # Docker build file
├── LICENSE               # License file
├── mypy.ini             # Type checking configuration
├── pyproject.toml       # Project configuration
├── README.md            # Project documentation (Chinese)
├── README_EN.md         # Project documentation (English)
├── requirements.txt     # Dependencies list
└── uv.lock              # Dependencies lock file
```

## ❓ FAQ

<details>
<summary>Connection Issues</summary>

**Q: Cannot connect to Modbus server?**
- Check if port 502 is available
- Verify firewall settings
- Check network connection
</details>

<details>
<summary>Display Issues</summary>

**Q: Web interface not showing data?**
- Check WebSocket connection
- Verify device ID configuration
- Check browser console
</details>

<details>
<summary>Performance Issues</summary>

**Q: Data updates not timely?**
- Check device update interval
- Verify WebSocket connection
- Check server load
</details>

## ⚠️ Notes

<div align="left">

| No. | Note | Description |
|-----|------|-------------|
| 1 | Port | Ensure port 502 is available |
| 2 | Firewall | Check firewall settings |
| 3 | Python | Ensure correct Python environment |
| 4 | Virtual Env | Run in virtual environment |
| 5 | Logs | Check logs regularly |
| 6 | Security | Pay attention to data security |

</div>

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👥 Contributing

We welcome contributions! Please ensure:

1. Code follows project standards
2. Add necessary tests
3. Update documentation
4. Provide clear commit messages

## 📞 Contact

<div align="left">

| Method | Content |
|--------|---------|
| Author | Your Name |
| Email | your.email@example.com |
| GitHub | [prairie-spark-iot](https://github.com/prairie-spark-iot) |
| Project | [modbus-simulator](https://github.com/prairie-spark-iot/modbus-simulator) |

</div>

## 🙏 Acknowledgments

Thanks to all contributors!

---

<div align="left">

**If this project helps you, please give it a ⭐️ Star!**

</div> 

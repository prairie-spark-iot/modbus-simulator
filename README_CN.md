# Modbus设备模拟器 🏭

<div align="left">

![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Modbus](https://img.shields.io/badge/Modbus-TCP-orange.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=flat&logo=fastapi&logoColor=white)
![WebSocket](https://img.shields.io/badge/WebSocket-000000?style=flat&logo=websocket&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-2496ED?style=flat&logo=docker&logoColor=white)

[English](README_EN.md) | [中文](README.md)

[![Star](https://img.shields.io/github/stars/prairie-spark-iot/modbus-simulator?style=social)](https://github.com/prairie-spark-iot/modbus-simulator)
[![Fork](https://img.shields.io/github/forks/prairie-spark-iot/modbus-simulator?style=social)](https://github.com/prairie-spark-iot/modbus-simulator)

<img src="https://img.shields.io/badge/Windows-0078D6?style=for-the-badge&logo=windows&logoColor=white" alt="Windows">
<img src="https://img.shields.io/badge/Linux-FCC624?style=for-the-badge&logo=linux&logoColor=black" alt="Linux">
<img src="https://img.shields.io/badge/macOS-000000?style=for-the-badge&logo=macos&logoColor=white" alt="macOS">

</div>

---

## 📋 项目简介

一个功能强大的Modbus设备模拟器，专为工业自动化测试、教学演示和系统集成测试设计。项目提供完整的Modbus服务器、Web监控界面和实时数据更新功能。

<div align="left">
<img src="https://img.shields.io/badge/工业自动化-FF6B6B?style=for-the-badge" alt="工业自动化">
<img src="https://img.shields.io/badge/教学演示-4ECDC4?style=for-the-badge" alt="教学演示">
<img src="https://img.shields.io/badge/系统集成-45B7D1?style=for-the-badge" alt="系统集成">
</div>

## ✨ 功能特点

<div align="left">

| 特性 | 描述 | 图标 |
|------|------|------|
| 🚀 高性能 | 基于异步IO实现，支持高并发连接 | ⚡ |
| 🔄 实时性 | WebSocket实时数据推送，毫秒级更新 | 🕒 |
| 📊 可视化 | 直观的Web界面，实时数据展示 | 📈 |
| 🔌 多设备 | 支持7种常见工业设备模拟 | 🏭 |
| 🛠 可扩展 | 模块化设计，易于添加新设备 | 🔧 |
| 🐳 Docker支持 | 支持Docker部署，一键启动 | 🐳 |

</div>

### 核心功能

<details>
<summary>🚀 高性能</summary>

- 基于异步IO实现
- 支持高并发连接
- 低延迟数据更新
- 优化的数据处理流程
</details>

<details>
<summary>🔄 实时性</summary>

- WebSocket实时数据推送
- 毫秒级数据更新
- 多客户端同步
- 可靠的数据传输
</details>

<details>
<summary>📊 可视化</summary>

- 直观的Web界面
- 实时数据展示
- 设备状态监控
- 数据趋势分析
</details>

<details>
<summary>🐳 Docker支持</summary>

- 一键部署
- 环境隔离
- 快速启动
- 易于维护
</details>

## 🚀 快速开始

### 环境要求

<div align="left">

| 要求 | 说明 |
|------|------|
| Python | 3.8+ |
| 操作系统 | Windows/Linux/MacOS |
| 网络 | 支持TCP/IP协议 |
| 内存 | 建议 2GB+ |
| 存储 | 建议 1GB+ |
| Docker | 可选，用于容器化部署 |

</div>

### 安装步骤

#### 方式一：直接运行

1. **克隆项目**
```bash
git clone https://github.com/prairie-spark-iot/modbus-simulator.git
cd modbus-simulator
```

2. **创建虚拟环境**
```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# Linux/MacOS
python -m venv .venv
source .venv/bin/activate
```

3. **安装依赖**
```bash
pip install -r requirements.txt
```

4. **运行项目**
```bash
python main.py
```

#### 方式二：Docker部署

1. **克隆项目**
```bash
git clone https://github.com/prairie-spark-iot/modbus-simulator.git
cd modbus-simulator
```

2. **构建并启动容器**
```bash
# 使用docker-compose（推荐）
docker-compose up -d

# 或使用docker命令
docker build -t modbus-simulator .
docker run -d -p 8000:8000 -p 502:502 --name modbus-simulator modbus-simulator
```

3. **查看容器状态**
```bash
docker-compose ps
# 或
docker ps
```

4. **查看日志**
```bash
docker-compose logs -f
# 或
docker logs -f modbus-simulator
```

5. **停止服务**
```bash
docker-compose down
# 或
docker stop modbus-simulator
```

### 访问方式

<div align="left">

| 服务 | 地址 | 说明 |
|------|------|------|
| 🌐 Web界面 | http://localhost:8000 | 设备监控界面 |
| 📡 Modbus服务器 | localhost:502 | Modbus通信服务 |
| 📚 API文档 | http://localhost:8000/docs | API接口文档 |

</div>

## 📦 设备支持

<div align="left">

| 设备类型 | 从站ID | 主要功能 | 图标 |
|---------|--------|----------|------|
| 温湿度传感器 | 1 | 温度、湿度数据模拟 | 🌡️ |
| 电能表 | 2 | 电压、电流、功率、电能数据 | ⚡ |
| 空调控制器 | 3 | 温度、模式、开关状态控制 | ❄️ |
| 空气质量传感器 | 4 | PM2.5、CO2、TVOC等数据 | 🌫️ |
| PLC/IO模块 | 5 | 数字输入输出、模拟量输入输出 | 🔌 |
| 智能灯控制器 | 6 | 亮度、色温、开关控制 | 💡 |
| 智能插座 | 7 | 功率、开关状态、定时控制 | 🔋 |

</div>

## 🏗 系统架构

### 技术栈

<div align="left">

| 层级 | 技术 | 说明 |
|------|------|------|
| 后端 | Python 3.8+ | 核心编程语言 |
| 后端 | pymodbus | Modbus协议实现 |
| 后端 | FastAPI | Web框架 |
| 后端 | WebSocket | 实时通信 |
| 后端 | asyncio | 异步处理 |
| 前端 | HTML5/CSS3 | 界面结构 |
| 前端 | JavaScript | 交互逻辑 |
| 前端 | Bootstrap 5 | UI框架 |
| 前端 | Chart.js | 数据可视化 |

</div>

### 系统分层

<details>
<summary>1. Modbus服务器层</summary>

- Modbus协议通信
- 设备数据管理
- 读写请求处理
- 数据验证
</details>

<details>
<summary>2. 数据管理层</summary>

- 数据生成和模拟
- 缓存机制
- 状态管理
- 数据持久化
</details>

<details>
<summary>3. Web服务层</summary>

- RESTful API
- WebSocket服务
- 静态资源服务
- 安全认证
</details>

<details>
<summary>4. 前端展示层</summary>

- 实时数据展示
- 设备控制界面
- 状态监控
- 数据可视化
</details>

## 📚 开发文档

### 项目结构
```
modbus-simulator/
├── src/                    # 源代码目录
│   ├── core/              # 核心功能模块
│   │   ├── config.py      # 配置管理
│   │   └── logger.py      # 日志管理
│   ├── modbus/            # Modbus 相关模块
│   │   ├── modbus_cache.py        # 数据缓存
│   │   └── modbus_data_generator.py # 数据生成
│   ├── web/               # Web 相关模块
│   │   ├── modbus_client.py      # Modbus 客户端
│   │   ├── routes.py             # 路由定义
│   │   ├── tasks.py              # 后台任务
│   │   └── websocket_manager.py  # WebSocket 管理
│   ├── __init__.py        # 包初始化
│   └── main.py            # 主程序入口
├── static/                # 静态资源
│   ├── css/              # CSS 样式文件
│   │   └── style.css     # 主样式文件
│   └── js/               # JavaScript 文件
│       └── app.js        # 主脚本文件
├── templates/             # 模板文件
│   └── index.html        # 主页面模板
├── logs/                  # 日志目录
├── docs/                  # 文档目录
├── .editorconfig         # 编辑器配置
├── .gitignore            # Git 忽略文件
├── .dockerignore         # Docker 忽略文件
├── .pre-commit-config.yaml # 预提交钩子配置
├── docker-compose.yml    # Docker Compose 配置
├── Dockerfile            # Docker 构建文件
├── LICENSE               # 许可证文件
├── mypy.ini             # 类型检查配置
├── pyproject.toml       # 项目配置
├── README.md            # 项目文档（中文）
├── README_EN.md         # 项目文档（英文）
├── requirements.txt     # 依赖列表
└── uv.lock              # 依赖锁定文件
```

## ❓ 常见问题

<details>
<summary>连接问题</summary>

**Q: 无法连接到Modbus服务器？**
- 检查端口502是否被占用
- 确认防火墙设置
- 验证网络连接
</details>

<details>
<summary>显示问题</summary>

**Q: Web界面无法显示数据？**
- 检查WebSocket连接
- 确认设备ID配置正确
- 查看浏览器控制台错误
</details>

<details>
<summary>性能问题</summary>

**Q: 数据更新不及时？**
- 检查设备更新间隔设置
- 确认WebSocket连接状态
- 查看服务器负载
</details>

## ⚠️ 注意事项

<div align="left">

| 序号 | 注意事项 | 说明 |
|------|----------|------|
| 1 | 端口占用 | 确保端口502未被占用 |
| 2 | 防火墙 | 检查防火墙设置 |
| 3 | Python环境 | 确保Python环境正确配置 |
| 4 | 虚拟环境 | 建议在虚拟环境中运行 |
| 5 | 日志检查 | 定期检查日志文件 |
| 6 | 数据安全 | 注意数据安全性 |

</div>

## 📄 许可证

本项目采用 MIT 许可证，详见 [LICENSE](LICENSE) 文件。

## 👥 贡献指南

欢迎提交Issue和Pull Request来帮助改进项目。在提交代码前，请确保：

1. 代码符合项目规范
2. 添加必要的测试
3. 更新相关文档
4. 提供清晰的提交信息

## 📞 联系方式

<div align="left">

| 方式 | 内容 |
|------|------|
| 作者 | Your Name |
| 邮箱 | your.email@example.com |
| GitHub | [prairie-spark-iot](https://github.com/prairie-spark-iot) |
| 项目地址 | [modbus-simulator](https://github.com/prairie-spark-iot/modbus-simulator) |

</div>

## 🙏 致谢

感谢所有为本项目做出贡献的开发者。

---

<div align="left">

**如果这个项目对您有帮助，欢迎给个 ⭐️ Star 支持一下！**

</div> 

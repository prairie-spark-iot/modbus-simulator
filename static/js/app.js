/**
 * Constant Configuration
 */
const CONFIG = {
    WS: {
        RECONNECT_DELAY: 3000,
        MAX_RECONNECT_ATTEMPTS: 5,
        HEARTBEAT_INTERVAL: 30000,
        MAX_ERRORS: 5,
        ERROR_RESET_INTERVAL: 60000
    },
    UI: {
        ANIMATION_DURATION: 500,
        UPDATE_THROTTLE: 100,
        BATCH_TIMEOUT: 50
    }
};

/**
 * Utility Functions
 */
const Utils = {
    debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    },

    throttle(func, limit) {
        let inThrottle;
        return function executedFunction(...args) {
            if (!inThrottle) {
                func(...args);
                inThrottle = true;
                setTimeout(() => inThrottle = false, limit);
            }
        };
    },

    formatTime(date) {
        return date.toLocaleTimeString('zh-CN', {
            hour: '2-digit',
            minute: '2-digit',
            second: '2-digit',
            hour12: false
        });
    },

    createElement(tag, className, innerHTML) {
        const element = document.createElement(tag);
        if (className) element.className = className;
        if (innerHTML) element.innerHTML = innerHTML;
        return element;
    },

    addAnimation(element, className, duration) {
        element.classList.add(className);
        setTimeout(() => element.classList.remove(className), duration);
    }
};

/**
 * WebSocket Connection Manager Base Class
 */
class BaseWebSocketManager {
    constructor(url, type) {
        this.ws = null;
        this.url = url;
        this.type = type;
        this.reconnectAttempts = 0;
        this.lastHeartbeat = null;
        this.heartbeatInterval = null;
        this._errorCount = 0;
        this._lastErrorReset = Date.now();
        this._messageQueue = [];
        this._isProcessingQueue = false;
    }

    connect() {
        try {
            const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
            const wsUrl = `${protocol}//${window.location.host}${this.url}`;
            this.ws = new WebSocket(wsUrl);
            this.setupEventHandlers();
        } catch (error) {
            console.error('Error creating WebSocket connection:', error);
            this.handleError(error);
        }
    }

    setupEventHandlers() {
        if (!this.ws) return;

        this.ws.onopen = () => this.handleOpen();
        this.ws.onclose = () => this.handleClose();
        this.ws.onerror = (error) => this.handleError(error);
        this.ws.onmessage = (event) => {
            try {
                const data = JSON.parse(event.data);
                this.handleMessage(data);
            } catch (error) {
                console.error('Error parsing WebSocket message:', error);
                this.incrementErrorCount();
            }
        };
    }

    handleOpen() {
        console.log(`${this.url} WebSocket connection established`);
        this.reconnectAttempts = 0;
        this._errorCount = 0;
        this.startHeartbeat();
        this.processMessageQueue();
        this.updateConnectionStatus(true);
    }

    handleClose() {
        console.log(`${this.url} WebSocket connection closed`);
        this.stopHeartbeat();
        this.attemptReconnect();
        this.updateConnectionStatus(false);
    }

    handleError(error) {
        console.error(`${this.url} WebSocket error:`, error);
        this.incrementErrorCount();
    }

    incrementErrorCount() {
        const now = Date.now();
        if (now - this._lastErrorReset >= CONFIG.WS.ERROR_RESET_INTERVAL) {
            this._errorCount = 0;
            this._lastErrorReset = now;
        }

        this._errorCount++;
        if (this._errorCount >= CONFIG.WS.MAX_ERRORS) {
            console.error('Too many errors, stopping reconnect');
            this.stopHeartbeat();
            if (this.ws) {
                this.ws.close();
            }
        }
    }

    startHeartbeat() {
        if (this.heartbeatInterval) clearInterval(this.heartbeatInterval);
        this.heartbeatInterval = setInterval(() => {
            if (this.ws?.readyState === WebSocket.OPEN) {
                this.sendMessage({type: 'heartbeat'});
            }
        }, CONFIG.WS.HEARTBEAT_INTERVAL);
    }

    stopHeartbeat() {
        if (this.heartbeatInterval) {
            clearInterval(this.heartbeatInterval);
            this.heartbeatInterval = null;
        }
    }

    attemptReconnect() {
        if (this.reconnectAttempts < CONFIG.WS.MAX_RECONNECT_ATTEMPTS) {
            console.log(`Attempting to reconnect ${this.url} (${this.reconnectAttempts + 1}/${CONFIG.WS.MAX_RECONNECT_ATTEMPTS})...`);
            setTimeout(() => this.connect(), CONFIG.WS.RECONNECT_DELAY);
            this.reconnectAttempts++;
        } else {
            console.error('Reached maximum reconnect attempts, please refresh the page and try again');
        }
    }

    sendMessage(data) {
        if (this.ws?.readyState === WebSocket.OPEN) {
            this.ws.send(JSON.stringify(data));
        } else {
            this._messageQueue.push(data);
        }
    }

    async processMessageQueue() {
        if (this._isProcessingQueue || !this._messageQueue.length) return;
        
        this._isProcessingQueue = true;
        while (this._messageQueue.length > 0) {
            const message = this._messageQueue.shift();
            if (this.ws?.readyState === WebSocket.OPEN) {
                this.ws.send(JSON.stringify(message));
            } else {
                this._messageQueue.unshift(message);
                break;
            }
            await new Promise(resolve => setTimeout(resolve, 50));
        }
        this._isProcessingQueue = false;
    }

    updateConnectionStatus(isConnected) {
        if (this.type === 'system') {
            updateSystemWebSocketStatus(isConnected);
        } else if (this.type === 'device') {
            updateDeviceWebSocketStatus(isConnected);
        }
    }

    handleMessage(data) {
        console.log('Received message:', data);
    }
}

/**
 * System Status WebSocket Manager
 */
class SystemWebSocketManager extends BaseWebSocketManager {
    constructor() {
        super('/ws/system', 'system');
    }

    handleOpen() {
        super.handleOpen();
        this.requestInitialData();
    }

    requestInitialData() {
        this.sendMessage({
            type: 'request_data',
            requestType: 'all'
        });
    }

    handleMessage(data) {
        try {
            switch (data.type) {
                case 'system_status':
                    updateModbusStatus(data.modbus_running);
                    updateWebStatus(data.web_running);
                    updateLastUpdateTime();
                    break;
            }
        } catch (error) {
            console.error('Error processing system status message:', error);
            this.incrementErrorCount();
        }
    }
}

/**
 * Device Status WebSocket Manager
 */
class DeviceWebSocketManager extends BaseWebSocketManager {
    constructor() {
        super('/ws', 'device');
        this.deviceDataCache = new Map();
        this.pendingUpdates = new Map();
        this._updateThrottle = new Map();
        this._batchUpdates = new Map();
    }

    handleOpen() {
        super.handleOpen();
        this.requestInitialData();
    }

    requestInitialData() {
        this.sendMessage({
            type: 'request_data',
            requestType: 'all'
        });
    }

    handleMessage(data) {
        try {
            switch (data.type) {
                case 'device_status':
                    this.handleDeviceStatus(data);
                    break;
                case 'device_update':
                    this.handleDeviceUpdate(data);
                    break;
            }
        } catch (error) {
            console.error('Error processing device status message:', error);
            this.incrementErrorCount();
        }
    }

    async handleDeviceStatus(data) {
        if (data.devices) {
            await updateDeviceTabs(data.devices);
            updateLastUpdateTime();
        }
    }

    async handleDeviceUpdate(data) {
        const {device_id, data: deviceData, timestamp} = data;
        if (deviceData) {
            if (!document.getElementById(`device-${device_id}`)) {
                createDeviceTab(device_id, deviceData);
            }
            this.deviceDataCache.set(device_id, {
                data: deviceData,
                timestamp: timestamp
            });
            await this.updateDeviceUI(device_id, deviceData);
            updateLastUpdateTime();
        }
    }

    async updateDeviceUI(deviceId, deviceData) {
        try {
            const deviceElement = document.getElementById(`device-${deviceId}`);
            if (!deviceElement) return;

            const updates = new Map();
            deviceData.data.forEach(item => {
                const valueElement = document.querySelector(
                    `#device-${deviceId} [data-register-type="${item.type.toLowerCase()}"][data-address="${item.address}"] .register-value`
                );

                if (valueElement) {
                    const oldValue = valueElement.textContent.trim();
                    const newValue = formatValue(deviceId, item);
                    const unit = getUnit(deviceId, item);

                    if (oldValue !== newValue) {
                        updates.set(valueElement, {
                            value: newValue,
                            unit: unit
                        });
                    }
                }
            });

            if (updates.size > 0) {
                requestAnimationFrame(() => {
                    updates.forEach((update, element) => {
                        element.innerHTML = `
                            ${update.value}
                            <span class="register-unit">${update.unit}</span>
                        `;
                        Utils.addAnimation(element, 'value-update-animation', CONFIG.UI.ANIMATION_DURATION);
                    });
                });
            }
        } catch (error) {
            console.error(`Error updating device ${deviceId} UI:`, error);
        }
    }
}

// Create WebSocket manager instances
const systemWsManager = new SystemWebSocketManager();
const deviceWsManager = new DeviceWebSocketManager();

// Initialize after page load
document.addEventListener('DOMContentLoaded', () => {
    systemWsManager.connect();
    deviceWsManager.connect();

    // Clean up resources before page close
    window.addEventListener('beforeunload', () => {
        systemWsManager.stopHeartbeat();
        deviceWsManager.stopHeartbeat();
        if (systemWsManager.ws) systemWsManager.ws.close();
        if (deviceWsManager.ws) deviceWsManager.ws.close();
    });
});

/**
 * Update device tabs
 */
const updateDeviceTabs = Utils.throttle(async (devices) => {
    try {
        if (!document.getElementById('deviceTabs').children.length) {
            createDeviceTabs(devices);
        } else {
            for (const [deviceId, deviceData] of Object.entries(devices)) {
                await updateDeviceContent(deviceId, deviceData);
            }
        }
    } catch (error) {
        console.error('Error updating device tabs:', error);
    }
}, CONFIG.UI.UPDATE_THROTTLE);

/**
 * Update device content
 */
const updateDeviceContent = Utils.throttle(async (deviceId, deviceData) => {
    try {
        const deviceElement = document.getElementById(`device-${deviceId}`);
        if (!deviceElement) return;

        const updates = new Map();
        deviceData.data.forEach(item => {
            const valueElement = document.querySelector(
                `#device-${deviceId} [data-register-type="${item.type.toLowerCase()}"][data-address="${item.address}"] .register-value`
            );

            if (valueElement) {
                const oldValue = valueElement.textContent.trim();
                const newValue = formatValue(deviceId, item);
                const unit = getUnit(deviceId, item);

                if (oldValue !== newValue) {
                    updates.set(valueElement, {
                        value: newValue,
                        unit: unit
                    });
                }
            }
        });

        if (updates.size > 0) {
            requestAnimationFrame(() => {
                updates.forEach((update, element) => {
                    element.innerHTML = `
                        ${update.value}
                        <span class="register-unit">${update.unit}</span>
                    `;
                    Utils.addAnimation(element, 'value-update-animation', CONFIG.UI.ANIMATION_DURATION);
                });
            });
        }
    } catch (error) {
        console.error(`Error updating device ${deviceId} content:`, error);
    }
}, CONFIG.UI.UPDATE_THROTTLE);

/**
 * Create single device tab
 */
function createDeviceTab(deviceId, deviceData) {
    try {
        const tabsContainer = document.getElementById('deviceTabs');
        const tabContentContainer = document.getElementById('deviceTabContent');

        // Check if temperature sensor tab exists
        const hasTempSensor = document.getElementById('device-1-tab');
        // If it's a temperature sensor or no temperature sensor exists, set as active
        const isActive = deviceId === '1' || !hasTempSensor;

        const tabButton = Utils.createElement('li', 'nav-item', `
            <button class="nav-link ${isActive ? 'active' : ''}"
                    id="device-${deviceId}-tab"
                    data-bs-toggle="tab"
                    data-bs-target="#device-${deviceId}"
                    type="button"
                    role="tab">
                <i class="fa-solid fa-${getDeviceIcon(deviceId)}" title="${deviceData.name}"></i>
                ${deviceData.name}
            </button>
        `);

        const tabContent = Utils.createElement('div', `tab-pane fade ${isActive ? 'show active' : ''}`, `
            <div class="device-header">
                <h2 class="device-title">
                    <i class="fa-solid fa-${getDeviceIcon(deviceId)}" title="${deviceData.name}"></i>
                    ${deviceData.name}
                </h2>
            </div>
            ${createRegisterSections(deviceId, deviceData)}
        `);
        tabContent.id = `device-${deviceId}`;
        tabContent.setAttribute('role', 'tabpanel');

        // Find correct insertion position
        const allTabs = Array.from(tabsContainer.children);
        const insertIndex = allTabs.findIndex(tab => {
            const tabId = tab.querySelector('.nav-link').id;
            const currentId = parseInt(deviceId);
            const tabDeviceId = parseInt(tabId.split('-')[1]);
            return tabDeviceId > currentId;
        });

        if (insertIndex === -1) {
            // If no larger ID is found, add to the end
            tabsContainer.appendChild(tabButton);
            tabContentContainer.appendChild(tabContent);
        } else {
            // Insert at the correct position
            const referenceTab = allTabs[insertIndex];
            const referenceContent = tabContentContainer.children[insertIndex];
            tabsContainer.insertBefore(tabButton, referenceTab);
            tabContentContainer.insertBefore(tabContent, referenceContent);
        }

        // If it's a temperature sensor, ensure it's active
        if (deviceId === '1') {
            const otherTabs = tabsContainer.querySelectorAll('.nav-link:not(#device-1-tab)');
            const otherContents = tabContentContainer.querySelectorAll('.tab-pane:not(#device-1)');
            otherTabs.forEach(tab => tab.classList.remove('active'));
            otherContents.forEach(content => content.classList.remove('show', 'active'));
        }

    } catch (error) {
        console.error(`Error creating device ${deviceId} tab:`, error);
    }
}

/**
 * Handle control change
 */
const handleControlChange = Utils.throttle((deviceId, type, address, value) => {
    if (deviceWsManager.ws?.readyState === WebSocket.OPEN) {
        const controlData = {
            type: 'control',
            deviceId,
            registerType: type,
            address,
            value: type === 'CO' ? Boolean(value) : Number(value),
            timestamp: Date.now()
        };

        deviceWsManager.pendingUpdates.set(deviceId, {
            timestamp: controlData.timestamp,
            data: controlData
        });

        deviceWsManager.sendMessage(controlData);

        setTimeout(() => {
            deviceWsManager.sendMessage({
                type: 'request_data',
                deviceId,
                requestType: 'single'
            });
        }, 100);
    }
}, CONFIG.UI.UPDATE_THROTTLE);

/**
 * Update status display
 */
const updateStatus = (elementId, isConnected, text) => {
    const status = document.getElementById(elementId);
    if (status) {
        status.className = `system-status-value ${isConnected ? 'online' : 'offline'}`;
        status.innerHTML = `
            <i class="fas fa-circle"></i>
            <span>${text}</span>
        `;
    }
};

const updateModbusStatus = (isRunning) => {
    updateStatus('modbus-status-value', isRunning, isRunning ? 'Online' : 'Offline');
};

const updateWebStatus = (isRunning) => {
    updateStatus('web-status-value', isRunning, isRunning ? 'Online' : 'Offline');
};

const updateSystemWebSocketStatus = (isConnected) => {
    updateStatus('web-status-value', isConnected, isConnected ? 'Connected' : 'Disconnected');
};

const updateDeviceWebSocketStatus = (isConnected) => {
    updateStatus('device-ws-status-value', isConnected, isConnected ? 'Connected' : 'Disconnected');
};

const updateLastUpdateTime = Utils.throttle(() => {
    const lastUpdateElement = document.getElementById('last-update-time');
    if (lastUpdateElement) {
        lastUpdateElement.innerHTML = `
            <i class="fas fa-clock"></i>
            <span>${Utils.formatTime(new Date())}</span>
        `;
        Utils.addAnimation(lastUpdateElement, 'updated', CONFIG.UI.ANIMATION_DURATION);
    }
}, CONFIG.UI.UPDATE_THROTTLE);

/**
 * Create device tabs
 */
function createDeviceTabs(devices) {
    try {
        const tabsContainer = document.getElementById('deviceTabs');
        const tabContentContainer = document.getElementById('deviceTabContent');

        // Use document fragment for DOM operation optimization
        const tabsFragment = document.createDocumentFragment();
        const contentFragment = document.createDocumentFragment();

        // Sort devices, ensure temperature sensors are first, other devices sorted by ID
        const sortedDevices = Object.entries(devices).sort(([deviceIdA], [deviceIdB]) => {
            if (deviceIdA === '1') return -1;
            if (deviceIdB === '1') return 1;
            return parseInt(deviceIdA) - parseInt(deviceIdB);
        });

        // Create tab for each device
        sortedDevices.forEach(([deviceId, deviceData], index) => {
            // Temperature sensor default active
            const isActive = deviceId === '1';

            // Create tab button
            const tabButton = document.createElement('li');
            tabButton.className = 'nav-item';
            tabButton.innerHTML = `
                    <button class="nav-link ${isActive ? 'active' : ''}"
                            id="device-${deviceId}-tab"
                            data-bs-toggle="tab"
                            data-bs-target="#device-${deviceId}"
                            type="button"
                            role="tab">
                        <i class="fa-solid fa-${getDeviceIcon(deviceId)}" title="${deviceData.name}"></i>
                        ${deviceData.name}
                    </button>
                `;
            tabsFragment.appendChild(tabButton);

            // Create tab content
            const tabContent = document.createElement('div');
            tabContent.className = `tab-pane fade ${isActive ? 'show active' : ''}`;
            tabContent.id = `device-${deviceId}`;
            tabContent.setAttribute('role', 'tabpanel');

            // Create device content
            tabContent.innerHTML = `
                    <div class="device-header">
                        <h2 class="device-title">
                            <i class="fa-solid fa-${getDeviceIcon(deviceId)}" title="${deviceData.name}"></i>
                            ${deviceData.name}
                        </h2>
                    </div>
                    ${createRegisterSections(deviceId, deviceData)}
                `;

            contentFragment.appendChild(tabContent);
        });

        // Batch update DOM
        requestAnimationFrame(() => {
            tabsContainer.innerHTML = '';
            tabContentContainer.innerHTML = '';
            tabsContainer.appendChild(tabsFragment);
            tabContentContainer.appendChild(contentFragment);
        });
    } catch (error) {
        console.error('Error creating device tabs:', error);
    }
}

/**
 * Create register section
 */
function createRegisterSections(deviceId, deviceData) {
    try {
        const sections = {
            ir: {title: 'Input Registers', items: []},
            hr: {title: 'Holding Registers', items: []},
            co: {title: 'Coils', items: []},
            di: {title: 'Discrete Inputs', items: []}
        };

        // Categorize register data
        deviceData.data.forEach(item => {
            const section = sections[item.type.toLowerCase()];
            if (section) {
                section.items.push(item);
            }
        });

        // Add switch status for smart plug (if not exists)
        if (deviceId === '7' && !sections.co.items.some(item => item.address === 0)) {
            sections.co.items.push({
                type: 'CO',
                address: 0,
                value: 0
            });
        }

        // Generate HTML
        return Object.entries(sections)
            .filter(([_, section]) => section.items.length > 0)
            .map(([type, section]) => `
                    <div class="register-section">
                        <h3 class="register-section-title">
                            <i class="fas fa-${getRegisterTypeIcon(type)}"></i>
                            ${section.title}
                        </h3>
                        <div class="register-grid">
                            ${section.items.map(item => createRegisterItem(deviceId, type, item)).join('')}
                        </div>
                    </div>
                `).join('');
    } catch (error) {
        console.error(`Error creating device ${deviceId} register section:`, error);
        return '';
    }
}

/**
 * Create register item
 */
function createRegisterItem(deviceId, type, item) {
    const label = getDataLabel(deviceId, item);
    const value = formatValue(deviceId, item);
    const unit = getUnit(deviceId, item);
    const control = createControl(deviceId, type, item);

    return `
            <div class="register-item" data-register-type="${type.toLowerCase()}" data-address="${item.address}">
                <div class="register-label">
                    <span class="register-type type-${type.toLowerCase()}">
                        <i class="fa-solid fa-${getRegisterTypeIcon(type)}" title="${type.toUpperCase()}"></i>
                        ${type.toUpperCase()}
                    </span>
                    <i class="fa-solid fa-${getDataIcon(deviceId, item)}" title="${label}"></i>
                    ${label}
                </div>
                ${control || `
                    <div class="register-value">
                        ${value}
                        <span class="register-unit">${unit}</span>
                    </div>
                `}
                <div class="register-address">
                    Address: ${item.address}
                </div>
            </div>
        `;
}

/**
 * Create control element
 */
function createControl(deviceId, type, item) {
    if (type === 'CO') {
        return `
                <label class="form-check-input">
                    <input type="checkbox" ${item.value ? 'checked' : ''}
                           onchange="handleControlChange('${deviceId}', '${type}', ${item.address}, this.checked)">
                </label>
            `;
    } else if (type === 'HR' && deviceId === '6' && item.address === 50) {
        return `
                <input type="range" class="form-range"
                       min="0" max="100" value="${item.value}"
                       onchange="handleControlChange('${deviceId}', '${type}', ${item.address}, this.value)">
            `;
    } else if (type === 'HR' && deviceId === '6' && item.address === 51) {
        return `
                <input type="color" class="form-control-color"
                       value="#${item.value.toString(16).padStart(6, '0')}"
                       onchange="handleControlChange('${deviceId}', '${type}', ${item.address}, parseInt(this.value.replace('#', ''), 16))">
            `;
    }
    return null;
}

/**
 * Format value
 */
function formatValue(deviceId, item) {
    let value = item.value;

    // Handle coil and discrete input switch states
    if (item.type === 'CO' || item.type === 'DI') {
        return value === 1 ? 'On' : 'Off';
    }

    switch (deviceId) {
        case '1': // Temperature and Humidity Sensor
            if (item.type === 'IR' && (item.address === 0 || item.address === 1)) {
                return (value / 10).toFixed(1);
            }
            break;
        case '2': // Power Meter
            if (item.type === 'IR') {
                if (item.address === 0) return (value / 10).toFixed(1);
                if (item.address === 1) return (value / 100).toFixed(2);
            }
            break;
        case '3': // AC Controller
            if (item.type === 'IR' && item.address === 0) {
                return (value / 10).toFixed(1);
            }
            if (item.type === 'HR' && item.address === 50) {
                return (value / 10).toFixed(1);
            }
            if (item.type === 'HR' && item.address === 51) {
                return ['Off', 'Cool', 'Heat'][value] || 'Unknown';
            }
            break;
        case '7': // Smart Plug
            if (item.type === 'IR') {
                if (item.address === 0) return (value / 10).toFixed(1);
                if (item.address === 1) return (value / 100).toFixed(2);
            }
            break;
    }

    return value;
}

/**
 * Get unit
 */
function getUnit(deviceId, item) {
    const units = {
        "1": {  // Temperature and Humidity Sensor
            "IR": {
                0: '°C',
                1: '%',
                2: '%'
            }
        },
        "2": {  // Power Meter
            "IR": {
                0: 'V',
                1: 'A',
                2: 'W',
                3: 'kWh',
                4: 'Hz'
            }
        },
        "3": {  // AC Controller
            "IR": {
                0: '°C'
            },
            "HR": {
                50: '°C',
                51: ''
            }
        },
        "4": {  // Air Quality Sensor
            "IR": {
                0: 'ug/m³',
                1: 'ug/m³',
                2: 'ppm',
                3: 'ppb'
            }
        },
        "6": {  // Smart Light Controller
            "HR": {
                50: '%',
                51: ''
            }
        },
        "7": {  // Smart Plug
            "IR": {
                0: 'V',
                1: 'A'
            }
        }
    };

    return units[deviceId]?.[item.type]?.[item.address] || '';
}

/**
 * Get register type icon
 */
function getRegisterTypeIcon(type) {
    const icons = {
        'ir': 'gauge',
        'hr': 'sliders-h',
        'co': 'toggle-on',
        'di': 'toggle-off'
    };
    return icons[type.toLowerCase()] || 'database';
}

/**
 * Get device icon
 */
function getDeviceIcon(deviceId) {
    const icons = {
        "1": "temperature-high",  // Temperature and Humidity Sensor
        "2": "bolt",              // Power Meter
        "3": "snowflake",         // AC Controller
        "4": "wind",              // Air Quality Sensor
        "5": "microchip",         // PLC/IO Module
        "6": "lightbulb",         // Smart Light Controller
        "7": "plug"               // Smart Plug
    };
    return icons[deviceId] || "device";
}

/**
 * Get data icon
 */
function getDataIcon(deviceId, item) {
    const icons = {
        "1": {  // Temperature and Humidity Sensor
            "IR": {
                0: "thermometer-half",
                1: "tint",
                2: "battery-three-quarters"
            }
        },
        "2": {  // Power Meter
            "IR": {
                0: "bolt",
                1: "bolt",
                2: "bolt",
                3: "bolt",
                4: "wave-square"
            }
        },
        "3": {  // AC Controller
            "IR": {
                0: "thermometer-half"
            },
            "HR": {
                50: "temperature-high",
                51: "cog"
            },
            "CO": {
                0: "power-off"
            }
        },
        "4": {  // Air Quality Sensor
            "IR": {
                0: "smog",
                1: "smog",
                2: "wind",
                3: "wind"
            }
        },
        "5": {  // PLC/IO Module
            "DI": {
                0: "toggle-on",
                1: "toggle-on",
                2: "toggle-on",
                3: "toggle-on"
            },
            "CO": {
                0: "toggle-on",
                1: "toggle-on",
                2: "toggle-on",
                3: "toggle-on"
            }
        },
        "6": {  // Smart Light Controller
            "CO": {
                0: "lightbulb"
            },
            "HR": {
                50: "sun",
                51: "palette"
            }
        },
        "7": {  // Smart Plug
            "IR": {
                0: "bolt",
                1: "bolt"
            },
            "CO": {
                0: "power-off"
            }
        }
    };

    return icons[deviceId]?.[item.type]?.[item.address] || "chart-line";
}

/**
 * Get data label
 */
function getDataLabel(deviceId, item) {
    const labels = {
        "1": {  // Temperature and Humidity Sensor
            "IR": {
                0: 'Temperature',
                1: 'Humidity',
                2: 'Battery Level'
            }
        },
        "2": {  // Power Meter
            "IR": {
                0: 'Voltage',
                1: 'Current',
                2: 'Power',
                3: 'Energy',
                4: 'Frequency'
            }
        },
        "3": {  // AC Controller
            "IR": {
                0: 'Current Temperature'
            },
            "HR": {
                50: 'Target Temperature',
                51: 'Mode'
            },
            "CO": {
                0: 'Power Status'
            }
        },
        "4": {  // Air Quality Sensor
            "IR": {
                0: 'PM2.5',
                1: 'PM10',
                2: 'CO₂',
                3: 'TVOC'
            }
        },
        "5": {  // PLC/IO Module
            "DI": {
                0: 'Input Status (Switch)',
                1: 'Input Status (Switch)',
                2: 'Input Status (Switch)',
                3: 'Input Status (Switch)'
            },
            "CO": {
                0: 'Output Control',
                1: 'Output Control',
                2: 'Output Control',
                3: 'Output Control'
            }
        },
        "6": {  // Smart Light Controller
            "CO": {
                0: 'Power'
            },
            "HR": {
                50: 'Brightness',
                51: 'RGB Color'
            }
        },
        "7": {  // Smart Plug
            "IR": {
                0: 'Voltage',
                1: 'Current'
            },
            "CO": {
                0: 'Power Status'
            }
        }
    };

    return labels[deviceId]?.[item.type]?.[item.address] || `Data ${item.address}`;
} 
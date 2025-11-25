# 🚀 LoRaWAN IoT API Documentation

<div align="center">

**API REST yang powerful untuk mengelola komunikasi uplink dan downlink perangkat LoRaWAN IoT**

[![Version](https://img.shields.io/badge/version-1.0-blue.svg)](https://github.com/yourusername/yourrepo)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/)

</div>

---

## 📋 Daftar Isi

- [🎯 Overview](#-overview)
- [✨ Fitur Utama](#-fitur-utama)
- [🔐 Autentikasi](#-autentikasi)
- [📡 Endpoints](#-endpoints)
  - [📱 Devices Management](#-devices-management)
  - [📥 Uplinks - Data Compact](#-uplinks---data-compact)
  - [📊 Uplinks - Data Full](#-uplinks---data-full)
  - [📤 Downlink Commands](#-downlink-commands)
- [🔧 Parameter & Filters](#-parameter--filters)
- [💡 Response Format](#-response-format)
- [⚠️ Error Handling](#️-error-handling)
- [🎓 Advanced Examples](#-advanced-examples)
- [📌 Best Practices](#-best-practices)

---

## 🎯 Overview

API ini menyediakan interface yang mudah dan efisien untuk berinteraksi dengan jaringan LoRaWAN. Dibangun dengan Flask dan PostgreSQL, API ini mendukung operasi real-time melalui MQTT untuk komunikasi downlink.

### 🏗️ Architecture

```
┌─────────────┐      HTTP/REST      ┌──────────────┐      MQTT       ┌─────────────┐
│   Client    │ ◄──────────────────► │  Flask API   │ ◄──────────────► │   Gateway   │
│ Application │                      │  + PostgreSQL│                  │  LoRaWAN    │
└─────────────┘                      └──────────────┘                  └─────────────┘
                                             │
                                             ▼
                                     ┌──────────────┐
                                     │   Database   │
                                     │  (Uplinks)   │
                                     └──────────────┘
```

---

## ✨ Fitur Utama

| Fitur | Deskripsi |
|-------|-----------|
| 🔍 **Device Discovery** | List semua device aktif dengan statistik uplink |
| 📊 **Data Retrieval** | Ambil data uplink dengan berbagai filter dan pagination |
| ⚡ **Real-time Downlink** | Kirim perintah ke device via MQTT |
| 🎯 **Flexible Queries** | Filter berdasarkan waktu, limit, offset |
| 📈 **Compact & Full Mode** | Pilih level detail data sesuai kebutuhan |
| 🔐 **Secure API** | Autentikasi dengan API Key |

---

## 🔐 Autentikasi

> **⚠️ Penting:** Semua request ke API harus menyertakan API Key untuk keamanan.

Kirim API Key melalui HTTP header:

```http
X-API-Key: your_api_key_here
```

### 📝 Cara Mendapatkan API Key

1. Hubungi administrator sistem
2. API Key akan diberikan secara aman
3. Simpan API Key di environment variable (jangan hardcode!)

```bash
# Contoh: simpan di .env file
API_KEY=your_secret_api_key_here
```

---

## 🌐 Base URL

Sesuaikan dengan environment Anda:

| Environment | Base URL |
|-------------|----------|
| 🧪 Development | `http://localhost:5000` |
| 🏢 Production | `http://teknikantarmuka.my.id` |

---

## 📡 Endpoints

<details open>
<summary><strong>📌 Endpoint Structure Overview</strong></summary>

```
📦 API Root (/api)
 ├── 📱 /uplinks/devices          → List all devices
 ├── 📥 /uplinks/{dev_eui}        → Get device uplinks (compact)
 │   ├── /latest                  → Latest uplink (compact)
 │   ├── /last10                  → Last N uplinks
 │   └── /full                    → Get uplinks (full data)
 │       └── /latest              → Latest uplink (full)
 └── 📤 /downlink                 → Send downlink command
```

</details>

---

### 📱 Devices Management

#### 🔍 List All Devices

Dapatkan overview semua device yang memiliki data uplink beserta statistiknya.

<details>
<summary><strong>📋 Endpoint Details</strong></summary>

**HTTP Method:** `GET`  
**Endpoint:** `/api/uplinks/devices`  
**Auth Required:** ✅ Yes

**Query Parameters:** ❌ None

**Success Response (200):**
```json
[
  {
    "dev_eui": "BE078DDB76F70371",
    "uplink_count": 1234
  },
  {
    "dev_eui": "1234567890ABCDEF",
    "uplink_count": 567
  }
]
```

</details>

<details>
<summary><strong>💻 Code Examples</strong></summary>

**🔸 cURL**
```bash
curl -X GET "http://localhost:5000/api/uplinks/devices" \
  -H "X-API-Key: your_api_key_here"
```

**🔸 JavaScript (Fetch API)**
```javascript
const apiKey = 'your_api_key_here';
const baseUrl = 'http://localhost:5000';

async function getAllDevices() {
    const response = await fetch(`${baseUrl}/api/uplinks/devices`, {
        headers: { 'X-API-Key': apiKey }
    });
    
    if (!response.ok) throw new Error('Failed to fetch devices');
    
    const devices = await response.json();
    console.log(`📱 Found ${devices.length} devices`);
    
    devices.forEach(device => {
        console.log(`• ${device.dev_eui}: ${device.uplink_count} packets`);
    });
    
    return devices;
}

getAllDevices();
```

**🔸 HTML + JavaScript**
```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>📱 Device List</title>
    <style>
        body { 
            font-family: 'Segoe UI', Tahoma, sans-serif; 
            max-width: 800px; 
            margin: 50px auto;
            background: #f5f5f5;
        }
        .device-card {
            background: white;
            padding: 20px;
            margin: 10px 0;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .dev-eui { 
            font-weight: bold; 
            color: #2196F3;
            font-family: monospace;
        }
        .uplink-count {
            background: #4CAF50;
            color: white;
            padding: 5px 15px;
            border-radius: 20px;
            font-size: 14px;
        }
        button {
            background: #2196F3;
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 5px;
            cursor: pointer;
            font-size: 16px;
        }
        button:hover { background: #1976D2; }
        .loading { text-align: center; color: #666; }
    </style>
</head>
<body>
    <h1>📱 LoRaWAN Device Monitor</h1>
    <button onclick="loadDevices()">🔄 Refresh Devices</button>
    <div id="devices" class="loading">Click refresh to load devices...</div>

    <script>
        async function loadDevices() {
            const devicesDiv = document.getElementById('devices');
            devicesDiv.innerHTML = '<div class="loading">⏳ Loading devices...</div>';
            
            try {
                const response = await fetch('http://localhost:5000/api/uplinks/devices', {
                    headers: { 'X-API-Key': 'your_api_key_here' }
                });
                
                const devices = await response.json();
                
                if (devices.length === 0) {
                    devicesDiv.innerHTML = '<p>No devices found.</p>';
                    return;
                }
                
                devicesDiv.innerHTML = devices.map(device => `
                    <div class="device-card">
                        <span class="dev-eui">📡 ${device.dev_eui}</span>
                        <span class="uplink-count">${device.uplink_count} packets</span>
                    </div>
                `).join('');
                
            } catch (error) {
                devicesDiv.innerHTML = `<p style="color: red;">❌ Error: ${error.message}</p>`;
            }
        }
    </script>
</body>
</html>
```

</details>

---

### 📥 Uplinks - Data Compact

> **💡 Tip:** Gunakan mode compact untuk dashboard dan monitoring real-time karena response lebih ringan.

#### 📊 Get Device Uplinks (Paginated)

Ambil data uplink device dengan pagination dan filter waktu.

<details>
<summary><strong>📋 Endpoint Details</strong></summary>

**HTTP Method:** `GET`  
**Endpoint:** `/api/uplinks/{dev_eui}`  
**Auth Required:** ✅ Yes

**Path Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `dev_eui` | string | ✅ | Device EUI (16 hex chars) |

**Query Parameters:**
| Parameter | Type | Default | Max | Description |
|-----------|------|---------|-----|-------------|
| `limit` | integer | 50 | 500 | Records per page |
| `offset` | integer | 0 | - | Pagination offset |
| `from` | timestamp | - | - | Filter from this time |
| `to` | timestamp | - | - | Filter until this time |

**Response Fields:**
| Field | Type | Description |
|-------|------|-------------|
| `uplink_id` | integer | Unique uplink identifier |
| `inserted_at` | timestamp | Database insertion time |
| `app_name` | string | LoRaWAN application name |
| `dev_eui` | string | Device EUI |
| `device_name` | string | Device friendly name |
| `ts` | timestamp | Device timestamp |
| `fcnt` | integer | Frame counter |
| `fport` | integer | LoRaWAN port number |
| `data_hex` | string | Payload in hexadecimal |
| `data_text` | string | Payload as text |
| `data_json` | object | Parsed JSON payload |
| `rssi_dbm` | float | Signal strength (dBm) |
| `snr_db` | float | Signal-to-noise ratio (dB) |
| `dr` | string | Data rate |
| `freq_hz` | integer | Frequency (Hz) |

</details>

<details>
<summary><strong>💻 Code Examples</strong></summary>

**🔸 Basic Request (cURL)**
```bash
curl -X GET "http://localhost:5000/api/uplinks/BE078DDB76F70371" \
  -H "X-API-Key: your_api_key_here"
```

**🔸 With Pagination (cURL)**
```bash
curl -X GET "http://localhost:5000/api/uplinks/BE078DDB76F70371?limit=100&offset=0" \
  -H "X-API-Key: your_api_key_here"
```

**🔸 With Time Filter (cURL)**
```bash
curl -X GET "http://localhost:5000/api/uplinks/BE078DDB76F70371?from=2024-01-01T00:00:00&to=2024-01-31T23:59:59" \
  -H "X-API-Key: your_api_key_here"
```

**🔸 JavaScript Function**
```javascript
async function getUplinks(devEUI, options = {}) {
    const { 
        limit = 50, 
        offset = 0, 
        from = null, 
        to = null 
    } = options;
    
    // Build query string
    const params = new URLSearchParams({ limit, offset });
    if (from) params.append('from', from);
    if (to) params.append('to', to);
    
    const url = `${baseUrl}/api/uplinks/${devEUI}?${params}`;
    
    try {
        const response = await fetch(url, {
            headers: { 'X-API-Key': apiKey }
        });
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        
        const uplinks = await response.json();
        console.log(`📥 Retrieved ${uplinks.length} uplinks`);
        return uplinks;
        
    } catch (error) {
        console.error('❌ Error fetching uplinks:', error);
        throw error;
    }
}

// Usage examples:
// Get first 10 uplinks
getUplinks('BE078DDB76F70371', { limit: 10 });

// Get uplinks from specific date range
getUplinks('BE078DDB76F70371', {
    from: '2024-01-01T00:00:00',
    to: '2024-01-31T23:59:59',
    limit: 100
});
```

**🔸 Interactive HTML Dashboard**
```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>📊 Uplink Monitor</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: 'Segoe UI', Tahoma, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 15px;
            padding: 30px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.3);
        }
        h1 { color: #333; margin-bottom: 20px; }
        .controls {
            display: flex;
            gap: 10px;
            margin-bottom: 20px;
            flex-wrap: wrap;
        }
        input, button {
            padding: 10px 15px;
            border: 2px solid #ddd;
            border-radius: 5px;
            font-size: 14px;
        }
        button {
            background: #667eea;
            color: white;
            border: none;
            cursor: pointer;
            transition: all 0.3s;
        }
        button:hover { background: #5568d3; transform: translateY(-2px); }
        .uplink-card {
            background: #f8f9fa;
            border-left: 4px solid #667eea;
            padding: 15px;
            margin: 10px 0;
            border-radius: 5px;
            transition: all 0.3s;
        }
        .uplink-card:hover {
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
            transform: translateX(5px);
        }
        .uplink-header {
            display: flex;
            justify-content: space-between;
            margin-bottom: 10px;
        }
        .timestamp { 
            color: #666; 
            font-size: 12px;
        }
        .signal-info {
            display: flex;
            gap: 15px;
            font-size: 12px;
            color: #888;
        }
        .signal-badge {
            background: #e3f2fd;
            padding: 3px 8px;
            border-radius: 3px;
            color: #1976d2;
        }
        .data-payload {
            background: #263238;
            color: #aed581;
            padding: 10px;
            border-radius: 5px;
            font-family: 'Courier New', monospace;
            margin-top: 10px;
            overflow-x: auto;
        }
        .loading {
            text-align: center;
            padding: 40px;
            color: #666;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>📊 LoRaWAN Uplink Monitor</h1>
        
        <div class="controls">
            <input type="text" id="devEUI" placeholder="Device EUI (16 hex)" value="BE078DDB76F70371">
            <input type="number" id="limit" placeholder="Limit" value="10" min="1" max="500">
            <button onclick="loadUplinks()">🔍 Load Uplinks</button>
            <button onclick="autoRefresh()">🔄 Auto Refresh</button>
        </div>
        
        <div id="uplinks" class="loading">
            Click "Load Uplinks" to fetch data 📡
        </div>
    </div>

    <script>
        const API_KEY = 'your_api_key_here';
        const BASE_URL = 'http://localhost:5000';
        let refreshInterval = null;

        async function loadUplinks() {
            const devEUI = document.getElementById('devEUI').value.trim();
            const limit = document.getElementById('limit').value;
            const uplinksDiv = document.getElementById('uplinks');
            
            if (!devEUI || devEUI.length !== 16) {
                uplinksDiv.innerHTML = '<div class="loading">⚠️ Please enter valid 16-character DevEUI</div>';
                return;
            }
            
            uplinksDiv.innerHTML = '<div class="loading">⏳ Loading uplinks...</div>';
            
            try {
                const response = await fetch(
                    `${BASE_URL}/api/uplinks/${devEUI}?limit=${limit}`,
                    { headers: { 'X-API-Key': API_KEY } }
                );
                
                if (!response.ok) throw new Error(`HTTP ${response.status}`);
                
                const uplinks = await response.json();
                
                if (uplinks.length === 0) {
                    uplinksDiv.innerHTML = '<div class="loading">📭 No uplinks found</div>';
                    return;
                }
                
                uplinksDiv.innerHTML = uplinks.map(uplink => `
                    <div class="uplink-card">
                        <div class="uplink-header">
                            <strong>📦 Uplink #${uplink.fcnt}</strong>
                            <span class="timestamp">🕐 ${new Date(uplink.ts).toLocaleString()}</span>
                        </div>
                        <div>Device: <code>${uplink.device_name || uplink.dev_eui}</code></div>
                        <div>Port: <strong>${uplink.fport}</strong></div>
                        <div class="signal-info">
                            <span class="signal-badge">📶 RSSI: ${uplink.rssi_dbm} dBm</span>
                            <span class="signal-badge">📡 SNR: ${uplink.snr_db} dB</span>
                            <span class="signal-badge">⚡ DR: ${uplink.dr}</span>
                        </div>
                        ${uplink.data_hex ? `
                            <div class="data-payload">
                                <strong>HEX:</strong> ${uplink.data_hex}<br>
                                ${uplink.data_text ? `<strong>TEXT:</strong> ${uplink.data_text}` : ''}
                            </div>
                        ` : ''}
                    </div>
                `).join('');
                
            } catch (error) {
                uplinksDiv.innerHTML = `<div class="loading">❌ Error: ${error.message}</div>`;
            }
        }
        
        function autoRefresh() {
            if (refreshInterval) {
                clearInterval(refreshInterval);
                refreshInterval = null;
                alert('🛑 Auto-refresh stopped');
            } else {
                loadUplinks();
                refreshInterval = setInterval(loadUplinks, 5000);
                alert('✅ Auto-refresh every 5 seconds');
            }
        }
    </script>
</body>
</html>
```

</details>

---

#### ⚡ Get Latest Uplink

Ambil data uplink terbaru dari device (single record).

<details>
<summary><strong>📋 Endpoint Details</strong></summary>

**HTTP Method:** `GET`  
**Endpoint:** `/api/uplinks/{dev_eui}/latest`  
**Auth Required:** ✅ Yes

**Response:** Single uplink object (same fields as paginated endpoint)

</details>

<details>
<summary><strong>💻 Code Examples</strong></summary>

**🔸 cURL**
```bash
curl -X GET "http://localhost:5000/api/uplinks/BE078DDB76F70371/latest" \
  -H "X-API-Key: your_api_key_here"
```

**🔸 JavaScript**
```javascript
async function getLatestUplink(devEUI) {
    try {
        const response = await fetch(
            `${baseUrl}/api/uplinks/${devEUI}/latest`,
            { headers: { 'X-API-Key': apiKey } }
        );
        
        if (!response.ok) {
            throw new Error(response.status === 404 
                ? 'Device has no uplinks yet' 
                : 'Failed to fetch latest uplink'
            );
        }
        
        const uplink = await response.json();
        console.log('⚡ Latest uplink:', uplink);
        
        // Display formatted info
        console.log(`📡 Device: ${uplink.device_name || uplink.dev_eui}`);
        console.log(`🕐 Time: ${new Date(uplink.ts).toLocaleString()}`);
        console.log(`📶 RSSI: ${uplink.rssi_dbm} dBm`);
        console.log(`📊 Data: ${uplink.data_hex}`);
        
        return uplink;
        
    } catch (error) {
        console.error('❌', error.message);
        throw error;
    }
}

// Usage
getLatestUplink('BE078DDB76F70371');
```

</details>

---

#### 📋 Get Last N Uplinks

Ambil beberapa uplink terakhir (default 10, max 500).

<details>
<summary><strong>📋 Endpoint Details</strong></summary>

**HTTP Method:** `GET`  
**Endpoint:** `/api/uplinks/{dev_eui}/last10`  
**Auth Required:** ✅ Yes

**Query Parameters:**
| Parameter | Type | Default | Max | Description |
|-----------|------|---------|-----|-------------|
| `n` | integer | 10 | 500 | Number of records |

</details>

<details>
<summary><strong>💻 Code Examples</strong></summary>

**🔸 cURL (Last 10)**
```bash
curl -X GET "http://localhost:5000/api/uplinks/BE078DDB76F70371/last10" \
  -H "X-API-Key: your_api_key_here"
```

**🔸 cURL (Last 25)**
```bash
curl -X GET "http://localhost:5000/api/uplinks/BE078DDB76F70371/last10?n=25" \
  -H "X-API-Key: your_api_key_here"
```

**🔸 JavaScript**
```javascript
async function getLastNUplinks(devEUI, n = 10) {
    try {
        const response = await fetch(
            `${baseUrl}/api/uplinks/${devEUI}/last10?n=${n}`,
            { headers: { 'X-API-Key': apiKey } }
        );
        
        if (!response.ok) throw new Error('Failed to fetch uplinks');
        
        const uplinks = await response.json();
        console.log(`📋 Last ${n} uplinks:`, uplinks.length);
        
        // Show quick stats
        const avgRSSI = uplinks.reduce((sum, u) => sum + u.rssi_dbm, 0) / uplinks.length;
        console.log(`📊 Average RSSI: ${avgRSSI.toFixed(2)} dBm`);
        
        return uplinks;
        
    } catch (error) {
        console.error('❌ Error:', error);
        throw error;
    }
}

// Usage
getLastNUplinks('BE078DDB76F70371', 25);
```

</details>

---

### 📊 Uplinks - Data Full

> **📝 Note:** Mode full mengembalikan semua field termasuk `app_id` dan `raw` JSON. Gunakan untuk debugging atau analisis mendalam.

#### 📦 Get Full Uplinks (Paginated)

Sama seperti compact endpoint, tapi dengan tambahan field `app_id` dan `raw`.

<details>
<summary><strong>📋 Endpoint Details</strong></summary>

**HTTP Method:** `GET`  
**Endpoint:** `/api/uplinks/{dev_eui}/full`  
**Auth Required:** ✅ Yes

**Additional Response Fields:**
- `app_id`: Application ID (internal)
- `raw`: Complete raw JSON from gateway

**Query Parameters:** Same as compact version

</details>

<details>
<summary><strong>💻 Code Examples</strong></summary>

**🔸 cURL**
```bash
curl -X GET "http://localhost:5000/api/uplinks/BE078DDB76F70371/full?limit=10" \
  -H "X-API-Key: your_api_key_here"
```

**🔸 JavaScript**
```javascript
async function getFullUplinks(devEUI, options = {}) {
    const { limit = 50, offset = 0, from, to } = options;
    const params = new URLSearchParams({ limit, offset });
    if (from) params.append('from', from);
    if (to) params.append('to', to);
    
    try {
        const response = await fetch(
            `${baseUrl}/api/uplinks/${devEUI}/full?${params}`,
            { headers: { 'X-API-Key': apiKey } }
        );
        
        if (!response.ok) throw new Error('Failed to fetch full uplinks');
        
        const uplinks = await response.json();
        console.log('📦 Full uplinks retrieved:', uplinks.length);
        
        // Access raw data for debugging
        uplinks.forEach(uplink => {
            console.log('Raw gateway data:', uplink.raw);
        });
        
        return uplinks;
    } catch (error) {
        console.error('❌ Error:', error);
        throw error;
    }
}
```

</details>

---

#### 📦 Get Latest Full Uplink

Ambil uplink terakhir dengan semua field.

<details>
<summary><strong>📋 Endpoint Details</strong></summary>

**HTTP Method:** `GET`  
**Endpoint:** `/api/uplinks/{dev_eui}/latest/full`  
**Auth Required:** ✅ Yes

</details>

<details>
<summary><strong>💻 Code Examples</strong></summary>

**🔸 cURL**
```bash
curl -X GET "http://localhost:5000/api/uplinks/BE078DDB76F70371/latest/full" \
  -H "X-API-Key: your_api_key_here"
```

**🔸 JavaScript**
```javascript
async function getLatestFullUplink(devEUI) {
    try {
        const response = await fetch(
            `${baseUrl}/api/uplinks/${devEUI}/latest/full`,
            { headers: { 'X-API-Key': apiKey } }
        );
        
        if (!response.ok) throw new Error('Device has no uplinks');
        
        const uplink = await response.json();
        console.log('📦 Latest full uplink:', uplink);
        
        // Parse raw data for gateway info
        if (uplink.raw) {
            const raw = typeof uplink.raw === 'string' 
                ? JSON.parse(uplink.raw) 
                : uplink.raw;
            console.log('🔍 Gateway info:', raw.rxInfo);
        }
        
        return uplink;
    } catch (error) {
        console.error('❌ Error:', error);
        throw error;
    }
}
```

</details>

---

### 📤 Downlink Commands

> **⚡ Real-time:** Downlink commands dikirim langsung ke device via MQTT broker.

#### 📨 Send Downlink to Device

Kirim perintah atau data ke device melalui network LoRaWAN.

<details>
<summary><strong>📋 Endpoint Details</strong></summary>

**HTTP Method:** `POST`  
**Endpoint:** `/api/downlink`  
**Auth Required:** ✅ Yes  
**Content-Type:** `application/json`

**Request Body:**
```json
{
  "applicationName": "LabElektro",
  "devEUI": "be078ddb76f70371",
  "fPort": 1,
  "confirmed": false,
  "data_hex": "414243",
  "data_text": "ABC"
}
```

**Body Parameters:**
| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `applicationName` | string | ✅ | - | LoRaWAN application name |
| `devEUI` | string | ✅ | - | Device EUI (auto-lowercase) |
| `fPort` | integer | ❌ | 1 | LoRaWAN port (1-223) |
| `confirmed` | boolean | ❌ | false | Request ACK from device |
| `data_hex` | string | ⚠️ | - | Hex payload (e.g., "414243") |
| `data_text` | string | ⚠️ | - | Text payload (auto-convert to hex) |

> **⚠️ Important:** Either `data_hex` OR `data_text` must be provided.

**Success Response (200):**
```json
{
  "published": true,
  "topic": "application/LabElektro/device/be078ddb76f70371/tx",
  "payload": {
    "confirmed": false,
    "fPort": 1,
    "data": "414243",
    "data_encode": "hexstring"
  }
}
```

</details>

<details>
<summary><strong>💻 Code Examples</strong></summary>

**🔸 cURL - Send Hex Data**
```bash
curl -X POST "http://localhost:5000/api/downlink" \
  -H "X-API-Key: your_api_key_here" \
  -H "Content-Type: application/json" \
  -d '{
    "applicationName": "LabElektro",
    "devEUI": "be078ddb76f70371",
    "fPort": 1,
    "confirmed": false,
    "data_hex": "414243"
  }'
```

**🔸 cURL - Send Text Data**
```bash
curl -X POST "http://localhost:5000/api/downlink" \
  -H "X-API-Key: your_api_key_here" \
  -H "Content-Type: application/json" \
  -d '{
    "applicationName": "LabElektro",
    "devEUI": "be078ddb76f70371",
    "fPort": 1,
    "confirmed": true,
    "data_text": "Hello Device"
  }'
```

**🔸 cURL - Turn On LED Example**
```bash
# Send command 0x01 to turn on LED on port 2
curl -X POST "http://localhost:5000/api/downlink" \
  -H "X-API-Key: your_api_key_here" \
  -H "Content-Type: application/json" \
  -d '{
    "applicationName": "LabElektro",
    "devEUI": "be078ddb76f70371",
    "fPort": 2,
    "confirmed": true,
    "data_hex": "01"
  }'
```

**🔸 JavaScript Function**
```javascript
async function sendDownlink(params) {
    const {
        applicationName,
        devEUI,
        fPort = 1,
        confirmed = false,
        data_hex,
        data_text
    } = params;
    
    // Validate required params
    if (!applicationName || !devEUI) {
        throw new Error('applicationName and devEUI are required');
    }
    
    if (!data_hex && !data_text) {
        throw new Error('Either data_hex or data_text must be provided');
    }
    
    const payload = {
        applicationName,
        devEUI,
        fPort,
        confirmed
    };
    
    // Add data field
    if (data_hex) {
        payload.data_hex = data_hex;
    } else {
        payload.data_text = data_text;
    }
    
    try {
        const response = await fetch(`${baseUrl}/api/downlink`, {
            method: 'POST',
            headers: {
                'X-API-Key': apiKey,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(payload)
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || 'Failed to send downlink');
        }
        
        const result = await response.json();
        console.log('✅ Downlink sent successfully!');
        console.log('📤 Topic:', result.topic);
        console.log('📦 Payload:', result.payload);
        
        return result;
        
    } catch (error) {
        console.error('❌ Failed to send downlink:', error.message);
        throw error;
    }
}

// Usage examples:

// 1. Send hex command
sendDownlink({
    applicationName: 'LabElektro',
    devEUI: 'be078ddb76f70371',
    fPort: 1,
    confirmed: false,
    data_hex: '414243'
});

// 2. Send text message
sendDownlink({
    applicationName: 'LabElektro',
    devEUI: 'be078ddb76f70371',
    fPort: 1,
    confirmed: true,
    data_text: 'Hello Device'
});

// 3. Send control command (turn on actuator)
sendDownlink({
    applicationName: 'LabElektro',
    devEUI: 'be078ddb76f70371',
    fPort: 2,
    confirmed: true,
    data_hex: '01FF' // Command: ON, Value: 255
});
```

**🔸 Interactive HTML Control Panel**
```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>📤 Downlink Control Panel</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', Tahoma, sans-serif;
            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
            padding: 20px;
            min-height: 100vh;
        }
        .container {
            max-width: 600px;
            margin: 0 auto;
            background: white;
            border-radius: 15px;
            padding: 30px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.3);
        }
        h1 { 
            color: #333; 
            margin-bottom: 10px;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        .subtitle {
            color: #666;
            font-size: 14px;
            margin-bottom: 25px;
        }
        .form-group {
            margin-bottom: 20px;
        }
        label {
            display: block;
            margin-bottom: 5px;
            color: #555;
            font-weight: 500;
        }
        input, select, textarea {
            width: 100%;
            padding: 12px;
            border: 2px solid #ddd;
            border-radius: 8px;
            font-size: 14px;
            transition: border-color 0.3s;
        }
        input:focus, select:focus, textarea:focus {
            outline: none;
            border-color: #f5576c;
        }
        .checkbox-group {
            display: flex;
            align-items: center;
            gap: 10px;
        }
        .checkbox-group input[type="checkbox"] {
            width: auto;
        }
        button {
            width: 100%;
            padding: 15px;
            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
            color: white;
            border: none;
            border-radius: 8px;
            font-size: 16px;
            font-weight: bold;
            cursor: pointer;
            transition: all 0.3s;
        }
        button:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(245, 87, 108, 0.4);
        }
        button:disabled {
            background: #ccc;
            cursor: not-allowed;
            transform: none;
        }
        .result {
            margin-top: 20px;
            padding: 15px;
            border-radius: 8px;
            display: none;
        }
        .result.success {
            background: #d4edda;
            color: #155724;
            border: 1px solid #c3e6cb;
            display: block;
        }
        .result.error {
            background: #f8d7da;
            color: #721c24;
            border: 1px solid #f5c6cb;
            display: block;
        }
        .tab-group {
            display: flex;
            gap: 10px;
            margin-bottom: 20px;
        }
        .tab {
            flex: 1;
            padding: 10px;
            background: #f0f0f0;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            font-size: 14px;
            transition: all 0.3s;
        }
        .tab.active {
            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
            color: white;
        }
        .tab-content {
            display: none;
        }
        .tab-content.active {
            display: block;
        }
        code {
            background: #f5f5f5;
            padding: 2px 6px;
            border-radius: 3px;
            font-family: 'Courier New', monospace;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>📤 LoRaWAN Downlink Control</h1>
        <p class="subtitle">Send commands to your LoRaWAN devices in real-time</p>
        
        <form id="downlinkForm">
            <div class="form-group">
                <label>📱 Application Name *</label>
                <input type="text" id="appName" value="LabElektro" required>
            </div>
            
            <div class="form-group">
                <label>🔑 Device EUI * <small>(16 hex characters)</small></label>
                <input type="text" id="devEUI" value="be078ddb76f70371" 
                       pattern="[a-fA-F0-9]{16}" maxlength="16" required>
            </div>
            
            <div class="form-group">
                <label>🚪 Port Number</label>
                <input type="number" id="fPort" value="1" min="1" max="223">
            </div>
            
            <div class="form-group checkbox-group">
                <input type="checkbox" id="confirmed">
                <label for="confirmed" style="margin-bottom: 0;">
                    ✅ Request Confirmation (ACK)
                </label>
            </div>
            
            <div class="tab-group">
                <button type="button" class="tab active" onclick="switchTab('hex')">
                    🔢 HEX Data
                </button>
                <button type="button" class="tab" onclick="switchTab('text')">
                    📝 Text Data
                </button>
            </div>
            
            <div id="hexTab" class="tab-content active">
                <div class="form-group">
                    <label>📦 Hex Payload <small>(e.g., 414243)</small></label>
                    <input type="text" id="dataHex" placeholder="414243" 
                           pattern="[a-fA-F0-9]*">
                </div>
            </div>
            
            <div id="textTab" class="tab-content">
                <div class="form-group">
                    <label>📝 Text Payload <small>(will be converted to hex)</small></label>
                    <textarea id="dataText" rows="3" placeholder="Hello Device"></textarea>
                </div>
            </div>
            
            <button type="submit" id="submitBtn">
                🚀 Send Downlink
            </button>
        </form>
        
        <div id="result" class="result"></div>
    </div>

    <script>
        const API_KEY = 'your_api_key_here';
        const BASE_URL = 'http://localhost:5000';
        let activeTab = 'hex';
        
        function switchTab(tab) {
            activeTab = tab;
            document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
            document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
            
            if (tab === 'hex') {
                document.querySelectorAll('.tab')[0].classList.add('active');
                document.getElementById('hexTab').classList.add('active');
            } else {
                document.querySelectorAll('.tab')[1].classList.add('active');
                document.getElementById('textTab').classList.add('active');
            }
        }
        
        document.getElementById('downlinkForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const submitBtn = document.getElementById('submitBtn');
            const resultDiv = document.getElementById('result');
            
            // Get form values
            const payload = {
                applicationName: document.getElementById('appName').value.trim(),
                devEUI: document.getElementById('devEUI').value.trim(),
                fPort: parseInt(document.getElementById('fPort').value),
                confirmed: document.getElementById('confirmed').checked
            };
            
            // Add data based on active tab
            if (activeTab === 'hex') {
                const hexData = document.getElementById('dataHex').value.trim();
                if (!hexData) {
                    showResult('error', '❌ Please enter hex data');
                    return;
                }
                payload.data_hex = hexData;
            } else {
                const textData = document.getElementById('dataText').value.trim();
                if (!textData) {
                    showResult('error', '❌ Please enter text data');
                    return;
                }
                payload.data_text = textData;
            }
            
            // Disable button during request
            submitBtn.disabled = true;
            submitBtn.textContent = '⏳ Sending...';
            resultDiv.style.display = 'none';
            
            try {
                const response = await fetch(`${BASE_URL}/api/downlink`, {
                    method: 'POST',
                    headers: {
                        'X-API-Key': API_KEY,
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(payload)
                });
                
                const data = await response.json();
                
                if (!response.ok) {
                    throw new Error(data.error || 'Failed to send downlink');
                }
                
                showResult('success', `
                    ✅ <strong>Downlink sent successfully!</strong><br><br>
                    <strong>Topic:</strong> <code>${data.topic}</code><br>
                    <strong>Port:</strong> ${data.payload.fPort}<br>
                    <strong>Data:</strong> <code>${data.payload.data}</code><br>
                    <strong>Confirmed:</strong> ${data.payload.confirmed ? 'Yes ✅' : 'No'}
                `);
                
            } catch (error) {
                showResult('error', `❌ <strong>Error:</strong> ${error.message}`);
            } finally {
                submitBtn.disabled = false;
                submitBtn.textContent = '🚀 Send Downlink';
            }
        });
        
        function showResult(type, message) {
            const resultDiv = document.getElementById('result');
            resultDiv.className = `result ${type}`;
            resultDiv.innerHTML = message;
        }
    </script>
</body>
</html>
```

</details>

<details>
<summary><strong>🎯 Common Use Cases</strong></summary>

**1. Turn On/Off Actuator**
```javascript
// Turn ON (0x01)
sendDownlink({
    applicationName: 'LabElektro',
    devEUI: 'be078ddb76f70371',
    fPort: 2,
    confirmed: true,
    data_hex: '01'
});

// Turn OFF (0x00)
sendDownlink({
    applicationName: 'LabElektro',
    devEUI: 'be078ddb76f70371',
    fPort: 2,
    confirmed: true,
    data_hex: '00'
});
```

**2. Set Sensor Interval**
```javascript
// Set reporting interval to 300 seconds (0x012C in hex)
sendDownlink({
    applicationName: 'LabElektro',
    devEUI: 'be078ddb76f70371',
    fPort: 3,
    confirmed: true,
    data_hex: '012C'
});
```

**3. Request Status**
```javascript
// Request device status (command 0x05)
sendDownlink({
    applicationName: 'LabElektro',
    devEUI: 'be078ddb76f70371',
    fPort: 1,
    confirmed: true,
    data_hex: '05'
});
```

**4. Send Configuration**
```javascript
// Multi-byte configuration
sendDownlink({
    applicationName: 'LabElektro',
    devEUI: 'be078ddb76f70371',
    fPort: 4,
    confirmed: true,
    data_hex: '0A1E3C64' // Various config parameters
});
```

</details>

---

**Endpoint:**
```
POST /api/downlink
```

**Request Body:**
```json
{
  "applicationName": "LabElektro",
  "devEUI": "be078ddb76f70371",
  "fPort": 1,
  "confirmed": false,
  "data_hex": "414243",
  "data_text": "ABC"
}
```

**Body Parameters:**
- `applicationName` (string, required): Nama aplikasi LoRaWAN
- `devEUI` (string, required): Device EUI (akan otomatis dikonversi ke lowercase)
- `fPort` (integer, optional): Port number (default: 1)
- `confirmed` (boolean, optional): Confirmed downlink (default: false)
- `data_hex` (string, optional): Data dalam format hex
- `data_text` (string, optional): Data dalam format text (akan dikonversi ke hex jika data_hex kosong)

**Catatan:** Salah satu dari `data_hex` atau `data_text` harus diisi.

**Response:**
```json
{
  "published": true,
  "topic": "application/LabElektro/device/be078ddb76f70371/tx",
  "payload": {
    "confirmed": false,
    "fPort": 1,
    "data": "414243",
    "data_encode": "hexstring"
  }
}
```

**Contoh cURL:**
```bash
# Dengan data_hex
curl -X POST "http://localhost:5000/api/downlink" \
  -H "X-API-Key: your_api_key_here" \
  -H "Content-Type: application/json" \
  -d '{
    "applicationName": "LabElektro",
    "devEUI": "be078ddb76f70371",
    "fPort": 1,
    "confirmed": false,
    "data_hex": "414243"
  }'

# Dengan data_text
curl -X POST "http://localhost:5000/api/downlink" \
  -H "X-API-Key: your_api_key_here" \
  -H "Content-Type: application/json" \
  -d '{
    "applicationName": "LabElektro",
    "devEUI": "be078ddb76f70371",
    "fPort": 1,
    "confirmed": true,
    "data_text": "Hello Device"
  }'
```

**Contoh HTML:**
```html
<!DOCTYPE html>
<html>
<head>
    <title>Send Downlink</title>
</head>
<body>
    <h1>Send Downlink Command</h1>
    <form id="downlinkForm">
        <label>Application Name:</label>
        <input type="text" id="appName" value="LabElektro"><br><br>
        
        <label>DevEUI:</label>
        <input type="text" id="devEUI" value="be078ddb76f70371"><br><br>
        
        <label>fPort:</label>
        <input type="number" id="fPort" value="1"><br><br>
        
        <label>Confirmed:</label>
        <input type="checkbox" id="confirmed"><br><br>
        
        <label>Data Text:</label>
        <input type="text" id="dataText" placeholder="Enter text data"><br><br>
        
        <button type="submit">Send Downlink</button>
    </form>
    <div id="result"></div>

    <script>
        document.getElementById('downlinkForm').addEventListener('submit', function(e) {
            e.preventDefault();
            
            const payload = {
                applicationName: document.getElementById('appName').value,
                devEUI: document.getElementById('devEUI').value,
                fPort: parseInt(document.getElementById('fPort').value),
                confirmed: document.getElementById('confirmed').checked,
                data_text: document.getElementById('dataText').value
            };
            
            fetch('http://localhost:5000/api/downlink', {
                method: 'POST',
                headers: {
                    'X-API-Key': 'your_api_key_here',
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(payload)
            })
            .then(response => response.json())
            .then(data => {
                document.getElementById('result').innerHTML = 
                    '<pre>' + JSON.stringify(data, null, 2) + '</pre>';
            })
            .catch(error => console.error('Error:', error));
        });
    </script>
</body>
</html>
```

**Contoh JavaScript:**
```javascript
async function sendDownlink(params) {
    const {
        applicationName,
        devEUI,
        fPort = 1,
        confirmed = false,
        data_hex,
        data_text
    } = params;
    
    const payload = {
        applicationName,
        devEUI,
        fPort,
        confirmed
    };
    
    if (data_hex) {
        payload.data_hex = data_hex;
    } else if (data_text) {
        payload.data_text = data_text;
    } else {
        throw new Error('Either data_hex or data_text must be provided');
    }
    
    try {
        const response = await fetch(`${baseUrl}/api/downlink`, {
            method: 'POST',
            headers: {
                'X-API-Key': apiKey,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(payload)
        });
        
        const data = await response.json();
        console.log('Downlink sent:', data);
        return data;
    } catch (error) {
        console.error('Error:', error);
        throw error;
    }
}

// Contoh penggunaan dengan hex
sendDownlink({
    applicationName: 'LabElektro',
    devEUI: 'be078ddb76f70371',
    fPort: 1,
    confirmed: false,
    data_hex: '414243'
});

// Contoh penggunaan dengan text
sendDownlink({
    applicationName: 'LabElektro',
    devEUI: 'be078ddb76f70371',
    fPort: 1,
    confirmed: true,
    data_text: 'Hello Device'
});
```

---

## 📊 Parameter Query

### Pagination

Semua endpoint list mendukung pagination dengan parameter berikut:

| Parameter | Type    | Default | Max | Description                    |
|-----------|---------|---------|-----|--------------------------------|
| limit     | integer | 50      | 500 | Jumlah data per halaman        |
| offset    | integer | 0       | -   | Offset untuk pagination        |

**Contoh:**
```
/api/uplinks/BE078DDB76F70371?limit=100&offset=200
```

### Time Filter

Filter data berdasarkan timestamp:

| Parameter | Type      | Description                          |
|-----------|-----------|--------------------------------------|
| from      | timestamp | Filter data dari timestamp ini       |
| to        | timestamp | Filter data sampai timestamp ini     |

**Contoh:**
```
/api/uplinks/BE078DDB76F70371?from=2024-01-01T00:00:00&to=2024-01-31T23:59:59
```

---

## 📝 Response Format

### Success Response

Semua response sukses mengembalikan JSON dengan data yang diminta.

**Single Object:**
```json
{
  "uplink_id": 12345,
  "dev_eui": "BE078DDB76F70371",
  "device_name": "Sensor-01",
  "ts": "2024-01-15T10:30:00",
  "data_hex": "414243",
  "rssi_dbm": -85,
  "snr_db": 9.5
}
```

**Array of Objects:**
```json
[
  {
    "uplink_id": 12345,
    "dev_eui": "BE078DDB76F70371"
  },
  {
    "uplink_id": 12346,
    "dev_eui": "BE078DDB76F70371"
  }
]
```

### Error Response

Error response menggunakan format berikut:

```json
{
  "error": "Error message description"
}
```

**HTTP Status Codes:**
- `200` - Success
- `400` - Bad Request (invalid parameters)
- `401` - Unauthorized (missing or invalid API key)
- `404` - Not Found (data tidak ditemukan)
- `500` - Internal Server Error

---

## ⚠️ Error Handling

### Common Errors

#### 1. Missing API Key
```json
{
  "error": "API key is required"
}
```

#### 2. Invalid DevEUI
```json
{
  "error": "dev_eui harus 16 karakter hex"
}
```

#### 3. No Data Found
```json
{
  "error": "No uplink found for this dev_eui"
}
```

#### 4. Invalid JSON (Downlink)
```json
{
  "error": "Invalid JSON"
}
```

#### 5. Missing Required Field
```json
{
  "error": "Missing field: applicationName"
}
```

### Error Handling Example (JavaScript)

```javascript
async function getUplinksWithErrorHandling(devEUI) {
    try {
        const response = await fetch(`${baseUrl}/api/uplinks/${devEUI}/latest`, {
            method: 'GET',
            headers: {
                'X-API-Key': apiKey
            }
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || 'Unknown error');
        }
        
        const data = await response.json();
        return data;
    } catch (error) {
        if (error.message.includes('No uplink found')) {
            console.log('Device belum mengirim data');
        } else if (error.message.includes('dev_eui')) {
            console.log('Format DevEUI tidak valid');
        } else {
            console.error('Error:', error.message);
        }
        throw error;
    }
}
```

---

## 🔧 Complete JavaScript Class Example

```javascript
class LoRaWANAPI {
    constructor(baseUrl, apiKey) {
        this.baseUrl = baseUrl;
        this.apiKey = apiKey;
    }
    
    async request(endpoint, options = {}) {
        const url = `${this.baseUrl}${endpoint}`;
        const headers = {
            'X-API-Key': this.apiKey,
            ...options.headers
        };
        
        try {
            const response = await fetch(url, { ...options, headers });
            
            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.error || 'Request failed');
            }
            
            return await response.json();
        } catch (error) {
            console.error('API Error:', error);
            throw error;
        }
    }
    
    // Devices
    async getDevices() {
        return this.request('/api/uplinks/devices');
    }
    
    // Uplinks
    async getUplinks(devEUI, params = {}) {
        const query = new URLSearchParams(params).toString();
        return this.request(`/api/uplinks/${devEUI}${query ? '?' + query : ''}`);
    }
    
    async getLatestUplink(devEUI) {
        return this.request(`/api/uplinks/${devEUI}/latest`);
    }
    
    async getLastNUplinks(devEUI, n = 10) {
        return this.request(`/api/uplinks/${devEUI}/last10?n=${n}`);
    }
    
    async getFullUplinks(devEUI, params = {}) {
        const query = new URLSearchParams(params).toString();
        return this.request(`/api/uplinks/${devEUI}/full${query ? '?' + query : ''}`);
    }
    
    async getLatestFullUplink(devEUI) {
        return this.request(`/api/uplinks/${devEUI}/latest/full`);
    }
    
    // Downlink
    async sendDownlink(params) {
        return this.request('/api/downlink', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(params)
        });
    }
}

// Usage
const api = new LoRaWANAPI('http://localhost:5000', 'your_api_key_here');

// Get all devices
const devices = await api.getDevices();

// Get latest uplink
const latest = await api.getLatestUplink('BE078DDB76F70371');

// Send downlink
await api.sendDownlink({
    applicationName: 'LabElektro',
    devEUI: 'be078ddb76f70371',
    fPort: 1,
    data_text: 'Hello'
});
```

---

## 📌 Tips dan Best Practices

1. **DevEUI Format**: DevEUI harus 16 karakter hex. API akan otomatis mengonversi ke uppercase untuk query, tapi akan menggunakan lowercase untuk MQTT downlink.

2. **Pagination**: Untuk data yang banyak, gunakan pagination dengan kombinasi `limit` dan `offset`.

3. **Time Filter**: Gunakan ISO 8601 format untuk timestamp (`YYYY-MM-DDTHH:mm:ss`).

4. **Error Handling**: Selalu implementasikan error handling yang proper untuk menangani berbagai kemungkinan error.

5. **Rate Limiting**: Pertimbangkan untuk mengimplementasikan rate limiting di sisi client untuk menghindari overload server.

6. **Downlink Data**: Jika tidak yakin dengan format hex, gunakan `data_text` yang akan otomatis dikonversi.

7. **MQTT Topic**: Topic MQTT untuk downlink mengikuti format: `application/{applicationName}/device/{devEUI}/tx`

---

## 📞 Support

Untuk pertanyaan dan dukungan, silakan hubungi tim development.

---

**Last Updated:** 2025
**API Version:** 1.0

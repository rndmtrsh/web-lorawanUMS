# 🚀 LoRaWAN IoT API Documentation

<div align="center">

**API REST untuk mengelola komunikasi uplink dan downlink perangkat LoRaWAN**

[![Version](https://img.shields.io/badge/version-1.0-blue.svg)](https://github.com/yourusername/yourrepo)
[![Python](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/)

</div>

---

## 📋 Daftar Isi

- [Autentikasi](#-autentikasi)
- [Base URL](#-base-url)
- [Available Routes](#-available-routes)
- [Endpoints](#-endpoints)
  - [Devices](#-list-all-devices)
  - [Uplinks](#-uplinks)
  - [Downlink](#-send-downlink)
- [Query Parameters](#-query-parameters)
- [Error Handling](#-error-handling)
- [JavaScript SDK](#-javascript-sdk)

---

## 🔐 Autentikasi

Semua request memerlukan API Key di header:

```http
X-API-Key: your_api_key_here
```

---

## 🌐 Base URL

```
Development: http://localhost:5000
Production:  http://your-server:port
```

---

## 📡 Available Routes

| Method | Endpoint | Description |
|--------|----------|-------------|
| **GET** | `/api/uplinks/devices` | List semua device dan statistik |
| **GET** | `/api/uplinks/{dev_eui}` | List uplinks (compact) |
| **GET** | `/api/uplinks/{dev_eui}/latest` | Uplink terakhir (compact) |
| **GET** | `/api/uplinks/{dev_eui}/last10` | N uplinks terakhir (compact) |
| **GET** | `/api/uplinks/{dev_eui}/full` | List uplinks (full data) |
| **GET** | `/api/uplinks/{dev_eui}/latest/full` | Uplink terakhir (full data) |
| **POST** | `/api/downlink` | Kirim perintah ke device |

---

## 📱 Endpoints

### 📌 List All Devices

Mendapatkan daftar semua device dengan jumlah uplink.

**Request:**
```bash
GET /api/uplinks/devices
```

**cURL:**
```bash
curl -X GET "http://localhost:5000/api/uplinks/devices" \
  -H "X-API-Key: your_api_key_here"
```

**Response:**
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

**JavaScript:**
```javascript
const response = await fetch('http://localhost:5000/api/uplinks/devices', {
    headers: { 'X-API-Key': 'your_api_key_here' }
});
const devices = await response.json();
console.log(devices);
```

---

### 📥 Uplinks

#### Get Uplinks (Compact)

**Request:**
```bash
GET /api/uplinks/{dev_eui}?limit=50&offset=0
```

**Query Parameters:**
- `limit` (optional): Jumlah data, default 50, max 500
- `offset` (optional): Offset untuk pagination, default 0
- `from` (optional): Filter dari timestamp (ISO 8601)
- `to` (optional): Filter sampai timestamp (ISO 8601)

**cURL:**
```bash
# Basic
curl -X GET "http://localhost:5000/api/uplinks/BE078DDB76F70371" \
  -H "X-API-Key: your_api_key_here"

# With pagination
curl -X GET "http://localhost:5000/api/uplinks/BE078DDB76F70371?limit=100&offset=0" \
  -H "X-API-Key: your_api_key_here"

# With time filter
curl -X GET "http://localhost:5000/api/uplinks/BE078DDB76F70371?from=2024-01-01T00:00:00&to=2024-01-31T23:59:59" \
  -H "X-API-Key: your_api_key_here"
```

**Response:**
```json
[
  {
    "uplink_id": 12345,
    "inserted_at": "2024-01-15T10:30:00",
    "app_name": "LabElektro",
    "dev_eui": "BE078DDB76F70371",
    "device_name": "Sensor-01",
    "ts": "2024-01-15T10:30:00",
    "fcnt": 42,
    "fport": 1,
    "data_hex": "414243",
    "data_text": "ABC",
    "data_json": null,
    "rssi_dbm": -85,
    "snr_db": 9.5,
    "dr": "SF7BW125",
    "freq_hz": 868100000
  }
]
```

**JavaScript:**
```javascript
async function getUplinks(devEUI, limit = 50, offset = 0) {
    const url = `http://localhost:5000/api/uplinks/${devEUI}?limit=${limit}&offset=${offset}`;
    const response = await fetch(url, {
        headers: { 'X-API-Key': 'your_api_key_here' }
    });
    return await response.json();
}

// Penggunaan
const uplinks = await getUplinks('BE078DDB76F70371', 10);
console.log(uplinks);
```

**HTML Example:**
```html
<!DOCTYPE html>
<html>
<head>
    <title>Get Uplinks</title>
</head>
<body>
    <h1>Device Uplinks</h1>
    <input type="text" id="devEUI" placeholder="DevEUI" value="BE078DDB76F70371">
    <button onclick="loadUplinks()">Load Data</button>
    <pre id="result"></pre>

    <script>
        async function loadUplinks() {
            const devEUI = document.getElementById('devEUI').value;
            const response = await fetch(`http://localhost:5000/api/uplinks/${devEUI}?limit=10`, {
                headers: { 'X-API-Key': 'your_api_key_here' }
            });
            const data = await response.json();
            document.getElementById('result').textContent = JSON.stringify(data, null, 2);
        }
    </script>
</body>
</html>
```

---

#### Get Latest Uplink

**Request:**
```bash
GET /api/uplinks/{dev_eui}/latest
```

**cURL:**
```bash
curl -X GET "http://localhost:5000/api/uplinks/BE078DDB76F70371/latest" \
  -H "X-API-Key: your_api_key_here"
```

**JavaScript:**
```javascript
async function getLatestUplink(devEUI) {
    const response = await fetch(`http://localhost:5000/api/uplinks/${devEUI}/latest`, {
        headers: { 'X-API-Key': 'your_api_key_here' }
    });
    return await response.json();
}

const latest = await getLatestUplink('BE078DDB76F70371');
console.log('Latest uplink:', latest);
```

---

#### Get Last N Uplinks

**Request:**
```bash
GET /api/uplinks/{dev_eui}/last10?n=10
```

**Query Parameters:**
- `n` (optional): Jumlah data, default 10, max 500

**cURL:**
```bash
# Last 10 (default)
curl -X GET "http://localhost:5000/api/uplinks/BE078DDB76F70371/last10" \
  -H "X-API-Key: your_api_key_here"

# Last 25
curl -X GET "http://localhost:5000/api/uplinks/BE078DDB76F70371/last10?n=25" \
  -H "X-API-Key: your_api_key_here"
```

**JavaScript:**
```javascript
async function getLastNUplinks(devEUI, n = 10) {
    const response = await fetch(`http://localhost:5000/api/uplinks/${devEUI}/last10?n=${n}`, {
        headers: { 'X-API-Key': 'your_api_key_here' }
    });
    return await response.json();
}

const last10 = await getLastNUplinks('BE078DDB76F70371', 10);
```

---

#### Get Full Uplinks

Sama seperti compact version, tapi termasuk field `app_id` dan `raw`.

**Request:**
```bash
GET /api/uplinks/{dev_eui}/full?limit=50&offset=0
```

**cURL:**
```bash
curl -X GET "http://localhost:5000/api/uplinks/BE078DDB76F70371/full?limit=10" \
  -H "X-API-Key: your_api_key_here"
```

**JavaScript:**
```javascript
async function getFullUplinks(devEUI, limit = 50) {
    const response = await fetch(`http://localhost:5000/api/uplinks/${devEUI}/full?limit=${limit}`, {
        headers: { 'X-API-Key': 'your_api_key_here' }
    });
    return await response.json();
}
```

---

#### Get Latest Full Uplink

**Request:**
```bash
GET /api/uplinks/{dev_eui}/latest/full
```

**cURL:**
```bash
curl -X GET "http://localhost:5000/api/uplinks/BE078DDB76F70371/latest/full" \
  -H "X-API-Key: your_api_key_here"
```

---

### 📤 Send Downlink

Mengirim perintah ke device via MQTT.

**Request:**
```bash
POST /api/downlink
Content-Type: application/json
```

**Request Body:**
```json
{
  "applicationName": "LabElektro",
  "devEUI": "be078ddb76f70371",
  "fPort": 1,
  "confirmed": false,
  "data_hex": "414243"
}
```

**Parameters:**
| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `applicationName` | string | ✅ | - | Nama aplikasi LoRaWAN |
| `devEUI` | string | ✅ | - | Device EUI (16 hex chars) |
| `fPort` | integer | ❌ | 1 | Port number (1-223) |
| `confirmed` | boolean | ❌ | false | Request ACK dari device |
| `data_hex` | string | ⚠️ | - | Data hex (e.g., "414243") |
| `data_text` | string | ⚠️ | - | Data text (auto-convert to hex) |

> **Note:** Salah satu dari `data_hex` atau `data_text` harus diisi.

**cURL - Send Hex:**
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

**cURL - Send Text:**
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

**JavaScript:**
```javascript
async function sendDownlink(appName, devEUI, data_hex, fPort = 1, confirmed = false) {
    const response = await fetch('http://localhost:5000/api/downlink', {
        method: 'POST',
        headers: {
            'X-API-Key': 'your_api_key_here',
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            applicationName: appName,
            devEUI: devEUI,
            fPort: fPort,
            confirmed: confirmed,
            data_hex: data_hex
        })
    });
    return await response.json();
}

// Penggunaan
const result = await sendDownlink('LabElektro', 'be078ddb76f70371', '414243');
console.log('Downlink sent:', result);
```

**HTML Example:**
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
        
        <label>Port:</label>
        <input type="number" id="fPort" value="1"><br><br>
        
        <label>Data Hex:</label>
        <input type="text" id="dataHex" placeholder="414243"><br><br>
        
        <label>
            <input type="checkbox" id="confirmed">
            Confirmed
        </label><br><br>
        
        <button type="submit">Send</button>
    </form>
    <pre id="result"></pre>

    <script>
        document.getElementById('downlinkForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const payload = {
                applicationName: document.getElementById('appName').value,
                devEUI: document.getElementById('devEUI').value,
                fPort: parseInt(document.getElementById('fPort').value),
                confirmed: document.getElementById('confirmed').checked,
                data_hex: document.getElementById('dataHex').value
            };
            
            const response = await fetch('http://localhost:5000/api/downlink', {
                method: 'POST',
                headers: {
                    'X-API-Key': 'your_api_key_here',
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(payload)
            });
            
            const result = await response.json();
            document.getElementById('result').textContent = JSON.stringify(result, null, 2);
        });
    </script>
</body>
</html>
```

---

## 🔧 Query Parameters

### Pagination

| Parameter | Type | Default | Max | Description |
|-----------|------|---------|-----|-------------|
| `limit` | integer | 50 | 500 | Jumlah data per halaman |
| `offset` | integer | 0 | - | Skip n records |

**Contoh:**
```bash
/api/uplinks/BE078DDB76F70371?limit=100&offset=50
```

### Time Filter

| Parameter | Type | Description |
|-----------|------|-------------|
| `from` | timestamp | Filter dari waktu ini (ISO 8601) |
| `to` | timestamp | Filter sampai waktu ini (ISO 8601) |

**Contoh:**
```bash
/api/uplinks/BE078DDB76F70371?from=2024-01-01T00:00:00&to=2024-01-31T23:59:59
```

**JavaScript Helper:**
```javascript
// Get today's data
const today = new Date().toISOString().split('T')[0];
const params = {
    from: `${today}T00:00:00`,
    to: `${today}T23:59:59`
};

// Get last 24 hours
const now = new Date();
const yesterday = new Date(now - 24*60*60*1000);
const params = {
    from: yesterday.toISOString(),
    to: now.toISOString()
};
```

---

## ⚠️ Error Handling

### HTTP Status Codes

| Code | Status | Description |
|------|--------|-------------|
| 200 | ✅ OK | Request berhasil |
| 400 | ❌ Bad Request | Parameter invalid |
| 401 | 🔒 Unauthorized | API key invalid/missing |
| 404 | 🔍 Not Found | Data tidak ditemukan |
| 500 | 💥 Server Error | Internal server error |

### Error Response Format

```json
{
  "error": "Error message description"
}
```

### Common Errors

**1. Missing API Key (401)**
```json
{ "error": "API key is required" }
```

**2. Invalid DevEUI (400)**
```json
{ "error": "dev_eui harus 16 karakter hex" }
```

**3. No Data Found (404)**
```json
{ "error": "No uplink found for this dev_eui" }
```

**4. Invalid JSON (400)**
```json
{ "error": "Invalid JSON" }
```

**5. Missing Field (400)**
```json
{ "error": "Missing field: applicationName" }
```

### Error Handling Example

```javascript
async function fetchWithErrorHandling(url, options = {}) {
    try {
        const response = await fetch(url, options);
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || `HTTP ${response.status}`);
        }
        
        return await response.json();
    } catch (error) {
        console.error('API Error:', error.message);
        throw error;
    }
}

// Penggunaan
try {
    const data = await fetchWithErrorHandling('http://localhost:5000/api/uplinks/devices', {
        headers: { 'X-API-Key': 'your_api_key_here' }
    });
    console.log(data);
} catch (error) {
    // Handle error
}
```

---

## 💻 JavaScript SDK

SDK lengkap untuk memudahkan integrasi.

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
        
        const response = await fetch(url, { ...options, headers });
        
        if (!response.ok) {
            const error = await response.json().catch(() => ({}));
            throw new Error(error.error || `HTTP ${response.status}`);
        }
        
        return await response.json();
    }
    
    // Devices
    getDevices() {
        return this.request('/api/uplinks/devices');
    }
    
    // Uplinks
    getUplinks(devEUI, params = {}) {
        const query = new URLSearchParams(params).toString();
        return this.request(`/api/uplinks/${devEUI}${query ? '?' + query : ''}`);
    }
    
    getLatestUplink(devEUI) {
        return this.request(`/api/uplinks/${devEUI}/latest`);
    }
    
    getLastNUplinks(devEUI, n = 10) {
        return this.request(`/api/uplinks/${devEUI}/last10?n=${n}`);
    }
    
    getFullUplinks(devEUI, params = {}) {
        const query = new URLSearchParams(params).toString();
        return this.request(`/api/uplinks/${devEUI}/full${query ? '?' + query : ''}`);
    }
    
    getLatestFullUplink(devEUI) {
        return this.request(`/api/uplinks/${devEUI}/latest/full`);
    }
    
    // Downlink
    sendDownlink(params) {
        return this.request('/api/downlink', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(params)
        });
    }
}

// ==================== USAGE ====================

// Initialize
const api = new LoRaWANAPI('http://localhost:5000', 'your_api_key_here');

// Get all devices
const devices = await api.getDevices();
console.log('Devices:', devices);

// Get latest uplink
const latest = await api.getLatestUplink('BE078DDB76F70371');
console.log('Latest:', latest);

// Get uplinks with filter
const uplinks = await api.getUplinks('BE078DDB76F70371', {
    limit: 100,
    from: '2024-01-01T00:00:00',
    to: '2024-01-31T23:59:59'
});
console.log('Uplinks:', uplinks);

// Send downlink
const result = await api.sendDownlink({
    applicationName: 'LabElektro',
    devEUI: 'be078ddb76f70371',
    fPort: 1,
    confirmed: true,
    data_hex: '414243'
});
console.log('Downlink sent:', result);
```

---

## 📌 Tips & Best Practices

### 1. DevEUI Format
- DevEUI harus **16 karakter hexadecimal** (0-9, A-F)
- API auto-convert ke uppercase untuk query
- Downlink menggunakan lowercase untuk MQTT

### 2. Pagination
Untuk dataset besar, gunakan pagination:
```javascript
const limit = 500; // max
const offset = 0;
const uplinks = await api.getUplinks(devEUI, { limit, offset });
```

### 3. Time Filters
Gunakan ISO 8601 format:
```javascript
const params = {
    from: '2024-01-01T00:00:00',
    to: '2024-01-31T23:59:59'
};
```

### 4. Error Handling
Selalu wrap API calls dengan try-catch:
```javascript
try {
    const data = await api.getLatestUplink(devEUI);
} catch (error) {
    console.error('Error:', error.message);
}
```

### 5. Downlink Confirmed
Gunakan `confirmed: true` untuk perintah penting:
```javascript
await api.sendDownlink({
    applicationName: 'LabElektro',
    devEUI: 'be078ddb76f70371',
    fPort: 2,
    confirmed: true,  // Request ACK
    data_hex: '01'
});
```

---

## 📞 Support

Untuk pertanyaan dan dukungan:
- **Email:** support@example.com
- **GitHub Issues:** [Report Bug](https://github.com/example/issues)

---

<div align="center">

**Version 1.0** | Last Updated: 2025

Made with ❤️ for IoT Developers

</div>

# Mitsubishi ILP IR Control

A FastAPI-based application for controlling Mitsubishi HVAC systems using IR signals via Raspberry Pi GPIO.

## 🚀 Features
- Control Mitsubishi HVAC using **FastAPI**
- Sends **IR signals** via Raspberry Pi GPIO
- Supports **cooling, heating, fan speed, temperature, and vane position settings**
- Works with **Raspberry Pi Zero W**
- **Optional web UI** for controlling the endpoints from a modern browser

### Project background
- Code in IrSender folder has been copied (and slightly modified) from [Ericmas001](https://github.com/Ericmas001/HVAC-IR-Control)

## 📜 Requirements
### Hardware
- **Raspberry Pi Zero W** (or other Raspberry Pi models)
- IR LED connected to GPIO
  - Examples for building a Raspberry Pi IR sender can be found [here](https://www.raspberry-pi-geek.com/Archive/2015/10/Raspberry-Pi-IR-remote)
- Mitsubishi HVAC unit
- DS1820 1-wire temperature sensor (optional)

### Software
- **Raspberry Pi OS (Bookworm or Bullseye)**
- **Python 3.9+**
- **FastAPI, Uvicorn, and dependencies**

## 🛠️ Installation
### 1️⃣ Install Raspberry Pi OS
Download and install **Raspberry Pi OS Bookworm** from the official site:
[Download here](https://www.raspberrypi.com/software/)

### 2️⃣ Update Raspberry Pi
```sh
sudo apt update && sudo apt upgrade -y
```

### 3️⃣ Install Required Packages
```sh
sudo apt install -y git python3 python3-pip pigpio python3-pigpio
```

#### 🔧 Important Note on pigpio Usage
When using `libpigpio.so` via `ctypes.CDLL('/usr/lib/libpigpio.so')`, ensure that the `pigpiod` service is **not running**, as they cannot be used simultaneously. This prevents conflicts when accessing the GPIO hardware.

### 4️⃣ Disable Wi-Fi Power Saving (Optional, but Recommended)
- Create a NetworkManager configuration file:
  ```sh
  sudo nano /etc/NetworkManager/conf.d/wifi-powersave-off.conf
  ```
- Add the following content:
  ```ini
  [connection]
  wifi.powersave = 2
  ```
- Save and exit (`CTRL + X`, then `Y`, and `Enter`).
- Restart NetworkManager:
  ```sh
  sudo systemctl restart NetworkManager
  ```
- Verify that Wi-Fi power saving is disabled:
  ```sh
  iw dev wlan0 get power_save
  ```
  Expected output:
  ```
  Power save: off
  ```

### 5️⃣ Clone the Repository
```sh
git clone https://github.com/anttitane/mitsubishi-ilp-ir-control.git
cd mitsubishi-ilp-ir-control
cd src
```

### 6️⃣ Create & Activate Virtual Environment
```sh
python3 -m venv venv
source venv/bin/activate
```

### 7️⃣ Install Python Dependencies
```sh
pip install --upgrade pip
pip install -r requirements.txt
```

### 8️⃣ Configure GPIO Pin
```sh
nano ../config.yaml
```
- Modify pin number to match your setup, save and exit (`CTRL + X`, then `Y`, and `Enter`).

### 9️⃣ Run FastAPI App
```sh
sudo uvicorn main:app --host 0.0.0.0 --port 8000
```
To deactivate the virtual environment:
```sh
deactivate
```

## 🔄 Run App on Boot (Systemd Service)
To automatically start the application on boot, create a **systemd service**:

1️⃣ Create a new systemd service file:
```sh
sudo nano /etc/systemd/system/mitsubishi-ilp.service
```

2️⃣ Add the following content:
```ini
[Unit]
Description=Mitsubishi ILP IR Control API
After=network.target

[Service]
ExecStart=/usr/bin/sudo /home/pi/mitsubishi-ilp-ir-control/src/venv/bin/uvicorn main:app --host 0.0.0.0 --port 8000
WorkingDirectory=/home/pi/mitsubishi-ilp-ir-control/src
Environment="PATH=/home/pi/mitsubishi-ilp-ir-control/src/venv/bin"
Restart=always
User=root
Group=root

[Install]
WantedBy=multi-user.target
```

3️⃣ Reload systemd and enable the service:
```sh
sudo systemctl daemon-reload
sudo systemctl enable mitsubishi-ilp.service
sudo systemctl start mitsubishi-ilp.service
```

4️⃣ Check the service status:
```sh
sudo systemctl status mitsubishi-ilp.service
```

If you need to stop or restart the service:
```sh
sudo systemctl stop mitsubishi-ilp.service
sudo systemctl restart mitsubishi-ilp.service
```

## 🔧 API Endpoints
### **Heating**
**POST /heating/**
#### Request Body (JSON):
```json
{
  "temperature": 22,
  "fan_speed": "high",
  "vertical_mode": "MiddleTop",
  "horizontal_mode": "MiddleRight"
}
```
#### Response:
```json
{
  "status": "Heating command sent"
}
```

### **Cooling**
**POST /cooling/**
#### Request Body (JSON):
```json
{
  "temperature": 20,
  "fan_speed": "auto",
  "vertical_mode": "Top",
  "horizontal_mode": "Left"
}
```
#### Response:
```json
{
  "status": "Cooling command sent"
}
```

### **Turn Off Air Pump**
**POST /turn_off/**
#### Request Body (JSON):
```json
{ }
```
#### Response:
```json
{
  "status": "Powered off"
}
```

### **Room Temperature**
**GET /air_pump/room_temperature/**

Retrieves the current room temperature from the connected DS1820 1-wire temperature sensor.

#### Response:
```json
{
  "status": "success",
  "message": "Room temperature retrieved",
  "details": {
    "temperature": 23.5,
    "unit": "celsius"
  }
}
```

### **Available Options**
#### Fan Speed Options:
- `auto`
- `low`
- `med`
- `high`

#### Vertical Mode Options:
- `Auto`
- `Top`
- `MiddleTop`
- `Middle`
- `MiddleBottom`
- `Bottom`
- `Swing`

#### Horizontal Mode Options:
- `NotSet`
- `Left`
- `MiddleLeft`
- `Middle`
- `MiddleRight`
- `Right`
- `Swing`

### **Test in Browser (Swagger UI)**
Go to **http://localhost:8000/docs**

## 🌐 CORS Configuration for Local/LAN Access
If you want to access these endpoints from different origins (e.g., React on `localhost:3000` or a LAN IP like `192.168.1.*`), you must configure CORS in **`config.yaml`**. For example:

```yaml
cors:
  allow_origins:
    - "http://127.0.0.1"
    - "http://localhost:3000"
  allow_origin_regex: "^http://192\\.168\\.1\\.[0-9]+(:[0-9]+)?$"
  allow_methods:
    - "*"
  allow_headers:
    - "*"
```

Localhost and 192.168.1.x is allowed by default. Adjust the IP range to match your local network.

## 🌡️ Temperature Sensor Configuration
The application supports reading room temperature from a DS1820 1-wire temperature sensor connected to the Raspberry Pi.

### Hardware Setup
1. Connect a DS1820 temperature sensor to your Raspberry Pi's GPIO pins
2. Enable 1-wire interface in Raspberry Pi configuration with `sudo raspi-config` and reboot

### Configuration Options
In `config.yaml`, under the `temperature_sensor` section:

```yaml
temperature_sensor:
  enabled: true              # Set to false to disable the temperature sensor
  device_path: "/sys/bus/w1/devices/28-00000a91e6ad"  # Path to your 1-wire sensor
  refresh_interval: 60       # How often to refresh readings (seconds, 0 = every request)
  display_in_ui: true        # Whether to show temperature in the web UI
```

## 🌐 Web UI
This project includes an optional **React**-based web interface for convenient control of the endpoints. 

To use it: **Open** `http://<raspberry-pi-ip>:8000/ui` in your browser.

<img src="./img/ui.jpg" alt="Web UI Interface" width="300">

## 🏠 Home Assistant Integration
Custom Home Assistant integration is available for easy integration to Home Assistant:
**https://github.com/anttitane/mitsubishi-ilp-ir-control-ha-integration**

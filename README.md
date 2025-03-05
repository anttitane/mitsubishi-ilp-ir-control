# Mitsubishi ILP IR Control

A FastAPI-based application for controlling Mitsubishi HVAC systems using IR signals via Raspberry Pi GPIO.

## 🚀 Features
- Control Mitsubishi HVAC using **FastAPI**
- Sends **IR signals** via Raspberry Pi GPIO
- Supports **cooling, heating, fan speed, and temperature settings**
- Works with **Raspberry Pi Zero W**

### Project background
- Code in IrSender folder has been copied (and slightly modified) from [Ericmas001](https://github.com/Ericmas001/HVAC-IR-Control)

## 🐜 Requirements
### Hardware
- **Raspberry Pi Zero W** (or other Raspberry Pi models)
- IR LED connected to GPIO
  - Examples for building a Raspberry Pi IR sender can be found [here](https://www.raspberry-pi-geek.com/Archive/2015/10/Raspberry-Pi-IR-remote)
- Mitsubishi HVAC unit

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

### 8️⃣ Run FastAPI App
```sh
uvicorn main:app --host 0.0.0.0 --port 8000
```
To deactivate the virtual environment:
```sh
deactivate
```

## 🔧 API Endpoints
### **Control Air Pump**
**POST /control_air_pump/**
#### Request Body (JSON):
```json
{
  "mode": "cooling",
  "temperature": 21,
  "fan_speed": "high"
}
```
#### Response:
```json
{
  "status": "Cooling command sent"
}
```

### **Test via cURL**
```sh
curl -X POST "http://localhost:8000/control_air_pump/" \
     -H "Content-Type: application/json" \
     -d '{"mode":"cooling", "temperature":21, "fan_speed":"high"}'
```

### **Test in Browser (Swagger UI)**
Go to **http://localhost:8000/docs**


# Mitsubishi ILP IR Control

A FastAPI-based application for controlling Mitsubishi HVAC systems using IR signals via Raspberry Pi GPIO.

## 🚀 Features
- Control Mitsubishi HVAC using **FastAPI**
- Sends **IR signals** via Raspberry Pi GPIO
- Supports **cooling, heating, fan speed, and temperature settings**
- Works with **Raspberry Pi Zero W**

### Project background
- Code in IrSender folder has been copied (and slightly modified) from [Ericmas001](https://github.com/Ericmas001/HVAC-IR-Control)

## 📜 Requirements
### Hardware
- **Raspberry Pi Zero W** (or other Raspberry Pi models)
- IR LED connected to GPIO
  - Examples for building a Raspberry Pi IR sender can be found [here](https://www.raspberry-pi-geek.com/Archive/2015/10/Raspberry-Pi-IR-remote)
- Mitsubishi HVAC unit

### Software
- **Raspberry Pi OS (Bookworm or Bullseye)**
- **Python 3.9+**
- **FastAPI, Uvicorn, and dependencies**

## ⚠️ Important Note About `pigpio`
When using `self.pigpio = ctypes.CDLL('/usr/lib/libpigpio.so')`, ensure that the `pigpiod` service is **not** running. You must **stop and disable** the service before running the app:
```sh
sudo systemctl stop pigpiod
sudo systemctl disable pigpiod
```

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
ExecStart=/usr/bin/sudo /home/pi/mitsubishi-ilp-ir-control/venv/bin/uvicorn main:app --host 0.0.0.0 --port 8000
WorkingDirectory=/home/pi/mitsubishi-ilp-ir-control
Environment="PATH=/home/pi/mitsubishi-ilp-ir-control/venv/bin"
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


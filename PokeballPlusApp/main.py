import asyncio
import sys
import math
from PyQt6.QtWidgets import (
    QApplication, QWidget, QPushButton, QTextEdit, QVBoxLayout, QLabel
)
from bleak import BleakClient, BleakScanner
from qasync import QEventLoop, asyncSlot

DEVICE_NAME = "Pokemon PBP"
BATTERY_LEVEL = 33
MANUFACTURER_NAME = 49
SOFTWARE_REVISION = 51
INPUT = 65

JOY_X_MIN = 7980
JOY_X_MAX = 49620
JOY_Y_MIN = 13350
JOY_Y_MAX = 50280

class PokeballApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Pokeball Plus GUI")
        self.resize(500, 400)

        self.log = QTextEdit(self)
        self.log.setReadOnly(True)
        self.start_button = QPushButton("Connect to Pokeball", self)
        self.start_button.clicked.connect(self.connect_to_device)

        layout = QVBoxLayout()
        layout.addWidget(QLabel("Pokeball Status Console:"))
        layout.addWidget(self.log)
        layout.addWidget(self.start_button)
        self.setLayout(layout)

    def log_message(self, text):
        self.log.append(text)

    @asyncSlot()
    async def connect_to_device(self):
        self.start_button.setEnabled(False)
        self.log_message("🔍 Scanning for devices...")
        device = await BleakScanner.find_device_by_name(DEVICE_NAME, timeout=30.0)
        if not device:
            self.log_message("❌ Pokeball not found. Make sure it's powered on.")
            self.start_button.setEnabled(True)
            return

        self.log_message(f"✅ Found device: {device.address}")
        async with BleakClient(device) as client:
            if not client.is_connected:
                self.log_message("❌ Failed to connect.")
                return

            self.log_message("🔗 Connected to Pokeball.")
            try:
                manufacturer = (await client.read_gatt_char(MANUFACTURER_NAME)).decode()
                software = (await client.read_gatt_char(SOFTWARE_REVISION)).decode()
                battery = int.from_bytes(await client.read_gatt_char(BATTERY_LEVEL), 'big')
            except Exception as e:
                self.log_message(f"⚠️ Error reading data: {e}")
                self.start_button.setEnabled(True)
                return

            self.log_message(f"🏷 Manufacturer: {manufacturer}")
            self.log_message(f"🔋 Battery Level: {battery}%")
            self.log_message(f"💾 Software Rev: {software}")

            await client.start_notify(INPUT, self.handle_input)
            self.log_message("📡 Listening to input data... Press Ctrl+C to stop.")

            try:
                while True:
                    await asyncio.sleep(1)
            except asyncio.CancelledError:
                await client.stop_notify(INPUT)
                self.log_message("🛑 Stopped listening.")
                self.start_button.setEnabled(True)

    def handle_input(self, sender, data):
        try:
            def toInt(b): return int.from_bytes(b, "big", signed=True)
            time = int.from_bytes(data[0:1], "big")
            buttons = int.from_bytes(data[1:2], "big")
            top_pressed = buttons & 1 != 0
            joy_pressed = buttons & 2 != 0

            joyX_raw = data[2:4].hex()
            joyX = joyX_raw[3] + joyX_raw[0] + joyX_raw[2] + joyX_raw[1]
            joyX = int(joyX, 16) - JOY_X_MIN
            joyX = joyX / (JOY_X_MAX - JOY_X_MIN)
            joyX = 2 * joyX - 1

            joyY = int.from_bytes(data[4:6], "big")
            joyY = joyY - JOY_Y_MIN
            joyY = joyY / (JOY_Y_MAX - JOY_Y_MIN)
            joyY = -2 * joyY + 1

            gyroX = toInt(data[6:8]) / 5600.0
            gyroY = toInt(data[8:10]) / 5600.0
            gyroZ = toInt(data[10:12]) / 5600.0
            gyroW = toInt(data[12:14]) / 32767.0

            accelX = toInt(data[-1:]) / 127.0
            accelY = toInt(data[-2:-1]) / 127.0
            accelZ = toInt(data[-3:-2]) / 127.0

            self.log_message(
                f"t:{time:3}, btn1:{top_pressed}, btn2:{joy_pressed}, "
                f"joy:({joyX:5.2f},{joyY:5.2f}), "
                f"gyro:({gyroX:6.2f},{gyroY:6.2f},{gyroZ:6.2f}) "
                f"acc:({accelX:5.2f},{accelY:5.2f},{accelZ:5.2f})"
            )
        except Exception as e:
            self.log_message(f"Error parsing input: {e}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    loop = QEventLoop(app)
    asyncio.set_event_loop(loop)

    window = PokeballApp()
    window.show()

    with loop:
        loop.run_forever()

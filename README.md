# micropython-airmonitor

This Air monitor system reads barometric data (temperature, pressure), air quality (eCO2, TVOC), and ambient light.

Configuration
microcontroller Lolin ESP32 S3-mini with various shields:
- barometric pressure shield (HP303B)
- ambient light sensor (BH1750)
- air quality SDGP30

displays
- TFT Ili7341, LATERON
- OLED SSD1306, 64*48 pixels   <-- basically TOO small

actuators: MAYBE

Additional shields:
- TFT & I2C connector shield - to connect I2C devices, IO-device and TFT-display
- Battery shield - to attach a Lipo battery

WORK IN PROGRESS
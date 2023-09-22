"""
main setup for Air Monitor

Configuration:
Lolin ESP32-S3 mini with sensors:
1. Barometric sensor: HP303B,   I2C address: 0x77 (0x76)
2. Ambien Light sensor: BH1750, I2C address: 0x23 (0x5C)
3. TVOC and eCO2 sensor: SGP30, I2C address: 0x58

SGP30:
TVOC: 0-60000 ppb
eCO2: 400-60000 ppm

HP303B:
Pressure: 300 -1200 hPa.
Temperature: -40 - 85 °C.

Lolin Shield I2C address table:
https://www.wemos.cc/en/latest/tutorials/others/lolin_shield_i2c_address_table.html

2023-0921 PP first setup
"""
import machine
import gc

# 2023-0922 PP first setup Air Monitor
try:
    import air_monitor
except KeyboardInterrupt:
    print("Done")

# cleanup
gc.collect()
print(f"Memory available: {gc.mem_free() // 1024} kB")

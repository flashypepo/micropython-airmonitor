"""
main setup for Environment Monitor

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
import micropython
micropython.alloc_emergency_exception_buf(100)

import machine
import gc

# 2023-0921 print I2C devices
#def print_i2cdevices(i2c):
#    print(f"I2C devices: {[hex(device) for device in i2c.scan()]}")

# test I2C
#i2c = machine.I2C(0)
#print_i2cdevices(i2c)

# demo SGP30 sensor
try:
    print("Demo SGP30 (air quality) shield...")
    import sgp30_adafruit_simpletest
    #import sgp30_test_safuya
except KeyboardInterrupt:
    print("Done")
    
# demo BH1750 sensor
try:
    print("Demo BH1750 ambient light shield...")
    import bh1750_test_octaprog7
    #import bh1750_test_pinkink
except KeyboardInterrupt:
    print("Done")

# demo dps310 sensor
try:
    print("Demo HP303B barometric Pressure shield...")
    import dps310_adafruit_advanced
    #import dps310_test_jposada202020
except KeyboardInterrupt:
    print("Done")

# demo TFT display
#TODO TFT ILI7341 demo

# cleanup
gc.collect()
print(f"Memory available: {gc.mem_free() // 1024} kB")

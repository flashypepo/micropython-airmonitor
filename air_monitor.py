"""
Air Monitor - monitors barometric pressure, air quality,
and ambient light, and present the data on a display.

Configuration:
Lolin ESP32 S3-mini
shields:
- barometric pressure shield (HP303B)
- ambient light sensor (BH1750)
- air quality SDGP30

displays:
- TFT Ili7341, ...
- OLED SSD1306, 64*48 pixels   <---- TOO small

actuators: MAYBE

Additional shields:
- TFT & I2C connector shield - to connect I2C devices, IO-device and TFT-display
- Battery shield - to attach a Lipo battery

2023-0922 PP first setup - synchronous version, console print, (small)OLED
"""
import machine
import time
# from micropython-lib
import datetime

# import sensor classes
from adafruit_sgp30 import Adafruit_SGP30
from adafruit_dps310.advanced import DPS310_Advanced as DPS310
# configuration parameters - not used in this example
#from adafruit_dps310.advanced import SampleCount, Rate, Mode

from octaprog7 import bh1750
from octaprog7.sensor_pack.bus_service import I2cAdapter

# import actuator classes
from ssd1306 import SSD1306_I2C

__VERSION__ = "0.0.1"

def title(display):
    print(f"Air Monitor... version {__VERSION__}")
    display.fill(0)
    display.text("Air", 0, 0, 1)
    display.text("Monitor", 0, 15, 1)
    display.text(__VERSION__, 0, 30, 1)
    display.show()

def show_message(display, txt, dt=1):
    msg = txt.split("\n")
    display.fill(0)
    y = 0
    for t in msg:
        display.text(t, 0, y, 1)
        y += 15
    display.show()
    time.sleep(dt)

        

# setup hardware I2C
#print("setup I2C...")
i2c = machine.I2C(0)


# ====================================
# setup display -> status program
# ====================================
# TODO: TFT-display

# OLED-shield, 64x48 pixels
WIDTH, HEIGTH = 64, 48   # Lolin OLED shield v2.0.0
display = SSD1306_I2C(WIDTH, HEIGTH, i2c) # default address 0x3C
# display title
title(display)

# ================
#     SETUP
# ================
devices = i2c.scan()
print(f"\tI2C devices: {[hex(device) for device in devices]}")

# setup HP303B barometric pressure sensor
print("setup barometric pressure shield...")
msg = "HP303B\nsensor\nsetup"
show_message(display, msg)
dps = DPS310(i2c)
time.sleep_ms(300)  # PP: wait sensor is ready
dps.sea_level_pressure = 1002.97 # A'dam, 2023-0922 20:30
print(f"\tsea level pressure: {dps.sea_level_pressure:.2f}HPa")


# setup BH1750 ambient light sensor
print("setup ambient light shield...")
msg = "BH1750\nsensor\nsetup"
show_message(display, msg)
adaptor = I2cAdapter(i2c)      # <-- maybe use globally
sol = bh1750.Bh1750(adaptor)
sol.power(on=True)     # Sensor Of Lux
sol.set_mode(continuously=True, high_resolution=True)
sol.measurement_accuracy = 1.0  # default value
old_lux = curr_max = 1.0

# setup SGP30 air quality sensor
print("setup air quality shield...")
msg = "SGP30\nsensor\nsetup"
show_message(display, msg)
sgp30 = Adafruit_SGP30(i2c)
#sgp_serial = "SGP30 serial #", [hex(i) for i in sgp30.serial]
#print(f"\t{sgp_serial}")
print(f"\tSGP30 serial #, {[hex(i) for i in sgp30.serial]}")
# Initialize SGP-30 internal drift compensation algorithm.
sgp30.iaq_init()
# Wait 15 seconds for the SGP30 to properly initialize
print("\tWaiting 15 seconds for SGP30 initialization.")
time.sleep(15)
# Retrieve previously stored baselines, if any (helps the compensation algorithm).
sgp_has_baseline = False
try:
    # open baseline files, if present
    f_co2 = open('co2eq_baseline.txt', 'r')
    f_tvoc = open('tvoc_baseline.txt', 'r')
    co2_baseline = int(f_co2.read())
    tvoc_baseline = int(f_tvoc.read())
    #Use them to calibrate the sensor
    sgp30.set_iaq_baseline(co2_baseline, tvoc_baseline)
    # close the files
    f_co2.close()
    f_tvoc.close()
    sgp_has_baseline = True
except:
    print('\tImpossible to read SGP30 baselines!')
#Store the time at which last baseline has been saved
sgp_baseline_time = time.time()

# Actuators
# future?

# ===================
#  MEASUREMENTS
# ===================
try:
    msg = "start\nsensor\ndata"
    show_message(display, msg)
    old_co2eq, old_tvoc = 300, -1
    old_temp, old_press = 100, 0

    while True:
        # get the current time
        lt = time.localtime()
        now = datetime.datetime(lt[0], lt[1], lt[2], lt[3], lt[4], lt[5])
        
        # Air Quality
        co2eq, tvoc = sgp30.iaq_measure()
        # Ambient light
        lux = sol.get_illumination()
        # barometric measurements
        temperature = dps.temperature
        pressure = dps.pressure
        altitude = dps.altitude
        
        # show sensor values - only when values are changed!

        # display air_quality(values) on console and display
        if co2eq != old_co2eq or tvoc != old_tvoc:
            print(f"{str(now)}: CO2Eq={str(co2eq)}ppm\tTVOC={str(tvoc)}ppb")
            msg = f"Air\n{co2eq} ppm\n{tvoc} ppb"
            show_message(display, msg)

        # display ambient(values) on console and display
        if lux != old_lux:
            curr_max = max(lux, curr_max)
            print(f"{str(now)}: Illumination={lux}lux.\tmax:{curr_max}.\tNormalized:{100*lux/curr_max}%.")
            old_lux = lux
            msg = f"Ambient\n{lux:.0f} lux\n{curr_max:.0f} max"
            show_message(display, msg)
        #time.sleep_ms(sol.get_conversion_cycle_time())

        # display barometric(values) on console and display
        if temperature != old_temp or pressure != old_press:
            print(f"{str(now)}: Temperature={temperature:.2f}°C\tPressure={pressure:.2f}HPa\tAltitude={altitude:.2f}m")
            old_temp, old_press = temperature, pressure
            msg = f"Barometr\n{temperature:.1f} *C\n{pressure:.0f}hPa"
            show_message(display, msg)

        # cleanup loop
        # SGP30 Baselines should be saved after 12 hour the first timen then every hour,
        # according to the doc.
        if (sgp_has_baseline and (time.time() - sgp_baseline_time >= 3600)) \
                or ((not sgp_has_baseline) and (time.time() - sgp_baseline_time >= 43200)):
            
            print(f"{str(now)}: saving baseline!")
            sgp_baseline_time = time.time()
            try:
                f_co2 = open('co2eq_baseline.txt', 'w')
                f_tvoc = open('tvoc_baseline.txt', 'w')
                bl_co2, bl_tvoc = sgp30.get_iaq_baseline()
                f_co2.write(str(bl_co2))
                f_tvoc.write(str(bl_tvoc))
                f_co2.close()
                f_tvoc.close()
                sgp_has_baseline = True
            except:
                print('Impossible to write SGP30 baselines!')

        #A measurement should be done every 60 seconds, according to the doc.
        time.sleep(1)

except KeyboardInterrupt:
    # clear display
    display.fill(0)
    display.show()
    #TODO: power off sensors

finally:
    print("Done")
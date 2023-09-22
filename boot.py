"""
This file is executed on every boot (including wake-boot from deepsleep)

"""
import micropython
micropython.alloc_emergency_exception_buf(100)

#import esp
#esp.osdebug(None)
#import webrepl
#webrepl.start()

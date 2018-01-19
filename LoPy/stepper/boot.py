# REPL duplication on UART0 for serial connection
from machine import UART
import os
usb = UART(0, 115200)
os.dupterm(usb)

# Disable heartbeat LED
from pycom import heartbeat
heartbeat(False)

# Disable WiFi radio
from pycom import wifi_on_boot
wifi_on_boot(False)

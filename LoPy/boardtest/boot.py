# REPL duplication on UART0 for serial connection
from machine import UART
import os
uart = UART(0, 115200)
os.dupterm(uart)

# Disable heartbeat LED
from pycom import heartbeat
heartbeat(False)

# Disable WiFi radio
from pycom import wifi_on_boot
wifi_on_boot(False)

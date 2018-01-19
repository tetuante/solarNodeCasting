# REPL duplication on UART0 for serial connection
from machine import UART
import os
uart = UART(0, 115200)
os.dupterm(uart)

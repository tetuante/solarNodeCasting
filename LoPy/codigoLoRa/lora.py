#LoRa connection
from network import LoRa
import socket
from utime import sleep
from binascii import unhexlify

# Initialize LoRa in LORAWAN mode.
lora = LoRa(mode=LoRa.LORAWAN)

# create an OTAA authentication parameters
app_eui = unhexlify('** ** ** ** ** ** ** **'.replace(' ',''))
app_key = unhexlify('** ** ** ** ** ** ** ** ** ** ** ** ** ** ** **'.replace(' ',''))

# create a LoRa socket
s = socket.socket(socket.AF_LORA, socket.SOCK_RAW)
# set the LoRaWAN data rate
s.setsockopt(socket.SOL_LORA, socket.SO_DR, 5)
s.setsockopt(socket.SOL_LORA, socket.SO_CONFIRMED, True)

def connect():
    # join a network using OTAA (Over the Air Activation)
    lora.join(activation=LoRa.OTAA, auth=(app_eui, app_key), timeout=0)

    # wait until the module has joined the network
    while not lora.has_joined():
        sleep(2.5)
        print('Not yet joined...')

    print('Joined!')

    # delete any queued messages in the gateway
    while sendReceive('0') != b'':
        sleep(1)
        print('Wiping queued messages...')

# Function to send messager to the LoRa gateway
def send(msg):
    # make the socket blocking
    # (waits for the data to be sent and for the 2 receive windows to expire)
    s.setblocking(True)
    # send the message
    s.send(msg)
    # make the socket non-blocking
    # (because if there's no data received it will block forever...)
    s.setblocking(False)

# Same as above but expecting a response from the gateway
def sendReceive(msg):
    send(msg)
    return s.recv(32) # Return the response

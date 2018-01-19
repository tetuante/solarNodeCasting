# WiFi connection, MQTT(SSL) and HTTPS GET request
from machine import idle
from network import WLAN
from umqtt import MQTTClient
from usocket import socket, getaddrinfo
from ussl import wrap_socket

# Store WiFi AP parameters
nets = {'casa': {'SSID': 'onessid', 'AUTH': (WLAN.WPA2, 'onekey')},\
        'lab':  {'SSID': 'anotherssid',           'AUTH': (WLAN.WPA2, 'anotherkey')}}

wlan = WLAN(mode=WLAN.STA, antenna=WLAN.INT_ANT, power_save=True)

def connect(net):
    # Connect to WiFi network
    wlan.connect(nets[net]['SSID'], auth=nets[net]['AUTH'], timeout=5000)
    while not wlan.isconnected():
        idle() # save power while waiting
    print('Connected to ' + nets[net]['SSID'] + '!')

client = MQTTClient('nodoSolar', 'mqtt.thingspeak.com', ssl=True)

# Send data to MQTT channel
def sendMQTT(msg):
    client.connect()
    client.publish('channels/281569/publish/GSUF8ZCW1D0RO0MB', msg)
    client.disconnect()

# Send HTTPS GET request to the given URL
def https_get(url):
    _, _, host, path = url.split('/', 3)
    addr = getaddrinfo(host, 443)[0][-1]
    s = socket()
    ss = wrap_socket(s)
    ss.connect(addr)
    ss.send(bytes('GET /%s HTTP/1.0\r\nHost: %s\r\n\r\n' % (path, host), 'utf8'))
    response = ''
    while True:
        data = ss.recv(100)
        if data:
            response += data.decode('UTF-8')
        else:
            break
    ss.close()
    return response

'''
Script de pruebas para receptores GPS basados en ublox7 (ABANDONADO)
'''

from machine import UART
from struct import *
from ubinascii import *
from ubx7 import *

uart1 = UART(1, baudrate=9600, bits=8, parity=None, stop=1)

def read(record='RMC'):
    nmea_records = ['GGA', 'GLL', 'GSA', 'GSV', 'RMC', 'VTG']
    if record not in nmea_records:
        print('Invalid NMEA record.')
        print('Valid NMEA records are:', end=' ')
        print(nmea_records)
        return
    record = b'$GP' + record
    rn = b'\r\n'
    start = 0
    end = 0
    lines = b''
    uart1.readall()
    while True:
        lines += readallwhenany()
        if record in lines:
            start = lines.find(record)
            lines = lines[start:]
            while rn not in lines:
                lines += readallwhenany()
            end = lines.find(rn)
            return lines[:end]

def track(record='RMC'):
    while True:
        print(read(record).decode())

def readall():
    uart1.readall()
    while True:
        print(readallwhenany().decode(), end='')

def rwCFG(msg_id='00', msg_payload=''):
    '''
    Poll or set a CFG (0x06) parameter, used to configure the receiver or to read the
    current configuration.

    Every message sent to the receiver is acknowledged with an ACK-ACK (0x05 0x01)
    message or rejected with an ACK-NAK (0x05 0x02) message.
    '''
    return sendReceive(msg_class='06', msg_id=msg_id, msg_payload=msg_payload)

def sendReceive(msg_class, msg_id, msg_payload=''):
    '''
    #########
    REVISAR GESTION DE RESPUESTA DE MENSAJES NO CFG
    #########

    Send a message to the receiver and wait for the response if any.
    '''
    response = None

    msg = compose_msg(msg_class, msg_id, msg_payload)

    if msg_class == '06':
        ack_ack, ack_nak = compose_ack(msg_id)
        ack = None
        valid = None

    uart1.readall()

    uart1.write(msg)

    response = readallwhenany()

    while b'\xb5b' not in response:
        if len(response) > 4096:
            del response
            raise NameError('Timeout :(')
        response += readallwhenany()

    response = response[response.find(b'\xb5b'):]

    '''
    Wait for ACK-ACK or ACK-NAK if we are sending a CFG message.
    '''
    if msg_class == '06':
        while not ack:
            if len(response) > 4096:
                del response
                raise NameError('Timeout :(')
            response += readallwhenany()
            if ack_ack in response:
                ack = ack_ack
            elif ack_nak in response:
                ack = ack_nak
        response = response[response.find(b'\xb5b'):response.find(ack)]
        if response:
            valid = checksum(response[2:-2]) == response[-2:]
            response = (str(hexlify(response[:2], ' '))[2:-1],
                        str(hexlify(response[2:4], ' '))[2:-1],
                        unpack('<H', response[4:6])[0],
                        str(hexlify(response[6:-2], ' '))[2:-1],
                        str(hexlify(response[-2:], ' '))[2:-1])
        else:
            response = None
        return {'RESPONSE': response, 'ACK': bool(ack[3]), 'VALID': valid}
    else:
        '''
        METODO CHAPUCERO. REVISAR.
        '''
        while b'$' not in response:
            if len(response) > 4096:
                del response
                raise NameError('Timeout :(')
            response += readallwhenany()
        return str(hexlify(response[:response.find(b'$')],' '))[2:-1]

def compose_msg(msg_class, msg_id, msg_payload):
    '''
    Compose a message for a given class, id and payload
    '''
    msg = None

    msg_sync = b'\xb5b' # Packet's header

    msg_class = unhexlify(msg_class) # Message class
    msg_id = unhexlify(msg_id) # Message ID
    msg_payload = unhexlify(msg_payload.replace(' ','')) # Message payload
    msg_length = pack('<H', len(msg_payload)) # Message length (unsigned short, little-endian)
    msg_checksum = checksum(msg_class + msg_id + msg_length + msg_payload) # Message checksum

    msg =  msg_sync + msg_class + msg_id + msg_length + msg_payload + msg_checksum # Message

    return msg

def compose_ack(msg_id):
    '''
    Compose ACK and NAK messages for a given message id of the CFG (0x06) class.
    '''
    ack_ack = None
    ack_nak = None

    msg_sync = b'\xb5b' # Packet's header
    msg_class = b'\x06'
    msg_id = unhexlify(msg_id) # Message ID

    ack_class = b'\x05'
    ack_ack_id = b'\x01'
    ack_nak_id = b'\x00'

    ack_length = b'\x02\x00'

    ack_ack_body = ack_class + ack_ack_id + ack_length + msg_class + msg_id
    ack_nak_body = ack_class + ack_nak_id + ack_length + msg_class + msg_id

    ack_ack_checksum = checksum(ack_ack_body)
    ack_nak_checksum = checksum(ack_nak_body)

    ack_ack = msg_sync + ack_ack_body + ack_ack_checksum
    ack_nak = msg_sync + ack_nak_body + ack_nak_checksum

    return ack_ack, ack_nak

def checksum(buff):
    '''
    Checksum calculation
    '''
    try:
        buff = unhexlify(buff.replace(' ',''))
    except:
        pass

    CK_A = 0
    CK_B = 0

    for i in range(len(buff)):
        CK_A = (CK_A + buff[i]) & 0xff
        CK_B = (CK_B + CK_A) & 0xff

    return pack('BB', CK_A, CK_B)

def readallwhenany():
    '''
    Wait until there's something to read and then read everything
    '''
    while not uart1.any():
        pass
    return uart1.readall()

def CFG_MSG(msg_class='f0', rate=''):
    '''
    CFG-MSG (0x06 0x01). Configure message rate for all I/O ports. Send an empty
    rate to get the current cofiguration of all ports.
    '''
    if msg_class == 'f0':
        # msg_ids = ['0a', '09', '00', '01', '43', '42', '0d', '40', '06', '02', '07', '03', '04', '41', '05', '08']
        # msg_ids = ['0a', '09', '00', '01', '0d', '06', '02', '07', '03', '04', '05', '08']
        msg_ids = ['00', '01', '02', '03', '04', '05']
    elif msg_class == 'f1':
        # msg_ids = ['41', '00', '40', '03', '04']
        msg_ids = ['00', '03', '04']
    else:
        print('Invalid msg_class. Use \'f0\' for NMEA and  \'f1\' for PUBX.')
        return

    for msg_id in msg_ids:
        print(msg_class + ' ' + msg_id + ': ', end='')
        print(rwCFG('01', msg_class + msg_id + rate * 6))

def CFG_NAV5(payload=''):
    '''
    CFG-NAV5 (0x06 0x24). Configure navigation engine. Send an empty
    payload to get the current cofiguration.

    Default values:

    default_payload = 'ff ff 00 03 00 00 00 00 10 27 00 00 05 00 fa 00 fa 00 64 00 2c 01 00 3c 00 00 00 00 00 00 00 00 00 00 00 00'

    mask = 'ff ff'
    dynModel = '00'
    fixMode = '03'
    fixedAlt = '00 00 00 00'
    fixedAltVar = '10 27 00 00'
    minElev = '05'
    drLimit = '00'
    pDop = 'fa 00'
    tDop = 'fa 00'
    pAcc = '64 00'
    tAcc = '2c 01'
    staticHoldThresh = '00'
    dgpsTimeOut = '3c'
    cnoThreshNumSVs = '00'
    cnoThresh = '00'
    reserved2 = '00 00'
    reserved3 = '00 00 00 00'
    reserver4 = '00 00 00 00'
    '''

    return rwCFG('24', payload)

def CFG_PM2(payload=''):
    '''
    CFG-NAV5 (0x06 0x3B). Configure power management. Send an empty
    payload to get the current cofiguration.

    Default values:

    default_payload = '01 06 00 00 00 90 02 00 e8 03 00 00 10 27 00 00 00 00 00 00 00 00 00 00 2c 01 00 00 4f c1 03 00 86 02 00 00 fe 00 00 00 64 40 01 00'

    version = '01'
    reserved1 = '06'
    reserved2 = '00'
    reserved3 = '00'
    flags = '00 90 02 00'
    updatePeriod = 'e8 03 00 00'
    searchPeriod = '10 27 00 00'
    gridOffset = '00 00 00 00'
    onTime = '00 00'
    minAcqTime = '00 00'
    reserver4 = '2c 01'
    reserver5 = '00 00'
    reserver6 = '4f c1 03 00'
    reserver7 = '86 02 00 00'
    reserver8 = 'fe'
    reserver9 = '00'
    reserver10 = '00 00'
    reserver11 = '64 40 01 00'
    '''

    return rwCFG('3b', payload)

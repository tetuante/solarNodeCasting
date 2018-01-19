from machine import UART
from ubx7 import *
from struct import unpack

uart = UART(1)

ubx = ubx7(uart) # UBX7 device declaration
cmd = ubx7msg() # commands to be sent to the ubx device
res = ubx7msg() # responses to be received from the ubx device
ack = ubx7msg() # ack (or nak) to be received from the ubx device

'''
This functions serve as examples of how to use the classes defined in ubx7.py
'''

def setgnss():
    '''
    CFG-GNSS
    - Disable GLONASS blocks
    '''
    print('Setting CFG.GNSS... ', end='')
    res, ack = ubx.sendrecv(CFG.GNSS)
    nBlocks = (len(res.PAYLOAD) - 4)//8
    data = res.unpackpl('u1u1u1' + 'u1u1u1u1x4'*nBlocks)
    data2 = {}
    for N in range(nBlocks):
        if data[4 + 8*N] == 6:
            data2[8 + 8*N] = [0, 'x4']
            print('GLONASS block found!')
    cmd = ubx7msg.packpl(ubx, CFG.GNSS, data2)
    ack, = ubx.sendrecvcmd(cmd)
    print('ACK: {} Valid: {}'.format(ack.CLASSID, ack.isvalid()))

def setnav5():
    '''
    CFG-NAV5 Settings:
    - dynModel: Stationary
    - staticThresh: 10 cm/s
    '''
    print('Setting CFG.NAV5... ', end='')
    cmd = ubx7msg.packpl(ubx, CFG.NAV5, {2: [2, 'u1'], 22: [10, 'u1']})
    ack, = ubx.sendrecvcmd(cmd)
    print('ACK: {} Valid: {}'.format(ack.CLASSID, ack.isvalid()))

def setpm2():
    '''
    CFG-PM2 Settings:
    - updatePeriod: 0
    - On/Off operation
    '''
    print('Setting CFG.PM2... ', end='')
    cmd = ubx7msg.packpl(ubx, CFG.PM2, {4: [36864, 'u4'], 8: [0, 'u4']}) ###!!! valor data[4]
    ack, = ubx.sendrecvcmd(cmd)
    print('ACK: {} Valid: {}'.format(ack.CLASSID, ack.isvalid()))

def setrxm():
    '''
    CFG-RXM Settings:
    - lpMode: 1 (Power Save Mode)
    '''
    print('Setting CFG.RXM... ', end='')
    cmd = ubx7msg.packpl(ubx, CFG.RXM, {1: [1, 'u1']})
    ack, = ubx.sendrecvcmd(cmd)
    print('ACK: {} Valid: {}'.format(ack.CLASSID, ack.isvalid()))

def getdata():
    res, = ubx.sendrecv(NAV.PVT)

    data = res.unpackpl('u4u2u1u1u1u1u1x1u4i4u1x1u1u1i4i4i4i4u4u4i4i4i4i4i4u4u4u2x2u4')

    printval(data[0], 'iTOW', 'ms')
    printval(data[4], 'year')
    printval(data[6], 'month')
    printval(data[7], 'day')
    printval(data[8], 'hour')
    printval(data[9], 'min')
    printval(data[10], 'sec')
    printval(data[11], 'valid')
    printval(data[12], 'tAcc', 'ns')
    printval(data[16], 'nano', 'ns')
    printval(data[20], 'fixType')
    printval(data[21], 'flags')
    printval(data[22], 'reserved1')
    printval(data[23], 'numSV')
    printval(data[24], 'lon', 'deg', 1e-7)
    printval(data[28], 'lat', 'deg', 1e-7)
    printval(data[32], 'height', 'm', 1e-3)
    printval(data[36], 'hMSL', 'm', 1e-3)
    printval(data[40], 'hAcc', 'm', 1e-3)
    printval(data[44], 'vAcc', 'm', 1e-3)
    printval(data[48], 'velN', 'cm/s', 10)
    printval(data[52], 'velE', 'cm/s', 10)
    printval(data[56], 'velD', 'cm/s', 10)
    printval(data[60], 'gSpeed', 'cm/s', 10)
    printval(data[64], 'heading', 'deg', 1e-5)
    printval(data[68], 'sAcc', 'cm/s', 10)
    printval(data[72], 'headingAcc', 'deg', 1e-5)
    printval(data[76], 'pDOP', 'deg', 0.01)
    printval(data[78], 'reserved2')
    printval(data[80], 'reserved3')

def printval(val, name, units='', scaling=1):
    print('{}: {} {}'.format(name, val*scaling, units))

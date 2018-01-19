from struct import pack, unpack
from ubinascii import hexlify, unhexlify

'''
ACK, CFG, NAV and RXM classes store the values of msgCLASS and msgID of several
ublox messages
'''
class ACK:
    CLASS = b'\x05'
    LENGTH = 10

    ACK = b'\x05\x01'
    NAK = b'\x05\x00'

class CFG:
    CLASS = b'\x06'

    ANT = b'\x06\x13'
    CFG = b'\x06\x09'
    DAT = b'\x06\x06'
    GNSS = b'\x06\x3e'
    INF = b'\x06\x02'
    ITFM = b'\x06\x39'
    LOG = b'\x06\x47'
    MSG = b'\x06\x01'
    NAV5 = b'\x06\x24'
    NAVX5 = b'\x06\x23'
    NMEA = b'\x06\x17'
    NVS = b'\x06\x22'
    PM2 = b'\x06\x3b'
    PRT = b'\x06\x00'
    RATE = b'\x06\x08'
    RINV = b'\x06\x34'
    RST = b'\x06\x04'
    RXM = b'\x06\x11'
    SBAS = b'\x06\x16'
    TP5 = b'\x06\x31'
    USB = b'\x06\x1b'

class NAV:
    CLASS = b'\x01'

    AOPSTATUS = b'\x01\x60'
    CLOCK = b'\x01\x22'
    DGPS = b'\x01\x31'
    DOP = b'\x01\x04'
    POSECEF = b'\x01\x01'
    POSLLH = b'\x01\x02'
    PVT = b'\x01\x07'
    SBAS = b'\x01\x32'
    SOL = b'\x01\x06'
    STATUS = b'\x01\x03'
    SVINFO = b'\x01\x30'
    TIMEGPS = b'\x01\x20'
    TIMEUTC = b'\x01\x21'
    VELECEF = b'\x01\x11'
    VELNED = b'\x01\x12'

class RXM:
    CLASS = b'\x02'

    ALM = b'\x02\x30'
    EPH = b'\x02\x31'
    PMREQ = b'\x02\x41'
    RAW = b'\x02\x10'
    SFRB = b'\x02\x11'
    SVSI = b'\x02\x20'

'''
This class includes methods to store, create and decode ublox messages
'''
class ubx7msg:

    HEADER = b'\xb5b'
    minmsgsize = 8

    def __init__(self, msg_classid=bytes(2), msg_payload=bytes(0)):
        self.CLASSID, self.PAYLOAD = string2bytes(msg_classid, msg_payload)
        self.LENGTH = pack('<H', len(self.PAYLOAD))
        self.CKSUM = self.checksum()

        self.LENGTHINT = len(self.PAYLOAD)
        self.WANTSACK = bool()

    def clear(self):
        self.CLASSID = bytes(2)
        self.PAYLOAD = bytes(0)
        self.LENGTH = bytes(2)
        self.CKSUM = bytes(2)

        self.LENGTHINT = len(self.PAYLOAD)
        self.WANTSACK = bool()

    def set(self, msg_classid, msg_payload=b''):
        self.CLASSID, self.PAYLOAD = string2bytes(msg_classid, msg_payload)

        self.LENGTH = pack('<H', len(self.PAYLOAD))
        self.CKSUM = self.checksum()

        self.LENGTHINT = len(self.PAYLOAD)
        self.WANTSACK = self.CLASSID.startswith(CFG.CLASS)

    def setfromraw(self, buff):
        if not buff.startswith(ubx7msg.HEADER) and len(buff) < ubx7msg.minmsgsize:
            raise NameError('ubx7msg.setfromraw(): Invalid message.')

        self.CLASSID = buff[2:4]
        self.LENGTH = buff[4:6]
        self.PAYLOAD = buff[6:-2]
        self.CKSUM = buff[-2:]

        self.LENGTHINT = len(self.PAYLOAD)
        self.WANTSACK = self.CLASSID.startswith(CFG.CLASS)

    def rawmsg(self):
        return ubx7msg.HEADER + self.CLASSID + self.LENGTH + self.PAYLOAD + self.CKSUM

    def printmsg(self):
        print('')

        print('HEADER')
        print(bytes2string(ubx7msg.HEADER)[0], end='\n\n')

        print('CLASSID')
        print(bytes2string(self.CLASSID)[0], end='\n\n')

        print('LENGTH')
        print(len(self.PAYLOAD), end='\n\n')

        print('PAYLOAD')
        print(bytes2string(self.PAYLOAD)[0], end='\n\n')

        print('CHECKSUM')
        print(bytes2string(self.CKSUM)[0], end='\n\n')

    def checksum(self):
        '''
        Checksum calculation
        '''
        msg_body = self.CLASSID + self.LENGTH + self.PAYLOAD
        CK_A = 0
        CK_B = 0

        for i in range(len(msg_body)):
            CK_A = (CK_A + msg_body[i]) & 0xff
            CK_B = (CK_B + CK_A) & 0xff

        return pack('BB', CK_A, CK_B)

    def isvalid(self):
        return (self.checksum() == self.CKSUM)

    def unpackpl(self, fmt):
        data = {}
        types = ()
        if type(fmt) is not str:
            raise NameError('unpackpl(fmt): Invalid format')

        fmt = fmt.lower()
        t = ''

        for s in fmt:
            if s.isalpha():
                t += s
            elif s.isdigit():
                types = types + (t + s,)
                t = ''
            else:
                raise NameError('unpackpl: wrong format')

        byteoffset = 0

        for _type in types:
            length = int(_type[-1])
            if _type.startswith('ch'):
                data[byteoffset] = self.PAYLOAD[byteoffset:byteoffset+length].decode().replace('\x00', '')
            else:
                data[byteoffset] = unpack(ubx7msg.ubx2python(_type), self.PAYLOAD[byteoffset:byteoffset+length])[-1]
            byteoffset += length

        return data

    @staticmethod
    def packpl(ubx, msg_classid, data):
        if type(ubx) is not ubx7:
            raise NameError('packpl(): Invalid ubx')
        if not msg_classid.startswith(CFG.CLASS):
            raise NameError('packpl(): Invalid classid')
        if type(data) is not dict:
            raise NameError('packpl(): Invalid data {byteoffset: [val, fmt]}')

        prevconf, ack, = ubx.sendrecv(msg_classid)

        payload = b''
        byteoffset = 0

        while byteoffset < len(prevconf.PAYLOAD):
            if byteoffset in data:
                value = pack(ubx7msg.ubx2python(data[byteoffset][1]), data[byteoffset][0])
                payload += value
                byteoffset += len(value)
            else:
                payload += pack('B', prevconf.PAYLOAD[byteoffset])
                byteoffset += 1

        return ubx7msg(msg_classid, payload)

    @staticmethod
    def ubx2python(fmt):
        if fmt == 'u1':
            fmt = '<B'
        elif fmt == 'u2':
            fmt = '<H'
        elif fmt == 'u4':
            fmt = '<L'
        elif fmt == 'i1':
            fmt = '<b'
        elif fmt == 'i2':
            fmt = '<h'
        elif fmt == 'i4':
            fmt = '<l'
        elif fmt == 'x1':
            fmt = '<B'
        elif fmt == 'x2':
            fmt = '<H'
        elif fmt == 'x4':
            fmt = '<L'
        elif fmt == 'r4':
            fmt = '<f'
        elif fmt == 'r8':
            fmt = '<f'
            print('WARNING: double precision is not supported!')
        else:
            raise NameError('Wrong UBX7 type')

        return fmt

'''
This class includes methods to communicate with the ubox receiver
'''
class ubx7:
    def __init__(self, uart, baudrate=9600, bits=8, parity=None, stop=1, pins=('G24', 'G11')):
        self.uart = uart
        self.uart.init(baudrate, bits, parity, stop, pins=pins)
        self.buffsize = 1024

        self.command = ubx7msg()
        self.response = ubx7msg()
        self.ack = ubx7msg()

    def sendrecvcmd(self, obj):
        self.sendcmd(obj)
        return self.recv()

    def sendcmd(self, obj):
        if isinstance(obj, ubx7msg):
            self.clearall()
            self.command = obj
            self.uart.readall()
            return self.uart.write(self.command.rawmsg())
        return None

    def sendrecv(self, msg_classid, msg_payload=b''):
        self.send(msg_classid, msg_payload)
        return self.recv()

    def recv(self):
        response = self.readallwhenany()

        while ubx7msg.HEADER not in response:
            if len(response) > self.buffsize:
                del response
                raise NameError('Missing header in response')
            response += self.readallwhenany()
        response = response[response.find(ubx7msg.HEADER):]

        while len(response) < ubx7msg.minmsgsize:
            if len(response) > self.buffsize:
                del response
                raise NameError('Timeout :(')
            response += self.readallwhenany()

        reslen = unpack('<H', response[4:6])[0] + ubx7msg.minmsgsize

        if self.command.WANTSACK:
            reslen = reslen + ACK.LENGTH # We expect an ack (+ response)

        while len(response) < reslen:
            if len(response) > self.buffsize:
                del response
                raise NameError('Timeout :(')
            response += self.readallwhenany()

        response = response[:reslen]

        if len(response.split(ubx7msg.HEADER)) > 2:
            self.response.setfromraw(response[:-ACK.LENGTH])
            self.ack.setfromraw(response[-ACK.LENGTH:])
            if self.response.isvalid() and self.ack.isvalid():
                return self.response, self.ack
        elif self.command.WANTSACK:
            self.ack.setfromraw(response[:ACK.LENGTH])
            if self.ack.isvalid():
                return self.ack,
        else:
            self.response.setfromraw(response)
            if self.response.isvalid():
                return self.response,

        raise NameError('Invalid results')

    def send(self, msg_classid, msg_payload=b''):
        self.clearall()
        self.command.set(msg_classid, msg_payload)
        self.uart.readall()
        return self.uart.write(self.command.rawmsg())

    def clearall(self):
        self.command.clear()
        self.response.clear()
        self.ack.clear()

    def readallwhenany(self):
        '''
        Wait until there's something to read and then read as much as possible
        '''
        while not self.uart.any():
            pass
        return self.uart.readall()

def string2bytes(*args):
    cargs = ()
    for arg in args:
        if type(arg) is not bytes:
            try:
                if arg:
                    arg = unhexlify(arg.replace(' ', ''))
                else:
                    arg = b''
            except:
                print('string2bytes: Unable to convert args')
                return
        cargs = cargs + (arg,)

    return cargs

def bytes2string(*args):
    cargs = ()
    for arg in args:
        if type(arg) is not str:
            try:
                if arg:
                    arg = str(hexlify(arg, ' '))[2:-1]
                else:
                    arg = ''
            except:
                print('bytes2string: Unable to convert args')
                return
        cargs = cargs + (arg,)

    return cargs

'''
ABANDONADO
'''

from machine import UART
from struct import *
from ubinascii import *

class ubx7(UART):

    def sendReceive(self, msg_class, msg_id, msg_payload=''):
        '''
        #########
        REVISAR GESTION DE RESPUESTA DE MENSAJES NO CFG
        #########

        Send a message to the receiver and wait for the response if any.
        '''
        response = None

        msg = self.__composemsg(msg_class, msg_id, msg_payload)

        if msg_class == '06':
            ack_ack, ack_nak = self.__composeack(msg_id)
            ack = None
            valid = None

        self.readall()

        self.write(msg)

        response = self.__readallwhenany()

        while b'\xb5b' not in response:
            if len(response) > 4096:
                del response
                raise NameError('Timeout :(')
            response += self.__readallwhenany()

        response = response[response.find(b'\xb5b'):]

        '''
        Wait for ACK-ACK or ACK-NAK if we are sending a CFG message.
        '''
        if msg_class == '06':
            while not ack:
                if len(response) > 4096:
                    del response
                    raise NameError('Timeout :(')
                response += self.__readallwhenany()
                if ack_ack in response:
                    ack = ack_ack
                elif ack_nak in response:
                    ack = ack_nak
            response = response[response.find(b'\xb5b'):response.find(ack)]
            if response:
                valid = self.__checksum(response[2:-2]) == response[-2:]
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
                response += self.__readallwhenany()
            return str(hexlify(response[:response.find(b'$')],' '))[2:-1]

    def __composemsg(self, msg_class, msg_id, msg_payload):
        '''
        Compose a message for a given class, id and payload
        '''
        msg = None

        msg_sync = b'\xb5b' # Packet's header

        msg_class = unhexlify(msg_class) # Message class
        msg_id = unhexlify(msg_id) # Message ID
        msg_payload = unhexlify(msg_payload.replace(' ','')) # Message payload
        msg_length = pack('<H', len(msg_payload)) # Message length (unsigned short, little-endian)
        msg_checksum = self.__checksum(msg_class + msg_id + msg_length + msg_payload) # Message checksum

        msg =  msg_sync + msg_class + msg_id + msg_length + msg_payload + msg_checksum # Message

        return msg

    def __composeack(self, msg_id):
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

        ack_ack_checksum = self.__checksum(ack_ack_body)
        ack_nak_checksum = self.__checksum(ack_nak_body)

        ack_ack = msg_sync + ack_ack_body + ack_ack_checksum
        ack_nak = msg_sync + ack_nak_body + ack_nak_checksum

        return ack_ack, ack_nak

    def __checksum(self, buff):
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

    def __readallwhenany(self):
        '''
        Wait until there's something to read and then read everything
        '''
        while not self.any():
            pass
        return self.readall()

import binascii
import struct
from bluepy import btle


class EmoPlus:
    
    def __init__(self, addr):
        self.conn = btle.Peripheral(addr)
        self.battery_ch = self.conn.getCharacteristics(uuid=btle.UUID('00002a19-0000-1000-8000-00805f9b34fb'))[0]
        self.value_ch = self.conn.getCharacteristics(uuid=btle.UUID(0xfff2))[0]
        self.cmd_ch = self.conn.getCharacteristics(uuid=btle.UUID(0xfff3))[0]
        
    def disconnect(self):
        self.conn.disconnect()
        
    def get_battery_level(self):
        if self.battery_ch.supportsRead():
            value = self.battery_ch.read()
            return struct.unpack('B', value)[0]
            
    def warm_up(self):
        value = self.cmd_ch.read()
        
            
    def get_haze_value(self):
        
        if self.value_ch.supportsRead():
            value = self.value_ch.read()
            print('value=%s' % binascii.b2a_hex(value))
    
            c1 = bytes(value[10:12])
            c2 = bytes(value[12:14])
            print('c1=%s, c2=%s' % (binascii.b2a_hex(c1), binascii.b2a_hex(c2)))
            
            a = struct.unpack('B', c1[1:])[0]
            b = struct.unpack('B', c1[:1])[0]
            density = int((b << 8) | (a & 0xff)) * 1.265

            a = struct.unpack('B', c2[1:])[0]
            b = struct.unpack('B', c2[:1])[0]
            count = (int((a & 0xff) << 0) + int((b & 0xff) << 8)) * 2.56
            if count < 0:
                count = 0

            print('%d ug/m3, %d 0.3um' % (density, count))
            return count, density

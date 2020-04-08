import binascii
import struct
from bluepy import btle


class EmoPlus:

    service_battery_uuid = "0000180f-0000-1000-8000-00805f9b34fb"
    service_pm2dot5_uuid = "0000fff0-0000-1000-8000-00805f9b34fb"
    
    def __init__(self, addr):
        self.addr = addr
        self.conn = btle.Peripheral()
        self.connected = False
        
    def connect(self):
        try:
            self.conn.connect(self.addr)
            self.connected = True

            self.service_battery = self.conn.getServiceByUUID(self.service_battery_uuid)
            self.service_pm2dot5 = self.conn.getServiceByUUID(self.service_pm2dot5_uuid)
        except btle.BTLEException as e:
            raise RuntimeError(e)
        
    def disconnect(self):
        self.conn.disconnect()
        self.connected = False
        
    def get_battery_level(self):
        try:
            battery_ch = self.service_battery.getCharacteristics(forUUID='00002a19-0000-1000-8000-00805f9b34fb')[0]
            value = battery_ch.read()
            return struct.unpack('B', value)[0]
        except btle.BTLEException as e:
            raise RuntimeError(e)
            
    def warm_up(self):
        try:
            cmd_ch = self.service_pm2dot5.getCharacteristics(forUUID='0000fff3-0000-1000-8000-00805f9b34fb')[0]
            value = cmd_ch.read()
        except btle.BTLEException as e:
            raise RuntimeError(e)

    def get_haze_value(self):
        
        try:
            value_ch = self.service_pm2dot5.getCharacteristics(forUUID='0000fff2-0000-1000-8000-00805f9b34fb')[0]
            
            value = value_ch.read()
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
        
        except btle.BTLEException as e:
            raise RuntimeError(e)

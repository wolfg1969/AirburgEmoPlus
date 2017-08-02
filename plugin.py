#           Airburg Emo Plus Plugin
#
#           Author:     wolfg1969, 2017
#
"""
<plugin key="AirburgEmoPlus" name="Airburg Emo Plus" author="wolfg1969" version="1.0.0" externallink="http://www.airburg.cn/jianceyi.html">
    <params>
        <param field="Address" label="Mac Address" width="150px" required="true"/>
        <param field="Mode1" label="Polling interval (minutes, 30 mini)" width="40px" required="true" default="30"/>
        <param field="Mode6" label="Debug" width="75px">
            <options>
                <option label="True" value="Debug"/>
                <option label="False" value="Normal"  default="true" />
            </options>
        </param>
    </params>
</plugin>
"""
import Domoticz
from datetime import datetime, timedelta
from emo_plus import EmoPlus

icons = {
    "airburgemoplusbatterylevelfull": "batterylevelfull icons.zip",
    "airburgemoplusbatterylevelok": "batterylevelok icons.zip",
    "airburgemoplusbatterylevellow": "batterylevellow icons.zip",
    "airburgemoplusbatterylevelempty": "batterylevelempty icons.zip",
    "airburgemoplusblue": "emoblue icons.zip",
    "airburgemoplusgreen": "emogreen icons.zip",
    "airburgemoyellow": "emoyellow icons.zip",
    "airburgemoorange": "emoorange icons.zip",
    "airburgemored": "emored icons.zip",
    "airburgemopurple": "emopurple icons.zip",
    "airburgemoblack": "emoblack icons.zip"
}

class EmoPlusPlugin:
    
    def __init__(self):
        
        self.debug = False
        
        self.emoDevice = None
        
        self.nextupdate = datetime.now()
        self.warmupcounter = 0
        self.startwarmup = False
        
        self.pollinterval = 30  # default polling interval in minutes

    def onStart(self):
        
        if Parameters["Mode6"] == "Debug":
            self.debug = True
            Domoticz.Debugging(1)
        else:
            Domoticz.Debugging(0)
            
        # load custom battery images
        Domoticz.Debug('icons=%s,Images=%s' % (icons, Images))
        for key, value in icons.items():
            if key not in Images:
                Domoticz.Image(Filename=value).Create()
                Domoticz.Debug("Added icon: " + key + " from file " + value)
            Domoticz.Debug('Images=%s' % Images.keys())
        Domoticz.Debug("Number of icons loaded = " + str(len(Images)))
        for image in Images:
            Domoticz.Debug("Icon " + str(Images[image].ID) + " " + Images[image].Name)
            
        # check polling interval parameter
        try:
            temp = int(Parameters["Mode1"])
        except:
            Domoticz.Error("Invalid polling interval parameter")
        else:
            if temp < 30:
                temp = 30  # minimum polling interval
                Domoticz.Error("Specified polling interval too short: changed to 30 minutes")
            elif temp > 1440:
                temp = 1440  # maximum polling interval is 1 day
                Domoticz.Error("Specified polling interval too long: changed to 1440 minutes (24 hours)")
            self.pollinterval = temp
        Domoticz.Log("Using polling interval of {} minutes".format(str(self.pollinterval)))
            
        if (len(Devices) == 0):
            Domoticz.Device(Name="PM2.5 Count", Unit=1, TypeName="Custom").Create()
            Domoticz.Device(Name="PM2.5 Density", Unit=2, TypeName="Custom", Options={"Custom": "1; ug/m3"}).Create()
            Domoticz.Device(Name="Battery Level", Unit=3, TypeName="Custom", Options={"Custom": "1;%"}).Create()
            Domoticz.Log("Devices created.")
            
        DumpConfigToLog()
        Domoticz.Log("Plugin is started.")

    def onStop(self):
        Domoticz.Log("Plugin is stopping.")
        Domoticz.Debugging(0)

    def onHeartbeat(self):
        now = datetime.now()
        
        if now >= self.nextupdate:
            self.nextupdate = now + timedelta(minutes=self.pollinterval)
            self.startwarmup = True
            
            self.warmUp()
            self.getBatteryLevel()
            
        if self.startwarmup:
            self.warmupcounter += 1
            
        if self.warmupcounter > 3:  # 3 * default heartbeat = 30 sec
        
            self.startwarmup = False
            self.warmupcounter = 0
            
            self.readValue()
            
                
    def warmUp(self):
        Domoticz.Log('warmUp')
        
        try:
            if self.emoDevice is None:
                self.emoDevice = EmoPlus(Parameters["Address"])
            
            self.emoDevice.connect()
            self.emoDevice.warm_up()
            
        except btle.BTLEException as err:
            Domoticz.Log('error when warming up Emo Plus %s (error: %s)' % (Parameters["Address"], str(err)))
            emo = None
            
        return True
        
    def getBatteryLevel(self):
        
        Domoticz.Log('getBatteryLevel')
        
        if 3 in Devices and self.emoDevice is not None and self.emoDevice.connected:
            
            levelBatt = self.emoDevice.get_battery_level()
            if levelBatt >= 75:
                icon = "airburgemoplusbatterylevelfull"
            elif levelBatt >= 50:
                icon = "airburgemoplusbatterylevelok"
            elif levelBatt >= 25:
                icon = "airburgemoplusbatterylevellow"
            else:
                icon = "airburgemoplusbatterylevelempty"
                
            Domoticz.Debug('icon=%s,Images=%s' % (icon, Images))
            
            try:
                if icon in Images:
                    Devices[3].Update(nValue=0, sValue=str(levelBatt), Image=Images[icon].ID)
                else:
                    Domoticz.Debug("icon not found: %s in %s" % (icon, Images))
                    Devices[3].Update(nValue=0, sValue=str(levelBatt))
            except:
                Domoticz.Error("Failed to update device unit " + str(3))
        
    def readValue(self):
        
        Domoticz.Log('read value')
        
        if self.emoDevice is not None and self.emoDevice.connected:
            try:
                (count, density) = self.emoDevice.get_haze_value()
                
                if density >= 0 and density < 36:
                    icon = "airburgemoplusblue"
                elif density >= 36 and density < 76:
                    icon = "airburgemoplusgreen"
                elif density >= 76 and density < 116:
                    icon = "airburgemoplusyellow"
                elif density >=116 and density < 151:
                    icon = "airburgemoplusorange" 
                elif density >=151 and density < 251:
                    icon = "airburgemoplusred"   
                elif density >=251 and density < 351:
                    icon = "airburgemopluspurple"
                else:
                    icon = "airburgemoplusblack"
                    
                Domoticz.Debug('icon=%s,Images=%s' % (icon, Images))
                
                Domoticz.Log('count = %d' % count)
                if 1 in Devices:
                    if icon in Images:
                        Devices[1].Update(nValue=0, sValue='%d' % count, Image=Images[icon].ID)
                    else:
                        Domoticz.Debug("icon not found: %s in %s" % (icon, Images))
                        Devices[1].Update(nValue=0, sValue='%d' % count)
            
                Domoticz.Log('density = %d' % density)
                if 2 in Devices:
                    if icon in Images:
                        Devices[2].Update(nValue=0, sValue='%d' % density, Image=Images[icon].ID)
                    else:
                        Domoticz.Debug("icon not found: %s in %s" % (icon, Images))
                        Devices[2].Update(nValue=0, sValue='%d' % density)
                
            finally:
                self.emoDevice.disconnect()


global _plugin
_plugin = EmoPlusPlugin()

def onStart():
    global _plugin
    _plugin.onStart()

def onStop():
    global _plugin
    _plugin.onStop()

def onHeartbeat():
    global _plugin
    _plugin.onHeartbeat()

# Generic helper functions
def DumpConfigToLog():
    for x in Parameters:
        if Parameters[x] != "":
            Domoticz.Debug( "'" + x + "':'" + str(Parameters[x]) + "'")
    Domoticz.Debug("Device count: " + str(len(Devices)))
    for x in Devices:
        Domoticz.Debug("Device:           " + str(x) + " - " + str(Devices[x]))
        Domoticz.Debug("Device ID:       '" + str(Devices[x].ID) + "'")
        Domoticz.Debug("Device Name:     '" + Devices[x].Name + "'")
        Domoticz.Debug("Device nValue:    " + str(Devices[x].nValue))
        Domoticz.Debug("Device sValue:   '" + Devices[x].sValue + "'")
        Domoticz.Debug("Device LastLevel: " + str(Devices[x].LastLevel))
    return

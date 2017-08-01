# AirburgEmoPlus
Domoticz plugin to read pm2.5 values from Airburg emo plus.

## Installation (Raspberry Pi)

* Clone this repository
```
$ cd domoticz/plugins
$ git clone https://github.com/wolfg1969/AirburgEmoPlus.git
```
* Install bluepy
```
$ cd domoticz/plugins/AirburgEmoPlus/
$ git clone https://github.com/IanHarvey/bluepy.git bluepy-src
$ cd bluepy-src
$ python3 setup.py build
$ python3 setup.py install --prefix=./bluepy
$ cp -R ./bluepy/lib/python3.4/site-packages/bluepy ../
```
* Restart domoticz server
```
$ sudo service domoticz restart
```

Battery Level device logic is borrowed from https://www.domoticz.com/wiki/Plugins/BatteryLevel.html

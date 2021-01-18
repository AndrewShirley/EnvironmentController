import IconBar
import Config
import time
#from umqtt.simple import MQTTClient
import ubinascii
import machine
import micropython
import network
import esp
import json
import bme280
import ssd1306
import MQTTDispatcher
import RelayModule
import EnvironmentController
import TextObject
import ImagesAndFonts.font10
import ImagesAndFonts.font
import sys,uselect
import Webserver


spoll=uselect.poll()
spoll.register(sys.stdin,uselect.POLLIN)

def ReadOneChrFromSTDIN():
    # This is a NON-BLOCKING check for characeters on the incoming stream. Returns None if nothing is available
    return(sys.stdin.read(1) if spoll.poll(0) else None)

MyConfig = Config.Config()

#print(MyConfig.Parameters["Environment"]["TargetTemperature"])

EC = EnvironmentController.Controller()

def SetUpEnvironmentController():
  EC.TargetTemperature = MyConfig.Parameters["Environment"]["TargetTemperature"]
  EC.MaximumTemperature=MyConfig.Parameters["Environment"]["MaximumTemperature"]
  EC.MinimumTemperature=MyConfig.Parameters["Environment"]["MinimumTemperature"]

  EC.TargetHumidity = MyConfig.Parameters["Environment"]["TargetHumidity"]
  EC.MaximumHumidity = MyConfig.Parameters["Environment"]["MaximumHumidity"]
  EC.MinimumHumidity = MyConfig.Parameters["Environment"]["MinimumHumidity"]

# GPIO_Relay_1_Pin = 16
# GPIO_Relay_2_Pin = 17
# GPIO_Relay_3_Pin = 18
# GPIO_Relay_4_Pin = 19

# OLED_SCLPin = MyConfig.Parameters["Oled"]["SCLPin"]
# OLED_SDAPin = MyConfig.Parameters["Oled"]["SDAPin"]
OLED_Width = MyConfig.Parameters["Oled"]["Width"]
OLED_Height = MyConfig.Parameters["Oled"]["Height"]

# BME_SCLPin = 22
# BME_SDAPin = 21

Wifi_SSID = MyConfig.Parameters["Wifi"]["SSID"]
Wifi_Password = MyConfig.Parameters["Wifi"]["Password"]
Wifi_Station = None
Message_Interval = 10       # seconds between status reports

MQTT_Server = MyConfig.Parameters["MQTT"]["Server"]
MQTT_ClientID = MyConfig.Parameters["MQTT"]["ClientID"]
MQTT_SubscribeTopic = MyConfig.Parameters["MQTT"]["SubscribeTopic"]
MQTT_PublishTopic = MyConfig.Parameters["MQTT"]["PublishTopic"]
MQTT_Dispatcher = MQTTDispatcher.MQTTDispatcher("PlugController",MQTT_SubscribeTopic)   # Fill in the details later


RM = RelayModule.RelayModule()
EC.RelayModule = RM
RM.AddRelay("Fan", MyConfig.Parameters["RelayModule"]["Relay_1_Pin"])
RM.AddRelay("Humidifier", MyConfig.Parameters["RelayModule"]["Relay_4_Pin"])
RM.Value(1)   # Sends 1 to ALL relays

'''
OLED_SCLPin = MyConfig.Parameters["Oled"]["SCLPin"]
OLED_SDAPin = MyConfig.Parameters["Oled"]["SDAPin"]
OLED_Width = MyConfig.Parameters["Oled"]["Width"]
OLED_Height = MyConfig.Parameters["Oled"]["Height"]
'''

print("SCL,SDA=",MyConfig.Parameters["BME280"]["SCLPin"],MyConfig.Parameters["BME280"]["SDAPin"])


OLED_I2C_Obj = machine.I2C(scl= machine.Pin(MyConfig.Parameters["Oled"]["SCLPin"]), sda=machine.Pin(MyConfig.Parameters["Oled"]["SDAPin"]))
BME_I2C = machine.I2C(scl=machine.Pin(MyConfig.Parameters["BME280"]["SCLPin"]), sda=machine.Pin(MyConfig.Parameters["BME280"]["SDAPin"]))

EC.BME280 = bme280.BME280(i2c=BME_I2C)
Oled_Obj = ssd1306.SSD1306_I2C(OLED_Width, OLED_Height, OLED_I2C_Obj)

I1 = IconBar.Icon("ImagesAndFonts/link-broken.pbm",True,2,"MQTTIcon")
I2 = IconBar.Icon("ImagesAndFonts/wi-fi.pbm",True,2,"WifiIcon")

IB = IconBar.IconBar(False, I1, I2)
IB.X = 0
IB.Y = 48
#IB.Icons[0].FlashesPerSecond = 1
#IB.Icons[1].FlashesPerSecond = 1

TextObj_IPAddr = TextObject.TextObject(38, 48, 1, "No Wifi", ImagesAndFonts.font10, 90, 16)
TextObj_HiTemp = TextObject.TextObject(2, 5, 1, "27", ImagesAndFonts.font, 30, 16)
TextObj_LoTemp = TextObject.TextObject(2, 25, 1, "18", ImagesAndFonts.font, 30, 16)

Last_WifiConnectionCheck = False
AwaitingWifiConnection = True
SentWifiConnect = False


def WebserverCallback(RequestObj, ResponseObj):
  WebServerObj.Parameters["Message"] = ""

  if RequestObj.PageName() == "index.html":
    MyConfig.Parameters["Environment"]["MaximumTemperature"] = RequestObj.GetQueryValue("HiTemp", MyConfig.Parameters["Environment"]["MaximumTemperature"])
    MyConfig.Parameters["Environment"]["MinimumTemperature"] = RequestObj.GetQueryValue("LowTemp", MyConfig.Parameters["Environment"]["MinimumTemperature"])
    MyConfig.Parameters["Environment"]["MaximumHumidity"] = RequestObj.GetQueryValue("HiHum", MyConfig.Parameters["Environment"]["MaximumHumidity"])
    MyConfig.Parameters["Environment"]["MinimumHumidity"] = RequestObj.GetQueryValue("LowHum", MyConfig.Parameters["Environment"]["MinimumHumidity"])

    MyConfig.Parameters["Environment"]["TargetTemperature"] = int(MyConfig.Parameters["Environment"]["MaximumTemperature"]) + int(MyConfig.Parameters["Environment"]["MinimumTemperature"]) / 2
    MyConfig.Parameters["Environment"]["TargetHumidity"] = int(MyConfig.Parameters["Environment"]["MaximumHumidity"]) + int(MyConfig.Parameters["Environment"]["MinimumHumidity"]) / 2

    MyConfig.Save()

    WebServerObj.Parameters["HiTemp"] = MyConfig.Parameters["Environment"]["MaximumTemperature"]
    WebServerObj.Parameters["LowTemp"] = MyConfig.Parameters["Environment"]["MinimumTemperature"]
    WebServerObj.Parameters["HiHum"] = MyConfig.Parameters["Environment"]["MaximumHumidity"]
    WebServerObj.Parameters["LowHum"] = MyConfig.Parameters["Environment"]["MinimumHumidity"]

    if int(RequestObj.GetQueryValue("HiTemp",-1)) > -1 :
      WebServerObj.Parameters["Message"] = "New Parameters Saved"

    SetUpEnvironmentController()


WebServerObj  = Webserver.WebServer(WebserverCallback) # Starts the web server


'''
HiTemp 35
LowTemp 15
HiHum 75
LoHum 10
'''


def NetworkConnect():
  ''' Attempts to keep Wifi up '''

  global Wifi_Station, Last_WifiConnectionCheck, AwaitingWifiConnection, SentWifiConnect

  if Wifi_Station is None:
    print("Connecting to Wifi...")
    Wifi_Station = network.WLAN(network.STA_IF)

    IB.GetIcon("WifiIcon").FlashesPerSecond = 1
    AwaitingWifiConnection = True
    Last_WifiConnectionCheck = False
    SentWifiConnect = False

  if AwaitingWifiConnection:
    if not SentWifiConnect:
      SentWifiConnect = True
      Wifi_Station.active(True)
      Wifi_Station.connect(Wifi_SSID, Wifi_Password)

    if Wifi_Station.isconnected():
      Last_WifiConnectionCheck = True
      AwaitingWifiConnection = False
      IB.GetIcon("WifiIcon").FlashesPerSecond = 0
      TextObj_IPAddr.Text = str(Wifi_Station.ifconfig()[0])
      #TextObj_IPAddr.JustifyHorizontalCentre()

      print("WIFI is Connected")


def MQTTConnected(MQTTDispObj):
  ''' Called by the MQTT_Dispatcher when an MQTT server has been connected '''
  IB.GetIcon("MQTTIcon").FlashesPerSecond = 0
  print("MQTT is Connected")


Oled_Obj.fill(0)
Oled_Obj.show()
IB.Draw(Oled_Obj.framebuf)


NetworkConnect()
time.sleep(1)
MQTT_Dispatcher.MQTTBrokerConnectedCB = MQTTConnected
MQTT_Dispatcher.ConnectAndSubscribe()


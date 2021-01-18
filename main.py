

import gc
import time
#import bme280
#import ssd1306
import socket
#import machine
import json
import boot2
 

# Valid Commands:
# Relay_1_On, Relay_1_Off to Relay_4_On / Off
# Status, Report
# SetHumidityHigh, SetHumidityLow, SetTemperatureLow, SetTemperatureHigh. Use json Value=


# These commands disable environmental controls from using these relays. For example, to purge the air
# from the veg room, you Override Relay_1 (exhaust fan) and turn it on using an mqtt command.
# All the commands still work for the relays, its just not touched by the environmental controls.
# Relay_1_Override_On, Relay_1_Override_Off, Relay_2_Override_On etc

def SendStatus():
  MyDict = dict()
  MyDict["Relay_1"] = 1 - boot2.EC.RelayModule.GetRelay("Fan").Value()
  MyDict["Relay_2"] = 0
  MyDict["Relay_3"] = 0
  MyDict["Relay_4"] = 1 - boot2.EC.RelayModule.GetRelay("Humidifier").Value()
  MyDict["temperature"] = _Temperature
  MyDict["humidity"] = _Humidity
  MyDict["pressure"] = _Pressure
  MyDict["IP"] =  boot2.Wifi_Station.ifconfig()[0]
  MyDict["Relay_1_Override"] = boot2.EC.RelayModule.GetRelay("Fan").Paused
  MyDict["Relay_2_Override"] = False
  MyDict["Relay_3_Override"] = False
  MyDict["Relay_4_Override"] = boot2.EC.RelayModule.GetRelay("Humidifier").Paused
  
  boot2.MQTT_Dispatcher.Publish(boot2.MQTT_PublishTopic, json.dumps(MyDict))


def __MQTT_Callback(Topic, Msg):
  MsgDecoded = Msg + ""

  try:
    MyDict = json.loads(MsgDecoded)  # encode object to JSON
  except:
    print("Error in the JSON command:\n", MsgDecoded)
    return

  # Use the get() method to prevent crash with direct index method ["indexname"]. Doesn't exist then it crashes
  Command = MyDict.get("Command")

  if Command == "Relay_1_On":
    boot2.EC.RelayModule.GetRelay("Fan").GPIO_Relay_1.off()
    SendStatus()
'''
  elif Command == "Relay_1_Off":
  elif Command == "Relay_1_Override_On":
  elif Command == "Relay_1_Override_Off":
  elif Command == "Relay_2_On":
  elif Command == "Relay_2_Off":
  elif Command == "Relay_2_Override_On":
  elif Command == "Relay_2_Override_Off":
  elif Command == "Relay_3_On":
  elif Command == "Relay_3_Off":
  elif Command == "Relay_3_Override_On":
  elif Command == "Relay_3_Override_Off":
  elif Command == "Relay_4_On":
  elif Command == "Relay_4_Off":
  elif Command == "Relay_4_Override_On":
  elif Command == "Relay_4_Override_Off":
  elif Command == "Status" or Command == "Report":
  elif Command == "Reboot" or Command == "Restart":
    machine.reset()
  elif Command == "SetHumidityHigh":
    MaximumHumidity = float(MyDict["Value"])
  elif Command == "SetHumidityLow":
  elif Command == "SetTemperatureHigh":
  elif Command == "SetTemperatureLow":
  elif Command == "SetConfig":
'''



import pbm
import TextObject
import ImagesAndFonts.freesans20
import ImagesAndFonts.font
import ImagesAndFonts.font10

#import Animation_Explode
#A = Animation_Explode.Explode(12,25,52,35,boot2.Oled_Obj.framebuf)
#A.Gravity = 0.08
#A.CentreX=20
#A.CentreY=30

#A.CentreX = 0

# A2 = Animation_Explode.Explode(94,20,128,40,boot2.Oled_Obj.framebuf)
# A2.CentreX = 128

TO1 = TextObject.TextObject(0,20,1,"--",ImagesAndFonts.freesans20,64,20)
TO2 = TextObject.TextObject(64,20,1, "--",ImagesAndFonts.freesans20, 64,20)
TO1_2 = TextObject.TextObject(0,10,1,"Temp",None,64,20)
TO2_2 = TextObject.TextObject(64,10,1, "Hum",None, 64,20)
TO1_2.JustifyHorizontalCentre()
TO2_2.JustifyHorizontalCentre()

def PrintOLEDStatus():
#  print("OLED STATUS")
  TO1.Text = "{:>2.1f}C".format(_Temperature)
  TO2.Text = "{:>2.0f}%".format(_Humidity)

  #boot2.Oled_Obj.framebuf.fill_rect(0, 0, 128, 16, 0)

  TO1.JustifyHorizontalCentre()
  TO2.JustifyHorizontalCentre()

  TO1.Draw(boot2.Oled_Obj.framebuf)
  TO2.Draw(boot2.Oled_Obj.framebuf)
  TO1_2.Draw(boot2.Oled_Obj.framebuf)
  TO2_2.Draw(boot2.Oled_Obj.framebuf)

  boot2.WebServerObj.Parameters["Temperature"] = str(_Temperature)
  boot2.WebServerObj.Parameters["Humidity"] = str(_Humidity)


NextMessage = 0
_Temperature, _Humidity, _Pressure = boot2.EC.GetTempHumidity()

print("Running")


nTimes = 0
 
while True:
  try:
    boot2.NetworkConnect()
    boot2.MQTT_Dispatcher.ConnectAndSubscribe()

    NeedsDraw = False

    #print(time.ticks_ms() - NextMessage)    

    if time.ticks_ms() >= NextMessage:
      #print(" IN: FreeMem:", gc.mem_free())
      print(".")
      nTimes += 1
      NextMessage = time.ticks_ms() + boot2.Message_Interval * 1000
      _Temperature, _Humidity, _Pressure = boot2.EC.GetTempHumidity()
      boot2.WebServerObj.Temperature = _Temperature
      boot2.WebServerObj.Humidity = _Humidity

      SendStatus() 

      #A.Go()


      
      NeedsDraw = True
      #print("OUT: FreeMem:", gc.mem_free())

    if boot2.IB.NeedsDrawing() or NeedsDraw or boot2.TextObj_IPAddr.NeedsDrawing:
      #print("OLED UPDATE START: FreeMem:", gc.mem_free())

      boot2.Oled_Obj.fill(0) 
      #print("Draw.2")
      PrintOLEDStatus()
      #print("Draw.3")
      boot2.IB.Draw(boot2.Oled_Obj.framebuf)
      #print("Draw.4")
      boot2.TextObj_IPAddr.Draw(boot2.Oled_Obj.framebuf)
      #print("Draw.5")
      boot2.TextObj_HiTemp.Draw(boot2.Oled_Obj.framebuf)
      #print("Draw.6")
      boot2.TextObj_LoTemp.Draw(boot2.Oled_Obj.framebuf)
      #print("Draw.7")
 
      #A.Draw(boot2.Oled_Obj.framebuf)
      #print("Draw.8")
      #SC.Draw(boot2.Oled_Obj.framebuf)
      #print("Draw.9")
      boot2.Oled_Obj.show()
      #print("OLED UPDATE  DONE: FreeMem:", gc.mem_free())

  # Keep things going
  except (KeyboardInterrupt, OSError) as e:
      import AndrewsTimer
      AndrewsTimer.DeInitMasterTimer()
      print(e)
      break

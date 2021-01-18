import time
import Scripts.lib.Hysteresis
import AndrewsTimer

class Controller:
    def __init__(self):
        self.MaximumTemperature = 32
        self.MinimumTemperature = 18
        self.TargetTemperature = 22

        self.TargetHumidity = 55
        self.MaximumHumidity = 57
        self.MinimumHumidity = 53

        self.BME280 = None
        self.RelayModule = None

        self.Timer =  AndrewsTimer.Timer(1000, self.HandleCB, "ECTimer")

        self.LastReadingTime = 0
        self.LastTemp = 0
        self.LastHumidity = 0

        self.Temperature_Hysteresis = Scripts.lib.Hysteresis.Hysteresis(self.MaximumTemperature, self.MinimumTemperature, self.TargetTemperature, self.TargetTemperature)
        self.Humidity_Hysteresis = Scripts.lib.Hysteresis.Hysteresis(self.MaximumHumidity, self.MinimumHumidity, self.TargetTemperature, self.TargetHumidity)


    def Temperature(self):
        if not self.BME280 is None:
            T, P, H = self.BME_Obj.read_compensated_data()
            return T / 100

    def Humidity(self):
        if not self.BME280 is None:
            T, P, H = self.BME280.read_compensated_data()
            return H / 1000

    def GetTempHumidity(self):
        if not self.BME280 is None:
            T, P, H = self.BME280.read_compensated_data()
            return T / 100, H / 1000, P / 1000


    def HandleCB(self,TimerObj):
        ''' Called once a second '''
        #print("EC Controller CB")

        T, H, P = self.GetTempHumidity()
        self.Temperature_Hysteresis.AddNewValue(T)
        self.Humidity_Hysteresis.AddNewValue(T)

        

import machine

class Relay:
    def __init__(self, GPIO_PinNumber=0, UseInverseLogic=True, Hysteresis=None, Paused=False):
        self.GPIO_PinNumber = GPIO_PinNumber
        self.InverseLogic = UseInverseLogic
        self.GPIO_PinObj = machine.Pin(self.GPIO_PinNumber, machine.Pin.OUT)
        self.Paused = False

    def TurnOn(self):
        if not self.Paused:
            if self.InverseLogic:
                self.GPIO_PinObj.off()
            else:
                self.GPIO_PinObj.on()

    def TurnOff(self):
        if not self.Paused:
            if self.InverseLogic:
                self.GPIO_PinObj.on()
            else:
                self.GPIO_PinObj.off()

    def Value(self, NewValue=-99):
        if NewValue != -99:
            self.GPIO_PinObj.value(NewValue)
            return

        return self.GPIO_PinObj.value()

    def Toggle(self):
        self.Value(1-self.Value())


class RelayModule:
    GPIO_Objs={}

    def __init__(self):
        pass

    def AddRelay(self, RelayName, GPIO_PinNumber):
        RelayObj = Relay(GPIO_PinNumber)
        self.GPIO_Objs[RelayName] = RelayObj

    def Value(self, NewValue = 1):
        ''' Sets the value on all relays to the same given value '''        
        for Key in self.GPIO_Objs:
            self.GPIO_Objs[Key].Value(NewValue)

    def GetRelay(self, RelayName):
        return self.GPIO_Objs[RelayName]




#### TESTING

# r=Relay(13)

# r.TurnOn()
# print("On",r.Value())

# r.TurnOff()
# print("Off",r.Value())

# r.Value(0)
# print("On",r.Value())

# r.Value(1)
# print("Off", r.Value())

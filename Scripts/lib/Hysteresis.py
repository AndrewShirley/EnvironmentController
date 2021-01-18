'''
Allows you to monitor a value while determining if its withing a valid range.  Outputs a command to
RAISE, LOWER or DO NOTHING to the value.


Lower Range          Value        Upper Range               DO NOTHING
Value          Lower Range        Upper Range               RAISE
Lower Range    Upper Range        Value                     LOWER

Hysteresis:

If the value goes out of range, the resulting command will be RAISE or LOWER.
As the value comes back into range, the resulting Command will switch to DO NOTHING. 
In order for that to happen, the value will need to be well within the range so that it doesn't immediately go back
out of range.  So, there are two values to help with keeping the Value with the range as much as possible:

LowerApproachRTN                Lower Approach Return To Normal
UpperApproachRTN                Upper Approach Return To Normal

Example:
Value goes below the lower range bounds and results in the command RAISE
Hosting software gets the message, turns on the humidifier, value begins to return to normal.
The Command remains RAISE until the value crosses the LowerApproachRTN value, at which point, there's a return to DO NOTHING


'''


class Hysteresis:
    Command = "DO NOTHING"

    CurrentValue = -1

    UpperMax = 100
    UpperApproachRTN = 60    
    
    LowerMin = 0
    LowerApproachRTN = 40

    Pause = False

    def __init__(self, UpperMax = 100, LowerMin = 0, UpperApproachRTN = 60, LowerApproachRTN = 40):
        self.UpperMax = UpperMax
        self.UpperApproachRTN = UpperApproachRTN
        self.LowerMin = LowerMin
        self.LowerApproachRTN = LowerApproachRTN


    def AddNewValue(self, NewValue):
        if self.Pause: return

        self.CurrentValue = NewValue

        if self.Command == "DO NOTHING":
            if NewValue < self.LowerMin:
                self.Command = "RAISE"
            elif NewValue > self.UpperMax:
                self.Command = "LOWER"
        elif self.Command == "LOWER":
            if NewValue <= self.UpperApproachRTN:
                self.Command = "DO NOTHING"
        elif self.Command == "RAISE":
            if NewValue >= self.LowerApproachRTN:
                self.Command = "DO NOTHING"



# Testing: Uncomment the following
'''
h = Hysteresis(100,50,70,80)    # Range is 50-100, LowerApproach=80 and UpperApproach=70

v=[75,76,77,100,101,102,103,99,98,71,70,69,75,76,77,51,50,49,48,49,50,51,52,79,80,81]
for n in v:
    h.AddNewValue(n)
    print(h.CurrentValue, h.Command)

'''


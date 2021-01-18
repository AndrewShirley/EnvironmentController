'''

Andrew's Timer is a one-shot or recurring timer with mili-second precision.

It was originally developed for use on an ESP32 and Micropython.  It can easily be adapted to any hardware.

Each timer instantiated under Micropython looks and acts like a Timer in any other language.  Behind the scenes, each
timer object uses the same master clock, there-by allowing unlimited Timers using only one hardware timer.


Example Code:
import AndrewsTimer

def TimerCB(TimerOBJ):
  print(TimerOBJ.__Name__,"CB Called ", time.ticks_ms())

Timer1 = AndrewsTimer.Timer(500,TimerCB)

at timer expiry, TimerCallBackFunction is called with the AndrewsTimer.Timer object


Notes:
- During a Timer callback, if code crashes, that timer is disabled and the program is allowed to continue along with the
  other timers still running





'''

import sys

import time
#import AndrewsTimer
import machine

def DeInitMasterTimer():
    ''' Shortcut method to release the timer '''
    t = Timer()
    t.ReleaseTimer(t)


class Timer:

    @classmethod
    def ReleaseTimer(cls,self):
        Timer.MasterTimer.deinit()
        Timer.MasterTimer = None


    @classmethod
    def ClassInit(cls,self):
        ''' Ensures MasterTimer and Timers[] is created, exactly once '''
        import sys

        if "AndrewsTimer" in sys.modules:
            M = sys.modules["AndrewsTimer"]

            if not M is None:
                if hasattr(M,"MasterTimer"):
                    cls.MasterTimer = M.MasterTimer
                    cls.Timers = M.Timers

        if not hasattr(cls,"MasterTimer"):
            #print("Creating Master Timer")
            cls.Timers = []
            cls.MasterTimer = machine.Timer(1)
            cls.MasterTimer.init(period=1, mode=machine.Timer.PERIODIC,callback=Timer.HandleTimerCB)

    def __init__(self, PeriodmS=100, CallBack=None, Name="", OneShot = False, Paused=False):
        self.Duration = PeriodmS             # 100 mS (5 frames per-second)
        self.Paused = False
        self.CallBack = CallBack
        self.OneShot = OneShot
        self.NextExpiry = time.ticks_ms() + PeriodmS                 # time.ticks_ms
        if Name == "":
            self.__Name__ = "Timer_" + str(len(Timer.Timers))
        else:
            self.__Name__ = Name
        Timer.ClassInit(self)
        Timer.Timers.append(self)


    def HandleTimerExpired(self):
        if not self.CallBack is None:
            self.CallBack(self)

        if not self.OneShot:        # Retrigger the timer if its not a single event.
            if self.NextExpiry < 0: # Coming off pause?
                self.NextExpiry = time.time_ms() + self.Duration
            else:
                self.NextExpiry += self.Duration        # Alternatively, time.time_ms() + self.Duration, but this should keep the timer more steady
        else:
            self.Pause()

    def Start(self):
        ''' Starts the timer. For OneShot, causes another OneShot trigger '''
        self.NextExpiry = time.ticks_ms() + self.Duration
        self.Paused = False

    def Pause(self):
        self.NextExpiry = -1
        self.Paused = True

    def Deinit(self):
        self.Pause()
        Timer.Timers.remove(self)

    def deinit(self):
        self.Deinit()

    @classmethod
    def HandleTimerCB(cls,TimerObj):
        CurrentTimer = time.ticks_ms()

        for T in Timer.Timers:
            NextExpiry = T.NextExpiry
            if NextExpiry > -1 and CurrentTimer >= NextExpiry:
                try:
                    T.HandleTimerExpired()
                except Exception as Ex:
                    print("Timer Function Failed:")
                    sys.print_exception(Ex)
                    print("Disabling Timer")
                    T.Deinit()


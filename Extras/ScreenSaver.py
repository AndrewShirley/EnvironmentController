import AndrewsTimer
import time
import gc

class ScreenSaver:
    def __init__(self):
        self.Visible = False
        self.NeedsDrawing = False
        self.TimerObj = AndrewsTimer.Timer(100,self.TimerCB)
        self.LastFrame = time.ticks_ms()
        self.ThisFrame = self.LastFrame
        self.FrameDelta = 0
        self.Points=[]      # List of Lists: [0]=X [1]=Y [2]=StepX [3]=StepY
        self.Gravity = 0.01

    def AddPoint(self, X, Y, StepX = 0, StepY = 0.1):
        self.Points.append([X,Y,StepX,StepY])

    def AdvancePoints(self):
        for P in self.Points:
            P[0] += P[2]
            P[1] += P[3]
            P[3] += self.Gravity        


    def TimerCB(self, TimerObj):
        self.LastFrame  = self.ThisFrame
        self.ThisFrame = time.ticks_ms()
        self.FrameDelta = self.ThisFrame - self.LastFrame
        if not self.Visible:
            return
        self.AdvancePoints()
        self.NeedsDrawing = True
        #print("NeedsDeawing=",self.NeedsDrawing)

    def Draw(self, Framebuf):
        if not self.Visible:
            #print("Skipping Draw")
            self.NeedsDrawing = False
            return

        #print("-ScreenSaverDraw-",end='')
        for P in self.Points:
            Framebuf.pixel(int(P[0]),int(P[1]),1)

        self.NeedsDrawing = False

    def Start(self, Framebuf):
        self.GeneratePoints(Framebuf)
        self.LastFrame = time.ticks_ms()
        self.ThisFrame = self.LastFrame
        self.FrameDelta = 0
        self.Visible = True
        self.NeedsDrawing = True

    def Pause(self):
        self.Visible = False

    def GeneratePoints(self, Framebuf):
        print("Generating Screen Saver Points")
        self.Points.clear()
        gc.collect()
        Done = False
        
        for y in range(0, 64):
            if Done: break
            for x in range(0, 128):
                IncX = (x - 64) / 8
                IncY = 2

                if Framebuf.pixel(x, y)  == 1:
                    self.AddPoint(x,y,IncX,IncY)
                    #print("P",x,y, end=' ')
                    if len(self.Points) > 199:
                        Done = True
                        break
        
        print("Done Generating Screen Saver Points - ", len(self.Points))






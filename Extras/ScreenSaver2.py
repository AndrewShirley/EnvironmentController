'''
    Screensaver to simulate gravity.
'''



import AndrewsTimer
import time
import gc

class ScreenSaver2:
    def __init__(self):
        self.Visible = False
        self.NeedsDrawing = False
        self.TimerObj = AndrewsTimer.Timer(100,self.TimerCB)
        self.LastFrame = time.ticks_ms()
        self.ThisFrame = self.LastFrame
        self.FrameDelta = 0
        self.nFrames = 0
        self.DisplacementX = 0
        self.DisplacementY = 0
        self.AddX = 3
        self.AddY = 3


    def TimerCB(self, TimerObj):
        self.LastFrame  = self.ThisFrame
        self.ThisFrame = time.ticks_ms()
        self.FrameDelta = self.ThisFrame - self.LastFrame
        if not self.Visible:
            return
        self.nFrames += 1
        self.NeedsDrawing = True

    def Draw(self, Framebuf):
        if not self.Visible:
            self.NeedsDrawing = False
            return

        self.DisplacementX += self.AddX
        self.DisplacementY += self.AddY

        if self.DisplacementX > 

        for y in range(0,64):
            for x in range(0,128):
                nX = self.nFrames % 10
                nY = 3
                Pixel = self.GetPixel(x,y,Framebuf)
                Pixel = Pixel or self.GetPixel(x,y,Framebuf)
                Pixel = Pixel or self.GetPixel(x + nX, y,Framebuf)
                #Pixel = Pixel or self.GetPixel(x - nX, y,Framebuf)
                Pixel = Pixel or self.GetPixel(x , y + nY,Framebuf)
                #Pixel = Pixel or self.GetPixel(x , y - nY,Framebuf)

                Framebuf.pixel(x,y,Pixel)

    def GetPixel(self,x,y,Framebuf):
        if x < 0 or x > 127:
            return 0
        if y < 0 or y > 64:
            return 0

        p = Framebuf.pixel(int(x),int(y))
        if p is None:
            return 0
        return p

    def Start(self, Framebuf):
        self.LastFrame = time.ticks_ms()
        self.ThisFrame = self.LastFrame
        self.FrameDelta = 0
        self.Visible = True
        self.NeedsDrawing = True

    def Pause(self):
        self.Visible = False


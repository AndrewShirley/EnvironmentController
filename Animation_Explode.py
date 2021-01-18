import math
import AndrewsTimer
import gc

# class MovingPoint:
#     def __init__(self, X, Y):
#         self.X = X
#         self.Y = Y
#         self.IncrementX = 0
#         self.IncrementY = 0



class Explode:
    def __init__(self, X1, Y1, X2, Y2, framebuf):
        ''' X1,Y1 to X2,Y2 is scanned for pixels and exploded '''
        self.X1 = X1
        self.Y1 = Y1
        self.X2 = X2
        self.Y2 = Y2
        self.Framebuf = framebuf
        self.CentreX = (X1 + X2) / 2
        self.CentreY = (Y1 + Y2) / 2
        self.Gravity = 0.5

        self.Points=[]     # Array of pixels to animate. Each entry is [X,Y,IncreaseX,IncreaseY]   
        self.NeedsDrawing = False
        self.GeneratePoints()
        self.QuitAfternFrames = 100
        self.nFramesRendered = 0

        self.Timer = AndrewsTimer.Timer(100,self.HandleCB)

    def HandleCB(self, TimerOBJ):
        self.DoIncrementsAndGravity()
        self.NeedsDrawing = True

    def Go(self):
        self.Timer.Pause()
        self.Points.clear()
        gc.collect()
        self.nFramesRendered = 0
        self.GeneratePoints()
        self.Timer.Start()


    def GeneratePoints(self):
        #print("Generating ponts")
        ScaleX = 17
        ScaleY = 5
        SpeedX = 8
        SpeedY = 3

        for y in range(self.Y1, self.Y2 + 1):
            for x in range(self.X1, self.X2 + 1):
                #print(self.Framebuf.pixel(x,y))
                if self.Framebuf.pixel(x,y) == 1:
                    #print("Making new point, centre=",self.CentreX, self.CentreY)
                    #p = MovingPoint(x,y)
                    dX = x - self.CentreX
                    dY = y - self.CentreY
                    SgnX = 1
                    SgnY = -1
                    if dX < 0: SgnX = -1
                    if dY < 0: SgnY = 1

                    
                    DegX = 0
                    DegY = 0

                    if dX != 0:
                        DegX = 1/(dX/ScaleX) * 45
                    
                    if dY != 0:
                        DegY = 1/(dY/ScaleY) * 45
                   
                    IncX = 1 + math.cos(math.radians(DegX)) * SpeedX * SgnX * math.cos(math.radians(DegX))
                    IncY = 1 + math.cos(math.radians(DegY)) * SpeedY * SgnY * math.cos(math.radians(DegY))
 
                    self.Points.append([x,y,IncX,IncY])

                    #print("Made Point:",p.X,p.Y,p.IncrementX,p.IncrementY)

    def DoIncrementsAndGravity(self):
        for P in self.Points:
            P[0] += P[2]   # P.X += P.IncrementX
            P[1] += P[3]   # P.Y += P.IncrementY

            P[3] += self.Gravity   # 3=P.IncrementY
            

    def Draw(self, Framebuf):
        if self.nFramesRendered >= self.QuitAfternFrames:
            return

        #print("A, nPoints=", len(self.Points))

        for p in self.Points:
            #self.Framebuf.pixel(int(p.X), int(p.Y), 1)
            Framebuf.pixel(int(p[0]), int(p[1]), 1)

        #print("B")

        self.NeedsDrawing = False
        self.nFramesRendered += 1
        if self.nFramesRendered >= self.QuitAfternFrames:
            self.Timer.Pause()
            self.NeedsDrawing = True            # Erase the remnants


'''
IconBar allows Icons to be printed across the framebuf/screen.  Icons can be variable width and height.
It can be vertical or horizonal with its origin set.

Stacked mode allows you to display one single image from a whole selection of them, contained within the IconBar.
Example of stacked mode:
IB = IconBar.IconBar(Stacked=True,"ImagesAndFonts/link.pbm","ImagesAndFonts/link-broken.pbm")  # Default Icon is last
IB.StackedModeTopIconIndex = 0      # Set to link.pbm

You can add as many images as you want and the last one is always shown by default until StackedModeTopIconIndex is set
to its index within the array.

Idea : Add Auto Increment to the Index to allow simple GIF type animations. This could work screen wide to allow
video type display.  AutoIncrement is easy to calculate using time between calls.  Its automatic.  You prolly should
add a framerate then.

'''

import AndrewsTimer
import pbm
import time


class Icon(pbm.pbm):
    nIcons = 0

    def __init__(self, IconPath="", Invert=True, FlashesPerSecond=0, UniqueName=""):
        super().__init__(IconPath, Invert)

        #        self._FlashesPerSecond = FlashesPerSecond
        self.Timer = None
        #self.FlashesPerSecond = property(self.Set_FlashesPerSecond, self.Get_FlashesPerSecond)
        self.FlasherImage = "ImagesAndFonts/Blank.pbm"
        self.FlashOverRideImageOn = False       # Goes True once every Flash cycle
        self._FlashesPerSecond = 0
        self.FlashesPerSecond = FlashesPerSecond
        self.NeedsDrawing = False
        if UniqueName == "":
            self.UniqueName = "Icon_" + str(Icon.nIcons)
        else:
            self.UniqueName = UniqueName

        Icon.nIcons += 1

    @property
    def FlashesPerSecond(self):
        #print("GEtting")
        return self._FlashesPerSecond

    @FlashesPerSecond.setter
    def FlashesPerSecond(self, Value):
        if self._FlashesPerSecond != Value:
            self._FlashesPerSecond = Value
        #print("Setting Flashes Per Second=",Value)
            if Value > 0:
                D = int((1 / Value) * 500)    # 1000 / 2 = On for half time and Off for the other half
                if self.Timer is None:
                    self.Timer = AndrewsTimer.Timer(D, self.HandleCB)
                else:
                    self.Timer.Duration = D
                self.Timer.Start()
            else:
                # TODO Redraw Icon in the ON position
                self.PauseTimer()

    


    def HandleCB(self,TimerOBJ):
        self.NeedsDrawing = False
        self.Flash()
        # Set to true to indicate something needs updating on the screen

    def GetImage(self):
        #print(type(self))
        if self.FlashOverRideImageOn:
            I = Icon(self.FlasherImage).GetImage()
            #print("Using Flasher Image")
        else:
            I = super().GetImage()
            #print("Using Proper Image")
        return I

    def Flash(self):
        self.FlashOverRideImageOn = not self.FlashOverRideImageOn
        self.NeedsDrawing = True
        #print("Setting Flash override to ",self.FlashOverRideImageOn)

    def PauseTimer(self):
        if not self.Timer is None:
            self.Timer.Pause()
            self.FlashOverRideImageOn = False
            self.NeedsDrawing = True


class IconBar:
    def __init__(self, Stacked=False, *Icons):
        self.Icons = {}
        self.X = 0
        self.Y = 0
        self.SpaceBetweenIcons = 2
        self.Stacked = Stacked
        self.StackedModeTopIconIndex = -1           # -1 = Last item in the array
        self.Vertical = False
        self.LastDraw = time.ticks_ms()
        #self.Flasher = False                        # Auto Flash between current Icon and Blank.pbm using FrameRate
        #self.FrameRate = 1                          # 1 Frames per second, 200ms per frame
        #self.NextFlash = time.ticks_ms() + (1/self.FrameRate) * 1000

        self.AutoIncrementIndex = False             # AutoIncrement? Uses FrameRate
        self.AutoIncrementAmount = 1                # Simply add 1 to index to autoincrement.
                                                    # Using various amounts of images and larger AutoIncrement amounts can 
                                                    # result in neat patterns
        #self.UseFlasherImage = False
        #self.FlasherImage = "ImagesAndFonts/Blank.pbm"
        self.Timer = AndrewsTimer.Timer(100,self.HandleCB)

        for I in Icons:
            #print(I,I.UniqueName)
            self.AddIcon(I)

    def AddIcon(self, *Icons):
        for I in Icons:
            self.Icons[I.UniqueName] = I

    def GetIcon(self, UniqueName):
        return self.Icons[UniqueName]



    def HandleCB(self,TimerOBJ):
        pass
        #self.Flash()


    def TimeSinceLastDraw(self):
        return time.ticks_ms() - self.LastDraw


    def Draw(self,framebuf):
        t = time.ticks_ms()

        if self.Stacked:
            I = self.Icons[self.StackedModeTopIconIndex].GetImage()
            I.NeedsDrawing = False
            framebuf.blit(I.GetImage(), self.X, self.Y)

        else:
            X = self.X
            Y = self.Y

            for I in self.Icons.values():
                #print(I,type(I), I.Path, I.GetImage)
                Img = I.GetImage()
                framebuf.blit(Img, X, Y)

                I.NeedsDrawing = False

                if self.Vertical:
                    Y += I.ImageHeight + self.SpaceBetweenIcons
                else:
                    X += I.ImageWidth + self.SpaceBetweenIcons

        self.LastDraw = t
        #self.NeedsDrawing = False

    # def Flash(self):
    #     Delta = self.NextFlash - time.ticks_ms()
    #     Period = (1/self.FrameRate) * 1000
    #     if Delta <= 0:
    #         self.NextFlash = self.NextFlash + Period
    #         self.UseFlasherImage = False
    #         return

    #     P = Delta / Period
    #     #print(P)
    #     if P >= 0.5:
    #         if self.UseFlasherImage != True:
    #             self.NeedsDrawing = True
    #             self.UseFlasherImage = True
    #     else:
    #         if self.UseFlasherImage != False:
    #             self.NeedsDrawing = True
    #             self.UseFlasherImage = False

    def NeedsDrawing(self):
        for I in self.Icons.values():
            if I.NeedsDrawing:
                return True

        return False


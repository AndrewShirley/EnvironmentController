'''
    Represents a Text Object, visible on the OLED screen
    - Supports Autoscrolling when content is too long
    - Supports custom fonts


    Known Issues:
     - Autoscrolling only works with custom fonts

'''


import framebuf
import AndrewsTimer
import time

class TextObject:
    def __init__(self, X=0, Y=0, Colour=1,InitialText="--", Font=None, Width=128, Height=64):
        self.NeedsDrawing = True
        self.X = X              # Origin of imaginary box in which text will be printed
        self.Y = Y
        self.TextX = 0          # Displacement into X,Y to print text
        self.TextY = 0
        self.Colour = Colour
        self._Text = InitialText
        #self._Text = Text
        self.Font = Font      #font Object.  If this one exists then drawing takes place using this font rather than default 8X8
        self.CharacterSpacing = 2    # pixels to put between each character if using a non-default font
        self.Width = Width             # Determines the justification of text, ie: halign=right or centre
        self.Height = Height             # and the clipping
        self.WordWrapOn = False
        self.ScrollX = 0                 # Amount to subtract from self.X
        self.ScrollXIncrement = 1
        self.AutoScrollX = True          # If Text exceeds bounds, autoscrolls
        self.ScrollPausedUntil = time.ticks_ms() + 4000    # Pause the scrolling Mechanism until after this time
        self._PixelWidth = -1            # Last Calculated. This will be returned if PixelWidth() has already been called due to its high cpu cost
        self._DoingEndPause = False
        self.Shadow = False
        try:
            self.Timer = AndrewsTimer.Timer(100,self.HandleCB)
        except Exception as Ex:
            print(Ex)
            AndrewsTimer.DeInitMasterTimer()

    @property
    def Text(self):
        return self._Text

    @Text.setter
    def Text(self, Value):
        #print("Setter Called with ",Value," Old value is ",self._Text)
        if self._Text != Value:
            self._Text = Value
            self._PixelWidth = -1
            self.NeedsDrawing = True
            #print("Set _PixelWidth to -1")

    def HandleCB(self,TimerObj):
        self.DoAutoScroll()

    def DoAutoScroll(self):
        if time.ticks_ms() < self.ScrollPausedUntil: return

        self.ScrollPausedUntil = 0

        if self.AutoScrollX:
            #print("PixelWidth=",self.PixelWidth(), self.Text)
            if self.PixelWidth() < self.Width : return
            n = self.ScrollX + self.Width       # 
            Delta = n - self.PixelWidth()
            if Delta <= 0:           # Continue
                self.ScrollX += self.ScrollXIncrement
                self.NeedsDrawing = True
                return
            # Can't compare Delta to 0 since it may never happen with different XIncrements
            if Delta > 0:           # We've Scrolled past the end, did a pause and now we reset
                if not self._DoingEndPause:
                    self.ScrollPausedUntil = time.ticks_ms() + 2000
                    self.ScrollX += self.ScrollXIncrement
                    self.NeedsDrawing = True
                    self._DoingEndPause = True

                else:       # Hit the end, time to reset
                    self.ScrollPausedUntil = time.ticks_ms() + 4000
                    self.ScrollX = 0
                    self.NeedsDrawing = True
                    self._DoingEndPause = False
                return

    def Draw(self, Framebuf):
        if not self.Font is None:               # If we have a custom font loaded
            self.DrawStringWithFont(Framebuf,self.Font,self.Text,self.Width,self.Height,self.TextX-self.ScrollX, self.TextY,self.X,self.Y)
        else:
            # ToDO: Redo this - won't work
            Framebuf.text(self.Text, self.X + self.TextX - self.ScrollX, self.Y + self.TextY, self.Colour)

        self.NeedsDrawing = False


    def DrawStringWithFont(self, FB, Font, Text, Width=128, Height=64, TextX=0, TextY=0, PlaceX=0, PlaceY=0, CharacterSpacing=2, Colour=1):
        #X, Y = PlaceX, PlaceY
        ByteArraySize = (self.Width * self.Height) // 8

        #print("Trying to DrawString...ByteArraySize=",ByteArraySize)
        TempFB = framebuf.FrameBuffer(bytearray(ByteArraySize),self.Width, self.Height, framebuf.MONO_HLSB)

        X = TextX
        Y = TextY
        for ch in Text:
            #print(ch)
            MemView, FontHeight, FontWidth = Font.get_ch(ch)
            f = framebuf.FrameBuffer(bytearray(MemView), FontWidth, FontHeight, framebuf.MONO_HLSB)
            TempFB.blit(f, X, TextY)
            X += FontWidth
            X += self.CharacterSpacing
            #print(bytes(MemView))

            # Wordwrap
            if self.WordWrapOn:
                if X + FontWidth >= Width:
                    X = TextX
                    Y += FontHeight

        FB.blit(TempFB,PlaceX, PlaceY, 0)
        del TempFB



    # Returns the width in pixels of self.Text if rendered using self.Font
    def PixelWidth(self):

        if self._PixelWidth > -1:
            #print("PixelWidth Precalculated at :",self._PixelWidth, self.Text)
            return self._PixelWidth

        W = -1


        if self.Font is None:
            W = len(self.Text) * 8                          # Width of characters only
        else:
            W = 0
            for C in self.Text:
                Obj,Height,Width = self.Font.get_ch(C)
                W += Width                                  # Width of characters only
                del Obj                                     # Help the GC?
                #print("Chr Width=",Width, "total=", W)

        W += self.CharacterSpacing * (len(self.Text) - 1)   # Add character spacing
        #print("Dont Calculating length of ", self.Text, " at ", W, " Chr Spacing adds ", self.CharacterSpacing * (len(self.Text) - 1), "Pixels")
        self._PixelWidth = W    
        #print("PixelWidth Calculated at :", self._PixelWidth, self.Text)

        return W

    # Returns the X coordinate to start printing this text to be centred within Width pixels
    def CalculateHorizontalCentre(self, Width):
        return int(Width / 2) - int(self.PixelWidth() / 2)

    # Returns the Y coordinate to start printing this text to be centred within Height pixels
    def CalculateVerticalCentre(self, Height):
        return int(Height/2) - int(self.Font.height() / 2) 



    def JustifyHorizontalRight(self):
        self.TextX = self.Width - self.PixelWidth()


    # Sets this Text object's X location to justify to centre with Width pixels
    def JustifyHorizontalCentre(self, Width=-1):
        W = Width if Width > -1 else self.Width
        self.TextX = self.CalculateHorizontalCentre(W)
        #print("Setting X to ",self.X, " Text = ", self.Text)

    # Sets this Text object's Y location to justify to centre with Height pixels
    def JustifyVerticalCentre(self, Height=-1):
        H = Height if Height > -1 else self.Height
        self.TextY = self.CalculateVerticalCentre(H)





'''
	Image file in PBM format.
	I don't claim ownership of this work, but I did modify it.  Sorry, I don't have the link...	

'''



import framebuf
import math

# A Class to represent a PBM image for display
class pbm:
	def __init__(self, Path="", Invert=True):
		#self.X1 = X
		#self.Y1 = Y
#		self.ImageWidth = Width
#		self.ImageHeight = Height
		self.Path = Path
		self.Invert = Invert
		self.ReadWidthAndHeight()
		self._Framebuf = None
		#print("Image is ",self.ImageWidth, " X ", self.ImageHeight)
		#print("!Init Path = ",Path)

	def Width(self):
		return self.ImageWidth

	def Height(self):
		return self.ImageHeight

	# def Draw(self, framebuffer, X, Y):
	# 	self.GetTile(framebuffer, X, Y, self.ImageWidth, self.ImageHeight)

	def ReadWidthAndHeight(self):
		try:
			with open(self.Path, 'rb') as f:
				f.readline()  # Magic number
				Str = f.readline()
				#print("#=",Str[0])
				while Str[0] == 35:		# This is the '#' sign
					Str = f.readline()

				Arr = Str.decode("utf-8").split(" ")  # Dimensions

				self.ImageWidth = int(Arr[0])
				self.ImageHeight = int(Arr[1])

		except Exception as ex:
			print(ex)

	def GetImage(self):
		''' Returns a Framebuf with the image in it '''
		
		if not self._Framebuf is None:
			return self._Framebuf

		with open(self.Path, 'rb') as f:
			f.readline()  # Magic number
			f.readline()  # Creator comment
			f.readline()  # Dimensions
			data = bytearray(f.read())
			
			if self.Invert:
				#print("Inverting", len(data))
				for X in range(0, len(data)):
					data[X] ^= 255

		#for i in range(0,len(data),2):
		#	print("{0:b}{0:b}".format(data[i], data[i+1]))

		#print("Making Framebuf: ",self.ImageWidth, self.ImageHeight)

		self._Framebuf = framebuf.FrameBuffer(data, self.ImageWidth, self.ImageHeight, framebuf.MONO_HLSB)
		return self._Framebuf

	# this function will get a section of the graphic to the given framebuffer
	def GetTile(self, framebuffer, TileX, TileY, TileWidth, TileHeight):
		#print("Opening file ",self.Path)
		with open(self.Path, 'rb') as f:
			f.readline()  # P4
			Str = f.readline()
			while Str[0] == 35:		# This is the '#' sign
				Str = f.readline()

			Inversion = 0 if self.Invert else 255
			
			StartX = math.floor(TileX / 8)
			EndX = math.floor( ( TileX + TileWidth -1 ) / 8 )
			RowWidthInBytes = math.ceil(self.ImageWidth / 8)
			data = bytearray()

			if TileY > 0:				# advance the file
				f.read(RowWidthInBytes * TileY)
				#print("Advancing ",RowWidthInBytes * TileY)

			print("PBM.1",StartX, EndX)

			for y in range(TileY,TileY + TileHeight):
				b = bytearray(f.read(RowWidthInBytes))
				#print(b)
				for x in range(StartX,EndX+1):
					print(x,y)
					data.append(b[x] ^ Inversion)


			fbuf = framebuf.FrameBuffer(data, TileWidth, TileHeight, framebuf.MONO_HLSB)
			framebuffer.blit(fbuf, self.X1, self.Y1)


# todo Just checking to see if lowercase to-do works

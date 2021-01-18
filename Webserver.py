'''
Webserver for Micropython by Andrew Shirley 2021

This webserver will run in the background and produce a callback when a page request comes in.
See Webserver.NewPageRequestCB

Import Objects:
--------------
Webserver
Webpage
Response
Request

Depends on AndrewsTimer

'''

import socket
import uselect
import AndrewsTimer
import sys


class Response:

    #        Socket.send('HTTP/1.0 200 OK\r\nContent-type: text/html\r\n\r\n')
    def __init__(self):
        self.HTTPVersion = "HTTP/1.0"
        self.ResponseCode = "200"
        self.ResponseText = "OK"
        self.ContentType = "text/html"
        self.ResourceName = ""          # Set to the resource requested, ie: index.html, favicon.gif etc
        self.Parameters = {}            # Parameters that will be inserted into the webpage. Probably a copy of the one in Webserver

    def ResourceExists(self):
        ''' Returns True or False, to determine if the resource exists, ie: Index.html '''
        try:
            Pathname = self.ResourceName
            f = open(self.ResourceName, "r")
            f.close()
            return True
        except Exception:
            return False


    def SendResponse(self, SocketObj):
        ''' Sends the entire response to the browser '''
        self.SendHeader(SocketObj)
        self.SendBody(SocketObj)

    def SendHeader(self, SocketObj):
        ''' Automatically called by SendResponse '''
        # Sample Response: 'HTTP/1.0 200 OK\r\nContent-type: text/html\r\n\r\n')
        SocketObj.send("{} {} {}\r\nContent-type: {}\r\n\r\n".format(self.HTTPVersion, self.ResponseCode, self.ResponseText ,self.ContentType))  

    def ReplaceWithParameters(self, Text):
        if Text.find("$Parameters") > -1:
            NewText = "<table>"
            for Key, Value in self.Parameters.items():
                NewText += "   <tr>"
                NewText += "      <td>" + Key + "</td><td>" + Value + "</td>"
                NewText += "   </tr>"
            NewText += "</table>"

            Text = Text.replace("$Parameters",NewText)
            #print("NewText=",NewText)

        for Key, Value in self.Parameters.items():
            Text = Text.replace("$"+Key, Value)

        return Text


    def SendBody(self, SocketObj):
        ''' Automatically called by SendResponse '''
        if self.ContentType == "text/html":
            self.SendHTML(SocketObj, self.ResourceName)
        pass

    def DoRunString(self,RunStr):
        #print("Called Runstr with:", RunStr)
        if len(RunStr) > 0 :
            try:
                ResponseString = ""
                #print("Running",RunStr)
                exec(RunStr.strip())
                #print("Response String=",boot2.ResponseString)
                return ResponseString
            except Exception as Ex:
                #print("Webserver, DoRunString in the Response object failed:")
                sys.print_exception(Ex)

        return("")

    def SendHTML(self, SocketObj, Filename):
        w = Webpage(Filename)       # Webpages/index.html
        #print("Reading file...",Filename)
        f = w.GetReader()
        ReadingPython = False

        if f is None:
            SocketObj.send("Oops!  Page not found, even though it was found earlier.  That's weird")
            print("Can't deliver webpage", w.GetPath())
        else:
            #print("Delivering",w.GetPath())
            #print(type(f))
            RunStr = ""
            Line = f.readline()
            while Line:

                if not ReadingPython:
                    if Line.find("<python>") > -1:       # <bold><python>x=27</python></bold>
                                                         # 012345678901234567
                        Line = Line[Line.index("<python>") + 8:]
                        ReadingPython = True
                        if len(Line) > 0: continue

                if ReadingPython:
                    # <bold><python>x=27</python></bold>
                    if Line.find("</python>") > -1:
                                                         # 012345678901234567
                        X = Line.index("</python>")
                        ReturnString = ""
                        if X > 0:
                            ReturnString = self.DoRunString(Line[0:X])       # >0 means </python> wasnt found against the leftside. Could be more code to send to the interpreter
                        Line = ReturnString + Line[ X + 9:]
                        ReadingPython = False
                        continue

                    # This is reached when sending the whole line to the interpreter
                    Line = self.DoRunString(Line)

                #print(self.ReplaceWithParameters(Line))
                try:
                    SocketObj.send(self.ReplaceWithParameters(Line))
                except Exception as Ex:
                    pass
                #print("Sending HTML Response Line:",Line)

                Line = f.readline()

            f.close()

class Request:
    def __init__(self):
        ''' Parameters collected from the page request.  Usually:
            PageRequested
            Host
            Connection
            Cache-Control
            Upgrade-Insecure-Requests
            User-Agent
            Accept
            Accept-Encoding
            Accept-Language
        '''
        self.Parameters = {}

    def PageName(self):
        str = "/"
        
        if "PageRequested" in self.Parameters.keys():
            str = self.Parameters["PageRequested"]

        Slash = str.rfind("/")                      # could be "/"
        if Slash == 0: return "index.html"

        #print("Webserver:Request:PageName:88:str=",str)
        return str.split("/")[-1].split("?")[0]

    def GetParameterValue(self, ParameterName, DefaultValue):
        ''' Returns a value from the Paramters dict if it exists.  Otherwise returns the DefaultValue '''
        if ParameterName in self.Parameters.keys():
            return self.Parameters[ParameterName]

        return DefaultValue

    def GetQueryValue(self, QueryName, DefaultValue):
        ''' Returns a value from the URL's Query if its specified.  Otherwise returns the DefaultValue '''
        Keys = self.QueryParameters()

        if QueryName in Keys.keys():
            return Keys[QueryName]

        return DefaultValue



    def QueryParameters(self):
        ''' Returns a dictionary with the key/value (if any) pairs from the Query string 
            Query like this: http://index.html?Andrew=10&Shirley=10
        '''

        Dict = {}
        Str = self.GetParameterValue("PageRequested", "/")
        QPs = Str.split("?") 
        if len(QPs) > 1:
            KeyValues = QPs[1].split("&")
            for I in KeyValues:
                Arr = I.split("=")
                if len(Arr) > 1:
                    Dict[Arr[0]] = Arr[1]
        return Dict


    def FillFromReader(self, Socket):
        while True:
            Line = Socket.readline()
            if not Line or Line == b'\r\n':
                break

            Str = Line.decode('utf-8')

            # print(Str)

            if Str.find("GET") == 0:
                Arr = Str.split(' ')
                self.Parameters["Type"] = Arr[0]
                self.Parameters["PageRequested"] = Arr[1]
                self.Parameters["HTTPVersion"] = Arr[2]
                #print("Setting Page Requested to ",Arr[1])
            else:
                Arr = Str.replace(':','').split(' ')
                self.Parameters[Arr[0]] = Arr[1]



class Webpage:
    def __init__(self,PageName="index.html"):
        self.PageName = PageName

    def GetPath(self):
        return self.PageName

    def GetReader(self):
        try:
            return open(self.GetPath())
        except Exception as Ex:
            print("Error Opening File:",self.GetPath())
            print(Ex)
            return None


class WebServer:
    def __init__(self, OnNewPageRequest=None):
        #self.Temperature = "22.1C"
        #self.Humidity = "38%"
        self.AsyncPoll = uselect.poll()
        self._s = socket.socket()
        self.Parameters = {}            # Search/Replace tokens. Index=Search,Value=Replace. Webpage contains $Temperature, then adding "Temperature","22" puts it in the webpage
        self.NewPageRequestCB = OnNewPageRequest
        Address = socket.getaddrinfo('0.0.0.0', 80)[0][-1]
        self._s.bind(Address)
        self._s.listen(-5)
        self.AsyncPoll.register(self._s, uselect.POLLIN)
        self.Timer = AndrewsTimer.Timer(100,self.HandleTimerCB)
        print("Webserver Listening on", Address)

    def DoNewPageCallBack(self, RequestObj, PageResponseObj):
        if not self.NewPageRequestCB == None:
            self.NewPageRequestCB(RequestObj, PageResponseObj)

    def AddParameter(self,KeyName, Value):
        ''' Adds a new parameter to the list. Each parameter is accessible from a webpage in Javascript '''
        self.Parameters[KeyName] = Value
    
    def HandleTimerCB(self, TimerObj):
        self.CheckForIncomingConnections()

    
    def Start(self):
        self.Timer.Start()

    def Pause(self):
        self.Timer.Pause()


    def CheckForIncomingConnections(self):
        Arr = self.AsyncPoll.poll(20)

        if not Arr:
            return
        
        #print("Arr=",Arr)

        Socket, addr = self._s.accept()

        #print('client connected from', addr)
        SocketFile = Socket.makefile('rwb', 0)

        #print("****Received the following Request:")
        PageRequest = Request()
        PageRequest.FillFromReader(SocketFile)
        PageResponse = Response()

        PageName = PageRequest.PageName()
        print("Webserver:200:PageName=",PageName)
        
        if PageName == "/":
            PageName = "index.html"

        if PageName[0] == "/":
            PageName = PageName[1:]
        PageResponse.ResourceName = "Webpages/" + PageName

        PageResponse.Parameters = self.Parameters           # Make a copy

        if not PageResponse.ResourceExists():
            PageResponse.ResponseCode = "404"
            PageResponse.ResponseText = "Not Found"

        self.DoNewPageCallBack(PageRequest, PageResponse)
        PageResponse.SendResponse(Socket)

        Socket.close()
        self._s.listen(0)
        print("Done HTML Webpage request")


'''
    MQTT Dispatcher takes care of sending and receiving MQTT messages.
     - Provides a callback when MQTT messages are received
     - Queues all MQTT messages locally and sends them when the MQTT server is available
     - Auto-resubscribes on WIFI reconnects
'''

import AndrewsTimer
import MQTTClient
import network


# Single topic or Comma seperated list ie: "Command/Input,Command/Ear,Command/Tellmewhattodo"
MQTT_SubscribeTopic = "OutletController_1/Input"
MQTT_PublishTopic = "OutletController_1/Output"


'''
Represents a Queue for sending messages via an MQTT client to a broker.  You can Queue up Messages even if the MQTTClient
hasn't been created yet, allowing late-creation of the client.  BUT, when the MQTTClient IS created, you need to add
a reference to this Dispatcher via MQTTDispatcher.MQTTClientObj
'''

class MQTTDispatcher:

    def __init__(self, MQTTClientID, SubscribeTo="", RetryTime=10):       # Default to 10s retry
        self.MQTT_ClientObj = None
        self.RetryTime = RetryTime
        self.Timer = AndrewsTimer.Timer(self.RetryTime * 1000, self.TimerCB,"MQTTRetry")
        self.Timer2 = AndrewsTimer.Timer(1000, self.CheckMQTTCB,"MQTTMsgLoop")
        self.Queue = []
        self.MQTTBrokerConnectedCB = None

        self.MQTT_Server = '192.168.2.208'
        self.MQTT_ClientID = MQTTClientID
        self.Subscriptions = SubscribeTo
        self._WifiObj = None
        self._NeedsSubscribe = True
        self._LastWifiConnectionCheck = False

    def Publish(self, Topic, Message):
        ''' Adds a new Topic/Message Tuplet to the Queue '''
        self.Queue.append((Topic, Message))
        self.ProcessQueue()

    def ProcessQueue(self):
        if self.MQTT_ClientObj is None:      # Wait for connection to be made before processing queue
            self.ConnectAndSubscribe()
            return

        while True:         # Troubleshooting, replaced while len(self.Queue) > 0:
            if len(self.Queue) == 0:
                break

            Msg = self.Queue[0]
            try:
                #print("Trying to Publish \n", Msg[0], Msg[1])
                self.MQTT_ClientObj.publish(Msg[0], Msg[1])
                del self.Queue[0]
                #print("Deleted. nItems in Queue is ",len(self.Queue))
            except Exception as X:         # If an Exception occurs, try the queue again later, maybe Wifi is down?
                print("EXCEPTION", X)
                return

    def TimerCB(self, TimerObj):
        self.ProcessQueue()


    def CheckMQTTCB(self, TimerObj):
        ''' Called once a second to check on received MQTT messages '''
        if not self.MQTT_ClientObj is None:
            self.MQTT_ClientObj.check_msg()


    def NetworkConnected(self):
        if self._WifiObj is None:
            self._WifiObj = network.WLAN(network.STA_IF)

        return self._WifiObj.isconnected()

    def ConnectAndSubscribe(self):
        ''' Ensures we are connected to the MQTT server and ensures subscriptions are made '''
        #print("X.1", self.NetworkConnected())

        v = self.NetworkConnected()
        if v != self._LastWifiConnectionCheck:
            self._NeedsSubscribe = True

        self._LastWifiConnectionCheck = v

        #print(v)
  
        if not v:       # No connection, wait for it to come back
            return

        #print("X.2")

        if(self.MQTT_ClientObj is None):
            self.MQTT_ClientObj = MQTTClient.MQTTClient(self.MQTT_ClientID, self.MQTT_Server)
            self.MQTT_ClientObj.set_callback(self.TimerCB)
            self.MQTT_ClientObj.connect()
    
            if not self.MQTTBrokerConnectedCB is None: self.MQTTBrokerConnectedCB(self)



        if self._NeedsSubscribe:
            print("Subscribging")
            self.SubscribeToTopics()
            self._NeedsSubscribe = False

        #print("X.3")

    def SubscribeToTopics(self):
        Topics = self.Subscriptions.split(",")
        if(len(Topics) < 1):
            # If only one topic is specified then it wouldn't survive the split on ",". Therefore make it the only element in the list
            Topics = [self.Subscriptions]

        for I in Topics:
            print("Subscribing to ",I)
            self.MQTT_ClientObj.subscribe(I)

        print("X.4")

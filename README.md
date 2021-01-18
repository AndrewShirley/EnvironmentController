# PlugController
 

EnvironmentController is a Micropython project to monitor and control temperature and humidity in an environment.
It features a web interface, MQTT control and status events and a flexible object-oriented GUI.

The project was written for an ESP32 with built-in 0.96 monochrome OLED.



For sensing temperature, humidity and pressure, I'm using a BME280.

For controlling a humidifier and fan, I'm using an SCR based 4X relay module.  SCR modules can control less current
than a mechanical relay, but they don't stick and can provide enough current to run the low needs of a fan and humidifier.

Setting the running configuration can be performed through the built-in web interface or via MQTT messages.

Status is displayed on the OLED screen, plus sent via MQTT or read through the built-in web interface.

Currently I have NodeRed capturing these MQTT status events and storing them in an InfluxDB.


The reason I wrote this project was for a number of reasons. 
- Reuse of code.  This project features a lot of code that I plan on reusing in future projects, such as:
    - AndrewsTimer
    - EnvironmentController
    - IconBar
    - MQTTDispatcher
    - RelayModule
    - TextObject
    - Webserver

AndrewsTimer:
    Andrew's Timer removes the complexity of interfacing with the ESP32's 4 hardware timers.  You can create an unlimited number of timers, which are all timed off of one main hardware timer.  Timers can be one-shot or recurring with 1mS precision.

EnvironmentController:
    The Environment Controller monitors the temperature and humidity and makes decisions to run the fan or humidifier
    in order to keep temperature and humidity within a range.

IconBar
    The IconBar is a GUI object that can display a row or column of images.  Optionally you can stack them on top of
    each other and bring one to the front so that its the only one being displayed.  A typical use would be for the Wifi
    connection Icon.  The stack consists of two images - one broken link and one connected link.  Simply bring the
    image to the front of the stack to match your wifi status, as is done in this project.

MQTTDispatcher
    The MQTT Dispatcher queues outgoing MQTT messages and sends them when Wifi is available.  Its tolerant to broken
    connections and will automatically reconnect and resubscribe to your subscriptions.  It fires a Callback when a new
    MQTT message is received.  

RelayModule
    A Relay Module is a 4 X Relay controllable by the GPIO pins one the ESP32.  Its useful for switching AC loads using
    nothing more than a small control voltage.  In this project I used an SCR based module since I had issues with
    my mechanical relays sticking.  SCR can't handle as much current as a standard mechanical relay but its enough
    to power a fan and humidifier.

TextObject
    A GUI object that displays text on the screen, bounded by width/height with optional scrolling for text that
    exceeds its boundaries.

Webserver
    I wrote this Webserver in micropython to be as simple as possible to use and as functional as any programmer would
    need.  Webpages support easy insertion of parameters from your program and can run Python right in the webpage.
    
    Parameter Example:
        
        <b>$temperature&deg;</b>
        
        is replaced by:
        
        <b>21.09&deg;</b>
        
        and sent to the browser

    Python Example:

        <b>print("Hello world from Python")</b>




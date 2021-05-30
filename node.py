from sensorclass import Sensor
from machine import Pin
from stepclass import Stepper
from neopixel import NeoPixel
import time

# sensor: backdoor2
# Started 10/24/2020

led = NeoPixel(Pin(0, Pin.OUT), 64)

lights = Sensor("state", "VS" )
lights.setstate(False)

brightness = Sensor("brightness", "VS" )
brightness.setvalue(20)

door = Sensor("door", "INP", 4, onname="Open", offname="Closed")

statusled = Sensor("led", "OUT", 2)
statusled.setstate(True)

ldr = Sensor("ldr", "ADC", 0, poll=1000, diff=50)

m = Stepper()
c = Sensor("curtains", "VS", onname="Open", offname="Closed", initval="init" )
c.triggered = False

setpos = Sensor("setpos", "VS", initval=0)
setpos.pubneeded = False
setpos.triggered = False

ucpos = Sensor("ucpos", "VS", initval=0, save=True) 
ucpos.pubneeded = False
ucpos.triggered = False

pos = Sensor("pos", "VS", initval=0, save=True) 
pos.pubneeded = False
pos.triggered = False

def setlight(brightlevel):
    global led
    for x in range(64):
        led[x] = (0,brightlevel,0)
    led.write()

def main():
    nightlight = False
    nldelay = 80
    start_nl = time.time()
    setlight(0)
    Sensor.MQTTSetup("backdoor")
    while True:
        Sensor.Spin()
        if pos.triggered and c.value == "init":
            print("pos.triggered, setting init position")
            pos.triggered = False
            m.setpos(pos=pos.value)
            setpos.setvalue(pos.value)
            m.kpos = True
        if setpos.triggered:
            print("setpos.triggered: ", setpos.value)
            setpos.triggered = False
            if setpos.value < 0:
                if m.home():
                    c.setvalue("Closed")
                else:
                    c.setvalue("HomeFail")
            else: 
                m.set(pos=setpos.value)
        if m.triggered:
            print("m.triggered")
            m.triggered = False
            if m.kpos:
                print("Moved to: ", m.pos)
                ucpos.setvalue(m.ucpos)
                pos.setvalue(m.pos)
                pos.triggered = False
                if m.pos > 0:
                    c.setvalue("Open")
                else:
                    c.setvalue("Closed")
            else:
                if m.olpin.value() == 1:
                    print("open limit detected")
                if m.clpin.value() == 1:
                    print("closed limit detected")
                c.setvalue('Error')
        if door.triggered:
            door.triggered = False
            setlight(brightness.value)
            start_nl = time.time()
            nightlight = True
        if not lights.state and nightlight and (time.time() - start_nl  > nldelay):
            setlight(0)
            nightlight = False
        if lights.triggered or brightness.triggered:
            if lights.state:
                setlight(brightness.value)
                nightlight = False
            if not lights.state:
                setlight(0)
            lights.triggered = False
            brightness.triggered = False

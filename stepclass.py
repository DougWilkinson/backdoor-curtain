from machine import Pin,PWM,Timer
import time

class Stepper:

    def __init__(self, pos=0, dirpin=15, steppin=13, enablepin=12, olpin=5, clpin=14, period=1250,  ratio=20):
        self.dirpin = Pin(dirpin, Pin.OUT)
        self.steppin = Pin(steppin, Pin.OUT)
        self.enablepin = Pin(enablepin, Pin.OUT)
        self.enablepin.value(1)
        self.olpin = Pin(olpin, Pin.IN, Pin.PULL_UP)
        self.clpin = Pin(clpin, Pin.IN, Pin.PULL_UP)
        self.ratio = ratio
        self.setpos()
        self.delay = period
        #kpos = True if we are confident ucpos is true
        self.kpos = False
        
        #current micro position
        self.dir = 0

        #self.timer = Timer(-1)
        #self.timer.init(period=period, mode=Timer.PERIODIC, callback=self.move)
        
        self.triggered = False

    def setpos(self, pos=0):
        self.kpos = False
        self.pos = pos
        self.npos = pos
        self.upos = pos * self.ratio
        self.ucpos = self.upos
        self.unpos = self.upos
        self.kpos = True
        self.triggered = True

    def set(self, pos=None):
        if pos == None:
            self.enablepin.value(1)
            self.unpos = self.ucpos
            return
        if not self.kpos or pos == self.pos:
            print("Position not known or already set to position")
            return
        self.enablepin.value(0)
        self.npos = pos
        self.unpos = pos * self.ratio
        self.move()

    def step(self):
        self.steppin.value(1)
        pass
        self.steppin.value(0)
    
    def move(self):
        if self.dir == 0:
            if self.unpos > self.ucpos:
                self.dir = 1
                self.dirpin.value(1)
            else:
                self.dir = -1
                self.dirpin.value(0)
        while (self.unpos != self.ucpos) and (self.olpin.value() == 0 and self.clpin.value() == 0):
            self.step()
            self.ucpos += self.dir
            time.sleep_us(self.delay)
        self.enablepin.value(1)
        self.triggered = True
        self.dir = 0
        if self.olpin.value() == 1 or self.clpin.value() == 1:
            #limit detected
            self.kpos = False
        if self.unpos == self.ucpos:
            self.pos = self.npos
            self.upos = self.unpos

    def home(self):
        self.enablepin.value(0)
        self.kpos = False
        t = time.time()
        self.dirpin.value(0)
        while self.clpin.value() == 0:
            self.step()
            time.sleep_ms(3)
        print("Time to home: ", time.time()-t)
        self.dirpin.value(1)
        for i in range(100):
            self.step()
            time.sleep_ms(3)
        self.enablepin.value(1)
        if self.clpin.value() == 1:
            print("Can't home, check limit switches")
            return False
        self.setpos()
        return True


import time
from os import listdir

import serial
import usbtmc

def get_serial_dev():
    dev_path="/dev/serial/by-id/"
    try:
        retval = [dev_path+f for f in listdir(dev_path)]
        return retval
    except:
        return []

# E-Load (CC mode)
class Choma6310:
    def __init__(self, ch=1): 
        self.instr = usbtmc.Instrument(0x0a69,0x084a)
        self.instr.write("CHAN {}\n".format(ch))
        #print self.instr.ask("CHAN?\n")
        self.instr.write("CHAN:ACT ON\n")
        self.instr.write(":MODE CCH\n")
        print "Found: {}".format(self.idn())
        
    def idn(self):
        return self.instr.ask("*IDN?\n")

    def enable(self):
        self.instr.write("LOAD:STAT ON\n")
        #print self.instr.ask(":LOAD:STAT?\n")

    def disable(self):
        self.instr.write(":LOAD:STAT OFF\n")
        #print self.instr.ask(":LOAD:STAT?\n")

    def get_curr(self):
        return float(self.instr.ask(":MEAS:CURR?\n"))

    def get_volt(self):
        return float(self.instr.ask(":MEAS:VOLT?\n"))

    def set_curr(self, curr):
        self.instr.write(":CURR:STAT:L1 {}\n".format(curr))
        #print self.instr.ask(":CURR:STAT:L1?\n")
        
if False:
    load=Choma6310()
    print load.idn()
    load.enable()
    load.set_curr(1.23)
    time.sleep(1)
    print "voltage: {}V".format(load.get_volt())
    print "current: {}A".format(load.get_curr())
    load.disable()
    

# Digital Meter
class Prova803:
    def __init__(self): 
        self.instr = serial.Serial("/dev/serial/by-id/usb-Silicon_Labs_CP2102_USB_to_UART_Bridge_Controller_0001-if00-port0", 9600, timeout=0.5)
        time.sleep(0.5)
        self.instr.write("?")
        time.sleep(1)
        
        v = self.instr.readline().rstrip().split(' ')
#        if v[0][:2]=="CH":
#            print "Found: Prova803"
#        else:
#            print "[ERROR] Prova 803 no response!"
#            raise

    # Get voltage, ch='1' or '2' for CH1 or CH2
    def get_volt(self, ch):
        for i in range(5):
            time.sleep(1)
            v = self.instr.readline().rstrip().split(' ')
            if v[0]=="CH{}".format(ch):
                if v[2]=="OL":
                    return -9999
                else:
                    if v[3]=="mV":
                        return float(v[2])*0.001
                    else:
                        return float(v[2])
            
    def ask(self, cmd):
        self.write(cmd)
        return self.instr.readline()

    def write(self, cmd):
        self.instr.write(cmd+'\n')
 
    def close(self):
        self.instr.close()

if False:
    dm=Prova803()
    print "CH1: {}V".format(dm.get_volt(1))
    print "CH2: {}V".format(dm.get_volt(2))

# Power Supply
class GPD43:
    def __init__(self): 
        self.instr = serial.Serial("/dev/serial/by-id/usb-FTDI_FT232R_USB_UART_A602R300-if00-port0", 9600, timeout=0.5)
        print "Found: {}".format(self.idn())
        
    def idn(self):
        return self.ask("*IDN?").rstrip()

    def enable(self):
        self.write("OUT1")

    def disable(self):
        self.write("OUT0")

    def set_curr(self, ch, curr):
        self.write("ISET{}:{}".format(ch,curr))

    def set_volt(self, ch, volt):
        self.write("VSET{}:{}".format(ch,volt))

    def get_curr(self, ch):
        return float(self.ask("IOUT{}?".format(ch)).rstrip()[:-1])

    def ask(self,cmd):
        self.write(cmd)
        return self.instr.readline()

    def write(self, cmd):
        self.instr.write(cmd+'\n')
        
if False:
    power = GPD43()
    print GPD43.idn()
    power.set_curr(1,1.10)
    power.set_curr(2,2.2)
    for i in range(4):
        print power.get_curr(i+1)


if __name__ == "__main__":
    None

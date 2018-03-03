from time import sleep
import numpy as np
import serial
import usbtmc
from matplotlib import pyplot as plt
from myinstruments_tpe101 import Choma6310, Prova803, GPD43

DUT="LUX_EVT3_Laird_MGAF10151R5M-10_1.5uH"
VINs = [5, 9, 12, 15, 20]
VOUT = 8
IIN_MAX = 2.8
IOUT_MAX=5
power = GPD43()
meter = Prova803()
load = Choma6310()

# Start testing...
for VIN in VINs:
    filename = "{}_Vin{}V_Vout{}V".format(DUT,VIN,VOUT)
    print "Set VIN to {}V".format(VIN)
    IOUT = np.linspace(0.1,IOUT_MAX,num=31)

    power.set_volt(1,VIN)
    power.set_curr(1,3)
    power.enable()
    load.set_curr(0)
    load.enable()

    plt.xlabel('IOUT (A)')
    plt.ylabel('EFFICIENCY (%)')
    plt.grid()
    plt.ion()

    with open("{}.csv".format(filename),'w') as f:
        f.write("Vin_V,Vout_V,Iin_A,Iout_A,Pin_W,Pout_W,Eff_%\n")
        for i in IOUT:
            load.set_curr(i)
            sleep(3)

            for t in range(10):
                iin = power.get_curr(1)
                sleep(0.1)
                if iin - power.get_curr(1)<0.01:
                    break
                else:
                    sleep(0.5*t)

            for t in range(10):
                iout = load.get_curr()
                sleep(0.1)
                if iout - load.get_curr()<0.01:
                   break
                else:
                    sleep(0.5*t)
            
            
            meter = Prova803()
            vin = meter.get_volt(1)
            vout = meter.get_volt(2)
            meter.close()

            pin = vin*iin
            pout = vout*iout
            loss = pin-pout
            eff = pout/pin*100

            f.write("{},{},{},{},{},{},{}\n".format(vin,vout,iin,iout,pin,pout,eff))

            print "IOUT={}A: vin={}V, iin={}A, vout={}V, iout={}A".format(i,vin,iin,vout,iout)
            print "   >> pin={:.2f}W, pout={:.2f}W, loss={:.2f}W, eff={:.2f}%".format(pin,pout,loss,eff) 
            plt.scatter(iout,eff)
            plt.pause(0.1)
        
            if iin>=IIN_MAX:
                break

    load.set_curr(0)
    load.disable()
    plt.axis([0,i,70,100])
    plt.ioff()
    plt.close()
    sleep(10)

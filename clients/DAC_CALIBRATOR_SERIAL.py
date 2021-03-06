import sys
from PyQt4 import QtGui
from PyQt4 import QtCore,uic
from qtui.QDACCalibrator import QDACCalibrator
import time
import numpy as np
import matplotlib.pyplot as plt
import datetime

class DAC_CALIBRATOR(QDACCalibrator):
    def __init__(self, cxn, parent=None):
        self.dacserver = cxn.cctdac
        self.dmmserver = cxn.keithley_2100_dmm
        self.datavault = cxn.data_vault
        self.r = cxn.registry

        QDACCalibrator.__init__(self, parent)

        self.clicked = False # state of the "Calibrate" button

        # Connect functions
        # self.spinPower.valueChanged.connect(self.powerChanged)
        self.start.released.connect(self.buttonClicked)
    
    # This is where the magic happens
    def calib(self):
        
        #stepsize = 0b101010101

        stepsize = 1000

        #self.digVoltages = range(0, 2**16, stepsize) # digital voltages we're going to iterate over
        self.digVoltages = range(0, 2**16, stepsize)
        self.anaVoltages = [] # corresponding analog voltages in volts
        self.dacserver.set_individual_digital_voltages([(int(self.channelToCalib), 0)])
        #time.sleep(1)
        for dv in self.digVoltages: # iterate over digital voltages

            self.dacserver.set_individual_digital_voltages([(int(self.channelToCalib), dv)]) 

            time.sleep(1)
            
            av = self.dmmserver.get_dc_volts()

            time.sleep(1)
            #av = 0

            self.anaVoltages.append(av)
            print dv, "; ", av
        
        plt.figure(1)
        plt.plot(self.digVoltages, self.anaVoltages, 'ro')
        plt.show()

        fit = np.polyfit(self.digVoltages, self.anaVoltages, 3) # fit to a second order polynomial
        
        print fit
    
        # Save the raw data to the datavault
        now = time.ctime()
        self.datavault.cd( ( ['DACCalibrations', self.channelToCalib], True ) )
        self.datavault.new( (now, [('Digital voltage', 'num')], [('Volts','Analog Voltage','v')]) )
        self.datavault.add( np.array([self.digVoltages, self.anaVoltages]).transpose().tolist() )

        # Update the registry with the new calibration
        self.r.cd( ( ['Calibrations', self.channelToCalib], True ) )
        self.r.set( ( 'y_int', fit[2] ) )
        self.r.set( ( 'slope', fit[1] ) )
        self.r.cd( ( [''] ))

        return fit

    def buttonClicked(self):
        self.channelToCalib = str(self.port.text())
        print self.channelToCalib
        
        self.clicked = True
        fit = self.calib() # Now calibrate

        #fit = [ -6.87774335e-18, 6.05469803e-13, 3.05235677e-04, -1.00067658e+01]
        #fit = [ -7.59798451e-18 ,  7.42121115e-13 ,  3.05226445e-04 , -1.00065850e+01]
        fit = [ -6.33002825e-18 ,  5.78910501e-13  , 3.05234325e-04,  -1.00066765e+01]
        self.results.setText('RESULTS')
        self.y_int.setText('Intercept: ' + str(fit[2]))
        self.slope.setText('Slope: ' + str(fit[1]))
        #self.order2.setText('Nonlinearity: ' + str(fit[0]))
        
        fitvals = np.array([ v*v*v*fit[0] + v*v*fit[1] + v * fit[2] + fit[3] for v in self.digVoltages])
        diffs = fitvals - self.anaVoltages
        
        m = 20./(2**16 - 1)
        b = -10
        idealVals = np.array([m*v + b for v in self.digVoltages])
        uncalDiffs = idealVals - self.anaVoltages
        
        print "MAX DEVIATION: ", 1000*max(abs(diffs)), " mV"
        plt.figure(2)
        plt.plot(self.digVoltages, 1000*(diffs))
        plt.title('Actual deviation from fit (mV)')
        plt.figure(3)
        plt.plot(self.digVoltages, 1000*(uncalDiffs) )
        plt.title('Deviation from nominal settings (mV)')
        plt.show()
        
        print "MAX DEV FROM NOMINAL: ", 1000*max(abs(uncalDiffs)), " mV"

if __name__=="__main__":
    import labrad
    cxn = labrad.connect()
    dacserver = cxn.cctdac
    dmmserver = cxn.keithley_2100_dmm
    datavault = cxn.data_vault
    registry = cxn.registry
    dmmserver.select_device('GPIB Bus - USB0::0x05E6::0x2100::1243106')
    app = QtGui.QApplication(sys.argv)
    icon = DAC_CALIBRATOR(cxn)
    icon.show()
    app.exec_()

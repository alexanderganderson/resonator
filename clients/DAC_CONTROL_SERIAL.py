import sys
import os
from PyQt4 import QtGui
from PyQt4 import QtCore,uic
from numpy import *
from qtui.QDACControl import QDACControl
from qtui.QCustomLevelSpin import QCustomLevelSpin
from qtui.QCustomSliderSpin import QCustomSliderSpin
from qtui.QCustomSpinBox import QCustomSpinBox
from twisted.internet.defer import inlineCallbacks, returnValue

UpdateTime = 100 # ms
SIGNALID = 270836
SIGNALID2 = 270835

class MULTIPOLE_CONTROL(QtGui.QWidget):
    def __init__(self, reactor, parent=None):
        super(MULTIPOLE_CONTROL, self).__init__(parent)
        self.reactor = reactor
        self.connect()
        
        
    @inlineCallbacks    
    def makeGUI(self):
        self.numWells = yield self.dacserver.return_number_wells()    
        self.ctrlLayout = QtGui.QGridLayout()
        self.controlLabels = ['Ex1','Ey1','Ez1','U1','U2','U3','U4','U5', 'Ex2', 'Ey2', 'Ez2', 'V1', 'V2', 'V3', 'V4', 'V5']
     
        self.controls = {}
        self.controls['Ex1'] = QCustomSpinBox('Ex1', (-2.,2.))
        self.controls['Ey1'] = QCustomSpinBox('Ey1', (-2.,2.))
        self.controls['Ez1'] = QCustomSpinBox('Ez1', (-2.,2.))
        self.controls['U1'] = QCustomSpinBox('U1', (-20.,20.))
        self.controls['U2'] = QCustomSpinBox('U2', (0.,20.))
        self.controls['U3'] = QCustomSpinBox('U3', (-10.,10.))
        self.controls['U4'] = QCustomSpinBox('U4', (-10.,10.))
        self.controls['U5'] = QCustomSpinBox('U5', (-10.,10.))
        self.controls['Ex2'] = QCustomSpinBox('Ex2', (-2.,2.))
        self.controls['Ey2'] = QCustomSpinBox('Ey2', (-2.,2.))
        self.controls['Ez2'] = QCustomSpinBox('Ez2', (-2.,2.))
        self.controls['V1'] = QCustomSpinBox('V1', (-20.,20.))
        self.controls['V2'] = QCustomSpinBox('V2', (0.,20.))
        self.controls['V3'] = QCustomSpinBox('V3', (-10.,10.))
        self.controls['V4'] = QCustomSpinBox('V4', (-10.,10.))
        self.controls['V5'] = QCustomSpinBox('V5', (-10.,10.)) 
        self.multipoleFileSelectButton2 = QtGui.QPushButton('MovTo Cfile')
        self.moveButton = QtGui.QPushButton('Move!')
        self.controls['slave'] = QtGui.QCheckBox('slave') 
        
        self.multipoleValues = {}
        for k in self.controlLabels:
            self.multipoleValues[k]=0.0

        if self.numWells == 1:
            self.ctrlLayout.addWidget(self.controls['Ex1'],0,0)
            self.ctrlLayout.addWidget(self.controls['Ey1'],1,0)
            self.ctrlLayout.addWidget(self.controls['Ez1'],2,0)
            self.ctrlLayout.addWidget(self.controls['U1'],0,1)
            self.ctrlLayout.addWidget(self.controls['U2'],1,1)
            self.ctrlLayout.addWidget(self.controls['U3'],2,1)
            self.ctrlLayout.addWidget(self.controls['U4'],3,1)
            self.ctrlLayout.addWidget(self.controls['U5'],4,1)
        else:
            self.ctrlLayout.addWidget(self.controls['Ex1'],0,0)
            self.ctrlLayout.addWidget(self.controls['Ey1'],1,0)
            self.ctrlLayout.addWidget(self.controls['Ez1'],2,0)
            self.ctrlLayout.addWidget(self.controls['U1'],0,1)
            self.ctrlLayout.addWidget(self.controls['U2'],1,1)
            self.ctrlLayout.addWidget(self.controls['U3'],2,1)
            self.ctrlLayout.addWidget(self.controls['U4'],3,1)
            self.ctrlLayout.addWidget(self.controls['U5'],4,1)
            self.ctrlLayout.addWidget(self.controls['Ex2'],0,2)
            self.ctrlLayout.addWidget(self.controls['Ey2'],1,2)
            self.ctrlLayout.addWidget(self.controls['Ez2'],2,2)
            self.ctrlLayout.addWidget(self.controls['V1'],0,3)
            self.ctrlLayout.addWidget(self.controls['V2'],1,3)
            self.ctrlLayout.addWidget(self.controls['V3'],2,3)
            self.ctrlLayout.addWidget(self.controls['V4'],3,3)
            self.ctrlLayout.addWidget(self.controls['V5'],4,3)	
            self.ctrlLayout.addWidget(self.multipoleFileSelectButton2,5,2)
            self.ctrlLayout.addWidget(self.moveButton,5,3)
            self.ctrlLayout.addWidget(self.controls['slave'], 4, 2)       	            
        self.multipoleFileSelectButton = QtGui.QPushButton('C File')
        self.ctrlLayout.addWidget(self.multipoleFileSelectButton,5,0)

        self.inputUpdated = False
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.sendToServer)
        self.timer.start(UpdateTime)       
        for k in self.controlLabels:
            self.controls[k].onNewValues.connect(self.inputHasUpdated)
            
        self.multipoleFileSelectButton.released.connect(self.selectCFile)
        self.multipoleFileSelectButton2.released.connect(self.selectNextCFile)
        self.moveButton.released.connect(self.moveToNextPosition)
        
        self.setLayout(self.ctrlLayout)
        yield self.followSignal(0, 0)
        
    @inlineCallbacks
    def updateGUI(self):
        self.numWells = yield self.dacserver.return_number_wells()
        print "num. wells: " + str(self.numWells)           
        if self.numWells == 2:
            try:
                self.ctrlLayout.addWidget(self.controls['Ex2'],0,2)
                self.ctrlLayout.addWidget(self.controls['Ey2'],1,2)
                self.ctrlLayout.addWidget(self.controls['Ez2'],2,2)
                self.ctrlLayout.addWidget(self.controls['V1'],0,3)
                self.ctrlLayout.addWidget(self.controls['V2'],1,3)
                self.ctrlLayout.addWidget(self.controls['V3'],2,3)
                self.ctrlLayout.addWidget(self.controls['V4'],3,3)
                self.ctrlLayout.addWidget(self.controls['V5'],4,3)
                self.ctrlLayout.addWidget(self.multipoleFileSelectButton2,5,2)
                self.ctrlLayout.addWidget(self.moveButton,5,3) 
                self.ctrlLayout.addWidget(self.controls['slave'], 4, 2)
            except: print "previous Cfile also had 2 wells"
        else:
            try:
                self.ctrlLayout.removeWidget(self.controls['Ex2'])
                self.ctrlLayout.removeWidget(self.controls['Ey2'])
                self.ctrlLayout.removeWidget(self.controls['Ez2'])
                self.ctrlLayout.removeWidget(self.controls['V1'])
                self.ctrlLayout.removeWidget(self.controls['V2'])
                self.ctrlLayout.removeWidget(self.controls['V3'])
                self.ctrlLayout.removeWidget(self.controls['V4'])
                self.ctrlLayout.removeWidget(self.controls['V5'])	
                self.ctrlLayout.removeWidget(self.multipoleFileSelectButton2)
                self.ctrlLayout.removeWidget(self.moveButton)
                self.ctrlLayout.removeWidget(self.controls['slave'])
            except: print "previous Cfile also had one well"
        yield self.followSignal(0, 0)
	
        
    @inlineCallbacks
    def connect(self):
        from labrad.wrappers import connectAsync
        from labrad.types import Error
        self.cxn = yield connectAsync()
        self.dacserver = yield self.cxn.cctdac
        yield self.setupListeners()
        yield self.makeGUI()
        
    def inputHasUpdated(self):
        self.inputUpdated = True
        if self.controls['slave'].isChecked():
            self.controls['Ex2'].spinLevel.setValue(round(self.controls['Ex1'].spinLevel.value(), 3))
            self.controls['Ey2'].spinLevel.setValue(round(self.controls['Ey1'].spinLevel.value(), 3))
            self.controls['Ez2'].spinLevel.setValue(round(self.controls['Ez1'].spinLevel.value(), 3))
            self.controls['V1'].spinLevel.setValue(round(self.controls['U1'].spinLevel.value(), 3))
            self.controls['V2'].spinLevel.setValue(round(self.controls['U2'].spinLevel.value(), 3))
            self.controls['V3'].spinLevel.setValue(round(self.controls['U3'].spinLevel.value(), 3))
            self.controls['V4'].spinLevel.setValue(round(self.controls['U4'].spinLevel.value(), 3))
            self.controls['V5'].spinLevel.setValue(round(self.controls['U5'].spinLevel.value(), 3))           
        for k in self.controlLabels:
            self.multipoleValues[k] = round(self.controls[k].spinLevel.value(), 3)

                    
        
    def sendToServer(self):
        if self.inputUpdated:
            print "sending to server ", self.multipoleValues
            self.dacserver.set_multipole_voltages(self.multipoleValues.items())
            self.inputUpdated = False
            #yield self.followSignal(0, 0)
    
    @inlineCallbacks        
    def selectCFile(self):
        fn = QtGui.QFileDialog().getOpenFileName()
        yield self.dacserver.set_multipole_control_file(str(fn))
        self.updateGUI()
        self.inputHasUpdated()
        
    @inlineCallbacks        
    def selectNextCFile(self):
        fn = QtGui.QFileDialog().getOpenFileName()
        yield self.dacserver.set_second_multipole_control_file(str(fn))
    
    @inlineCallbacks    
    def moveToNextPosition(self):
        yield self.dacserver.shuttle_ion(0, 10)
        
    @inlineCallbacks    
    def setupListeners(self):
        yield self.dacserver.signal__ports_updated(SIGNALID)
        yield self.dacserver.addListener(listener = self.followSignal, source = None, ID = SIGNALID) 
        
    @inlineCallbacks
    def followSignal(self, x, s):
	try:
	    multipoles = yield self.dacserver.get_multipole_voltages()
	    for (k,v) in multipoles:
		self.controls[k].setValueNoSignal(v)
	except: print '...'
    
    def closeEvent(self, x):
        self.reactor.stop()  
        
        #self.reactor = reactor
        #self.connect()
        
        #ctrlLayout = QtGui.QGridLayout() 
               
        #self.controlLabels = ['Ex','Ey','Ez','U1','U2','U3','U4','U5']
        
        #self.controls = {}
        #self.controls['Ex'] = QCustomLevelSpin('Ex', (-2.,2.))
        #self.controls['Ey'] = QCustomLevelSpin('Ey', (-2.,2.))
        #self.controls['Ez'] = QCustomLevelSpin('Ez', (-2.,2.))
        #self.controls['U1'] = QCustomLevelSpin('U1', (-20.,20.))
        #self.controls['U2'] = QCustomLevelSpin('U2', (0.,20.))
        #self.controls['U3'] = QCustomLevelSpin('U3', (-10.,10.))
        #self.controls['U4'] = QCustomLevelSpin('U4', (-10.,10.))
        #self.controls['U5'] = QCustomLevelSpin('U5', (-10.,10.))
        
        #self.multipoleValues = {}
        #for k in self.controlLabels:
            #self.multipoleValues[k]=0.0

        #ctrlLayout.addWidget(self.controls['Ex'],0,0)
        #ctrlLayout.addWidget(self.controls['Ey'],1,0)
        #ctrlLayout.addWidget(self.controls['Ez'],2,0)
        #ctrlLayout.addWidget(self.controls['U1'],0,1)
        #ctrlLayout.addWidget(self.controls['U2'],1,1)
        #ctrlLayout.addWidget(self.controls['U3'],2,1)
        #ctrlLayout.addWidget(self.controls['U4'],3,1)
        #ctrlLayout.addWidget(self.controls['U5'],4,1)
        
        #self.multipoleFileSelectButton = QtGui.QPushButton('Set C File')
        #ctrlLayout.addWidget(self.multipoleFileSelectButton,4,0)

        #self.inputUpdated = False
        #self.timer = QtCore.QTimer(self)
        #self.timer.timeout.connect(self.sendToServer)
        #self.timer.start(UpdateTime)
        
        #for k in self.controlLabels:
            #self.controls[k].onNewValues.connect(self.inputHasUpdated)
            
        #self.multipoleFileSelectButton.released.connect(self.selectCFile)
        
        #self.setLayout(ctrlLayout)
        
        
        
    #@inlineCallbacks
    #def connect(self):
        #from labrad.wrappers import connectAsync
        #from labrad.types import Error
        #self.cxn = yield connectAsync()
        #self.dacserver = yield self.cxn.cctdac
        #yield self.setupListeners()
        #yield self.followSignal(0, 0)
        
    #def inputHasUpdated(self):
        #self.inputUpdated = True
        #print "in inputHasUpdated"
        #for k in self.controlLabels:
            #self.multipoleValues[k] = round(self.controls[k].spinLevel.value(), 3)
        
    #def sendToServer(self):
        #if self.inputUpdated:
            #print "sending to server ", self.multipoleValues
            #print 'why?'
            #self.dacserver.set_multipole_voltages(self.multipoleValues.items())
            #print "set the values"
            #self.inputUpdated = False
            
    #def selectCFile(self):
        #fn = QtGui.QFileDialog().getOpenFileName()
        #self.dacserver.set_multipole_control_file(str(fn))
        
    #@inlineCallbacks    
    #def setupListeners(self):
        #yield self.dacserver.signal__ports_updated(SIGNALID)
        #yield self.dacserver.addListener(listener = self.followSignal, source = None, ID = SIGNALID) #cxzv 
    
    #@inlineCallbacks
    #def followSignal(self, x, s):
	#try:
	    #multipoles = yield self.dacserver.get_multipole_voltages()
	    #for (k,v) in multipoles:
		#self.controls[k].setValueNoSignal(v)
	#except: print '...'
    
    #def closeEvent(self, x):
        #self.reactor.stop()  
        

class CHANNEL_CONTROL (QtGui.QWidget):
    def __init__(self, reactor, parent=None):
        super(CHANNEL_CONTROL, self).__init__(parent)
        self.reactor = reactor
        self.connect()
        
        ctrlLayout = QtGui.QGridLayout()
        
        self.controlLabels = ['1','2','3','4','5','6','7','8','9','10','11','12','13','14','15','16','17','CNT']
        
        self.labelToNumber = {}
        for k in self.controlLabels:
            if k == 'CNT':
                self.labelToNumber[k]=18
            else:
                self.labelToNumber[k]=int(k)

        self.controls = {}
        for label in self.controlLabels:
            self.controls[label] = QCustomLevelSpin(label, (-10,10))
              
        self.channelValues = {}
        for k in self.controlLabels:
            self.channelValues[k]=0.0
        
        self.oldValues = {}
        for k in self.controlLabels:
            self.oldValues[k]=0.0
       
        ctrlLayout.addWidget(self.controls['1'],0,0)
        ctrlLayout.addWidget(self.controls['2'],1,0)
        ctrlLayout.addWidget(self.controls['3'],2,0)
        ctrlLayout.addWidget(self.controls['4'],3,0)
        ctrlLayout.addWidget(self.controls['5'],4,0)
        ctrlLayout.addWidget(self.controls['6'],5,0)
        ctrlLayout.addWidget(self.controls['7'],0,1)
        ctrlLayout.addWidget(self.controls['8'],1,1)
        ctrlLayout.addWidget(self.controls['9'],2,1)
        ctrlLayout.addWidget(self.controls['10'],3,1)
        ctrlLayout.addWidget(self.controls['11'],4,1)
        ctrlLayout.addWidget(self.controls['12'],5,1)
        ctrlLayout.addWidget(self.controls['13'],0,2)
        ctrlLayout.addWidget(self.controls['14'],1,2)
        ctrlLayout.addWidget(self.controls['15'],2,2)
        ctrlLayout.addWidget(self.controls['16'],3,2)
        ctrlLayout.addWidget(self.controls['17'],4,2)
        ctrlLayout.addWidget(self.controls['CNT'],5,2)
                
        self.inputUpdated = False                
        self.timer = QtCore.QTimer(self)        
        self.timer.timeout.connect(self.sendToServer)
        self.timer.start(UpdateTime)
        
        for k in self.controlLabels:
            self.controls[k].onNewValues.connect(self.inputHasUpdated2(k))
                   
        self.setLayout(ctrlLayout)
        

            
    @inlineCallbacks
    def connect(self):
        from labrad.wrappers import connectAsync
        from labrad.types import Error
        self.cxn = yield connectAsync()
        self.dacserver = yield self.cxn.cctdac
        yield self.setupListeners()

    def inputHasUpdated2(self,name):
        def iu():
            self.inputUpdated = True
            print "in inputHasUpdated"
            self.oldValues = self.channelValues.copy() 
            for k in self.controlLabels:
                self.channelValues[k] = round(self.controls[k].spinLevel.value(), 3)
            self.changedChannel = name
            print "Channel changed: " + name
        return iu

    def sendToServer(self):
        if self.inputUpdated:
            c = self.changedChannel
            print 'hi'
            self.dacserver.set_individual_analog_voltages([(self.labelToNumber[c], self.channelValues[c])])
            print [(self.labelToNumber[c], self.channelValues[c])]
            print "set the values"
            self.inputUpdated = False
            
    @inlineCallbacks    
    def setupListeners(self):
        yield self.dacserver.signal__ports_updated(SIGNALID2)
        yield self.dacserver.addListener(listener = self.followSignal, source = None, ID = SIGNALID2)
    
    @inlineCallbacks
    def followSignal(self, x, s):
        av = yield self.dacserver.get_analog_voltages()
        for (c, v) in zip(self.controlLabels, av):
            self.controls[c].setValueNoSignal(v)

    def closeEvent(self, x):
        self.reactor.stop()        

class CHANNEL_MONITOR(QtGui.QWidget):
    """
    A widget to monitor each of the DAC channel voltages.
    """
    
    def __init__(self, reactor, Nelectrodes, parent=None):
        super(CHANNEL_MONITOR, self).__init__(parent)
        self.reactor = reactor
        self.connect()
        
        self.Nelectrodes = Nelectrodes
        self.electrodes = [QtGui.QLCDNumber() for i in range(self.Nelectrodes)]
        
        elecLayout = QtGui.QGridLayout()
                
        for j in range(self.Nelectrodes/2):
            elecLayout.addWidget(QtGui.QLabel(str(j+1)),j,0)
            elecLayout.addWidget(self.electrodes[j],j,1)
            #elecLayout.setColumnStretch(1, 1)
        for j in range(self.Nelectrodes/2,self.Nelectrodes-1):
            elecLayout.addWidget(QtGui.QLabel(str(j+1)), j - self.Nelectrodes/2,2)
            elecLayout.addWidget(self.electrodes[j],j - self.Nelectrodes/2,3)
            #elecLayout.setColumnStretch(3, 1)
            
        for i in range(4):
	    elecLayout.setColumnStretch(i, 1)
	  

        elecLayout.addWidget(QtGui.QLabel('CNT'),int(round(self.Nelectrodes/2.))-1,2)
        elecLayout.addWidget(self.electrodes[self.Nelectrodes-1], int(round(self.Nelectrodes/2.)) - 1,3) 

        self.setLayout(elecLayout)      
        
    @inlineCallbacks
    def connect(self):
        from labrad.wrappers import connectAsync
        from labrad.types import Error
        self.cxn = yield connectAsync()
        self.dacserver = yield self.cxn.cctdac
        yield self.setupListeners()
        yield self.followSignal(0, 0)
        
    @inlineCallbacks    
    def setupListeners(self):
        yield self.dacserver.signal__ports_updated(SIGNALID2)
        yield self.dacserver.addListener(listener = self.followSignal, source = None, ID = SIGNALID2)
    
    @inlineCallbacks
    def followSignal(self, x, s):
        print "CHMON followSignal"
        av = yield self.dacserver.get_analog_voltages()
        for (e, v) in zip(self.electrodes, av):
            e.display(float(v))
        for (i, v) in zip(range(self.Nelectrodes), av):
            if math.fabs(v) > 10:
                self.electrodes[i].setStyleSheet("QWidget {background-color: orange }")
                self.electrodes[i].setAutoFillBackground(True)
            if math.fabs(v) < 10:
                self.electrodes[i].setStyleSheet("QWidget {background-color:  }")
                self.electrodes[i].setAutoFillBackground(False)      
       
    def closeEvent(self, x):
        self.reactor.stop()

class DAC_Control(QtGui.QMainWindow):
    def __init__(self, reactor, parent=None):
        super(DAC_Control, self).__init__(parent)
        self.reactor = reactor
        self.Nelectrodes = 18
        channelControlTab = self.buildChannelControlTab()        
        multipoleControlTab = self.buildMultipoleControlTab()
        scanControlTab = self.buildScanControlTab()
        tabWidget = QtGui.QTabWidget()
        tabWidget.addTab(multipoleControlTab,'&Multipoles')
        tabWidget.addTab(channelControlTab, '&Channels')
        tabWidget.addTab(scanControlTab, '&Scans')
        self.setCentralWidget(tabWidget)
        self.setWindowTitle('DAC Control')
    
    def buildMultipoleControlTab(self):
        widget = QtGui.QWidget()
        gridLayout = QtGui.QGridLayout()
        gridLayout.addWidget(CHANNEL_MONITOR(self.reactor, self.Nelectrodes),0,0)
        gridLayout.addWidget(MULTIPOLE_CONTROL(self.reactor),0,1)
        widget.setLayout(gridLayout)
        return widget

    def buildChannelControlTab(self):
        widget = QtGui.QWidget()
        gridLayout = QtGui.QGridLayout()
        gridLayout.addWidget(CHANNEL_CONTROL(self.reactor),0,0)
        widget.setLayout(gridLayout)
        return widget
    
    def buildScanControlTab(self):
        from SCAN_Ex_and_TICKLE import Scan_Control_Ex_and_Tickle
        from SCAN_Ey_and_TICKLE import Scan_Control_Ey_and_Tickle
        widget = QtGui.QWidget()
        gridLayout = QtGui.QGridLayout()
        gridLayout.addWidget(Scan_Control_Ex_and_Tickle(self.reactor), 0, 0)
        gridLayout.addWidget(Scan_Control_Ey_and_Tickle(self.reactor), 0, 1)
        widget.setLayout(gridLayout)
        return widget
	
    def closeEvent(self, x):
        self.reactor.stop()  

if __name__ == "__main__":
    a = QtGui.QApplication( [] )
    import qt4reactor
    qt4reactor.install()
    from twisted.internet import reactor
    DAC_Control = DAC_Control(reactor)
    DAC_Control.show()
    reactor.run()

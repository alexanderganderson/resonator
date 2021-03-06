from PyQt4 import QtGui, QtCore
from twisted.internet.defer import inlineCallbacks, returnValue, Deferred

class ResonatorGUI(QtGui.QMainWindow):
    def __init__(self, reactor, parent=None):
        super(ResonatorGUI, self).__init__(parent)
        self.reactor = reactor
        lightControlTab = self.makeLightWidget(reactor)
        voltageControlTab = self.makeVoltageWidget(reactor)      
        self.tabWidget = QtGui.QTabWidget()
        self.tabWidget.addTab(voltageControlTab,'&Trap Voltages')
        self.tabWidget.addTab(lightControlTab,'&Laser Room')
        self.createGrapherTab()
        
        scriptControl = self.makeScriptControl(reactor)
        gridLayout = QtGui.QGridLayout()
        gridLayout.addWidget(scriptControl, 0, 0, 1, 1)
        gridLayout.addWidget(self.tabWidget, 0, 1, 1, 3)
        centralWidget = QtGui.QWidget()
        centralWidget.setLayout(gridLayout)
        self.setCentralWidget(centralWidget)
        self.setWindowTitle('Resonator GUI')

        
    def makeScriptControl(self, reactor):
        from SCRIPT_CONTROL.scriptcontrol import ScriptControl
        self.sc = ScriptControl(reactor, self)
        self.sc, self.experimentParametersWidget = self.sc.getWidgets()
        self.createExperimentParametersTab()
        return self.sc
        
    def createExperimentParametersTab(self):
        self.tabWidget.addTab(self.experimentParametersWidget, '&Experiment Parameters')

        
    @inlineCallbacks
    def createGrapherTab(self):
        grapher = yield self.makeGrapherWidget(reactor)
        self.tabWidget.addTab(grapher, '&Grapher')
    
    @inlineCallbacks
    def makeGrapherWidget(self, reactor):
        widget = QtGui.QWidget()
        from pygrapherlive.connections import CONNECTIONS
        vboxlayout = QtGui.QVBoxLayout()
        Connections = CONNECTIONS(reactor)
        @inlineCallbacks
        def widgetReady():
            window = yield Connections.introWindow
            vboxlayout.addWidget(window)
            widget.setLayout(vboxlayout)
        yield Connections.communicate.connectionReady.connect(widgetReady)
        returnValue(widget)

    def makeLightWidget(self, reactor):        
        from common.clients.CAVITY_CONTROL import cavityWidget
        from common.clients.multiplexer.MULTIPLEXER_CONTROL import multiplexerWidget
        widget = QtGui.QWidget()
        gridLayout = QtGui.QGridLayout()
        gridLayout.addWidget(multiplexerWidget(reactor),0,1)
        gridLayout.addWidget(cavityWidget(reactor),0,0)
        widget.setLayout(gridLayout)
        return widget
        
    def makeVoltageWidget(self, reactor):        
        from DAC_CONTROL import DAC_Control
        from common.clients.PMT_CONTROL import pmtWidget
        from TRAPDRIVE_CONTROL import TD_CONTROL
        from TICKLE_CONTROL import Tickle_Control
        from SHUTTER_CONTROL import SHUTTER
        from common.clients.multiplexer.MULTIPLEXER_CONTROL import multiplexerWidget
        widget = QtGui.QWidget()
        gridLayout = QtGui.QGridLayout()        
        gridLayout.addWidget(DAC_Control(reactor), 0, 0)            
        rightPanel = QtGui.QGridLayout()
        rightPanel.addWidget(pmtWidget(reactor), 0, 0)
        bottomPanel = QtGui.QGridLayout()
        bottomPanel.addWidget(Tickle_Control(reactor), 1, 1)      
        bottomPanel.addWidget(TD_CONTROL(reactor), 1, 0)
        bottomPanel.addWidget(SHUTTER(reactor), 1, 2) 
        gridLayout.addLayout(rightPanel, 0, 1, 2, 1)          
        gridLayout.addLayout(bottomPanel, 1, 0)
        gridLayout.setRowStretch(0, 1)
        rightPanel.setRowStretch(2, 1)            
        widget.setLayout(gridLayout)
        return widget

    def closeEvent(self, x):
        self.reactor.stop()

if __name__=="__main__":
    a = QtGui.QApplication( [] )
    import qt4reactor
    qt4reactor.install()
    from twisted.internet import reactor
    ResonatorGUI = ResonatorGUI(reactor)
    ResonatorGUI.show()
    reactor.run()

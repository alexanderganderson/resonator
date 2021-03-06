import numpy as np
#from FFT import measureFFT
import labrad
import time
import datetime

now = datetime.datetime.now()
date = now.strftime("%Y%m%d")
timey = now.strftime('%H%M%S')
amplMin = 0.05
amplMax = 0.2
amplStep = 0.01
amplitudes = np.arange(amplMin, amplMax + amplStep, amplStep)

for Ex in amplitudes:

    cxn = labrad.connect()
    cxn2 = labrad.connect('192.168.169.30')
    dv = cxn.data_vault
    ds = cxn.cctdac
    pmt = cxn.normalpmtflow
    rs = cxn2.rohdeschwarz_server
    rs.select_device('GPIB Bus - USB0::0x0AAD::0x0054::104543')

    freqMin = 45.7
    freqMax = 46.3
    freqStep = 0.015
    recordTime = 0.5 #seconds
    average = 6
    freqSpan = 100.0 #Hz 
    freqOffset = -920.0 #Hz, the offset between the counter clock and the rf synthesizer clock
    #setting up FFT
 #   fft = measureFFT(cxn, recordTime, average, freqSpan, freqOffset, savePlot = False)
    #saving
   # dv.cd(['', date, 'QuickMeasurements','MMComp'],True)
    dv.cd(['', date, 'QuickMeasurements','MMComp', timey + '-Ex and Tickle'],True)
    #name = dv.new('EyandRS',[('Ey', 'V/m'), ('Frequency', 'Hz')], [('Counts', 'counts', 'counts')])
    Ey = -0.39
    name = dv.new('Ex: %s V/m; RS: scan' % str(Ex),[('Frequency', 'Hz')], [('Counts', 'counts', 'counts')])
    #dv.add_parameter('Window',['mm'])
    dv.add_parameter('plotLive',True)
    dv.add_parameter('Ey', Ey)
    print 'Saving {}'.format(name)

    frequencies = np.arange(freqMin, freqMax +freqStep, freqStep)
    frequencies = frequencies[::-1] # The ion asks that you kindly scan downwards, thanks

   # Ey = -0.36
    Ez = 0
    U1 = -.22
    U2 = 4.5
    U3 = .22
    U4 = 0
    U5 = 0

    ds.set_multipole_voltages([('Ex', Ex), ('Ey', Ey), ('Ez', Ez), ('U1', U1), ('U2', U2), ('U3', U3), ('U4', U4), ('U5', U5)])
    for f in frequencies:
      rs.frequency(f)
      pmtcount = pmt.get_next_counts('ON', 3, True)
      dv.add(f, pmtcount)

##installation instructions:
##    
##    download libusb-0.1 (for windows: http://sourceforge.net/projects/libusb-win32/)
##        unzip to local folder
##        open folder, enter bin-directory and run inf-wizard
##        follow onscreen instructions. on last screen, click "install now"
##
##    download pyusb-1.0.0b1 (http://walac.github.io/pyusb/)
##        unzip to local folder
##        open command line, cd to directory
##        type "python setup.py install"
##    download ap--/python-oceanoptics (https://github.com/ap--/python-oceanoptics)
##        unzip to local folder
##        open command line, cd to directory
##        type "python setup.py install"
##          




#import oceanoptics

from seabreeze.spectrometers import Spectrometer
spectrometer = Spectrometer.from_first_available()

import time
import os
import numpy as np
import matplotlib
matplotlib.use('WXAgg')
import matplotlib.pyplot as plt

from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas
from matplotlib.backends.backend_wx import NavigationToolbar2Wx
from matplotlib.figure import Figure

from scipy.interpolate import interp1d

import wx
from wx.lib.masked import NumCtrl


class LiveView(wx.Panel):
    
    def __init__(self,parent, spectrometer):
        self.spectrometer = spectrometer
 
        # background correspond to noise values, we want to take of
        # reference is for computing transmittance
        # avg is for window average.
        
        wx.Panel.__init__(self, parent)
        
        self.figure = Figure()
        self.axes = self.figure.add_subplot(111)
        
        self.canvas = FigureCanvas(self, -1, self.figure)

        self.sizer = wx.BoxSizer(wx.VERTICAL)       # main window
        
        self.sizer1 = wx.BoxSizer(wx.HORIZONTAL)    # graph
        self.sizer2 = wx.BoxSizer(wx.VERTICAL)      # controls

        self.sizer3 = wx.BoxSizer(wx.HORIZONTAL)    # main, data, plotrange
        self.sizer4 = wx.BoxSizer(wx.HORIZONTAL)    # file save
        
        self.sizer5 = wx.BoxSizer(wx.VERTICAL)      # main
        self.sizer6 = wx.BoxSizer(wx.VERTICAL)      # data
        self.sizer7 = wx.BoxSizer(wx.VERTICAL)      # plotrange
        self.sizer16 = wx.BoxSizer(wx.VERTICAL)

        self.sizer8 = wx.BoxSizer(wx.HORIZONTAL)    # integration
        self.sizer9 = wx.BoxSizer(wx.HORIZONTAL)    # averaging
        self.sizer10 = wx.BoxSizer(wx.HORIZONTAL)   # Background
        self.sizer11 = wx.BoxSizer(wx.HORIZONTAL)   # Reference

        self.sizer12 = wx.BoxSizer(wx.HORIZONTAL)   # xmin
        self.sizer13 = wx.BoxSizer(wx.HORIZONTAL)   # xmax
        self.sizer14 = wx.BoxSizer(wx.HORIZONTAL)   # ymin
        self.sizer15 = wx.BoxSizer(wx.HORIZONTAL)   # ymax
        
        self.sizer17 = wx.BoxSizer(wx.HORIZONTAL)
        self.sizer18 = wx.BoxSizer(wx.HORIZONTAL)



        


        self.livebutton=wx.Button(self,label="live",pos=(225,32),size=(90,30))
        self.Bind(wx.EVT_BUTTON, self.live, self.livebutton)

        self.recordbutton=wx.Button(self,label="record on/off",pos=(225,32),size=(90,30))
        self.Bind(wx.EVT_BUTTON, self.record, self.recordbutton)

        self.stopbutton=wx.Button(self,label="stop",pos=(225,32),size=(90,30))
        self.Bind(wx.EVT_BUTTON, self.stop, self.stopbutton)

        self.IntLabel = wx.StaticText(self, -1, "    Integration time (milisec):", size=(150,20))
        self.Int = NumCtrl(self, id=-1, value = 20, integerWidth = 9, fractionWidth = 0)
        self.Bind(wx.EVT_TEXT, self.refresh, self.Int)

        self.AvgLabel = wx.StaticText(self, -1, "    Wavelenght convolution window:", size=(150,20))
        self.Avg = NumCtrl(self, id=-1, value = 1, integerWidth = 4, fractionWidth = 0)
        #self.Bind(wx.EVT_TEXT, self.refresh, self.AvgLabel)

        self.backgrdLabel = wx.StaticText(self, -1, "    Background", size=(110,20))
        self.backgrdbutton1=wx.Button(self,label="reset",pos=(225,32),size=(45,-1))
        self.Bind(wx.EVT_BUTTON, self.zero_background, self.backgrdbutton1)
        self.backgrdbutton2=wx.Button(self,label="set",pos=(225,32),size=(45,-1))
        self.Bind(wx.EVT_BUTTON, self.set_background, self.backgrdbutton2)

        
        self.referenceLabel = wx.StaticText(self, -1, "    Reference", size=(110,20))
        self.referencebutton1=wx.Button(self,label="reset",pos=(225,32),size=(45,-1))
        self.Bind(wx.EVT_BUTTON, self.zero_reference, self.referencebutton1)
        self.referencebutton2=wx.Button(self,label="set",pos=(225,32),size=(45,-1))
        self.Bind(wx.EVT_BUTTON, self.set_reference, self.referencebutton2)

        self.xminLabel  = wx.StaticText(self, -1, "     X min", size=(70,20))
        self.xminVal = NumCtrl(self, id=-1, value = 170, integerWidth = 5, fractionWidth = 1)
        self.xminbutton=wx.Button(self,label="toggle auto",pos=(225,32),size=(75,-1))
        self.Bind(wx.EVT_BUTTON, self.xmin_toggle, self.xminbutton)

        self.xmaxLabel  = wx.StaticText(self, -1, "     X max", size=(70,20))
        self.xmaxVal = NumCtrl(self, id=-1, value = 900, integerWidth = 5, fractionWidth = 1)
        self.xmaxbutton=wx.Button(self,label="toggle auto",pos=(225,32),size=(75,-1))
        self.Bind(wx.EVT_BUTTON, self.xmax_toggle, self.xmaxbutton)

        self.yminLabel  = wx.StaticText(self, -1, "     Y min", size=(70,20))
        self.yminVal = NumCtrl(self, id=-1, value = 0, integerWidth = 5, fractionWidth = 1)
        self.yminbutton=wx.Button(self,label="toggle auto",pos=(225,32),size=(75,-1))
        self.Bind(wx.EVT_BUTTON, self.ymin_toggle, self.yminbutton)

        self.ymaxLabel  = wx.StaticText(self, -1, "     Y max", size=(70,20))
        self.ymaxVal = NumCtrl(self, id=-1, value = 100, integerWidth = 10, fractionWidth = 1)
        self.ymaxbutton=wx.Button(self,label="toggle auto",pos=(225,32),size=(75,-1))
        self.Bind(wx.EVT_BUTTON, self.ymax_toggle, self.ymaxbutton)

        self.savebutton=wx.Button(self,label="save",pos=(225,32),size=(90,-1))
        self.Bind(wx.EVT_BUTTON, self.save, self.savebutton)

        self.dataLabel = wx.StaticText(self, -1, "    Data filename:", size=(90,20))
        self.dataFile = wx.TextCtrl(self, -1, "spectrum", size=(120, 20))

        self.dataIndexLabel = wx.StaticText(self, -1, " Index:", size=(45,20))
        self.dataIndex = NumCtrl(self, id=-1, value = 1, integerWidth = 4, fractionWidth = 0)

        self.intervalLabel = wx.StaticText(self, -1, " Interval(s):", size=(60,20))
        self.Interval = NumCtrl(self, id=-1, value = 1, integerWidth = 4, fractionWidth = 0)

        self.absorbanceLabel = wx.StaticText(self, -1, "    Absorbance", size=(110,20))
        self.absorbance_on_button=wx.Button(self,label="On",pos=(225,32),size=(45,-1))
        self.Bind(wx.EVT_BUTTON, self.absorbance_on, self.absorbance_on_button)
        self.absorbance_off_button=wx.Button(self,label="Off",pos=(225,32),size=(45,-1))
        self.Bind(wx.EVT_BUTTON, self.absorbance_off, self.absorbance_off_button)

        self.scantimeLabel = wx.StaticText(self, -1, "    Scan to average:", size=(150,20))
        self.scan_time = NumCtrl(self, id=-1, value = 1, integerWidth = 10, fractionWidth = 0)
        

      

        self.sizer.Add(self.sizer1, flag=wx.EXPAND)
        self.sizer.Add(self.sizer2, flag=wx.EXPAND)

        self.sizer1.Add(self.canvas, -1)

        self.SetSizer(self.sizer)  

        self.sizer2.Add(self.sizer3, flag=wx.EXPAND)
        self.sizer2.Add(self.sizer4, flag=wx.EXPAND)
        
        self.sizer3.Add(self.sizer5, flag=wx.EXPAND)
        self.sizer3.Add(self.sizer6, flag=wx.EXPAND)
        self.sizer3.Add(self.sizer7, flag=wx.EXPAND)
        self.sizer3.Add(self.sizer16, flag=wx.EXPAND)

        self.sizer6.Add(self.sizer8, flag=wx.EXPAND)
        self.sizer6.Add(self.sizer9, flag=wx.EXPAND)
        self.sizer6.Add(self.sizer10, flag=wx.EXPAND)
        self.sizer6.Add(self.sizer11, flag=wx.EXPAND)

        self.sizer7.Add(self.sizer12, flag=wx.EXPAND)
        self.sizer7.Add(self.sizer13, flag=wx.EXPAND)
        self.sizer7.Add(self.sizer14, flag=wx.EXPAND)
        self.sizer7.Add(self.sizer15, flag=wx.EXPAND)

        self.sizer16.Add(self.sizer17, flag=wx.EXPAND)
        self.sizer16.Add(self.sizer18, flag=wx.EXPAND)

        self.sizer5.Add(self.livebutton)
        self.sizer5.Add(self.recordbutton)
        self.sizer5.Add(self.stopbutton)
        
        self.sizer8.Add(self.IntLabel)
        self.sizer8.Add(self.Int)

        self.sizer9.Add(self.AvgLabel)
        self.sizer9.Add(self.Avg)
        
        self.sizer10.Add(self.backgrdLabel)
        self.sizer10.Add(self.backgrdbutton1)
        self.sizer10.Add(self.backgrdbutton2)
        
        self.sizer11.Add(self.referenceLabel)
        self.sizer11.Add(self.referencebutton1)
        self.sizer11.Add(self.referencebutton2)

        self.sizer12.Add(self.xminLabel)
        self.sizer12.Add(self.xminVal)
        self.sizer12.Add(self.xminbutton)

        self.sizer13.Add(self.xmaxLabel)
        self.sizer13.Add(self.xmaxVal)
        self.sizer13.Add(self.xmaxbutton)

        self.sizer14.Add(self.yminLabel)
        self.sizer14.Add(self.yminVal)
        self.sizer14.Add(self.yminbutton)
        
        self.sizer15.Add(self.ymaxLabel)
        self.sizer15.Add(self.ymaxVal)
        self.sizer15.Add(self.ymaxbutton)

        self.sizer4.Add(self.savebutton)
        self.sizer4.Add(self.dataLabel)
        self.sizer4.Add(self.dataFile)
        self.sizer4.Add(self.dataIndexLabel)
        self.sizer4.Add(self.dataIndex)

        self.sizer4.Add(self.intervalLabel)
        self.sizer4.Add(self.Interval)

        self.sizer17.Add(self.absorbanceLabel)      
        self.sizer17.Add(self.absorbance_on_button)
        self.sizer17.Add(self.absorbance_off_button)     

        self.sizer18.Add(self.scantimeLabel)     
        self.sizer18.Add(self.scan_time)
    

        

        self.intTimeS = self.Int.GetValue()
         
        self.spectrometer.integration_time_micros(self.intTimeS)
        self.wl = self.spectrometer.wavelengths()[2:]
        self.int = self.spectrometer.intensities()[2:]

        self.background = np.zeros(len(self.int))
        self.reference = np.ones(len(self.int))

        self.avgnum = 1
        self.scan_time_window = 1 
        self.time_buffer = list()

        self.data = (self.int - self.background)/self.reference

        self.minx = 170
        self.maxx = 3000
        self.miny = min(self.data)*0.9
        self.maxy = min(self.data)*1.1

        self.running = False
        self.recording = False

        self.xminstate = False
        self.xmaxstate = False
        self.yminstate = False
        self.ymaxstate = False

        self.zero_ref = 1
        self.absorbance = False

        
    def draw(self):
        
        self.graph, = self.axes.plot(self.wl, self.data)

    def update(self, event):

        self.avgint = np.zeros (len(self.wl))

        if self.Avg.GetValue() == 0:
            self.avgnum = 1
        else:
            self.avgnum = self.Avg.GetValue()
                    
        self.int = self.spectrometer.intensities()[2:]

        # Taking wavelength averaging      
        self.avg_window = np.hamming(self.avgnum)               
        self.avgint = np.convolve(self.int, self.avg_window, 'same')/self.avgnum
        self.avgref = np.convolve(self.reference, self.avg_window, 'same')/self.avgnum
        
        # 
        if self.zero_ref == 0:
            self.int_ref_treshold = 100
            self.data = self.avgint - self.background   
            bool_array = self.data > self.int_ref_treshold
            
            self.data = 100 * self.data/self.avgref

        else:
            self.data = (self.avgint - self.background)/self.avgref
            
        
        
        border = int(self.avgnum/2)
        if border != 0:
            self.data[0:border] = self.data[border + 1]
            self.data[-border:] = self.data[-border - 1]
        if self.absorbance == True:
            self.data = self.data/100 + 0.1 * (self.data/100 < 0.001)
            self.data = -np.log(self.data)

        
        
        if self.scan_time.GetValue() == 0:
            self.scan_time_window = 1
        else:
            self.scan_time_window = self.scan_time.GetValue() 
        time_buffer = self.time_buffer

        print('scan_time_window', self.scan_time_window)
        print('largo de time buffer', len(self.time_buffer))
        if len(self.time_buffer) > self.scan_time_window:
            time_buffer.pop(0)
        elif len(self.time_buffer) == self.scan_time_window:
            time_buffer.pop(0)
            time_buffer.append(self.data)
            print('self.data antes',self.data)
        elif len(self.time_buffer) < self.scan_time_window:
            time_buffer.append(self.data)
        self.time_buffer = time_buffer
                
        
        arr_buff = np.array(self.time_buffer)
        
        self.avg_time_data = np.average(arr_buff, axis = 0)
        
        
        self.graph.set_ydata(self.avg_time_data)
        
        self.graph.set_color("blue")

        if max(self.int) > 60000:
            self.graph.set_color("red")
            print('holas')

        if self.xminstate == False:
            self.minx = 170
        else:
            self.minx = self.xminVal.GetValue()

        if self.xmaxstate == False:
            self.maxx = 900
        else:
            self.maxx = self.xmaxVal.GetValue()
            
        if self.yminstate == False:
            self.miny = min(self.data)*0.9
        else:
            self.miny = self.yminVal.GetValue()

        if self.ymaxstate == False:
            self.maxy = max(self.data)*1.1
        else:
            self.maxy = self.ymaxVal.GetValue()

            
        
        
        


        self.axes.axis([self.minx, self.maxx, self.miny, self.maxy])
        
        self.canvas.draw()

    def refresh(self, event):
        
        self.intTimeS = self.Int.GetValue()
        
        #self.intTimes = 20
        self.intTimeS = self.intTimeS*1000
        self.spectrometer.integration_time_micros(self.intTimeS)

        if self.Avg.GetValue() == 0:
            self.avgnum = 1
        else:
            self.avgnum = self.Avg.GetValue()       
        
        #if self.scan_time.GetValue() == 0:
        #    self.scan_time_window = 1
        #else:
        #    self.scan_time_window = self.scan_time.GetValue() 

    def set_background(self, event):
        self.background = self.avgint
        
    def zero_background(self, event):
        self.background = np.zeros(len(self.wl))

    def set_reference(self, event):
        for i in range (0, len(self.data)):
            if np.abs(self.data[i]) <= 0.9:
                self.reference[i] = 10000000000000
            else:
                self.reference[i] = self.data[i]
        self.zero_ref = 0        

    def zero_reference(self, event):
        self.reference = np.ones(len(self.wl))
        self.zero_ref = 1

    def xmin_toggle(self, event):
        if self.xminstate == False:
            self.xminstate = True
        else:
            self.xminstate = False
        
    def xmax_toggle(self, event):
        if self.xmaxstate == False:
            self.xmaxstate = True
        else:
            self.xmaxstate = False

    def ymin_toggle(self, event):
        if self.yminstate == False:
            self.yminstate = True
        else:
            self.yminstate = False
        
    def ymax_toggle(self, event):
        if self.ymaxstate == False:
            self.ymaxstate = True
        else:
            self.ymaxstate = False
    
    def absorbance_on(self, event):
        self.absorbance = True
    def absorbance_off(self, event):
        self.absorbance = False
   


        
    def live(self,event):        

        if self.running == False:
            print('live')
            self.running = True
           
        else:
            print('already running')
            return            

        while self.running == True:
            wx.Yield()

            if self.running == False:
                break

            self.update(self)

            if self.recording == True:
                
                self.timeElapsed = time.time()-self.startingTime

                if self.timeElapsed >= self.n*self.Interval.GetValue():
                    self.n +=1
                    self.save(self)

            

    def record(self,event):
        
        if self.recording == False:
            self.recording = True
            self.startingTime = time.time()
            self.n = 0
        else:
            self.recording = False

        if self.running == False:
            self.live(self)

    def save(self,event):

        os.mkdir(self.dataFile.GetValue())
        self.index = self.dataIndex.GetValue()
        file = open(""+str(self.dataFile.GetValue())+"/timestep"+str(self.index)+".txt", "w")
        file.write("Time: "+str(time.time())+"\n")
        for i in range (0, len(self.wl)):
            file.write(""+str(self.wl[i])+" "+str(self.data[i])+"\n")
        file.close()
        print("Spectrum "+str(self.index)+" recorded")
        self.dataIndex.SetValue(self.index+1)

    def stop(self,event):

        self.recording = False

        if self.running == False:
            print('not running')
        else:
            self.running = False
            print('stop')
        
        

if __name__ == "__main__":
    
    app = wx.PySimpleApp()
    fr = wx.Frame(None, title='USB4000', size=(530,635))
    panel = LiveView(fr, spectrometer)
    panel.draw()
    fr.Show()    
    app.MainLoop()
    


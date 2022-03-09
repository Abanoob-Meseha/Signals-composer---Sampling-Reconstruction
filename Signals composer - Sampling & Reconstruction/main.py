from operator import index
from re import X
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import *
from matplotlib.backends.backend_agg import FigureCanvasAgg
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from numpy.fft.helper import rfftfreq
from pyqtgraph import *
from pyqtgraph import PlotWidget, PlotItem
import pyqtgraph as pg
import pandas as pd
import matplotlib.pyplot as plt
import sys
import os
import pathlib
import numpy as np
from pyqtgraph.Qt import _StringIO
from DSP2FINAL import Ui_MainWindow
from PyQt5.QtWidgets import QApplication, QWidget, QInputDialog, QLineEdit, QFileDialog
from PyQt5.QtGui import QIcon
from matplotlib.figure import Figure
from fpdf import FPDF
import pyqtgraph.exporters
import math 
from scipy.interpolate import make_interp_spline
from scipy import signal
from scipy.fft import fft, fftfreq,rfft



class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)


        #______________________________IMPORTANT INSTANCE VARIABLES__________________________________________________________#
        self.SIGNAL_X=[]
        self.SIGNAL_Y=[]
        self.GraphicsView=[self.ui.graphicsView,self.ui.graphicsView_2,self.ui.graphicsView_3,self.ui.graphicsView_4]#ALL GRAPHIGSVIEW TO USE THEM WIH JUST INDEX
        #VIP THE TOTAL SIGNAL POINTS ARE 1000 POINT
        Y1=np.zeros(1000)#INITIAL VALLUE OF ZEROS FOR SIGNAL1<FIRST SINE WAVE>
        Y2=np.zeros(1000)
        Y3=np.zeros(1000)
        Y4=np.zeros(1000)
        self.Y_SUM=[]#THE SUM OF 4 SIGNALS (Y1,Y2,Y3,Y4)
        self.sin_List=[Y1,Y2,Y3,Y4]#STORE THE 4 SIGNALS <SINE>
        self.x_Time=np.arange(0, 10, 0.01).tolist()#TIME AXIS ARRAY
        self.white=mkPen(color=(255,255, 255))#white
        self.Color1=mkPen(color=(255, 0, 0))#RED
        self.Color2=mkPen(color=(0, 255, 0))#GREEN
        self.Color3=mkPen(color=(0, 0, 255))#BLUE
        self.Color4=mkPen(color=(255, 200, 200), style=QtCore.Qt.DotLine)#Dotted pale-red line
        self.Color5=mkPen(color=(200, 255, 200), style=QtCore.Qt.DotLine)#Dotted pale-green line
        self.Color6=mkPen(color=(200, 200, 255), style=QtCore.Qt.DotLine)## Dotted pale-blue line
        self.COLOR_Pen=[self.Color1,self.Color2,self.Color3,self.Color4,self.Color5,self.Color6]#STORE COLORS TO BE USED WITH INDEX
        self.SampleTabColors=[self.Color4,self.Color5,self.Color6]

        #______________________________________CONNECTING BUTTONS WITH THEIR FUNCTIONS_______________________________________#
        self.ui.LOAD.clicked.connect(lambda: self.load())
        self.ui.ADD.clicked.connect(lambda: self.ADD_SIN())
        self.ui.DELETE.clicked.connect(lambda: self.DELETE_SIN())
        self.ui.CONFIRM.clicked.connect(lambda: self.SUM_CONFIRM())
        self.ui.EXPORT.clicked.connect(lambda: self.EXPORT_CSV())
        self.ui.MOVE_TO_MAIN.clicked.connect(lambda: self.MOVE_TO_MAIN())
        self.ui.HIDE.clicked.connect(lambda: self.hide())
        self.ui.MIGRATE.clicked.connect(lambda: self.MIGRATE_HERE())
        self.ui.RESET.clicked.connect(lambda: self.clear())
        self.ui.SAMPLE.clicked.connect(lambda: self.sample())
        self.ui.CONSTRUCT.clicked.connect(lambda: self.construct())

        
    #_____________________________________________BUTTTONS FUNCTIONS_______________________________________________________# 
    def ADD_SIN(self):#..................................>ADD NEW SIGNAL
        signalIndex=self.ui.SIGNALS.currentIndex()#GET THE VALUE FROM SPINBOX OF SIGNALS
        magnitude=int(self.ui.MAGNITUDE.value())#GET THE VALUE FROM SPINBOX OF MAGNITUDE
        phase=int(self.ui.PHASE.value())
        frequency=int(self.ui.FREQUENCY.value())
        Y=np.zeros(1000)#TEMP ARRAY FOR SAVING SINE SIGNAL VALUES
        for i in range(1000):
            Y[i]=(magnitude*(math.sin((2*np.pi*frequency*self.x_Time[i])+phase)))
        self.sin_List[signalIndex]=Y
        self.plotting(2,self.x_Time,Y,self.COLOR_Pen[signalIndex])
        


    def DELETE_SIN(self):#............................>DELETE SELECTED SIGNAL FROM SUM
        signalIndex=self.ui.SIGNALS.currentIndex()
        self.GraphicsView[2].clear()#CLEAR THE GRAPHICSVIEW
        Y=np.zeros(1000)
        self.sin_List[signalIndex]=Y #DELETE SIGNAL BY MAKE ITS VALUES=ZEROS
        for i in range(4):#LOOP FOR PLOTTING THE OTHER REMAINING <NON-DELETED SIGNALS>
            if i!=signalIndex:
                Y=self.sin_List[i]
                if Y[0]!= Y[1]:
                    self.GraphicsView[2].plot(self.x_Time, Y,pen=self.COLOR_Pen[i])
                    

    def SUM_CONFIRM(self):#........................>SUM THE SIGNALS AND PLOT THE SUM
        self.GraphicsView[3].clear()
        self.Y_SUM=np.zeros(1000)
        for i in range(1000):
            self.Y_SUM[i]=(self.sin_List[0][i]+self.sin_List[1][i]+self.sin_List[2][i]+self.sin_List[3][i])# SUM OF ALL SIGNALS VALUES 
        self.plotting(3,self.x_Time,self.Y_SUM,self.white)
        

    def EXPORT_CSV(self):#...........................>EXPORT THE SIGNAL TO CSV FILE
        
        np.savetxt('CSV-FILE.csv', [p for p in zip(self.x_Time, self.Y_SUM)], delimiter=',', fmt='%s')
        

    def MOVE_TO_MAIN(self):#.........................>MOVE THE TOTAL SUM SIGNAL TO BE SAMPLED 
        self.y=self.Y_SUM
        self.x=self.x_Time
        self.plotting(0,self.x_Time,self.Y_SUM,self.white)
        

    def hide(self):#.................................>HIDE THE SECOND GRAPH
        self.ui.graphicsView_2.setParent(None)


    def read_file(self):#----------------->>BROWSE TO READ THE FILE<<
        path = QFileDialog.getOpenFileName()[0]
        if pathlib.Path(path).suffix == ".csv":
            self.data = np.genfromtxt(path, delimiter=',')
            self.x = list(self.data[:, 0])
            self.y = list(self.data[:, 1])

    def load(self):#------------------------>>LOAD THE SIGNAL AND PLOT IT<<
        self.read_file()
        self.Signal_Color_index = self.ui.MAIN_COLOR.currentIndex()
        self.plotting(0,self.x,self.y,self.COLOR_Pen[self.Signal_Color_index])
        
        

    def sample(self):#.........................>GET SAMPLING FREQ AND PLOT THE POINTS
        self.GraphicsView[0].clear()
        self.Channel_ID=self.ui.SIGNALS.currentIndex()
        self.Signal_Color_index = self.ui.MAIN_COLOR.currentIndex()
        self.plotting(0,self.x,self.y,self.COLOR_Pen[self.Signal_Color_index])
        #--------------------------------------------------------UNTILL HERE JUST PLOTTING THE ORIGINAL SIGNAL WITHOUT SAMPLING POINTS
        
        fs = self.ui.SAMPLING_RATE.value()#GET FREQ SAMPLE FROM SPINBOX
        self.sampled_time = (self.x)[::int(100/fs)]#MAKE POINTS BY DIVIDING THE NUMBER OF POINTS IN SECOND <100> OVER FS
        self.sampled_signal = (self.y)[::int(100/fs)]
        self.GraphicsView[0].plot(self.sampled_time, self.sampled_signal,pen=None,symbol='o')
        self.GraphicsView[0].plotItem.setLabel("bottom", text="Time (ms)")
        self.GraphicsView[0].plotItem.showGrid(True, True, alpha=1)
        self.GraphicsView[0].plotItem.setLimits(xMin=0, xMax=10, yMin=-20, yMax=20)
        
    def construct(self):#.........................>CONSTRUCT THE SIGNAL SAMPLED AND CONNECT THE POINTS 
        self.Construct_Color_index = self.ui.SAMPLING_COLOR.currentIndex()
        self.GraphicsView[1].clear()
        self.xnew = np.linspace(min(self.sampled_time), max(self.sampled_time), 1000)
        self.spl = make_interp_spline(self.sampled_time, self.sampled_signal, 3)#INTERPOLATION AND CONNECT THE POINTS <3 HERE MEANS quadratic>
        self.ynew = self.spl(self.xnew)
        self.plotting(0,self.xnew,self.ynew,self.SampleTabColors[self.Construct_Color_index])
        
        
    def MIGRATE_HERE(self):#-------------------------->>SHOW THE CONSTRUCTED SIGNAL IN THE SECOND GRAPH <<
        self.ui.verticalLayout.addWidget(self.ui.graphicsView_2)
        self.GraphicsView[1].clear()
        self.Construct_Color_index = self.ui.SAMPLING_COLOR.currentIndex()
        self.plotting(1,self.xnew,self.ynew,self.SampleTabColors[self.Construct_Color_index])
        

    def clear(self):#------------------------------>>CLEAR THE 2 GRAPHS<<
        self.GraphicsView[0].clear()
        self.GraphicsView[1].clear()

    def plotting(self,GRAPHICSINDEX,X_ARRAY,Y_ARRAY,COLORLIST):#................>FUNCTION OF PLOTTING <FOR REDUCING THE REPEATATION OF CODE>
        self.GraphicsView[GRAPHICSINDEX].plot(X_ARRAY, Y_ARRAY, pen=COLORLIST)
        self.GraphicsView[GRAPHICSINDEX].plotItem.setLabel("bottom", text="Time (ms)")
        self.GraphicsView[GRAPHICSINDEX].plotItem.showGrid(True, True, alpha=1)
        self.GraphicsView[GRAPHICSINDEX].plotItem.setLimits(xMin=0, xMax=10, yMin=-20, yMax=20)


    

    def close_app(self):
        sys.exit()
#---------------------------------END OF MAINWINDOW CLASS---------------------------------------------#


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    main = MainWindow()
    main.show()
    sys.exit(app.exec_())

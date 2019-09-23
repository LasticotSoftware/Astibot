#!.


import threading
import time
import sys    
    
import ipdb # To be able to see error stack messages occuring in the Qt MainLoop

import os

from Settings import Settings    
from MarketData import MarketData
from InputDataHandler import InputDataHandler
from GDAXControler import GDAXControler
from TransactionManager import TransactionManager
from Trader import Trader
from UIGraph import UIGraph
from AppState import AppState
import TradingBotConfig as theConfig
import pyqtgraph as pg

from pyqtgraph.Qt import QtCore, QtGui # Only useful for splash screen
    

   
class TradingBot(object):

            
    def __init__(self):
        
        
        cwd = os.getcwd()
        print("Running Astibot in: %s" % cwd)

        self.isInitializing = True
        self.iterationCounter = 0
        self.historicPriceIterationCounter = 0
        
        self.app = pg.QtGui.QApplication(['Astibot'])
        
        # Show Splash Screen
        splash_pix = QtGui.QPixmap('AstibotSplash.png')
        splash = QtGui.QSplashScreen(splash_pix, QtCore.Qt.WindowStaysOnTopHint)
        splash.show()
        
        
        # Instanciate objects        
        self.theSettings = Settings()
        self.theUIGraph = UIGraph(self.app, self.theSettings)
        self.theGDAXControler = GDAXControler(self.theUIGraph, self.theSettings)
        self.theMarketData = MarketData(self.theGDAXControler, self.theUIGraph)
        self.theTransactionManager = TransactionManager(self.theGDAXControler, self.theUIGraph, self.theMarketData, self.theSettings)
        self.theUIGraph.UIGR_SetTransactionManager(self.theTransactionManager)
        self.theTrader = Trader(self.theTransactionManager, self.theMarketData, self.theUIGraph, self.theSettings)
        self.theInputDataHandler = InputDataHandler(self.theGDAXControler, self.theUIGraph, self.theMarketData, self.theTrader, self.theSettings)
        self.theApp = AppState(self.theUIGraph, self.theTrader, self.theGDAXControler, self.theInputDataHandler, self.theMarketData, self.theSettings)
 
        # Setup Main Tick Timer
        self.mainTimer = pg.QtCore.QTimer()
        self.mainTimer.timeout.connect(self.MainTimerHandler)
        self.mainTimer.start(100)
        
        # Hide splash screen
        splash.close()
        
        # Endless call        
        self.app.exec_()
        
        # App closing
        self.theGDAXControler.GDAX_closeBackgroundOperations()
        self.theInputDataHandler.INDH_closeBackgroundOperations()
        self.theUIGraph.UIGR_closeBackgroundOperations()
  
   
    def MainTimerHandler(self):
        self.theApp.APP_Execute()
  
        
if __name__ == '__main__':
    theTradingBot = TradingBot()
  

    
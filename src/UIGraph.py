from datetime import datetime
import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtGui
from PyQt5.QtCore import QTime, QTimer
from PyQt5.QtWidgets import QFrame
import numpy as np
import time
from threading import Timer, Lock
import pytz
from tzlocal import get_localzone
from random import randint


import TradingBotConfig as theConfig
from UIWidgets import ButtonHoverStart
from UIWidgets import ButtonHoverStart
from UIWidgets import ButtonHoverPause
from UIWidgets import ButtonHoverSettings
from UIWidgets import ButtonHoverDonation
from UIWidgets import ButtonHoverInfo
from UIWidgets import RadioHoverSimulation
from UIWidgets import RadioHoverTrading
from UIWidgets import SliderHoverRiskLevel
from UIWidgets import SliderHoverSensitivityLevel
from UIWidgets import LabelClickable
from UISettings import UISettings
from UIDonation import UIDonation
from UIInfo import UIInfo


class TimeAxisItem(pg.AxisItem):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.localTimezone = pytz.timezone(str(get_localzone())) 

    def tickStrings(self, values, scale, spacing):

        try:
            if (theConfig.CONFIG_INPUT_MODE_IS_REAL_MARKET == False): # 
                valuesToReturn = [(datetime.fromtimestamp(value, self.localTimezone).strftime("%H:%M:%S\n%b%d")) for value in values]
            else:
                valuesToReturn = [(datetime.fromtimestamp(value, self.localTimezone).strftime("%H:%M:%S")) for value in values]
        except BaseException as e:
            print("UIGR - Exception in tick strings: %s" % str(e))
            
        return valuesToReturn

class UIGraph():

    MAIN_WINDOW_WIDTH_IN_PX = 1120
    MAIN_WINDOW_HEIGHT_IN_PX = 900
    
    MAX_NB_POINTS_ON_PLOT = 2000
    Y_AXIS_TOP_MARGIN_IN_EXTREMUM_PERCENT = 1.0001
    Y_AXIS_BOTTOM_MARGIN_IN_EXTREMUM_PERCENT = 0.9999
    PLOT1_DEFAULT_MINIMUM = 8000
    PLOT1_DEFAULT_MAXIMUM = 10000
    
    STR_RADIO_SIMULATION = 'Simulation mode'
    STR_RADIO_TRADING = 'Live trading mode'
    STR_BUTTON_START = 'Start'
    STR_BUTTON_PAUSE = 'Pause'
    STR_BUTTON_SETTINGS = 'Settings'
    STR_BUTTON_Donation = 'Donate'
    STR_BUTTON_INFO = 'Info'
    STR_LABEL_MONEY_MIDDLEMARKET_PRICE = 'MiddleMarket price : '
    STR_LABEL_INFO = 'Info : '
    STR_LABEL_CURRENT_STATE = 'Current State : '
    STR_LABEL_TOTAL_GAINS = 'Total profit : '

    STR_BORDER_BLOCK_STYLESHEET = "QWidget {background-color : #151f2b;}"
    STR_USER_BLOCK_STYLESHEET = "QWidget {background-color : #203044;}"
    STR_QLABEL_STYLESHEET = "QLabel { background-color : #203044; color : white; font: bold 13px;}"
    STR_QLABEL_PROFIT_GREEN_STYLESHEET = "QLabel { background-color : #203044; color : #24b62e; font: bold 14px;}"
    STR_QLABEL_PROFIT_RED_STYLESHEET = "QLabel { background-color : #203044; color : #FF2F2F; font: bold 14px;}"
    STR_QLABEL_CURRENT_STATE_LIVE_TRADING_STYLESHEET = "QLabel { background-color : #203044; color : #ff2e2e; font: bold 14px;}"
    STR_QLABEL_INFO_STYLESHEET = "QLabel { background-color : #203044; color : white; font: 14px;}"
    STR_QLABEL_INFO_ERROR_STYLESHEET = "QLabel { background-color : #203044; color : #FF2F2F; font: 14px;}"
    STR_QLABEL_INFO_GREEN_STYLESHEET = "QLabel { background-color : #203044; color : #29CF36; font: bold 14px; text-decoration: underline;}"
    STR_QLABEL_INFO_ORANGE_STYLESHEET = "QLabel { background-color : #203044; color : #FF8000; font: bold 14px; text-decoration: underline;}"
    STR_QLABEL_TOOLTIP_STYLESHEET = "QLabel { background-color : #151f2b; color : white; font: 10px;}"
    STR_QLABEL_CONNECTION_STATUS_STYLESHEET = "QLabel { background-color : #151f2b; color : green; font: 10px;}"
    STR_QLABEL_VERSION_STYLESHEET = "QLabel { background-color : #151f2b; color : #334c6b; font: 11px;}"
    STR_QLABEL_LIVE_DATA_STYLESHEET = "QLabel { background-color : #151f2b; color : #334c6b; font: 10px;}"
    STR_QRADIOBUTTON_STYLESHEET = "QRadioButton { background-color : #203044; color : white; font: 14px;} QRadioButton::indicator:checked {background-color: #007ad9; border: 1px solid white;} QRadioButton::indicator:unchecked {background-color: #203044; border: 1px solid white;}"
    STR_QRADIOBUTTON_DISABLED_STYLESHEET = "QRadioButton { background-color : #203044; color : white; font: 14px;} QRadioButton::indicator:checked {background-color: #007ad9; border: 1px solid #203044;} QRadioButton::indicator:unchecked {background-color: #203044; border: 1px solid #203044;}"
    STR_QBUTTON_START_STYLESHEET = "QPushButton {background-color: #23b42c; border-width: 2px; border-radius: 10px; border-color: white; font: bold 18px; color:white} QPushButton:pressed { background-color: #1d8d24 } QPushButton:hover { background-color: #1a821f }"
    STR_QBUTTON_SETTINGS_STYLESHEET = "QPushButton {background-color: #21435e; border-width: 1.5px; border-radius: 10px; border-color: white; font: bold 15px; color:white} QPushButton:pressed { background-color: #096fbf } QPushButton:hover { background-color: #1D3850 }"
    STR_QBUTTON_SETTINGS_DISABLED_STYLESHEET = "QPushButton {background-color: #183145; border-width: 1.5px; border-radius: 10px; border-color: #838fa7; font: bold 15px; color:#838fa7}"
    STR_QBUTTON_START_DISABLED_STYLESHEET = "QPushButton {background-color: #9f9f9f; border-width: 2px; border-radius: 10px; border-color: white; font: bold 18px; color:white}"
    STR_QBUTTON_LOADING_STYLESHEET = "QPushButton {background-color: #9f9f9f; border-width: 2px; border-radius: 10px; border-color: white; font: bold 15px; color:white}"
    STR_QBUTTON_STOP_STYLESHEET = "QPushButton {background-color: #ff1824; border-width: 2px; border-radius: 10px; border-color: white; font: bold 18px; color:white} QPushButton:pressed { background-color: #aa0009 } QPushButton:hover { background-color: #aa0009 }"
    STR_QBUTTON_PAUSE_STYLESHEET = "QPushButton {background-color: #ddbd00; border-width: 2px; border-radius: 10px; border-color: white; font: bold 18px; color:white} QPushButton:pressed { background-color: #b3af00 } QPushButton:hover { background-color: #b3af00 }"
    STR_QBUTTON_PAUSE_DISABLED_STYLESHEET = "QPushButton {background-color: #9f9f9f; border-width: 2px; border-radius: 10px; border-color: white; font: bold 18px; color:white}"
    STR_QFRAME_SEPARATOR_STYLESHEET = "background-color: rgb(20, 41, 58);"
    STR_QSLIDER_STYLESHEET = "QSlider::handle:hover {background-color: #C6D0FF;}"
    
    def __init__(self, QtApplication, Settings):
        print("UIGR - UIGraph Constructor")

        self.theSettings = Settings
        
        self.firstGraphDataInitIsDone = False
                
        # Settings-dependant variables init
        self.STR_LABEL_FIAT_BALANCE = str(self.theSettings.SETT_GetSettings()["strFiatType"]) + " Account Balance : "
        self.STR_LABEL_CRYPTO_BALANCE = str(self.theSettings.SETT_GetSettings()["strCryptoType"]) + " Account Balance : "
    
        # Window initialization
        self.theQtApp = QtApplication
        self.mainWidget = QtGui.QWidget()
        self.rootGrid = QtGui.QGridLayout()        
        self.mainWidget.setWindowTitle('Astibot')        
        self.mainWidget.resize(self.MAIN_WINDOW_WIDTH_IN_PX, self.MAIN_WINDOW_HEIGHT_IN_PX)
        self.mainWidget.setWindowIcon(QtGui.QIcon("AstibotIcon.png"))
        
        # Customize main widget (window)
        self.mainWidget.setStyleSheet("background-color:#203044;")
        self.mainWidget.setAutoFillBackground(True);
               
        # By default consider the data series will start now. This can be overridden 
        self.MostRecentPointTimestamp = time.time()
 
        # Widget additional data initialization
        self.bStartButtonHasBeenClicked = False
        self.bPauseButtonHasBeenClicked = False
        self.timerBlinkWidgets = QtCore.QTimer()
        self.timerBlinkWidgets.timeout.connect(self.TimerRaisedBlinkWidgets)
        self.timerBlinkWidgets.start(1000)
        self.isLblCurrentStateBlinking = False
        self.currentRiskLineRawAvgValue = 0
        self.currentSensitivitySliderValue = 3
        self.sensitivitySliderValueHasChanged = True
        
        # Graph data initialization
        pg.setConfigOptions(antialias=True)
        nbPointsOnPlot = self.MAX_NB_POINTS_ON_PLOT
        self.UIGR_ResetAllGraphData(False, -1, nbPointsOnPlot)
        
        # Layouts and widgets init
        self.initializeTopWindowWidgets()   
        self.initializeGraphWidgets()
        self.initializeRootLayout()
        self.mainWidget.setLayout(self.mainGridLayout)

        # Graph refresh and multithreading management      
        self.isContinuousGraphRefreshEnabled = False
        self.areNewSamplesRequested = False
        self.timerUpdateGraph = QtCore.QTimer()
        self.timerUpdateGraph.timeout.connect(self.UIGR_updateGraphsSimuTimer)
        self.currentAppState = ""
        # True if a pending UI refresh has been requested from a background thread calling a UIGR API        
        self.safeUIRefreshIsRequested = False
        # Necessary storage of safe UI updates
        self.lblInfoInErrorStyle = False
        self.lblInfoStr = ""
        self.realProfit = 0.0
        self.theoricProfit = 0.0
        self.percentageProfit = 0.0
        self.displayProfitAsInSimulation = False
        self.priceLabelStr = ""
        self.strEURBalance = ""
        self.strCryptoBalance = ""
        self.strLiveData = "-"
        
        # Live data update timer
        self.timerUpdateLiveData = QtCore.QTimer()
        self.timerUpdateLiveData.timeout.connect(self.UIGR_updateLiveDataTimer)
        self.timerUpdateLiveData.start(150)
         
        # End if UI init, show window
        self.mainWidget.show()
        
        # Child windows 
        self.theUISettings = UISettings(Settings)
        self.theUIDonation = UIDonation(Settings)
        self.theUIInfo = UIInfo()
        
        # Set child UIs to clickable label that can open them
        self.lblInfo.SetUIs(self.theUISettings, self.theUIDonation) 
        
        print("UIGR - UIGraph init done!")
    
    # Argument startTimeStamp :
    # - Set to -1 if the graph will be batch updated with a number of data greater than nbPointsOnPlot : time 
    # axis will be ok and next samples will be added on the left shifting the whole graph
    # - Set to the timestamp of the first sample that will be added to the graph. This function will then build a 
    # retro time axis so that, during the period where added samples < nbPointsOnPlot, next samples will be added 
    # on the left shifting the whole graph
    def UIGR_ResetAllGraphData(self, applyToGraphs, startTimeStamp, nbPointsOnPlot):

        print("UIGR - Reseting all graph data with applyToGraphs = %s, startTimeStamp = %s, nbPointsOnPlot = %s" % (applyToGraphs, startTimeStamp, nbPointsOnPlot))
        self.totalNbIterations = 0
        self.totalNbGraphUpdates = 0
        self.timeOfLastSampleDisplayed = 0
        self.nbPointsOnPlot = nbPointsOnPlot
        self.currentRiskLineRawAvgValue = 0
        
        self.graphDataTime = []
        self.graphDataBitcoinPrice = []
        self.graphDataBitcoinPriceSmoothSlow = []
        self.graphDataBitcoinPriceSmoothFast = []
        self.graphDataBitcoinPriceMarker1 = []
        self.graphDataBitcoinPriceMarker2 = []
        self.graphDataBitcoinRiskLine = []
        self.graphDataIndicatorMACD = []
        self.minInPlot1 = self.PLOT1_DEFAULT_MINIMUM
        self.maxInPlot1 = self.PLOT1_DEFAULT_MAXIMUM
        
        self.graphDataTime = np.zeros(self.nbPointsOnPlot)
           
        # Y-Data vectors : put empty values (apprently set to zero) 
        self.graphDataBitcoinPrice = np.zeros(self.nbPointsOnPlot) #For tests np.random.normal(size=self.nbPointsOnPlot)
        self.graphDataBitcoinPriceSmoothFast = np.zeros(self.nbPointsOnPlot)
        self.graphDataBitcoinPriceSmoothSlow = np.zeros(self.nbPointsOnPlot)
        self.graphDataBitcoinPriceMarker1 = np.zeros(self.nbPointsOnPlot)
        self.graphDataBitcoinPriceMarker2 = np.zeros(self.nbPointsOnPlot)
        self.graphDataBitcoinRiskLine = np.zeros(self.nbPointsOnPlot)
        self.graphDataIndicatorMACD = np.zeros(self.nbPointsOnPlot)
        
        if (startTimeStamp != -1):
            # Time vector : put old timestamps until now so that the "present time" will be located at the right of the graph
            self.graphDataTime = self.initInitialTimeVector(startTimeStamp)            

    # Called from Main (UI) thread - OK
    def UIGR_StartContinuousGraphRefresh(self, refreshPeriodInMs):
        if (self.isContinuousGraphRefreshEnabled == False):
            print("UIGR - Starting continuous graph refresh")
            self.isContinuousGraphRefreshEnabled = True
            self.areNewSamplesRequested = True
            self.timerUpdateGraph.start(refreshPeriodInMs)
        
    # Called from Main (UI) thread - OK
    def UIGR_StopContinuousGraphRefresh(self):
        if (self.isContinuousGraphRefreshEnabled == True):
            print("UIGR - Stopping continuous graph refresh")
            self.isContinuousGraphRefreshEnabled = False
            self.areNewSamplesRequested = False
            self.timerUpdateGraph.stop()
    
    def UIGR_AreNewSamplesRequested(self):
        if (self.areNewSamplesRequested == True):
            self.areNewSamplesRequested = False
            return True
        else:
            return False
        
    def EventStartButtonClick(self):
        self.bStartButtonHasBeenClicked = True
    
    def EventPauseButtonClick(self):
        self.bPauseButtonHasBeenClicked = True
    
    def EventSettingsButtonClick(self):
        self.theUISettings.UIST_ShowWindow()
       
    def EventDonationButtonClick(self):
        self.theUIDonation.UIDO_ShowWindow()
    
    def EventInfoButtonClick(self):
        self.theUIInfo.UIFO_ShowWindow()
        
    def EventRadioModeToggle(self):
        theConfig.CONFIG_INPUT_MODE_IS_REAL_MARKET = not self.radioButtonSimulation.isChecked()
    
    def UIGR_IsStartButtonClicked(self):
        if (self.bStartButtonHasBeenClicked == True):
            self.bStartButtonHasBeenClicked = False
            return True
        else:
            return False   
             
    def UIGR_IsPauseButtonClicked(self):
        if (self.bPauseButtonHasBeenClicked == True):
            self.bPauseButtonHasBeenClicked = False
            return True
        else:
            return False  
        
    def UIGR_GetSelectedRadioMode(self):
        if (self.radioButtonSimulation.isChecked() == True):
            return "Simulation"
        else:
            return "Trading"
        
    def EventMovedSliderRiskLevel(self):
        
        newRiskLineValue = theConfig.CONFIG_RISK_LINE_PERCENTS_ABOVE_THRESHOLD_TO_BUY_MIN + ((self.sliderRiskLevel.value() / 100.0) * (theConfig.CONFIG_RISK_LINE_PERCENTS_ABOVE_THRESHOLD_TO_BUY_MAX - theConfig.CONFIG_RISK_LINE_PERCENTS_ABOVE_THRESHOLD_TO_BUY_MIN))
        if (abs(newRiskLineValue - theConfig.CONFIG_RiskLinePercentsAboveThresholdToBuy) > 0.0005):
            theConfig.CONFIG_RiskLinePercentsAboveThresholdToBuy = newRiskLineValue
            riskPercent = round((theConfig.CONFIG_RiskLinePercentsAboveThresholdToBuy - 1) * 100, 1)
            self.lblRiskLevelSlider1.setText("Risk level: %s%%" % str(riskPercent))
            
            # Refresh risk line plot data
            self.graphDataBitcoinRiskLine.fill(self.currentRiskLineRawAvgValue * theConfig.CONFIG_RiskLinePercentsAboveThresholdToBuy)
            # Update graph
            self.plot1GraphRiskLine.setData(x=self.graphDataTime, y=self.graphDataBitcoinRiskLine)
            
            if (theConfig.CONFIG_INPUT_MODE_IS_REAL_MARKET == True):
                # Force UI refresh. After a long running time, UI refresh is not automatic sometimes
                self.plot1.update()           
            
    def EventMovedSliderSensitivityLevel(self):
        print("slider moved to %s" % self.sliderSensitivityLevel.value())
        if (self.sliderSensitivityLevel.value() != self.currentSensitivitySliderValue):
            self.currentSensitivitySliderValue = self.sliderSensitivityLevel.value()
            self.lblSensitivityLevelSlider1.setText("Dips sensitivity: %s/6" % str(self.currentSensitivitySliderValue))
            self.sensitivitySliderValueHasChanged = True
    

                
    def UIGR_hasSensitivityLevelValueChanged(self):
        return self.sensitivitySliderValueHasChanged
    
    def UIGR_getSensitivityLevelValue(self):
        self.sensitivitySliderValueHasChanged = False
        return self.currentSensitivitySliderValue
    
    def initializeRootLayout(self):
        print("UIGR - InitializeRootLayout")
        self.mainGridLayout.setContentsMargins(0, 0, 0, 0)                
        
        self.rootBlockTop = QtGui.QWidget()
        self.rootBlockTop.setStyleSheet(self.STR_BORDER_BLOCK_STYLESHEET)
                
        # Top ====================================
        self.buttonSettings = ButtonHoverSettings(self.lblToolTip, self.STR_BUTTON_SETTINGS)
        self.buttonSettings.setVisible(True)
        self.buttonSettings.clicked.connect(self.EventSettingsButtonClick)
        self.buttonSettings.setFixedWidth(110)
        self.buttonSettings.setFixedHeight(28)
        self.buttonSettings.setStyleSheet(self.STR_QBUTTON_SETTINGS_STYLESHEET)
        self.buttonSettings.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.buttonDonation = ButtonHoverDonation(self.lblToolTip, self.STR_BUTTON_Donation)
        self.buttonDonation.setVisible(True)
        self.buttonDonation.clicked.connect(self.EventDonationButtonClick)
        self.buttonDonation.setFixedWidth(110)
        self.buttonDonation.setFixedHeight(28)
        self.buttonDonation.setStyleSheet(self.STR_QBUTTON_SETTINGS_STYLESHEET)
        self.buttonDonation.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.buttonInfo = ButtonHoverInfo(self.lblToolTip, self.STR_BUTTON_INFO)
        self.buttonInfo.setVisible(True)
        self.buttonInfo.clicked.connect(self.EventInfoButtonClick)
        self.buttonInfo.setFixedWidth(110)
        self.buttonInfo.setFixedHeight(28)
        self.buttonInfo.setStyleSheet(self.STR_QBUTTON_SETTINGS_STYLESHEET)
        self.buttonInfo.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        
        self.lblVersion = QtGui.QLabel("Version " + str(theConfig.CONFIG_VERSION))
        self.lblVersion.setStyleSheet(self.STR_QLABEL_VERSION_STYLESHEET);
        self.lblVersion.setAlignment(QtCore.Qt.AlignLeft)
        self.lblVersion.setFixedHeight(28)
        
        self.rootTopBlock = QtGui.QWidget()
        self.rootTopBlock.setStyleSheet(self.STR_BORDER_BLOCK_STYLESHEET)
        self.rootTopBlock.setFixedHeight(60)
        self.rootHboxTop = QtGui.QHBoxLayout()
        self.rootHboxTop.setContentsMargins(40, 0, 40, 0) # left, top, right, bottom
        self.lblLogo = QtGui.QLabel("lblLogo")
        pixmap = QtGui.QPixmap('AstibotLogo.png')
        self.lblLogo.setPixmap(pixmap)
        self.rootHboxTop.addWidget(self.lblLogo)
        self.rootHboxTop.addWidget(self.lblVersion)
        self.rootHboxTop.addWidget(self.buttonSettings, QtCore.Qt.AlignRight)
        self.rootHboxTop.addWidget(self.buttonDonation, QtCore.Qt.AlignRight)
        self.rootHboxTop.addWidget(self.buttonInfo, QtCore.Qt.AlignRight)
        self.rootTopBlock.setLayout(self.rootHboxTop)
        
        self.mainGridLayout.addWidget(self.rootTopBlock, 0, 0, 1, 4)
        
        # Bottom ==================================
        self.rootBottomBlock = QtGui.QWidget()
        self.rootBottomBlock.setStyleSheet(self.STR_BORDER_BLOCK_STYLESHEET)
        self.rootBottomBlock.setFixedHeight(40)

        self.rootHboxBottom = QtGui.QHBoxLayout()
        self.rootHboxBottom.setContentsMargins(40, 0, 40, 0) # left, top, right, bottom
        self.rootVboxBottomRight = QtGui.QVBoxLayout()
        self.lblConnection = QtGui.QLabel("")
        self.lblConnection.setAlignment(QtCore.Qt.AlignRight)
        self.lblToolTip.setStyleSheet(self.STR_QLABEL_TOOLTIP_STYLESHEET);
        self.lblToolTip.setWordWrap(True);
        self.lblToolTip.setFixedWidth((self.MAIN_WINDOW_WIDTH_IN_PX / 2))
        self.lblToolTip.setFixedHeight(42)
        self.lblConnection.setStyleSheet(self.STR_QLABEL_CONNECTION_STATUS_STYLESHEET);
        self.lblLiveData = QtGui.QLabel("")
        self.lblLiveData.setStyleSheet(self.STR_QLABEL_LIVE_DATA_STYLESHEET);
        self.lblLiveData.setAlignment(QtCore.Qt.AlignRight)
        self.lblConnection.setAlignment(QtCore.Qt.AlignRight)
        self.rootHboxBottom.addWidget(self.lblToolTip, QtCore.Qt.AlignLeft)
        self.rootVboxBottomRight.addWidget(self.lblConnection)
        self.rootVboxBottomRight.addWidget(self.lblLiveData)     
        self.rootHboxBottom.addLayout(self.rootVboxBottomRight, QtCore.Qt.AlignRight)
        self.rootBottomBlock.setLayout(self.rootHboxBottom)
         
        self.mainGridLayout.addWidget(self.rootBottomBlock, 13, 0, 1, 4)
        
        # Left and Right
        self.rootLeftBlock = QtGui.QWidget()
        self.rootLeftBlock.setStyleSheet(self.STR_BORDER_BLOCK_STYLESHEET)
        self.rootLeftBlock.setFixedWidth(40)
        self.rootRightBlock = QtGui.QWidget()
        self.rootRightBlock.setStyleSheet(self.STR_BORDER_BLOCK_STYLESHEET)
        self.rootRightBlock.setFixedWidth(40)
        self.mainGridLayout.addWidget(self.rootLeftBlock, 0, 0, 14, 1)
        self.mainGridLayout.addWidget(self.rootRightBlock, 0, 3, 14, 1)

        
    def initializeTopWindowWidgets(self):
        
        # Pre requisite for further inits
        self.lblToolTip = QtGui.QLabel("");
        
        self.rootMiddleBlock1 = QtGui.QWidget()
        self.rootMiddleBlock1.setStyleSheet(self.STR_BORDER_BLOCK_STYLESHEET)
        self.rootMiddleBlock1.setFixedHeight(15)
        self.rootMiddleBlock2 = QtGui.QWidget()
        self.rootMiddleBlock2.setStyleSheet(self.STR_BORDER_BLOCK_STYLESHEET)
        self.rootMiddleBlock2.setFixedHeight(15)
        
        # Part 1
        self.hBox1 = QtGui.QHBoxLayout()
        self.vBoxRadioModeButtons = QtGui.QVBoxLayout()
        self.vBoxSliders = QtGui.QVBoxLayout()
        self.hBoxSliders1 = QtGui.QHBoxLayout()
        self.hBoxSliders2 = QtGui.QHBoxLayout()
        self.hBox1.setSpacing(10)
        
        self.radioButtonSimulation = RadioHoverSimulation(self.lblToolTip, self.STR_RADIO_SIMULATION)
        self.radioButtonSimulation.setChecked(False)
        self.radioButtonSimulation.setFixedWidth(200)
        self.radioButtonSimulation.setStyleSheet(self.STR_QRADIOBUTTON_STYLESHEET);
        self.radioButtonSimulation.toggled.connect(self.EventRadioModeToggle)
        self.radioButtonSimulation.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.radioButtonTrading = RadioHoverTrading(self.lblToolTip, self.STR_RADIO_TRADING)
        self.radioButtonTrading.setChecked(True)
        self.radioButtonTrading.setFixedWidth(200)
        self.radioButtonTrading.setStyleSheet(self.STR_QRADIOBUTTON_STYLESHEET);
        self.radioButtonTrading.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.buttonPause = ButtonHoverPause(self.lblToolTip, self.STR_BUTTON_PAUSE)
        self.buttonPause.setVisible(True)
        self.buttonPause.clicked.connect(self.EventPauseButtonClick)
        self.buttonPause.setFixedWidth(80)
        self.buttonPause.setFixedHeight(60)
        self.buttonPause.setStyleSheet(self.STR_QBUTTON_PAUSE_STYLESHEET)
        self.buttonPause.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.buttonStart = ButtonHoverStart(self.lblToolTip, self.STR_BUTTON_START)
        self.buttonStart.setVisible(True)
        self.buttonStart.clicked.connect(self.EventStartButtonClick)
        self.buttonStart.setFixedWidth(80)
        self.buttonStart.setFixedHeight(60)
        self.buttonStart.setStyleSheet(self.STR_QBUTTON_START_STYLESHEET)
        self.buttonStart.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        
        self.vBoxRadioModeButtons.addWidget(self.radioButtonSimulation)
        self.vBoxRadioModeButtons.addWidget(self.radioButtonTrading)
        self.hBox1.addLayout(self.vBoxRadioModeButtons, QtCore.Qt.AlignLeft)
        self.hBox1.addWidget(self.buttonPause, QtCore.Qt.AlignLeft)
        self.hBox1.addWidget(self.buttonStart, QtCore.Qt.AlignLeft)
        
        # Slider Risk level
        self.lblRiskLevelSlider1 = QtGui.QLabel("Risk level: ");
        self.lblRiskLevelSlider1.setFixedWidth(140)
        self.lblRiskLevelSlider2 = QtGui.QLabel("Low");
        self.lblRiskLevelSlider2.setFixedWidth(30);
        self.lblRiskLevelSlider3 = QtGui.QLabel("High");
        self.lblRiskLevelSlider3.setFixedWidth(30)
        self.sliderRiskLevel = SliderHoverRiskLevel(self.lblToolTip, QtCore.Qt.Horizontal)
        self.sliderRiskLevel.setMinimum(0)
        self.sliderRiskLevel.setMaximum(100)
        self.sliderRiskLevel.setFixedWidth(130)
        self.sliderRiskLevel.setValue(round((theConfig.CONFIG_RiskLinePercentsAboveThresholdToBuy - theConfig.CONFIG_RISK_LINE_PERCENTS_ABOVE_THRESHOLD_TO_BUY_MIN) * 100 / (theConfig.CONFIG_RISK_LINE_PERCENTS_ABOVE_THRESHOLD_TO_BUY_MAX - theConfig.CONFIG_RISK_LINE_PERCENTS_ABOVE_THRESHOLD_TO_BUY_MIN)))
        self.sliderRiskLevel.valueChanged.connect(self.EventMovedSliderRiskLevel)
        self.sliderRiskLevel.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.EventMovedSliderRiskLevel() # Refresh trading parameter according to slider initial position
        self.lblRiskLevelSlider1.setStyleSheet(self.STR_QLABEL_STYLESHEET)
        self.lblRiskLevelSlider2.setStyleSheet(self.STR_QLABEL_STYLESHEET)
        self.lblRiskLevelSlider3.setStyleSheet(self.STR_QLABEL_STYLESHEET)
        self.sliderRiskLevel.setStyleSheet(self.STR_QSLIDER_STYLESHEET)
        
        self.lblSensitivityLevelSlider1 = QtGui.QLabel("Dips sensitivity: ");
        self.lblSensitivityLevelSlider1.setFixedWidth(140)
        self.lblSensitivityLevelSlider2 = QtGui.QLabel("Low");
        self.lblSensitivityLevelSlider2.setFixedWidth(30)
        self.lblSensitivityLevelSlider3 = QtGui.QLabel("High");
        self.lblSensitivityLevelSlider3.setFixedWidth(30)
        self.sliderSensitivityLevel = SliderHoverSensitivityLevel(self.lblToolTip, QtCore.Qt.Horizontal)
        self.sliderSensitivityLevel.setMinimum(1)
        self.sliderSensitivityLevel.setMaximum(6)
        self.sliderSensitivityLevel.setTickInterval(1)
        self.sliderSensitivityLevel.setSingleStep(1)
        self.sliderSensitivityLevel.setFixedWidth(130)
        self.sliderSensitivityLevel.setValue(self.currentSensitivitySliderValue)
        self.sliderSensitivityLevel.setTickPosition(QtGui.QSlider.TicksBelow)
        self.sliderSensitivityLevel.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.sliderSensitivityLevel.valueChanged.connect(self.EventMovedSliderSensitivityLevel)
        self.lblSensitivityLevelSlider1.setStyleSheet(self.STR_QLABEL_STYLESHEET)
        self.lblSensitivityLevelSlider2.setStyleSheet(self.STR_QLABEL_STYLESHEET)
        self.lblSensitivityLevelSlider3.setStyleSheet(self.STR_QLABEL_STYLESHEET)
        self.sliderSensitivityLevel.setStyleSheet(self.STR_QSLIDER_STYLESHEET)
        
        self.vBoxSliders.addLayout(self.hBoxSliders1, QtCore.Qt.AlignLeft)
        self.vBoxSliders.addLayout(self.hBoxSliders2, QtCore.Qt.AlignLeft)
        self.hBoxSliders1.addWidget(self.lblRiskLevelSlider1, QtCore.Qt.AlignLeft)
        self.hBoxSliders1.addWidget(self.lblRiskLevelSlider2)
        self.hBoxSliders1.addWidget(self.sliderRiskLevel)
        self.hBoxSliders1.addWidget(self.lblRiskLevelSlider3)
        self.hBoxSliders2.addWidget(self.lblSensitivityLevelSlider1, QtCore.Qt.AlignLeft)
        self.hBoxSliders2.addWidget(self.lblSensitivityLevelSlider2)
        self.hBoxSliders2.addWidget(self.sliderSensitivityLevel)
        self.hBoxSliders2.addWidget(self.lblSensitivityLevelSlider3)

        
        # Part 2
        self.lblLivePrice = QtGui.QLabel()
        self.STR_LABEL_MONEY_MIDDLEMARKET_PRICE = self.theSettings.SETT_GetSettings()["strCryptoType"] + str(" ") + str(self.STR_LABEL_MONEY_MIDDLEMARKET_PRICE)
        self.lblLivePrice.setText(self.STR_LABEL_MONEY_MIDDLEMARKET_PRICE)
        self.lblInfo = LabelClickable(self.STR_LABEL_INFO)
        self.lblInfo.setFixedHeight(24)
        self.lblCurrentState = QtGui.QLabel(self.STR_LABEL_CURRENT_STATE)
        self.lblFiatBalance = QtGui.QLabel(self.STR_LABEL_FIAT_BALANCE)
        self.lblCryptoMoneyBalance = QtGui.QLabel(self.STR_LABEL_CRYPTO_BALANCE)
        self.lblCryptoMoneyBalance.setFixedHeight(20)
        self.lblTotalGains = QtGui.QLabel(self.STR_LABEL_TOTAL_GAINS)
        
        self.lblLivePrice.setStyleSheet(self.STR_QLABEL_STYLESHEET);
        self.lblInfo.setStyleSheet(self.STR_QLABEL_STYLESHEET);
        self.lblCurrentState.setStyleSheet(self.STR_QLABEL_STYLESHEET);
        self.lblFiatBalance.setStyleSheet(self.STR_QLABEL_STYLESHEET);
        self.lblCryptoMoneyBalance.setStyleSheet(self.STR_QLABEL_STYLESHEET);
        self.lblTotalGains.setStyleSheet(self.STR_QLABEL_STYLESHEET);
        
        # Add widgets to layout
        self.mainGridLayout = QtGui.QGridLayout()   
        
        self.mainGridLayout.addWidget(self.rootMiddleBlock1, 5, 0, 1, 4)
        self.mainGridLayout.addWidget(self.lblLivePrice, 1, 2)
        self.mainGridLayout.addWidget(self.lblCurrentState, 2, 2)
        self.mainGridLayout.addWidget(self.lblInfo, 4, 1, 1, 2)
        self.mainGridLayout.addWidget(self.lblFiatBalance, 1, 1, QtCore.Qt.AlignLeft)
        self.mainGridLayout.addWidget(self.lblCryptoMoneyBalance, 2, 1, QtCore.Qt.AlignLeft)
        self.mainGridLayout.addWidget(self.lblTotalGains, 3, 1, QtCore.Qt.AlignLeft)
        self.mainGridLayout.addLayout(self.hBox1, 6, 1, QtCore.Qt.AlignLeft)
        self.mainGridLayout.addLayout(self.vBoxSliders, 6, 2, QtCore.Qt.AlignLeft)
        self.mainGridLayout.addWidget(self.rootMiddleBlock2, 7, 0, 1, 4)
        
        
        # Each column of the grid layout has the same total width proportion 
        self.mainGridLayout.setColumnStretch(1, 1)
        self.mainGridLayout.setColumnStretch(2, 1)
        self.mainGridLayout.setRowStretch(10, 2)
    
    def initializeGraphWidgets(self):
        
        pg.setConfigOption('foreground', 'w')
        pg.setConfigOption('background', (32, 48, 68))
        pg.GraphicsLayout(border=(100,100,100))
        
        self.strPlot1Title = str(self.theSettings.SETT_GetSettings()["strTradingPair"]) + ' Coinbase Pro Market Price (' + str(self.theSettings.SETT_GetSettings()["strFiatType"]) + ')'
        self.plot1 = pg.PlotWidget(title=self.strPlot1Title, axisItems={'bottom': TimeAxisItem(orientation='bottom')})        
        self.plot1.setYRange(self.minInPlot1, self.maxInPlot1)
        self.plot1.setMouseEnabled(False, False) # Mettre False, True pour release
        self.plot1.setMenuEnabled(False)
        axis = self.plot1.getAxis('bottom')  # This is the trick
        axis.setStyle(textFillLimits = [(0, 0.7)])
        
        #self.plot1.plotItem.vb.setBackgroundColor((15, 25, 34, 255))
        self.plot2 = pg.PlotWidget(title='Astibot decision indicator (normalized)')
        self.plot2.showGrid(x=True,y=True,alpha=0.1)
        self.plot2.setYRange(-100, 100)
        self.plot2.setMouseEnabled(False, True)
        self.plot2.setMouseEnabled(False)
        self.plot2.hideAxis('bottom')
        
        # Graphs take one row but 2 columns
        self.mainGridLayout.addWidget(self.plot1, 9, 1, 1, 2)
        self.mainGridLayout.addWidget(self.plot2, 10, 1, 1, 2)
   
        # Graph curves initialization
        self.plot1GraphLivePrice = self.plot1.plot(x=self.graphDataTime, y=self.graphDataBitcoinPrice, name='     Price') # , clipToView=True
        self.plot1GraphLivePrice.setPen(color=(220,220,220), width=3)
        self.plot1GraphSmoothPriceFast = self.plot1.plot(x=self.graphDataTime, y=self.graphDataBitcoinPriceSmoothFast, name='    Price Fast MA')
        self.plot1GraphSmoothPriceFast.setPen(color=(3,86,243), width=2)
        self.plot1GraphSmoothPriceSlow = self.plot1.plot(x=self.graphDataTime, y=self.graphDataBitcoinPriceSmoothSlow, name='    Price Slow MA')
        self.plot1GraphSmoothPriceSlow.setPen(color=(230,79,6), width=2)        
        self.plot1GraphRiskLine = self.plot1.plot(x=self.graphDataTime, y=self.graphDataBitcoinRiskLine, name='    Risk Line')
        self.plot1GraphRiskLine.setPen(color=(255,46,46), width=2, style=QtCore.Qt.DotLine) 
        self.plot1Markers1 = self.plot1.plot(x=self.graphDataTime, y=self.graphDataBitcoinPriceMarker1, name='      Buy', pen=None, symbol='o', symbolPen=(43, 206, 55), symbolBrush=(43, 206, 55), symbolSize = 30)
        self.plot1Markers2 = self.plot1.plot(x=self.graphDataTime, y=self.graphDataBitcoinPriceMarker2, name='      Sell', pen=None, symbol='o', symbolPen=(255, 0, 0), symbolBrush=(255, 0, 0), symbolSize = 30)
 
        # Graph 2 (Indicators) curves initialization
        self.plot2GraphIndicatorMACD = self.plot2.plot(x=self.graphDataTime, y=self.graphDataIndicatorMACD, pen='y', name='     MACD')
   
        self.graphicObject = pg.GraphicsObject()
        
    def initInitialTimeVector(self, firstFutureSampleTimeStamp):
        np.set_printoptions(suppress=True)
        timeBetweenRetrievedSamplesInSec = 60
        startTimeValue = firstFutureSampleTimeStamp - (self.nbPointsOnPlot * timeBetweenRetrievedSamplesInSec)
        tempTimeVector = np.linspace(startTimeValue, firstFutureSampleTimeStamp, self.nbPointsOnPlot)
        self.timeOfLastSampleDisplayed = startTimeValue

        return tempTimeVector


    def UIGR_updateNextIterationData(self, newTime, newSpotPrice, newSmoothPriceFast, newSmoothPriceSlow, newRiskLineRawAvgValue, newIndicatorMACD):
        # Don't append data that were before the oldest time in the graphs and that are older than the last sample displayed
        if (newTime > self.timeOfLastSampleDisplayed):
             
            self.graphDataTime[-1] = newTime
            self.timeOfLastSampleDisplayed = newTime
            self.graphDataBitcoinPrice[-1] = newSpotPrice
            self.graphDataBitcoinPriceSmoothFast[-1] = newSmoothPriceFast
            self.graphDataBitcoinPriceSmoothSlow[-1] = newSmoothPriceSlow
            self.graphDataBitcoinPriceMarker1[-1] = 0
            self.graphDataBitcoinPriceMarker2[-1] = 0
            self.currentRiskLineRawAvgValue = newRiskLineRawAvgValue
            self.graphDataBitcoinRiskLine.fill(newRiskLineRawAvgValue * theConfig.CONFIG_RiskLinePercentsAboveThresholdToBuy)
             
            self.graphDataIndicatorMACD[-1] = newIndicatorMACD
     
            # Shift data in the array one sample left (see also: np.roll)
            self.graphDataTime[:-1] = self.graphDataTime[1:]
            self.graphDataBitcoinPrice[:-1] = self.graphDataBitcoinPrice[1:]     
            self.graphDataBitcoinPriceSmoothFast[:-1] = self.graphDataBitcoinPriceSmoothFast[1:] 
            self.graphDataBitcoinPriceSmoothSlow[:-1] = self.graphDataBitcoinPriceSmoothSlow[1:]
            self.graphDataBitcoinPriceMarker1[:-1] = self.graphDataBitcoinPriceMarker1[1:]
            self.graphDataBitcoinPriceMarker2[:-1] = self.graphDataBitcoinPriceMarker2[1:]
            self.graphDataBitcoinRiskLine[:-1] = self.graphDataBitcoinRiskLine[1:]
            self.graphDataIndicatorMACD[:-1] = self.graphDataIndicatorMACD[1:]
             
            self.totalNbIterations = self.totalNbIterations + 1


    # Experimentation pour live trading aussi
    def UIGR_updateGraphsSimuTimer(self):
        if (theConfig.CONFIG_INPUT_MODE_IS_REAL_MARKET == False):
            if (self.totalNbIterations > theConfig.CONFIG_NB_POINTS_INIT_SIMU_GRAPH):
                self.UIGR_updateGraphs()
                self.totalNbGraphUpdates = self.totalNbGraphUpdates + 1
                
                # Perform UI apdates that were requested from the background thread
                self.UIGR_SAFE_updatePriceLbl()
                
                if (self.safeUIRefreshIsRequested == True):
                    self.safeUIRefreshIsRequested = False
                    self.UIGR_SAFE_updateInfoText()
                    self.UIGR_SAFE_updateTotalProfit()
                    self.UIGR_SAFE_updateAccountsBalance()
        else:
            self.UIGR_updateGraphs()
            
            # Perform UI updates that were requested from the background thread
            self.UIGR_SAFE_updatePriceLbl()
             
            if (self.safeUIRefreshIsRequested == True):
                self.safeUIRefreshIsRequested = False
                self.UIGR_SAFE_updateInfoText()
                self.UIGR_SAFE_updateTotalProfit()
                self.UIGR_SAFE_updateAccountsBalance()
            
            
    def UIGR_updateGraphs(self):
        
        self.plot1GraphLivePrice.setData(x=self.graphDataTime, y=self.graphDataBitcoinPrice)
        self.plot1GraphSmoothPriceFast.setData(x=self.graphDataTime, y=self.graphDataBitcoinPriceSmoothFast)
        self.plot1GraphSmoothPriceSlow.setData(x=self.graphDataTime, y=self.graphDataBitcoinPriceSmoothSlow)
        self.plot1Markers1.setData(x=self.graphDataTime, y=self.graphDataBitcoinPriceMarker1)
        self.plot1Markers2.setData(x=self.graphDataTime, y=self.graphDataBitcoinPriceMarker2)
        self.plot1GraphRiskLine.setData(x=self.graphDataTime, y=self.graphDataBitcoinRiskLine)
        self.plot2GraphIndicatorMACD.setData(x=self.graphDataTime, y=self.graphDataIndicatorMACD, fillLevel=0, brush=(255, 243, 20, 80))
   
        # Update Y avis scale in live market mode
        if (theConfig.CONFIG_INPUT_MODE_IS_REAL_MARKET == True):
            if (self.totalNbIterations > 1): # Avoid computing min on a full of zeros array which throws an exception
                maxInPlot1 = np.amax(self.graphDataBitcoinPrice) * self.Y_AXIS_TOP_MARGIN_IN_EXTREMUM_PERCENT
                minInPlot1 = (min(i for i in self.graphDataBitcoinPrice if i > 0)) * self.Y_AXIS_BOTTOM_MARGIN_IN_EXTREMUM_PERCENT
                # Set larget Y scaling if chart amplitude is too weak
                if ((maxInPlot1 - minInPlot1) < (self.graphDataBitcoinPrice[-1] * 0.02)):
                    maxInPlot1 = maxInPlot1 * 1.006
                    minInPlot1 = minInPlot1 * 0.994
            else:
                minInPlot1 = self.PLOT1_DEFAULT_MINIMUM
                maxInPlot1 = self.PLOT1_DEFAULT_MAXIMUM
             
            # Y range update only on change to avoid permanent axis rescaling which affects the user experience when zomming
            if ((self.minInPlot1 != minInPlot1) or (self.maxInPlot1 != maxInPlot1)):
                self.minInPlot1 = minInPlot1
                self.maxInPlot1 = maxInPlot1
                self.plot1.setYRange(minInPlot1, maxInPlot1)
                
            # Force UI refresh. After a long running time, UI refresh is not automatic sometimes
            QtGui.QApplication.processEvents()
            self.plot1.update()
        else:
            # Simulation mode
            if (self.totalNbIterations > 1): # Avoid computing min on a full of zeros array which throws an exception
                if (self.totalNbGraphUpdates % 4 == 0): 
                    maxInPlot1 = np.amax(self.graphDataBitcoinPrice) * self.Y_AXIS_TOP_MARGIN_IN_EXTREMUM_PERCENT
                    minInPlot1 = (min(i for i in self.graphDataBitcoinPrice if i > 0)) * self.Y_AXIS_BOTTOM_MARGIN_IN_EXTREMUM_PERCENT
                    # Set larget Y scaling if chart amplitude is too weak
                    if ((maxInPlot1 - minInPlot1) < (self.graphDataBitcoinPrice[-1] * 0.02)):
                        maxInPlot1 = maxInPlot1 * 1.006
                        minInPlot1 = minInPlot1 * 0.994
                 
                    # Y range update only on change to avoid permanent axis rescaling which affects the user experience when zomming
                    if ((self.minInPlot1 != minInPlot1) or (self.maxInPlot1 != maxInPlot1)):
                        self.minInPlot1 = minInPlot1
                        self.maxInPlot1 = maxInPlot1
                        self.plot1.setYRange(minInPlot1, maxInPlot1)
                                 
                    # Every 3 refreshes is sufficient
                    QtGui.QApplication.processEvents()
                    self.plot1.update()
         
            # Shall be at the end
            self.areNewSamplesRequested = True

    
    def UIGR_performManualYRangeRefresh(self):
        if (self.totalNbIterations > 1): # Avoid computing min on a full of zeros array which throws an exception
            maxInPlot1 = np.amax(self.graphDataBitcoinPrice) * self.Y_AXIS_TOP_MARGIN_IN_EXTREMUM_PERCENT
            minInPlot1 = (min(i for i in self.graphDataBitcoinPrice if i > 0)) * self.Y_AXIS_BOTTOM_MARGIN_IN_EXTREMUM_PERCENT
            # Set larget Y scaling if chart amplitude is too weak
            if ((maxInPlot1 - minInPlot1) < (self.graphDataBitcoinPrice[-1] * 0.02)):
                maxInPlot1 = maxInPlot1 * 1.006
                minInPlot1 = minInPlot1 * 0.994
        else:
            minInPlot1 = self.PLOT1_DEFAULT_MINIMUM
            maxInPlot1 = self.PLOT1_DEFAULT_MAXIMUM
         
        # Y range update only on change to avoid permanent axis rescaling which affects the user experience when zomming
        if ((self.minInPlot1 != minInPlot1) or (self.maxInPlot1 != maxInPlot1)):
            self.minInPlot1 = minInPlot1
            self.maxInPlot1 = maxInPlot1
            self.plot1.setYRange(minInPlot1, maxInPlot1)    

        
    def UIGR_updateAccountsBalance(self, EURBalance, CryptoBalance):
        self.strEURBalance = str(EURBalance)
        
        # Avoid display like 1e-7
        if (CryptoBalance <= theConfig.CONFIG_CRYPTO_PRICE_QUANTUM):
            CryptoBalance = 0.0
        self.strCryptoBalance = str(CryptoBalance)
        
        # If there's no risk from being called from a background thread, update UI here
        if (self.isContinuousGraphRefreshEnabled == False):
            if (theConfig.CONFIG_INPUT_MODE_IS_REAL_MARKET == True):
                strSimulationPrecision = ""
            else:
                strSimulationPrecision = " (Simulation)"
            self.lblFiatBalance.setText(self.STR_LABEL_FIAT_BALANCE + self.strEURBalance + ' ' + str(self.theSettings.SETT_GetSettings()["strFiatType"]) + strSimulationPrecision)
            self.lblCryptoMoneyBalance.setText(self.STR_LABEL_CRYPTO_BALANCE + self.strCryptoBalance + ' ' + str(self.theSettings.SETT_GetSettings()["strCryptoType"]) + strSimulationPrecision)
        else:
            self.safeUIRefreshIsRequested = True
            
    def UIGR_SAFE_updateAccountsBalance(self):
        if (theConfig.CONFIG_INPUT_MODE_IS_REAL_MARKET == True):
            strSimulationPrecision = ""
        else:
            strSimulationPrecision = " (Simulation)"
        self.lblFiatBalance.setText(self.STR_LABEL_FIAT_BALANCE + self.strEURBalance + ' ' + str(self.theSettings.SETT_GetSettings()["strFiatType"]) + strSimulationPrecision)
        self.lblCryptoMoneyBalance.setText(self.STR_LABEL_CRYPTO_BALANCE + self.strCryptoBalance + ' ' + str(self.theSettings.SETT_GetSettings()["strCryptoType"]) + strSimulationPrecision)

                        
    def UIGR_updatePriceLbl(self, newPrice):

        self.priceLabelStr = str(newPrice)
        
        # If there's no risk from being called from a background thread, update UI here
        if (self.isContinuousGraphRefreshEnabled == False):
            self.lblLivePrice.setText(self.STR_LABEL_MONEY_MIDDLEMARKET_PRICE + self.priceLabelStr + " " + str(self.theSettings.SETT_GetSettings()["strFiatType"]))
        else:
            pass # No need to set a flag, price lbl update is automatic in background
    
                
    def UIGR_SAFE_updatePriceLbl(self):
        self.lblLivePrice.setText(self.STR_LABEL_MONEY_MIDDLEMARKET_PRICE + self.priceLabelStr + " " + str(self.theSettings.SETT_GetSettings()["strFiatType"]))
          
    def UIGR_updateCurrentState(self, newState, isLiveTrading, blink):
        if (blink == True):
            self.isLblCurrentStateBlinking = True
        else:
            self.isLblCurrentStateBlinking = False
            self.lblCurrentState.setVisible(True)
            
        self.lblCurrentState.setText(str(newState))
        if (isLiveTrading == True):
            self.lblCurrentState.setStyleSheet(self.STR_QLABEL_CURRENT_STATE_LIVE_TRADING_STYLESHEET)
        else:
            self.lblCurrentState.setStyleSheet(self.STR_QLABEL_STYLESHEET)
    
    def UIGR_toogleStatus(self):
        self.lblCurrentState.setVisible(False);
        
    def UIGR_updateTotalProfit(self, realProfit, theoricProfit, percentageProfit, isSimulation):
        self.realProfit = realProfit
        self.theoricProfit = theoricProfit
        self.percentageProfit = percentageProfit
        self.displayProfitAsInSimulation = isSimulation
        
        # If there's no risk from being called from a background thread, update UI here
        if (self.isContinuousGraphRefreshEnabled == False):
            if (self.displayProfitAsInSimulation == True):
                self.lblTotalGains.setText(self.STR_LABEL_TOTAL_GAINS + str(self.theoricProfit) + " " + str(self.theSettings.SETT_GetSettings()["strFiatType"]) + " (" + str(self.percentageProfit) + "%) (Simulation)")
            else:
                self.lblTotalGains.setText(self.STR_LABEL_TOTAL_GAINS + str(self.realProfit) + " " + str(self.theSettings.SETT_GetSettings()["strFiatType"]) + " (Theoric: " + str(self.theoricProfit) + " " + str(self.theSettings.SETT_GetSettings()["strFiatType"]) + ")" + " (" + str(self.percentageProfit) + "%)")
             
            if (self.theoricProfit > 0):
                self.lblTotalGains.setStyleSheet(self.STR_QLABEL_PROFIT_GREEN_STYLESHEET)
            elif (self.theoricProfit < 0):
                self.lblTotalGains.setStyleSheet(self.STR_QLABEL_PROFIT_RED_STYLESHEET)
            else:
                self.lblTotalGains.setStyleSheet(self.STR_QLABEL_STYLESHEET)    
        else:
            self.safeUIRefreshIsRequested = True
    
    def UIGR_SAFE_updateTotalProfit(self):
        if (self.displayProfitAsInSimulation == True):
            self.lblTotalGains.setText(self.STR_LABEL_TOTAL_GAINS + str(self.theoricProfit) + " " + str(self.theSettings.SETT_GetSettings()["strFiatType"]) + " (" + str(self.percentageProfit) + "%) (Simulation)")
        else:
            self.lblTotalGains.setText(self.STR_LABEL_TOTAL_GAINS + str(self.realProfit) + " " + str(self.theSettings.SETT_GetSettings()["strFiatType"]) + " (Theoric: " + str(self.theoricProfit) + " " + str(self.theSettings.SETT_GetSettings()["strFiatType"]) + ")"  + " (" + str(self.percentageProfit) + "%)")
         
        if (self.theoricProfit > 0):
            self.lblTotalGains.setStyleSheet(self.STR_QLABEL_PROFIT_GREEN_STYLESHEET)
        elif (self.theoricProfit < 0):
            self.lblTotalGains.setStyleSheet(self.STR_QLABEL_PROFIT_RED_STYLESHEET)            
        else:
            self.lblTotalGains.setStyleSheet(self.STR_QLABEL_STYLESHEET)    
            
      
    def UIGR_updateInfoText(self, newInfoText, isError):
        self.lblInfoInErrorStyle = isError
        self.lblInfoStr = newInfoText
        
        # If there's no risk from being called from a background thread, update UI here
        if (self.isContinuousGraphRefreshEnabled == False):
            # Actual update
            self.lblInfo.setText(self.lblInfoStr)         
            if (self.lblInfoInErrorStyle == True):
                self.lblInfo.setStyleSheet(self.STR_QLABEL_INFO_ERROR_STYLESHEET)
            else:
                self.lblInfo.setStyleSheet(self.STR_QLABEL_INFO_STYLESHEET);
                
            # Automatic style change if needed
            if ((("Welcome" in self.lblInfoStr) == True)):
                self.lblInfo.setStyleSheet(self.STR_QLABEL_INFO_GREEN_STYLESHEET)
                self.lblInfo.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
            elif (("here to unlock" in self.lblInfoStr) == True):
                self.lblInfo.setStyleSheet(self.STR_QLABEL_INFO_ORANGE_STYLESHEET)
                self.lblInfo.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
            else:
                # Set default cursor back
                self.lblInfo.setCursor(QtGui.QCursor(QtCore.Qt.ArrowCursor))
        else:
            self.safeUIRefreshIsRequested = True

    def UIGR_SAFE_updateInfoText(self):
        self.lblInfo.setText(self.lblInfoStr)         
        if (self.lblInfoInErrorStyle == True):
            self.lblInfo.setStyleSheet(self.STR_QLABEL_INFO_ERROR_STYLESHEET);
        else:
            self.lblInfo.setStyleSheet(self.STR_QLABEL_INFO_STYLESHEET);
        pass
        
    def UIGR_updateLoadingDataProgress(self, progressInPercent):
        if (self.buttonStart.text() != "Start"):
            self.buttonStart.setText("Loading\nData...\n%s%%" % progressInPercent)
        
    def TimerRaisedBlinkWidgets(self):
        if (self.isLblCurrentStateBlinking == True):
            if (self.lblCurrentState.isVisible() == False):
                self.lblCurrentState.setVisible(True)
            else:
                self.lblCurrentState.setVisible(False)
    
    def UIGR_resetConnectionText(self):
        self.lblConnection.setText("")
          
    def UIGR_updateConnectionText(self, newText):
        if (self.lblConnection.text() == ""):
            self.lblConnection.setText(newText)

    def UIGR_updateLiveData(self, newData):
        self.strLiveData = (str(newData)[:100])

    def UIGR_updateLiveDataTimer(self):
        self.lblLiveData.setText(self.strLiveData)
    
    # Will be added to data on the next call to UIGR_updateNextIterationData()
    # Will be displayed on the next call to UIGR_updateGraphs
    # 1 => Buy marker
    # 2 => Sell marker
    # This function needs to be called after UIGR_updateNextIterationData to avoid the markers to be overwritten
    def UIGR_addMarker(self, markerNumber):
        print("UIGR - Marker added at %s" % self.graphDataBitcoinPrice[-1])
        if (markerNumber == 1):
            # Added on the last-but-one sample in order to avoid last sample to be overwritten by UIGR_updateNextIterationData
            self.graphDataBitcoinPriceMarker1[-2] = self.graphDataBitcoinPrice[-1]
            pass
        elif (markerNumber == 2):
            # Added on the last-but-one sample in order to avoid last sample to be overwritten by UIGR_updateNextIterationData
            self.graphDataBitcoinPriceMarker2[-2] = self.graphDataBitcoinPrice[-1]
            pass
             
    def UIGR_getRadioButtonSimulation(self):
        return self.radioButtonSimulation;

    def UIGR_getRadioButtonTrading(self):
        return self.radioButtonTrading;
    
    def UIGR_SetRadioButtonsEnabled(self, bEnable):
        self.radioButtonSimulation.setEnabled(bEnable)
        self.radioButtonTrading.setEnabled(bEnable)
        if (bEnable == True):
            self.radioButtonSimulation.setStyleSheet(self.STR_QRADIOBUTTON_STYLESHEET)
            self.radioButtonTrading.setStyleSheet(self.STR_QRADIOBUTTON_STYLESHEET)
        else:
            self.radioButtonSimulation.setStyleSheet(self.STR_QRADIOBUTTON_DISABLED_STYLESHEET)
            self.radioButtonTrading.setStyleSheet(self.STR_QRADIOBUTTON_DISABLED_STYLESHEET)
            
    def UIGR_SetStartButtonEnabled(self, bEnable):
        self.buttonStart.setEnabled(bEnable)
            
    def UIGR_SetStartButtonAspect(self, aspect):
        if (aspect == "START"):
            self.buttonStart.setText("Start")
            self.buttonStart.setStyleSheet(self.STR_QBUTTON_START_STYLESHEET)
        if (aspect == "START_DISABLED"):
            self.buttonStart.setText("Start")
            self.buttonStart.setStyleSheet(self.STR_QBUTTON_START_DISABLED_STYLESHEET)
        elif (aspect == "STOP"):
            self.buttonStart.setText("Stop")
            self.buttonStart.setStyleSheet(self.STR_QBUTTON_STOP_STYLESHEET)
        elif (aspect == "LOADING"):
            self.buttonStart.setText("Loading\ndata...")
            self.buttonStart.setStyleSheet(self.STR_QBUTTON_LOADING_STYLESHEET)
            
    def UIGR_SetPauseButtonEnabled(self, bEnable):
        self.buttonPause.setEnabled(bEnable)
        self.buttonPause.setVisible(bEnable)
        
    def UIGR_SetPauseButtonAspect(self, aspect):
        if (aspect == "PAUSE"):
            self.buttonPause.setText("Pause")
            self.buttonPause.setStyleSheet(self.STR_QBUTTON_PAUSE_STYLESHEET)
        if (aspect == "PAUSE_DISABLED"):
            self.buttonPause.setText("Pause")
            self.buttonPause.setStyleSheet(self.STR_QBUTTON_PAUSE_DISABLED_STYLESHEET)
        elif (aspect == "RESUME"):
            self.buttonPause.setText("Resume")
            self.buttonPause.setStyleSheet(self.STR_QBUTTON_PAUSE_STYLESHEET)
    
    def UIGR_SetSettingsButtonsEnabled(self, bEnable):
        self.buttonSettings.setEnabled(bEnable)
        if (bEnable == True):
            self.buttonSettings.setStyleSheet(self.STR_QBUTTON_SETTINGS_STYLESHEET)
        else:
            self.buttonSettings.setStyleSheet(self.STR_QBUTTON_SETTINGS_DISABLED_STYLESHEET)
    
    def UIGR_SetDonationButtonsEnabled(self, bEnable):
        self.buttonDonation.setEnabled(bEnable)
        if (bEnable == True):
            self.buttonDonation.setStyleSheet(self.STR_QBUTTON_SETTINGS_STYLESHEET)
        else:
            self.buttonDonation.setStyleSheet(self.STR_QBUTTON_SETTINGS_DISABLED_STYLESHEET)
            
    def UIGR_SetCurrentAppState(self, appState):
        self.currentAppState = appState
    
    # Perform UI actions due to a trading pair change
    def UIGR_NotifyThatTradingPairHasChanged(self):
        self.STR_LABEL_MONEY_MIDDLEMARKET_PRICE = self.theSettings.SETT_GetSettings()["strCryptoType"] + str(" MiddleMarket price : ")
        self.lblLivePrice.setText(self.STR_LABEL_MONEY_MIDDLEMARKET_PRICE)
        
        # Non destructive "search and replace" because of the possible '(Simulation)' annotation
        self.lblFiatBalance.setText(self.lblFiatBalance.text().replace("USD", "---"))
        self.lblFiatBalance.setText(self.lblFiatBalance.text().replace("EUR", "---"))
        self.lblFiatBalance.setText(self.lblFiatBalance.text().replace("---", self.theSettings.SETT_GetSettings()["strFiatType"]))
        
        self.lblCryptoMoneyBalance.setText(self.lblCryptoMoneyBalance.text().replace("USD", "---"))
        self.lblCryptoMoneyBalance.setText(self.lblCryptoMoneyBalance.text().replace("EUR", "---"))
        self.lblCryptoMoneyBalance.setText(self.lblCryptoMoneyBalance.text().replace("---", self.theSettings.SETT_GetSettings()["strFiatType"]))
        
        self.lblTotalGains.setText(self.lblTotalGains.text().replace("USD", "---"))
        self.lblTotalGains.setText(self.lblTotalGains.text().replace("EUR", "---"))
        self.lblTotalGains.setText(self.lblTotalGains.text().replace("---", self.theSettings.SETT_GetSettings()["strFiatType"]))
        
        self.STR_LABEL_FIAT_BALANCE = str(self.theSettings.SETT_GetSettings()["strFiatType"]) + " Account Balance : "
        self.STR_LABEL_CRYPTO_BALANCE = str(self.theSettings.SETT_GetSettings()["strCryptoType"]) + " Account Balance : "
        
        self.strPlot1Title = str(self.theSettings.SETT_GetSettings()["strTradingPair"]) + ' Coinbase Pro Market Price (' + str(self.theSettings.SETT_GetSettings()["strFiatType"]) + ')'
        self.plot1.setTitle(self.strPlot1Title)
        
        self.UIGR_ResetAllGraphData(True, -1, 600)
        
    def UIGR_SetTransactionManager(self, transactionManager):
        self.theUIDonation.UIDO_SetTransactionManager(transactionManager)
        
    def UIGR_RequestDonationWindowDisplay(self):
        self.theUIDonation.UIDO_ShowWindow()
        
    def UIGR_closeBackgroundOperations(self):
        self.timerUpdateLiveData.stop()
        
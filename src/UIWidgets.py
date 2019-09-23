import TradingBotConfig as theConfig
from pyqtgraph.Qt import QtCore, QtGui

class ButtonHoverStart(QtGui.QPushButton):

    def __init__(self, inLblToolTip, parent=None):
        super(QtGui.QPushButton, self).__init__(parent)
        self.lblToolTip = inLblToolTip

    def enterEvent(self, QEvent):
        if (theConfig.CONFIG_INPUT_MODE_IS_REAL_MARKET == True):
            self.lblToolTip.setText("Start / Stop live trading")            
        else:
            self.lblToolTip.setText("Start / Stop simulated trading")

    def leaveEvent(self, QEvent):
        self.lblToolTip.setText("")

class ButtonHoverPause(QtGui.QPushButton):

    def __init__(self, inLblToolTip, parent=None):
        super(QtGui.QPushButton, self).__init__(parent)
        self.lblToolTip = inLblToolTip

    def enterEvent(self, QEvent):
        self.lblToolTip.setText("Pause / Resume simulation")

    def leaveEvent(self, QEvent):
        self.lblToolTip.setText("")

class ButtonHoverSettings(QtGui.QPushButton):

    def __init__(self, inLblToolTip, parent=None):
        super(QtGui.QPushButton, self).__init__(parent)
        self.lblToolTip = inLblToolTip

    def enterEvent(self, QEvent):
        self.lblToolTip.setText("Open Settings page")

    def leaveEvent(self, QEvent):
        self.lblToolTip.setText("")
       
class ButtonHoverDonation(QtGui.QPushButton):

    def __init__(self, inLblToolTip, parent=None):
        super(QtGui.QPushButton, self).__init__(parent)
        self.lblToolTip = inLblToolTip

    def enterEvent(self, QEvent):
        self.lblToolTip.setText("Open Donation page")

    def leaveEvent(self, QEvent):
        self.lblToolTip.setText("")

class ButtonHoverInfo(QtGui.QPushButton):

    def __init__(self, inLblToolTip, parent=None):
        super(QtGui.QPushButton, self).__init__(parent)
        self.lblToolTip = inLblToolTip

    def enterEvent(self, QEvent):
        self.lblToolTip.setText("Open Information page")

    def leaveEvent(self, QEvent):
        self.lblToolTip.setText("")
                                    
class RadioHoverSimulation(QtGui.QRadioButton):

    def __init__(self, inLblToolTip, parent=None):
        super(QtGui.QRadioButton, self).__init__(parent)
        self.lblToolTip = inLblToolTip

    def enterEvent(self, QEvent):
        self.lblToolTip.setText("Simulation mode: In order to test your strategy, the bot operates on historic data and simulates the trades in order to estimate the money you could have earned. No real transaction is performed in this mode.")

    def leaveEvent(self, QEvent):
        self.lblToolTip.setText("")
        
class RadioHoverTrading(QtGui.QRadioButton):

    def __init__(self, inLblToolTip, parent=None):
        super(QtGui.QRadioButton, self).__init__(parent)
        self.lblToolTip = inLblToolTip

    def enterEvent(self, QEvent):
        self.lblToolTip.setText("Trading mode: Astibot trades on live market. It will buy the dips and sell the tops on the current trading pair. Refresh is performed every 10 seconds. Depending on the market, the first trade can be initiated a few minutes or hours after the start. By using this mode, you give Astibot the control of your account balance.")

    def leaveEvent(self, QEvent):
        self.lblToolTip.setText("")             

         
class SliderHoverRiskLevel(QtGui.QSlider):

    def __init__(self, inLblToolTip, parent=None):
        super(QtGui.QSlider, self).__init__(parent)
        self.lblToolTip = inLblToolTip

    def enterEvent(self, QEvent):
        self.lblToolTip.setText("Adjust the level of the red dashed line (risk line): Astibot will not buy if the current price value is above this line. This line is updated with the past hours average price and it is weighted with your setting.")

    def leaveEvent(self, QEvent):
        self.lblToolTip.setText("")  
        
class SliderHoverSensitivityLevel(QtGui.QSlider):

    def __init__(self, inLblToolTip, parent=None):
        super(QtGui.QSlider, self).__init__(parent)
        self.lblToolTip = inLblToolTip

    def enterEvent(self, QEvent):
        self.lblToolTip.setText("Sensitivity to dips and tops detection. If you change this setting, consequences will be visible after 1 to 2 hours as it affects the price smoothing")

    def leaveEvent(self, QEvent):
        self.lblToolTip.setText("")
        
class LabelClickable(QtGui.QLabel):
    
    def __init__(self, parent):
        QtGui.QLabel.__init__(self, parent)
        self.UIsAreSet = False
    
    def SetUIs(self, UISettings, UIDonation):
        self.theUISettings = UISettings
        self.theUIDonation = UIDonation
        self.UIsAreSet = True
        
    def mousePressEvent(self, event):
        print("QLabelMouseClick")
        
        if (self.UIsAreSet == True):
            if (("Welcome" in self.text()) == True):
                self.theUISettings.UIST_ShowWindow()
            elif (("here to unlock" in self.text()) == True):
                self.theUIDonation.UILI_ShowWindow()
    
                
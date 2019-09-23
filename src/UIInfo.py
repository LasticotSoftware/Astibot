import math
from pyqtgraph.Qt import QtCore, QtGui
from PyQt5.QtWidgets import QFrame
from PyQt5.Qt import QIntValidator
from PyQt5.Qt import QDoubleValidator
import ctypes # Message box popup

import TradingBotConfig as theConfig

class UIInfo(QtGui.QWidget):
    
    STR_CHECKBOX_AUTHORIZATION_TEXT = "I accept to give the present software a full control of my account through the Application Programming Interface. It includes algorithm-based buying or selling of fiat or cryptocurrency money / assets. I understand the risks related to software-based trading and, by entering here my personal API keys access, I am the only responsible for the totality of every action that is performed by this software through the API system even in case of bug, undesired software behavior, unfavorable market, inappropriate buy or sell decision. I have trained myself in Simulation mode to understand the Software trading strategy and, by entering my API keys, I only give control to money / assets that I can afford to loose."

    STR_BORDER_BLOCK_STYLESHEET = "QWidget {background-color : #151f2b;}"
    STR_QLABEL_STYLESHEET = "QLabel { background-color : #203044; color : white; font: 13px;}"
    STR_QLABEL_GREEN_STYLESHEET = "QLabel { background-color : #203044; color : #24b62e; font: bold 14px;}"
    STR_QLABEL_RED_STYLESHEET = "QLabel { background-color : #203044; color : #ff2e2e; font: bold 14px;}"
    STR_QLABEL_SMALL_STYLESHEET = "QLabel { background-color : #203044; color : #C2C2C2; font: 11px;}"
    STR_QCHECKBOX_STYLESHEET = "QCheckBox { background-color : #203044; color : white; font: 10px;}"
    STR_QCHECKBOX_LABEL_STYLESHEET = "QLabel { background-color : #203044; color : #C2C2C2; font: 10px;}"
    STR_QLABEL_TITLE_STYLESHEET = "QLabel { background-color : #203044; color : #81C6FE; font: bold 16px;}"
    STR_QFRAME_SEPARATOR_STYLESHEET = "background-color: rgb(20, 41, 58);"
    STR_QBUTTON_CLOSE_STYLESHEET = "QPushButton {background-color: #01599e; border-width: 2px; border-radius: 10px; border-color: white; font: bold 15px; color:white} QPushButton:pressed { background-color: #1d8d24 } QPushButton:hover { background-color: #002c4f }"
    STR_QBUTTON_WITHDRAW_ENABLED_STYLESHEET = "QPushButton {background-color: #23b42c; border-width: 2px; border-radius: 10px; border-color: white; font: bold 13px; color:white} QPushButton:pressed { background-color: #1d8d24 } QPushButton:hover { background-color: #1a821f }"
    STR_QBUTTON_WITHDRAW_DISABLED_STYLESHEET = "QPushButton {background-color: #9f9f9f; border-width: 2px; border-radius: 10px; border-color: white; font: bold 13px; color:white}"
    
    RIGHT_LABELS_WIDTH_IN_PX = 75
    
    def __init__(self):
        # Here, you should call the inherited class' init, which is QDialog
        QtGui.QWidget.__init__(self)
        
        print("UIFO - UI Info constructor")
        
        # Window settings
        #self.setWindowModality(QtCore.Qt.ApplicationModal)
        self.setWindowTitle('Astibot Information')
        self.setStyleSheet("background-color:#203044;")
        self.setWindowIcon(QtGui.QIcon("AstibotIcon.png"))
        self.setAutoFillBackground(True);
        self.setFixedSize(1060, 750)
        
        # Build layout
        self.BuildWindowLayout()


    def BuildWindowLayout(self):
        self.rootGridLayout = QtGui.QGridLayout()
        self.rootGridLayout.setContentsMargins(0, 0, 0, 0)    
        self.mainGridLayout = QtGui.QGridLayout()
        self.mainGridLayout.setContentsMargins(0, 0, 0, 0)       
        self.setLayout(self.rootGridLayout)
        self.rootGridLayout.addLayout(self.mainGridLayout, 1, 1)
        rowNumber = 0
        
        # Root left and right
        self.rootLeftBlock = QtGui.QWidget()
        self.rootLeftBlock.setStyleSheet(self.STR_BORDER_BLOCK_STYLESHEET)
        self.rootLeftBlock.setFixedWidth(20)
        self.rootRightBlock = QtGui.QWidget()
        self.rootRightBlock.setStyleSheet(self.STR_BORDER_BLOCK_STYLESHEET)
        self.rootRightBlock.setFixedWidth(20)
        self.rootGridLayout.addWidget(self.rootLeftBlock, 0, 0, 3, 1)
        self.rootGridLayout.addWidget(self.rootRightBlock, 0, 2, 3, 1)
        
        # Root top and bottom
        self.rootTopBlock = QtGui.QWidget()
        self.rootTopBlock.setStyleSheet(self.STR_BORDER_BLOCK_STYLESHEET)
        self.rootTopBlock.setFixedHeight(20)
        self.rootBottomBlock = QtGui.QWidget()
        self.rootBottomBlock.setStyleSheet(self.STR_BORDER_BLOCK_STYLESHEET)
        self.rootBottomBlock.setFixedHeight(60)
        self.rootGridLayout.addWidget(self.rootTopBlock, 0, 0, 1, 3)
        self.rootGridLayout.addWidget(self.rootBottomBlock, 2, 0, 1, 3)
        
        # Body layout ===========================================================
        self.mainGridLayout.setColumnStretch(0, 1)
        self.mainGridLayout.setColumnStretch(1, 10)
        
        # Section 1 ==================================================================================
        self.lblTitleSection1 = QtGui.QLabel("How does Astibot trading strategy work?")                
        self.lblTitleSection1.setStyleSheet(self.STR_QLABEL_TITLE_STYLESHEET);        
        self.mainGridLayout.addWidget(self.lblTitleSection1, rowNumber, 0, 1, 2)
        rowNumber = rowNumber + 1
        
                
        self.lblTxtSubtitle1 = QtGui.QLabel()
        self.lblTxtSubtitle1.setWordWrap(True)
        self.lblTxtSubtitle1.setStyleSheet(self.STR_QLABEL_STYLESHEET);   
        self.lblTxtSubtitle1.setText("<p style=\"margin-left: 20px\"><b>- In live trading mode:</b></p>")
        self.mainGridLayout.addWidget(self.lblTxtSubtitle1, rowNumber, 0, 1, 2)
        rowNumber = rowNumber + 1
        
        self.lblTxtSection11 = QtGui.QLabel()
        self.lblTxtSection11.setWordWrap(True)
        self.lblTxtSection11.setStyleSheet(self.STR_QLABEL_STYLESHEET);   
        self.lblTxtSection11.setText("<p style=\"margin-left: 45px\"><b></b>When running in live trading mode, Astibot updates the price chart every 10 seconds with the most recent middle-market price from Coinbase Pro exchange. It also computes a MACD-like indicator (bottom yellow graph) that helps finding buy and sell opportunities. Astibot strategy is simple:<br/><br/><b>1. Wait the dip.</b> First, Astibot is waiting for a buy opportunity. Ideally buy oppotunities are detected at the end of a dip.<br/><br/><b>2. Buy the dip. </b> If a buy opportunity is detected AND if the current price is below the red dashed line (the « risk line »), Astibot sends a market buy order to Coinbase Pro in order to buy the crypto asset. The amount of fiat money that is invested can be adjusted in the Settings.<br/><br/><b>3. Wait the top. </b> Astibot waits for the next sell oppotunity that would generate a positive profit, in other words which will at least cover the 2 market order fees (buy + sell fees).<br/><br/><b>4. Sell the top. </b> If a sell oppotunity meets the conditions explained at step 3, the entirety of your crypto asset balance is sold into fiat, and you funds should have increased. Then Astibot goes back to step 1 for another trade<br/>")
        self.mainGridLayout.addWidget(self.lblTxtSection11, rowNumber, 0, 1, 2)
        rowNumber = rowNumber + 1
        
        self.lblTxtSubtitle1 = QtGui.QLabel()
        self.lblTxtSubtitle1.setWordWrap(True)
        self.lblTxtSubtitle1.setStyleSheet(self.STR_QLABEL_STYLESHEET);   
        self.lblTxtSubtitle1.setText("<p style=\"margin-left: 20px\"><b>- In Simulation mode:</b></p>")
        self.mainGridLayout.addWidget(self.lblTxtSubtitle1, rowNumber, 0, 1, 2)
        rowNumber = rowNumber + 1
        
        self.lblTxtSection12 = QtGui.QLabel()
        self.lblTxtSection12.setWordWrap(True)
        self.lblTxtSection12.setStyleSheet(self.STR_QLABEL_STYLESHEET);   
        self.lblTxtSection12.setText("<p style=\"margin-left: 45px\"><b></b>In simulation mode, Trading strategy is the same as in Live trading mode, excepted that it is performed on historic samples that quickly scroll allowing you to test different tunnings or trading pairs. No orders are sent to Coinbase Pro in simulation mode, trades are entirely simulated. <br/>Simulation mode will familiarise you with Astibot trading strategy and how to tune it. <br/></p>")
        self.mainGridLayout.addWidget(self.lblTxtSection12, rowNumber, 0, 1, 2)
        rowNumber = rowNumber + 1
        
        # Section 2 ==================================================================================
        self.lblTitleSection2 = QtGui.QLabel("What is displayed on the graphs ?")                
        self.lblTitleSection2.setStyleSheet(self.STR_QLABEL_TITLE_STYLESHEET);        
        self.mainGridLayout.addWidget(self.lblTitleSection2, rowNumber, 0, 1, 2)
        rowNumber = rowNumber + 1        
            
        self.lblTxtSubtitle21 = QtGui.QLabel()
        self.lblTxtSubtitle21.setWordWrap(True)
        self.lblTxtSubtitle21.setStyleSheet(self.STR_QLABEL_STYLESHEET);   
        self.lblTxtSubtitle21.setText("<p style=\"margin-left: 20px\"><b>- Main Graph:</b></p>")
        self.mainGridLayout.addWidget(self.lblTxtSubtitle21, rowNumber, 0, 1, 2)
        rowNumber = rowNumber + 1
        
        # White chart -------------------------------
        self.lblChartWhite = QtGui.QLabel("")
        pixmap = QtGui.QPixmap('chart_white.png')
        self.lblChartWhite.setPixmap(pixmap)
        self.mainGridLayout.addWidget(self.lblChartWhite, rowNumber, 0, 1, 1, QtCore.Qt.AlignRight)
        
        self.lblTxtSection21 = QtGui.QLabel()
        self.lblTxtSection21.setWordWrap(True)
        self.lblTxtSection21.setStyleSheet(self.STR_QLABEL_STYLESHEET);   
        self.lblTxtSection21.setText("Estimate of the trading pair price")
        self.mainGridLayout.addWidget(self.lblTxtSection21, rowNumber, 1, 1, 1)
        rowNumber = rowNumber + 1
        
        # Orange chart -------------------------------
        self.lblChartOrange = QtGui.QLabel("")
        pixmap = QtGui.QPixmap('chart_orange.png')
        self.lblChartOrange.setPixmap(pixmap)
        self.mainGridLayout.addWidget(self.lblChartOrange, rowNumber, 0, 1, 1, QtCore.Qt.AlignRight)
        
        self.lblTxtSection22 = QtGui.QLabel()
        self.lblTxtSection22.setWordWrap(True)
        self.lblTxtSection22.setStyleSheet(self.STR_QLABEL_STYLESHEET);   
        self.lblTxtSection22.setText("Price slow moving average. The smoothing intensity can be set with the sensitivity cursor. This chart is used for the bottom (yellow graph) computation.")
        self.mainGridLayout.addWidget(self.lblTxtSection22, rowNumber, 1, 1, 1)
        rowNumber = rowNumber + 1
        
        # Blue chart -------------------------------
        self.lblChartBlue = QtGui.QLabel("")
        pixmap = QtGui.QPixmap('chart_blue.png')
        self.lblChartBlue.setPixmap(pixmap)
        self.mainGridLayout.addWidget(self.lblChartBlue, rowNumber, 0, 1, 1, QtCore.Qt.AlignRight)
        
        self.lblTxtSection23 = QtGui.QLabel()
        self.lblTxtSection23.setWordWrap(True)
        self.lblTxtSection23.setStyleSheet(self.STR_QLABEL_STYLESHEET);   
        self.lblTxtSection23.setText("Price fast moving average. The smoothing intensity can be set with the sensitivity cursor. This chart is used for the bottom (yellow graph) computation.")
        self.mainGridLayout.addWidget(self.lblTxtSection23, rowNumber, 1, 1, 1)
        rowNumber = rowNumber + 1
        
        # Red line -------------------------------
        self.lblChartRed = QtGui.QLabel("")
        pixmap = QtGui.QPixmap('chart_red.png')
        self.lblChartRed.setPixmap(pixmap)
        self.mainGridLayout.addWidget(self.lblChartRed, rowNumber, 0, 1, 1, QtCore.Qt.AlignRight)
        
        self.lblTxtSection24 = QtGui.QLabel()
        self.lblTxtSection24.setWordWrap(True)
        self.lblTxtSection24.setStyleSheet(self.STR_QLABEL_STYLESHEET);   
        self.lblTxtSection24.setText("Risk line: This is the maximum buy level. Astibot only performs buy transactions if the current price is below this line. The purpose of this line is to avoid opening a trade too high that could hardly be sold. You are free to set your own risk level thanks to the Risk level cursor.  This line also evolves automatically to match the average market level (based on the last few hours), but its value is weighted by the risk level you set.")
        self.mainGridLayout.addWidget(self.lblTxtSection24, rowNumber, 1, 1, 1)
        rowNumber = rowNumber + 1
        
        # Buy Sells symbols -------------------------------
        self.lblChartSymbols = QtGui.QLabel("")
        pixmap = QtGui.QPixmap('chart_symbols.png')
        self.lblChartSymbols.setPixmap(pixmap)
        self.mainGridLayout.addWidget(self.lblChartSymbols, rowNumber, 0, 1, 1, QtCore.Qt.AlignRight)
        
        self.lblTxtSection25 = QtGui.QLabel()
        self.lblTxtSection25.setWordWrap(True)
        self.lblTxtSection25.setStyleSheet(self.STR_QLABEL_STYLESHEET);   
        self.lblTxtSection25.setText("Approximate positions of the buy (green symbol) and sell (red symbol) transactions performed by Astibot.")
        self.mainGridLayout.addWidget(self.lblTxtSection25, rowNumber, 1, 1, 1)
        rowNumber = rowNumber + 1
        
        # Bottom chart -------------------------------
        self.lblTxtSubtitle21 = QtGui.QLabel()
        self.lblTxtSubtitle21.setWordWrap(True)
        self.lblTxtSubtitle21.setStyleSheet(self.STR_QLABEL_STYLESHEET);   
        self.lblTxtSubtitle21.setText("<p style=\"margin-left: 20px\"><b>- Bottom Graph:</b></p>")
        self.mainGridLayout.addWidget(self.lblTxtSubtitle21, rowNumber, 0, 1, 2)
        rowNumber = rowNumber + 1
        
        self.lblChartYellow = QtGui.QLabel("")
        pixmap = QtGui.QPixmap('chart_yellow.png')
        self.lblChartYellow.setPixmap(pixmap)
        self.mainGridLayout.addWidget(self.lblChartYellow, rowNumber, 0, 1, 1, QtCore.Qt.AlignRight)
        
        self.lblTxtSection26 = QtGui.QLabel()
        self.lblTxtSection26.setWordWrap(True)
        self.lblTxtSection26.setStyleSheet(self.STR_QLABEL_STYLESHEET);   
        self.lblTxtSection26.setText("<b></b>Decision indicator chart. It is computed with the subtraction of the blue and orange smoothed prices. It is similar to the well known MACD indicator. If it goes from negative to positive, Astibot will interpret it as a buy signal. A positive to negative change is identified as a sell signal. The influence of the sensitivity setting is directly visible on this graph as if you increase the sensitivity, more buy and sell signals will appear.")
        self.mainGridLayout.addWidget(self.lblTxtSection26, rowNumber, 1, 1, 1)
        rowNumber = rowNumber + 1
        
        # Bottom buttons ==================================================================================
        self.btnClose = QtGui.QPushButton("Close")
        self.btnClose.setStyleSheet(self.STR_QBUTTON_CLOSE_STYLESHEET)
        self.btnClose.setFixedWidth(120)
        self.btnClose.setFixedHeight(38)
        self.btnClose.clicked.connect(self.HideWindow)
        self.btnClose.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.hBoxBottomButtons = QtGui.QHBoxLayout()
        self.hBoxBottomButtons.addWidget(self.btnClose, QtCore.Qt.AlignRight)
        self.rootBottomBlock.setLayout(self.hBoxBottomButtons)
        rowNumber = rowNumber + 1
        
        
    def UIFO_ShowWindow(self):
        print("UIFO - Show")
        self.show()
        
    def HideWindow(self):
        self.hide()
        
import math
from pyqtgraph.Qt import QtCore, QtGui
from PyQt5.QtWidgets import QFrame
from PyQt5.Qt import QIntValidator
from PyQt5.Qt import QDoubleValidator
import ctypes # Message box popup

import TradingBotConfig as theConfig

class UIDonation(QtGui.QWidget):
    
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
    STR_QTEXTEDIT_STYLESHEET = "QLineEdit { background-color : #203044; color : white; font: bold 13px; border: 1px solid white; border-radius: 4px;} QLineEdit:focus {border: 2px solid #007ad9;}"
 
    RIGHT_LABELS_WIDTH_IN_PX = 75
    
    def __init__(self, settings):
        # Here, you should call the inherited class' init, which is QDialog
        QtGui.QWidget.__init__(self)
        
        print("UIDO - UI Donating constructor")
        
        # Application settings data instance
        self.theSettings = settings
        
        # Functional
        self.BTCBalance = -1.0
        self.windowIsShown = False
        self.timerRefreshBTCBalance = QtCore.QTimer()
        self.timerRefreshBTCBalance.timeout.connect(self.TimerRaisedRefreshBTCBalance)
        self.timerRefreshBTCBalance.start(200)
        self.withdrawHasBeenPerformed = False
    
        # Window settings
        self.setWindowModality(QtCore.Qt.ApplicationModal)
        self.setWindowTitle('Astibot')
        self.setStyleSheet("background-color:#203044;")
        self.setWindowIcon(QtGui.QIcon("AstibotIcon.png"))
        self.setAutoFillBackground(True);
        self.setFixedSize(450, 350)
        
        # Build layout
        self.BuildWindowLayout()

    def EventWithdrawButtonClick(self):
        print("UIDO - Withdraw Click")
        
        # Set to True to keep Withdraw button disabled during transaction
        self.withdrawHasBeenPerformed = True
        self.SetWithdrawEnabled(False)
        self.btnWithdrawForDonating.setText("Withdrawing...")        
        QtGui.QApplication.processEvents() # Force UI to update previous lines, because we will block main UI loop
        
        # Perform withdraw
        withdrawRequestReturn = self.theTransactionManager.TRNM_WithdrawBTC(theConfig.CONFIG_BTC_DESTINATION_ADDRESS, float(self.txtDonationAmountEntry.text()))
        
        if (withdrawRequestReturn != "Error"):
            self.btnWithdrawForDonating.setText("Withdraw successful!")
            self.MessageBoxPopup("Your donation has been successfully sent: Thank you! Coinbase Pro Transfer ID is %s" % withdrawRequestReturn, 0)
        else:
            self.MessageBoxPopup("The withdraw failed, you will not be charged. Make sure you authorized the transfer feature when creating your API key.", 0)
            self.btnWithdrawForDonating.setText("Withdraw failed")
            
    
    def EventCloseButtonClick(self):
        print("UIDO - Close Click")
        self.HideWindow()
    
    def TimerRaisedRefreshBTCBalance(self):
        if (self.windowIsShown == True):
            # Retrieve balance data
            self.BTCBalance = self.theTransactionManager.TRNM_getBTCBalance()            
            # Fast account refresh required in case the user would currently be withdrawing money, he would like to quickly see the update on the UI
            self.theTransactionManager.TRNM_ForceAccountsUpdate()
            
            try:
                if (float(self.BTCBalance) >= float(self.txtDonationAmountEntry.text()) and (float(self.txtDonationAmountEntry.text()) >= theConfig.MIN_CRYPTO_AMOUNT_REQUESTED_TO_SELL)):  
                    # If donation has just been performed, do not enable Withdraw button again
                    if (self.withdrawHasBeenPerformed == False):        
                        self.SetWithdrawEnabled(True)                        
                    self.lblAvailableBTCBalance.setText("%s BTC" % str(round(float(self.BTCBalance), 7)))
                else:
                    self.SetWithdrawEnabled(False)
                    self.lblAvailableBTCBalance.setText("%s BTC" % str(round(float(self.BTCBalance), 7)))
                self.btnWithdrawForDonating.setText("Donate %s BTC" % self.txtDonationAmountEntry.text())
            except ValueError:
                self.SetWithdrawEnabled(False)
                
                
    def SetWithdrawEnabled(self, bEnable):
        if (bEnable == True):
            self.btnWithdrawForDonating.setStyleSheet(self.STR_QBUTTON_WITHDRAW_ENABLED_STYLESHEET)
        else:
            self.btnWithdrawForDonating.setStyleSheet(self.STR_QBUTTON_WITHDRAW_DISABLED_STYLESHEET)
        
        self.btnWithdrawForDonating.setEnabled(bEnable)
            
    ##  Styles:
    ##  0 : OK
    ##  1 : OK | Cancel
    ##  2 : Abort | Retry | Ignore
    ##  3 : Yes | No | Cancel
    ##  4 : Yes | No
    ##  5 : Retry | No 
    ##  6 : Cancel | Try Again | Continue
    def MessageBoxPopup(self, text, style):
        title = "Astibot Donating"
        return ctypes.windll.user32.MessageBoxW(0, text, title, style)

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
        
        self.lblTitleDonating = QtGui.QLabel("Donate & Contribute to Astibot project")

                    
        self.lblTitleDonating.setStyleSheet(self.STR_QLABEL_TITLE_STYLESHEET);
        self.mainGridLayout.addWidget(self.lblTitleDonating, rowNumber, 0, 1, 2)
        rowNumber = rowNumber + 1
        
        self.lblSubTitleDonating = QtGui.QLabel("If you like this project or if you make money with it: please donate to help me make this software better!")        
        self.lblSubTitleDonating.setStyleSheet(self.STR_QLABEL_STYLESHEET);
        self.lblSubTitleDonating.setWordWrap(True)
        self.mainGridLayout.addWidget(self.lblSubTitleDonating, rowNumber, 0, 1, 2)        
        rowNumber = rowNumber + 1
        
        # Available BTC Balance
        self.lblAvailableBTCBalanceText = QtGui.QLabel("<b>Available BTC Balance:</b>")
        self.lblAvailableBTCBalanceText.setStyleSheet(self.STR_QLABEL_STYLESHEET);
        self.lblAvailableBTCBalanceText.setFixedHeight(28)
        if (self.BTCBalance >= 0):
            if (self.BTCBalance >= theConfig.CONFIG_DONATION_DEFAULT_AMOUNT_IN_BTC):
                self.lblAvailableBTCBalance = QtGui.QLabel("%s BTC" % str(round(float(self.BTCBalance))))
            else:
                self.lblAvailableBTCBalance = QtGui.QLabel("%s BTC (insufficient funds)" % str(round(float(self.BTCBalance))))
        else:
            self.lblAvailableBTCBalance = QtGui.QLabel("-- BTC")
        self.lblAvailableBTCBalance.setStyleSheet(self.STR_QLABEL_STYLESHEET);
        self.mainGridLayout.addWidget(self.lblAvailableBTCBalanceText, rowNumber, 0)
        self.mainGridLayout.addWidget(self.lblAvailableBTCBalance, rowNumber, 1)
        rowNumber = rowNumber + 1
        
        # Donation amount entry
        self.lblYourDonation = QtGui.QLabel("<b>Your donation (BTC):</b>")
        self.lblYourDonation.setStyleSheet(self.STR_QLABEL_STYLESHEET);
        self.lblYourDonation.setFixedHeight(28)
        
        self.txtDonationAmountEntry = QtGui.QLineEdit()
        self.txtDonationAmountEntry.setStyleSheet(self.STR_QTEXTEDIT_STYLESHEET)
        self.txtDonationAmountEntry.setFixedWidth(80)
        self.txtDonationAmountEntry.setText(str(theConfig.CONFIG_DONATION_DEFAULT_AMOUNT_IN_BTC))
        #self.txtDonationAmountEntry.changeEvent.connect(self.EventDonationAmountEntryChanged)
        
        self.mainGridLayout.addWidget(self.lblYourDonation, rowNumber, 0)
        self.mainGridLayout.addWidget(self.txtDonationAmountEntry, rowNumber, 1)
        rowNumber = rowNumber + 1
        
                
        # Withdraw button
        self.btnWithdrawForDonating = QtGui.QPushButton("Donate %s BTC" % theConfig.CONFIG_DONATION_DEFAULT_AMOUNT_IN_BTC)
        self.btnWithdrawForDonating.setStyleSheet(self.STR_QBUTTON_WITHDRAW_DISABLED_STYLESHEET)
        self.btnWithdrawForDonating.setFixedHeight(35)
        self.btnWithdrawForDonating.setFixedWidth(240)
        self.btnWithdrawForDonating.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.btnWithdrawForDonating.clicked.connect(self.EventWithdrawButtonClick)
        self.mainGridLayout.addWidget(self.btnWithdrawForDonating, rowNumber, 0, 1, 2, QtCore.Qt.AlignCenter)
        rowNumber = rowNumber + 1
        
        # Bottom buttons
        self.btnClose = QtGui.QPushButton("Close")
        self.btnClose.setStyleSheet(self.STR_QBUTTON_CLOSE_STYLESHEET)
        self.btnClose.setFixedWidth(120)
        self.btnClose.setFixedHeight(38)
        self.btnClose.clicked.connect(self.EventCloseButtonClick)
        self.btnClose.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.hBoxBottomButtons = QtGui.QHBoxLayout()
        self.hBoxBottomButtons.addWidget(self.btnClose, QtCore.Qt.AlignRight)
        self.rootBottomBlock.setLayout(self.hBoxBottomButtons)
        rowNumber = rowNumber + 1
        
        
    def UIDO_ShowWindow(self):
        print("UIDO - Show")
        self.windowIsShown = True
        self.withdrawHasBeenPerformed = False
        
        # Force refresh
        self.TimerRaisedRefreshBTCBalance()
        
        self.show()
        
    def HideWindow(self):
        self.windowIsShown = False
        self.hide()
        
    def UIDO_SetTransactionManager(self, transactionManager):
        self.theTransactionManager = transactionManager
        
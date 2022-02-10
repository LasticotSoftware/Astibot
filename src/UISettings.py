import math
from pyqtgraph.Qt import QtCore, QtGui
from PyQt5.QtWidgets import QFrame
from PyQt5.Qt import QIntValidator
from PyQt5.Qt import QDoubleValidator
from GDAXCurrencies import GDAXCurrencies
import ctypes # Message box popup

import TradingBotConfig as theConfig

class UISettings(QtGui.QWidget):

    STR_CHECKBOX_AUTHORIZATION_TEXT = "By entering your API keys, you accept to leave control of your Coinbase Pro account to this software through the Application Programming Interface (API). It includes algorithm-based buying or selling of fiat money or crypto-assets. You are the only responsible for the actions that are performed by this software through the API, even in case of unfavorable market, inappropriate buy or sell decision, software bug, undesired software behavior or any other undesired activity. Train yourself on the simulator before performing actual trading. Only give control to money / assets that you can afford to loose."

    STR_BORDER_BLOCK_STYLESHEET = "QWidget {background-color : #151f2b;}"
    STR_QLABEL_STYLESHEET = "QLabel { background-color : #203044; color : white; font: bold 13px;}"
    STR_QLABEL_NOTE_STYLESHEET = "QLabel { background-color : #203044; color : white; font: 12px;}"
    STR_QCHECKBOX_STYLESHEET = "QCheckBox { background-color : #203044; color : white; font: 10px;}"
    STR_QCHECKBOX_LABEL_STYLESHEET = "QLabel { background-color : #203044; color : #C2C2C2; font: 10px;}"
    STR_QLABEL_TITLE_STYLESHEET = "QLabel { background-color : #203044; color : #81C6FE; font: bold 16px;}"
    STR_QTEXTEDIT_STYLESHEET = "QLineEdit { background-color : #203044; color : white; font: bold 13px; border: 1px solid white; border-radius: 4px;} QLineEdit:focus {border: 2px solid #007ad9;}"
    STR_QTEXTEDIT_BLINK_STYLESHEET = "QLineEdit { background-color : #203044; color : white; font: bold 13px; border: 3px solid #00c11a; border-radius: 4px;} QLineEdit:focus {border: 3px solid #00c11a;}"
    STR_QFRAME_SEPARATOR_STYLESHEET = "background-color: rgb(28, 30, 28)"
    STR_COMBO_STYLESHEET = "QComboBox { background-color : #203044; color : white; font: bold bold 13px; border: 1px solid white; border-radius: 4px;} QComboBox:focus {border: 2px solid #007ad9;} QListView{color: white; font: bold 13px;} QListView:focus {border: 2px solid #007ad9;} QComboBox QAbstractItemView::item{min-height: 32px;}"
    STR_QSLIDER_STYLESHEET = "QSlider::handle:hover {background-color: #C6D0FF;}"
    STR_QBUTTON_APPLY_STYLESHEET = "QPushButton {background-color: #01599e; border-width: 2px; border-radius: 10px; border-color: white; font: bold 15px; color:white} QPushButton:pressed { background-color: #1d8d24 } QPushButton:hover { background-color: #002c4f }"
    STR_QBUTTON_CANCEL_STYLESHEET = "QPushButton {background-color: #7e8c98; border-width: 2px; border-radius: 10px; border-color: white; font: bold 15px; color:white} QPushButton:pressed { background-color: #bda300 } QPushButton:hover { background-color: #56616b }"

    RIGHT_LABELS_WIDTH_IN_PX = 75

    def __init__(self, settings):
        # Here, you should call the inherited class' init, which is QDialog
        QtGui.QWidget.__init__(self)

        print("UIST - UI Settings constructor")

        # Application settings data instance
        self.theSettings = settings

        # Window settings
        self.setWindowModality(QtCore.Qt.ApplicationModal)
        self.setWindowTitle('Astibot Settings')
        self.setStyleSheet("background-color:#203044;")
        self.setWindowIcon(QtGui.QIcon("AstibotIcon.png"))
        self.setAutoFillBackground(True);
        self.setFixedSize(646, 660)

        # Build layout
        self.BuildWindowLayout()

        # Timer to make API textboxes blink
        self.timerBlinkStuffs = QtCore.QTimer()
        self.timerBlinkStuffs.timeout.connect(self.TimerRaisedBlinkStuff)
        self.blinkIsOn = False
        self.blinkCounter = 0

        # Apply saved (or default) settings
        self.ApplySettings()


    def ApplySettings(self):
        self.txtAPIKey.setText(self.theSettings.SETT_GetSettings()["strAPIKey"])
        self.strAPIKeyApplicable = self.theSettings.SETT_GetSettings()["strAPIKey"]

        self.txtSecretKey.setText(self.theSettings.SETT_GetSettings()["strSecretKey"])
        self.strSecretKeyApplicable = self.theSettings.SETT_GetSettings()["strSecretKey"]

        self.txtPassPhrase.setText(self.theSettings.SETT_GetSettings()["strPassphrase"])
        self.strPassPhraseApplicable = self.theSettings.SETT_GetSettings()["strPassphrase"]

#         if (str(self.theSettings.SETT_GetSettings()["bHasAcceptedConditions"]) == "True"):
#             self.checkboxAuthorization.setChecked(True)
#         else:
#             self.checkboxAuthorization.setChecked(False)

        self.strTradingPair = self.theSettings.SETT_GetSettings()["strTradingPair"]
        self.strApplicableTradingPair = self.strTradingPair
        self.comboTradingPair.setCurrentIndex(GDAXCurrencies.get_index_for_currency_pair(self.strTradingPair))

        self.strFiatType = self.theSettings.SETT_GetSettings()["strFiatType"]
        self.strCryptoType = self.theSettings.SETT_GetSettings()["strCryptoType"]

        self.simulationTimeRange = self.theSettings.SETT_GetSettings()["simulationTimeRange"]
        if (self.simulationTimeRange == 24):
            self.comboSimulationTimeRange.setCurrentIndex(0)
        elif (self.simulationTimeRange == 48):
            self.comboSimulationTimeRange.setCurrentIndex(1)
        elif (self.simulationTimeRange == 72):
            self.comboSimulationTimeRange.setCurrentIndex(2)
        elif (self.simulationTimeRange == 168):
            self.comboSimulationTimeRange.setCurrentIndex(3)
        else:
            self.comboSimulationTimeRange.setCurrentIndex(0)

        self.investPercentage = self.theSettings.SETT_GetSettings()["investPercentage"]
        self.sliderFiatAmount.setValue(int(self.investPercentage))
        self.lblFiatAmountValue.setText(str(self.sliderFiatAmount.value()) + " %")

        self.platformTakerFee = self.theSettings.SETT_GetSettings()["platformTakerFee"]
        self.sliderTakerFee.setValue(float(self.platformTakerFee) * 20.0) # 20 = 1/quantum, a cabler
        self.lblTakerFeePercent.setText(str(self.platformTakerFee) + " %")

        self.sellTrigger = self.theSettings.SETT_GetSettings()["sellTrigger"]
        self.sliderSellTrigger.setValue(float(self.sellTrigger) * 20.0) # 20 = 1/quantum, a cabler)
        self.lblSellTriggerPercent.setText(str(self.sellTrigger) + " %")

        self.autoSellThreshold = self.theSettings.SETT_GetSettings()["autoSellThreshold"]
        self.sliderAutoSellThreshold.setValue(float(self.autoSellThreshold) * 4) # 4 = 1/quantum, a cabler
        self.lblAutoSellPercent.setText(str(self.autoSellThreshold) + " %")

        self.txtSimulatedFiatBalance.setText(str(self.theSettings.SETT_GetSettings()["simulatedFiatBalance"]))
        self.txtSimulatedFiatBalance.text().replace('.',',') # TODO: ok for french only

        self.simulationSpeed = self.theSettings.SETT_GetSettings()["simulationSpeed"]
        self.sliderSimulationSpeed.setValue(int(self.simulationSpeed))

    def EventApplylButtonClick(self):
        print("UIST - Apply Click")

        if (self.checkParametersValidity() == True):
            # Set settings
            settingsList = self.theSettings.SETT_GetSettings()

            settingsList["strAPIKey"] = self.txtAPIKey.text()
            if (str(settingsList["strAPIKey"]) != self.strAPIKeyApplicable):
                print("UIST - New API Key set")
                self.strAPIKeyApplicable = str(settingsList["strAPIKey"])
                self.theSettings.SETT_NotifyAPIDataHasChanged()

            settingsList["strSecretKey"] = self.txtSecretKey.text()
            if (str(settingsList["strSecretKey"]) != self.strSecretKeyApplicable):
                print("UIST - New Secret Key set")
                self.strSecretKeyApplicable = str(settingsList["strSecretKey"])
                self.theSettings.SETT_NotifyAPIDataHasChanged()

            settingsList["strPassphrase"] = self.txtPassPhrase.text()
            if (str(settingsList["strPassphrase"]) != self.strPassPhraseApplicable):
                print("UIST - New API Passphrase set")
                self.strPassPhraseApplicable = str(settingsList["strPassphrase"])
                self.theSettings.SETT_NotifyAPIDataHasChanged()

            #settingsList["bHasAcceptedConditions"] = self.checkboxAuthorization.isChecked()
            settingsList["strTradingPair"] = self.strTradingPair
            if (self.strTradingPair != self.strApplicableTradingPair):
                print("UIST - New trading pair set: new %s / old %s" % (self.strTradingPair, self.strApplicableTradingPair))
                self.strApplicableTradingPair = self.strTradingPair # The new applicable trading pair becomes this one
                self.theSettings.SETT_NotifyTradingPairHasChanged()
            settingsList["strFiatType"] = self.strFiatType
            settingsList["strCryptoType"] = self.strCryptoType
            settingsList["investPercentage"] = self.investPercentage
            settingsList["platformTakerFee"] = self.platformTakerFee
            settingsList["sellTrigger"] = self.sellTrigger
            settingsList["autoSellThreshold"] = self.autoSellThreshold
            settingsList["simulatedFiatBalance"] = self.txtSimulatedFiatBalance.text().replace(',','.')
            settingsList["simulationSpeed"] = self.simulationSpeed
            settingsList["simulationTimeRange"] = self.simulationTimeRange

            # Save settings
            self.theSettings.SETT_SaveSettings()

            # Close window
            self.HideWindow()


    def EventCancelButtonClick(self):
        print("UIST - Cancel Click")
        self.HideWindow()

    def EventComboTradingPairChanged(self):
        print("UIST - Combo Trading pair set to: %s" % str(self.comboTradingPair.currentIndex()))
        all_data = GDAXCurrencies.get_currencies_list()
        try:
            a_currency = all_data[self.comboTradingPair.currentIndex()]
            self.strTradingPair = a_currency['full']
            self.strFiatType = a_currency['fiat']
            self.strCryptoType = a_currency['coin']
        except IndexError:
            pass

        # Refresh labels that mention the currency
        self.lblSimulatedFiatBalance.setText(self.strFiatType)
        self.lblFiatPercentageToInvest.setText("Percentage of " + self.strFiatType + " account balance to invest in trades:")

    def EventMovedSliderFiatAmountInvest(self):
        #print("Fiat amount percentage to invest : " + str(self.sliderFiatAmount.value()))
        self.lblFiatAmountValue.setText(str(self.sliderFiatAmount.value()) + " %")
        self.investPercentage = self.sliderFiatAmount.value()

    def EventMovedSliderTakerFee(self):
        #print("UIST - Slider Taker Fee value change: " + str(self.sliderTakerFee.value()*theConfig.CONFIG_PLATFORM_TAKER_FEE_QUANTUM))
        self.platformTakerFee = round(float(self.sliderTakerFee.value()*theConfig.CONFIG_PLATFORM_TAKER_FEE_QUANTUM), 2)
        self.lblTakerFeePercent.setText(str(self.platformTakerFee) + " %")

    def EventMovedSliderAutoSell(self):
        #print("UIST - Slider Auto Sell Threshold value change: " + str(self.sliderAutoSellThreshold.value()*theConfig.CONFIG_PLATFORM_AUTO_SELL_THRESHOLD_QUANTUM))
        self.autoSellThreshold = round(float(self.sliderAutoSellThreshold.value()*theConfig.CONFIG_PLATFORM_AUTO_SELL_THRESHOLD_QUANTUM), 2)
        self.lblAutoSellPercent.setText(str(self.autoSellThreshold) + " %")

    def EventMovedSliderSimulationSpeed(self):
        self.simulationSpeed = int(self.sliderSimulationSpeed.value())

    def EventMovedSliderSellTrigger(self):
        self.sellTrigger = round(float(self.sliderSellTrigger.value()*theConfig.CONFIG_SELL_TRIGGER_PERCENTAGE_QUANTUM), 2)
        self.lblSellTriggerPercent.setText(str(self.sellTrigger) + " %")

    def EventComboSimulationTimeRange(self):
        print("UIST - Combo Simulation time range set to: %s" % str(self.comboSimulationTimeRange.currentIndex()))
        if (self.comboSimulationTimeRange.currentIndex() == 0):
            self.simulationTimeRange = 24
        elif (self.comboSimulationTimeRange.currentIndex() == 1):
            self.simulationTimeRange = 48
        elif (self.comboSimulationTimeRange.currentIndex() == 2):
            self.simulationTimeRange = 72
        elif (self.comboSimulationTimeRange.currentIndex() == 3):
            self.simulationTimeRange = 168
        else:
            pass

    def TimerRaisedBlinkStuff(self):
        if (self.blinkCounter < 6):
            self.blinkIsOn = not self.blinkIsOn
            self.UpdateBlinkWidgetsDisplay()
            self.blinkCounter = self.blinkCounter + 1
        else:
            self.blinkIsOn = False
            self.UpdateBlinkWidgetsDisplay()

    def UpdateBlinkWidgetsDisplay(self):
        if (self.blinkIsOn == True):
            self.txtAPIKey.setStyleSheet(self.STR_QTEXTEDIT_BLINK_STYLESHEET)
            self.txtPassPhrase.setStyleSheet(self.STR_QTEXTEDIT_BLINK_STYLESHEET)
            self.txtSecretKey.setStyleSheet(self.STR_QTEXTEDIT_BLINK_STYLESHEET)
        else:
            self.txtAPIKey.setStyleSheet(self.STR_QTEXTEDIT_STYLESHEET)
            self.txtPassPhrase.setStyleSheet(self.STR_QTEXTEDIT_STYLESHEET)
            self.txtSecretKey.setStyleSheet(self.STR_QTEXTEDIT_STYLESHEET)

    def checkParametersValidity(self):
        # Check amount of money to virtually invest in simulation mode
        if (self.txtSimulatedFiatBalance.text() != ""):
            fiatBalance = float(self.txtSimulatedFiatBalance.text().replace(',','.'))
            if ((fiatBalance < theConfig.CONFIG_SIMU_INITIAL_BALANCE_MIN) or (fiatBalance > theConfig.CONFIG_SIMU_INITIAL_BALANCE_MAX)):
                print("UIST - Input range error on Simulated fiat balance to invest")
                self.MessageBoxPopup("Error: Initial simulated fiat balance entry must be between " + str(theConfig.CONFIG_SIMU_INITIAL_BALANCE_MIN) + " to " + str(theConfig.CONFIG_SIMU_INITIAL_BALANCE_MAX), 0)
                return False
        else:
            print("UIST - No entry for initial simulated balance to invest")
            self.MessageBoxPopup("Error: No entry for initial simulated fiat balance (range is " + str(theConfig.CONFIG_SIMU_INITIAL_BALANCE_MIN) + " to " + str(theConfig.CONFIG_SIMU_INITIAL_BALANCE_MAX) + ")", 0)
            return False

        return True


    ##  Styles:
    ##  0 : OK
    ##  1 : OK | Cancel
    ##  2 : Abort | Retry | Ignore
    ##  3 : Yes | No | Cancel
    ##  4 : Yes | No
    ##  5 : Retry | No
    ##  6 : Cancel | Try Again | Continue
    def MessageBoxPopup(self, text, style):
        title = "Astibot Settings"
        return ctypes.windll.user32.MessageBoxW(0, text, title, style)

    def BuildWindowLayout(self):
        self.rootGridLayout = QtGui.QGridLayout()
        self.rootGridLayout.setContentsMargins(0, 0, 0, 0)
        self.mainGridLayout1 = QtGui.QGridLayout()
        self.mainGridLayout1.setContentsMargins(0, 0, 0, 0)
        self.mainGridLayout2 = QtGui.QGridLayout()
        self.mainGridLayout2.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.rootGridLayout)
        self.rootGridLayout.addLayout(self.mainGridLayout1, 1, 1)
        self.rootGridLayout.addLayout(self.mainGridLayout2, 3, 1)
        self.mainGridLayout1.setColumnStretch(0, 2)
        self.mainGridLayout1.setColumnStretch(1, 1)
        self.mainGridLayout2.setColumnStretch(0, 2)
        self.mainGridLayout2.setColumnStretch(1, 1)
        rowNumber = 0

        # Root left and right
        self.rootLeftBlock = QtGui.QWidget()
        self.rootLeftBlock.setStyleSheet(self.STR_BORDER_BLOCK_STYLESHEET)
        self.rootLeftBlock.setFixedWidth(20)
        self.rootRightBlock = QtGui.QWidget()
        self.rootRightBlock.setStyleSheet(self.STR_BORDER_BLOCK_STYLESHEET)
        self.rootRightBlock.setFixedWidth(20)
        self.rootGridLayout.addWidget(self.rootLeftBlock, 0, 0, 5, 1)
        self.rootGridLayout.addWidget(self.rootRightBlock, 0, 3, 5, 1)

        # Root top and bottom
        self.rootTopBlock = QtGui.QWidget()
        self.rootTopBlock.setStyleSheet(self.STR_BORDER_BLOCK_STYLESHEET)
        self.rootTopBlock.setFixedHeight(20)
        self.rootBottomBlock = QtGui.QWidget()
        self.rootBottomBlock.setStyleSheet(self.STR_BORDER_BLOCK_STYLESHEET)
        self.rootBottomBlock.setFixedHeight(60)
        self.rootGridLayout.addWidget(self.rootTopBlock, 0, 0, 1, 4)
        self.rootGridLayout.addWidget(self.rootBottomBlock, 4, 0, 1, 4)

        # Reuse ============================================================================
        self.SeparatorLine = QtGui.QWidget()
        self.SeparatorLine.setStyleSheet(self.STR_BORDER_BLOCK_STYLESHEET)
        self.SeparatorLine.setFixedHeight(15)
        self.SeparatorLine2 = QtGui.QWidget()
        self.SeparatorLine2.setStyleSheet(self.STR_BORDER_BLOCK_STYLESHEET)
        self.SeparatorLine2.setFixedHeight(15)

        # Trading Account layout ===========================================================
        self.lblTitleTradingAccount = QtGui.QLabel("Coinbase Pro Connection parameters")
        self.lblTitleTradingAccount.setStyleSheet(self.STR_QLABEL_TITLE_STYLESHEET);
        self.mainGridLayout1.addWidget(self.lblTitleTradingAccount, rowNumber, 0)
        rowNumber = rowNumber + 1

        # API Key
        self.lblAPIKey = QtGui.QLabel("API Key:")
        self.lblAPIKey.setStyleSheet(self.STR_QLABEL_STYLESHEET);
        self.lblAPIKey.setFixedHeight(30)
        self.lblAPIKey.setContentsMargins(20,0,0,0)
        self.mainGridLayout1.addWidget(self.lblAPIKey, rowNumber, 0)
        self.txtAPIKey = QtGui.QLineEdit()
        self.txtAPIKey.setStyleSheet(self.STR_QTEXTEDIT_STYLESHEET)
        self.mainGridLayout1.addWidget(self.txtAPIKey, rowNumber, 1)
        rowNumber = rowNumber + 1

        # Secret Key
        self.lblSecretKey = QtGui.QLabel("Secret Key:")
        self.lblSecretKey.setStyleSheet(self.STR_QLABEL_STYLESHEET);
        self.lblSecretKey.setFixedHeight(30)
        self.lblSecretKey.setContentsMargins(20,0,0,0)
        self.mainGridLayout1.addWidget(self.lblSecretKey, rowNumber, 0)
        self.txtSecretKey = QtGui.QLineEdit()
        self.txtSecretKey.setStyleSheet(self.STR_QTEXTEDIT_STYLESHEET)
        self.txtSecretKey.setEchoMode(QtGui.QLineEdit.Password)
        self.mainGridLayout1.addWidget(self.txtSecretKey, rowNumber, 1)
        rowNumber = rowNumber + 1

        # Passphrase
        self.lblPassPhrase = QtGui.QLabel("Passphrase:")
        self.lblPassPhrase.setStyleSheet(self.STR_QLABEL_STYLESHEET);
        self.lblPassPhrase.setFixedHeight(30)
        self.lblPassPhrase.setContentsMargins(20,0,0,0)
        self.mainGridLayout1.addWidget(self.lblPassPhrase, rowNumber, 0)
        self.txtPassPhrase = QtGui.QLineEdit()
        self.txtPassPhrase.setStyleSheet(self.STR_QTEXTEDIT_STYLESHEET)
        self.txtPassPhrase.setEchoMode(QtGui.QLineEdit.Password)
        self.mainGridLayout1.addWidget(self.txtPassPhrase, rowNumber, 1)
        rowNumber = rowNumber + 1

        # Authorization checkbox
        self.lblPermissions = QtGui.QLabel("Note: Make sure you enabled the <b>View</b> and <b>Trade</b> permissions when creating your API keys on your Coinbase Pro profile. These permissions are required for Astibot to operate.")
        self.lblPermissions.setWordWrap(True)
        self.lblPermissions.setStyleSheet(self.STR_QLABEL_NOTE_STYLESHEET);
        self.lblAuthorization = QtGui.QLabel(self.STR_CHECKBOX_AUTHORIZATION_TEXT)
        self.lblAuthorization.setStyleSheet(self.STR_QCHECKBOX_LABEL_STYLESHEET)
        self.lblAuthorization.setWordWrap(True)

        self.mainGridLayout1.addWidget(self.lblPermissions, rowNumber, 0, 1, 2)
        rowNumber = rowNumber + 1
        self.mainGridLayout1.addWidget(self.lblAuthorization, rowNumber, 0, 1, 2)
        rowNumber = rowNumber + 1

        # Separator
        self.rootGridLayout.addWidget(self.SeparatorLine, 2, 0, 1, 4)
        rowNumber = 0

        # Trading Parameters layout ========================================================
        self.lblTitleTradingParameters = QtGui.QLabel("Trading parameters")
        self.lblTitleTradingParameters.setStyleSheet(self.STR_QLABEL_TITLE_STYLESHEET);
        self.mainGridLayout2.addWidget(self.lblTitleTradingParameters, rowNumber, 0)
        rowNumber = rowNumber + 1

        # Trading pair
        self.lblTradingPair = QtGui.QLabel("Trading pair:")
        self.lblTradingPair.setStyleSheet(self.STR_QLABEL_STYLESHEET);
        self.lblTradingPair.setFixedHeight(30)
        self.lblTradingPair.setContentsMargins(20,0,0,0)
        self.mainGridLayout2.addWidget(self.lblTradingPair, rowNumber, 0)
        self.comboTradingPair = QtGui.QComboBox()
        self.comboTradingPair.setView(QtGui.QListView())  # Necessary to allow height change
        for currency in GDAXCurrencies.get_all_pairs():
            self.comboTradingPair.addItem(currency)
        self.comboTradingPair.currentIndexChanged.connect(self.EventComboTradingPairChanged)
        self.comboTradingPair.setStyleSheet(self.STR_COMBO_STYLESHEET)
        self.mainGridLayout2.addWidget(self.comboTradingPair, rowNumber, 1)
        rowNumber = rowNumber + 1

        # Fiat amount to invest
        self.lblFiatPercentageToInvest = QtGui.QLabel("Percentage of " + self.theSettings.SETT_GetSettings()["strFiatType"] + " account balance to invest in trades:")
        self.lblFiatPercentageToInvest.setStyleSheet(self.STR_QLABEL_STYLESHEET);
        self.lblFiatPercentageToInvest.setFixedHeight(30)
        self.lblFiatPercentageToInvest.setContentsMargins(20,0,0,0)
        self.mainGridLayout2.addWidget(self.lblFiatPercentageToInvest, rowNumber, 0)
        self.hBoxFiatAmount = QtGui.QHBoxLayout()
        self.sliderFiatAmount = QtGui.QSlider(QtCore.Qt.Horizontal)
        self.sliderFiatAmount.setMinimum(1)
        self.sliderFiatAmount.setMaximum(99)
        self.sliderFiatAmount.setValue(50)
        self.sliderFiatAmount.setStyleSheet(self.STR_QSLIDER_STYLESHEET)
        self.sliderFiatAmount.valueChanged.connect(self.EventMovedSliderFiatAmountInvest)
        self.lblFiatAmountValue = QtGui.QLabel("90 %")
        self.lblFiatAmountValue.setStyleSheet(self.STR_QLABEL_STYLESHEET);
        self.lblFiatAmountValue.setFixedWidth(self.RIGHT_LABELS_WIDTH_IN_PX)
        self.hBoxFiatAmount.addWidget(self.sliderFiatAmount)
        self.hBoxFiatAmount.addWidget(self.lblFiatAmountValue)
        self.mainGridLayout2.addLayout(self.hBoxFiatAmount, rowNumber, 1)
        rowNumber = rowNumber + 1

        # Coinbase Pro Taker fee
        self.lblTakerFee = QtGui.QLabel("Coinbase Pro Taker and Maker order fee:")
        self.lblTakerFee.setStyleSheet(self.STR_QLABEL_STYLESHEET);
        self.lblTakerFee.setFixedHeight(30)
        self.lblTakerFee.setContentsMargins(20,0,0,0)
        self.mainGridLayout2.addWidget(self.lblTakerFee, rowNumber, 0)
        self.sliderTakerFee = QtGui.QSlider(QtCore.Qt.Horizontal)
        self.sliderTakerFee.setMinimum(theConfig.CONFIG_PLATFORM_TAKER_FEE_MIN_ON_SLIDER)
        self.sliderTakerFee.setMaximum(theConfig.CONFIG_PLATFORM_TAKER_FEE_MAX_ON_SLIDER)
        self.sliderTakerFee.setSingleStep(1)
        self.sliderTakerFee.setValue(theConfig.CONFIG_PLATFORM_TAKER_FEE_DEFAULT_VALUE)
        self.sliderTakerFee.setStyleSheet(self.STR_QSLIDER_STYLESHEET)
        self.sliderTakerFee.valueChanged.connect(self.EventMovedSliderTakerFee)
        self.lblTakerFeePercent = QtGui.QLabel("%")
        self.lblTakerFeePercent.setStyleSheet(self.STR_QLABEL_STYLESHEET);
        self.lblTakerFeePercent.setFixedWidth(self.RIGHT_LABELS_WIDTH_IN_PX)
        self.hBoxTakerFee = QtGui.QHBoxLayout()
        self.hBoxTakerFee.addWidget(self.sliderTakerFee)
        self.hBoxTakerFee.addWidget(self.lblTakerFeePercent)
        self.mainGridLayout2.addLayout(self.hBoxTakerFee, rowNumber, 1)
        rowNumber = rowNumber + 1

        # Sell trigger
        self.lblSellTrigger = QtGui.QLabel("Auto-Sell trigger (% above buy price, set 0 to disable):")
        self.lblSellTrigger.setStyleSheet(self.STR_QLABEL_STYLESHEET);
        self.lblSellTrigger.setFixedHeight(30)
        self.lblSellTrigger.setContentsMargins(20,0,0,0)
        self.mainGridLayout2.addWidget(self.lblSellTrigger, rowNumber, 0)
        self.sliderSellTrigger = QtGui.QSlider(QtCore.Qt.Horizontal)
        self.sliderSellTrigger.setMinimum(theConfig.CONFIG_SELL_TRIGGER_PERCENTAGE_MIN_ON_SLIDER)
        self.sliderSellTrigger.setMaximum(theConfig.CONFIG_SELL_TRIGGER_PERCENTAGE_MAX_ON_SLIDER)
        self.sliderSellTrigger.setSingleStep(1)
        self.sliderSellTrigger.setValue(theConfig.CONFIG_SELL_TRIGGER_PERCENTAGE_DEFAULT_VALUE)
        self.sliderSellTrigger.setStyleSheet(self.STR_QSLIDER_STYLESHEET)
        self.sliderSellTrigger.valueChanged.connect(self.EventMovedSliderSellTrigger)
        self.lblSellTriggerPercent = QtGui.QLabel("%")
        self.lblSellTriggerPercent.setStyleSheet(self.STR_QLABEL_STYLESHEET);
        self.lblSellTriggerPercent.setFixedWidth(self.RIGHT_LABELS_WIDTH_IN_PX)
        self.hBoxSellTrigger = QtGui.QHBoxLayout()
        self.hBoxSellTrigger.addWidget(self.sliderSellTrigger)
        self.hBoxSellTrigger.addWidget(self.lblSellTriggerPercent)
        self.mainGridLayout2.addLayout(self.hBoxSellTrigger, rowNumber, 1)
        rowNumber = rowNumber + 1

        # Auto-sell by percentage threshold
        self.lblAutoSellThreshold = QtGui.QLabel("Stop-loss trigger (% below buy price, set 0 to disable):")
        self.lblAutoSellThreshold.setStyleSheet(self.STR_QLABEL_STYLESHEET);
        self.lblAutoSellThreshold.setFixedHeight(30)
        self.lblAutoSellThreshold.setContentsMargins(20,0,0,0)
        self.mainGridLayout2.addWidget(self.lblAutoSellThreshold, rowNumber, 0)
        self.sliderAutoSellThreshold = QtGui.QSlider(QtCore.Qt.Horizontal)
        self.sliderAutoSellThreshold.setMinimum(theConfig.CONFIG_PLATFORM_AUTO_SELL_THRESHOLD_MIN_ON_SLIDER)
        self.sliderAutoSellThreshold.setMaximum(theConfig.CONFIG_PLATFORM_AUTO_SELL_THRESHOLD_MAX_ON_SLIDER)
        self.sliderAutoSellThreshold.setSingleStep(1)
        self.sliderAutoSellThreshold.setValue(theConfig.CONFIG_PLATFORM_AUTO_SELL_THRESHOLD_DEFAULT_VALUE)
        self.sliderAutoSellThreshold.setStyleSheet(self.STR_QSLIDER_STYLESHEET)
        self.sliderAutoSellThreshold.valueChanged.connect(self.EventMovedSliderAutoSell)
        self.lblAutoSellPercent = QtGui.QLabel("%")
        self.lblAutoSellPercent.setStyleSheet(self.STR_QLABEL_STYLESHEET);
        self.lblAutoSellPercent.setFixedWidth(self.RIGHT_LABELS_WIDTH_IN_PX)
        self.hBoxAutoSell = QtGui.QHBoxLayout()
        self.hBoxAutoSell.addWidget(self.sliderAutoSellThreshold)
        self.hBoxAutoSell.addWidget(self.lblAutoSellPercent)
        self.mainGridLayout2.addLayout(self.hBoxAutoSell, rowNumber, 1)
        rowNumber = rowNumber + 1

        # Simulated fiat account balance
        self.lblSimulatedFiatBalance = QtGui.QLabel("Simulated fiat account balance (simulation mode only):")
        self.lblSimulatedFiatBalance.setStyleSheet(self.STR_QLABEL_STYLESHEET);
        self.lblSimulatedFiatBalance.setFixedHeight(30)
        self.lblSimulatedFiatBalance.setContentsMargins(20,0,0,0)
        self.mainGridLayout2.addWidget(self.lblSimulatedFiatBalance, rowNumber, 0)
        self.txtSimulatedFiatBalance = QtGui.QLineEdit()
        self.txtSimulatedFiatBalance.setStyleSheet(self.STR_QTEXTEDIT_STYLESHEET)
        self.txtSimulatedFiatBalance.setFixedWidth(80)
        self.txtSimulatedFiatBalance.setValidator(QDoubleValidator())
        self.lblSimulatedFiatBalance = QtGui.QLabel(self.theSettings.SETT_GetSettings()["strFiatType"])
        self.lblSimulatedFiatBalance.setStyleSheet(self.STR_QLABEL_STYLESHEET);
        self.lblSimulatedFiatBalance.setFixedWidth(self.RIGHT_LABELS_WIDTH_IN_PX)
        self.hBoxSimulatedFiatBalance = QtGui.QHBoxLayout()
        self.hBoxSimulatedFiatBalance.addWidget(self.txtSimulatedFiatBalance, QtCore.Qt.AlignLeft)
        self.hBoxSimulatedFiatBalance.addWidget(self.lblSimulatedFiatBalance, QtCore.Qt.AlignLeft)
        self.mainGridLayout2.addLayout(self.hBoxSimulatedFiatBalance, rowNumber, 1, QtCore.Qt.AlignLeft)
        rowNumber = rowNumber + 1

        # Simulation speed
        self.lblSimulationSpeed = QtGui.QLabel("Simulation speed (simulation mode only):")
        self.lblSimulationSpeed.setStyleSheet(self.STR_QLABEL_STYLESHEET);
        self.lblSimulationSpeed.setFixedHeight(30)
        self.lblSimulationSpeed.setContentsMargins(20,0,0,0)
        self.mainGridLayout2.addWidget(self.lblSimulationSpeed, rowNumber, 0)
        self.sliderSimulationSpeed = QtGui.QSlider(QtCore.Qt.Horizontal)
        self.sliderSimulationSpeed.setMinimum(0)
        self.sliderSimulationSpeed.setMaximum(100)
        self.sliderSimulationSpeed.setValue(50)
        self.sliderSimulationSpeed.setStyleSheet(self.STR_QSLIDER_STYLESHEET)
        self.sliderSimulationSpeed.valueChanged.connect(self.EventMovedSliderSimulationSpeed)
        self.lblSlow = QtGui.QLabel("Slow")
        self.lblSlow.setStyleSheet(self.STR_QLABEL_STYLESHEET);
        self.lblFast = QtGui.QLabel("Fast")
        self.lblFast.setStyleSheet(self.STR_QLABEL_STYLESHEET);
        self.lblFast.setFixedWidth(self.RIGHT_LABELS_WIDTH_IN_PX)
        self.hBoxSimulationSpeed = QtGui.QHBoxLayout()
        self.hBoxSimulationSpeed.addWidget(self.lblSlow)
        self.hBoxSimulationSpeed.addWidget(self.sliderSimulationSpeed)
        self.hBoxSimulationSpeed.addWidget(self.lblFast, QtCore.Qt.AlignLeft)
        self.mainGridLayout2.addLayout(self.hBoxSimulationSpeed, rowNumber, 1)
        rowNumber = rowNumber + 1

        # Simulation time range
        self.lblSimulationTimeRange = QtGui.QLabel("Simulation time range (simulation mode only):")
        self.lblSimulationTimeRange.setFixedHeight(30)
        self.lblSimulationTimeRange.setStyleSheet(self.STR_QLABEL_STYLESHEET);
        self.lblSimulationTimeRange.setContentsMargins(20,0,0,0)
        self.mainGridLayout2.addWidget(self.lblSimulationTimeRange, rowNumber, 0)
        self.comboSimulationTimeRange = QtGui.QComboBox()
        self.comboSimulationTimeRange.setView(QtGui.QListView()); # Necessary to allow height change
        self.comboSimulationTimeRange.addItem("Last 24h")
        self.comboSimulationTimeRange.addItem("Last 48h")
        self.comboSimulationTimeRange.addItem("Last 72h")
        self.comboSimulationTimeRange.addItem("Last Week")
        self.comboSimulationTimeRange.setStyleSheet(self.STR_COMBO_STYLESHEET)
        self.comboSimulationTimeRange.currentIndexChanged.connect(self.EventComboSimulationTimeRange)
        self.mainGridLayout2.addWidget(self.comboSimulationTimeRange, rowNumber, 1)
        rowNumber = rowNumber + 1

        # Bottom buttons
        self.btnCancel = QtGui.QPushButton("Cancel")
        self.btnCancel.setStyleSheet(self.STR_QBUTTON_CANCEL_STYLESHEET)
        self.btnCancel.setFixedWidth(120)
        self.btnCancel.setFixedHeight(38)
        self.btnCancel.clicked.connect(self.EventCancelButtonClick)
        self.btnCancel.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.btnApply = QtGui.QPushButton("Apply and Close")
        self.btnApply.setStyleSheet(self.STR_QBUTTON_APPLY_STYLESHEET)
        self.btnApply.setFixedWidth(140)
        self.btnApply.setFixedHeight(38)
        self.btnApply.clicked.connect(self.EventApplylButtonClick)
        self.btnApply.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.hBoxBottomButtons = QtGui.QHBoxLayout()
        self.hBoxBottomButtons.addWidget(self.btnCancel, QtCore.Qt.AlignRight)
        self.hBoxBottomButtons.addWidget(self.btnApply, QtCore.Qt.AlignRight)
        self.rootBottomBlock.setLayout(self.hBoxBottomButtons)
        rowNumber = rowNumber + 1


    def UIST_ShowWindow(self):
        print("UIST - Show")

        # Apply saved settings
        self.ApplySettings()

        # Start blink timer if relevant
        if ((self.txtAPIKey.text() == "") or (self.txtSecretKey.text() == "") or (self.txtPassPhrase.text() == "")):
            self.timerBlinkStuffs.start(500)
            self.blinkCounter = 0

        self.show()

        # Sometimes the window is not correctly displayed (blank zone in the bottom) until for example a manual window resize. So force a refresh.
        QtGui.QApplication.processEvents()

    def HideWindow(self):
        self.timerBlinkStuffs.stop()
        self.blinkIsOn = False
        self.UpdateBlinkWidgetsDisplay()
        self.hide()
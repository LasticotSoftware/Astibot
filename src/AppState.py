from MarketData import MarketData
from GDAXControler import GDAXControler
from TransactionManager import TransactionManager
from Trader import Trader
from UIGraph import UIGraph
import TradingBotConfig as theConfig


class AppState(object):

    currentAppState = "STATE_INITIALIZATION"
    nextAppState = "STATE_INITIALIZATION"
    
    def __init__(self, UIGraph, Trader, GDAXControler, InputDataHandler, MarketData, Settings):
        self.theUIGraph = UIGraph
        self.theTrader = Trader
        self.theGDAXControler = GDAXControler
        self.theInputDataHandler = InputDataHandler
        self.theMarketData = MarketData
        # Application settings data instance
        self.theSettings = Settings
        
        self.previousModeWasRealMarket = theConfig.CONFIG_INPUT_MODE_IS_REAL_MARKET
        
        # Entry actions for Initialization state
        self.PerformInitializationStateEntryActions()
        
        self.generalPurposeDecreasingCounter = 0
        
    def APP_Execute(self):
        self.nextAppState = self.currentAppState
        #print(self.currentAppState)
        
        if (self.currentAppState == 'STATE_INITIALIZATION'):
            self.ManageInitializationState()
        elif (self.currentAppState == 'STATE_IDLE'):
            self.ManageIdleState()
        elif (self.currentAppState == 'STATE_SIMULATION_LOADING'):
            self.ManageSimulationLoadingState()  
        elif (self.currentAppState == 'STATE_SIMULATION'):
            self.ManageSimulationState()
        elif (self.currentAppState == 'STATE_SIMULATION_STOPPING'):
            self.ManageSimulationStoppingState()
        elif (self.currentAppState == 'STATE_TRADING_LOADING'):
            self.ManageTradingLoadingState()                
        elif (self.currentAppState == 'STATE_TRADING'):
            self.ManageTradingState()                     
        elif (self.currentAppState == 'STATE_FAILURE'):
            self.ManageFailureState()          
        else:
            self.ManageIdleState() # Error case
    
        # If transition requested
        if (self.nextAppState != self.currentAppState):
            self.currentAppState = self.nextAppState
            self.theUIGraph.UIGR_SetCurrentAppState(self.currentAppState)
            
        if (self.generalPurposeDecreasingCounter > 0):
            self.generalPurposeDecreasingCounter = self.generalPurposeDecreasingCounter - 1
            #print(self.generalPurposeDecreasingCounter)
    
    def PerformInitializationStateEntryActions(self):
        self.nextAppState = "STATE_INITIALIZATION"        
        self.theUIGraph.UIGR_updateCurrentState("Initializing...", False, True)
        
        # Init HMI functional features
        self.theUIGraph.UIGR_SetStartButtonEnabled(False)
        self.theUIGraph.UIGR_SetStartButtonAspect("START_DISABLED")
        self.theUIGraph.UIGR_SetPauseButtonEnabled(False)
        self.theUIGraph.UIGR_SetPauseButtonAspect("PAUSE_DISABLED")
        self.theUIGraph.UIGR_SetSettingsButtonsEnabled(False)
        self.theUIGraph.UIGR_SetDonationButtonsEnabled(False)
        
        self.theGDAXControler.GDAX_InitializeGDAXConnexion()
        self.theUIGraph.UIGR_SetDonationButtonsEnabled(False)
        self.theInputDataHandler.INDH_PrepareHistoricDataSinceGivenHours(True, theConfig.NB_HISTORIC_DATA_HOURS_TO_PRELOAD_FOR_TRADING)
        
        
    def ManageInitializationState(self):
        self.theUIGraph.UIGR_updateCurrentState("Initializing...", False, True)
        
        if (self.theGDAXControler.GDAX_IsConnectedAndOperational() == "True"):
            if (self.theInputDataHandler.INDH_GetPreloadHistoricDataStatus() == "Ended"):
                # Initialization to Idle state transition actions
                self.nextAppState = 'STATE_IDLE'
                self.theUIGraph.UIGR_SetStartButtonEnabled(True)
                self.theUIGraph.UIGR_SetStartButtonAspect("START")
                self.theUIGraph.UIGR_SetSettingsButtonsEnabled(True)
                self.theTrader.TRAD_InitiateNewTradingSession(False) # Force accounts balances display refresh
                self.theUIGraph.UIGR_SetDonationButtonsEnabled(True)
                print("APPL - Init: go to idle")
        elif (self.theGDAXControler.GDAX_IsConnectedAndOperational() == "False"):
            self.nextAppState = 'STATE_FAILURE'
            self.theUIGraph.UIGR_SetStartButtonEnabled(False)
            self.theUIGraph.UIGR_SetStartButtonAspect("START_DISABLED")
            self.theUIGraph.UIGR_SetSettingsButtonsEnabled(True)
            print("APPL: Init: go to failure")
        else:
            # Ongoing
            print("APPL - Initialization State - Ongoing init")
            pass
        
    def ManageIdleState(self):
        self.theUIGraph.UIGR_updateCurrentState("Idle", False, False)
        
        self.CheckImpactingSettingsChanges()
        
        # User actions analysis ===================================================================
        # If user clicks on "Start"
        if (self.theUIGraph.UIGR_IsStartButtonClicked() == True):
            if (self.theUIGraph.UIGR_GetSelectedRadioMode() == "Simulation"):
                print("APPL - ManageIdleState - StartButtonClicked, going to Simulaltion")
                # Transition to STATE_SIMULATION_LOADING
                self.theInputDataHandler.INDH_PrepareHistoricDataSinceGivenHours(False, float(self.theSettings.SETT_GetSettings()["simulationTimeRange"]) + 3.0)
                self.theUIGraph.UIGR_SetStartButtonEnabled(False)
                self.theUIGraph.UIGR_SetStartButtonAspect("LOADING")
                self.theUIGraph.UIGR_SetRadioButtonsEnabled(False)
                self.theUIGraph.UIGR_SetSettingsButtonsEnabled(False)
                self.theUIGraph.UIGR_SetDonationButtonsEnabled(False)
                self.nextAppState = 'STATE_SIMULATION_LOADING'
            else:
                # If Fiat balance is OK
                if (self.theGDAXControler.GDAX_GetFiatAccountBalance() > theConfig.CONFIG_MIN_INITIAL_FIAT_BALANCE_TO_TRADE):
                    print("APPL - ManageIdleState - StartButtonClicked, fiat balance OK, going to Trading")
                    # Transition to STATE_TRADING_LOADING
                    self.theInputDataHandler.INDH_PrepareHistoricDataSinceGivenHours(True, theConfig.NB_HISTORIC_DATA_HOURS_TO_PRELOAD_FOR_TRADING)
                    self.theUIGraph.UIGR_SetStartButtonEnabled(False)
                    self.theUIGraph.UIGR_SetStartButtonAspect("LOADING")
                    self.theUIGraph.UIGR_SetRadioButtonsEnabled(False)
                    self.theUIGraph.UIGR_SetSettingsButtonsEnabled(False)
                    self.theUIGraph.UIGR_SetDonationButtonsEnabled(False)
                    self.nextAppState = 'STATE_TRADING_LOADING'
                else:
                    # Fiat balance too small, stay in Idle
                    self.theUIGraph.UIGR_updateInfoText("Your balance is too low to start Trading. A minimum of %s %s is required to ensure trades comply with Coinbase Pro minimum orders sizes." % (theConfig.CONFIG_MIN_INITIAL_FIAT_BALANCE_TO_TRADE, self.theSettings.SETT_GetSettings()["strFiatType"]), True)
                
    def ManageSimulationLoadingState(self):
        self.theUIGraph.UIGR_updateCurrentState("Downloading and analyzing historic data...", False, True)
        
        if (self.theInputDataHandler.INDH_GetPreloadHistoricDataStatus() == "Ended"):
            # Transition to STATE_SIMULATION            
            self.theUIGraph.UIGR_SetStartButtonEnabled(True)
            self.theUIGraph.UIGR_SetStartButtonAspect("STOP")
            # 5 additional hours are needed aproximately to let indicators to settle
            if (self.theInputDataHandler.INDH_PerformSimulation(float(self.theSettings.SETT_GetSettings()["simulationTimeRange"]) + 5) == "Ongoing"):
                self.nextAppState = 'STATE_SIMULATION'
                # Set new state in anticipation to UIGR so that it will prepare the right captions
                self.theUIGraph.UIGR_SetCurrentAppState(self.nextAppState)
                self.theTrader.TRAD_InitiateNewTradingSession(True)                
                self.theUIGraph.UIGR_SetPauseButtonEnabled(True)
                self.theUIGraph.UIGR_SetPauseButtonAspect("PAUSE")
            else:
                # Error
                print("APPL - Simulation loading state > error launching simulation, going to Idle state")
                self.nextAppState = 'STATE_IDLE'
                self.theUIGraph.UIGR_SetRadioButtonsEnabled(True)
                self.theUIGraph.UIGR_SetStartButtonAspect("START")
        else:
            # Wait
            pass
        
    def ManageSimulationState(self):
        self.theUIGraph.UIGR_updateCurrentState("Ongoing simulation", False, False)
        
        # If user clicked on PAUSE button
        if (self.theUIGraph.UIGR_IsPauseButtonClicked() == True):
            self.theInputDataHandler.INDH_PauseResumeSimulation()
            
        # If user clicked on STOP button
        if (self.theUIGraph.UIGR_IsStartButtonClicked() == True):
            print("APPL - Simulation state > go to Simulation Stopping because of StartButton clicked")
            self.theInputDataHandler.INDH_StopSimulation()
            # Request graph refresh timer stop from same thread as it was launched (Main / UI Thread)
            self.theUIGraph.UIGR_StopContinuousGraphRefresh()
            # Short pass in Simulation stopping state is necessary in order to let simulation thread to end by itself
            # so that if user clicks quickly on Start, it will be ready to be started again
            self.nextAppState = 'STATE_SIMULATION_STOPPING'
            self.generalPurposeDecreasingCounter = 3
            self.theUIGraph.UIGR_SetStartButtonEnabled(False)
            self.theUIGraph.UIGR_SetStartButtonAspect("START_DISABLED")
            self.theUIGraph.UIGR_SetPauseButtonEnabled(False)
            self.theUIGraph.UIGR_SetPauseButtonAspect("PAUSE_DISABLED")
            
        # If simulation is ended by itself (end of data buffer)
        if (self.theInputDataHandler.INDH_GetOperationalStatus() == "Ended"):
            print("APPL - Simulation state > go to Idle because of buffer ended")
            # Request graph refresh timer stop from same thread as it was launched (Main / UI Thread)
            self.theUIGraph.UIGR_StopContinuousGraphRefresh()
            self.nextAppState = 'STATE_IDLE'
            self.theUIGraph.UIGR_SetStartButtonEnabled(True)
            self.theUIGraph.UIGR_SetStartButtonAspect("START")
            self.theUIGraph.UIGR_SetPauseButtonEnabled(False)
            self.theUIGraph.UIGR_SetPauseButtonAspect("PAUSE_DISABLED")
            self.theUIGraph.UIGR_SetRadioButtonsEnabled(True)
            self.theUIGraph.UIGR_SetSettingsButtonsEnabled(True)
            self.theUIGraph.UIGR_SetDonationButtonsEnabled(True)
            # Set new state in anticipation to UIGR so that it will prepare the right captions
            self.theUIGraph.UIGR_SetCurrentAppState(self.nextAppState)
            self.theTrader.TRAD_TerminateTradingSession()
    
    def ManageSimulationStoppingState(self):
        print("APPL - Simulation Stopping state")
        if (self.generalPurposeDecreasingCounter == 0):
            self.nextAppState = 'STATE_IDLE'
            self.theUIGraph.UIGR_SetStartButtonEnabled(True)
            self.theUIGraph.UIGR_SetStartButtonAspect("START")
            self.theUIGraph.UIGR_SetPauseButtonEnabled(False)
            self.theUIGraph.UIGR_SetPauseButtonAspect("PAUSE_DISABLED")
            self.theUIGraph.UIGR_SetRadioButtonsEnabled(True)
            self.theUIGraph.UIGR_SetSettingsButtonsEnabled(True)
            self.theUIGraph.UIGR_SetDonationButtonsEnabled(True)
            # Set new state in anticipation to UIGR so that it will prepare the right captions
            self.theUIGraph.UIGR_SetCurrentAppState(self.nextAppState)
            self.theTrader.TRAD_TerminateTradingSession()
        
        
    def ManageTradingLoadingState(self):
        self.theUIGraph.UIGR_updateCurrentState("Downloading and analyzing historic data to prepare trading indicators...", False, True)
        
        if (self.theInputDataHandler.INDH_GetPreloadHistoricDataStatus() == "Ended"):
            print("APPL - ManageTradingLoadingState - PreloadHistoricDataStatus is ended - Going to Trading state")
            # Transition to STATE_TRADING
            self.theUIGraph.UIGR_SetStartButtonEnabled(True)
            self.theUIGraph.UIGR_SetStartButtonAspect("STOP")
            if (self.theInputDataHandler.INDH_PerformLiveTradingOperation(theConfig.NB_HISTORIC_DATA_HOURS_TO_PRELOAD_FOR_TRADING) == "Ongoing"):
                self.nextAppState = 'STATE_TRADING'
                # Set new state in anticipation to UIGR so that it will prepare the right captions
                self.theUIGraph.UIGR_SetCurrentAppState(self.nextAppState)
                self.theTrader.TRAD_InitiateNewTradingSession(True)   
                # DEBUG
                #♠self.generalPurposeDecreasingCounter = 600             
            else:
                # Error
                print("APPL - Trading loading state > error launching trading, going to Idle state")
                self.nextAppState = 'STATE_IDLE'
                self.theUIGraph.UIGR_SetRadioButtonsEnabled(True)
                self.theUIGraph.UIGR_SetStartButtonAspect("START")
                self.theUIGraph.UIGR_SetSettingsButtonsEnabled(True)
                self.theUIGraph.UIGR_SetDonationButtonsEnabled(True)
        else:
            # Wait
            print("APPL - ManageTradingLoadingState - Loading ongoing")
            pass
        
    def ManageTradingState(self):
        self.theUIGraph.UIGR_updateCurrentState("Live trading", True, True)
                        
        # If user clicked on STOP button
        if (self.theUIGraph.UIGR_IsStartButtonClicked() == True):
            print("APPL - Trading state > go to Idle because of StartButton clicked")
            self.theInputDataHandler.INDH_StopLiveTrading()
            # Request graph refresh timer stop from same thread as it was launched (Main / UI Thread)
            self.theUIGraph.UIGR_StopContinuousGraphRefresh()
            self.nextAppState = 'STATE_IDLE'
            self.theUIGraph.UIGR_SetStartButtonEnabled(True)
            self.theUIGraph.UIGR_SetStartButtonAspect("START")
            self.theUIGraph.UIGR_SetPauseButtonEnabled(False)
            self.theUIGraph.UIGR_SetRadioButtonsEnabled(True)
            self.theUIGraph.UIGR_SetSettingsButtonsEnabled(True)
            self.theUIGraph.UIGR_SetDonationButtonsEnabled(True)
            # Set new state in anticipation to UIGR so that it will prepare the right captions
            self.theUIGraph.UIGR_SetCurrentAppState(self.nextAppState)
            self.theTrader.TRAD_TerminateTradingSession()
    
    def ManageFailureState(self):
        self.theUIGraph.UIGR_updateCurrentState("", False, False) # Don't display error to the user
        
        self.CheckImpactingSettingsChanges()
        
    def isFailureStateRequired(self):
        return False
        
    def CheckImpactingSettingsChanges(self):
        # Settings change analysis ===================================================================
        bTradingPairHasChanged = False
        bAPIDataHasChanged = False
        
        # If trading pair or API IDs have changed, Notify stakeholders and perform Initialization state entry actions
        # Heavy code because SETT_hasXXXChanged APIs are "read-once"
        if (self.theSettings.SETT_hasTradingPairChanged() == True):
            bTradingPairHasChanged = True
            
        if (self.theSettings.SETT_hasAPIDataChanged() == True):
            bAPIDataHasChanged = True   
            
        if ((bTradingPairHasChanged == True) or (bAPIDataHasChanged == True)):
            if (bTradingPairHasChanged == True):
                print("APPL - Trading pair has changed")
                self.theUIGraph.UIGR_NotifyThatTradingPairHasChanged()
                self.theGDAXControler.GDAX_NotifyThatTradingPairHasChanged()
            
            if (bAPIDataHasChanged == True):
                print("APPL - API data has changed")
                pass # Nothing specific to do as GDAX will be asked to perform a new connexion
                             
            # Entry actions for Initialization state
            self.PerformInitializationStateEntryActions()
            
            
        # Mode change analysis (Live trading or simulation)
        if (theConfig.CONFIG_INPUT_MODE_IS_REAL_MARKET != self.previousModeWasRealMarket):
            self.previousModeWasRealMarket = theConfig.CONFIG_INPUT_MODE_IS_REAL_MARKET            
            # Accounts balances display differs depending on the mode (simulation or trading), we need to refresh it
            self.theTrader.TRAD_InitiateNewTradingSession(False)
            
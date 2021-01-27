import TradingBotConfig as theConfig
import Notifier as theNotifier
import time

class Trader(object):

    def __init__(self, transactionManager, marketData, UIGraph, Settings):
        self.theTransactionManager = transactionManager
        self.theMarketData = marketData
        self.theUIGraph = UIGraph
        # Application settings data instance
        self.theSettings = Settings

        self.TRAD_ResetTradingParameters()

    def TRAD_ResetTradingParameters(self):
        self.currentState = 'IDLE'
        self.nextState = 'IDLE'

        self.currentPriceValue = 0
        self.previousMACDValue = 0
        self.currentMACDValue = 0
        self.currentBuyPriceInFiat = 0
        #self.MACDConfirmationCounter = 0
        #self.MACDStrength = 0
        self.bought = False
        self.autoSellSamplesCounter = 0
        self.sellTriggerInPercent = self.theSettings.SETT_GetSettings()["sellTrigger"]
        self.ongoingBuyOrderWasFree = False

    def TRAD_InitiateNewTradingSession(self, startSession):
        self.TRAD_ResetTradingParameters()
        self.theTransactionManager.TRNM_InitiateNewTradingSession(startSession)
        if (startSession == True):
            theNotifier.SendWhatsappMessage("*Astibot: New trading session* started on the %s trading pair!" % self.theSettings.SETT_GetSettings()["strTradingPair"])

    def TRAD_TerminateTradingSession(self):
        self.theTransactionManager.TRNM_TerminateCurrentTradingSession()

    def TRAD_ProcessDecision(self):

        #print("TRAD - Process decision")
        
        self.nextState = self.currentState
        self.updateIndicatorsTransitions()

        if (self.currentState == 'IDLE'):
            self.ManageIdleState()
        elif (self.currentState == 'WAITING_TO_BUY'):
            self.ManageWaitingToBuyState()
        elif (self.currentState == 'BUYING'):
            self.ManageBuyingState()
        elif (self.currentState == 'WAITING_TO_SELL'):
            self.ManageWaitingToSellState()
        elif (self.currentState == 'SELLING'):
            self.ManageSellingState()
        else:
            self.ManageIdleState() # Error case

        if (self.nextState != self.currentState):
            self.currentState = self.nextState

    def TRAD_DEBUG_ForceSell(self): 
        print("Auto DEBUG SELL >>>>>>>>>>>>>>>>>>>")
        #self.theTransactionManager.TRNM_BuyNow()
        self.theTransactionManager.TRNM_SellNow(False)

    def TRAD_DEBUG_ForceBuy(self):
        print("Auto DEBUG BUY >>>>>>>>>>>>>>>>>>>")
        self.theTransactionManager.TRNM_BuyNow()
        #self.theTransactionManager.TRNM_SellNow(False)

    def ManageIdleState(self):
        # Check transition to WAITING_TO_BUY or WAITING_TO_SELL state
        if (self.theMarketData.MRKT_AreIndicatorsEstablished() == True):
            # By default, go to WAITING_TO_BUY state
            self.nextState = 'WAITING_TO_BUY'

    def updateIndicatorsTransitions(self):
        self.currentPriceValue = self.theMarketData.MRKT_GetLastRefPrice()
        self.previousMACDValue = self.currentMACDValue
        self.currentMACDValue = self.theMarketData.MRKT_GetLastMACDValue()


    # When MACD indicator is < BUY1 THRESHOLD : No buy signal, do nothing
    # When MACD indicator is > BUY1 THRESHOLD and < BUY1 THRESHOLD : Try to place a buy limit order on top of the order book
    # When MACD indicator is > BUY2 THRESHOLD : Do a market buy order
    # => The limit order mode (betwen B1 and B2 threshold) has not been fully tested. So I recommend to only use market orders.
    # For that, set BUY1 THRESHOLD to a value greater than BUY2 THRESHOLD in Config file so that only MACD > B2 THRESHOLD will occur.
    def ManageWaitingToBuyState(self):
        
        #print("ManageWaitingToBuyState")
        
        isBUY1ThresholdReached = (self.previousMACDValue < theConfig.CONFIG_MACD_BUY_1_THRESHOLD) and (self.currentMACDValue >= theConfig.CONFIG_MACD_BUY_1_THRESHOLD)
        isB2ThresholdReached = (self.previousMACDValue < theConfig.CONFIG_MACD_BUY_2_THRESHOLD) and (self.currentMACDValue >= theConfig.CONFIG_MACD_BUY_2_THRESHOLD)

        # Check MACD buy signal
        if (isBUY1ThresholdReached):
            # Check current price towards risk line
            riskLineThresholdInFiat = self.theMarketData.MRKT_GetLastRiskLineValue() * theConfig.CONFIG_RiskLinePercentsAboveThresholdToBuy
            if (self.currentPriceValue < riskLineThresholdInFiat):
                # Check current price toward maximum allowed buy price
                if (self.currentPriceValue < theConfig.CONFIG_MAX_BUY_PRICE):                    
                    print("TRAD - ManageWaitingToBuyState: B1 reached, limit buy ordered and successful: Going to Buying state ============================================")
                    self.theTransactionManager.TRNM_StartBuyOrSellAttempt("BUY", riskLineThresholdInFiat)
                    self.nextState = 'BUYING'
                else:
                    print("TRAD - ManageWaitingToBuyState: Buy not performed : Price is above max allowed limit - price: " + str(self.currentPriceValue))
            else:
                print("TRAD - ManageWaitingToBuyState: Buy not performed : Price is above the risk line")
        elif (isB2ThresholdReached):
            self.ManageBuyingState()

                
    def ManageBuyingState(self):
        
        #print("ManageBuyingState")
        
        isB2ThresholdReached = (self.previousMACDValue < theConfig.CONFIG_MACD_BUY_2_THRESHOLD) and (self.currentMACDValue >= theConfig.CONFIG_MACD_BUY_2_THRESHOLD)
        
        # Is ongoing limit order filled?
        currentBuyOrderState = self.theTransactionManager.TRNM_GetOngoingLimitOrderState()
        
        #print(currentBuyOrderState)
        
#        if (currentBuyOrderState == "NONE"):
#            print("TRAD - Buy limit order canceled: go back to WAITING TO BUY state ============================================")
#            self.nextState = 'WAITING_TO_BUY'
#            self.theUIGraph.UIGR_updateInfoText("Buy order canceled. Waiting for next buy opportunity", False)
#        elif (currentBuyOrderState == "FILLED"):
        if (currentBuyOrderState == "FILLED"):
            self.ongoingBuyOrderWasFree = True
            self.currentBuyPriceInFiat = self.theTransactionManager.TRNM_GetCurrentBuyInitialPrice()  
            if (self.sellTriggerInPercent > 0.0):
                print("TRAD - ManageBuyingState: Buy Order filled and sellTrigger is set, place sell order and go to SELLING ============================================")
                
                # In real market conditions, wait for GDAX accounts to be refreshed
                if (theConfig.CONFIG_INPUT_MODE_IS_REAL_MARKET == True):
                    time.sleep(10)
                
                self.theTransactionManager.TRNM_StartBuyOrSellAttempt("SELL", self.currentBuyPriceInFiat * (1 + (self.sellTriggerInPercent / 100)))                  
                self.nextState = 'SELLING'                             
            else: 
                print("TRAD - ManageBuyingState: Buy Order filled and sellTrigger is not set, go to WAITING TO SELL")
                self.nextState = 'WAITING_TO_SELL'
        elif (isB2ThresholdReached):
            # MACD crossed the B2 threshold
            if (currentBuyOrderState == "MATCHED"):
                print("TRAD - ManageBuyingState: B2 reached, canceling ongoing buy order to go to Selling / Waiting to sell state")
                # Cancel ongoing order: too risky to maintain it
                self.theTransactionManager.TRNM_CancelOngoingOrder()
                self.currentBuyPriceInFiat = self.theTransactionManager.TRNM_GetCurrentBuyInitialPrice()
                self.ongoingBuyOrderWasFree = True
                if (self.sellTriggerInPercent > 0.0):
                    print("TRAD - ManageBuyingState: B2 reached, buy Order matched (not filled) and sellTrigger is set, place sell order and go to SELLING ============================================")                   
                    self.nextState = 'SELLING' 
                else:
                    print("TRAD - ManageBuyingState: B2 reached, buy Order matched (not filled) and sellTrigger is not set, go to WAITING TO SELL ============================================")
                    self.nextState = 'WAITING_TO_SELL'
            else: # Order still ongoing or no limit order performed
                # Market buy if enabled and if price is below risk line
                # Check current price towards risk line
                riskLineThresholdInFiat = self.theMarketData.MRKT_GetLastRiskLineValue() * theConfig.CONFIG_RiskLinePercentsAboveThresholdToBuy
                if ((self.currentPriceValue < riskLineThresholdInFiat) and (theConfig.CONFIG_ENABLE_MARKET_ORDERS == True)): 
                    print("TRAD - ManageBuyingState: B2 reached, price below risk, canceling ongoing buy order before sending Market order")
                    # Cancel ongoing order
                    self.theTransactionManager.TRNM_CancelOngoingOrder()
                    # In real market conditions, wait for GDAX accounts to be refreshed
                    if (theConfig.CONFIG_INPUT_MODE_IS_REAL_MARKET == True):
                        time.sleep(0.8)
                            
                    if (self.theTransactionManager.TRNM_BuyNow() == True):
                        self.nextState = 'WAITING_TO_SELL'
                        self.ongoingBuyOrderWasFree = False
                        self.currentBuyPriceInFiat = self.theTransactionManager.TRNM_GetCurrentBuyInitialPrice()
                        
                        if (self.sellTriggerInPercent > 0.0):
                            print("TRAD - ManageBuyingState: B2 reached, price below risk, Market Buy ordered and successful, sellTrigger is set, place sell order and go to SELLING ============================================")
                                      
                            # In real market conditions, wait for GDAX accounts to be refreshed
                            if (theConfig.CONFIG_INPUT_MODE_IS_REAL_MARKET == True):
                                time.sleep(10)
                        
                            self.theTransactionManager.TRNM_StartBuyOrSellAttempt("SELL", self.currentBuyPriceInFiat * (1 + (self.sellTriggerInPercent / 100)))                  
                            self.nextState = 'SELLING'     
                        else:
                            print("TRAD - ManageBuyingState: B2 reached, price below risk, Market Buy ordered and successful: Going to WAITING_TO_SELL ============================================")
                    else:
                        print("TRAD - ManageBuyingState: B2 reached, price below risk, Market Buy ordered and failed: Going to WAITING_TO_BUY ============================================")
                        self.nextState = 'WAITING_TO_BUY'
                else:
                    # Cancel ongoing order
                    self.theTransactionManager.TRNM_CancelOngoingOrder()
                    print("TRAD - ManageBuyingState: B2 reached, no market buy allowed or high risk: don't continue buying, go to WAITING_TO_BUY ============================================")
        else:
            # B1 < MACD < B2
            # If MACD < B1, order shall have been filled            
            pass 
                    

    
    # When MACD indicator is > SELL1 THRESHOLD : No sell signal, do nothing
    # When MACD indicator is < SELL1 THRESHOLD and > SELL2 THRESHOLD : Try to place a sell limit order on top of the order book
    # When MACD indicator is < SELL2 THRESHOLD : Do a market sell order
    # => The limit order mode (betwen S1 and S2 threshold) has not been fully tested. So I recommend to only use market orders.
    # To do that, set SELL1 THRESHOLD to a value greater than SELL2 THRESHOLD in TradingBotConfig file so that only MACD < S2 THRESHOLD will occur.
    def ManageWaitingToSellState(self):
        
        #print("ManageWaitingToSellState")
        
        currentMidMarketPrice = self.theMarketData.MRKT_GetLastRefPrice()        
        risingRatio = float(currentMidMarketPrice) / self.theTransactionManager.TRNM_GetCurrentBuyInitialPrice()
        isS1ThresholdReached = (self.previousMACDValue > theConfig.CONFIG_MACD_SELL_1_THRESHOLD) and (self.currentMACDValue <= theConfig.CONFIG_MACD_SELL_1_THRESHOLD)
        isAutoSellThresholdReached = risingRatio < (1 - (self.theSettings.SETT_GetSettings()["autoSellThreshold"]/100))
        isS2ThresholdReached = (self.previousMACDValue > theConfig.CONFIG_MACD_SELL_2_THRESHOLD) and (self.currentMACDValue <= theConfig.CONFIG_MACD_SELL_2_THRESHOLD)
        
        
        #isS1ThresholdReached = True
        
        # Compute min ratio to sell without loss
        if (self.ongoingBuyOrderWasFree == True):
            minProfitRatio = theConfig.CONFIG_MIN_PRICE_ELEVATION_RATIO_TO_SELL + 0*float(self.theSettings.SETT_GetSettings()["platformTakerFee"])*0.01
        else:
            minProfitRatio = theConfig.CONFIG_MIN_PRICE_ELEVATION_RATIO_TO_SELL + 1*float(self.theSettings.SETT_GetSettings()["platformTakerFee"])*0.01
        
        # If price is high enough to sell with no loss (covers tax fees + minimum profit ratio)
        if (risingRatio > minProfitRatio):            
            # Check MACD sell signal
            if (isS1ThresholdReached):
                print("TRAD - ManageWaitingToSellState: S1 crossed and rising ratio is OK to sell. Placing limit sell order.")
                self.theTransactionManager.TRNM_StartBuyOrSellAttempt("SELL", minProfitRatio * float(currentMidMarketPrice))
                self.nextState = 'SELLING'
            elif (isS2ThresholdReached): # Market sell
                self.ManageSellingState()
            else:
                pass
                # Price high enough to sell but no MACD cross
        # If auto-sell threshold is reached, market sell now
        elif ((isAutoSellThresholdReached) and (self.theSettings.SETT_GetSettings()["autoSellThreshold"] != 0.0)):
            if (self.theTransactionManager.TRNM_SellNow(True) == True):
                self.nextState = 'WAITING_TO_BUY'
                self.ongoingBuyOrderWasFree = False
                print("TRAD - ManageWaitingToSellState: Auto-sell Threshold reached, Market Sell ordered and successful: Going to WAITING_TO_BUY ============================================")
            else:
                print("TRAD - ManageWaitingToSellState: Auto-sell Threshold reached, Market Sell order FAILED, staying in WAITING_TO_SELL state ============================================")

            

    def ManageSellingState(self):
    
        #print("ManageSellingState")
    
        # Is ongoing limit order filled?
        currentSellOrderState = self.theTransactionManager.TRNM_GetOngoingLimitOrderState()
        isS2ThresholdReached = (self.previousMACDValue > theConfig.CONFIG_MACD_SELL_2_THRESHOLD) and (self.currentMACDValue <= theConfig.CONFIG_MACD_SELL_2_THRESHOLD)
        # Is auto-sell threshold reached?
        currentMidMarketPrice = self.theMarketData.MRKT_GetLastRefPrice()    
        
        # Buy ongoing
        if (self.theTransactionManager.TRNM_GetCurrentBuyInitialPrice() > 0):
            risingRatio = float(currentMidMarketPrice) / self.theTransactionManager.TRNM_GetCurrentBuyInitialPrice()
            isAutoSellThresholdReached = risingRatio < (1 - (self.theSettings.SETT_GetSettings()["autoSellThreshold"]/100))
        else:
        # No buy ongoing, for example a sell trigger limit order has filled so currentBuyInitialPrice has been reset
            isAutoSellThresholdReached = False
        
        #if (currentSellOrderState == "NONE"):
        #    print("TRAD - ManageSellingState: Sell limit order canceled: go back to WAITING TO SELL state ============================================")
        #    self.nextState = 'WAITING_TO_SELL'
        #    self.theUIGraph.UIGR_updateInfoText("Sell order canceled. Waiting for next sell opportunity", False)
        #elif (currentSellOrderState == "FILLED"):         
        if (currentSellOrderState == "FILLED"):         
            print("TRAD - ManageSellingState: Ongoing sell limit order filled: going to WAITING TO BUY ============================================")
            self.nextState = 'WAITING_TO_BUY'
        elif (isS2ThresholdReached):
            if (currentSellOrderState == "MATCHED"):
                print("TRAD - ManageSellingState: Ongoing sell limit order matched: waiting to complete fill")
                pass # Do nothing, wait for complete sell 
            else: # Order is still ongoing
                if (theConfig.CONFIG_ENABLE_MARKET_ORDERS == True):
                    currentMidMarketPrice = self.theMarketData.MRKT_GetLastRefPrice() 
                    risingRatio = float(currentMidMarketPrice) / self.theTransactionManager.TRNM_GetCurrentBuyInitialPrice()
            
                    # Compute min ratio to sell without loss
                    if (self.ongoingBuyOrderWasFree == True):
                        # Count sell order price only, buy was free
                        minProfitRatio = theConfig.CONFIG_MIN_PRICE_ELEVATION_RATIO_TO_SELL + 1*float(self.theSettings.SETT_GetSettings()["platformTakerFee"])*0.01
                    else:
                        minProfitRatio = theConfig.CONFIG_MIN_PRICE_ELEVATION_RATIO_TO_SELL + 2*float(self.theSettings.SETT_GetSettings()["platformTakerFee"])*0.01
             
                    # If profit is positive, market sell
                    if (risingRatio > minProfitRatio):
                        print("TRAD - ManageSellingState: S2 reached, price below risk, canceling ongoing sell order before sending Market order")
                        # Cancel ongoing order: too risky to maintain it
                        self.theTransactionManager.TRNM_CancelOngoingOrder()
                        # In real market conditions, wait for GDAX accounts to be refreshed
                        if (theConfig.CONFIG_INPUT_MODE_IS_REAL_MARKET == True):
                            time.sleep(0.3)
                                
                        if (self.theTransactionManager.TRNM_SellNow(False) == True):
                            self.nextState = 'WAITING_TO_BUY'
                            self.ongoingBuyOrderWasFree = False
                            print("TRAD - ManageSellingState: S2 reached, rising ratio profitable, Market Sell ordered and successful: Going to WAITING_TO_BUY ============================================")
                        else:
                            print("TRAD - ManageSellingState: S2 reached, rising ratio profitable, sell market order FAILED, staying in SELLING state ============================================")
                    else:
                        pass
                        # Price is not high enough to market sell
                else:
                    pass
                    # Market orders not allowed. Only try to sell with limit orders                    
        elif ((isAutoSellThresholdReached) and (self.theSettings.SETT_GetSettings()["autoSellThreshold"] != 0.0)):
            print("TRAD - ManageSellingState: Auto-sell Threshold reached, canceling ongoing limit order and performing market sell")
            
            self.theTransactionManager.TRNM_CancelOngoingOrder()
            
            # In real market conditions, wait for GDAX accounts to be refreshed
            if (theConfig.CONFIG_INPUT_MODE_IS_REAL_MARKET == True):
                time.sleep(0.4)
                
            if (self.theTransactionManager.TRNM_SellNow(True) == True):
                self.nextState = 'WAITING_TO_BUY'
                self.ongoingBuyOrderWasFree = False
                print("TRAD - ManageSellingState: Auto-sell Threshold reached, Market Sell ordered and successful: Going to WAITING_TO_BUY ============================================")
            else:
                print("TRAD - ManageSellingState: Auto-sell Threshold reached, Market Sell order FAILED, staying in SELLING state ============================================")

            
            
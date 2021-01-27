import time
from datetime import datetime

import threading

from GDAXControler import GDAXControler
from UIGraph import UIGraph
import TradingBotConfig as theConfig
import Notifier as theNotifier

class TransactionManager(object):


    def __init__(self, GDAXControler, UIGraph, MarketData, Settings):
        self.theGDAXControler = GDAXControler
        self.theUIGraph = UIGraph
        self.theMarketData = MarketData
        # Application settings data instance
        self.theSettings = Settings

        self.FiatAccountBalance = 0
        self.FIATAccountBalanceSimulated = 0
        self.initialFiatAccountBalance = 0 # Only necessary in Trading mode. In simulation mode, profit is only theoric
        self.initialInvestedFiatAmount = 0
        self.CryptoAccountBalance = 0
        self.cryptoAccountBalanceSimulated = 0
        self.theoricalProfit = 0
        self.realProfit = 0
        self.percentageProfit = 0
        self.currentBuyAmountInCryptoWithoutFee = 0
        self.currentBuyAmountInCryptoWithFee = 0
        self.currentSoldAmountInCryptoViaLimitOrder = 0
        self.averageSellPriceInFiat = 0
        self.platformTakerFeeInPercent = float(self.theSettings.SETT_GetSettings()["platformTakerFee"]) * 0.01
        self.pendingNotificationToSend = ""

        self.buyTimeInTimeStamp = 0
        self.currentBuyInitialPriceInEUR = 0

        self.theUIGraph.UIGR_updateAccountsBalance(round(self.FiatAccountBalance, 6), round(self.CryptoAccountBalance, 6))
        self.theUIGraph.UIGR_updateTotalProfit(self.realProfit, self.theoricalProfit, self.percentageProfit, False)

        threadOrderPlacing = threading.Timer(1, self.threadOrderPlacing)
        threadOrderPlacing.start()
        self.threadOrderPlacingLock = threading.Lock()
        self.isOrderPlacingActive = False
        self.orderPlacingType = 'NONE'
        self.orderPlacingState = 'NONE'
        self.orderPlacingMinMaxPrice = 0
        self.orderPlacingCurrentPriceInFiat = 0

        self.isRunning = True


    def TRNM_InitiateNewTradingSession(self, startSession):
        self.theoricalProfit = 0
        self.realProfit = 0
        self.percentageProfit = 0
        self.currentBuyAmountInCryptoWithoutFee = 0
        self.currentBuyAmountInCryptoWithFee = 0
        self.currentSoldAmountInCryptoViaLimitOrder = 0
        self.averageSellPriceInFiat = 0
        self.buyTimeInTimeStamp = 0
        self.currentBuyInitialPriceInEUR = 0
        self.pendingNotificationToSend = ""
        self.isOrderPlacingActive = False
        self.orderPlacingType = 'NONE'
        self.orderPlacingState = 'NONE'
        self.orderPlacingMinMaxPrice = 0
        self.orderPlacingCurrentPriceInFiat = 0

        # Refresh platform taker fee
        self.platformTakerFeeInPercent = float(self.theSettings.SETT_GetSettings()["platformTakerFee"]) * 0.01
        print("TRNM - Initiating new trading session. Applied platformTakerFee multiplicator is %s" % self.platformTakerFeeInPercent)

        # In simulation mode, simulate an amount of money on the account
        if (theConfig.CONFIG_INPUT_MODE_IS_REAL_MARKET == False):
            self.initialFiatAccountBalance = 0
            self.FIATAccountBalanceSimulated = float(self.theSettings.SETT_GetSettings()["simulatedFiatBalance"])
            self.initialInvestedFiatAmount = float(self.theSettings.SETT_GetSettings()["investPercentage"]) * 0.01 * self.FIATAccountBalanceSimulated
            self.cryptoAccountBalanceSimulated = 0
            self.theUIGraph.UIGR_updateAccountsBalance(self.FIATAccountBalanceSimulated, self.cryptoAccountBalanceSimulated)
            self.theUIGraph.UIGR_updateTotalProfit(self.realProfit, self.theoricalProfit, self.percentageProfit, True)
        else:
            self.initialFiatAccountBalance = self.theGDAXControler.GDAX_GetFiatAccountBalance()
            print("TRNM - Initial fiat balance is %s" % self.initialFiatAccountBalance)
            self.FIATAccountBalanceSimulated = 0
            self.cryptoAccountBalanceSimulated = 0
            self.initialInvestedFiatAmount = float(self.theSettings.SETT_GetSettings()["investPercentage"]) * 0.01 * self.initialFiatAccountBalance
            self.theUIGraph.UIGR_updateTotalProfit(self.realProfit, self.theoricalProfit, self.percentageProfit, False)
            self.theGDAXControler.GDAX_RefreshAccountsDisplayOnly()
            self.theGDAXControler.GDAX_RequestAccountsBalancesUpdate()

        if (startSession == True):
            self.theUIGraph.UIGR_updateInfoText("Waiting for next buy opportunity", False)

    def TRNM_TerminateCurrentTradingSession(self):
        print("TRNM - Terminating current trading session...")
        
        self.FIATAccountBalanceSimulated = 0
        self.cryptoAccountBalanceSimulated = 0
        self.theUIGraph.UIGR_updateInfoText("", False)
        self.pendingNotificationToSend = ""
        self.isOrderPlacingActive = False
        self.isOrderPlacingActive = True
        self.orderPlacingCurrentPriceInFiat = 0
        self.isOrderPlacingActive = False
        self.orderPlacingState = "NONE"

        if (theConfig.CONFIG_INPUT_MODE_IS_REAL_MARKET == False):
            pass 
        else:
            # In real trading mode let GDAX controler update the accounts labels. TRNM will manage
            # money / refresh itself when initiating the new trading session
            self.theGDAXControler.GDAX_CancelOngoingLimitOrder()

    def TRNM_getCryptoBalance(self):
        return self.theGDAXControler.GDAX_GetCryptoAccountBalance()

    def TRNM_ForceAccountsUpdate(self):
        self.theGDAXControler.GDAX_RequestAccountsBalancesUpdate()

    def TRNM_getBTCBalance(self):
        return self.theGDAXControler.GDAX_GetBTCAccountBalance()

    def TRNM_StartBuyOrSellAttempt(self, buyOrSell, MinMaxPrice):
        
        if (buyOrSell == "BUY"):
            print("TRNM - Limit %s requested, max buy price is %s %s" % (buyOrSell, round(MinMaxPrice, 5), self.theSettings.SETT_GetSettings()["strFiatType"]))
            self.theUIGraph.UIGR_updateInfoText("Placing %s order, max buy price is %s %s" % (buyOrSell, round(MinMaxPrice, 5), self.theSettings.SETT_GetSettings()["strFiatType"]), False)
        elif (buyOrSell == "SELL"):
            print("TRNM - Limit %s requested, min sell price is %s %s" % (buyOrSell, round(MinMaxPrice, 5), self.theSettings.SETT_GetSettings()["strFiatType"]))
            self.theUIGraph.UIGR_updateInfoText("Placing %s order, min sell price is %s %s" % (buyOrSell, round(MinMaxPrice, 5), self.theSettings.SETT_GetSettings()["strFiatType"]), False)
        else:
            print("TRNM - Limit %s requested, unknown order type" % buyOrSell)
        
        if (theConfig.CONFIG_INPUT_MODE_IS_REAL_MARKET == True):
            
            self.threadOrderPlacingLock.acquire()
        
            self.isOrderPlacingActive = True
            self.orderPlacingCurrentPriceInFiat = 0
            self.orderPlacingType = buyOrSell
            self.orderPlacingState = 'ONGOING'
            self.orderPlacingMinMaxPrice = MinMaxPrice
            
            if (buyOrSell == "BUY"):
                self.currentBuyAmountInCryptoWithoutFee = 0
                self.currentBuyAmountInCryptoWithFee = 0
                self.currentSoldAmountInCryptoViaLimitOrder = 0
                self.averageSellPriceInFiat = 0
                self.currentBuyInitialPriceInEUR = 0
                    
            self.threadOrderPlacingLock.release()
            
        else:
            # In simulation, buy and sell are simulated on buy / sell status retrieving
            if (buyOrSell == "BUY"):
                self.orderPlacingType = "SIMULATED_BUY"
            elif (buyOrSell == "SELL"):
                self.orderPlacingType = "SIMULATED_SELL"

        
        
    def TRNM_GiveupBuyOrSellAttempt(self):
        
        self.threadOrderPlacingLock.acquire()
        
        print("TRNM - TRNM_GiveupBuyOrSellAttempt")
        self.isOrderPlacingActive = True
        self.orderPlacingCurrentPriceInFiat = 0
        self.isOrderPlacingActive = False
        self.orderPlacingState = "NONE"

        self.threadOrderPlacingLock.release()
        
        
    def computeBuyCapabilityInCrypto(self, includeHeldBalance):
        buyCapabilityInCrypto = 0.0
        accountBalanceHeld = 0.0
        
        if (theConfig.CONFIG_INPUT_MODE_IS_REAL_MARKET == True):
            self.FiatAccountBalance = self.theGDAXControler.GDAX_GetFiatAccountBalance()
            if (includeHeldBalance):
                accountBalanceHeld = self.theGDAXControler.GDAX_GetFiatAccountBalanceHeld()
                self.FiatAccountBalance += accountBalanceHeld
            currentPriceInFiat = self.theGDAXControler.GDAX_GetRealTimePriceInEUR()
            buyCapabilityInCrypto = float(self.FiatAccountBalance) / float(currentPriceInFiat)
            print("TRNM - computeBuyCapabilityInCrypto: capability is %s (current balance is %s + %s (hold))" % (buyCapabilityInCrypto, self.FiatAccountBalance, accountBalanceHeld))
        else:
            buyCapabilityInCrypto = self.FIATAccountBalanceSimulated / self.theMarketData.MRKT_GetLastRefPrice()
        return buyCapabilityInCrypto

    def computeProfitEstimation(self, isSellFeeApplied, soldAmountInCryptoWithFee):         
        # Don't include fee to get actual amount of money invested by the user (its cost for user point of view), not the amount of money actually invested in the platform after deducing the fee
        InvestmentInFiat = self.currentBuyInitialPriceInEUR * self.currentBuyAmountInCryptoWithoutFee
        if (isSellFeeApplied):
            SellPriceWithFeeInFiat = (self.averageSellPriceInFiat * soldAmountInCryptoWithFee) * (1-(self.platformTakerFeeInPercent))
        else:
            SellPriceWithFeeInFiat = (self.averageSellPriceInFiat * soldAmountInCryptoWithFee)
            
        print("TRNM - ComputeProfitEstimation : Buy  price with fee: %s" % InvestmentInFiat)
        print("TRNM - ComputeProfitEstimation : Sell price with fee: %s, fee applied? %s" % (SellPriceWithFeeInFiat, isSellFeeApplied))
        profitEstimation = (SellPriceWithFeeInFiat - InvestmentInFiat)
        return [profitEstimation, SellPriceWithFeeInFiat]
        
        
    def TRNM_BuyNow(self):
        if ((self.theGDAXControler.GDAX_IsConnectedAndOperational() == "True") or (theConfig.CONFIG_INPUT_MODE_IS_REAL_MARKET == False)):
            if (self.currentBuyAmountInCryptoWithoutFee == 0): # Security : no telesopic buys
                bOrderIsSuccessful = False
                bAmountIsAboveMinimumRequested = False

                # Refresh account balances =======================================================================
                self.FiatAccountBalance = self.theGDAXControler.GDAX_GetFiatAccountBalance()
                self.CryptoAccountBalance = self.theGDAXControler.GDAX_GetCryptoAccountBalance()

                # Compute capability  ============================================================================
                BuyCapabilityInCrypto = self.computeBuyCapabilityInCrypto(False)
                print("TRNM - Buy Now, capability is: %s Crypto (fiat balance is %s, crypto balance is %s)" % (BuyCapabilityInCrypto, self.FiatAccountBalance, self.CryptoAccountBalance))
                
                # Compute and fill Buy data ======================================================================
                if (theConfig.CONFIG_INPUT_MODE_IS_REAL_MARKET == True):
                    self.currentBuyInitialPriceInEUR = self.theGDAXControler.GDAX_GetRealTimePriceInEUR()
                else:
                    self.currentBuyInitialPriceInEUR = self.theMarketData.MRKT_GetLastRefPrice()                
                ratioOfCryptoCapabilityToBuy = float(self.theSettings.SETT_GetSettings()["investPercentage"]) * 0.01
                self.currentBuyAmountInCryptoWithoutFee = BuyCapabilityInCrypto * ratioOfCryptoCapabilityToBuy
                self.currentBuyAmountInCryptoWithFee = BuyCapabilityInCrypto * ratioOfCryptoCapabilityToBuy * (1-(self.platformTakerFeeInPercent))

                # Perform transaction  ===========================================================================
                print("TRNM - Buy Now, amount is: %s Crypto" % self.currentBuyAmountInCryptoWithoutFee)
                bAmountIsAboveMinimumRequested = self.theGDAXControler.GDAX_IsAmountToBuyAboveMinimum(self.currentBuyAmountInCryptoWithoutFee)
                print("TRNM - Amount to buy is above minimum possible ? %s" % bAmountIsAboveMinimumRequested)
                if (bAmountIsAboveMinimumRequested == True):
                    if (theConfig.CONFIG_INPUT_MODE_IS_REAL_MARKET == True):
                        # Real market: Send the Buy order
                        bOrderIsSuccessful = self.theGDAXControler.GDAX_SendBuyOrder(self.currentBuyAmountInCryptoWithoutFee)
                    else:
                        # Simulation: Compute new simulated balances
                        self.FIATAccountBalanceSimulated = self.FIATAccountBalanceSimulated - (self.FIATAccountBalanceSimulated * ratioOfCryptoCapabilityToBuy)
                        self.cryptoAccountBalanceSimulated = self.currentBuyAmountInCryptoWithFee
                        self.theUIGraph.UIGR_updateAccountsBalance(round(self.FIATAccountBalanceSimulated, 5), round(self.cryptoAccountBalanceSimulated, 5))
                        bOrderIsSuccessful = True
                
                # Update display  ============================================================================
                self.buyTimeInTimeStamp = time.time()
                print("TRNM - === BUY %s Crypto at %s Fiat" % (self.currentBuyAmountInCryptoWithoutFee, self.currentBuyInitialPriceInEUR))
                buyTimeStr = datetime.fromtimestamp(int(self.buyTimeInTimeStamp)).strftime('%H:%M')
                if (bOrderIsSuccessful == True):
                    self.performBuyDisplayActions(False)
                else:
                    # Buy transaction failed, cancel
                    self.currentBuyAmountInCryptoWithoutFee = 0
                    self.currentBuyAmountInCryptoWithFee = 0
                    self.currentSoldAmountInCryptoViaLimitOrder = 0
                    self.averageSellPriceInFiat = 0
                    self.currentBuyInitialPriceInEUR = 0
                    if (bAmountIsAboveMinimumRequested == False):
                        self.theUIGraph.UIGR_updateInfoText("%s: Buy order error: amount is too low, increase your %s balance" % (buyTimeStr, self.theSettings.SETT_GetSettings()["strFiatType"]), True)
                    else:
                        self.theUIGraph.UIGR_updateInfoText("%s: Buy order error" % buyTimeStr, True)

                return bOrderIsSuccessful
            else:
                print("TRNM - Trying to buy but there's already a pending buy. Aborted.")
                return False
        else:
            print("TRNM - Trying to buy but GDAX Controler not operational. Aborted.")
            return False


    def TRNM_SellNow(self, isStopLossSell):
        if ((self.theGDAXControler.GDAX_IsConnectedAndOperational() == "True") or (theConfig.CONFIG_INPUT_MODE_IS_REAL_MARKET == False)):
            if (self.currentBuyAmountInCryptoWithoutFee >= theConfig.MIN_CRYPTO_AMOUNT_REQUESTED_TO_SELL):
                bOrderIsSuccessful = False

                # Refresh account balances =================================================================================
                self.FiatAccountBalance = self.theGDAXControler.GDAX_GetFiatAccountBalance()
                self.CryptoAccountBalance = self.theGDAXControler.GDAX_GetCryptoAccountBalance()

                print("TRNM - Sell Now (fiat balance is %s, crypto balance is %s)" % (self.FiatAccountBalance, self.CryptoAccountBalance))

                # Send the Sell order ======================================================================================
                if (theConfig.CONFIG_INPUT_MODE_IS_REAL_MARKET == True):
                    # Subtract quantum so that it compensate up roundings when retrieving balance that could be greater than actual crypto balance and cause an insufficient funds sell error
                    bOrderIsSuccessful = self.theGDAXControler.GDAX_SendSellOrder(self.CryptoAccountBalance - theConfig.CONFIG_CRYPTO_PRICE_QUANTUM)        
                    self.averageSellPriceInFiat = self.theGDAXControler.GDAX_GetRealTimePriceInEUR()
                else:
                    self.averageSellPriceInFiat = self.theMarketData.MRKT_GetLastRefPrice()
                    
                # Compute profit estimation ================================================================================
                [profitEstimationInFiat, sellPriceWithFeeInFiat] = self.computeProfitEstimation(True, self.currentBuyAmountInCryptoWithFee)

                # If in simulation, simulate the sell amount of money going back to the FIAT account =======================
                if (theConfig.CONFIG_INPUT_MODE_IS_REAL_MARKET == False):
                    #                                    FIAT balance already present      sell value (with GDAX fee) -> money that goes back into fiat
                    self.FIATAccountBalanceSimulated = self.FIATAccountBalanceSimulated + sellPriceWithFeeInFiat
                    self.cryptoAccountBalanceSimulated = 0
                    self.theUIGraph.UIGR_updateAccountsBalance(round(self.FIATAccountBalanceSimulated, 5), round(self.cryptoAccountBalanceSimulated, 5))
                    bOrderIsSuccessful = True

                # Update display
                sellTimeInTimestamp = time.time()
                sellTimeStr = datetime.fromtimestamp(int(sellTimeInTimestamp)).strftime('%Hh%M')

                if (bOrderIsSuccessful == True):
                    self.theoricalProfit = self.theoricalProfit + profitEstimationInFiat
                    
                    if (theConfig.CONFIG_INPUT_MODE_IS_REAL_MARKET == True):
                        currentMidMarketPrice = self.theGDAXControler.GDAX_GetRealTimePriceInEUR()
                    else:
                        currentMidMarketPrice = self.theMarketData.MRKT_GetLastRefPrice()
                    
                    print("=== SELL %s at %s EUR. Profit made : %s" % (self.currentBuyAmountInCryptoWithFee, currentMidMarketPrice, profitEstimationInFiat))
                    self.performSellDisplayActions(False, isStopLossSell, currentMidMarketPrice, profitEstimationInFiat)
                    self.currentBuyAmountInCryptoWithoutFee = 0
                    self.currentBuyAmountInCryptoWithFee = 0
                    self.currentSoldAmountInCryptoViaLimitOrder = 0
                    self.averageSellPriceInFiat = 0
                    self.currentBuyInitialPriceInEUR = 0
                    self.buyTimeInTimeStamp = 0                    
                    self.TRNM_RefreshAccountBalancesAndProfit()
                else:
                    self.theUIGraph.UIGR_updateInfoText("%s: Sell order error" % sellTimeStr, True)

                return bOrderIsSuccessful
            else:
                print("TRNM - Trying to sell but no more BTC on the account. Aborted")
                return False
        else:
            print("TRNM - Trying to buy but GDAX Controler not operational. Aborted.")
            return False

    def TRNM_WithdrawBTC(self, destinationAddress, amountToWithdrawInBTC):
        print("TRNM - Withdraw %s BTC to %s" % (amountToWithdrawInBTC, destinationAddress))

        # Check if balance is OK
        if (float(self.TRNM_getBTCBalance()) >= amountToWithdrawInBTC):
            withdrawRequestReturn = self.theGDAXControler.GDAX_WithdrawBTC(destinationAddress, amountToWithdrawInBTC)
            if (withdrawRequestReturn != "Error"):
                print("TRNM - Withdraw BTC: No error")
                return withdrawRequestReturn
            else:
                return "Error"
        else:
            return "Error"

    def TRNM_ResetBuyData(self):
        self.theUIGraph.UIGR_updateInfoText("Last Buy has probably been sold manually", False)
        self.currentBuyAmountInCryptoWithoutFee = 0
        self.currentBuyAmountInCryptoWithFee = 0
        self.currentBuyInitialPriceInEUR = 0
        self.currentSoldAmountInCryptoViaLimitOrder = 0
        self.averageSellPriceInFiat = 0

    def TRNM_GetCurrentBuyInitialPrice(self):
        
        self.threadOrderPlacingLock.acquire()
        
        currentBuyInitialPriceInEUR = self.currentBuyInitialPriceInEUR
        
        self.threadOrderPlacingLock.release()
        
        return self.currentBuyInitialPriceInEUR

    def TRNM_RefreshAccountBalancesAndProfit(self):
        print("TRNM - Refresh Account balances and profit")

        # Real calculation is only applicable on real market
        if (theConfig.CONFIG_INPUT_MODE_IS_REAL_MARKET == True):
            # Sleep before fetching account balance (let time to GDAXControler to retrieve the new balances)
            time.sleep(0.5)
            self.FiatAccountBalance = self.theGDAXControler.GDAX_GetFiatAccountBalance()
            # Update real profit only if nothing is spent in BTC
            if (self.currentBuyAmountInCryptoWithoutFee < theConfig.CONFIG_CRYPTO_PRICE_QUANTUM):
                print("TRNM - Nothing spent in Crypto, profit update  to %s - initial was %s" % (self.FiatAccountBalance, self.initialFiatAccountBalance))
                self.realProfit = self.FiatAccountBalance - self.initialFiatAccountBalance
                self.percentageProfit = ((self.realProfit + self.initialInvestedFiatAmount) / (self.initialInvestedFiatAmount) - 1) * 100
                if (self.pendingNotificationToSend != ""):
                    theNotifier.SendWhatsappMessage(self.pendingNotificationToSend + "\n*Total profit: %s %%*" % round(self.percentageProfit, 1) )
            else:
                print("TRNM - RefreshAccountBalancesAndProfit : currentBuyAmountInCryptoWithoutFee greater than quantum: don't update profit. currentBuyAmountInCryptoWithoutFee is %s" % self.currentBuyAmountInCryptoWithoutFee)
                
            self.CryptoAccountBalance = self.theGDAXControler.GDAX_GetCryptoAccountBalance()
            self.theUIGraph.UIGR_updateTotalProfit(round(self.realProfit, 7), round(self.theoricalProfit, 7), round(self.percentageProfit, 1), False)
        else:
            self.percentageProfit = ((self.theoricalProfit + self.initialInvestedFiatAmount) / (self.initialInvestedFiatAmount) - 1) * 100
            self.theUIGraph.UIGR_updateTotalProfit(0, round(self.theoricalProfit, 7), round(self.percentageProfit, 1), True)
            if (self.pendingNotificationToSend != ""):
                theNotifier.SendWhatsappMessage(self.pendingNotificationToSend + "\n*Total profit: %s %%*" % round(self.percentageProfit, 1) )

        self.pendingNotificationToSend = ""

    def TRNM_GetOngoingLimitOrderState(self):
        
        # In simulation always return filled
        if (theConfig.CONFIG_INPUT_MODE_IS_REAL_MARKET == False):
            if (self.orderPlacingType == "SIMULATED_BUY"):
                self.orderPlacingType = "NONE"
                self.SimulateBuyOrderFilled()
                return "FILLED"
            elif (self.orderPlacingType == "SIMULATED_SELL"):
                # If sell trigger is set, simulated the sell when price reaches the trigger threshold
                sellTriggerInPercent = self.theSettings.SETT_GetSettings()["sellTrigger"]
                if (sellTriggerInPercent > 0.0):
                    #print((1+(sellTriggerInPercent/100))*self.currentBuyInitialPriceInEUR)
                    #print("ref price %s" % self.theMarketData.MRKT_GetLastRefPrice())
                    if (self.theMarketData.MRKT_GetLastRefPrice() >= ((1+(sellTriggerInPercent/100))*self.currentBuyInitialPriceInEUR)):
                        print("TRNM - GetOngoingLimitOrderState: Simulated price : %s above sellTrigger, simulate sell order filled" % self.theMarketData.MRKT_GetLastRefPrice())
                        self.averageSellPriceInFiat = self.theMarketData.MRKT_GetLastRefPrice()
                        self.SimulateSellOrderFilled()

                        return "FILLED"
                    else:
                        return "ONGOING" 
                else:
                    print("TRNM - GetOngoingLimitOrderState: SellTriggerInPercent null, simulate MACD-based sell")
                    self.averageSellPriceInFiat = self.theMarketData.MRKT_GetLastRefPrice()
                    self.SimulateSellOrderFilled()
                    # MACD-based sell trigger
                    return "FILLED" 
            else:
                print("TRNM - GetOngoingLimitOrderState: Unknown orderPlacingType. NONE returned.")                 
                return "NONE"
        else: # Real market        
            self.threadOrderPlacingLock.acquire()
            currentState = self.orderPlacingState
            
            if (currentState == "FILLED"):
                self.orderPlacingState = "NONE"
            
            self.threadOrderPlacingLock.release()
            
            return currentState

    def TRNM_CancelOngoingOrder(self):
        
        self.threadOrderPlacingLock.acquire()
        
        self.theGDAXControler.GDAX_CancelOngoingLimitOrder()
        
        self.isOrderPlacingActive = False
        self.orderPlacingCurrentPriceInFiat = 0
        self.orderPlacingType = "NONE"
        self.orderPlacingState = 'NONE'
        
        self.threadOrderPlacingLock.release()
        
        self.TRNM_ForceAccountsUpdate()
        
    def threadOrderPlacing(self):
        while (self.isRunning == True):
            if (self.theGDAXControler.GDAX_IsConnectedAndOperational() == "True"):
                if (self.isOrderPlacingActive == True):
                    liveBestBidPrice = self.theGDAXControler.GDAX_GetLiveBestBidPrice()  
                    liveBestAskPrice = self.theGDAXControler.GDAX_GetLiveBestAskPrice() 
                        
                    isOrderFilled = False
                    isReplaceOrderNeeded = False
    
                    self.threadOrderPlacingLock.acquire()
    
                    # Already an order placed ? Evaluate if not filled and still on the best bid / ask position
                    if (self.orderPlacingCurrentPriceInFiat > 0):
                        if (self.theGDAXControler.GDAX_GetCurrentLimitOrderState() == "FILLED"): # ORDER IS TOTALLY FILLED
                            print("TRNM - threadOrderPlacing: Order totally filled part1, request account balances update")
                            self.theGDAXControler.GDAX_RequestAccountsBalancesUpdate()
                            if (self.orderPlacingType == "BUY"):                                
                                # Set / Refresh buy data
                                self.currentBuyAmountInCryptoWithoutFee = self.theGDAXControler.GDAX_GetAveragePriceInFiatAndSizeFilledInCrypto()[1]
                                self.currentBuyAmountInCryptoWithFee = self.currentBuyAmountInCryptoWithoutFee
                                self.currentBuyInitialPriceInEUR = self.theGDAXControler.GDAX_GetAveragePriceInFiatAndSizeFilledInCrypto()[0]
                                self.isOrderPlacingActive = False # Set to false before display                                            
                                self.performBuyDisplayActions(True)
                            elif (self.orderPlacingType == "SELL"):
                                self.currentSoldAmountInCryptoViaLimitOrder = self.theGDAXControler.GDAX_GetAveragePriceInFiatAndSizeFilledInCrypto()[1]
                                self.averageSellPriceInFiat = self.theGDAXControler.GDAX_GetAveragePriceInFiatAndSizeFilledInCrypto()[0]
                                profitEstimationInFiat = self.computeProfitEstimation(True, self.currentSoldAmountInCryptoViaLimitOrder)[0]
                                self.isOrderPlacingActive = False # Set to false before display
                                self.performSellDisplayActions(True, False, liveBestAskPrice, profitEstimationInFiat)
                                # Total profit computation
                                self.currentBuyAmountInCryptoWithoutFee = 0 # Necessary for TRNM_RefreshAccountBalancesAndProfit
                                self.theoricalProfit = self.theoricalProfit + profitEstimationInFiat
                                self.TRNM_RefreshAccountBalancesAndProfit()                        
                            self.orderPlacingCurrentPriceInFiat = 0
                            self.orderPlacingType = "NONE"
                            self.orderPlacingState = 'FILLED'
                            isOrderFilled = True
                            print("TRNM - threadOrderPlacing: Order totally filled part2, order placing process closed")                                                
                        elif (self.theGDAXControler.GDAX_GetCurrentLimitOrderState() == "MATCHED"): # Order has been partially (or totally filled). In case of totally filled, it will also enter the FILLED branch
                            # Set / Refresh buy data
                            if (self.orderPlacingType == "BUY"):
                                # If there's been a new match since last iteration (or it's the first match)
                                if (self.currentBuyAmountInCryptoWithoutFee != self.theGDAXControler.GDAX_GetAveragePriceInFiatAndSizeFilledInCrypto()[1]):
                                    self.currentBuyAmountInCryptoWithoutFee = self.theGDAXControler.GDAX_GetAveragePriceInFiatAndSizeFilledInCrypto()[1]
                                    self.currentBuyAmountInCryptoWithFee = self.currentBuyAmountInCryptoWithoutFee
                                    self.currentBuyInitialPriceInEUR = self.theGDAXControler.GDAX_GetAveragePriceInFiatAndSizeFilledInCrypto()[0]
                                    self.performBuyDisplayActions(True)
                                    self.orderPlacingState = 'MATCHED'
                                else:
                                    pass # Same quantity matched since previous iteration, do nothing
                            elif (self.orderPlacingType == "SELL"):
                                # If there's been a new match since last iteration (or it's the first match)
                                if (self.currentSoldAmountInCryptoViaLimitOrder != self.theGDAXControler.GDAX_GetAveragePriceInFiatAndSizeFilledInCrypto()[1]):
                                    # If there's been a new match since last iteration
                                    self.currentSoldAmountInCryptoViaLimitOrder = self.theGDAXControler.GDAX_GetAveragePriceInFiatAndSizeFilledInCrypto()[1]
                                    self.averageSellPriceInFiat = self.theGDAXControler.GDAX_GetAveragePriceInFiatAndSizeFilledInCrypto()[0]
                                    profitEstimationInFiat = self.computeProfitEstimation(True, self.currentSoldAmountInCryptoViaLimitOrder)[0]
                                    self.performSellDisplayActions(True, False, liveBestAskPrice, profitEstimationInFiat)
                                    self.orderPlacingState = 'MATCHED'
                                else:
                                    pass # Same quantity matched since previous iteration, do nothing                                        
                        elif (self.theGDAXControler.GDAX_GetCurrentLimitOrderState() == "NONE"): # Order does not exist anymore due to any reason (canceled?)
                            self.isOrderPlacingActive = False
                            self.orderPlacingCurrentPriceInFiat = 0
                            self.orderPlacingType = "NONE"
                            self.orderPlacingState = 'NONE'
                            print("TRNM - Order does not exist anymore (canceled?)")
                        elif (self.theGDAXControler.GDAX_GetCurrentLimitOrderState() == "SUBMITTED"):
                            print("TRNM - threadOrderPlacing: Order submitted. Do nothing and wait for open state")
                        else:
                            # Order still opened: check if it's still at the right price
                            if (self.orderPlacingType == "BUY"):
                                if (self.orderPlacingCurrentPriceInFiat != liveBestBidPrice):
                                    isReplaceOrderNeeded = True
                                    print("TRNM - threadOrderPlacing: Buy order replace is needed. Current Bid is %s, Best order book bid is: %s" % (self.orderPlacingCurrentPriceInFiat, liveBestBidPrice))
                            elif (self.orderPlacingType == "SELL"):
                                # Replace sell order on top of the order book only if sell order is not from a sellTrigger
                                sellTriggerInPercent = self.theSettings.SETT_GetSettings()["sellTrigger"]
                                if (sellTriggerInPercent != 0.0):
                                    # Replace order on top of the book only if current lowest sell price (ask) is higher than our min sell price
                                    # If not sell order will be placed / replaced at the min requested price
                                    if (liveBestAskPrice > self.orderPlacingMinMaxPrice):
                                        if (self.orderPlacingCurrentPriceInFiat != liveBestAskPrice):
                                            isReplaceOrderNeeded = True
                                            print("TRNM - threadOrderPlacing: Sell order replace is needed. Current Ask is %s, Best order book ask is: %s" % (self.orderPlacingCurrentPriceInFiat, liveBestAskPrice))
                                    else:
                                        if (self.orderPlacingCurrentPriceInFiat != self.orderPlacingMinMaxPrice):
                                            isReplaceOrderNeeded = True
                                            print("TRNM - threadOrderPlacing: Best ask below min minRequested price, sell order replace at minRequested price is needed. Current Ask is %s, Best order book ask is: %s" % (self.orderPlacingCurrentPriceInFiat, liveBestAskPrice))
                                else:
                                    # Sell order is from a sellTrigger : do not try to replace it on top of the book
                                    pass       
                                
                    # Replace order on top of the book (or place it for the first time)                    
                    if (isOrderFilled == False):
                        if ((isReplaceOrderNeeded) or (self.orderPlacingCurrentPriceInFiat == 0)):
                            statusIsOk = True
                            
                            if (self.orderPlacingType == "BUY"):
                                print("TRNM - threadOrderPlacing: Placing / Replacing a Buy limit order on the top of the order book")                            
                                # Include held account balance because if we replace an order already set, the Fiat amount is held by the current 
                                # order (that will be canceled before placing the new order)
                                buyCapabilityInCrypto = self.computeBuyCapabilityInCrypto(True) 
                                ratioOfCryptoCapabilityToBuy = float(self.theSettings.SETT_GetSettings()["investPercentage"]) * 0.01
                                
                                # Check if buy price is not too high
                                if (liveBestBidPrice < self.orderPlacingMinMaxPrice):
                                    self.orderPlacingCurrentPriceInFiat = liveBestBidPrice
                                    print("TRNM - threadOrderPlacing: BUY - LiveBestBidPrice = %s, ask=%s" % (liveBestBidPrice, liveBestAskPrice))
                                    statusIsOk = self.theGDAXControler.GDAX_PlaceLimitBuyOrder(buyCapabilityInCrypto * ratioOfCryptoCapabilityToBuy, self.orderPlacingCurrentPriceInFiat)
                                elif (self.currentBuyInitialPriceInEUR == 0): # Order book buy price too high: cancel order only if it has not matched
                                    print("TRNM - threadOrderPlacing: live best bid price too high: cancel order")
                                    self.theGDAXControler.GDAX_CancelOngoingLimitOrder()
                                    # live best bid too high: cancel order
                                    self.isOrderPlacingActive = False
                                    self.orderPlacingCurrentPriceInFiat = 0
                                    self.orderPlacingType = "NONE"
                                    self.orderPlacingState = 'NONE'
                            elif (self.orderPlacingType == "SELL"):
                                print("TRNM - threadOrderPlacing: Placing / Replacing a Sell limit order on the top of the order book")
                                sellAmountInCrypto = self.theGDAXControler.GDAX_GetCryptoAccountBalance() + self.theGDAXControler.GDAX_GetCryptoAccountBalanceHeld() - theConfig.CONFIG_CRYPTO_PRICE_QUANTUM                                
                                # Check if sell price is not too high
                                if (liveBestAskPrice > self.orderPlacingMinMaxPrice):
                                    self.orderPlacingCurrentPriceInFiat = liveBestAskPrice
                                    print("TRNM - threadOrderPlacing: SELL - LiveBestBidPrice = %s, ask=%s" % (liveBestBidPrice, liveBestAskPrice))
                                    statusIsOk = self.theGDAXControler.GDAX_PlaceLimitSellOrder(sellAmountInCrypto, self.orderPlacingCurrentPriceInFiat)
                                else:
                                    # Current live sell price is below the min requested sell price (we want to sell higher)
                                    # Do not cancel order: needs to be sold. Can be an order requested by sellTrigger.
                                    # If not placed yet, put order on the min requested price
                                    self.orderPlacingCurrentPriceInFiat = self.orderPlacingMinMaxPrice
                                    statusIsOk = self.theGDAXControler.GDAX_PlaceLimitSellOrder(sellAmountInCrypto, self.orderPlacingMinMaxPrice)                                    
                            else:
                                print("TRNM - threadOrderPlacing: Incorrect order placing type: %s" % self.orderPlacingType)
                            
                            if (statusIsOk == False):
                                print("TRNM - threadOrderPlacing: Placing the order failed. Waiting for next %s opportunity" % self.orderPlacingType)
                                self.isOrderPlacingActive = False
                                self.orderPlacingCurrentPriceInFiat = 0
                                self.orderPlacingType = "NONE"
                                self.orderPlacingState = 'NONE'
                                
                    self.threadOrderPlacingLock.release()

            time.sleep(0.03)

    # /!\ TODO Check if UIGR calls are thread safe
    def performBuyDisplayActions(self, isLimitOrder):
                
        if (isLimitOrder):
            if (self.isOrderPlacingActive == False): # Order is totally filled
                sellTriggerInPercent = self.theSettings.SETT_GetSettings()["sellTrigger"]
                if (sellTriggerInPercent > 0.0):
                    sellThreshold = self.currentBuyInitialPriceInEUR * ((sellTriggerInPercent/100)+1) 
                else:
                    sellThreshold = self.currentBuyInitialPriceInEUR * (theConfig.CONFIG_MIN_PRICE_ELEVATION_RATIO_TO_SELL + 2*self.platformTakerFeeInPercent) # Not the official one : for display only. Trader class manages this actual feature.
                self.theUIGraph.UIGR_updateInfoText("%s %s Bought @ %s %s via limit order - Waiting for a sell opportunity above %s %s" % (round(self.currentBuyAmountInCryptoWithoutFee, 5), self.theSettings.SETT_GetSettings()["strCryptoType"], round(self.currentBuyInitialPriceInEUR, 5), self.theSettings.SETT_GetSettings()["strFiatType"], round(sellThreshold, 5), self.theSettings.SETT_GetSettings()["strFiatType"]), False)            
                theNotifier.SendWhatsappMessage("*BUY filled* %s %s @ %s %s via limit order - Waiting for a sell opportunity above %s %s" % (round(self.currentBuyAmountInCryptoWithoutFee, 5), self.theSettings.SETT_GetSettings()["strCryptoType"], round(self.currentBuyInitialPriceInEUR, 5), self.theSettings.SETT_GetSettings()["strFiatType"], round(sellThreshold, 5), self.theSettings.SETT_GetSettings()["strFiatType"]))
                
                # Order is totally filled, add marker
                self.theUIGraph.UIGR_addMarker(1)  
            else:
                self.theUIGraph.UIGR_updateInfoText("%s %s Partially bought @ %s %s. Still ongoing, waiting for next matches" % (round(self.currentBuyAmountInCryptoWithoutFee, 5), self.theSettings.SETT_GetSettings()["strCryptoType"], round(self.currentBuyInitialPriceInEUR, 5), self.theSettings.SETT_GetSettings()["strFiatType"]), False)            
                theNotifier.SendWhatsappMessage("*BUY match* %s %s @ %s %s. Still ongoing, waiting for next matches" % (round(self.currentBuyAmountInCryptoWithoutFee, 5), self.theSettings.SETT_GetSettings()["strCryptoType"], round(self.currentBuyInitialPriceInEUR, 5), self.theSettings.SETT_GetSettings()["strFiatType"]))                  
        else:
            buyTimeStr = datetime.fromtimestamp(int(self.buyTimeInTimeStamp)).strftime('%H:%M')
            sellThreshold = self.currentBuyInitialPriceInEUR * (theConfig.CONFIG_MIN_PRICE_ELEVATION_RATIO_TO_SELL + 2*self.platformTakerFeeInPercent) # Not the official one : for display only. Trader class manages this actual feature.
            self.theUIGraph.UIGR_updateInfoText("%s - %s %s Bought @ %s %s - Waiting for a sell opportunity above %s %s" % (buyTimeStr, round(self.currentBuyAmountInCryptoWithoutFee, 5), self.theSettings.SETT_GetSettings()["strCryptoType"], round(self.currentBuyInitialPriceInEUR, 5), self.theSettings.SETT_GetSettings()["strFiatType"], round(sellThreshold, 5), self.theSettings.SETT_GetSettings()["strCryptoType"]), False)            
            theNotifier.SendWhatsappMessage("*BUY* %s %s @ %s %s - Waiting for a sell opportunity above %s %s" % (round(self.currentBuyAmountInCryptoWithoutFee, 5), self.theSettings.SETT_GetSettings()["strCryptoType"], round(self.currentBuyInitialPriceInEUR, 5), self.theSettings.SETT_GetSettings()["strFiatType"], round(sellThreshold, 5), self.theSettings.SETT_GetSettings()["strFiatType"]))
        
            self.theUIGraph.UIGR_addMarker(1)
        
    def performSellDisplayActions(self, isLimitOrder, isStopLossSell, sellPriceInFiat, profitEstimationInFiat):
        sellTimeInTimestamp = time.time()
        sellTimeStr = datetime.fromtimestamp(int(sellTimeInTimestamp)).strftime('%Hh%M')
        
        if (isLimitOrder):
            if (self.isOrderPlacingActive == False): # Order is totally filled
                self.theUIGraph.UIGR_updateInfoText("SELL filled at %s, profit was about %s EUR. Waiting for next buy opportunity" % (sellTimeStr, round(profitEstimationInFiat, 5)), False)
                self.pendingNotificationToSend = ("*SELL filled* at %s %s, profit was about *%s EUR*. " % (round(sellPriceInFiat, 5), self.theSettings.SETT_GetSettings()["strFiatType"], round(profitEstimationInFiat, 5)))
                # Order is totally filled, add marker
                self.theUIGraph.UIGR_addMarker(2)
            else:                
                self.theUIGraph.UIGR_updateInfoText("Partial sell at %s, profit was about %s EUR. Still ongoing, waiting for next matches" % (sellTimeStr, round(profitEstimationInFiat, 5)), False)
                self.pendingNotificationToSend = ("*SELL match* at %s %s, profit was about *%s EUR*. " % (round(sellPriceInFiat, 5), self.theSettings.SETT_GetSettings()["strFiatType"], round(profitEstimationInFiat, 5)))
        else:
            if (isStopLossSell == False):
                self.theUIGraph.UIGR_updateInfoText("Last sell at %s, profit was about %s EUR. Waiting for next buy opportunity" % (sellTimeStr, round(profitEstimationInFiat, 5)), False)
                self.pendingNotificationToSend = ("*SELL* at %s %s, profit was about *%s EUR*. " % (round(sellPriceInFiat, 5), self.theSettings.SETT_GetSettings()["strFiatType"], round(profitEstimationInFiat, 5)))
            else:
                self.theUIGraph.UIGR_updateInfoText("StopLoss-sell at %s, loss was about %s EUR. Waiting for next buy opportunity" % (sellTimeStr, round(profitEstimationInFiat, 5)), True)
                self.pendingNotificationToSend = ("*STOPLOSS-SELL* at %s %s, loss was about *%s EUR*. " % (round(sellPriceInFiat, 5), self.theSettings.SETT_GetSettings()["strFiatType"], round(profitEstimationInFiat, 5)))
            
            # Add marker
            self.theUIGraph.UIGR_addMarker(2)
        
    def SimulateBuyOrderFilled(self):
        # Compute capability  ============================================================================
        BuyCapabilityInCrypto = self.computeBuyCapabilityInCrypto(False)
        print("TRNM - Simulated limit Buy Now, capability is: %s Crypto" % BuyCapabilityInCrypto)
        
        # Compute and fill Buy data ======================================================================
        self.currentBuyInitialPriceInEUR = self.theMarketData.MRKT_GetLastRefPrice()
            
        ratioOfCryptoCapabilityToBuy = float(self.theSettings.SETT_GetSettings()["investPercentage"]) * 0.01
        self.currentBuyAmountInCryptoWithoutFee = BuyCapabilityInCrypto * ratioOfCryptoCapabilityToBuy
        self.currentBuyAmountInCryptoWithFee = BuyCapabilityInCrypto * ratioOfCryptoCapabilityToBuy * (1-(self.platformTakerFeeInPercent))

        # Simulated market: simulate new balances
        self.FIATAccountBalanceSimulated = self.FIATAccountBalanceSimulated - (self.currentBuyInitialPriceInEUR * self.currentBuyAmountInCryptoWithoutFee)
        self.cryptoAccountBalanceSimulated = self.currentBuyAmountInCryptoWithoutFee
        self.UIGR_update_accounts_balance = self.theUIGraph.UIGR_updateAccountsBalance(round(self.FIATAccountBalanceSimulated, 5), round(self.cryptoAccountBalanceSimulated, 5))
        
        # Reset simulated buy order data
        self.orderPlacingType = "NONE"
        
        # Update display  =================================================================================
        self.buyTimeInTimeStamp = time.time()
        print("TRNM - Simulated limit Buy performed: %s Crypto at %s Fiat" % (self.currentBuyAmountInCryptoWithoutFee, self.currentBuyInitialPriceInEUR))
        self.performBuyDisplayActions(True)


    def SimulateSellOrderFilled(self):
        print("TRNM - Simulated limit Sell Now")
                
        [profitEstimationInFiat, sellPriceWithFeeInFiat] = self.computeProfitEstimation(True, self.currentBuyAmountInCryptoWithFee)

        # Simulate the sell amount of money going back to the FIAT account =======================
            #                                    FIAT balance already present      sell value (with GDAX fee) -> money that goes back into fiat
        self.FIATAccountBalanceSimulated = self.FIATAccountBalanceSimulated + sellPriceWithFeeInFiat
        self.cryptoAccountBalanceSimulated = 0
        self.theUIGraph.UIGR_updateAccountsBalance(round(self.FIATAccountBalanceSimulated, 5), round(self.cryptoAccountBalanceSimulated, 5))
        bOrderIsSuccessful = True

        print("TRNM - Simulated limit Sell performed: sellAmountInFiat=%s, profit estimation in fiat=%s" % (sellPriceWithFeeInFiat, profitEstimationInFiat))

        self.isOrderPlacingActive = False # Set to false before display
        self.performSellDisplayActions(True, False, sellPriceWithFeeInFiat, profitEstimationInFiat)
        
        self.theoricalProfit = self.theoricalProfit + profitEstimationInFiat
        self.TRNM_RefreshAccountBalancesAndProfit()
        
        # Reset simulated sell order data
        self.orderPlacingType = "NONE"
        
        # Reset buy data
        self.currentBuyAmountInCryptoWithoutFee = 0
        self.currentBuyAmountInCryptoWithFee = 0
        self.currentSoldAmountInCryptoViaLimitOrder = 0
        self.averageSellPriceInFiat = 0
        self.currentBuyInitialPriceInEUR = 0
        self.buyTimeInTimeStamp = 0                

import time
import threading

import TradingBotConfig as theConfig
from MarketData import MarketData
from Trader import Trader


class InputDataHandler(object):


    def __init__(self, GDAXControler, UIGraph, MarketData, Trader, Settings):
        
        self.theGDAXControler = GDAXControler
        self.theUIGraph = UIGraph
        self.theMarketData = MarketData
        self.theTrader = Trader
        self.theSettings = Settings
        self.currentSubSchedulingFactor = 1
        self.nbIterations = 0
        self.PreloadHistoricDataStatus = "Idle"
        self.operationalStatus = "Idle"
        self.simulationPauseIsRequested = False
        self.simulationStopIsRequested = False
        self.liveTradingStopIsRequested = False
        self.abortOperations = False
        
        self.currentSubSchedulingFactor = self.theGDAXControler.GDAX_GetHistoricDataSubSchedulingFactor()
    
    def INDH_GetPreloadHistoricDataStatus(self):
        # If read once at Ended state, go back to Idle state
        if (self.PreloadHistoricDataStatus == "Ended"):
            self.PreloadHistoricDataStatus = "Idle"
            return "Ended"
        else:
            return self.PreloadHistoricDataStatus
    

    def PreloadHistoricData(self, displayWholeBufferAtTheEnd, nbHoursToPreload):
        self.nbHoursToPreload = nbHoursToPreload
        
        # First call in a sequence, launch loading thread
        if (self.PreloadHistoricDataStatus != "Ongoing"):
            self.PreloadHistoricDataStatus = "Ongoing"
            self.threadLoadHistoricData = threading.Timer(0, self.LoadHistoricData, [displayWholeBufferAtTheEnd])
            self.threadLoadHistoricData.start()
        else:
            # Fetching is ongoing, do nothing
            pass
    
    def INDH_PrepareHistoricDataSinceGivenHours(self, displayWholeBufferAtTheEnd, nbHoursToPreload):
        
        if ((self.PreloadHistoricDataStatus == "Idle") or (self.PreloadHistoricDataStatus == "Ended")):
            self.PreloadHistoricData(displayWholeBufferAtTheEnd, nbHoursToPreload)
        else:
            # Ongoing, do nothing but poll INDH_GetPreloadHistoricDataStatus
            pass
        
    def GetLoadedDataStartTimestamp(self):
        return self.theGDAXControler.GDAX_GetLoadedDataStartTimeStamp()
    
    def GetLoadedDataEndTimestamp(self):
        return self.theGDAXControler.GDAX_GetLoadedDataStopTimeStamp()
    
    # Blocking function that allows GDAXControler to load historic data. Shall be called from a background thread.
    def LoadHistoricData(self, displayWholeBufferAtTheEndArray):
        print("INDH - Thread Load Historic Data: Started")

        self.initialTimeStampInUserTime = time.time()
        
        print("INDH - nbHoursToPreload: %s" % str(self.nbHoursToPreload))
        print("INDH - initialTimeStampInUserTime: %s" % str(self.initialTimeStampInUserTime))
        
        desiredStartTimeStamp = time.time() - (self.nbHoursToPreload * 3600)
        desiredEndTimeStamp = time.time()
        
        print("INDH - INDH_PrepareHistoricDataSinceGivenHours : desired start = %s, desired end = %s" % (desiredStartTimeStamp, desiredEndTimeStamp))
            
        # If preloaded data start time is after desired start time with a delta, reloading is necessary OR
        # if preloaded end time is before current time with a delta, reloading is necessary
        if (self.GetLoadedDataStartTimestamp() > (desiredStartTimeStamp +  theConfig.NB_SECONDS_THRESHOLD_FROM_NOW_FOR_RELOADING_DATA)) or ((self.GetLoadedDataEndTimestamp() + theConfig.NB_SECONDS_THRESHOLD_FROM_NOW_FOR_RELOADING_DATA) < desiredEndTimeStamp):
            print("INDH - INDH_PrepareHistoricDataSinceGivenHours : Desired data not present. Loaded start is %s, end is %s. Loading in background thread..." % (self.GetLoadedDataStartTimestamp(), self.GetLoadedDataEndTimestamp()))
            startTimeStampToLoadData = self.initialTimeStampInUserTime - (self.nbHoursToPreload * 3600)
            stopTimeStampToLoadData = self.initialTimeStampInUserTime
            print("INDH - Will retrieve Historic price data from %s to %s" % (startTimeStampToLoadData, stopTimeStampToLoadData))
            self.theGDAXControler.GDAX_LoadHistoricData(startTimeStampToLoadData, stopTimeStampToLoadData)
            print("INDH - Historic Data loading ended")
            print("INDH - Display everything in one shot: %s" % displayWholeBufferAtTheEndArray)
        else:
            print("INDH - No need to preload historic data")
            
        # Only true for trading where we want to see the historic price d'un coup 
        if (displayWholeBufferAtTheEndArray ==  True):
            print("INDH - Thread Load Historic Data: batch MarketData and Graph update. Subscheduling factor is %s" % self.currentSubSchedulingFactor)
            
            self.theMarketData.MRKT_ResetAllData(1)
                    
            startTimeStampRequested = time.time() - (theConfig.NB_HISTORIC_DATA_HOURS_TO_PRELOAD_FOR_TRADING * 3600)
            self.theGDAXControler.GDAX_SetReadIndexFromPos(startTimeStampRequested)
                
            nbOfSamplesToDisplayOnGraph = theConfig.CONFIG_NB_POINTS_LIVE_TRADING_GRAPH   
            print("INDH - Choosen to display %s points on graph" % nbOfSamplesToDisplayOnGraph)
            self.theUIGraph.UIGR_ResetAllGraphData(False, -1, int(nbOfSamplesToDisplayOnGraph))   
            
            [self.retrievedTime, self.retrievedPrice, endOfList] = self.theGDAXControler.GDAX_GetNextHistoricDataSample()
            currentTimeStamp = self.retrievedTime
            endOfList = False
            timeStep = theConfig.CONFIG_TIME_BETWEEN_RETRIEVED_SAMPLES_IN_MS / 1000
            
            while ((endOfList == False) and (self.abortOperations == False)):
                #print("currentTimestamp %s" % currentTimeStamp)
                if (currentTimeStamp >= self.retrievedTime):
                    # Update market data with this original (non artificial) sample
                    self.theMarketData.MRKT_updateMarketData(self.retrievedTime, self.retrievedPrice)
                    currentTimeStamp = self.retrievedTime
                    # Get next sample in memory
                    [self.retrievedTime, self.retrievedPrice, endOfList] = self.theGDAXControler.GDAX_GetNextHistoricDataSample()
                else:
                    # Interpolate with previous sample value
                    currentTimeStamp = currentTimeStamp + timeStep
                    self.theMarketData.MRKT_updateMarketData(currentTimeStamp, self.retrievedPrice)
                    
            self.theUIGraph.UIGR_updateGraphs()
            self.theUIGraph.UIGR_performManualYRangeRefresh()     

        self.PreloadHistoricDataStatus = "Ended"
    
    # Initiates the simulation thread. 
    def INDH_PerformSimulation(self, nbHoursFromNow):
        # Security : if historic data is still loading, return Ended
        if (self.PreloadHistoricDataStatus == "Ongoing"):
            return "Ended"
        
        # Open background thread to perform simulation
        if (self.operationalStatus != "Ongoing"):
            self.operationalStatus = "Ongoing"
            self.simulationPauseIsRequested = False
            self.simulationStopIsRequested = False
            
            # Set read index at right pos
            startTimeStampRequested = time.time() - (nbHoursFromNow * 3600)
            setReadPosResult = self.theGDAXControler.GDAX_SetReadIndexFromPos(startTimeStampRequested)
            
            if (setReadPosResult == True):
                # Clear graph data and enable continuous graph update
                self.theMarketData.MRKT_ResetAllData(self.theGDAXControler.GDAX_GetHistoricDataSubSchedulingFactor())
                self.theUIGraph.UIGR_ResetAllGraphData(True, startTimeStampRequested, theConfig.CONFIG_NB_POINTS_SIMU_GRAPH) # Last arg is the nb of points on simulation graph
                self.theUIGraph.UIGR_StartContinuousGraphRefresh(25)
                # Prepare trader
                self.theTrader.TRAD_ResetTradingParameters()
                # Launch simulation thread
                self.threadPerformSimulation = threading.Timer(0, self.PerformSimulationThread)
                self.threadPerformSimulation.start()
                return "Ongoing"
            else:
                # Read position not found, return Error
                return "Error"
        else:
            # Already initiated, should not happen
            return "Error"    
    
    def PerformSimulationThread(self):
        
        batchSamplesSizeForSpeed = self.theSettings.SETT_GetSettings()["simulationSpeed"] + 2
        batchSamplesInitGraph = theConfig.CONFIG_NB_POINTS_INIT_SIMU_GRAPH * self.getCurrentSubSchedulingFactor()
        nbHistoricSamplesRetrieved = 0
        [self.retrievedTime, self.retrievedPrice, endOfList] = self.theGDAXControler.GDAX_GetNextHistoricDataSample()
        currentTimeStamp = self.retrievedTime
        endOfList = False
        timeStep = theConfig.CONFIG_TIME_BETWEEN_RETRIEVED_SAMPLES_IN_MS / 1000
        
        print("INDH - Starting Simulation Thread. Batch size for simulation speed is %s" % batchSamplesSizeForSpeed)
        
        while ((endOfList == False) and (self.simulationStopIsRequested == False)):
            #print("currentTimestamp %s" % currentTimeStamp)
            if (currentTimeStamp >= self.retrievedTime):
                # Update market data with this original (non artificial) sample
                self.theMarketData.MRKT_updateMarketData(self.retrievedTime, self.retrievedPrice)
                currentTimeStamp = self.retrievedTime
                # Get next sample in memory
                [self.retrievedTime, self.retrievedPrice, endOfList] = self.theGDAXControler.GDAX_GetNextHistoricDataSample()
            else:
                # Interpolate with previous sample value
                currentTimeStamp = currentTimeStamp + timeStep
                self.theMarketData.MRKT_updateMarketData(currentTimeStamp, self.retrievedPrice)

            #start = time.clock()
            #self.theMarketData.MRKT_updateMarketData(self.retrievedTime, self.retrievedPrice)
            #print("MRKT_updateMarketData : %s" % (time.clock() - start))
            
            nbHistoricSamplesRetrieved = nbHistoricSamplesRetrieved + 1
            self.theTrader.TRAD_ProcessDecision()                        
            
            # Pause if UIGR is busy
            if (nbHistoricSamplesRetrieved > batchSamplesInitGraph): # Init graph phase passed
                if (nbHistoricSamplesRetrieved % batchSamplesSizeForSpeed == 0):
                    #print("UIGR_updateGraphs : %s" % (time.clock() - start))
                    #print("E")
                    while ((self.theUIGraph.UIGR_AreNewSamplesRequested() == False) and (self.simulationStopIsRequested == False)):
                        #print("pause")
                        time.sleep(0.002)
                  
            if (self.simulationPauseIsRequested == True):
                while ((self.simulationPauseIsRequested == True) and (self.simulationStopIsRequested == False)):
                    # Simulation is on pause, wait
                    time.sleep(0.05)
        
        # End of simulation                
        print("INDH - Simulation Thread has ended : Stop ? %s End of buffer ? %s" % (self.simulationStopIsRequested, endOfList))
        self.operationalStatus = "Ended"
        
    def INDH_GetOperationalStatus(self):
        return self.operationalStatus

    def INDH_PauseResumeSimulation(self):
        if (self.simulationPauseIsRequested == True):
            self.simulationPauseIsRequested = False
            self.theUIGraph.UIGR_SetPauseButtonAspect("PAUSE")
        else:
            self.theUIGraph.UIGR_SetPauseButtonAspect("RESUME")
            self.simulationPauseIsRequested = True
            
    def INDH_StopSimulation(self):
        if (self.simulationStopIsRequested == True):
            self.simulationStopIsRequested = False
        else:
            self.simulationStopIsRequested = True
            print("INDH - StopSimulation: setting simulationStopIsRequested to true")

    def INDH_StopLiveTrading(self):
        if (self.liveTradingStopIsRequested == True):
            self.liveTradingStopIsRequested = False
        else:
            self.liveTradingStopIsRequested = True
                    
    def INDH_PerformLiveTradingOperation(self, nbHoursFromNow):
        # Security : if historic data is still loading, return Ended
        if (self.PreloadHistoricDataStatus == "Ongoing"):
            return "Ended"
        
        # Open background thread to perform simulation
        if (self.operationalStatus != "Ongoing"):
            self.operationalStatus = "Ongoing"
            self.liveTradingStopIsRequested = False
            
            # Prepare trader
            self.theTrader.TRAD_ResetTradingParameters()
            
            # Prepare UIGR graph updater
            self.theUIGraph.UIGR_StartContinuousGraphRefresh(200)
            
            # Launch simulation thread
            self.threadPerformLiveTrading = threading.Timer(0, self.PerformLiveTradingThread)
            self.threadPerformLiveTrading.start()            
                
            return "Ongoing"
        else:
            # Already initiated, should not happen
            return "Error"    

    
    def PerformLiveTradingThread(self):
        nbLiveSamplesRetrieved = 0
        waitingCounter = 0
        timeToWaitInSecGranulaity = 0.1
        nbIterationToPassToWaitPeriodTime = (theConfig.CONFIG_TIME_BETWEEN_RETRIEVED_SAMPLES_IN_MS / 1000) / timeToWaitInSecGranulaity
        
        # While user does not want to stop trading
        while (self.liveTradingStopIsRequested == False):
            
            # Retrieve next live sample
            self.retrievedPrice = self.theGDAXControler.GDAX_GetRealTimePriceInEUR()    
            self.retrievedTime = time.time()

            self.theMarketData.MRKT_updateMarketData(self.retrievedTime, self.retrievedPrice)            
            self.theTrader.TRAD_ProcessDecision()
            
            nbLiveSamplesRetrieved = nbLiveSamplesRetrieved + 1
            
                       
            while ((self.liveTradingStopIsRequested == False) and (waitingCounter < nbIterationToPassToWaitPeriodTime)):
                time.sleep(timeToWaitInSecGranulaity)
                waitingCounter = waitingCounter + 1
                
            waitingCounter = 0
            
        # End of Live Trading        
        print("INDH - Live Trading Thread has ended : Stop ? %s" % (self.simulationStopIsRequested))
        self.operationalStatus = "Ended"
    
    def INDH_GetCurrentState(self):
        return self.marketPhase
        
    def getCurrentSpotPrice(self):
        return self.theGDAXControler.GDAX_GetRealTimePriceInEUR()
    
    def getCurrentSubSchedulingFactor(self):
        return self.currentSubSchedulingFactor
    
    def INDH_closeBackgroundOperations(self):
        print("INDH - Close background operations requested")
        self.abortOperations = True
        self.INDH_StopSimulation()
        self.INDH_StopLiveTrading()
from scipy import signal
import numpy as np
import time
import math

import TradingBotConfig as theConfig

class MarketData():
    

    MAX_HISTORIC_SAMPLES = 20000
    NB_POINTS_FOR_FAST_SMOOTH_FILTER = 600
    NB_POINTS_FOR_SLOW_SMOOTH_FILTER = 1200
    NB_POINTS_DELAY_FOR_RISK_LINE_COMPUTATION = 220
    NB_POINTS_FOR_RISK_LINE_COMPUTATION = 1200
    RISK_LINE_START_INDEX = - (NB_POINTS_FOR_RISK_LINE_COMPUTATION + NB_POINTS_DELAY_FOR_RISK_LINE_COMPUTATION)
    RISK_LINE_END_INDEX = - (NB_POINTS_DELAY_FOR_RISK_LINE_COMPUTATION)

    maxMACDValuePricePercentageForNormalization = 60 

    NB_POINTS_MIN_FOR_ESTABLISHMENT = NB_POINTS_FOR_SLOW_SMOOTH_FILTER
    
    
    def __init__(self, GDAXControler, UIGraph):
        
        self.theGDAXControler = GDAXControler
        self.theUIGraph = UIGraph
    
        # Init model data
        self.MRKT_ResetAllData(1)
        self.RefreshSmoothFiltersCoefficients()
        
    def MRKT_ResetAllData(self, UIGraphSubScheduling):
        print("MRKT - Reset all data")

        self.totalNbIterations = 0
        self.dataRefTime = []
        self.dataRefCryptoPriceInEUR = []
        self.dataRefSmoothAverageFast = []
        self.dataRefSmoothAverageSlow = []
        self.dataRefRiskLine = []
        self.dataRefMACD = []
        self.UIGraphSubScheduling = UIGraphSubScheduling
    
    def RefreshSmoothFiltersCoefficients(self):
        newSensitvityValue = self.theUIGraph.UIGR_getSensitivityLevelValue()
        print("MRKT - Applied coefficients : %s" % newSensitvityValue)
        
        if (newSensitvityValue == 6):
            N = 1
            WnFast=float(0.0333) # 1/30
            WnSlow=float(0.01) # 1/100
            self.maxMACDValuePricePercentageForNormalization = 0.006  
        elif (newSensitvityValue == 5):
            N = 1
            WnFast=float(0.01666) # 1/60
            WnSlow=float(0.005882) # 1/170
            self.maxMACDValuePricePercentageForNormalization = 0.007    
        elif (newSensitvityValue == 4):
            N = 1
            WnFast=float(0.010) # 1/80
            WnSlow=float(0.0040) # 1/230
            self.maxMACDValuePricePercentageForNormalization = 0.008    
        elif (newSensitvityValue == 3):
            N = 1
            WnFast=float(0.008) # 1/110
            WnSlow=float(0.003) # 1/250
            self.maxMACDValuePricePercentageForNormalization = 0.01    
        elif (newSensitvityValue == 2):
            N = 1
            WnFast=float(0.0040) # 1/
            WnSlow=float(0.0018) # 1/
            self.maxMACDValuePricePercentageForNormalization = 0.012             
        elif (newSensitvityValue == 1):
            N = 2
            WnFast=float(0.01111) # 1/90
            WnSlow=float(0.0041667) # 1/240
            self.maxMACDValuePricePercentageForNormalization = 0.012      
        else: # Should not happen
            N = 1
            WnFast=float(0.0125) # 1/80
            WnSlow=float(0.004347) # 1/230
            self.maxMACDValuePricePercentageForNormalization = 0.012   
        
        if (self.totalNbIterations > 1):
            self.maxMACDForNormalization = self.dataRefCryptoPriceInEUR[1] * self.maxMACDValuePricePercentageForNormalization
        else:
            self.maxMACDForNormalization = 10000 * self.maxMACDValuePricePercentageForNormalization
        
        print("MRKT - Coefficients updated. New self.maxMACDForNormalization is %s, WnFast = %s, WnSlow = %s" % (self.maxMACDForNormalization, WnFast, WnSlow))

        self.bFast, self.aFast = signal.butter(N, float(WnFast), 'low') # One gotcha is that Wn is a fraction of the Nyquist frequency (half the sampling frequency).
        self.bSlow, self.aSlow = signal.butter(N, float(WnSlow), 'low') # One gotcha is that Wn is a fraction of the Nyquist frequency (half the sampling frequency). 
       
    def MRKT_AreIndicatorsEstablished(self):
        #print("MRKT_AreIndicatorsEstablished - nb it %s  minRequested %s" % (self.totalNbIterations,self.MRKT_GetMinNumberOfRequiredSamplesForEstablishment()))
        if (self.totalNbIterations > self.NB_POINTS_MIN_FOR_ESTABLISHMENT):
            return True
        else:
            return False
    
    def MRKT_GetLastRiskLineValue(self):
        return self.dataRefRiskLine[-1]
    
    def MRKT_GetLastMACDValue(self):
        return self.dataRefMACD[-1]
    
    # Used in SImulation mode in order to get the price at which we buy or sell
    def MRKT_GetLastRefPrice(self):
        return self.dataRefCryptoPriceInEUR[-1]
    
    def MRKT_GetLastFastSmoothedPrice(self):
        return self.dataRefSmoothAverageFast[-1]
        
    # Needs one sample every 10 sec
    def MRKT_updateMarketData(self, newSampleTime, newSamplePrice):    
        
        if (newSampleTime is not None):
            if (newSamplePrice is not None):                 
                # Drop old samples (buffers shifts)
                self.dropOldData()
                
                # Add new sample
                self.updateMarketPriceAndTime(newSampleTime, newSamplePrice)
                
                # Update indicators
                self.updateFastSmoothAverage()
                self.updateSlowSmoothAverage()
                self.updatePriceMACD()
                self.updateRiskLine()
        
                # UI Data Update
                if (self.totalNbIterations % self.UIGraphSubScheduling == 0):  
                    self.theUIGraph.UIGR_updateNextIterationData(self.dataRefTime[-1], self.dataRefCryptoPriceInEUR[-1], self.dataRefSmoothAverageFast[-1], self.dataRefSmoothAverageSlow[-1], self.dataRefRiskLine[-1], self.dataRefMACD[-1])                    
                
                if (self.totalNbIterations % 20 == 0):       
                    # Update Smooth filters coefficients if needed. Check value changed in subscheduled part to save CPU
                    # Last condition is made for calibration of MACD normalization indicator with price data
                    if ((self.theUIGraph.UIGR_hasSensitivityLevelValueChanged() == True) or (self.totalNbIterations == 20)):
                        self.RefreshSmoothFiltersCoefficients()
                    
                self.totalNbIterations = self.totalNbIterations + 1
            else:
                print("MRKT - None Sampleprice detected")
        else:
            print("MRKT - None Sampletime detected")
            
    def dropOldData(self):
        if (self.totalNbIterations > self.MAX_HISTORIC_SAMPLES):
            self.dataRefTime.pop(0)
            self.dataRefCryptoPriceInEUR.pop(0) 
            if (self.totalNbIterations % self.UIGraphSubScheduling == 0):
                self.dataRefSmoothAverageFast.pop(0)
                self.dataRefSmoothAverageSlow.pop(0)
                self.dataRefRiskLine.pop(0)
                self.dataRefMACD.pop(0)
  
    def updateMarketPriceAndTime(self, newSampleTime, newSamplePrice):         

        self.dataRefCryptoPriceInEUR.append(newSamplePrice)
        self.dataRefTime.append(newSampleTime)
        
        # Update price on the UI
        if (self.totalNbIterations % self.UIGraphSubScheduling == 0):            
            self.theUIGraph.UIGR_updatePriceLbl(round(self.dataRefCryptoPriceInEUR[-1], 5))

    def updateFastSmoothAverage(self):
        if (self.totalNbIterations > self.NB_POINTS_FOR_FAST_SMOOTH_FILTER + 1):
            if (self.totalNbIterations % self.UIGraphSubScheduling == 0):
                self.dataRefSmoothAverageFast.append((signal.lfilter(self.bFast, self.aFast, self.dataRefCryptoPriceInEUR[-self.NB_POINTS_FOR_FAST_SMOOTH_FILTER:]))[-1])       
        else:
            self.dataRefSmoothAverageFast.append(self.dataRefCryptoPriceInEUR[-1]*0.999)
            
    def updateSlowSmoothAverage(self):
        if (self.totalNbIterations > self.NB_POINTS_FOR_SLOW_SMOOTH_FILTER + 1):
            if (self.totalNbIterations % self.UIGraphSubScheduling == 0):
                self.dataRefSmoothAverageSlow.append((signal.lfilter(self.bSlow, self.aSlow, self.dataRefCryptoPriceInEUR[-self.NB_POINTS_FOR_SLOW_SMOOTH_FILTER:]))[-1])
        else:
            self.dataRefSmoothAverageSlow.append(self.dataRefCryptoPriceInEUR[-1]*0.999)
               
    def updateRiskLine(self):
        if (self.totalNbIterations > self.NB_POINTS_FOR_RISK_LINE_COMPUTATION + 1):
            if (self.totalNbIterations % self.UIGraphSubScheduling == 0):   
                average = (np.sum(self.dataRefCryptoPriceInEUR[self.RISK_LINE_START_INDEX:self.RISK_LINE_END_INDEX])) / self.NB_POINTS_FOR_RISK_LINE_COMPUTATION

                self.dataRefRiskLine.append(average)
            else:
                pass # Keep last value
        else:
            self.dataRefRiskLine.append(0)
                        
    def updatePriceMACD(self):
        # Derivate is computed over smooth price data so wait until this one is established
        if (self.totalNbIterations > self.NB_POINTS_FOR_SLOW_SMOOTH_FILTER + 2):
            if (self.totalNbIterations % self.UIGraphSubScheduling == 0):
                localMACD = (self.dataRefSmoothAverageFast[-1] - self.dataRefSmoothAverageSlow[-1])
                self.dataRefMACD.append(localMACD * 100 / (self.maxMACDForNormalization))
        else:
            self.dataRefMACD.append(0)


import pickle
import ctypes # Message box popup

class Settings(object):
    '''
    classdocs
    '''


    def __init__(self):
        print("SETT - Constructor")
        
        # Default settings if no settings file has been saved
        self.settings = {"strAPIKey": "",
                    "strSecretKey": "",
                    "strPassphrase": "",
                    "bHasAcceptedConditions": False,
                    "strTradingPair": "BTC-EUR",
                    "strFiatType": "EUR",
                    "strCryptoType": "BTC",
                    "investPercentage": 90,
                    "platformTakerFee": 0.3,
                    "sellTrigger" : 0.0,
                    "autoSellThreshold": 0.0,
                    "simulatedFiatBalance": 1000,
                    "simulationSpeed": 20,
                    "simulationTimeRange": 24,
                    }
    
        self.tradingPairHasChanged = False
        self.APIDataHasChanged = False
        self.isSettingsFilePresent = False
        
        self.SETT_LoadSettings()
        
    def SETT_SaveSettings(self):
        print("SETT - Saving settings")
        try:
            pickle.dump(self.settings, open("astibot.settings", "wb"))
        except BaseException as e:
            self.MessageBoxPopup("Error during write operation of Astibot settings file. Check that you are running Astibot from a writable directory.", 0)

        self.SETT_DisplayCurrentSettings()
    
    def SETT_LoadSettings(self):
        print("SETT - Loading settings")
        try:
            self.settings = pickle.load(open("astibot.settings", "rb"))
            self.isSettingsFilePresent = True
        except BaseException as e:
            print("SETT - Exception : " + str(e))
            self.isSettingsFilePresent = False
            
            
        self.SETT_DisplayCurrentSettings()
    
    def SETT_IsSettingsFilePresent(self):
        return self.isSettingsFilePresent
        
    def SETT_GetSettings(self):
        return self.settings
        
    def SETT_DisplayCurrentSettings(self):
        for key, value in self.settings.items():
            print("SETT - %s: %s" % (key, value))
            
    def SETT_NotifyTradingPairHasChanged(self):
        self.tradingPairHasChanged = True
        
    def SETT_hasTradingPairChanged(self):
        if (self.tradingPairHasChanged == True):
            self.tradingPairHasChanged = False
            return True
        else:
            return False
    
    def SETT_NotifyAPIDataHasChanged(self):
        self.APIDataHasChanged = True
        
    def SETT_hasAPIDataChanged(self):
        if (self.APIDataHasChanged == True):
            self.APIDataHasChanged = False
            print("SETT - API Data has Changed - returning info")
            return True
        else:
            return False
           
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
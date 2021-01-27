CONFIG_VERSION = "1.3.1"

#####################################################################################################################
######## Operational Parameters
#####################################################################################################################

# False: CSV file input. True: Real-time market price 
CONFIG_INPUT_MODE_IS_REAL_MARKET = True

# Main ticker : Retrieves the next samples and processes them
CONFIG_MAIN_TICK_DURATION_IN_MS = 200

# Terrestrial time between two retrieved sample. 
#Should be equal to CONFIG_MAIN_TICK_DURATION_IN_MS in live mode, custom value in simulation mode that
# depends on the csv file sampling time
CONFIG_TIME_BETWEEN_RETRIEVED_SAMPLES_IN_MS = 10000

# UI Graph refresh per call to the main ticker
CONFIG_UI_GRAPH_UPDATE_SUBSCHEDULING = 1

# True to record price in output csv file. For the live mode only
CONFIG_RECORD_PRICE_DATA_TO_CSV_FILE = False

# True to enable real buy and sell transaction to the market
CONFIG_ENABLE_REAL_TRANSACTIONS = True

# Number of hours of historical samples to retrieve
NB_HISTORIC_DATA_HOURS_TO_PRELOAD_FOR_TRADING = 10

NB_SECONDS_THRESHOLD_FROM_NOW_FOR_RELOADING_DATA = 1000

CONFIG_NB_POINTS_LIVE_TRADING_GRAPH = 2500
CONFIG_NB_POINTS_SIMU_GRAPH = 620
CONFIG_NB_POINTS_INIT_SIMU_GRAPH = CONFIG_NB_POINTS_SIMU_GRAPH

# Quantum = 0.05 (%)
CONFIG_PLATFORM_TAKER_FEE_QUANTUM = 0.05 # 0.05 %
CONFIG_PLATFORM_TAKER_FEE_DEFAULT_VALUE = 5 # 0.25 %
CONFIG_PLATFORM_TAKER_FEE_MIN_ON_SLIDER = 0 # 0 %
CONFIG_PLATFORM_TAKER_FEE_MAX_ON_SLIDER = 40 # 2 %

# Quantum = 0.05 (%)
CONFIG_SELL_TRIGGER_PERCENTAGE_QUANTUM = 0.05 # 0.05 %
CONFIG_SELL_TRIGGER_PERCENTAGE_DEFAULT_VALUE = 0 # 0.0 %
CONFIG_SELL_TRIGGER_PERCENTAGE_MIN_ON_SLIDER = 0 # 0 %
CONFIG_SELL_TRIGGER_PERCENTAGE_MAX_ON_SLIDER = 40 # 2 %

# Quantum = 0.25 (%)
CONFIG_PLATFORM_AUTO_SELL_THRESHOLD_QUANTUM = 0.25 # 0.25 %
CONFIG_PLATFORM_AUTO_SELL_THRESHOLD_DEFAULT_VALUE = 0 # 0 %
CONFIG_PLATFORM_AUTO_SELL_THRESHOLD_MIN_ON_SLIDER = 0 # 0 %
CONFIG_PLATFORM_AUTO_SELL_THRESHOLD_MAX_ON_SLIDER = 40 # 10 %

CONFIG_SIMU_INITIAL_BALANCE_MIN = 0.001
CONFIG_SIMU_INITIAL_BALANCE_MAX = 20000

CONFIG_MIN_INITIAL_FIAT_BALANCE_TO_TRADE = 0.0001

CONFIG_DONATION_DEFAULT_AMOUNT_IN_BTC = 0.0002
CONFIG_BTC_DESTINATION_ADDRESS = "136wzpD2fYFRAAHLU5yVxiMNcARQtktoDo"


#####################################################################################################################
######## Trading Parameters
#####################################################################################################################
CONFIG_RISK_LINE_PERCENTS_ABOVE_THRESHOLD_TO_BUY_MIN = 0.97
CONFIG_RISK_LINE_PERCENTS_ABOVE_THRESHOLD_TO_BUY_MAX = 1.02
CONFIG_RiskLinePercentsAboveThresholdToBuy = 0.994

CONFIG_MAX_BUY_PRICE = 100000


# Buy policy: 
#     When MACD indicator is < BUY1 THRESHOLD : No buy signal, do nothing
#     When MACD indicator is > BUY1 THRESHOLD and < BUY1 THRESHOLD : Try to place a buy limit order on top of the order book
#     When MACD indicator is > BUY2 THRESHOLD : Do a market buy order
#     => The limit order mode (betwen B1 and B2 threshold) has not been fully tested. So I recommend to only use market orders.
#     For that, set BUY1 THRESHOLD to a value greater than BUY2 THRESHOLD in Config file so that only MACD > B2 THRESHOLD will occur.
CONFIG_MACD_BUY_1_THRESHOLD = 999
CONFIG_MACD_BUY_2_THRESHOLD = 0


# Sell policy:
#     When MACD indicator is > SELL1 THRESHOLD : No sell signal, do nothing
#     When MACD indicator is < SELL1 THRESHOLD and > SELL2 THRESHOLD : Try to place a sell limit order on top of the order book
#     When MACD indicator is < SELL2 THRESHOLD : Do a market sell order
#     => The limit order mode (betwen S1 and S2 threshold) has not been fully tested. So I recommend to only use market orders.
# To do that, set SELL1 THRESHOLD to a value greater than SELL2 THRESHOLD in TradingBotConfig file so that only MACD < S2 THRESHOLD will occur.
CONFIG_MACD_SELL_1_THRESHOLD = -999
CONFIG_MACD_SELL_2_THRESHOLD = 0

# A bit too approximative
MIN_CRYPTO_AMOUNT_REQUESTED_TO_SELL = 0.0005

# Minimum percentage ratio to sell with no loss : shall not include fees
CONFIG_MIN_PRICE_ELEVATION_RATIO_TO_SELL = 1.0005

# Orders policy : 'MAKER' or 'TAKER'
CONFIG_ENABLE_MARKET_ORDERS = True

# Percentage of the highest ask price to set buy price
CONFIG_LIMIT_BUY_PRICE_RADIO_TO_HIGHEST_ASK = 0.999

# Percentage of the highest ask price to set buy price
CONFIG_LIMIT_BUY_PRICE_RATIO_TO_HIGHEST_ASK = 1.0000

# Percentage of the lowest ask price to set buy price
CONFIG_LIMIT_SELL_PRICE_RATIO_TO_HIGHEST_BID = 1.0000

# Crypto price quantum. Useful for rounds
CONFIG_CRYPTO_PRICE_QUANTUM = 0.0000001

# Number of confirmed samples below auto-sell threshold to actually perform auto sell
CONFIG_AUTO_SELL_NB_CONFIRMATION_SAMPLES = 10


#####################################################################################################################
######## Debug Parameters
#####################################################################################################################
CONFIG_DEBUG_ENABLE_DUMMY_WITHDRAWALS = False
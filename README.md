# Astibot
**Astibot is a simple, visual and automated trading software for Coinbase Pro cryptocurrencies**

Astibot is a trading bot that operates on the Coinbase Pro trading platform through a set of API keys. Its trading strategy is basic, but it provides a powerful and interactive simulation tool to backtest your settings.

Astibot bases its decisions on 2 real-time indicators:
* **a MACD-like indicator:** it provides buy and sell signals based on 2 moving averages: one fast, one slow. These averages can be tuned to be short-term focused (very sensitive, ~5 min chart) or more robust to price noise (less sensitive, ~2h chart). They are not computed in a traditional way, but with signal processing algorithms (recursive low pass filters).
* **a risk indicator:** the purpose of this risk line is to avoid opening a trade too high that could hardly be sold with a profit. The user can set his own risk level thanks to a dedicated cursor. This line evolves automatically to match the average market level (based on the last few hours), but its value is weighted by the risk level the user has set.

![Alt text](/doc/astibot_overview.png?raw=true "Astibot overview")

## Main features
* Real-time graph update
* On-graph trades display (buy and sell markers)
* Live trading mode (real-time trading)
* Simulation mode (to backtest the settings)
* Customizable MACD-like decision indicator (to detect buy and sell opportunities)
* Supported Coinbase pro trading pairs: BTC-USD, BTC-EUR, ETH-USD, ETH-EUR, LTC-USD, LTC-EUR, BCH-USD, BCH-EUR, ETC-USD, ETC-EUR (new pairs are easy to add)

## Advanced features
* Risk line: a customizable, real-time updated limit price limit above which Astibot will never buy
* Stop loss: crypto is automatically sold if price is below a customizable percentage of the buy price
* Sell trigger: a fixed percentage above the buy price to sell, for scalping. After a buy, Astibot places a limit order at this percentage of the buy price. If this parameter is set to zero this feature is disabled and Astibot will rely on its MACD-like indicator to decide when to sell.
* Limit and Market orders management: when Astibot detects a buy (or a sell) opportunity, it first tries to buy (or sell) the asset through a limit order to benefit from the fee reduction (limit orders are less expensive and on the right side of the spread). If the order cannot be filled, Astibot decides to perform a market order (immediate effect, more expensive) or to cancel the buy if the buy opportunity strength has decreased too much.


## How to use Astibot ?

Astibot can run on any computer capable of runnning Python 3, including Raspberry Pi (very convenient for 24/7 trading).

#### Required dependencies
* Python 3
* PyQt5
* pyqtgraph
* ctypes
* numpy
* cbpro

#### Start-up

1. python Astibot.py
2. At first start-up, enter your Coinbase Pro API keys (view and trade permissions are required)

## Results

Let's talk about the key topic! I have run Astibot serveral weeks on my Raspberry pi.
Here are my conclusions:
* Astibot needs volatility to make profit: a 0.8% - 1% price amplitude on the short term chart is a minimum. These variations are required to detect dips and tops properly with the smoothing indicators, and to cover the buy and sell fees.
* Astibot runs well during sideways periods. If volume and volatility are good, Astibot can outperform the chart.
* Astibot is not very interesting during a bull market. Price dips are harder to find, and because of the risk line, Astibot never buys when price is too high.
* Astibot is not profitable during a bear market: it will detect a lot of dips, buy these dips and it will not be able to close a trade with profit because price will have decreased.

To sum up, the mose difficult part is to know **when** it is interesting to run Astibot for the next hours or days. 
But, there's no rule. Use the Simulation mode and tune the cursors to try :) 



## Development

I think current Astibot version could be a good starting point to implement more sophisticated strategies.
To understand the general software breakdown, a diagram is worth thousand words. Top modules call services from the modules below.
![Alt text](/doc/astibot_architecture.png?raw=true "Astibot software architecture")

## Known limitations
* In the current version, limit orders are considered to be free: that is not the case anymore since Coinbase Pro increased all their fees. Astibot needs to be updated to take this in consideration for the profit computation and trading strategy.
* Astibot only implements the Coinbase Pro interface. It would not be that hard to create a "BinanceControler", "BitfinexControler" ... to add multiplatform support. These specific controlers could herit from a more generic and abstrct controler seen from higher level modules (polymorphism).
* Some modules are too big and could be splitted into more micro modules (UIGraph for example).




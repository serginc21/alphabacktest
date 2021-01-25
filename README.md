# alphabacktest -- under construction #
-------

> **DISCLAIMER: The results this backtesting software might produce may not be accurate, reliable or suppose any evidence for reassurance on a trading strategy. The results are indicative and might not be appropiate for trading purposes. Therefore, the creator does not bear any responsibility for any losses you might incur as a result of using this software.**
> 
> **Please, be fully informed about the risks and costs associated with trading the financial markets, as it is one of the riskiest investment forms possible.**


## Description ##

alphabacktest is a library that aims at bringing algorithmic trading to all Pyhton programmers via a very simple set of methods that allow backtesting any trading strategy anyone can come up with.

You can find below an example of the structure to use when working with alphabacktest. The module is designed to be inherited in a new class created by the user and call the methods within the class. ```Backtest()``` has the engine to run the backtest and calls ```strategy()``` at each point.

```python
from alphabacktest import Backtest  

class mStrategy(Backtest):
    def __init__(self):
        super().__init__(ticker="AMZN")

    def strategy(self,_open, close, high, low, vol, dtime):
        if not self.has_positions():
            q = int(self.free_balance / close[-1])
            self.long_order(security=self.symbol, amount=q, dtime=dtime, price=close[-1])

if __name__ == '__main__':
    mStrategy()      

```
As seen, the usage is pretty straightforward, and does not require a huge effort for the user to import and/or work with it, being a smooth process and giving freedom to apply any strategy, from those based on technical indicators to machine learning, going through many different tools.

Regarding the data source (explained at Usage), getting the proper data is sometimes rather difficult, especially when one is looking for tight timeframes (1m,5m,15m...). This data is not usually free, so this module gives the chance to either get the data from Yahoo Finance or from a csv file that the user can have in their local memory from a purchase or own harvest. 

For backtesting, one of the critical parameters is the time it takes for the system to complete the backtest, especially when there are a lot of data points to go through. This highly affects to those studies that aim at assessing long periods with low timeframes. This package has been optimised in order to follow a chronological flow while maintaining a high execution speed. The average time of a loop execution is 0.004s with a simple strategy. Therefore, if there are over 400000 points, the backtesting can be very slow (over 20m).


## Installation ##

```$ pip install alphabacktest```

### Requirements ###

- Python 3.8.5+

### Dependencies ###

As some of the features provided by the module are meant to be optional, **the installation of alphabacktest does not depend** on the following modules.


- **TA-lib**. As there are sometimes difficulties when installing this module, there is an option for the backtest not to calculate any technical indicator (as all are based on TA-lib), so in that case you don't necessarily need to have it installed. In case you want to enable the calculation of technical indicators, you can find the module [here](https://github.com/mrjbq7/ta-lib).
- **Dash**. alphabacktest uses dash in order to plot and display the results. However, this option can also be desactivated. In case you want it, you can find it [here](https://dash.plotly.com/installation). 
- **Pandas datareader**. This module allows the program to import data from Yahoo Finance, you can find how to install it [here](https://github.com/pydata/pandas-datareader).

## Usage ## 

The ```super().__init__()``` is highly important here to define exactly how we want our backtest to be. It is customisable to an extent and allows multiple features to be desactivated or included.

```python
    super().__init__(self, 
            sym="",
            initial_time="first",
            final_time="last",
            dateformat="%Y-%m-%d",
            file_path="",
            ticker=None,
            indicators=True,
            slippage=0.0001,
            leverage=1,
            fees=0.005/100,
            capital=20000,
            save_results=True,
            save_path=os.getcwd(),
            plot_results=True)

```
### Data source ###
The user has many options to configure the bactkester. On the first place, the data can be pulled from Yahoo Finance via [pandas_datareader](https://pandas-datareader.readthedocs.io/en/latest/); or it can be pulled from a local file.
#### **From Yahoo Finance** ####
In the first case, ```sym``` and ```file_path``` can be left as they are, while the ```ticker``` needs to be filled with the security symbol (according to the symbols Yahoo Finance uses). The ```dateformat``` of Yahoo Finance is the default format.
```python
    super().__init__(self,ticker="AAPL")

```
Simple, right?

#### **From a local CSV file** ####
If it is the second case, the initialization varies a little and ```sym```, ```file_path``` and ```dateformat``` parameters need to be specified, whilst ```ticker``` can be left as it is. It is important that the dateformat is specified correctly, otherwise an error will be raised by the datetime module.
```python
    super().__init__(self, 
            sym="SP500",
            dateformat="%Y-%m-%d %H:%M:%S",
            file_path="yourCSVfiledirectory.csv")
```
### Timeperiod ###

#### **All the data available** ####
If the aim of the user is to backtest the strategy for all the points in the data, the parameters ```initial_time``` and ```final_time``` should not be modified, they are already set as the very beginning and the last point respectively.

#### **Specific timeframes** ####

If the user wants to backtest certain scenarios, the ```initial_time``` and ```final_time``` need to be modified accordingly, always following the format specified in ```dateformat```.

```python
    super().__init__(self, 
            sym="GOLD",
            file_path="yourCSVfiledirectory.csv"),
            initial_time="01/01/2015 00:00:00",
            final_time="01/01/2020 23:55:00",
            dateformat="%Y-%m-%d %H:%M:%S",
            )

```

### Extras ###

#### **Technical Indicators** ####
The technical indicators that come with the alphabacktest module are the SMA, EMA, RSI, Bollinger Bands and MACD. However if anyone would want to change it, you can also redefine the ```indicators()``` method.
```python
from bcktclasses_cy import Backtest  

class mStrategy(Backtest):
    def __init__(self):
        super().__init__(ticker="AMZN")

    def strategy(self,_open, close, high, low, vol, dtime):
        
        ''' Your strategy'''

    def indicators(self, close):
        from talib import RSI, BBANDS, MACD, EMA, SMA #....
        '''Define your indicators'''

if __name__ == '__main__':
    mStrategy()
```


Otherwise, if the user does not wish to use any of them, the indicators calculation can be desactivated by setting ```indicators=False``` in the ```super().__init()``` declaration.

#### **Trading environment conditions** ####

In order to simulate a real brokerage activity, the orders are not placed and executed right away. Instead, they first pass through a check and are placed in the following period. This adds more realism and settles the real-pessimistic scenario.

Moreover, the parameters that are required by the engine to reproduce this behaviour are set by default but the user can change them and adapt it to what their broker sets as conditions. The attributes are the following.

- ```slippage```. This parameter refers to the difference between the price at which the order is placed and the price at which the trade is executed [CFI](https://corporatefinanceinstitute.com/resources/knowledge/trading-investing/slippage/). Although the slippage can really be zero, positive or negative, in alphabacktest it is considered to always be playing against the interests of the trader.


- ```leverage```. [Investopedia](https://www.investopedia.com/terms/l/leverage.asp) describes the leverage as found in the following quote.
  >Leverage refers to the use of debt (borrowed funds) to amplify returns from an investment or project.
    
    In this module the leverage is a multiplier that refers to the *n* times your capital is increased by the debt. Leverage can range from 1 (meaning no debt) up to 400 depending on the financial product. (Again, thanks [Investopedia](https://www.investopedia.com/terms/m/maximum-leverage.asp)). Nonetheless, this number is usually set by your broker.
            
- ```fees```. This refers to the commission the broker is charging per unit of currency, meaning that it will be dependent on the amount the trader allocates to the trade. 

-```capital```. Total initial amount of liquidity the account is provided with. It is not considered to be in any specific currency; just the currency the security is traded with. Therefore, the backtest will not consider fluctuations due to the FX markets evolution.

#### **Results treatment** ####
The default configuration is set to save the results in csv files inside a folder the engine creates in the cwd and it runs a [Dash](https://dash.plotly.com) app where the results are plotted and presented. In case the user wanted to desactivate any of this features, the initialisation allows it. Setting ```save_results``` or ```plot_results``` (bool) as ```False```. Moreover, if the user wanted to change the directory where the results are stored, ```save_path``` (str) is the parameter to customize.

Example: 

```python
    super().__init__(self, 
            sym="",
            initial_time="first",
            final_time="last",
            dateformat="%Y-%m-%d",
            file_path="",
            ticker=None,
            indicators=True,
            slippage=0.0001,
            leverage=1,
            fees=0.005/100,
            capital=20000,
            save_results=True,
            save_path="your/preferred/directory",
            plot_results=False)

```

### **Class attributes** ###
The attributes of the inherited class are the following.


- ```self.user_positions```. Pandas DataFrame containing the history of all positions

<!---
Add a table with an example of positions dataframe
-->
- ```self.user_portfolio```. Pandas DataFrame with the representation of the assets in the user's portfolio and the total value of their wallet.
<!---
Add a table with an example of positions dataframe
-->
- ```self.trades```. Pandas DataFrame with the information on the executed trades
<!---
Add a table with an example of positions dataframe
-->
- ```self.orders```. Pandas DataFrame with the information of all orders either they are placed or not.
<!---
Add a table with an example of positions dataframe
-->

### **Class methods** ###

The methods of the inherited class are the following ones.

- ```self.long_order(security, amount, dtime, price)```. Sends a long (buy) order to the broker. The parameters are:
    - **security**: str. Name of the security to be traded, it is a must for the engine to account the traded asset.
    - **amount**: int. Quantity of contracts the order aims at. The minimum quantity is 1 and only whole (integer) numbers are accepted.
    - **dtime**: str. Time at which the long order is placed in the specified ```dateformat```.
    - **price**: float. Price at which the order is aimed. This price will not have any influence, but is useful for further analysis on the results of one's trades.
  
- ```self.short_order(security, amount, dtime, price)```. Sends a short (sell) order to the broker. The parameters are:
  - **security**: str. Name of the security to be traded, it is a must for the engine to account the traded asset.
  - **amount**: int. Quantity of contracts the order aims at. The minimum quantity is 1 and only whole (integer) numbers are accepted.
  - **dtime**: str. Time at which the short order is placed in the specified ```dateformat```.
  - **price**: float. Price at which the order is aimed. This price will not have any influence, but is useful for further analysis on the results of one's trades.
  
- ```self.closing_order(p_id, dtime, double price)```. Sends a closing order to the broker. The parameters are:
  - **pID**: str. This represents the position ID, which is generated randomly once a position starts after the trade is executed. It is placed at the Position DataFrame index and allows the selection of a particular position.
  - **dtime**: str. Time at which the closing order is placed in the specified ```dateformat```.
  - **price**: float. Price at which the order is aimed. This price will not have any influence, but is useful for further analysis on the results of one's trades.


- ```self.has_positions()```. Returns a bool referring to the possession of an open contract. Returns ```True``` if there are open contracts and ```False``` if there is no open position. No parameters taken.


- ```self.get_positions(security,_open=True)```. Returns a pandas DataFrame with the positions related to the specified security. The parameters are:
  - **security**: str. Name of the security of the positions.
  - **_open**: bool. Refers to the state of the positions to be returned. If the method is called with ```_open=True```, the positions that will be returned are the currently open posigions; whilst if it is ```_open=False```, the method will return all positions regardless their state.


- ```self.get_long_positions(security,_open=True)```. Returns a pandas Dataframe with only long positions. The parameters are:
  - **security**: str. Name of the security of the positions.
  - **_open**: bool. Refers to the state of the positions to be returned. If the method is called with ```_open=True```, the positions that will be returned are the currently open posigions; whilst if it is ```_open=False```, the method will return all positions regardless their state.

- ```self.get_short_positions(security,_open=True)```. Returns a pandas Dataframe with only short positions. The parameters are:
  - **security**: str. Name of the security of the positions.
  - **_open**: bool. Refers to the state of the positions to be returned. If the method is called with ```_open=True```, the positions that will be returned are the currently open posigions; whilst if it is ```_open=False```, the method will return all positions regardless their state.



Features
--------
TO DO: 
- Multiple assets (threading)
- Improve resulting dash app

Credits
-------

This package was created with Cookiecutter_ and the `audreyr/cookiecutter-pypackage`_ project template.

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage
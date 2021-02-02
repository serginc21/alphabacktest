# alphabacktest #
[![PyPI version](https://badge.fury.io/py/alphabacktest.svg)](https://badge.fury.io/py/alphabacktest)
[![Build Status](https://travis-ci.com/serginc21/alphabacktest.svg?branch=main)](https://travis-ci.com/serginc21/alphabacktest)
[![Coverage Status](https://coveralls.io/repos/github/serginc21/alphabacktest/badge.svg?branch=main)](https://coveralls.io/github/serginc21/alphabacktest?branch=main)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/alphabacktest?style=plastic)
![PyPI - Wheel](https://img.shields.io/pypi/wheel/alphabacktest)
[![Documentation Status](https://readthedocs.org/projects/alphabacktest/badge/?version=latest)](https://alphabacktest.readthedocs.io/en/latest/?badge=latest)
-------
> **DISCLAIMER: The results this backtesting software might produce may not be accurate, reliable or suppose any evidence ensuring the profitability of an algorithmic trading strategy. The results are indicative and might not be appropiate for trading purposes. Therefore, the creator does not bear any responsibility for any losses anyone might incur as a result of using this software.**
> 
> **Please, be fully informed about the risks and costs associated with trading the financial markets, as it is one of the riskiest investment forms possible.**


## Description ##

alphabacktest is a library that aims at bringing algorithmic trading to all Pyhton programmers via a very simple set of methods that allow backtesting any trading strategy anyone can come up with, allowing external functions or modules.

You can find below an example of the structure to use when working with alphabacktest. The module is designed to be inherited in a new class created by the user and call the methods within the class. ```Backtest()``` has the engine to run the backtest chronologically and calls ```strategy()``` at each point in the data. The variables passed on to the function are ```list``` types with the previous quotes at each point for all the prices (high,close...) and volumes; except for ```dtime``` which is a string representing the current data point.

```python
from alphabacktest import Backtest  

class mStrategy(Backtest):
    ''' Always call super().__init__() '''
    def __init__(self):
        super().__init__(ticker="AMZN")

    ''' You can choose the parameters name'''
    def strategy(self,_open, close, high, low, vol, dtime):
        ''' Fill in your strategy '''
        if not self.has_positions():
            q = int(self.free_balance / close[-1])
            self.long_order(security=self.symbol, amount=q, dtime=dtime, price=close[-1])

if __name__ == '__main__':
    mStrategy()      
```
As seen, the usage is pretty straightforward, and does not require a huge effort for the user to import and/or work with it, being a smooth process and giving freedom to apply any strategy, from those based on technical indicators to AI, going through many different tools.

Regarding the data source (explained at Usage), getting the proper data is sometimes rather difficult, especially when one is looking for tight timeframes (1m,5m,15m...). This data is not usually free, so this module gives the chance to either get the data from Yahoo Finance or from a csv file that the user can have in their local memory from a purchase or own harvest. 



## Installation ##

You can find all releases in [PyPI](https://pypi.org/project/alphabacktest/).

```$ pip install alphabacktest```


### Requirements ###

- Python 3.6+

### Dependencies ###

As some of the features provided by the module are meant to be optional, **the installation of alphabacktest does not imply the collection** of TA-lib nor dash. Therefore, the package comes without these modules, which need to be installed by the user.

- **TA-lib**. As there are sometimes difficulties when installing this module depending on the OS and IDE configuration, there is an option for the backtesting engine not to calculate any technical indicator (as all are based on TA-lib), so in that case you don't necessarily need to have it installed. In case you want to enable the calculation of technical indicators, you will indeed need the module you can find [here](https://github.com/mrjbq7/ta-lib). 
- **Dash**. alphabacktest uses dash to plot and display the results. However, this option can also be desactivated. In case you do want it, you can find it [here](https://dash.plotly.com/installation). 



## Usage ## 

The ```super().__init__()``` is highly important as it defines exactly the settings of the backtest. It is customisable to an extent and allows multiple features to be desactivated or included.

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
In the first place, the data can be pulled from Yahoo Finance via [pandas_datareader](https://pandas-datareader.readthedocs.io/en/latest/), or it can be imported from a local file.
#### **From Yahoo Finance** ####
In the first case, ```sym``` and ```file_path``` need to be left as they are, while the ```ticker``` needs to be filled with the security symbol (according to the symbols Yahoo Finance uses). The ```dateformat``` of Yahoo Finance is the default format.
```python
    super().__init__(self,ticker="AAPL")
```

#### **From a local CSV file** ####
If it is the second case, the initialization varies a little and ```sym```, ```file_path``` and ```dateformat``` parameters need to be specified, and **do not** specify  ```ticker```. It is important that the dateformat is specified correctly, otherwise an error will be raised by the datetime module.
```python
    super().__init__(self, 
            sym="SP500",
            dateformat="%Y-%m-%d %H:%M:%S",
            file_path="yourCSVfiledirectory.csv")
```
However, the requirements for the file are very tight. The engine imports the data and assigns "Datetime","Open","High","Low","Close","Volume" values to the columns in that order. The format in Datetime column will be kept as a string and set as index whilst the format for Open-Volume will be converted to float. At last, the separator needs to be ','. If the format of your csv file is not this one, you can either transform it externally or provide your own data (which is recommended).

#### **From a given DataFrame** ####
The data format must be the same as the described above, meaning "Datetime" (str),"Open" (float),"High" (float),"Low" (float),"Close" (float),"Volume" (float) [**IN THIS ORDER**]. Datetime must be the dataframe's index.

Example:
```python
data = pd.read_csv('csv/file/path.csv')
''' Data treatment'''
data= data.set_index("Datetime")
data.loc[:,'Open':'Close'] = data.loc[:,'Open':'Close'].astype(float)
class myStrategy(Backtest):
    def __init__(self,data):
        super().__init__(sym='BTCUSD',data=data,initial_time="04/01/2020 01:00:00",dateformat="%d/%m/%Y %H:%M:%S")
myStrategy(data)
```

Data example:
```python
                        Open     High      Low    Close  Volume
Datetime                                                       
01/04/2007 17:15:00  3746.71  3850.91  3707.23  3843.52   4324200990.0
01/04/2007 17:30:00  3849.22  3947.98  3817.41  3943.41   5244856835.0
01/04/2007 17:45:00  3931.05  3935.69  3826.22  3836.74   4530215218.0
01/04/2007 18:00:00  3832.04  3865.93  3783.85  3857.72   4847965467.0
01/04/2007 18:15:00  3851.97  3904.90  4093.30  3836.90   5137609823.0
...                      ...      ...      ...      ...     ...

[m rows x n columns]

```
### Timeperiod ###

#### **All the data available** ####
If the aim of the user is to backtest the strategy for all the points in the data, the parameters ```initial_time``` and ```final_time``` should not be modified, they are already set as the very beginning and the last point respectively.


#### **Specific timeframes** ####

If the user wants to backtest certain scenarios, the ```initial_time``` and ```final_time``` need to be modified accordingly, always following the format specified in ```dateformat```.

```python
    super().__init__(self, 
            sym="GOLD",
            data=your_data,
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

- ```slippage```. This parameter refers to the difference between the price at which the order is placed and the price at which the trade is executed ([CFI](https://corporatefinanceinstitute.com/resources/knowledge/trading-investing/slippage/)). Although the slippage can really be zero, positive or negative, in alphabacktest it is considered to always be playing against the interests of the trader.


- ```leverage```. [Investopedia](https://www.investopedia.com/terms/l/leverage.asp) describes the leverage as follows.
  >Leverage refers to the use of debt (borrowed funds) to amplify returns from an investment or project.
    
    In this module the leverage is a multiplier that refers to the *n* times your capital is increased by taking debt. Leverage can range from 1 (meaning no debt) up to 400 depending on the financial product. (Again, thanks [Investopedia](https://www.investopedia.com/terms/m/maximum-leverage.asp)). Nonetheless, this number is usually set by your broker.
            
- ```fees```. This refers to the commissions the broker is charging per unit of capital invested, meaning that it will be dependent on the amount the trader allocates to the trade. 

- ```capital```. Total initial amount of liquidity the account is provided with. It is not considered to be in any specific currency; just the currency the security is traded with. Therefore, the backtest will not consider fluctuations due to the FX markets evolution.

#### **Results treatment** ####
The default configuration is set to save the results in csv files inside a folder named ```backtest_results``` the engine creates in the cwd and it runs a [Dash](https://dash.plotly.com) app where the results are plotted and the statistics presented. In case the user wanted to desactivate any of this features, the initialisation allows it by setting ```save_results``` or ```plot_results``` (bool) as ```False```. Moreover, if the user wanted to change the directory where the results are stored, ```save_path``` (str) is the parameter to customize.

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


- ```self.user_positions``` Pandas DataFrame containing the open positions.

Example:
```
        Security       OPrice                ODate CPrice CDate Amount       PNL Performance
btoHxGN    SP500  3653.884575  30/11/2020 20:30:00      -     -    -20  4.037615    0.110502
```


- ```self.closed_positions``` Pandas DataFrame containing the history of the closed positions.

Example:
```
        Security       OPrice                ODate   CPrice                CDate Amount         PNL  Performance
l7h7eRx    SP500  3517.898175  12/10/2020 10:30:00  3482.75  14/10/2020 11:00:00    -20  699.445602    19.882486
eO9fL5Q    SP500  3444.844450  15/10/2020 04:00:00  3476.75  15/10/2020 14:30:00     20  634.666156    18.423652
sIWnkka    SP500  3503.649600  16/10/2020 09:45:00  3473.50  16/10/2020 15:00:00    -20  599.488350    17.110397
XihBLba    SP500  3423.092275  19/10/2020 14:00:00  3450.00  20/10/2020 05:30:00     20  534.731408    15.621297
Dm2U5jQ    SP500  3418.591825  26/10/2020 02:45:00  3396.25  26/10/2020 10:00:00     20 -450.255092   -13.170777
EAtb5UL    SP500  3388.088775  26/10/2020 10:30:00  3361.75  26/10/2020 12:30:00     20 -530.163589   -15.647866
3ua0S1x    SP500  3386.088575  26/10/2020 13:30:00  3360.00  27/10/2020 17:15:00     20 -525.157589   -15.509269
...
```

- ```self.user_portfolio``` Pandas DataFrame with the representation of the assets in the user's portfolio and the total value of their wallet.

Example:
```
    Security Amount    Value
0    SP500    -20 -73070.0
```

- ```self.trades``` Pandas DataFrame with the information on the executed trades.

Example:
```
       Security           Type             Datetime    Price Amount
lfdXIFo    SP500           Sell  12/10/2020 10:15:00  3516.00      1
6sp7cHv    SP500  Close#l7h7eRx  14/10/2020 10:45:00  3499.25    -20
JXKYklr    SP500            Buy  15/10/2020 03:45:00  3444.25      1
32Bc0fR    SP500  Close#eO9fL5Q  15/10/2020 14:15:00  3470.00     20
oP3w0Ha    SP500           Sell  16/10/2020 09:30:00  3507.00      1
XPTZCZE    SP500  Close#sIWnkka  16/10/2020 14:45:00  3484.00    -20
izB77xS    SP500            Buy  19/10/2020 13:45:00  3432.25      1
4qGx5Ld    SP500  Close#XihBLba  20/10/2020 05:15:00  3443.50     20
...
```

- ```self.orders``` Pandas DataFrame with the information of all orders either if they are placed or not.

Example:
```
        Security           Type             Datetime    Price Amount     Status
DsN3JXP    SP500           Sell  12/10/2020 10:15:00  3516.00      1   Executed
Ztfajo7    SP500  Close#l7h7eRx  14/10/2020 10:45:00  3499.25    -20   Executed
VOiZwri    SP500            Buy  15/10/2020 03:45:00  3444.25      1   Executed
2hUedWm    SP500  Close#eO9fL5Q  15/10/2020 14:15:00  3470.00     20   Executed
O2j9Sjf    SP500           Sell  16/10/2020 09:30:00  3507.00      1   Executed
lStGqRL    SP500  Close#sIWnkka  16/10/2020 14:45:00  3484.00    -20   Executed
9lcGAFG    SP500            Buy  19/10/2020 13:45:00  3432.25      1   Executed
X86B0s7    SP500  Close#XihBLba  20/10/2020 05:15:00  3443.50     20   Executed
...
```
<!---
Add a table with an example of positions dataframe
-->

### **Class methods** ###

The methods of the inherited class are the following ones.

- ```self.long_order(security, amount, dtime, price)``` Sends a long (buy) order to the broker. The parameters are:
    - **security**: str. Name of the security to be traded, it is a must for the engine to account the traded asset.
    - **amount**: int. Quantity of contracts the order aims at. The minimum quantity is 1 and only whole (integer) numbers are accepted.
    - **dtime**: str. Time at which the long order is placed in the specified ```dateformat```.
    - **price**: float. Price at which the order is aimed. This price will not have any influence, but is useful for further analysis on the results of one's trades.
  
- ```self.short_order(security, amount, dtime, price)``` Sends a short (sell) order to the broker. The parameters are:
  - **security**: str. Name of the security to be traded, it is a must for the engine to account the traded asset.
  - **amount**: int. Quantity of contracts the order aims at. The minimum quantity is 1 and only whole (integer) numbers are accepted.
  - **dtime**: str. Time at which the short order is placed in the specified ```dateformat```.
  - **price**: float. Price at which the order is aimed. This price will not have any influence, but is useful for further analysis on the results of one's trades.
  
- ```self.closing_order(p_id, dtime, double price)``` Sends a closing order to the broker. The parameters are:
  - **pID**: str. This represents the position ID, which is generated randomly once a position starts after the trade is executed. It is placed at the Position DataFrame index and allows the selection of a particular position.
  - **dtime**: str. Time at which the closing order is placed in the specified ```dateformat```.
  - **price**: float. Price at which the order is aimed. This price will not have any influence, but is useful for further analysis on the results of one's trades.


- ```self.has_positions()``` Returns a bool referring to the possession of an open contract. Returns ```True``` if there are open contracts and ```False``` if there is no open position. No parameters taken.


- ```self.get_positions(security,_open=True)``` Returns a pandas DataFrame with the positions related to the specified security. The parameters are:
  - **security**: str. Name of the security of the positions.
  - **_open**: bool. Refers to the state of the positions to be returned. If the method is called with ```_open=True```, the positions that will be returned are the currently open posigions; whilst if it is ```_open=False```, the method will return all positions regardless of their state.


- ```self.get_long_positions(security,_open=True)``` Returns a pandas Dataframe with only long positions. The parameters are:
  - **security**: str. Name of the security of the positions.
  - **_open**: bool. Refers to the state of the positions to be returned. If the method is called with ```_open=True```, the positions that will be returned are the currently open posigions; whilst if it is ```_open=False```, the method will return all positions regardless their state.

- ```self.get_short_positions(security,_open=True)``` Returns a pandas Dataframe with only short positions. The parameters are:
  - **security**: str. Name of the security of the positions.
  - **_open**: bool. Refers to the state of the positions to be returned. If the method is called with ```_open=True```, the positions that will be returned are the currently open posigions; whilst if it is ```_open=False```, the method will return all positions regardless their state.



Results
--------
The results are obtained via csv files and a dash app summary of the strategy performance that will be running on the local server ```http://127.0.0.1:port/``` as the logs report. 

![](./img/dashappserver.png)


Features
--------
TO DO: 
- Multiple assets (threading)

Credits
-------

This package was created with Cookiecutter_ and the `audreyr/cookiecutter-pypackage`_ project template.

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage
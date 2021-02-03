import os, progressbar, threading, random, string
from datetime import datetime, timedelta
from time import time
import pandas as pd
import numpy as np


class Account():
    def __init__(self):
        self.symbol = ''
        self.__settings()
        self.free_balance = self._capital
        self.user_portfolio = pd.DataFrame(columns=['Security', 'Amount','Value'])
        self.total_value = self.free_balance + self.user_portfolio['Value'].sum() + self._on_hold
        self.costs_fees = 0
        

    def get_portfolio(self):
        return self.user_portfolio


    def _add_asset(self, security, amount, price):
        asset = pd.DataFrame([[security, amount, price*amount]], columns=['Security', 'Amount','Value'])
        self.user_portfolio=self.user_portfolio.append(asset, ignore_index=True)


    def __settings(self):
            self._capital = 20000
            self._fees_perc = 0
            self._slippage = 0.0003
            self._leverage = 20
            self._on_hold = 0
            self._on_hold_book = pd.DataFrame(columns=['Position ID','Amount','Value'])
            self._borrowed_money = 0
            self._borrowed_book = pd.DataFrame(columns=['Position ID','Value'])

    def _update_total_value(self):

        self.total_value = self.free_balance + self.user_portfolio['Value'].sum() + self._on_hold - self._borrowed_money


class Portfolio(Account):

    def __init__(self):
        super().__init__()
        self.user_positions = pd.DataFrame(columns=['Security','OPrice','ODate','CPrice','CDate','Amount','PNL','Performance'])
        self.closed_positions = pd.DataFrame(columns=['Security','OPrice','ODate','CPrice','CDate','Amount','PNL','Performance'])


    def get_positions(self, security, _open=True):
        if _open:
            return self.user_positions
        else:
            return pd.concat([self.closed_positions, self.user_positions])


    def get_long_positions(self, _open=True):

        if _open:
            return self.user_positions[self.user_positions['Amount']>0]
        else:
            return pd.concat([self.closed_positions[self.closed_positions['Amount']>0], self.user_positions[self.user_positions['Amount']>0]])

    def get_short_positions(self, _open=True):
        if _open:
            return self.user_positions[self.user_positions['Amount']<0]
        else:
            return pd.concat([self.closed_positions[self.closed_positions['Amount']<0], self.user_positions[self.user_positions['Amount']<0]])


    def has_positions(self):
        positions = self.get_positions(security=self.symbol,_open=True)
        if positions.shape[0] > 0:
            return True
        else:
            return False

    def _open_position(self, sec,  oprice, odate,  amount,  ptype='Buy'):

        pID = ''.join(random.choices(string.ascii_letters+string.digits,k=7))
        if ptype =='Buy':

            oprice = oprice *(1+self._slippage)
            bamount = amount * (self._leverage-1)
            tamount = bamount + amount
            newBorrowed = pd.Series(data=[pID, bamount*oprice],index=self._borrowed_book.columns)
            newBorrowed.name = ''.join(random.choices(string.ascii_letters+string.digits,k=7))
            self._borrowed_book = self._borrowed_book.append(newBorrowed)
            self._borrowed_money = self._borrowed_book['Value'].sum()

            self.user_positions.loc[pID,:] = [sec, oprice, odate, '-','-',tamount,-tamount*oprice*self._fees_perc, 0]
        else:
            
            oprice = oprice*(1-self._slippage)
            bamount = amount * (self._leverage-1)
            tamount = bamount + amount

            self._borrowed_book.loc[''.join(random.choices(string.ascii_letters+string.digits,k=7)),:] = [pID, bamount*oprice]
            self._borrowed_money = self._borrowed_book['Value'].sum()

            self.user_positions.loc[pID,:] = [sec, oprice, odate, '-','-',-tamount,-tamount*oprice*self._fees_perc, 0]

            ohID = ''.join(random.choices(string.ascii_letters+string.digits,k=7))

            self._on_hold_book.loc[ohID,:] = [pID, 2*tamount, 2*tamount*oprice]
            self._on_hold = self._on_hold_book['Value'].sum()

        self.free_balance -= (tamount * oprice * self._fees_perc + amount*oprice)
        self.costs_fees += abs(tamount * oprice * self._fees_perc)
        if sec in self.user_portfolio['Security'].values:

            self._update_assets_amount(oprice)
        else:
            if ptype == 'Buy':
                self._add_asset(sec,tamount, oprice)
            else:
                self._add_asset(sec,-tamount, oprice)



    def _close_position(self, position, dtime,  price):

        self._update_position(price)
        tamount= self.user_positions.loc[position, 'Amount']
        bmID = self._borrowed_book.index[self._borrowed_book['Position ID']==position].to_list()[0]
        if tamount > 0:
            self.user_positions.loc[position, 'CPrice'] = price
            self.user_positions.loc[position, 'CDate'] = dtime
            self.free_balance += (self.user_positions.loc[position, 'Amount']) * price - self._borrowed_book.loc[bmID,'Value']

        else:
            self.user_positions.loc[position, 'CPrice'] = price
            self.user_positions.loc[position, 'CDate'] = dtime
            ohID = self._on_hold_book.index[self._on_hold_book['Position ID']==position].to_list()[0]
            # print(f"GIVING BACK TO FREE BALANCE: USD {self.on_hold_book.loc[ohID,'Value']/2 - abs(self.user_positions.loc[position, 'Amount']*price)}")
            self.free_balance += self._on_hold_book.loc[ohID,'Value'] - abs(self.user_positions.loc[position, 'Amount']*price) - self._borrowed_book.loc[bmID,"Value"]
            self._on_hold_book = self._on_hold_book.drop(ohID,axis=0)
            self._on_hold = self._on_hold_book['Value'].sum()
        
        closedPosition = pd.Series(data=self.user_positions.loc[position,:],index=self.closed_positions.columns)
        closedPosition.name = position
        self.closed_positions = self.closed_positions.append(closedPosition)

        self.user_positions.drop(labels=[position],axis=0,inplace=True)
        self._borrowed_book = self._borrowed_book.drop(bmID,axis=0)
        self._borrowed_money =self._borrowed_book['Value'].sum()
        
        self.free_balance -= abs(tamount * price * self._fees_perc)
        self.costs_fees += abs(tamount * price * self._fees_perc)
        self._update_assets_amount(price)


    def _update_position(self, cprice):
        for pID in self.user_positions.index:
            oPrice = self.user_positions.loc[pID,'OPrice']
            pAmount = self.user_positions.loc[pID,'Amount']
            if pAmount >0:
                self.user_positions.loc[pID,'PNL'] = -abs(pAmount*oPrice*self._fees_perc) + (cprice - oPrice)*abs(pAmount)
                self.user_positions.loc[pID,'Performance'] = self.user_positions.loc[pID,'PNL'] / abs(oPrice * pAmount) * self._leverage *100
            else:
                self.user_positions.loc[pID,'PNL'] = -abs(pAmount*oPrice*self._fees_perc) + (oPrice - cprice)*abs(pAmount)
                self.user_positions.loc[pID,'Performance'] = self.user_positions.loc[pID,'PNL'] / abs(oPrice * pAmount)* self._leverage * 100


    def _update_assets_amount(self, price):

        for iAsset in self.user_portfolio.index:
            sec_positions = self.user_positions[self.user_positions['Security']==self.user_portfolio.loc[iAsset,'Security']]
            open_positions = sec_positions[sec_positions['CPrice']=='-']
            self.user_portfolio.loc[iAsset, 'Amount'] = open_positions['Amount'].sum()
            
            self._update_assets_value(price)


    def _update_assets_value(self, price):

        for iAsset in self.user_portfolio.index:
            self.user_portfolio.loc[iAsset, 'Value'] = self.user_portfolio.loc[iAsset, 'Amount'] * price




class Trader(Portfolio):
    def __init__(self):
        super().__init__()
        self.orders = pd.DataFrame(columns=['Security','Type', 'Datetime', 'Price', 'Amount', 'Status'])
        self.symbol = ''

    def long_order(self, security, amount, dtime, price):
        newOrder = pd.Series(data=[self.symbol, 'Buy',dtime, price ,amount, 'TBExecuted'],index=self.orders.columns)
        newOrder.name = ''.join(random.choices(string.ascii_letters+string.digits,k=7))
        self.orders = self.orders.append(newOrder)

    def short_order(self, security, amount, dtime, price):
        newOrder = pd.Series(data=[self.symbol, 'Sell',dtime, price ,amount, 'TBExecuted'],index=self.orders.columns)
        newOrder.name = ''.join(random.choices(string.ascii_letters+string.digits,k=7))
        self.orders = self.orders.append(newOrder)

    def closing_order(self, p_id, dtime, price):
        newOrder = pd.Series(data=[self.symbol, 'Close#'+p_id,dtime, price ,self.user_positions.loc[p_id, 'Amount'], 'TBExecuted'],index=self.orders.columns)
        newOrder.name = ''.join(random.choices(string.ascii_letters+string.digits,k=7))
        self.orders = self.orders.append(newOrder)



class Broker(Trader):
    def __init__(self):
        super().__init__()
        self.trades = pd.DataFrame(columns=['Security', 'Type', 'Datetime', 'Price', 'Amount'])

    def _order_execution(self, dtime, price):
        orderstba = self.orders[self.orders['Status']=='TBExecuted']
        for oID in orderstba.index:
            if 'Close#' in self.orders.loc[oID,'Type']:
                self.__execute_closing_order(dtime, price, oID)
            else:
                self.__execute_opening_order(dtime, price, oID)

        

    def __execute_opening_order(self, dtime, price, oID):
        if abs(self.orders.loc[oID,'Amount'] * price) > self.free_balance or self._on_hold/self._leverage > 1*self.total_value/2:
            self.orders.loc[oID,'Status'] = 'NotExecutedIF'
        elif self.orders.loc[oID,'Amount'] == 0:
            self.orders.loc[oID,'Status'] = 'NotExecutedN'
        else:
            if self.orders.loc[oID,'Type'] == 'Buy':
                self._open_position(self.symbol, price, dtime, self.orders.loc[oID,'Amount'])
                self.orders.loc[oID,'Status'] = ' Executed'
                newTrade = pd.Series(data=[self.orders.loc[oID,'Security'],self.orders.loc[oID,'Type'],self.orders.loc[oID,'Datetime'],self.orders.loc[oID,'Price'],self.orders.loc[oID,'Amount']],index=self.trades.columns)
                newTrade.name = ''.join(random.choices(string.ascii_letters+string.digits,k=7))
                self.trades = self.trades.append(newTrade)
            else:
                self._open_position(self.symbol, price, dtime, self.orders.loc[oID,'Amount'],ptype='Sell')
                self.orders.loc[oID,'Status'] = 'Executed'
                newTrade = pd.Series(data=[self.orders.loc[oID,'Security'],self.orders.loc[oID,'Type'],self.orders.loc[oID,'Datetime'],self.orders.loc[oID,'Price'],self.orders.loc[oID,'Amount']],index=self.trades.columns)
                newTrade.name = ''.join(random.choices(string.ascii_letters+string.digits,k=7))
                self.trades = self.trades.append(newTrade)

    def __execute_closing_order(self, dtime, price, oID):

        position = self.orders.loc[oID,'Type'].split('Close#')[1]
        if self.user_positions.loc[position,'CDate'] == '-':
            self._close_position(position, dtime, price)
            self.orders.loc[oID,'Status'] = 'Executed'
            tID = ''.join(random.choices(string.ascii_letters+string.digits,k=7))
            newTrade = pd.Series(data=[self.orders.loc[oID,'Security'],self.orders.loc[oID,'Type'],self.orders.loc[oID,'Datetime'],self.orders.loc[oID,'Price'],self.orders.loc[oID,'Amount']],index=self.trades.columns)
            newTrade.name = tID
            self.trades = self.trades.append(newTrade)
        else:
            self.orders.loc[oID,'Status'] = 'NotExecuted'



class Engine(Broker):

    def __init__(self, sym, initial_time, final_time, dateformat,file_path, ticker, indicators, slippage, leverage,fees,capital,save_results,save_path,plot_results,data):

        """Period can be 1m-59m, 1h-23h, 1d-29d, 1M-11M, Xy"""
        super().__init__()
        
        self._slippage = slippage
        self._leverage = leverage
        self._fees_perc = fees
        self._capital = capital
        if ticker is not None:
            self.symbol = ticker
        else:
            self.symbol = sym
        
        self.pnl_history=pd.DataFrame(columns=["PNL"])
        self.p_history=pd.DataFrame(columns=["Price"])
        if data is None:
            self._get_data(file_path,ticker)
        else:
            self.data=data

        self._backtest_settings(initial_time,final_time,dateformat)
        self.calculate_indicators = indicators
        self.indInit = True
        self.__driver(dateformat)
        if save_results:
            self._save_account_books(save_path,dateformat)
        if plot_results:
            
            self._plot_results(dateformat,save_path)
            
        
    def _backtest_settings(self,
                    initial_time, 
                    final_time, 
                    dateformat):

        converted = False
        try:
            if initial_time.lower() == "first":
                initial = 500
            else:
                initial=list(self.data.index).index(initial_time)
        except ValueError:
            print("Initial date does not match exactly, calculating nearest w7 datetime...")
            point = datetime.strptime(initial_time,dateformat)
            dataindex = self.data.index
            dataindex = pd.to_datetime(dataindex,dayfirst=True,format=dateformat)
            diffs = np.absolute(np.array(list(dataindex)) - point)
            value = diffs.min()
            initial = list(np.where(diffs==value)[0])[0]
            print(f"New origin: {dataindex[initial]}")
            converted = True
        try:
            if final_time.lower()=="last":
                final = -1
            else:
                final = list(self.data.index).index(final_time)
        except ValueError:
            print("Final date does not match exactly, calculating nearest w/ datetime...")
            point = datetime.strptime(final_time,dateformat)
            if not converted:
                dataindex = self.data.index[initial:]
                dataindex = pd.to_datetime(dataindex,dayfirst=True,format=dateformat)

            diffs = np.absolute(np.array(list(dataindex)) - point)
            value = diffs.min()
            final = list(np.where(diffs==value)[0])[0] + initial
            print(f"New final: {self.data.index[final]}")

        self.b_index = [initial, final]


    def __driver(self,dateformat):
        
        opening_price = self.data.iloc[self.b_index[0]-500:self.b_index[1],0].tolist()
        closing_price = self.data.iloc[self.b_index[0]-500:self.b_index[1],3].tolist()
        highest_price = self.data.iloc[self.b_index[0]-500:self.b_index[1],1].tolist()
        lowest_price = self.data.iloc[self.b_index[0]-500:self.b_index[1],2].tolist()
        volume = self.data.iloc[self.b_index[0]-500:self.b_index[1],4].tolist()
        period_data = self.data.index[self.b_index[0]-500:self.b_index[1]]
        period = range(500,len(opening_price))
        
        for point, _ in zip(period,progressbar.progressbar(range(period_data.shape[0]))):
            dpoint = period_data[point]
            pnl = pd.Series(data=[round((self.total_value/self._capital-1)*100,2)],index=self.pnl_history.columns)
            pnl.name = dpoint
            self.pnl_history = self.pnl_history.append(pnl)
            p = pd.Series(data=[closing_price[point]],index=self.p_history.columns)
            p.name = dpoint
            self.p_history = self.p_history.append(p)
            if self.calculate_indicators:
                thread = threading.Thread(target=self.indicators,args=[closing_price[(point-500):point]])
                thread.start()
            if self.orders.shape[0] > 0:
                self._order_execution(period_data[point], opening_price[point])
            if self.user_positions.shape[0] > 0:
                self._update_position(closing_price[point])
            if self.user_portfolio.shape[0] > 0:
                self._update_assets_value(closing_price[point])
            if self.calculate_indicators:
                thread.join()   
            self.strategy(opening_price[:point],closing_price[:point], highest_price[:point], lowest_price[:point], volume[:point], period_data[point])
            self._update_total_value()
            if self.total_value < closing_price[point] and not self.has_positions:
                print("Wiped out")
                break


    def indicators(self, ind_data):

        from talib import RSI, BBANDS, MACD, EMA, SMA

        
        ind_data = np.array(ind_data)

        self.RSI = RSI(ind_data, timeperiod=14)
        self.UBB, self.MBB, self.LBB = BBANDS(ind_data, timeperiod=20, nbdevup= 2.5, nbdevdn=2.5, matype=0)
        self.MACD, self.MACD_SIGNAL, self.MACD_HIST = MACD(ind_data, fastperiod=12, slowperiod=26, signalperiod=9)
        self.EMA = EMA(ind_data, timeperiod=10)
        self.EMA = self.EMA[~np.isnan(self.EMA)]
        self.SMA = SMA(ind_data, timeperiod=100)
        self.SMA = self.SMA[~np.isnan(self.SMA)]
        


    def strategy(self, _open, close, high, low, vol, dtime):
        pass
        

    def _plot_results(self,dateformat,system_path):
        from ._dash_results import DashApp
        pd.options.plotting.backend = "plotly"
        DashApp(dateformat,system_path)



    def _get_data(self,file_path,ticker):
    
        if file_path != "":

            data = pd.read_csv(file_path,sep=',',header=None)
            data = data.rename(columns={0:'Datetime',2:'Open',3:'High',4:'Low',5:'Close',6:'Volume'})
            data = data.set_index('Datetime')

            data.loc[:,'Open':'Volume'] = data.loc[:,'Open':'Volume'].astype(float)

            self.data = data

        elif ticker is not None:
            import pandas_datareader as pdr
            data = pdr.get_data_yahoo(ticker,start="2007-01-01",
                                end=datetime.strftime(datetime.today(),"%Y-%m-%d"))
            data.index = data.index.strftime("%Y-%m-%d")
            self.data = data.iloc[:,:-1]


    def _save_account_books(self, save_path, dateformat):

        print('----- Saving...')
        path = save_path + '/backtest_results'
        try:
            files = os.listdir(path)
            for f in files:
                os.remove(path+'/'+f)
        except FileNotFoundError:
            os.mkdir(path)

        self.orders.to_csv(save_path+'/backtest_results/orders.csv',index_label="ID")
        self.trades.to_csv(save_path+'/backtest_results/trades.csv',index_label="ID")
        total_positions = pd.concat([self.closed_positions,self.user_positions])
        total_positions.to_csv(save_path+'/backtest_results/userpositions.csv',index_label="ID")
        self.user_portfolio.to_csv(save_path+'/backtest_results/userportfolio.csv',index=False)
        
        self.pnl_history["BDiff"]= (self.p_history['Price'] - self.p_history.iloc[0,0]) / self.p_history.iloc[0,0] * 100

        self.pnl_history.to_csv(save_path+'/backtest_results/pnls.csv',index_label='Datetime')
        _data = self.data.iloc[self.b_index[0]:self.b_index[1],:]
        _data.to_csv(save_path+'/backtest_results/prices.csv',index_label="Datetime")

        positions_stats = pd.DataFrame(columns=["PNLp","Duration"])

        for position in total_positions.index:
            if total_positions.loc[position,"CDate"] == "-":
                positions_stats.loc[position,"Duration"] = datetime.strptime(_data.index[-1],dateformat) - datetime.strptime(total_positions.loc[position,"ODate"],dateformat)
            else:
                positions_stats.loc[position,"Duration"] = datetime.strptime(total_positions.loc[position,"CDate"],dateformat) - datetime.strptime(total_positions.loc[position,"ODate"],dateformat)

        positions_stats["Duration"] = (positions_stats["Duration"]/np.timedelta64(1, 'm')).astype(int)
        positions_stats["PNLp"] = total_positions["Performance"]
        positions_stats.to_csv(save_path+'/backtest_results/positions_stats.csv')

        stats = pd.DataFrame(columns=['Parameter','Value'])

        stats.loc[0,:] = ['Number of trades',self.trades.shape[0]]
        stats.loc[1,:] = ['Number of closed positions',self.closed_positions.shape[0]]
        stats.loc[2,:] = ['Number of open positions',self.user_positions.shape[0]]
        stats.loc[3,:] = ['Best trade',round(total_positions["Performance"].max(),2)]
        stats.loc[4,:] = ['Worst trade',round(total_positions["Performance"].min(),2)]
        stats.loc[5,:] = ['Profitable trades(%)',round((self.closed_positions["Performance"]>0).sum()/self.closed_positions.shape[0]*100,2)]

        stats.loc[6,:] = ['Final PNL (%)',self.pnl_history.iloc[-1,0]]
        SR = self.pnl_history["PNL"].mean()/self.pnl_history["PNL"].std()
        stats.loc[7,:] = ['Sharpe Ratio',round(SR,2)]

        r_max = self.pnl_history["PNL"].cummax()
        if r_max.iloc[-1] == 0:
            mdd = round(self.pnl_history["PNL"].min(),2)
        else:
            bools = r_max != 0
            pdd = self.pnl_history["PNL"][bools]/r_max[bools] - 1
            pdd = pdd * r_max[bools]
            mdd =round(pdd.min(),2)
        

        stats.loc[8,:] = ['MDD (%)',mdd]
        perf = total_positions["Performance"].astype(float)
        GTPR = perf[perf>0].sum()/abs(perf[perf<0].sum())
        stats.loc[9,:] = ["Gain to Pain Ratio",round(GTPR,2)]
        if positions_stats["Duration"].shape[0] == 1:
            if positions_stats["Duration"].mean() > 1440:
                stats.loc[10,:] = ["Average position holding (d)",str(int(positions_stats["Duration"].mean()/1440))+"±0"]
            elif positions_stats["Duration"].mean() > 60:
                stats.loc[10,:] = ["Average position holding (h)",str(int(positions_stats["Duration"].mean()/60))+"±0"]
            else:
                stats.loc[10,:] = ["Average position holding (min)",str(int(positions_stats["Duration"].mean()))+"±0"]
        else:
            if positions_stats["Duration"].mean() > 1440:
                stats.loc[10,:] = ["Average position holding (d)",str(int(positions_stats["Duration"].mean()/1440))+"±"+str(int(positions_stats["Duration"].std()/1440))]
            elif positions_stats["Duration"].mean() > 60:
                stats.loc[10,:] = ["Average position holding (h)",str(int(positions_stats["Duration"].mean()/60))+"±"+str(int(positions_stats["Duration"].std()/60))]
            else:
                stats.loc[10,:] = ["Average position holding (min)",str(int(positions_stats["Duration"].mean()))+"±"+str(int(positions_stats["Duration"].std()))]

            
        stats.loc[11,:] = ["Average pnl (%)",str(round(positions_stats["PNLp"].mean(),2))+"±"+str(round(positions_stats["PNLp"].std(),2))]
        stats.loc[12,:] = ['Paid in fees', self.costs_fees]
        stats.to_csv(save_path+'/backtest_results/stats.csv',index=False)
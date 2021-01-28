import pandas as pd
import numpy as np
from datetime import datetime
import logging, os
import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)


class DashApp():
    def __init__(self,dateformat="%Y-%m-%d",system_path=os.getcwd()):

        
        self.treat_data(dateformat,system_path)
        self.treat_graphs(dateformat)
        self.app_manager()


        

    def treat_data(self,dateformat,system_path):
        ## Importing data
        self.positions_stats = pd.read_csv(system_path+'/backtest_results/positions_stats.csv',sep=',')
        self.positions = pd.read_csv(system_path+'/backtest_results/userpositions.csv',sep=',')# ,format="%d/%m/%y %H:%M:00"
        self.positions["PNL"] = self.positions["PNL"].astype(float).round(decimals=2)
        self.positions["Performance"] = self.positions["Performance"].astype(float).round(decimals=2)
        self.positions["OPrice"] = self.positions["OPrice"].astype(float).round(decimals=2)
        self.trades = pd.read_csv(system_path+'/backtest_results/trades.csv',sep=',')
        self.orders = pd.read_csv(system_path+'/backtest_results/orders.csv',sep=',')
        self.portfolio =pd.read_csv(system_path+'/backtest_results/userportfolio.csv',sep=',')
        self.portfolio["Value"] = self.portfolio["Value"].astype(float).round(decimals=2)
        self.pnls = pd.read_csv(system_path+'/backtest_results/pnls.csv',sep=',')
        self.prices = pd.read_csv(system_path+'/backtest_results/prices.csv',sep=',')
        self.pnls['Datetime'] = pd.to_datetime(self.pnls['Datetime'],format=dateformat)
        self.prices['Datetime'] = pd.to_datetime(self.prices['Datetime'],format=dateformat)
        self.stats = pd.read_csv(system_path+'/backtest_results/stats.csv',sep=',')



    ## Generating table function
    def generate_table(self,dataframe, max_rows=100):
        return html.Table(style={'font-size':'10pt','margin-top':'10px'},children=[
            html.Thead(
                html.Tr([html.Th(col) for col in dataframe.columns])
            ),
            html.Tbody([
                html.Tr([
                    html.Td(dataframe.iloc[i][col]) for col in dataframe.columns
                ]) for i in range(min(len(dataframe), max_rows))
            ])
        ])
    ## Generating table function 1 
    def generate_table_1(self,dataframe, max_rows=100):
        return html.Table(style={'font-size':'8pt','margin-top':'10px'},children=[
            html.Thead(
                html.Tr([html.Th(col) for col in dataframe.columns])
            ),
            html.Tbody([
                html.Tr([
                    html.Td(dataframe.iloc[i][col]) for col in dataframe.columns
                ]) for i in range(min(len(dataframe), max_rows))
            ])
        ])

    def treat_graphs(self,dateformat):

        ## Positions histograms
        self.pnlshistogram = go.Figure(data=[go.Histogram(x=self.positions_stats["PNLp"],histnorm='probability',xbins=dict(size=5))])
        self.durationhistogram = go.Figure(data=[go.Histogram(x=self.positions_stats["Duration"],histnorm='probability',xbins=dict(size=100))])
        self.durationhistogram.update_layout(bargap=0.1)
        self.pnlshistogram.update_layout(bargap=0.1)
        ## Performance Graph creation
        self.myfig = go.Figure(layout=go.Layout(height=500,width=850,margin=go.layout.Margin(l=0,r=0,b=0,t=20)))
        self.myfig.add_trace(go.Scatter(x=self.pnls['Datetime'],y=self.pnls['PNL'],name='PNL'))
        self.myfig.add_trace(go.Scatter(x=self.pnls['Datetime'],y=self.pnls['BPrice'],name='Benchmarked'))
        self.myfig.update_xaxes(rangeslider_visible=True,rangebreaks=[{ 'pattern': 'day of week', 'bounds':["sat", "sun"]}])
        self.myfig.update_layout(hovermode='x',showlegend=False)

        ## Candlestick Graph creation

        self.fig_candle = go.Figure(data=[go.Candlestick(x=self.prices['Datetime'],open=self.prices['Open'],high=self.prices['High'],low=self.prices['Low'],close=self.prices['Close'])],layout=go.Layout(height=500,width=850,margin=go.layout.Margin(l=0,r=0,b=0,t=20)))
        self.fig_candle.update_xaxes(rangebreaks=[{ 'pattern': 'day of week', 'bounds':["sat", "sun"]}])
        for position in self.positions.index:
            this_datetime = datetime.strptime(self.positions.loc[position,'ODate'],dateformat)
            if self.positions.loc[position,'Amount'] < 0 and self.positions.loc[position,"CPrice"] != '-':
                ccolor = 'red'
                y0 =float(self.positions.loc[position,"CPrice"])+20
                yf = float(self.positions.loc[position,"CPrice"])+70
            else:
                ccolor = 'green'
                y0 = float(self.positions.loc[position,"OPrice"])-20
                yf = float(self.positions.loc[position,"OPrice"])-70

            self.fig_candle.add_annotation(
                x = this_datetime,
                y = y0,
                ax = this_datetime,
                ay = yf,
                xref = 'x',
                yref = 'y',
                axref = 'x',
                ayref = 'y',
                text = '',
                showarrow = True,
                arrowhead = 3,
                arrowsize = 1.5,
                arrowwidth = 1.5,
                arrowcolor = ccolor
            )

            if self.positions.loc[position,'CDate'] != '-':
                if self.positions.loc[position,'Amount'] < 0:
                    y0 = float(self.positions.loc[position,"OPrice"])-20
                    yf = float(self.positions.loc[position,"OPrice"])-70
                else:
                    y0 = float(self.positions.loc[position,"CPrice"])+20
                    yf = float(self.positions.loc[position,"CPrice"])+70
                this_datetime = datetime.strptime(self.positions.loc[position,'CDate'],dateformat)
                self.fig_candle.add_annotation(
                    x = this_datetime,
                    y = y0,
                    ax = this_datetime,
                    ay = yf,
                    xref = 'x',
                    yref = 'y',
                    axref = 'x',
                    ayref = 'y',
                    text = '',
                    showarrow = True,
                    arrowhead = 3,
                    arrowsize = 1.5,
                    arrowwidth = 1.5,
                    arrowcolor = 'black'
                )

    def app_manager(self):

        self.app = dash.Dash(__name__,assets_url_path='assets/')

        self.app.layout = html.Div(children=[
            html.H1(children=["Backtesting results"]),
            html.Div(id="graphscontainer",lang="en",style={
                'margin':'50px',
                'font-size':'14pt',
                'min-height':'500px',
                'width':'1300px',
                'height': '600px',
            }
            ,children=[
                
                html.Div(children=[html.H4(children=["Graphs"],style={'margin-top':'0'}),
                    dcc.Tabs(style={'width':'500px'},children=[
                    dcc.Tab(label="Performance: benchmarked vs strategy",
                    children=[
                        dcc.Graph(
                            id='pnlvsbench',
                            figure=self.myfig,
                            className='pnlgraph'
                            

                    ),],disabled_style={'margin-top':'0','padding-top':'0'}),

                    dcc.Tab(label="Candlestick: O/C positions",
                    children=[
                        dcc.Graph(
                            id='prices',
                            figure=self.fig_candle,
                            className='pnlgraph'
                    ),
                    
                    ],disabled_style={'margin-top':'0','padding-top':'0'}),
                    dcc.Tab(label="Positions duration",
                    children=[
                        dcc.Graph(
                            id='durationhist',
                            figure=self.durationhistogram,
                            className='pnlshist'
                    ),
                    
                    ],disabled_style={'margin-top':'0','padding-top':'0'}),
                    dcc.Tab(label="Positions PNL",
                    children=[
                        dcc.Graph(
                            id='pnlshist',
                            figure=self.pnlshistogram,
                            className='pnlshist'
                    ),
                    
                    ],disabled_style={'margin-top':'0','padding-top':'0'})

                ]),],style={'float':'left','width':'70%','font-size':'10pt'}),
                
                
                html.Div(style={'float':'right','margin-top':'0'},children=[
                    html.H4(children='Final Portfolio', style={'textAlign':'center'}),
                    self.generate_table(self.portfolio)]),

                html.Div(style={'float':'right','margin-top':'30px'},children=[
                    html.H4(children='Statistics', style={'textAlign':'center'}),
                    self.generate_table(self.stats),]),


            ]),
            html.Div(
                style={'width':'1200px', 'margin-top':'100px'},
                children=[
                    html.Div(style={'textAlign':'center','clear':'both'},children=[
                        html.H4(children='Positions held',
                        style={'textAlign':'center'}),
                        self.generate_table(self.positions),
                    ]),

                    html.Div(style={'margin-top':'50px'},children=[
                        
                        html.Div(style={'float':'left','width':'50%'},children=[html.H4(children='Trades', style={'textAlign':'center','width':'100%'}), self.generate_table_1(self.trades),]),
                        html.Div(style={'float':'right','width':'50%'},children=[html.H4(children='Orders', style={'textAlign':'center','width':'100%','margin-left':'0'}), self.generate_table_1(self.orders),]),


                    ]),
                ]
            ),


        ])
        self.app.run_server(debug=False)


# DashApp()
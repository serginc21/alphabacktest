import pandas as pd
import numpy as np
from datetime import datetime
import logging, os
import dash
import dash_table
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
        
        if self.positions_stats['Duration'].mean() > 3000:
            self.positions_stats['Duration'] = self.positions_stats['Duration'] / 60 / 24
            self.duration_tag = 'Duration (d)'        
            self.duration_size = 5
        elif self.positions_stats['Duration'].mean() > 180:
            self.positions_stats['Duration'] = self.positions_stats['Duration'] / 60
            self.duration_size = 5
            self.duration_tag = 'Duration (h)'
        else:
            self.duration_tag = 'Duration (min)'
            self.duration_size = 60


        self.positions = pd.read_csv(system_path+'/backtest_results/userpositions.csv',sep=',')# ,format="%d/%m/%y %H:%M:00"
        self.positions["PNL"] = self.positions["PNL"].astype(float).round(decimals=2)
        self.positions["Performance"] = self.positions["Performance"].astype(float).round(decimals=2)
        self.positions["OPrice"] = self.positions["OPrice"].astype(float).round(decimals=2)
        self.positions = self.positions.rename(columns={'Performance':'PNL (%)'})
        self.trades = pd.read_csv(system_path+'/backtest_results/trades.csv',sep=',')
        self.orders = pd.read_csv(system_path+'/backtest_results/orders.csv',sep=',')
        self.portfolio =pd.read_csv(system_path+'/backtest_results/userportfolio.csv',sep=',')
        self.portfolio["Value"] = self.portfolio["Value"].astype(float).round(decimals=2)
        self.pnls = pd.read_csv(system_path+'/backtest_results/pnls.csv',sep=',')
        self.prices = pd.read_csv(system_path+'/backtest_results/prices.csv',sep=',')
        self.pnls['Datetime'] = pd.to_datetime(self.pnls['Datetime'],format=dateformat)
        self.prices['Datetime'] = pd.to_datetime(self.prices['Datetime'],format=dateformat)
        self.stats = pd.read_csv(system_path+'/backtest_results/stats.csv',sep=',')




    def treat_graphs(self,dateformat):

        ## Positions histograms
        self.pnlshistogram = go.Figure(data=[go.Histogram(x=self.positions_stats["PNLp"],histnorm='probability',xbins=dict(size=2),marker_color='#007fbf')])
        self.durationhistogram = go.Figure(data=[go.Histogram(x=self.positions_stats["Duration"],histnorm='probability',xbins=dict(size=self.duration_size),marker_color='#007fbf')])
        self.pnlshistogram.update_yaxes(title_text='Proportion',title_font=dict(color='white'),gridcolor='#444444',gridwidth=2)
        self.pnlshistogram.update_xaxes(title_text='PNL (%)',title_font=dict(color='white'))
        self.durationhistogram.update_yaxes(gridcolor='#444444',gridwidth=2,title_text='Proportion',title_font=dict(color='white'))
        self.durationhistogram.update_xaxes(title_text=self.duration_tag,title_font=dict(color='white'))
        self.durationhistogram.update_layout(bargap=0.1,paper_bgcolor='rgba(0,0,0,0)',plot_bgcolor='rgba(0,0,0,0)',xaxis=dict(tickfont=dict(color='white')),yaxis=dict(tickfont=dict(color='white')))
        self.pnlshistogram.update_layout(bargap=0.1,paper_bgcolor='rgba(0,0,0,0)',plot_bgcolor='rgba(0,0,0,0)',xaxis=dict(tickfont=dict(color='white')),yaxis=dict(tickfont=dict(color='white')))
        ## Performance Graph creation
        self.myfig = go.Figure(layout=go.Layout(height=600,width=1000,margin=go.layout.Margin(l=0,r=0,b=0,t=20)))
        self.myfig.add_trace(go.Scatter(x=self.pnls['Datetime'],y=self.pnls['PNL'],name='Strategy pnl',line=dict(color='#01796f')))
        self.myfig.add_trace(go.Scatter(x=self.pnls['Datetime'],y=self.pnls['BDiff'],name='Security pnl',line=dict(color='#bfc1c2')))
        self.myfig.update_xaxes(title_text='Time',title_font=dict(color='white'),rangeslider_visible=True,rangebreaks=[{ 'pattern': 'day of week', 'bounds':["sat", "sun"]}],gridcolor='#444444',gridwidth=2)
        self.myfig.update_yaxes(title_text='Profit/Loss (%)',gridcolor='#444444',gridwidth=2,title_font=dict(color='white'))
        self.myfig.update_layout(hovermode='x',showlegend=False,paper_bgcolor='rgba(0,0,0,0)',plot_bgcolor='#555555',xaxis=dict(tickfont=dict(color='white')),yaxis=dict(autorange=True, fixedrange=False,tickfont=dict(color='white')))

        ## Candlestick Graph creation

        self.fig_candle = go.Figure(data=[go.Candlestick(x=self.prices['Datetime'],open=self.prices['Open'],high=self.prices['High'],low=self.prices['Low'],close=self.prices['Close'])],layout=go.Layout(height=600,width=1000,margin=go.layout.Margin(l=0,r=0,b=0,t=20)))
        self.fig_candle.update_xaxes(rangebreaks=[{ 'pattern': 'day of week', 'bounds':["sat", "sun"]}],title_font=dict(color='white'),title_text='Time',gridcolor='#444444',gridwidth=2)
        self.fig_candle.update_yaxes(title_font=dict(color='white'),title_text='Price',gridcolor='#444444',gridwidth=2)
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
                self.fig_candle.update_layout(paper_bgcolor='rgba(0,0,0,0)',plot_bgcolor='#555555',xaxis=dict(tickfont=dict(color='white')),yaxis=dict(autorange=True,fixedrange=False,tickfont=dict(color='white')))

    def app_manager(self):
        self.app = dash.Dash(__name__,assets_url_path='assets/')

        self.app.layout = html.Div(style={}, children=[
            html.H1(style={'margin-top':'50px','margin-left':'50px'},children=["Backtesting results"]),
            html.Hr(className='mainline',style={'border-top':'2px solid #878683','width':'70%','margin-left':'30px','margin-top':'0'}),
            html.Div(id="graphscontainer",lang="en",style={'min-height':'700px','min-width':'1600px'}
            ,children=[
                
                html.Div(children=[html.H2(children=["Graphs"],style={'margin-top':'0','color':'#2069e0'}),
                    dcc.Tabs(style={'width':'900px','font-size':'9pt','padding':'0','margin':'0','height':'30px'},colors={'border':'white','background':'#444444','primary':'#444444'},children=[
                    dcc.Tab(label="Performance",
                    children=[
                        dcc.Graph(
                            id='pnlvsbench',
                            figure=self.myfig,
                            className='pnlgraph',
                            style={'background-color':'transparent','padding':'0','margin':'0','width':'40px','vertical-align':'text-top'}
                            

                    ),],style={'margin':'0','padding':'0','color':'white'}),

                    dcc.Tab(label="Candlestick",
                    children=[
                        dcc.Graph(
                            id='prices',
                            figure=self.fig_candle,
                            className='pnlgraph'
                    ),
                    
                    ],style={'margin':'0','padding':'0','color':'white'}),
                    dcc.Tab(label="Positions duration",
                    children=[
                        dcc.Graph(
                            id='durationhist',
                            figure=self.durationhistogram,
                            className='pnlshist'
                    ),
                    
                    ],style={'margin':'0','padding':'0','color':'white'}),
                    dcc.Tab(label="Positions pnl",
                    children=[
                        dcc.Graph(
                            id='pnlshist',
                            figure=self.pnlshistogram,
                            className='pnlshist'
                    ),
                    
                    ],style={'margin':'0','padding':'0','color':'white'})

                ]),],style={'float':'left','width':'65%','font-size':'10pt','margin-left':'5%'}),
                
                
                html.Div(style={'float':'right','margin-top':'0','font-size':'12pt','width':'25%','margin-right':'5%'},children=[
                    html.H3(children='Final Portfolio', style={'textAlign':'left','color':'#2069e0','margin':'0'}),
                    dash_table.DataTable(
                                id='portfolio_table',
                                columns=[{'name':i,'id':i} for i in self.portfolio.columns],
                                data = self.portfolio.to_dict('records'),
                                style_as_list_view=True,
                                page_size=10,
                                style_cell={
                                    'backgroundColor': '#444444',
                                    'color': 'white'
                                },
                                style_data={'font-family':'Helvetica'},
                                style_table={'width':'60%'},
                                style_header={'font-family':'Helvetica','font-weight':'bold'},
                            ),

                    html.H3(children='Statistics', style={'textAlign':'left','color':'#2069e0','margin':'50px 0 0 0'}),
                    dash_table.DataTable(
                                id='stats_table',
                                columns=[{'name':i,'id':i} for i in self.stats.columns],
                                data = self.stats.to_dict('records'),
                                style_as_list_view=True,
                                page_size=10,
                                style_cell={
                                    'backgroundColor': '#444444',
                                    'color': 'white'
                                },  
                                style_cell_conditional=[
                                    {
                                        'if': {'column_id': 'Parameter'},
                                        'textAlign': 'left'
                                    }],
                                style_data={'font-family':'Helvetica'},
                                style_table={'width':'60%','margin-top':'0'},
                                style_header={'font-family':'Helvetica','font-weight':'bold'},
                            )
                    
                    ]),


            ]),
            
            html.Div(
                style={'height':'900px','min-width':'1400px'},
                children=[
                        html.Div(style={'float':'left','width':'55%', 'margin-left':'5%','min-width':'750px'},children=[
                        html.H3(children='Positions held',
                        style={'textAlign':'left','color':'#2069e0','margin':'0'}),
                        html.Div(
                        dash_table.DataTable(
                                id='positions_table',
                                data = self.positions.to_dict('records'),
                                columns=[{'name':i,'id':i} for i in self.positions.columns],
                                style_as_list_view=True,
                                page_size=20,
                                style_cell={
                                    'backgroundColor': '#444444',
                                    'color': 'white'
                                },  
                                style_data={'font-family':'Helvetica','textAlign': 'center','font-size':'10.5pt'},
                                style_header={'font-family':'Helvetica','font-weight':'bold','textAlign': 'center'},
                                style_table={'width':'100%'}
                            ),style={'width':'700px'}),
                ],),

                    html.Div(style={'float':'right','width':'35%','margin-right':'5%','min-width':'300px'},children=[
                        
                        # html.Div(style={'float':'left','width':'50%'},children=[html.H4(children='Trades', style={'textAlign':'center','width':'100%'}), self.generate_table_1(self.trades),]),
                        html.Div(style={},children=[
                            html.H3(children='Trades', style={'textAlign':'left','color':'#2069e0','margin':'0'}), 
                            dash_table.DataTable(
                                id='trades_table',
                                columns=[{'name':i,'id':i} for i in self.trades.columns],
                                data = self.trades.to_dict('records'),
                                style_as_list_view=True,
                                page_size=10,
                                style_cell={
                                    'backgroundColor': '#444444',
                                    'color': 'white'
                                }, 
                                style_data={'font-family':'Helvetica','textAlign': 'left','font-size':'10.5pt'},
                                style_header={'font-family':'Helvetica','font-weight':'bold','textAlign': 'left'},
                                style_table={'width':'80%'},

                            ),]),

                            html.Div(style={},children=[
                            html.H3(children='Orders', style={'textAlign':'left','color':'#2069e0','margin':'20px 0 0 0'}), 
                            dash_table.DataTable(
                                id='orders_table',
                                columns=[{'name':i,'id':i} for i in self.orders.columns],
                                data = self.orders.to_dict('records'),
                                style_as_list_view=True,
                                page_size=10,
                                style_cell={
                                    'backgroundColor': '#444444',
                                    'color': 'white'
                                },
                                style_data={'font-family':'Helvetica','textAlign': 'left','font-size':'10.5pt'},
                                style_header={'font-family':'Helvetica','font-weight':'bold','textAlign': 'left'},
                                style_table={'width':'80%','margin-top':0},
                            ),]),


                    ]),
                ]
            )


        ])
        self.app.run_server(debug=False)

# DashApp(dateformat="%d/%m/%Y %H:%M:%S")
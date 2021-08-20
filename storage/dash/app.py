from dash import Dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output, State, MATCH
from datetime import datetime as dt
import datetime
import pandas as pd
import dash_daq as daq
import plotly.graph_objects as go

from flask import Flask

from backtesting import Backtest, Strategy
from backtesting.lib import crossover

from backtesting.test import SMA

import logging

server = Flask(__name__)

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = Dash(__name__, server=server, external_stylesheets=external_stylesheets)

bt_id_to_return = ['return', 'win_rate' , 'worst_trade', 'max_trade_duration', 'avg_trade_duration']
bt_var_to_return = ['Return [%]', 'Win Rate [%]' , 'Worst Trade [%]', 'Max. Trade Duration', 'Avg. Trade Duration']

app.layout = html.Div(
  children=[
    html.H1("Hubert's Backtesting Web Page"),
    html.Div(
      children=[
        html.Div(
          style={
            'width': '60%',
            'display': 'inline-block',
            'border': '3px solid #73AD21',
            'padding-left': '1%',
            'padding-right': '1%',
            'padding-bottom': '1%',
          },# 'text-align': 'justify'},
          children=[
            html.H4("Stocks to show:", style={'text-align':'center'}),
            dcc.Input(
              id="stock_symbols",
              value='TSLA AAPL',
              style={'width': '99%'},
              debounce=True,
              persistence=True
            ),
            html.H4("Amount to invest:", style={'text-align':'center'}),
            dcc.Slider(
              id="amount_invested",
              min=0,
              max=10**5,
              step=10**3,
              value=10**4,
              marks={
                10**4: '10k U$D',
                5*10**4: '50k U$D',
                10**5: '100k U$D'
              },
              persistence=True
            ),
            html.Div(
               style={'width': '30%','display': 'flex', 'border': '1px solid #73AD21', 'padding-left': '1%', 'float':'center', 'display': 'inline-block'},
               children=[
                  html.H5("Data Frequency:", style={'display': 'inline-block', 'text-align':'left', 'width':'100%'}),
                  dcc.RadioItems(
                    id="data_frequency",
                    options=[
                      {'label': 'Every 1 minute (last 7 days)', 'value': '1m'},
                      {'label': 'Every 1 hour (last 730 days)', 'value': '1h'},
                      {'label': 'Every 1 day (all historical data)', 'value': '1d'}
                    ],
                    value='1h',
                    persistence=True,
                    labelStyle={'display': 'inline-block', 'width':'100%'}
                  ),
               ]
            ),
            html.Div(
              style={'width': '25%','display': 'flex', 'padding-left': '1%', 'float':'center', 'display': 'inline-block'},
              children=[
                html.H5(["Start Date:",html.Br(),"End Date:"], style={'display': 'inline-block', 'text-align':'center', 'width':'40%'}),
                dcc.DatePickerRange(
                  id="invest_date",
                  start_date=dt.date(dt.today()-datetime.timedelta(730)),
                  end_date=dt.date(dt.today()),
                  style={'display': 'inline-block', 'text-align':'left', 'width':'60%'},
                  calendar_orientation='vertical',
                ),
              ]
            ),
            html.Div(
              style={'width': '40%','display': 'flex', 'padding-left': '1%', 'float':'center', 'display': 'inline-block'},
              children=[
                html.H5(
                  [
                    "1st Moving Average:",
                    html.Br(),
                    "2nd Moving Average:"
                  ],
                  style={'display': 'inline-block', 'text-align':'right', 'width':'45%', 'padding-left': '15%'}
                ),
                html.Div(
                  style={'width': '40%','display': 'flex', 'float':'center', 'display': 'inline-block'},
                  children=[
                    dcc.Input(id="N1",type="number", value=10, style={'display': 'inline-block', 'width':'50%'}),
                    html.Br(),
                    dcc.Input(id="N2",type="number", value=20, style={'display': 'inline-block', 'width':'50%'}),
                  ]
                ),
                
              ]
            )
            # html.Button("Update Graphs", id="update_graphs", n_clicks=0),
          ],
        ),
        html.Div(
          children=[
            html.H1("Data currently available:"),
            html.Ul(
              children=[
                html.Li(f"{stock} - [1m] [1h] [1d]") for stock in [
                "AMZN",
                "AAPL",
                "MSFT",
                "NVDA",
                "TSLA"
                ]
              ]
            )
          ],
          style={'width': '29%', 'display': 'inline-block', 'text-align': 'center', 'float': 'center'}#'text-align': 'justify'}
        )
      ]
    ),
    html.Div(id='container',children=[])
  ]
)

# def take_percentage_number(elem):
#   print(type(elem))
#   # print(elem['props']['children'])
#   try:
#     new_elem = float(elem.children[0].children[1].children.strip('%'))
#     return new_elem
#   except:
#     return 1

# @app.callback(
#   Output('main_container', 'children'),
#   [
#     Input('update_graphs', 'n_clicks'),
#     State('main_container', 'children'),
#   ]
# )
# def sort_graphs(n_clicks, div_children):
#   if n_clicks != None:
#     print(div_children.children[2])
#     div_children.children[2].sort(key=take_percentage_number)
#   return div_children


@app.callback(
  Output('container', 'children'),
  [
    Input('stock_symbols', 'value'),
  ]
)
def list_of_div_callback(stock_name: str) -> list:
  stocks = stock_name.upper().split()
  div_children = [
    html.Div(
      style={'width': '49%', 'text-align': 'center', 'display': 'inline-block', 'height':'600px'},
      children=[
        html.H4(stock, id={'type':'stock_name','index':stock}),
        html.Div(
          style={'width': '100%', 'text-align': 'center', 'display': 'inline-block', 'height':'200px'},
          children=[
            html.Div(
              style={'width': '49%', 'text-align': 'center', 'display': 'inline-block', 'height':'250px'},
              children=[
                html.H6('Without Backtest:'),
                html.P(id={'type':'profit_percentage','index':stock}),
                html.P(id={'type':'profit_amount','index':stock}),
                html.P(id={'type':'time_until_sell','index':stock}),
              ]
            ),
            html.Div(
              style={'width': '49%', 'text-align': 'center', 'display': 'inline-block', 'height':'250px'},
              children=[
                dcc.Graph(id={'type':'graph','index':stock}, style={'height':'300px'})
              ]
            ),
          ]
        ),
        html.Div(
          style={'width': '100%', 'text-align': 'center', 'display': 'inline-block', 'height':'200px'},
          children=[
            html.Div(
              style={'width': '49%', 'text-align': 'center', 'display': 'inline-block', 'height':'250px'},
              children=[
                html.H6('Backtest:'),
              ] + [html.P(id={'type':var,'index':stock}) for var in bt_id_to_return]
            ),
            html.Div(
              style={'width': '49%', 'text-align': 'center', 'display': 'inline-block', 'height':'200px'},
              children=[
                dcc.Graph(id={'type':'bt_graph','index':stock}, style={'height':'300px'})
              ]
            ),
          ]
        ),
        dcc.Store(id={'type':'data_storage','index':stock})
      ]
    )
    for stock in (stocks)
  ]
  return div_children

def SmaCross(N1, N2):
  class SmaCross(Strategy):
      n1 = N1
      n2 = N2

      def init(self):
          close = self.data.Close
          self.sma1 = self.I(SMA, close, self.n1)
          self.sma2 = self.I(SMA, close, self.n2)

      def next(self):
          if crossover(self.sma1, self.sma2):
              self.buy()
          elif crossover(self.sma2, self.sma1):
              self.sell()
  return SmaCross


@app.callback(
  [
    Output({'type': 'graph', 'index': MATCH}, 'figure'),
    Output({'type': 'profit_percentage', 'index': MATCH}, 'children'),
    Output({'type': 'profit_amount', 'index': MATCH}, 'children'),
    Output({'type': 'time_until_sell', 'index': MATCH}, 'children'),
    Output({'type': 'bt_graph', 'index': MATCH}, 'figure'),
  ] + [Output({'type': var, 'index': MATCH}, 'children') for var in bt_id_to_return],
  [
    Input({'type':'stock_name','index':MATCH},'children'),
    Input({'type':'data_storage','index':MATCH}, 'data'),
    Input('amount_invested', 'value'),
    Input('N1', 'value'),
    Input('N2', 'value'),
  ]
)
def div_content_callback(stock_name:str, df_json, amount_invested: int, N1: int, N2: int):
  df = pd.read_json(df_json, orient='split')
  # logging.error(df.info())
  col_to_consider = "Open"
  series_variation = df[col_to_consider]/df[col_to_consider][0]-1
  max_series = max(series_variation)
  profit_percentage = f"Profit Percentage: {max_series:.2%}"
  profit_amount = f"Profit Amount: {max_series*amount_invested}"
  time_until_sell = f"Time until sell: \
    {(series_variation[series_variation==max_series].index - min(series_variation.index)).tolist()[0]} \
    ({series_variation[series_variation==max_series].index.tolist()[0].date()}) \
    "
  
  bt = Backtest(df, SmaCross(N1, N2),
              cash=amount_invested, commission=.002,
              exclusive_orders=True)

  output = bt.run()

  figure = {
    'data':[
      {
        'x': series_variation.index.tolist(),
        'y': series_variation.tolist(),
        
      }
    ],
    'layout':{
      'yaxis':{
        'tickformat': ',.0%',
      }
    }
  }
  bt_return = f"Return: {output['Return [%]']/100:.2%}"
  bt_win_rate = f"Win Rate: {output['Win Rate [%]']/100:.2%}"
  bt_wrst_trd = f"Worst Trade: {output['Worst Trade [%]']/100:.2%}"
  bt_max_trd_duration = f"Max. Trade Duration: {output['Max. Trade Duration']}"
  bt_avg_trd_duration = f"Avg. Trade Duration: {output['Avg. Trade Duration']}"
  output._equity_curve["Equity"] = output._equity_curve["Equity"]/10000-1
  bt_figure = {
    'data':[
      {
        'x': output._equity_curve["Equity"].index.tolist(),
        'y': output._equity_curve["Equity"].tolist(),
      }
    ],
    'layout':{
      'yaxis':{
        'tickformat': ',.0%',
      }
    }
  }
  return figure, profit_percentage, profit_amount, time_until_sell, bt_figure, bt_return, bt_win_rate, bt_wrst_trd, bt_max_trd_duration, bt_avg_trd_duration

# def load_dataframe(stock_name: str, data_frequency:str) -> pd.DataFrame:
#   return pd.read_csv(f'5stocks-{data_frequency}.csv', parse_dates=True, index_col=0, header=[0, 1])[stock_name]

# def load_data(stock_name: str, date: str, data_frequency:str) -> pd.DataFrame:
#   return load_dataframe(stock_name, data_frequency).loc[
#     datetime.datetime.strptime(
#       f"{date}:-04:00", "%Y-%m-%d:%z"
#     ):datetime.datetime.now(
#       datetime.timezone(datetime.timedelta(hours=-4))
#     )]

@app.callback(
  Output({'type':'data_storage','index':MATCH}, 'data'),
  [
    Input({'type':'stock_name','index':MATCH},'children'),
    Input('invest_date', 'start_date'),
    Input('invest_date', 'end_date'),
    Input('data_frequency', 'value')
  ]
)
def get_data(stock_name:str, start_date:str, end_date:str, data_frequency:str):
  return pd.read_csv(f'5stocks-{data_frequency}.csv', parse_dates=True, index_col=0, header=[0, 1])[stock_name].dropna().loc[
    datetime.datetime.strptime(
      f"{start_date}:-04:00", "%Y-%m-%d:%z"
    ):datetime.datetime.strptime(
      f"{end_date}:-04:00", "%Y-%m-%d:%z"
    )].to_json(date_format='iso', orient='split')

if __name__ == '__main__':
    app.run_server(host='0.0.0.0',debug=True, port=8050)
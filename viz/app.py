"""
The dash_core_components package is deprecated. Please replace
`import dash_core_components as dcc` with `from dash import dcc`
  import dash_core_components as dcc
/home/thomas/Project/spark-nyc/viz/app.py:6: UserWarning: 
The dash_html_components package is deprecated. Please replace
`import dash_html_components as html` with `from dash import html`
  import dash_html_components as html
"""

import os
import pandas as pd
import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output
import plotly.express as px
import plotly.graph_objects as go

# PREP
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
LOGO_LINK = 'https://s3-us-west-1.amazonaws.com/plotly-tutorials/logo/new-branding/dash-logo-by-plotly-stripe.png'


# DATAFRAME
parent = os.getcwd()
file = 'output/nyc-green-2020/'
green_df = pd.read_parquet(os.path.join(parent, file))


# DASH APP
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

app.layout = html.Div(children=[
  html.Div(children=[
    html.Img(src=LOGO_LINK, style={'display':'inline-block', 'width':'200px','margin':'25px'}),
    html.H1('NYC Green Taxi', style={'display':'inline-block', 'margin':'25px'})
  ]),
  html.Div(
    children=[
      html.H2('Controls'),
      html.Br(),
      html.H3('Vendors'),
      dcc.Checklist(id='vendor-list',
      options=['Creative Mobile Technologies, LLC','VeriFone Inc.'],
      value=['Creative Mobile Technologies, LLC','VeriFone Inc'],
      inline=False,
      style={'width':'400px'}),
      html.Br(),
      html.H3('Payments'),
      dcc.Dropdown(id='payment-dd',
      options=['Credit card','Cash','No charge','Dispute','Unknown','Voided trip'],
      value=['Credit card','Cash'],
      multi=True,
      placeholder='Select payment types',
      style={'width':'300px'}),
      html.Br(),
      html.H3('Passengers'),
      dcc.RangeSlider(id='passenger-slider',
      min=1,
      max=4,
      step=1,
      value=[1,2]),
      html.Br(),
      html.H3('Pick Up Dates'),
      html.P('Please select with minimum range of 30 days.'),
      dcc.DatePickerRange(id='date-picker',
      start_date='2019-12-31',
      end_date='2020-12-31',
      min_date_allowed='2019-12-31',
      max_date_allowed='2020-12-31',
      minimum_nights=30,
      disabled=True)      
    ],
    style={'display':'inline-block','width':'350px', 'padding':'5px','border':'2px #3260a8 solid'}
  ),
  html.Div(children=[
    html.Div(dcc.Graph(id='dist-time')),
    html.Div(dcc.Graph(id='income-month')),
    html.Div(dcc.Graph(id='order-month')),
  ],
  style={'display':'inline-block'}),
  # html.Div(dcc.Graph(id='payment-bar')),
  
  html.Div(dcc.Graph(id='heatmap'))
])

# HELPER
def filter_dataframe(df, vendor, payment, passenger):
  dff = df[df['vendor'].isin(vendor)
           & df['payment'].isin(payment)
           & (df['passenger_count'] >= passenger[0]) 
           & (df['passenger_count'] <= passenger[1])]
  return dff

# CALLBACKS
@app.callback(
  Output(component_id='heatmap', component_property='figure'),
  Input(component_id='vendor-list', component_property='value'),
  Input(component_id='payment-dd', component_property='value'),
  Input(component_id='passenger-slider', component_property='value'),
  # Input(component_id='date-picker', component_property='value'),
)
def update_heatmap(vendor, payment, passenger):
  df = green_df.copy()

  df = filter_dataframe(df, vendor, payment, passenger)

  green_grouped = df \
    .groupby(['pu_day','pu_hour'])['pu_hour'] \
    .count() \
    .reset_index(name='pu_count')

  hour_day = green_grouped.pivot('pu_day','pu_hour','pu_count')
  hour_day = hour_day.reindex(['Mon','Tue','Wed','Thu','Fri','Sat','Sun'])
  fig = px.imshow(hour_day,
                labels=dict(x='Pick Up Hour', y='Pick Up Day', color='Number of Orders'),
                aspect='auto', 
                height=350, 
                title='Bussiest hour every day',
                color_continuous_scale='Aggrnyl')

  fig.update_xaxes(type='category')

  return fig

@app.callback(
  Output(component_id='income-month', component_property='figure'),
  Input(component_id='vendor-list', component_property='value'),
  Input(component_id='payment-dd', component_property='value'),
  Input(component_id='passenger-slider', component_property='value')
)
def update_income_month(vendor, payment, passenger):
  df = green_df.copy()

  df = filter_dataframe(df, vendor, payment, passenger)

  income_month = df \
    .groupby('pu_month')['total_amount'] \
    .agg('sum') \
    .reset_index(name='income_per_month')

  fig = px.line(data_frame=income_month, 
                title='Monthly Income',
                x='pu_month', 
                y='income_per_month',
                height=350)
  fig.update_xaxes(type='category')
              
  return fig

@app.callback(
  Output(component_id='order-month', component_property='figure'),
  Input(component_id='vendor-list', component_property='value'),
  Input(component_id='payment-dd', component_property='value'),
  Input(component_id='passenger-slider', component_property='value')
)
def update_order_month(vendor, payment, passenger):
  df = green_df.copy()

  df = filter_dataframe(df, vendor, payment, passenger)

  order_month = df \
    .groupby('pu_month')['pu_month'] \
    .agg('count') \
    .reset_index(name='order_per_month')

  fig = px.line(data_frame=order_month, 
                title='Monthly Orders',
                x='pu_month', 
                y='order_per_month',
                height=350)
  fig.update_xaxes(type='category')
              
  return fig

@app.callback(
  Output(component_id='dist-time', component_property='figure'),
  Input(component_id='vendor-list', component_property='value'),
  Input(component_id='payment-dd', component_property='value'),
  Input(component_id='passenger-slider', component_property='value')
)
def update_dist_time(vendor, payment, passenger):
  df = green_df.copy()

  df = filter_dataframe(df, vendor, payment, passenger)

  green_trim = df \
    .loc[:,['trip_duration_minute','trip_distance','fare_amount','vendor']]

  if len(green_trim) > 80000:  
    green_trim = green_trim.sample(80000)

  fig = px.scatter(data_frame=green_trim, 
                  x='trip_distance',
                  y='trip_duration_minute',
                  color='fare_amount',
                  opacity=0.6,
                  height=350)
              
  return fig

# RUN
if __name__ == '__main__':
    app.run_server(debug=True)
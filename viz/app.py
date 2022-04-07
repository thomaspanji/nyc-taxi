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
# import dash_core_components as dcc
# import dash_html_components as html
from dash import dcc
from dash import html
import plotly.express as px


parent = os.getcwd()
file = 'output/nyc-green-2020/'

green_taxi = pd.read_parquet(os.path.join(parent, file))

order_month = green_taxi.groupby('pu_month')['total_amount'].agg('sum').reset_index(name='income')

line_graph = px.line(
    data_frame=order_month, title='Monthly Income',
    x='pu_month', y='income'
)

app = dash.Dash(__name__)

app.layout = html.Div(children=[
    html.H1('Income Graph'),
    html.Div(dcc.Graph(id='income-month', figure=line_graph))
])

if __name__ == '__main__':
    app.run_server(debug=True)
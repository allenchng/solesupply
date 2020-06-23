import plotly.plotly as py
import plotly.graph_objs as go
import plotly.figure_factory as ff
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import os
import flask

import pandas as pd

# Step 1. Launch the application

server = flask.Flask(__name__)
app = dash.Dash(__name__, server=server)

server = app.server

# Step 2. Import the dataset

df = pd.read_csv("sample_data_for_dash.csv")
observed = df[(df['date'] >= '2019-05-31') & (df['date'] <= '2019-06-14')]
forecast_df = pd.read_csv("forecast2.csv", index_col=0)

# forecast_df.volume = forecast_df.volume.astype(int)
# forecast_df = forecast_df[(forecast_df['dates'] > '2019-05-31') & (forecast_df['dates'] < '2019-06-17')]
forecast_df.columns = ['Date', 'Projected Sales', 'Lower Interval', 'Upper Interval']
forecast_df = forecast_df[(forecast_df['Date'] >= '2019-05-31') & (forecast_df['Date'] <= '2019-06-14')]

df = df[(df['date'] > '2018-05-31') & (df['date'] < '2019-06-01')]

# range slider options
# df['date'] = pd.to_datetime(df.date)
# dates = ['2017-04-01', '2017-07-01', '2017-10-01', '2018-01-01',
#          '2018-04-01', '2018-07-01', '2018-10-01', '2019-01-01',
#          '2019-06-15']
# date_mark = {i : dates[i] for i in range(0, 9)}

# Step 3. Create a plotly figure

trace1 = go.Scatter(
    x=df.date,
    y=df['volume'],
    name = "Training",
    line = dict(color = '#000000'),
    opacity = 0.8)

trace2 = {
  "x": forecast_df['Date'],
  "y": forecast_df['Projected Sales'],
  "marker": {
    "color": "#3fae2b", 
    "line": {
      "color": "#3fae2b", 
      "width": 2
    }, 
    "size": 4
  }, 
  "mode": "lines+markers",
  "name": "Forecast", 
  "type": "scatter", 
}

trace3 = {
  "x": observed.date,
  "y": observed.volume, 
  "marker": {
    "color": "#969e99",
    "line": {
      "color": "#969e99 ",
      "width": 2
    }, 
    "size": 4
  }, 
  "mode": "lines",
  "name": "Observed", 
  "type": "scatter", 
}

trace4 = {
  "x": forecast_df['Date'],
  "y": forecast_df['Upper Interval'],
  "marker": {
    "color": "#afdeb9",
    "line": {
      "color": "#afdeb9 ",
      "width": 2
    },
    "size": 4
  },
  "mode": "lines",
  "name": "Upper interval",
  "type": "scatter",
}

trace5 = {
  "x": forecast_df['Date'],
  "y": forecast_df['Lower Interval'],
  "marker": {
    "color": "#afdeb9",
    "line": {
      "color": "#afdeb9",
      "width": 2
    },
    "size": 4
  },
  "mode": "lines",
  "fill": "tonexty",
  "name": "Lower interval",
  "type": "scatter",
}


# trace3 = go.Scatter(
#     x=observed.date,
#     y=observed['volume'],
#     name = "Observed",
#     line = dict(color = '#000080'),
#     opacity = 0.8)

colorscale = [[0, '#3fae2b'],[.5, '#ffffff'],[1, '#ffffff']]
table1 = ff.create_table(forecast_df, colorscale=colorscale)

for i in range(len(table1.layout.annotations)):
    table1.layout.annotations[i].font.size = 16

data = [trace1, trace4, trace5, trace3, trace2]

# layout = dict(
#     # title='Total Sneaker Sales',
#     xaxis=dict(
#         rangeselector=dict(
#             buttons=list([
#                 dict(count=1,
#                      label='1m',
#                      step='month',
#                      stepmode='backward'),
#                 dict(count=6,
#                      label='6m',
#                      step='month',
#                      stepmode='backward'),
#                 dict(step='all')
#             ])
#         ),
#         rangeslider=dict(),
#         type='date'
#     )
# )

layout = {
  "autosize": True, 
#   "height": 450, 
  "title": "Sneaker Transaction Timeseries: Bayesian Model Forecast", 
#   "width": 785.469, 
  "xaxis": {
    "autorange": True, 
    "title": "Date", 
  }, 
  "yaxis": {
    "title": "Number of Transactions", 
  }
}

fig = dict(data=data, layout=layout)

# Step 4. Create a Dash layout

app.layout = html.Div([
                html.Div([
                  html.Img(src='./static/SoleSupply-White.png',
                  style={
                    'height': '12%',
                    'width': '12%'
                  }),
                    # html.H1("SoleSupply"),
                    html.H3("A sneak peek into the future")
                         ],
                     style = {'padding' : '50px' ,
                              'backgroundColor' : '#3fae2b',
                              'font-family' : 'HelveticaNeue',
                              'color': 'white',
                              'text-align' : 'center'}),
                dcc.Graph(id='total_graph', 
                          figure=fig),
                # html.P([
                #     # html.Label("Time Period"),
                #     dcc.RangeSlider(id = 'slider',
                #                     marks = {i : dates[i] for i in range(0, 9)},
                #                     min = 0,
                #                     max = 8,
                #                     value = [1, 7])
                #         ], style = {'width' : '80%',
                #                     'color': '#3fae2b',
                #                     'fontSize' : '20px',
                #                     'padding-left' : '100px',
                #                     'display': 'inline-block',
                #                     'font-family' : 'HelveticaNeue'}),
                dcc.Graph(id='my-table', figure=table1)
])

# Step 5. Add callback functions
# @app.callback(Output('total_graph', 'figure'),
#              [Input('slider', 'value')])
# def update_figure(X):
#     df2 = df[(df.date > dates[X[0]]) & (df.date < dates[X[1]])]
#     trace = go.Scatter(x = df2.date, y = df2['volume'],
#                         name = 'Total',
#                         line = dict(width = 2,
#                                     color = 'rgb(63, 174, 43)'))
#     fig = go.Figure(data = [trace], layout = layout)
#     return fig

if __name__ == '__main__':
    app.run_server(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
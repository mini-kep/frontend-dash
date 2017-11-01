"""Controls and vizualisation for 'mini-kep' dataset using Dash/Plotly

Scenario:

1. when page is loaded there is one frequency and one indicator selected,
   one indicator shows on plot 
    
2. select frequency in radio buttons
  -> frequency selection affects list of indicators in drop-down menu 1 and 2
     (same list there)
  
3. select indicator 1 by name in drop-down menu 
  -> choosing name affects plot

4. select indicator 2 by name in drop-down menu 
  -> choosing name affects plot

"""
import os
from random import randint

import flask
import dash
from dash.dependencies import Input, Output
import dash_core_components as dcc
import dash_html_components as html

import requests
import urllib.parse


# Setup the app
# Make sure not to change this file name or the variable names below,
# the template is configured to execute 'server' on 'app.py'
server = flask.Flask(__name__)
server.secret_key = os.environ.get('secret_key', str(randint(0, 1000000)))
app = dash.Dash(__name__, server=server)


# NOT TODO: may be a class Data with 
# - Data.names() 
# - data.time_series(freq, name) 
# - frequencies()

# NOT TODO: frequencies can be imported from db API
#           see for example 
#           <https://minikep-db.herokuapp.com/api/datapoints?name=ABC&freq=z&format=json>
#
def frequencies():
    return [
        {'label': 'Annual', 'value': 'a'},
        {'label': 'Quarterly', 'value': 'q'},
        {'label': 'Monthly', 'value': 'm'},        
        {'label': 'Daily', 'value': 'd'}
    ]

    
BASE_URL = 'http://minikep-db.herokuapp.com/api'

def get_from_api_names(freq):
    url = f'{BASE_URL}/names/{freq}'
    names = requests.get(url).json()
    return [{'label': name, 'value': name} for name in names]


def get_datapoints_url(freq, name, format='csv'):
    url = f'{BASE_URL}/datapoints?'
    params = urllib.parse.urlencode(dict(freq=freq, name=name, format=format))
    return url + params


def get_from_api_datapoints(freq, name):
    url = get_datapoints_url(freq, name)
    data = requests.get(url).json()
    if not isinstance(data, list):
         # if parameters are invalid, response is not a jsoned list
         return []
    return data

def get_time_series_dict(freq, name):
    data = get_from_api_datapoints(freq, name)
    return dict(x = [d['date'] for d in data],
                y = [d['value'] for d in data],
                name = name)   

# NOT TODO: may have additional formatting for html
# - centering
# - sans serif font
# - header
    
# app.layout controls HTML layout of dcc components on page
# there are four dcc components:
#  - radio items 
#  - dropdown menu
#  - graph with time series
#  - links to download data
app.layout = html.Div([
    dcc.RadioItems(
        options=frequencies(),
        value='q',
        id='frequency'
    ),
    dcc.Dropdown(id='name1', value = "GDP_yoy"),
    dcc.Dropdown(id='name2', value = None),
    dcc.Graph(id='time-series-graph'),
    html.Div(id='download-links')
], style={'width': '500'})


 
@app.callback(output=Output('name1', component_property='options'), 
              inputs=[Input('frequency', component_property='value')])
def update_names1(freq):
    return get_from_api_names(freq)


@app.callback(output=Output('name2', component_property='options'), 
              inputs=[Input('frequency', component_property='value')])
def update_names2(freq):
    return get_from_api_names(freq)


@app.callback(output=Output('time-series-graph', 'figure'),
              inputs=[Input('frequency', component_property='value'), 
                      Input('name1', component_property='value'),
                      Input('name2', component_property='value'),                      
                      ])    
def update_graph_parameters(freq, name1, name2):
    layout_dict = dict(margin = {'l': 40, 'r': 0, 't': 20, 'b': 30},
                       legend = dict(orientation="h"),
                       showlegend = True)    
    data_list = [get_time_series_dict(freq, name1)]
    if name2:
        data_list.append(get_time_series_dict(freq, name2))
    return dict(layout=layout_dict, data=data_list) 



def download_html(freq, name):
    link_text = f'{freq}_{name}.csv'
    url = get_datapoints_url(freq, name, 'csv')
    return html.Div(children=[
        # f'Download data for {name} at {freq}: ',
        html.A(link_text, href=url)
    ])


@app.callback(output=Output('download-links', 'children'),
              inputs=[Input('frequency', component_property='value'),
                      Input('name1', component_property='value'),
                      Input('name2', component_property='value'),
                      ])
def update_link_parameters(freq, name1, name2):
    link1 = link2 = None
    if freq and name1:
        link1 = download_html(freq, name1)
    if freq and name2:
        link2 = download_html(freq, name2)
    return [
        link1,
        html.Br(),
        link2
    ]


# NOT TODO: what tests should be designed for this code?
#           specifically, how to test for sah components behaviour?


# NOT TODO: in newer versions - split this list to priority and requires something
# Must split list below to features requiring API change and not.
#
# Components:
# - sections of variables ('GDP Components', 'Prices'...) 
# - download this data as.... [done]
# - human varname description in Russian/English
# - more info about variables as text
# - show latest value
# - link to github <https://github.com/mini-kep/intro>
#


#if __name__ == '__main__':
#    app.run_server(debug=True)           
# Run the Dash app
if __name__ == '__main__':
    app.server.run(debug=True, threaded=True)
    

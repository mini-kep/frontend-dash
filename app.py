"""Controls and vizualisation for 'mini-kep' dataset using Dash/Plotly

Scenario:

1. when page is loaded there is one frequency and one indicator selected,
   one indicator shows on plot 
    
2. select frequency in radio buttons
  -> frequency selection affects list of indicators in drop-down menu 1 and 2
  
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


# Setup from <https://github.com/plotly/dash-heroku-template>
# > ...the template is configured to execute 'server' on 'app.py'
server = flask.Flask(__name__)
server.secret_key = os.environ.get('secret_key', str(randint(0, 1000000)))
app = dash.Dash(__name__, server=server)

# FIXME(css formatting): adding css below affects positioning of radio buttons
# <https://github.com/mini-kep/frontend-dash/issues/4>
# app.css.append_css({"external_url": "https://codepen.io/chriddyp/pen/bWLwgP.css"})

# NOT TODO: may be a class Source with 
# - Source.names() 
# - Source.time_series(freq, name) 
# - Source.frequencies()

def frequencies():
    return [
        {'label': 'Annual', 'value': 'a'},
        {'label': 'Quarterly', 'value': 'q'},
        {'label': 'Monthly', 'value': 'm'},        
        {'label': 'Daily', 'value': 'd'}
    ]

    
BASE_URL = 'http://minikep-db.herokuapp.com/api'

def get_from_api_names(freq):
    """Get dropdown menu labels."""
    url = f'{BASE_URL}/names/{freq}'
    names = requests.get(url).json()
    return [{'label': name, 'value': name} for name in names]


def get_datapoints_url(freq, name, format):
    return (f'{BASE_URL}/datapoints'
            f'?freq={freq}&name={name}&format={format}')    
    

def get_from_api_datapoints(freq, name):
    url = get_datapoints_url(freq, name, format='json')
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

    
# app.layout controls HTML layout of dcc components on page
# there are four dcc components:
#  - TODO: header 
#  - TODO: markdown block
#  - radio items 
#  - 2 dropdown menus
#  - graph with time series
#  - links to download data

# NOT TODO: may have additional formatting for html
# - centering
# - sans serif font (see css issue above)
# - header

app.layout = html.Div([
    # Superceed by level 1 header in markdown
    # html.H1('Explore mini-kep dataset'),     
    dcc.Markdown('''
# Explore mini-kep dataset

Use controls below to select time series 
frequency and variable names.

'''),
   dcc.RadioItems(
        options=frequencies(),
        value='q',
        id='frequency'
    ),
    dcc.Dropdown(id='name1', value = "GDP_yoy"),
    dcc.Dropdown(id='name2', value = None),
    dcc.Graph(id='time-series-graph'),
    html.Div(id='download-links'), 
    dcc.Markdown('''

# Proposed enhancements
    
#### Todo 1 (presentation):
    
New: 
 - show latest value for time series
 - show shorthand url in the data footer
 
Existing: 
 - download data footer as single line
 - move this block on the right, as table
 - hover day in date for daily data
    
#### Todo 2 (requires schema/API/data model change):
 - sections of variables ('GDP Components', 'Prices'...) 
 - human varname description in Russian/English
 - more info about variables as text
 
#### Todo 3 (data map/data integrity):
 - list all time series URLs for download                 

#### Todo 4 (data transformation):
 - diff accumulated time series

#### Todo 5 (ipython notebook):
 - see case list

# Github
 - [Project home](https://github.com/mini-kep/intro) 
 - [This app code](https://github.com/mini-kep/frontend-dash)
    
''') 
    
], style={'width': '500', 
          'marginBottom': 50, 
          'marginTop': 10,
          'marginLeft': 50, 
          'marginRight': 50 
          }
)


 
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
    return html.A(link_text, href=url)

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
        # FIXME: what is the formatting needed to put all of elements below in one line?
        #        is it possible to change html.Div() to something?            
        html.Div("Download data: "),
        link1,
        html.Div(" "),
        link2
    ]

# NOT TODO: what tests should be designed for this code?
#           specifically, how to test for sah components behaviour?

if __name__ == '__main__':
    port = os.environ.get('DASH_PORT', 8000)
    app.server.run(debug=True, threaded=True, port=int(port))
    

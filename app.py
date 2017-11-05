"""Controls and vizualisation for 'mini-kep' dataset using Dash/Plotly

Scenario:

1. when page is loaded there is a frequency and two indicators selected,
   a plot is drawn   
    
2. select frequency in radio buttons
  -> frequency selection affects list of indicators in drop-down menu 1 and 2
  
3. select indicator 1 by name in drop-down menu 
  -> choosing name affects plot and download footer

4. select indicator 2 by name in drop-down menu 
  -> choosing name affects plot and download footer 

    
5. Slider controls source date range and axis range. When changing 
   source the Y axis changes as well.    

"""

"""
NOT IMPLMENTED:
    
1. Group selector added before each variable name selector.

2. One link for csv with two variables (requires API change or
   merging dataframes, a bit harder for daily data). 

3. Annotation for the last observation value.

4. Names description of the variables - must have some text field.

5. Footer formatting.

"""

from datetime import datetime  
from random import randint
import os

import flask
import dash
from dash.dependencies import Input, Output
import dash_core_components as dcc
import dash_html_components as html

import requests


# Setup from <https://github.com/plotly/dash-heroku-template>
# > the template is configured to execute 'server' on 'app.py'
server = flask.Flask(__name__)
server.secret_key = os.environ.get('secret_key', str(randint(0, 1000000)))
app = dash.Dash(__name__, server=server)

# app properties
app.css.append_css({"external_url": "https://codepen.io/anon/pen/LONErz.css"})
app.title = 'mini-kep browser'


BASE_URL = 'http://minikep-db.herokuapp.com/api'

def get_names_from_api(freq):
    return requests.get(f'{BASE_URL}/names/{freq}').json()


class Names:
    """Varibale names by frequency."""

    NAMES = {freq: get_names_from_api(freq) for freq in 'aqmd'}

    def __init__(self, freq):
        self.freq = freq
    
    @property
    def menu_items(self):
        return [{'label': name, 'value': name} for name in self.NAMES.get(self.freq)]   


def frequencies():
    return [
        {'label': 'Annual', 'value': 'a'},
        {'label': 'Quarterly', 'value': 'q'},
        {'label': 'Monthly', 'value': 'm'},        
        {'label': 'Daily', 'value': 'd'}
    ]


class DataSeries:
    def __init__(self, freq, name):
        self.freq = freq
        self.name = name
        self.data = self.get_from_api()
        
    @staticmethod
    def make_url(freq, name, format):
        return (f'{BASE_URL}/datapoints'
                f'?freq={freq}&name={name}&format={format}')    
    
    def get_from_api(self):
        url = self.make_url(self.freq, self.name, 'json')
        data = requests.get(url).json()
        # if parameters are invalid, response is not a jsoned list
        if not isinstance(data, list):
             return []
        return data

    @staticmethod
    def get_year(datapoint):
        return datetime.strptime(datapoint['date'], "%Y-%m-%d").year

    def filter(self, start, end):
        def is_in_range(datapoint):
            year = self.get_year(datapoint)
            return year>=start and year<=end
        self.data = [d for d in self.data if is_in_range(d)]
        return self
    
    def convert_annual_dates_to_int(self):
        """In annual time series plot 1999-12-31 will be plotted around 2000,
           which is misleading, must shift x value to 1999."""
        if self.freq=='a':
            for d in self.data:
                d['date'] = self.get_year(d)        
    
    @property
    def dict(self):
        self.convert_annual_dates_to_int()
        return dict(x = [d['date'] for d in self.data],
                    y = [d['value'] for d in self.data],
                    name = self.name)   

# move to tests
assert DataSeries('a', 'GDP_yoy').filter(2000,2001).dict == \
    {'x': [2000, 2001], 'y': [110.0, 105.1], 'name': 'GDP_yoy'}


MIN_YEAR=1999    
# TODO: change MAX_YEAR when 2018 data arrives
MAX_YEAR=2017

def marks(min_year=MIN_YEAR, max_year=MAX_YEAR):
    marks = {i: "" for i in range(min_year, max_year)}
    for year in [min_year, 2005, 2010, 2015, max_year]:
        marks[year] = str(year)
    return marks   

# app.layout controls HTML layout of dcc components on page:
#  - header and footer markdown blocks
#  - radio items 
#  - 2 dropdown menus
#  - graph with time series
#  - slider for timerange
#  - links to download data

HEADER = '''
# Explore mini-kep dataset

Use controls below to select time series frequency and variable names.
'''

FOOTER = '''
**Github links**:
    
  - [This app code](https://github.com/mini-kep/frontend-dash)
  - [Proposed enhancements](https://github.com/mini-kep/frontend-dash/blob/master/README.md#proposed-enhancements) 
  - [Project home](https://github.com/mini-kep/intro) and
    [dev notes](https://github.com/mini-kep/intro/blob/master/DEV.md)    
'''

START_VALUES = dict(freq='q', name1='GDP_yoy', name2='CPI_rog')


left_window = html.Div([
   dcc.Markdown(HEADER),
   dcc.RadioItems(
        id='frequency',
        options=frequencies(),
        value=START_VALUES['freq']        
    ),
    dcc.Dropdown(id='name1', value = START_VALUES['name1']),
    dcc.Dropdown(id='name2', value = START_VALUES['name2']),
    html.Div([            
            dcc.Graph(id='time-series-graph'),
            dcc.RangeSlider(
                id='view-years',    
                count=1,
                step=1,
                min=MIN_YEAR, max=MAX_YEAR,
                marks=marks(),
                value=[MIN_YEAR, MAX_YEAR]
                )
        ], style={'marginBottom': '50'}),
    html.Div(id='download-links', style={'marginBottom': '25'}), 
], style={'width': '500', 
          'marginTop': 10,
          'marginLeft': 50,
          }
)
    
# FIXME: must align to top    
right_window = html.Div([
    dcc.Markdown("""

**Frontend/dash TODO:**
 - [ ] show latest value for time series (WIP)
 - [ ] show shorthand url in data footer + fix when shorthand url not working
 
**NOT TODO:** 
 - plot on extra axis (NOT TODO)
 - hover day in date for daily data (NOT TODO)

"""),
    dcc.Markdown(FOOTER)
    ])  
    
app.layout = html.Table([

    html.Tr([
            html.Td(left_window),
            html.Td(right_window)
            ])        
        
])
    


@app.callback(output=Output('name1', component_property='options'), 
              inputs=[Input('frequency', component_property='value')])
def update_names1(freq):
    return Names(freq).menu_items


@app.callback(output=Output('name2', component_property='options'), 
              inputs=[Input('frequency', component_property='value')])
def update_names2(freq):
    return Names(freq).menu_items


def xrange(freq, years):
    """Updating x axis based on years selection in renage slider."""
    if freq == 'a':
       start = years[0] - 2
       end = years[1] + 2    
       return dict(range=["{start}", "{end}"])
    else:
       start = years[0] - 2
       end = years[1] + 1    
       return dict(range=[f"{start}-12-31", f"{end}-12-31"])
    

@app.callback(output=Output('time-series-graph', 'figure'),
              inputs=[Input('frequency', component_property='value'), 
                      Input('name1', component_property='value'),
                      Input('name2', component_property='value'),                      
                      Input('view-years', component_property='value'),  
                      ])    
def update_graph_parameters(freq, name1, name2, years):
    layout_dict = dict(margin = {'l': 40, 'r': 0, 't': 20, 'b': 30},
                       legend = dict(orientation="h"),
                       showlegend = True)   
    data_list = [DataSeries(freq, name1).filter(*years).dict]
    if name2:
        ts2 = DataSeries(freq, name2).filter(*years).dict
        data_list.append(ts2)
    layout_dict['xaxis']=xrange(freq, years)
    return dict(layout=layout_dict, data=data_list) 
    

# FIXME: annotations
# <https://community.plot.ly/t/annotation-not-showing-on-dash-dcc-graph/6660>


def download_html(freq, name):
    link_text = f'{freq}_{name}.csv'
    url = DataSeries.make_url(freq, name, 'csv')
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
    return ["Download data: ", link1, " ",  link2]


if __name__ == '__main__':
    port = os.environ.get('DASH_PORT', 8000)
    app.server.run(debug=True, threaded=True, port=int(port))

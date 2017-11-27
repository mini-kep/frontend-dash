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

NOT IMPLMENTED:

1. Group selector added before each variable name selector.

2. Position right pane

3. Show latest value 

4. Show var and unit description

5. Default vars for frequency

6. More html header
"""


import os
import flask
from datetime import datetime
from random import randint

import dash
from dash.dependencies import Input, Output
import dash_core_components as dcc
import dash_html_components as html

import access

# Setup from <https://github.com/plotly/dash-heroku-template>
# > the template is configured to execute 'server' on 'app.py'
server = flask.Flask(__name__)
server.secret_key = os.environ.get('secret_key', str(randint(0, 1000000)))
app = dash.Dash(__name__, server=server)

# app properties
app.css.append_css({"external_url": "https://codepen.io/anon/pen/LONErz.css"})
app.title = 'Macro dataset browser'


NAMES = {freq: access.get_names(freq) for freq in 'aqmd'}


class WidgetItems:
    @classmethod
    def names(cls, freq):
        """Varibale names by frequency."""
        return [{'label': name, 'value': name} for name in NAMES.get(freq)]

    @classmethod
    def frequencies(cls):
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
        self.data = access.DatapointsJSON(freq, name).json()

    @staticmethod
    def get_year(datapoint):
        return datetime.strptime(datapoint['date'], "%Y-%m-%d").year

    def filter(self, start, end):
        def is_in_range(datapoint):
            year = self.get_year(datapoint)
            return year >= start and year <= end

        self.data = [d for d in self.data if is_in_range(d)]
        return self

    def convert_annual_dates_to_int(self):
        """In annual time series plot 1999-12-31 will be plotted around 2000,
           which is misleading, must shift x value to 1999."""
        if self.freq == 'a':
            for d in self.data:
                d['date'] = self.get_year(d)

    @property
    def dict(self):
        self.convert_annual_dates_to_int()
        return dict(x=[d['date'] for d in self.data],
                    y=[d['value'] for d in self.data],
                    name=self.name)


MIN_YEAR = 1999
MAX_YEAR = datetime.today().year


def marks(min_year=MIN_YEAR, max_year=MAX_YEAR):
    marks = {i: "" for i in range(min_year, max_year)}
    for year in [min_year, 2005, 2010, 2015, max_year]:
        marks[year] = str(year)
    return marks



HEADER = '''
# Explore mini-kep dataset
'''

# Use controls below to select time series frequency and variable names.

FOOTER = '''Links: 
  [project home](https://github.com/mini-kep/intro),
  [app code](https://github.com/mini-kep/frontend-dash), 
  [dev notes](https://github.com/mini-kep/intro/blob/master/DEV.md), 
  [Trello issues](https://trello.com/b/ioHBMwH7/minikep)
'''

START_VALUES = dict(freq='q', name1='GDP_yoy', name2='CPI_rog')

left_window = html.Div([
    dcc.Markdown(HEADER),
    dcc.RadioItems(
        id='frequency',
        options=WidgetItems.frequencies(),
        value=START_VALUES['freq']
    ),
    dcc.Dropdown(id='name1', value=START_VALUES['name1']),
    dcc.Dropdown(id='name2', value=START_VALUES['name2']),
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
            ], style={'marginBottom': '50'}
            ),
    html.Div(id='download-links'),
], style={'width': '500'}
)

right_window = html.Div([
    html.Div(id='var1-info', style={'marginBottom': 25}),
    html.Div(id='var2-info', style={'marginBottom': 25}),
], style={'marginRight': 75})


tr1 = html.Tr([
        html.Td(left_window, style={'verticalAlign': 'top'}),
        html.Td(right_window, style={'verticalAlign': 'top'}),
    ])

# TODO: two extra hr-like lines appear 

app.layout =  html.Div([
       
        html.Table([tr1]),
        
        html.Div(dcc.Markdown(FOOTER), style={'marginTop': 15})          
        
        ], style={'marginTop': 25, 'marginLeft': 50})
    
    
# callbacks    
    

#
#        information block 
#
#        Variable         BRENT
#        Frequency:       d
#        Start:           1987-05-20
#        End:             2017-10-30
#        Latest value:    60.65
#        Download:        <api/datapoints?freq=d&name=BRENT&format=csv>
#        Short link:      <oil/series/BRENT/d>


def make_row(x):
    return html.Tr([html.Td(x[0]), html.Td(x[1])])

def make_html_table(table_elements):
    return html.Table([make_row(x) for x in table_elements])

# FIXME: freq repeated in two tables

def short_link(freq, name):
    cu = access.CustomAPI(freq, name)
    text = cu.endpoint
    return html.A(text, href=cu.url)

def varinfo(freq, name):
    vi = access.VarInfo(freq, name)
    table_elements = [
        (html.B('Variable'), html.B(name)),
        ('Description', 'reserved'),
        ('Frequency', freq),
        ('Start', vi.start_date),
        ('Latest date', vi.latest_date),
        # FIMXE in API: shows 'reserved'
        ('Latest value', vi.latest_value),
        #('Download', download_link(freq, name)),
        ('Short link', short_link(freq, name))
    ]
    return make_html_table(table_elements)


@app.callback(output=Output('var1-info', 'children'),
              inputs=[Input('frequency', component_property='value'),
                      Input('name1', component_property='value'),
                      ])
def update_varinfo1(freq, name):
    return varinfo(freq, name)


@app.callback(output=Output('var2-info', 'children'),
              inputs=[Input('frequency', component_property='value'),
                      Input('name2', component_property='value')
                      ])
def update_varinfo2(freq, name):
    return varinfo(freq, name)


@app.callback(output=Output('name1', component_property='options'),
              inputs=[Input('frequency', component_property='value')])
def update_names1(freq):
    return WidgetItems.names(freq)


@app.callback(output=Output('name2', component_property='options'),
              inputs=[Input('frequency', component_property='value')])
def update_names2(freq):
    return WidgetItems.names(freq)


def xrange(freq, years):
    """Updating x axis based on years selection in range slider."""
    if freq == 'a':
        start = years[0] - 2
        end = years[1] + 3
        return dict(range=["{start}", "{end}"])
    else:
        start = years[0] - 2
        end = years[1] + 2
        return dict(range=[f"{start}-12-31", f"{end}-12-31"])


def annotation_item(data_dict):
    x, y = get_last(data_dict)
    return dict(xref='x', yref='y',
                x=x, y=y,
                font=dict(color='black'),
                xanchor='left',
                yanchor='middle',
                text=f' {y}',
                showarrow=False)


def get_last(data_dict):
    return data_dict['x'][-1], data_dict['y'][-1]


@app.callback(output=Output('time-series-graph', 'figure'),
              inputs=[Input('frequency', component_property='value'),
                      Input('name1', component_property='value'),
                      Input('name2', component_property='value'),
                      Input('view-years', component_property='value'),
                      ])
def update_graph_parameters(freq, name1, name2, years):
    # data
    ts1 = DataSeries(freq, name1).filter(*years).dict
    anno = [annotation_item(ts1)]
    data_list = [ts1]
    if name2:
        ts2 = DataSeries(freq, name2).filter(*years).dict
        data_list.append(ts2)
        anno.append(annotation_item(ts2))
    # layout
    layout_dict = dict(margin={'l': 40, 'r': 0, 't': 20, 'b': 30},
                       legend=dict(orientation="h"),
                       showlegend=True)
    layout_dict['xaxis'] = xrange(freq, years)
    layout_dict['annotations'] = anno
    return dict(layout=layout_dict, data=data_list)


def download_data_html(freq, names, years):
    link_text = 'Download data in CSV format'
    url = access.Frame(freq, names).url
    # FIXME: bring back years
    return html.A(link_text, href=url)


@app.callback(output=Output('download-links', 'children'),
              inputs=[Input('frequency', component_property='value'),
                      Input('name1', component_property='value'),
                      Input('name2', component_property='value'),
                      Input('view-years', component_property='value'),
                      ])
def update_link_parameters(freq, name1, name2, years):
    link1 = None
    # FIXME: must simplify
    # (names,) = [','.join((name1, name2)) if name1 and name2 else name1 or name2]
    names = []
    for name in (name1, name2):
        if name: 
            names.append(name)
    if freq and names:
        link1 = download_data_html(freq, names, years)
    return [link1]


# app.layout controls HTML layout of dcc components on page:
#  - header and footer markdown blocks
#  - radio items
#  - 2 dropdown menus
#  - graph with time series
#  - slider for timerange
#  - links to download data



if __name__ == '__main__':
    port = os.environ.get('DASH_PORT', 8000)
    app.server.run(debug=True, threaded=True, port=int(port))

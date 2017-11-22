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

2. Annotation for the last observation value.

"""

import os
import flask
import requests
from datetime import datetime
from random import randint

import dash
from dash.dependencies import Input, Output
import dash_core_components as dcc
import dash_html_components as html

# Setup from <https://github.com/plotly/dash-heroku-template>
# > the template is configured to execute 'server' on 'app.py'
server = flask.Flask(__name__)
server.secret_key = os.environ.get('secret_key', str(randint(0, 1000000)))
app = dash.Dash(__name__, server=server)

# app properties
app.css.append_css({"external_url": "https://codepen.io/anon/pen/LONErz.css"})
app.title = 'mini-kep browser'

BASE_URL = 'http://minikep-db.herokuapp.com'


def fetch(url):
    return requests.get(url).json()


def get_list(url):
    data = fetch(url)
    # if parameters are invalid, response is not a list
    if not isinstance(data, list):
        return []
    return data


# NOT TODO: this may need change
class URL:
    def __init__(self, freq, name=None):
        self.freq = freq
        self.name = name

    def info(self):
        return (f'{BASE_URL}/api/info'
                f'?freq={self.freq}&name={self.name}')

    def names(self):
        return f'{BASE_URL}/api/names/{self.freq}'

    def datapoints(self, format):
        return (f'{BASE_URL}/api/datapoints'
                f'?freq={self.freq}&name={self.name}&format={format}')

    def frame(self, names, start_date, end_date):
        return (f'{BASE_URL}/api/frame?freq={self.freq}&names={names}'
                f'&start_date={start_date}&end_date={end_date}')

    @property
    def custom_text(self):
        return f'series/{self.name}/{self.freq}'

    @property
    def custom_link(self):
        return f'{BASE_URL}/all/series/{self.name}/{self.freq}'

    @property
    def csv(self):
        return self.datapoints('csv')


class RemoteAPI:
    def __init__(self, freq, name=None):
        self.freq = freq
        self.name = name

    @property
    def info(self):
        url = URL(self.freq, self.name).info()
        return fetch(url)

    @property
    def names(self):
        url = URL(self.freq).names()
        return get_list(url)

    @property
    def json(self):
        url = URL(self.freq, self.name).datapoints('json')
        return get_list(url)

    @property
    def csv(self):
        url = URL(self.freq, self.name).datapoints('csv')
        return get_list(url)


NAMES = {freq: RemoteAPI(freq).names for freq in 'aqmd'}


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
        self.data = RemoteAPI(freq, name).json

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
  - [Project home](https://github.com/mini-kep/intro) and
    [dev notes](https://github.com/mini-kep/intro/blob/master/DEV.md)
  - [Trello issues board](https://trello.com/b/ioHBMwH7/minikep)
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
    ], style={'marginBottom': '50'}),
    html.Div(id='download-links'),
], style={'width': '500',
          'marginTop': 10,
          'marginLeft': 50,
          'marginRight': 100}
)

right_window = html.Div([
    html.Div(id='var1-info', style={'marginTop': 25}),
    html.Div(id='var2-info', style={'marginBottom': 25}),
    dcc.Markdown(FOOTER)
])

app.layout = html.Table([
    html.Tr([
        html.Td(left_window, style={'verticalAlign': 'top'}),
        html.Td(right_window, style={'verticalAlign': 'top'})
    ])
])


# Needed following change
#
#        a. Layout: make every variable information block an html table
#
#        Variable         BRENT
#        Frequency:       d
#        Start:           1987-05-20
#        End:             2017-10-30
#        Latest value:    60.65
#        Download:        <api/datapoints?freq=d&name=BRENT&format=csv>
#        Short link:      <oil/series/BRENT/d>
#        More info:       <api/info?name=BRENT>
#
#        b. content - retrieve this data from api/info?name=BRENT
#
#        c. NOT TODO: update with slider change ?


class VarInfo:
    def __init__(self, freq, name):
        self.freq = freq
        url = URL(freq, name).info()
        self.info = fetch(url)

    def __getattr__(self, x):
        return self.info[self.freq].get(x)


def short_link(freq, name):
    text = f'ru/series/{name}/{freq}'
    return html.A(text, href=f'{BASE_URL}/{text}')


def download_link(freq, name):
    text = f'api/datapoints?freq={freq}&name={name}'
    return html.A(text, href=f'{BASE_URL}/{text}')


def make_row(x):
    return html.Tr([html.Td(x[0]), html.Td(x[1])])


def make_html_table(table_elements):
    return html.Table([make_row(x) for x in table_elements])

# WONTFIX: freq repeated in two tables

# WONTFIX: variables too close together


def varinfo(freq, name):
    vi = VarInfo(freq, name)
    table_elements = [
        (html.B('Variable'), html.B(name)),
        # WONTFIX: repeated in two tables
        ('Frequency', freq),
        ('Start', vi.start_date),
        ('End', vi.latest_date),
        # WONTFIX: will show 'reserved'
        ('Latest value', vi.latest_value),
        ('Download', download_link(freq, name)),
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


# FIXME: annotations
# <https://community.plot.ly/t/annotation-not-showing-on-dash-dcc-graph/6660>


def download_data_html(freq, names, years):
    link_text = 'csv'
    url = URL(freq).frame(names, *years)
    return html.A(link_text, href=url)


@app.callback(output=Output('download-links', 'children'),
              inputs=[Input('frequency', component_property='value'),
                      Input('name1', component_property='value'),
                      Input('name2', component_property='value'),
                      Input('view-years', component_property='value'),
                      ])
def update_link_parameters(freq, name1, name2, years):
    link1 = None
    (names,) = [','.join((name1, name2)) if name1 and name2 else name1 or name2]
    if freq and names:
        link1 = download_data_html(freq, names, years)
    return ["Download data: ", link1]


if __name__ == '__main__':
    port = os.environ.get('DASH_PORT', 8000)
    app.server.run(debug=True, threaded=True, port=int(port))

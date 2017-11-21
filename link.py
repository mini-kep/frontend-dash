import dash
import dash_core_components as dcc
import dash_html_components as html

class BrowserURL:
    def __init__(self, url_path):
        legs = [leg for leg in url_path.split("/") if leg] 
        self.freq = legs[0]
        self.name2 = None
        if '+' in legs[1]: 
            self.name1, self.name2 = legs[1].split('+')
        else:
            self.name1 = legs[1]        



app = dash.Dash()

app.layout = html.Div([
    # represents the URL bar, doesn't render anything
    dcc.Location(id='url', refresh=False),

    # content will be rendered in this element
    html.Div(id='page-content')
])


@app.callback(dash.dependencies.Output('page-content', 'children'),
              [dash.dependencies.Input('url', 'pathname')])
def display_page(pathname):
    bu = BrowserURL(pathname)
    return html.Div([
        html.Div([f'frequency: {bu.freq}']),
        html.Div([f'name1: {bu.name1}']),
        html.Div([f'name2: {bu.name2}'])
    ])    
    
app.css.append_css({
    'external_url': 'https://codepen.io/chriddyp/pen/bWLwgP.css'
})


if __name__ == '__main__':
    app.run_server(debug=True)
import dash
import dash_core_components as dcc
import dash_html_components as html

class BrowserURL:
    def __init__(self, url_path):
        legs = [leg for leg in url_path.split("/") if leg] 
        self.freq = legs[0]
        self.names = legs[1].split('+')

assert BrowserURL('/d/BRENT').freq == 'd' 
assert BrowserURL('/d/BRENT').names == ['BRENT'] 
assert BrowserURL('/d/BRENT+USDRUR_CB').names == ['BRENT', 'USDRUR_CB'] 
assert BrowserURL('zzz/GDP_yoy+CPI_rog').freq == 'zzz'
assert BrowserURL('zzz/a+b').names == ['a', 'b']


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

# ------- app.py main table goes here -----------------           
            
            
        html.Div([f'frequency: {bu.freq}']),
        html.Div([f'names: {bu.names}']),

# -----------------------------------------------------
    ])    
    
app.css.append_css({
    'external_url': 'https://codepen.io/chriddyp/pen/bWLwgP.css'
})


if __name__ == '__main__':
    app.run_server(debug=True)
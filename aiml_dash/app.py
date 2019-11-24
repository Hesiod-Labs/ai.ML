import dash
from run2 import server

app = dash.Dash(__name__,
                server=server,
                external_stylesheets=['https://codepen.io/chriddyp/pen/bWLwgP.css'],
                routes_pathname_prefix='/dash/')
app.config.suppress_callback_exceptions = True

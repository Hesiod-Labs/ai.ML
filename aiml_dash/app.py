import dash

app = dash.Dash(__name__,
                external_stylesheets=['https://codepen.io/chriddyp/pen/bWLwgP.css'],
                routes_pathname_prefix='/dash/')
app.config.suppress_callback_exceptions = True

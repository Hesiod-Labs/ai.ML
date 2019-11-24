import dash
import dash_core_components as dcc
import dash_html_components as html
from aiml_dash.layouts import build_layout, dataset_layout

def baselayout(app):
    import aiml_dash.callbacks 
    app.layout = html.Div([
        dcc.Tabs(id='tabs', value='dataset', children=[
            dcc.Tab(label='Dataset', value='dataset', children=dataset_layout,
                    style={'fontSize': '14pt', 'fontWeight': 'bold'}),
            dcc.Tab(label='Build', value='build', children=build_layout,
                    style={'fontSize': '14pt', 'fontWeight': 'bold'})]),
        html.Div(id='tabs-content')])

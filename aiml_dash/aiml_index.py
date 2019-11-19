from aiml_dash.app import app
import dash_html_components as html
import dash_core_components as dcc

from aiml_dash.layouts import dataset_layout, build_layout
import aiml_dash.callbacks

'''From Dash documentation: The Dash instance is defined in a separate 
app.py, while the entry point for running the app is aiml_index.py. This 
separation is required to avoid circular imports: the files containing the 
callback definitions require access to the Dash app instance however if this 
were imported from aiml_index.py, the initial loading of aiml_index.py would 
ultimately require itself to be already imported, which cannot be satisfied. '''

app.layout = html.Div([
    dcc.Tabs(id='tabs', value='tab-1', children=[
        dcc.Tab(label='Dataset', value='dataset', children=dataset_layout,
                style={'fontSize': '14pt'}),
        dcc.Tab(label='Build', value='build', children=build_layout,
                style={'fontSize': '14pt'})]),
    html.Div(id='tabs-content')])


if __name__ == '__main__':
    app.run_server(debug=True)

import base64
import io
import flask

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import dash_table
from plotly import graph_objects as go

import pandas as pd
import numpy as np

server = flask.Flask(__name__)
'''
@server.route('/')
def index():
    return 'Hello Flask'
'''

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

example_csv = pd.read_csv('https://gist.githubusercontent.com/chriddyp/'
                          'c78bf172206ce24f77d6363a2d754b59/raw/'
                          'c353e8ef842413cae56ae3920b8fd78468aa4cb2/'
                          'usa-agricultural-exports-2011.csv')

app = dash.Dash(__name__,
                server=server,
                routes_pathname_prefix='/dash/',
                external_stylesheets=external_stylesheets)


ops = {
    'ge': '>=',
   'le': '<=',
   'lt': '<',
   'gt': '>',
   'ne': '!=',
   'eq': '=',
   'contains': None,
   'datestartswith': None
}


def generate_options(options: list):
    return [{'label': str.capitalize(o),
             'value': str.lower(o)
             } for o in options]


def generate_dtable(df, table_id: str, virtual=True):
    df = pd.DataFrame(df)
    df[''] = df.index
    return dash_table.DataTable(
        id=table_id,
        columns=[{'name': col,
                  'id': col,
                  'deletable': True}
                 for col in sorted(df.columns)],
        data=df.to_dict('records'),
        virtualization=virtual,

        filter_action='custom',
        filter_query='',

        sort_action='custom',
        sort_mode='multi',
        sort_by=[],

        fixed_rows={'headers': True, 'data': 0},

        style_as_list_view=True,
        style_cell={'padding': '5px'},
        style_header={
            'backgroundColor': 'white',
            'fontWeight': 'bold'
        },
    )

'''
def split_filter(filter_part):
    for k, v in ops.items():
        if v in filter_part:
            name_part, value_part = filter_part.split(v, 1)
            name = name_part[name_part.find('{') + 1: name_part.rfind('}')]
            value_part = value_part.strip()
            v0 = value_part[0]
            if v0 == value_part[-1] and v0 in {"'", '"', '`'}:
                value = value_part[1:-1].replace('\\' + v0, v0)
            else:
                try:
                    value = float(value_part)
                except ValueError:
                    value = value_part
            # word operators need spaces but we don't want these later
            return name, k.strip(), value
    return [None] * 3
'''

dataset_layout = html.Div([
    dcc.Upload(
        id='upload-data',
        children=html.Div([
            'Drag and Drop or ',
            html.A('Select Files')
        ]),
        style={
            'width': '100%',
            'height': '60px',
            'lineHeight': '60px',
            'borderWidth': '1px',
            'borderStyle': 'dashed',
            'borderRadius': '5px',
            'textAlign': 'center',
            'margin': '10px'
        },
        # Allow multiple files to be uploaded
        multiple=False
    ),
    html.Div(id='output-data-upload'),
])

exploration_layout = html.Div([
    html.Div(style={'display': 'inline-block', 'width': '49%'}, children=[
        dcc.Graph(id='scatter'),
        html.Div([
            dcc.RadioItems(
                id='x_scale',
                options=generate_options(['linear', 'log']),
                value='linear',
                labelStyle={'display': 'inline-block'}
            ),
            dcc.RadioItems(
                id='y_scale',
                options=generate_options(['linear', 'log']),
                value='linear',
                labelStyle={'display': 'inline-block'}
            )
        ], style={'display': 'inline-block', 'width': '49%'}),
        html.Div([
            dcc.Dropdown(
                id='x_options',
                options=generate_options(example_csv.columns.unique()),
                value=example_csv.columns[0]
            ),
            dcc.Dropdown(
                id='y_options',
                options=generate_options(example_csv.columns.unique()),
                value=example_csv.columns[1]
            )
        ], style={'display': 'inline-block', 'width': '49%'})
    ]),
    html.Div([
        dcc.Graph(id='distribution'),
    ], style={'display': 'inline-block', 'width': '49%'})
])

app.layout = html.Div([
    dcc.Tabs(id='tabs', value='tab-1', children=[
        dcc.Tab(label='Dataset', value='dataset', children=dataset_layout),
        #dcc.Tab(label='Exploration', value='explore',
        #        children=exploration_layout),
        dcc.Tab(label='Build', value='build')
    ]),
    html.Div(id='tabs-content')
])


def parse_contents(file, filename):
    content_type, content_string = file.split(',')
    decoded = base64.b64decode(content_string)
    try:
        if 'csv' in filename:
            df = pd.read_csv(io.StringIO(decoded.decode('utf-8')))
    except Exception as e:
        print(e)
        return html.Div(['There was an error processing this file.'])

    return html.Div([
        html.H3(str.split(filename, '.')[0].capitalize()),
        html.H6('Descriptive Statistics'),
        html.Div([generate_dtable(df.describe(), 'descriptive',
                                  virtual=False)]),
        html.Hr(),
        html.H6('Dataset'),
        html.Div([generate_dtable(df, table_id='dataset')]),
    ])


@app.callback(Output('output-data-upload', 'children'),
              [Input('upload-data', 'contents')],
              [State('upload-data', 'filename')])
def update_output(content, name):
    if content:
        return [parse_contents(content, name)]

'''
@app.callback(
    Output('dataset', 'data'),
    [Input('dataset', 'sort_by'),
     Input('dataset', 'filter_query')])
def update_dtable(sort_by, table_filter):
    filter_expr = table_filter.split(' && ')
    df = example_csv
    for filter_part in filter_expr:
        col_name, op, filter_val = split_filter(filter_part)
        if op in set(ops.keys()).difference({'contains, datestartswith'}):
            df = df.loc[getattr(col_name, op)(filter_val)]
        elif op == 'contains':
            df = df.loc[df[col_name].str.contains(filter_val)]
        elif op == 'datestartswith':
            df = df.loc[df[col_name].str.startswith(filter_val)]
    if len(sort_by):
        df = df.sort_values(
            [col['column_id'] for col in sort_by],
            ascending=[
                col['direction'] == 'asc' for col in sort_by
            ],
            inplace=False
        )
    return df.to_dict('records')
@app.callback(Output('scatter', 'figure'), [
    Input('x_options', 'value'),
    Input('y_options', 'value'),
    Input('x_scale', 'value'),
    Input('y_scale', 'value')
])
def update_scatter(x_axis, y_axis, x_scale, y_scale):
    return {
        'data': [go.Scatter(
            x=example_csv[x_axis],
            y=example_csv[y_axis],
            mode='markers')],
        'layout': go.Layout(
            xaxis={
                'title': x_axis,
                'type': x_scale
            },
            yaxis={
                'title': y_axis,
                'type': y_scale
            }
        )
    }
@app.callback(Output('distribution', 'figure'), [
    Input('x_options', 'value'),
    Input('y_scale', 'value')
])
def update_dist(x_axis, y_scale):
    return {
        'data': [go.Histogram(
            x=example_csv[x_axis]
        )],
        'layout': go.Layout(
            xaxis={
                'title': x_axis,
            },
            yaxis={
                'type': y_scale,
            }
        )
    }
'''

if __name__ == '__main__':
    app.run_server(debug=True, dev_tools_hot_reload_interval=0.1)

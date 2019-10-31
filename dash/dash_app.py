import base64
import io

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import dash_table
import dash_daq as daq
from plotly import graph_objects as go

import pandas as pd

from sklearn.linear_model.logistic import LogisticRegression
from sklearn.svm import SVC

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

app.config.suppress_callback_exceptions = True

ALGO_PARAMS = {'logistic regression': [
    'tolerance',
    'cost',
    'fit intercept',
    'l1 ratio',
    'train model'
],
    'support vector classification': [
        'tolerance',
        'cost',
        'kernel',
        'degree',
        'gamma',
        'shrinking',
        'probability',
        'train model'
    ]
}


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
        html.Div([generate_dtable(df.describe(),
                                  'descriptive',
                                  virtual=False)
                  ]),
        html.Br(),
        html.H6('Dataset'),
        html.Div([generate_dtable(df, table_id='dataset')]),
    ])


def generate_options(options: list):
    return [{'label': str.capitalize(o),
             'value': str.lower(o)} for o in options]


def generate_dtable(df, table_id: str, virtual=True):
    df = pd.DataFrame(df)
    df[''] = df.index
    return dash_table.DataTable(
        id=table_id,
        columns=[{'name': col,
                  'id': col,
                  'deletable': False}
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
        style_cell={'padding': '5px', 'fontSize': '14pt'},
        style_header={
            'backgroundColor': 'white',
            'fontWeight': 'bold',
            'fontSize': '14pt',
        },
    )


def generate_slider(sl_id, minimum, maximum, step, val, marks=None):
    slider = dcc.Slider(id=sl_id,
                        min=minimum,
                        max=maximum,
                        step=step,
                        value=val)
    if marks:
        slider.marks = marks
    return slider


def generate_dropdown(dd_id, options):
    return dcc.Dropdown(id=dd_id, options=generate_options(options))


PARAMS_MENU = {
    'tolerance':
        html.Div(className='model-parameters', children=[
            html.H6('Tolerance'),
            html.Div(id='tolerance-container'),
            generate_slider('tolerance-slider', 0, 0.01, 0.00001, 0.005),
            html.Br()]),
    'cost': html.Div(className='model-parameters', children=[
        html.H6('Cost'),
        html.Div(id='cost-container'),
        generate_slider('cost-slider', 0, 1, 0.01, 0.5),
        html.Br()]),
    'l1 ratio': html.Div(className='model-parameters', children=[
        html.H6('L1 Ratio'),
        html.Div(id='l1-ratio-container'),
        generate_slider('l1-ratio-slider', 0, 1, 0.01, 0.5, {0: 'L2', 1: 'L1'}),
        html.Br()]),
    'fit intercept': html.Div(className='model-parameters', children=[
        html.H6('Fit Intercept'),
        html.Div(id='fit-intercept-container'),
        daq.BooleanSwitch(id='fit-intercept-switch', on=False),
        html.Br()]),
    'kernel': html.Div(className='model-parameters', children=[
        html.H6('Kernel'),
        html.Div(id='kernel-container'),
        generate_dropdown(
            'kernel-dropdown',
            ['radial basis function', 'linear', 'polynomial', 'sigmoid']),
        html.Br()]),
    'degree': html.Div(className='model-parameters', children=[
        html.H6('Kernel Degree'),
        html.Div(id='kernel-degree-container'),
        generate_slider('kernel-degree-slider', 1, 5, 1, 3,
                        marks={1: '1', 2: '2', 3: '3', 4: '4', 5: '5'}),
        html.Br()]),
    'gamma': html.Div(className='model-parameters', children=[
        html.H6('Gamma'),
        html.Div(id='gamma-container'),
        generate_dropdown('gamma-dropdown', ['scale', 'auto']),
        html.Br()]),
    'shrinking': html.Div(className='model-parameters', children=[
        html.H6('Shrinking'),
        html.Div(id='shrinking-container'),
        daq.BooleanSwitch(id='shrinking-switch', on=True),
        html.Br()]),
    'probability': html.Div(className='model-parameters', children=[
        html.H6('Probability'),
        html.Div(id='probability-container'),
        daq.BooleanSwitch(id='probability-switch', on=True),
        html.Br()]),
    'train model': html.Div(className='model-parameters', children=[
        html.Br(),
        dcc.ConfirmDialogProvider(
            children=html.Button(id='train-model',
                                 children='Train Model',
                                 n_clicks=0),
            message='Confirm that you want to train the model'),
        html.Br()
    ])
}

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
        multiple=False
    ),
    html.Div(id='output-data-upload'),
])

build_layout = html.Div([
    html.Div([
        dcc.Dropdown(id='algorithms',
                     options=generate_options(list(ALGO_PARAMS.keys())))]),
    html.Div(id='params-menu',
             className='model-parameters',
             style={'display': 'inline-block', 'width': '15%'}),
    html.Div(id='results', style={'display': 'inline-block'})])


app.layout = html.Div([
    dcc.Tabs(id='tabs', value='tab-1', children=[
        dcc.Tab(label='Dataset', value='dataset', children=dataset_layout,
                style={'fontSize': '14pt'}),
        dcc.Tab(label='Build', value='build', children=build_layout,
                style={'fontSize': '14pt'})]),
    html.Div(id='tabs-content')])


@app.callback(Output('params-menu', 'children'),
              [Input('algorithms', 'value')])
def update_parameter_container(value):
    if value:
        return [PARAMS_MENU[p] for p in ALGO_PARAMS[value.lower()]]


@app.callback(Output('l1-ratio-container', 'children'),
              [Input('l1-ratio-slider', 'value')])
def update_l1_ratio_output(value):
    return value


@app.callback(Output('cost-container', 'children'),
              [Input('cost-slider', 'value')])
def update_cost_slider_output(value):
    return value


@app.callback(Output('tolerance-container', 'children'),
              [Input('tolerance-slider', 'value')])
def update_tolerance_slider_output(value):
    return value

'''
@app.callback(Output('results', 'children'),
              [Input('algorithms', 'value'),
               Input('tolerance-slider', 'value'),
               Input('cost-slider', 'value'),
               Input('probability-switch', 'on'),
               Input('l1-ratio-slider', 'value'),
               Input('fit-intercept-switch', 'on'),
               Input('kernel-dropdown', 'value'),
               Input('kernel-degree-dropdown', 'value'),
               Input('gamma-dropdown', 'value'),
               Input('shrinking-switch', 'on')])
def train_model(algo, tol, cost, prob, ratio, fit, ker, ker_deg, gamma, shrink):
    if algo.lower() == 'logistic regression':
        lr = LogisticRegression(penalty='elasticnet',
                                tol=tol,
                                C=cost,
                                fit_intercept=fit,
                                l1_ratio=ratio)
    elif algo.lower() == 'support vector classification':
        sk_kernels = {'linear': 'linear',
                      'polynomial': 'poly',
                      'radial basis function': 'rbf',
                      'sigmoid': 'sigmoid'}
        svc = SVC(C=cost,
                  kernel=sk_kernels[ker],
                  degree=ker_deg,
                  shrinking=shrink,
                  gamma=gamma,
                  probability=prob,
                  )
    return [html.H5('Model has been trained')]
'''


@app.callback(Output('output-data-upload', 'children'),
              [Input('upload-data', 'contents')],
              [State('upload-data', 'filename')])
def update_output(content, name):
    if content:
        return [parse_contents(content, name)]


if __name__ == '__main__':
    app.run_server(debug=True, dev_tools_hot_reload_interval=0.1)

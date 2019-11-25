import base64
import io

import dash_html_components as html
from dash.dependencies import Input, Output, State

import pandas as pd

from model import model
from app import app
from build_parameters import PARAMETERS
import utils

ALGO_CALLBACK_INPUTS = [(
    f'{algo}-{param}-{meta["widget"]}',
    Input(f'{algo}-{param}-{meta["widget"]}', 'value'))
    for algo in PARAMETERS.keys() for param, meta in PARAMETERS[algo].items()
]


# Dataset page callbacks
@app.callback(
    Output('stored_data-upload', 'children'),
    [Input('data-upload', 'contents')],
    [State('data-upload', 'filename')]
)
def json_data(file, filename):
    try:
        if file and filename:
            content_type, content_string = file.split(',')
            decoded = base64.b64decode(content_string)
            if 'csv' in filename:
                df = pd.read_csv(io.StringIO(decoded.decode('utf-8')))
                return [utils.json_df(utils.format_dataset_name(filename), df)]
    except Exception as e:
        print(e)
        return html.Div(['There was an error processing this file.'])


@app.callback(
    Output('data_output-upload', 'children'),
    [Input('stored_data-upload', 'children')]
)
def update_dataset_output(jsoned_data):
    if jsoned_data:
        name, data = utils.unjson_df(jsoned_data[0])
        return [html.Div([
            html.H2(name, style={'fontWeight': 'bold'}),
            html.H4('Descriptive Statistics'),
            utils.generate_dtable(
                data.describe(),
                'descriptive',
                virtual=False,
                editable=False
            ),
            html.Br(),
            html.H4('Dataset'),
            utils.generate_dtable(data, table_id='dataset'),
        ])]


# Build page callbacks
@app.callback(
    Output('hyperparameters-container', 'children'),
    [Input('algorithm_selection-dropdown', 'value')]
)
def update_hyperparameters_container(value):
    return [html.H4('Hyperparameters', style={'fontWeight': 'bold'})] + \
           utils.generate_widget(value)


@app.callback(
    Output('logistic regression-penalty-dropdown', 'options'),
    [Input('logistic regression-solver-dropdown', 'value')]
)
def filter_available_logistic_regression_penalty(value):
    penalties = PARAMETERS['logistic regression']['penalty']['options']
    items = penalties.items()
    solvers = {
        'sag': {k: v for k, v in items if k in {'l2', 'none'}},
        'saga': penalties,
        'newton-cg': {k: v for k, v in items if k in {'l2', 'none'}},
        'lbfgs': {k: v for k, v in items if k == 'l2'},
        'liblinear': {k: v for k, v in items if k != 'none'}
    }
    return utils.generate_options(solvers[value])


@app.callback(
    Output('logistic regression-solver-dropdown', 'options'),
    [Input('logistic regression-penalty-dropdown', 'value')]
)
def filter_available_logistic_regression_solver(value):
    solvers = PARAMETERS['logistic regression']['solver']['options']
    elastic_net = {k: v for k, v in solvers.items() if k == 'saga'}
    if value == 'elasticnet':
        return utils.generate_options(elastic_net)
    else:
        return utils.generate_options(solvers)


@app.callback(
    Output('logistic regression-l1_ratio-input', 'disabled'),
    [Input('logistic regression-penalty-dropdown', 'value')]
)
def allow_l1_ratio_specification(value):
    return value.lower() != 'elasticnet'


@app.callback(
    Output('k nearest neighbors-p-input', 'disabled'),
    [Input('k nearest neighbors-metric-dropdown', 'value')]
)
def allow_minkowski_specification(value):
    return value.lower() != 'minkowski'


@app.callback(
    Output('support vector classification-degree-input', 'disabled'),
    [Input('support vector classification-kernel-dropdown', 'value')]
)
def allow_degree_specification(value):
    return value.lower() != 'poly'


@app.callback(
    Output('support vector classification-coef0-input', 'disabled'),
    [Input('support vector classification-kernel-dropdown', 'value')]
)
def allow_coef0_specification(value):
    return value.lower() not in {'poly', 'sigmoid'}


@app.callback(
    Output('cross_validation_repeats-input', 'disabled'),
    [Input('cross_validation_method-dropdown', 'value')]
)
def allow_repeats_specification(value):
    if value.lower() in {'repeated k fold', 'repeated stratified k fold'}:
        return False
    return True


@app.callback(
    Output('train_model-output', 'children'),
    [i[1] for i in ALGO_CALLBACK_INPUTS[:5]] +
    [Input('train_model-confirm', 'submit_n_clicks')] +
    [Input('model_name-input', 'value')] +
    [Input('stored_data-upload', 'children')] +
    [Input('algorithm_selection-dropdown', 'value')]
)
def train_model(*args):
    button_click = args[-4]
    if button_click:
        name, data = utils.unjson_df(args[-2][0])
        selected_algo = args[-1]
        model_name = args[-3]
        sk_params = {sk_param[0].split('-')[1]: value for sk_param, value in
                     zip(ALGO_CALLBACK_INPUTS, args[:-4])}
        print(sk_params)
        m = model.Model(model_name, selected_algo, name)
        np_data = data.to_numpy()
        features = np_data[:, :-1]
        target = np_data[::, -1]
        m.train(features, target, **sk_params)
        print(m)
        return [model.pickle(m)]


@app.callback(
    Output('scale-container', 'children'),
    [Input('add_scale-button', 'n_clicks'),
     Input('stored_data-upload', 'children')]
)
def add_sliders(n_clicks, data):
    if n_clicks:
        name, df = utils.unjson_df(data[0])
        return html.Div(
            style=utils.generate_flex_style(),
            children=[
                html.Div(
                    style=utils.generate_flex_style(direction='column',
                                                    max_width='50%',
                                                    ),
                    children=[html.H6('Scale')] +
                             [utils.generate_dropdown(
                                 f'scale_feature-dropdown-{i}',
                                 list(df.columns.values),
                                 multi=True,
                                 max_width='100%') for i in range(n_clicks)
                              ]),
                html.Div(
                    style=utils.generate_flex_style(direction='column',
                                                    min_width='50%'),
                    children=[html.H6('Method')] +
                             [utils.generate_dropdown(
                                 f'scale_method-dropdown-{i}',
                                 ['normalize', 'min-max', 'max-abs', 'standard',
                                  'robust'], max_width='100%')
                                 for i in range(n_clicks)
                              ])
            ])


for i in range(10):
    @app.callback([Output(f'scale_feature-dropdown-{i}', 'children'),
                   Output(f'scale_method-dropdown-{i}', 'children')],
                  [Input(f'scale_feature-dropdown-{i}', 'value'),
                   Input(f'scale_method-dropdown-{i}', 'value')]
                  )
    def update_output(feature_dropdown, method_dropdown):
        return feature_dropdown, method_dropdown

'''
@app.callback(
    Output('data_output-upload', 'data'),
    [Input('data_output-upload', 'sort_by'),
     Input('data_output-upload', 'filter_query')]
)
def update_sort_filter_table(sort_by, filter_query):
    expressions = filter_query.split(' && ')
'''

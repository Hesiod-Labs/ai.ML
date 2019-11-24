import dash_html_components as html
from dash.dependencies import Input, Output, State
import dash_core_components as dcc

from app import app
from build_parameters import PARAMETERS
import utils
from dataset.dataset import Element, Feature, Dataset

MOCK_DS = Dataset(
    [Feature([Element(i * j) for i in range(10)]) for j in range(5)]
)


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
    Output('hyperparameters-container', 'children'),
    [Input('algorithm_selection-dropdown', 'value')]
)
def update_hyperparameters_container(value):
    return [html.H4('Hyperparameters', style={'fontWeight': 'bold'})] + \
           utils.generate_widget(value)


@app.callback(
    Output('data_output-upload', 'children'),
    [Input('data-upload', 'contents')],
    [State('data-upload', 'filename')]
)
def update_output(content, name):
    if content:
        return [utils.parse_contents(content, name)]


@app.callback(
    Output('cross_validation_repeats-input', 'disabled'),
    [Input('cross_validation_method-dropdown', 'value')]
)
def allow_repeats_specification(value):
    if value.lower() in {'repeated k fold', 'repeated stratified k fold'}:
        return False
    return True


'''
@app.callback(
    Output('scale-container', 'children'),
    [Input('add_scale-button', 'n_clicks')]
)
def add_sliders(n_clicks):
    return html.Div(
        [html.Div([
            html.Div(dcc.Slider(id='slider-{}'.format(i))),
            html.Div(id='output-{}'.format(i), style={'marginTop': 30})
        ]) for i in range(n_clicks)]
    )


for i in range(MOCK_DS.n_features()):
    @app.callback(Output('slider-{}'.format(i), 'children'),
                  [Input('slider-{}'.format(i), 'value')])
    def update_additional_center(slider_i_value):
        return slider_i_value

for i in range(10):
    @app.callback(Output(f'scale-{i}-container', 'children'),
                  [Input(f'scale_feature-dropdown-{i}', 'value'),
                   Input(f'scale_method-dropdown-{i}', 'value')]
                  )
    def update_output(feature_dropdown, method_dropdown):
        return scale_children

@app.callback(
    Output('data_output-upload', 'data'),
    [Input('data_output-upload', 'sort_by'),
     Input('data_output-upload', 'filter_query')]
)
def update_sort_filter_table(sort_by, filter_query):
    expressions = filter_query.split(' && ')
'''
import dash_html_components as html
from dash.dependencies import Input, Output, State

from app import app
from build_parameters import PARAMETERS
import utils


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
    Output('algorithm_parameters', 'children'),
    [Input('algorithm_selection', 'value')]
)
def update_hyperparameter_container(value):
    return utils.generate_widget(value)


@app.callback(
    Output('data_output-upload', 'children'),
    [Input('data-upload', 'contents')],
    [State('data-upload', 'filename')]
)
def update_output(content, name):
    if content:
        return [utils.parse_contents(content, name)]


model_output = html.Div(id='model_output', hidden=True)

# TODO If the dictionary approach works, delete this section
'''
algo_callback_inputs = {
    algo: [Input(f'{algo}-{param}-{meta["widget"]}', 'value')
           for param, meta in PARAMETERS[algo].items()]
    for algo in PARAMETERS.keys()
}


@app.callback(
    Output('model_output', 'children'),
    algo_callback_inputs['logistic regression']

)
def train_logistic_regression(
        solver, penalty, l1_ratio, dual, tol, C, fit_intercept,
        intercept_scaling, max_iter
):
    pass


@app.callback(
    Output('model_output', 'children'),
    algo_callback_inputs['support vector classification']
)
def train_support_vector_classification(
        kernel, C, degree, gamma, coef0, shrinking, tol, max_iter
):
    pass


@app.callback(
    Output('model_output', 'children'),
    algo_callback_inputs['k nearest neighbors']
)
def train_k_nearest_neighbors(
        algorithm, weights, metric, p, n_neighbors, leaf_size
):
    pass


@app.callback(
    Output('model_output', 'children'),
    algo_callback_inputs['decision tree classification']
)
def train_decision_tree_classification(
        criterion, splitter, max_features, max_depth, min_samples_split,
        min_samples_leaf, min_weight_fraction_leaf, min_leaf_nodes,
        min_impurity_decrease
):
    pass


@app.callback(
    Output('model_output', 'children'),
    algo_callback_inputs['linear discriminant analysis']
)
def train_linear_discriminant_analysis(solver, shrinkage, n_components, tol):
    pass
'''


@app.callback(
    Output('data_output-upload', 'data'),
    [Input('data_output-upload', 'sort_by'),
     Input('data_output-upload', 'filter_query')]
)
def update_sort_filter_table(sort_by, filter_query):
    expressions = filter_query.split(' && ')

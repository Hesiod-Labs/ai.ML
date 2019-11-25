import base64
import io

import dash_html_components as html
from dash.dependencies import Input, Output, State
from pymongo import MongoClient

import pandas as pd

from model import Model
from run import app
from .build_parameters import PARAMETERS
from . import utils
from dataset.dataset import Element, Feature, Dataset

client = MongoClient("mongodb+srv://hlabs_1:thinkBox@aiml-thzu0.mongodb.net/test?retryWrites=true&w=majority")
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
    [Input('k nearest neighbors-n_neighbors-dropdown', 'value')]
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
    Output('stored_data-upload', 'children'),
    [Input('data-upload', 'contents')],
    [State('data-upload', 'filename')]
)
def jsonify_data(file, filename):
    db = client['aiML']
    try:
        if file and filename:
            content_type, content_string = file.split(',')
            decoded = base64.b64decode(content_string)
            if 'csv' in filename:
                df = pd.read_csv(io.StringIO(decoded.decode('utf-8')))
                for key in df:
                    new_key = key.replace(".", "")
                    df[new_key] = df.pop(key)
                stored_data = df.to_dict(orient='records')
                collection_name = os.path.splitext(filename)[0]
                collection = db[f'{collection_name}']
                collection.insert_many(stored_data)
                client.close()
                return [df.to_json()]
    except Exception as e:
        print(e)
        return html.Div(['There was an error processing this file.'])


@app.callback(
    Output('data_output-upload', 'children'),
    [Input('stored_data-upload', 'children')]
)
def update_dataset_output(json_data):
    if json_data:
        data = pd.read_json(json_data[0])
        return [html.Div([
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


@app.callback(
    Output('cross_validation_repeats-input', 'disabled'),
    [Input('cross_validation_method-dropdown', 'value')]
)
def allow_repeats_specification(value):
    if value.lower() in {'repeated k fold', 'repeated stratified k fold'}:
        return False
    return True


ALGO_CALLBACK_INPUTS = {
    algo: [Input(f'{algo}-{param}-{meta["widget"]}', 'value')
           for param, meta in PARAMETERS[algo].items()]
    for algo in PARAMETERS.keys()
}


# TODO model_id, dataset_id, X, y parameters
# dataset_id not needed if X can be train data and y can be labels
# model id needed for database recording, if not stored then not needed


@app.callback(
    Output('logistic regression-output', 'children'),
    ALGO_CALLBACK_INPUTS['logistic regression'] +
    [Input('model_name-input', 'value')] +
    [Input('stored_data-upload', 'children')] +
    [Input('train_model-confirm', 'submit_n_clicks')] +
    [Input('algorithm_selection-dropdown', 'value')]
)
def train_logistic_regression(
        solver, penalty, l1_ratio, dual, tol, C, fit_intercept,
        intercept_scaling, max_iter, model_name, uploaded, button_click, algo
):
    if button_click:
        if l1_ratio == 0 and penalty != 'elasticnet':
            l1_ratio = None
        params = {'solver': solver, 'penalty': penalty, 'l1_ratio': l1_ratio,
                  'dual': dual, 'tol': tol, 'C': C,
                  'fit_intercept': fit_intercept,
                  'intercept_scaling': intercept_scaling, 'max_iter': max_iter}
        model_id = '1'
        dataset_id = '1'
        data = pd.read_json(uploaded[0]).to_numpy()
        X = data[:, :-1]
        y = data[::, -1]
        model = Model(model_name=model_name, model_type='LGR', params=params,
                      model_id=model_id, dataset_id=dataset_id, X=X, y=y)
        model.train()
        return [model.picklize()]

'''
@app.callback(
    Output('support vector classification-output', 'children'),
    ALGO_CALLBACK_INPUTS['support vector classification'] +
    [Input('model_name-input', 'value')] +
    [Input('stored_data-upload', 'children')] +
    [Input('train_model-confirm', 'submit_n_clicks')]
)
def train_support_vector_classification(
        kernel, C, degree, gamma, coef0, shrinking, tol, max_iter, model_name,
        uploaded, button_click
):
    params = {'kernel': kernel, 'C': C, 'degree': degree, 'gamma': gamma,
              'coef0': coef0, 'shrinking': shrinking,
              'tol': tol, 'max_iter': max_iter}
    model_id = '1'
    dataset_id = '1'
    data = pd.read_json(uploaded[0]).to_numpy()
    X = data[:, :-1]
    y = data[::, -1]
    model = Model(model_name=model_name, model_type='SVC', params=params,
                  model_id=model_id, dataset_id=dataset_id,
                  X=X, y=y)
    return [model.picklize()]
@app.callback(
    Output('k nearest neighbors', 'children'),
    ALGO_CALLBACK_INPUTS['k nearest neighbors'] +
    [Input('model_name-input', 'value')]
)
def train_k_nearest_neighbors(
        algorithm, weights, metric, p, n_neighbors, leaf_size, model_name
):
    params = {'algorithm': algorithm, 'weights': weights, 'metric': metric,
              'p': p, 'n_neighbors': n_neighbors,
              'leaf_size': leaf_size}
    model_id = '1'
    dataset_id = '1'
    X = []
    y = []
    model = Model(model_name=model_name, model_type='KNN', params=params,
                  model_id=model_id, dataset_id=dataset_id,
                  X=X, y=y)
    return [model.picklize()]
@app.callback(
    Output('decision tree classification', 'children'),
    ALGO_CALLBACK_INPUTS['decision tree classification'] +
    [Input('model_name-input', 'value')]
)
def train_decision_tree_classification(
        criterion, splitter, max_features, max_depth, min_samples_split,
        min_samples_leaf, min_weight_fraction_leaf, min_leaf_nodes,
        min_impurity_decrease, model_name
):
    params = {'criterion': criterion, 'splitter': splitter,
              'max_features': max_features, 'max_depth': max_depth,
              'min_samples_split': min_samples_split,
              'min_samples_leaf': min_samples_leaf,
              'min_weight_fraction_leaf': min_weight_fraction_leaf,
              'min_leaf_nodes': min_leaf_nodes,
              'min_impurity_decrease': min_impurity_decrease}
    model_id = '1'
    dataset_id = '1'
    X = []
    y = []
    model = Model(model_name=model_name, model_type='DTC', params=params,
                  model_id=model_id, dataset_id=dataset_id,
                  X=X, y=y)
    return [model.picklize()]
@app.callback(
    Output('linear discriminant analysis', 'children'),
    ALGO_CALLBACK_INPUTS['linear discriminant analysis'] +
    [Input('model_name-input', 'value')]
)
def train_linear_discriminant_analysis(solver, shrinkage, n_components, tol,
                                       model_name):
    params = {'solver': solver, 'shrinkage': shrinkage,
              'n_components': n_components, 'tol': tol}
    model_id = '1'
    dataset_id = '1'
    X = []
    y = []
    model = Model(model_name=model_name, model_type='LDA', params=params,
                  model_id=model_id, dataset_id=dataset_id,
                  X=X, y=y)
    return [model.picklize()]
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
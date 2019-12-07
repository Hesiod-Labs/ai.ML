import base64
import io
import os
from typing import List

import dash_html_components as html
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import pandas as pd
import plotly.graph_objs as go
import plotly.express as px
from pymongo import MongoClient

from model import model
from run import app
from .build_parameters import PARAMETERS
from . import utils

"""All callback functions for Dash."""

# Connection String to MongoDB Atlas
CLIENT = MongoClient("mongodb+srv://hlabs_1:thinkBox@aiml-thzu0.mongodb.net"
                     "/test?retryWrites=true&w=majority")
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
def json_data(file, filename: str) -> List:
    """Dash callback that uploads, decodes, and stores the dataset uploaded
    by the user.

    Given a .csv file, the file is decoded using pandas built-in functions,
    stored in the MongoDB database and in an HTML hidden div for training the
    model.

    Args:
        file: The .csv file uploaded by the user.
        filename: The name of the .csv file.

    Raises:
        Generic Exception if an error occurs during the process of uploading
        and storing the .csv in either the MongoDB or the hidden div.

    Returns:
        If an exception occurs: a dash_html_components.html.Div() containing
            an error message.
        Otherwise: a list containing the JSON version of the .csv.

    """
    db = CLIENT['aiML']  # Connects to ai.ML database
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
                # Names database collection after filename
                collection_name = os.path.splitext(filename)[0]
                collection = db[f'{collection_name}']
                collection.insert_many(stored_data)
                CLIENT.close()
                return [utils.json_df(utils.format_dataset_name(filename), df)]
    except Exception as e:
        print(e)
        return [html.Div(['There was an error processing this file.'])]


@app.callback(
    Output('data_output-upload', 'children'),
    [Input('stored_data-upload', 'children')]
)
def update_dataset_output(jsoned_data):
    """Dash callback that updates the Dataset page layout.

    Given a file has been uploaded successfully, update the Dataset page to
    contain a descriptive statistics table and a dataset table to view the data.

    Args:
        jsoned_data: JSON version of the dataset file.

    Returns:
        A list containing the HTML Div children to be populate the HTML Div
        on the Dataset page.
    """
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
    """Dash callback for updating the HTML div containing all algorithm
    parameter Dash core components.

    Given an algorithm is selected from the algorithm dropdown, the HTML div
    will be updated to include all the available parameters that can be
    edited by the user.

    Args:
        value: Algorithm selected in the dropdown.

    Returns:
        A list containing the HTML header and Dash core components to
        populate the children attribute of the HTML div for container the
        algorithm parameter widgets.
    """
    return [html.H4('Hyperparameters', style={'fontWeight': 'bold'})] + \
           utils.generate_widget(value)


@app.callback(
    Output('logistic regression-penalty-dropdown', 'options'),
    [Input('logistic regression-solver-dropdown', 'value')]
)
def filter_available_logistic_regression_penalty(value):
    """Dash callback for filtering the logistic regression penalty dropdown.

    Given a specified solver for logistic regression, the valid options
    for logistic regression penalty are filtered and used in the Dash
    core component dropdown.

    Args:
        value: Selected logistic regression solver from dropdown.

    Returns:
        A list of supported penalties for the given logistic regression
        solver that populate the penalties dropdown.
    """
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
    """Dash callback for filtering the logistic regression solver dropdown.

    Given a specified penalty for logistic regression, the valid
    options for logistic regression solver are filtered and used in
    the Dash core component dropdown.

    Args:
        value: Selected logistic regression penalty from dropdown.

    Returns:
        A list of supported solvers for the given logistic regression
        penalty that populate the solver dropdown.
    """
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
    """Dash callback for enabling/disabling the L1 ratio input widget.

    Given a specified solver for logistic regression, the valid options
    for logistic regression penalty are filtered and used in the Dash
    core component dropdown.

    Args:
        value: Selected logistic regression solver from dropdown.

    Returns:
        True if the penalty selected is "elasticnet" and False otherwise.
    """
    return value.lower() != 'elasticnet'


@app.callback(
    Output('k nearest neighbors-p-input', 'disabled'),
    [Input('k nearest neighbors-metric-dropdown', 'value')]
)
def allow_minkowski_specification(value):
    """Dash callback for enabling/disabling the Minkowski distance input
    widget for k nearest neighbors.

    Given a distance metric to use for measuring the distance between
    neighbors in the k nearest neighbors algorithm, only allow user input of
    the Minkowski distance if the metric selected is Minkowski.

    Args:
        value: Selected k nearest neighbors distance metric from dropdown.

    Returns:
        True if the distance metric is not "minkowski" and False otherwise.
    """
    return value.lower() != 'minkowski'


@app.callback(
    Output('support vector classification-degree-input', 'disabled'),
    [Input('support vector classification-kernel-dropdown', 'value')]
)
def allow_degree_specification(value):
    """Dash callback for enabling/disabling the degree input widget for
    support vector classification.

    Given a kernel from the dropdown menu, allow the user to specify a degree
    if the selected kernel is polynomial, "poly." Otherwise, do not the allow
    th user to specify a degree.

    Args:
        value: Selected kernel from the dropdown menu.

    Returns:
        True if the distance metric is not "poly" and False otherwise.
    """
    return value.lower() != 'poly'


@app.callback(
    Output('support vector classification-coef0-input', 'disabled'),
    [Input('support vector classification-kernel-dropdown', 'value')]
)
def allow_coef0_specification(value):
    """Dash callback for enabling/disabling the 0th coefficient input widget for
    support vector classification.

    Given a kernel from the dropdown menu, allow the user to specify a 0th
    coefficient if the selected kernel is polynomial ("poly") or sigmoid.
    Otherwise, do not the allow the user to specify a 0th coefficient.

    Args:
        value: Selected kernel from the dropdown menu.

    Returns:
        True if the kernel is polynomial or sigmoid and False otherwise.
    """
    return value.lower() not in {'poly', 'sigmoid'}


@app.callback(
    Output('cross_validation_repeats-input', 'disabled'),
    [Input('cross_validation_method-dropdown', 'value')]
)
def allow_repeats_specification(value):
    """Dash callback for enabling/disabling the cross validation repeats input
    widget.

    Given a cross validation method from the dropdown, allow the user to
    specify the number of times to repeat the cross validation if the
    selected method is either 'repeated k fold' or 'repeated stratified k fold'.
    Otherwise, do not allow the user to specify the number of repeats.

    Args:
        value: Selected cross validation method from the dropdown menu.

    Returns:
        True if the method is either 'repeated k fold' or 'repeated
        stratified k fold'
    """
    if value.lower() in {'repeated k fold', 'repeated stratified k fold'}:
        return False
    return True


@app.callback(
    Output('train_model-output', 'children'),
    [Input('train_model-confirm', 'submit_n_clicks')] +
    [Input('model_name-input', 'value')] +
    [Input('stored_data-upload', 'children')] +
    [Input('algorithm_selection-dropdown', 'value')] +
    [i[1] for i in ALGO_CALLBACK_INPUTS[:5]]
)
def train_model(*args):
    """Dash callback that trains the model.

    Given the user has uploaded a dataset and clicks the 'Train Model' button,
    the scikit-learn function that trains the specified algorithm is called
    to fit the corresponding Estimator object.

    Args:
        *args:
            - The number of times the 'Train Model' button has been clicked.
            - The name of the model to train.
            = The stored JSON dataset file.
            - The selected algorithm with which to train the model.

    Returns: A list containing a jsonpickle object of the Model class instance.

    """
    button_click = args[0]
    if button_click:
        # Get the dataset file and name.
        name, data = utils.unjson_df(args[2][0])
        selected_algo = args[3]
        model_name = args[1]
        sk_params = {sk_param[0].split('-')[1]: value for sk_param, value in
                     zip(ALGO_CALLBACK_INPUTS, args[5:])}
        # Create a model to train.
        m = model.Model(model_name, selected_algo, name)
        np_data = data.to_numpy()
        features = np_data[:, :-1]
        target = np_data[::, -1]
        # Train the model given the features and target data, as well as all
        # the necessary scikit-learn parameters to fit the Estimator.
        m.train(features, target, **sk_params)
        return [model.pickle(m)]


@app.callback(
    Output('scale-container', 'children'),
    [Input('add_scale-button', 'n_clicks'),
     Input('stored_data-upload', 'children')]
)
def add_sliders(n_clicks, data):
    """Dash callback to add additional scaling dropdowns upon clicking the
    'Add' button.

    Args:
        n_clicks: Number of times the 'Add' button has been clicked.
        data: Uploaded dataset file which is used to allow the user to
            specify which features should be scaled.

    Returns: A dash_html_components.html.Div() whose children is all of the
    scale features and scale methods dropdowns.

    """
    if n_clicks:
        name, df = utils.unjson_df(data[0])
        scale_dropdowns = [html.H6('Scale')] + \
                          [utils.generate_dropdown(
                              f'scale_feature-dropdown-{i}',
                              list(df.columns.values),
                              multi=True,
                              max_width='100%') for i in range(n_clicks)
                          ]

        method_dropdowns = [html.H6('Method')] + \
                           [utils.generate_dropdown(
                               f'scale_method-dropdown-{i}',
                               ['normalize', 'min-max', 'max-abs', 'standard',
                                'robust'], max_width='100%')
                               for i in range(n_clicks)
                           ]
        child_style = utils.generate_flex_style(direction='column',
                                                min_width='50%')
        return [html.Div(
            style=utils.generate_flex_style(),
            children=[
                html.Div(style=child_style, children=scale_dropdowns),
                html.Div(style=child_style, children=method_dropdowns)
            ])]


# Define the Dash callbacks for all of the additional scale dropdowns that
# can be added, but are not initially loaded.
for i in range(10):
    @app.callback([Output(f'scale_feature-dropdown-{i}', 'children'),
                   Output(f'scale_method-dropdown-{i}', 'children')],
                  [Input(f'scale_feature-dropdown-{i}', 'value'),
                   Input(f'scale_method-dropdown-{i}', 'value')]
                  )
    def update_output(feature_dropdown, method_dropdown):
        return feature_dropdown, method_dropdown


# Results page callbacks
@app.callback(Output('results-container', 'children'),
              [Input('train_model-output', 'children'),
               Input('train_model-confirm', 'submit_n_clicks')]
              )
def print_model_results(json_model, button_click):
    """Update the Results page with graphics describing the trained model.

    Given a JSON version of the Model object and the number of times the
    train model confirmation button has been clicked, update the output of
    the Results page to include graphics, such as a scatter plot of the
    dataset, the confusion matrix, and a classification report.

    Args:
        json_model: JSON version of the Model object.
        button_click: Number of times the confirmation button has been clicked.

    Returns:
        A list containing a dash_html_components.Div() object whose children
        is all of the graphics and text output generated from training and
        testing the Model.
    """

    if button_click:
        trained_model = model.unpickle(json_model[0])
        class_report = trained_model.scores['classification report']
        confusion_matrix = trained_model.scores['confusion matrix']
        confusion_matrix_plot = dcc.Graph(
            id='confusion_matrix',
            style={'width': '100%'},
            figure=go.Figure(
                data=go.Heatmap(
                    x=trained_model.classes,
                    y=trained_model.classes,
                    z=confusion_matrix,
                    colorscale='Blues'
                )
            )
        )
        scatter_plot = dcc.Graph(
            id='scatter_plot',
            style={'width': '100%'},
            figure=go.Figure(
                data=px.scatter(
                    px.data.iris(),
                    x='sepal_width',
                    y='sepal_length',
                    color='species',
                    hover_data=['petal_width']
                )
            )
        )
        plots = html.Div(
            style=utils.generate_flex_style(grow='1'),
            children=[
                html.H4('Confusion Matrix'),
                confusion_matrix_plot,
                html.H4('Scatter Plot'),
                scatter_plot
            ]
        )

        return [html.Div([
            html.H2(trained_model.model_id, style={'fontWeight': 'bold'}),
            html.H4('Classification Report'),
            utils.generate_dtable(
                class_report,
                'classification_report-table',
                virtual=False,
                editable=False,
            ),
            html.Br(),
            html.Div(style=utils.generate_flex_style(), children=[plots])
        ])]

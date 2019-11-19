import dash_core_components as dcc
import dash_html_components as html

from aiml_dash.build_parameters import PARAMETERS
from aiml_dash.build_parameters import SCORING_METRICS
import aiml_dash.utils

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

algorithm_selection = html.Div([
    html.Div(
        style={'float': 'left', 'width': '46%', 'padding': '2%'},
        children=[
            html.H4('Algorithm Selection', style={'fontWeight': 'bold'}),
            aiml_dash.utils.generate_dropdown(
                'algorithm_selection',
                list(PARAMETERS.keys()),
            )
        ]),
    html.Div(style={'float': 'right', 'width': '46%', 'padding': '2%'},
             children=[
                 html.H4('Model Name', style={'fontWeight': 'bold'}),
                 dcc.Input(
                     id='model-name',
                     value=f'Unnamed Model ({aiml_dash.utils.NOW})',
                     maxLength=50,
                     style={'display': 'inline-block', 'width': '100%'}
                 ),
             ])
])

algorithm_parameters = html.Div(
    id='algorithm_parameters',
    style={'float': 'left', 'width': '28%', 'padding': '2%'}
)

preproccesing = html.Div(
    id='preprocessing',
    style={'float': 'left', 'width': '30%', 'padding': '2%'},
    children=[
        html.H4('Preprocessing', style={'fontWeight': 'bold'}),
        html.H6('Center'),
        dcc.Dropdown(
            id='center-dropdown',
            options=aiml_dash.utils.generate_options(
                ['A', 'B', 'C', 'All']
            ),
            multi=True
        ),
        html.Br(),
        html.H6('Scale'),
        dcc.Dropdown(
            id='scale-dropdown',
            options=aiml_dash.utils.generate_options(
                ['A', 'B', 'C', 'All']
            ),
            multi=True
        ),
        html.Br(),
        html.H6('Map to Distribution'),
        html.Div(style={'float': 'left', 'width': '50%'},
                 children=[
                     dcc.Dropdown(
                         id='map_to_distribution-dropdown',
                         options=aiml_dash.utils.generate_options(
                             ['Gaussian', 'Poisson']
                         ),
                         multi=False
                     )]),
        html.Div(style={'float': 'right', 'width': '50%'},
                 children=[
                     dcc.Dropdown(
                         id='map_to_distribution2-dropdown',
                         options=aiml_dash.utils.generate_options(
                             ['a', 'b', 'c', 'all']
                         ),
                         multi=True
                     )
                 ])
    ])

model_selection = html.Div(
    id='model_selection',
    style={'float': 'right',
           'width': '30%',
           'padding': '2%'},
    children=[
        html.H4('Model Selection', style={'fontWeight': 'bold'}),
        html.H6('Cross Validation'),
        aiml_dash.utils.generate_dropdown(
            'cross_validation-dropdown',
            ['A', 'B', 'C', 'All'],
            multi=True
        ),
        html.Br(),
        html.Div([
            html.H6('Scoring Metric'),
            aiml_dash.utils.generate_dropdown(
                'scoring_metrics-dropdown',
                SCORING_METRICS['classification'],
                multi=True
            )
        ]),
        html.Br(),
        html.H6('Hyperparameter Tuning Strategy'),
        aiml_dash.utils.generate_dropdown(
            'hyperparameter_tuning_strategy-dropdown',
            ['none', 'grid search', 'random']
        )
    ])

train_model = html.Div(style={'textAlign': 'center'}, children=[
        dcc.ConfirmDialogProvider(
            children=html.Button(id='train-model',
                                 children='Train Model',
                                 n_clicks=0,
                                 style={'fontSize': '125%'}),
            message='Confirm that you want to train the model')
    ])

build_layout = html.Div([
    algorithm_selection,
    algorithm_parameters,
    preproccesing,
    model_selection,
    train_model
])

import dash_core_components as dcc
import dash_html_components as html

from .build_parameters import PARAMETERS, SCORING_METRICS
from . import utils

dataset_layout = html.Div(
    style={'margin': '2%'},
    children=[
        dcc.Upload(
            id='data-upload',
            children=html.Div(['Drag and Drop or ', html.A('Select Files')]),
            style={
                'width': '100%',
                'height': '60px',
                'lineHeight': '60px',
                'borderWidth': '1px',
                'borderStyle': 'dashed',
                'borderRadius': '5px',
                'textAlign': 'center'
            },
            multiple=False
        ),
        html.Div(
            id='data_output-upload',
            style={'padding': '2%'}
        ),
    ])

algorithm_selection = html.Div(
    id='algorithm_selection-container',
    style=utils.generate_flex_style(grow='1', padding='1%'),
    children=[
        html.H4('Algorithm Selection', style={'fontWeight': 'bold'}),
        utils.generate_dropdown(
            'algorithm_selection-dropdown',
            list(PARAMETERS.keys()),
            width='100%'
        )
    ])

model_name = html.Div(
    id='model_name-container',
    style=utils.generate_flex_style(grow='1', padding='1%'),
    children=[
        html.H4('Model Name', style={'fontWeight': 'bold'}),
        dcc.Input(
            id='model_name-input',
            value=f'Unnamed Model ({utils.NOW})',
            maxLength=50,
            style={'width': '100%'}
        )
    ])

selection_and_name = html.Div(
    id='algorithm_selection_model_name-container',
    style=utils.generate_flex_style(),
    children=[algorithm_selection, model_name]
)

hyperparameters = html.Div(
    id='hyperparameters-container',
    style=utils.generate_flex_style(
        grow='1',
        direction='column',
        padding='1%',
        min_width='10%',
        max_width='25%'
    ),
    children=[html.H4('Hyperparameters', style={'fontWeight': 'bold'})]
)

center_feature = html.Div(
    id='center_feature-container',
    style=utils.generate_flex_style(grow='1'),
    children=[
        html.H6('Center'),
        utils.generate_dropdown('center_feature-dropdown', ['a', 'b', 'c'],
                                multi=True, width='100%')
    ]
)

center_value = html.Div(
    id='center_value-container',
    style=utils.generate_flex_style(grow='1'),
    children=[
        html.H6('Value'),
        dcc.Input(
            id='center_value-input',
            value=0,
            style={'width': '100%', 'textAlign': 'center'},
            type='number'
        )
    ]
)

center = html.Div(
    id='center-container',
    style=utils.generate_flex_style(),
    children=[center_feature, center_value]
)

scale_feature = html.Div(
    id='scale_feature-container',
    style=utils.generate_flex_style(grow='1'),
    children=[
        html.H6('Scale'),
        utils.generate_dropdown('scale_feature-dropdown', ['a', 'b', 'c'],
                                multi=True, width='100%')
    ]
)

scale_method = html.Div(
    id='scale_method-container',
    style=utils.generate_flex_style(grow='1'),
    children=[
        html.H6('Method'),
        utils.generate_dropdown(
            'scale_method-dropdown',
            ['a', 'b', 'c'],
            width='100%'
        )
    ]
)

add_scale = html.Div(
    id='add_scale-container',
    style=utils.generate_flex_style(),
    children=[
        html.Button(id='add_scale-button',
                    children='Add',
                    n_clicks=0,
                    style={'fontSize': '100%'}
                    )
    ])

scale = html.Div(
    id='scale-container',
    style=utils.generate_flex_style(),
    children=[scale_feature, scale_method]
)

preprocessing = html.Div(
    id='preprocessing-container',
    style=utils.generate_flex_style(
        direction='column',
        grow='2',
        padding='1%',
        min_width='10%',
        max_width='30%'),
    children=[
        html.H4('Preprocessing', style={'fontWeight': 'bold'}),
        center,
        scale,
        add_scale,
        dcc.Input(style={'display': 'none'})
    ])

cv_method = html.Div(
    id='cross_validation_method-container',
    style=utils.generate_flex_style(grow='1'),
    children=[
        html.H6('Cross Validation'),
        utils.generate_dropdown(
            'cross_validation_method-dropdown',
            [
                'k fold',
                'repeated k fold',
                'stratified k fold',
                'repeated stratified k fold',
                'leave one out'
            ],
            width='100%'
        )
    ])

cv_folds = html.Div(
    id='cross_validation_folds-container',
    style=utils.generate_flex_style(shrink='2'),
    children=[
        html.H6('Folds'),
        dcc.Input(
            id='cross_validation_folds-input',
            min=2,
            step=1,
            type='number',
            style={'textAlign': 'center', 'width': '100%'}
        )
    ])

cv_repeats = html.Div(
    id='cross_validation_repeats-container',
    style=utils.generate_flex_style(shrink='2'),
    children=[
        html.H6('Repeats'),
        dcc.Input(
            id='cross_validation_repeats-input',
            min=0,
            step=1,
            type='number',
            style={'textAlign': 'center', 'width': '100%'}
        )
    ])

cross_validation = html.Div(
    id='cross_validation-container',
    style=utils.generate_flex_style(),
    children=[cv_method, cv_folds, cv_repeats]
)

scoring_metric = html.Div(
    id='scoring_metric-container',
    style=utils.generate_flex_style(),
    children=[
        html.H6('Scoring Metrics'),
        utils.generate_dropdown(
            'scoring_metrics-dropdown',
            SCORING_METRICS['classification'],
            multi=True,
            width='100%'
        )
    ])

tuning_strategy = html.Div(
    id='_tuning_strategy-container',
    style=utils.generate_flex_style(),
    children=[
        html.H6('Hyperparameter Tuning Strategy'),
        utils.generate_dropdown(
            'hyperparameter_tuning_strategy-dropdown',
            ['none', 'grid search', 'random'],
            width='100%'
        )
    ])

train_model = html.Div(style={'textAlign': 'left'}, children=[
    dcc.ConfirmDialogProvider(
        id='train_model-confirm',
        children=html.Button(id='train_model-button',
                             children='Train Model',
                             n_clicks=0,
                             style={'fontSize': '100%'}),
        message='Confirm that you want to train the model')
])

model_selection = html.Div(
    id='model_selection-container',
    style=utils.generate_flex_style(
        direction='column',
        grow='2',
        padding='1%',
        min_width='10%',
        max_width='45%'),
    children=[
        html.H4('Model Selection', style={'fontWeight': 'bold'}),
        cross_validation,
        scoring_metric,
        tuning_strategy,
        train_model
    ])

params_preprocess_selection = html.Div(
    id='params_preprocess_selection-container',
    style=utils.generate_flex_style(alignment='flex-start'),
    children=[hyperparameters, preprocessing, model_selection]
)

build_layout = html.Div([
    html.Div(id='stored_data-upload', hidden=True),
    html.Div(id='logistic regression-output', hidden=True),
    html.Div(id='support vector classification-output', hidden=True),
    html.Div(id='linear discriminant analysis-output', hidden=True),
    html.Div(id='k nearest neighbors-output', hidden=True),
    html.Div(id='decision tree classification-output', hidden=True),
    selection_and_name,
    params_preprocess_selection,

])

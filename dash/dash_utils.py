import base64
import io
from typing import Union, List, Dict
from datetime import datetime

import dash_core_components as dcc
import dash_html_components as html
import dash_table
import dash_daq as daq

import pandas as pd

from build_parameters import PARAMETERS

NOW = datetime.strftime(datetime.now(), "%Y%m%d%H%M%S")


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
        html.Div([generate_dtable(
            df.describe(),
            'descriptive',
            virtual=False)]),
        html.Br(),
        html.H6('Dataset'),
        html.Div([generate_dtable(df, table_id='dataset')]),
    ])


def generate_options(options: Union[List, Dict]):
    if isinstance(options, List):
        return [
            {'label': str.title(o),
             'value': str.lower(o)} for o in options
        ]
    if isinstance(options, Dict):
        return [
            {'label': l['label'].title(),
             'value': v.lower()} for v, l in options.items()
        ]


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


def generate_slider(sl_id: str, attrs: Dict):
    slider = dcc.Slider(
        id=sl_id,
        min=attrs['options']['min'],
        max=attrs['options']['max'],
        value=attrs['default'],
        step=attrs['options']['step'],
        tooltip={'always_visible': False}
    )
    if 'marks' in attrs['options']:
        slider.marks = attrs['options']['marks']
    return slider


def generate_input(
        in_id: str,
        attrs: Dict,
        alignment='center',
        input_type='number',
        max_length=None):
    return dcc.Input(
        id=in_id,
        min=attrs['options']['min'],
        max=attrs['options']['max'],
        maxLength=max_length if max_length else None,
        value=attrs['default'],
        step=attrs['options']['step'],
        style={'textAlign': alignment},
        type=input_type
    )


def generate_switch(sw_id: str, attrs: Dict):
    return daq.BooleanSwitch(id=sw_id, on=attrs['default'])


def generate_dropdown(dd_id: str, attrs: Union[List, Dict], multi=False):
    print(dd_id, type(attrs))
    if isinstance(attrs, List):
        return dcc.Dropdown(
            id=dd_id,
            options=generate_options(attrs),
            value=attrs[0],
            multi=multi
        )
    if isinstance(attrs, Dict):
        return dcc.Dropdown(
            id=dd_id,
            options=generate_options(attrs['options']),
            value=attrs['default'],
            multi=multi
        )


def generate_widget(algo_name):
    name = algo_name.lower()
    algo = PARAMETERS[name]
    widgets = []
    options = {
        'slider': generate_slider,
        'dropdown': generate_dropdown,
        'switch': generate_switch,
        'input': generate_input
    }

    for param, meta in algo.items():
        widget_type = meta['widget']
        widget_id = f'{name}-{param}-{widget_type}'

        w = html.Div(id=f'{widget_id}-container', children=[
            html.H6(meta['label'].title()),
            options[widget_type](widget_id, meta)
        ])

        widgets.append(w)
    return widgets

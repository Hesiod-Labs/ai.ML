import json
from typing import Union, List, Dict
from datetime import datetime

import dash_core_components as dcc
import dash_html_components as html
import dash_table
import dash_daq as daq

import pandas as pd

from build_parameters import PARAMETERS

NOW = datetime.strftime(datetime.now(), "%Y%m%d%H%M%S")


def json_df(name: str, dataframe: pd.DataFrame):
    return json.dumps({'name': name, 'data': dataframe.to_json()})


def unjson_df(df_json: str):
    df_dict = json.loads(df_json)
    return df_dict['name'], pd.read_json(df_dict['data'])


def format_dataset_name(filename: str):
    name = str.split(filename, '.')[0]
    specials = ['_', '-', '~']
    for s in specials:
        if s in name:
            name = name.replace(s, ' ')
    return name.title()


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


def split_filter_query(query):
    operators = [
        ['ge ', '>='],
        ['le ', '<='],
        ['lt ', '<'],
        ['gt ', '>'],
        ['ne ', '!='],
        ['eq ', '='],
        ['contains '],
        ['datestartswith ']
    ]
    for op_type in operators:
        for op in op_type:
            if op in query:
                name, value = query.split(op, 1)
                name = name[name.find('{') + 1: name.rfind('}')]
                value = value.strip()
                v0 = value[0]
                if v0 == value[-1] and v0 in {"'", '"', '`'}:
                    value = value[1: -1].replace('\\' + v0, v0)
                else:
                    try:
                        value = float(value)
                    except ValueError as e:
                        print(e)
                return name, op_type[0].strip(), value
    return [None] * 3


def generate_dtable(
        df,
        table_id: str,
        hide_cols=True,
        rename_cols=True,
        delete_cols=False,
        virtual=True,
        editable=True
):
    df = pd.DataFrame(df)
    df[''] = df.index
    df.columns = [c.replace('_', ' ').title() for c in df.columns]
    return dash_table.DataTable(
        id=table_id,
        columns=[
            {'name': col.title(),
             'id': col,
             'deletable': delete_cols,
             'hideable': hide_cols,
             'renamable': rename_cols} for col in df.columns
        ],
        # row_selectable='multi',
        data=df.to_dict('records'),
        virtualization=virtual,
        editable=editable,
        filter_action='custom',
        filter_query='',
        sort_action='custom',
        sort_mode='multi',
        sort_by=[],
        #style_table={'overflowX': 'scroll'},
        style_data_conditional=[
            {
                'if': {'row_index': 'odd'},
                'backgroundColor': 'rgb(248, 248, 248)'
            }
        ],
        #style_data={
        #    'whiteSpace': 'normal',
        #    'height': 'auto'
        #},
        style_header={
            'textAlign': 'center',
            'padding': '2px',
            'backgroundColor': 'rgb(230, 230, 230)',
            'fontWeight': 'bold',
            'fontSize': '12pt',
        },
        style_cell={
            'padding': '2px',
            'fontSize': '12pt',
            'textAlign': 'center'
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
        style={'textAlign': alignment, 'width': '100%'},
        type=input_type
    )


def generate_switch(sw_id: str, attrs: Dict):
    return daq.BooleanSwitch(id=sw_id, on=attrs['default'])


def convert_underscore_to_dash(kwargs: Dict):
    formatted = kwargs.copy()
    for k, v in kwargs.items():
        if '_' in k:
            formatted.pop(k)
            formatted[k.replace('_', '-')] = v
    return formatted


def generate_dropdown(dd_id: str, attrs: Union[List, Dict], multi=False,
                      **style):
    formatted_style = convert_underscore_to_dash(style)

    if isinstance(attrs, List):
        return dcc.Dropdown(
            id=dd_id,
            options=generate_options(attrs),
            value=attrs[0],
            multi=multi,
            style=formatted_style
        )
    if isinstance(attrs, Dict):
        return dcc.Dropdown(
            id=dd_id,
            options=generate_options(attrs['options']),
            value=attrs['default'],
            multi=multi,
            style=formatted_style
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


def generate_flex_style(direction='row', wrap=True, justify='left',
                        alignment='stretch', grow='0', **kwargs):
    formatted_style = convert_underscore_to_dash(kwargs)

    params = {
        'display': 'flex',
        'flex-direction': direction,
        'flex-wrap': 'wrap' if wrap else '',
        'justify-content': justify,
        'align-items': alignment,
        'flex-grow': grow,
    }
    return {**params, **formatted_style}

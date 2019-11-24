import base64
import io
import json
import os
from datetime import datetime
from typing import Dict, List, Union

import pandas as pd
from bson.objectid import ObjectId
from flask import (Flask, flash, redirect, render_template, request, session,
                   url_for)
from pandas.io.json import json_normalize
from pymongo import MongoClient

import dash
import dash_core_components as dcc
import dash_daq as daq
import dash_html_components as html
import dash_table
from dash.dependencies import Input, Output, State
from dataset.dataset import Dataset, Element, Feature
from model import Model

"""Connections instantiated to Flask, MongoDB, and Plotly"""

server = Flask(__name__)
server.secret_key = os.urandom(24)
client = MongoClient("mongodb+srv://hlabs_1:thinkBox@aiml-thzu0.mongodb.net/test?retryWrites=true&w=majority")
df = pd.DataFrame()

app = dash.Dash(__name__,
                server=server,
                external_stylesheets=['https://codepen.io/chriddyp/pen/bWLwgP.css'],
                routes_pathname_prefix='/dash/')
app.config.suppress_callback_exceptions = True

"""Parameters to be used heavily in Dash pages"""

NOW = datetime.strftime(datetime.now(), "%Y%m%d%H%M%S")

MOCK_DS = Dataset(
    [Feature([Element(i * j) for i in range(10)]) for j in range(5)]
)

SCORING_METRICS = {
    'classification': {
        'default': 'accuracy',
        'options': {
            'accuracy': {'label': 'accuracy'},
            'balanced_accuracy': {'label': 'balanced accuracy'},
            'brier_score_loss': {'label': 'brier score loss'},
            'f1': {'label': 'f1 (no averaging)'},
            'f1_micro': {'label': 'f1 (micro averaging)'},
            'f1_macro': {'label': 'f1 (macro averaging)'},
            'f1_weighted': {'label': 'f1 (weighted averaging)'},
            'f1_samples': {'label': 'f1 (samples averaging)'},
            'precision': {'label': 'precision (no averaging)'},
            'precision_micro': {'label': 'precision (micro averaging)'},
            'precision_macro': {'label': 'precision (macro averaging)'},
            'precision_weighted': {'label': 'precision (weighted averaging)'},
            'precision_samples': {'label': 'precision (samples averaging)'},
            'recall': {'label': 'precision (no averaging)'},
            'recall_micro': {'label': 'recall (micro averaging)'},
            'recall_macro': {'label': 'recall (macro averaging)'},
            'recall_weighted': {'label': 'recall (weighted averaging)'},
            'recall_samples': {'label': 'recall (samples averaging)'},
            'jaccard': {'label': 'jaccard (no averaging)'},
            'jaccard_micro': {'label': 'jaccard (micro averaging)'},
            'jaccard_macro': {'label': 'jaccard (macro averaging)'},
            'jaccard_weighted': {'label': 'jaccard (weighted averaging)'},
            'jaccard_samples': {'label': 'jaccard (samples averaging)'},
            'roc_auc_score': {'label': 'ROC AUC'}
        }
    }
}

PARAMETERS = {
    'logistic regression': {
        'solver': {
            'label': 'algorithm',
            'widget': 'dropdown',
            'options': {
                'newton-cg': {'label': 'nonlinear conjugate gradient'},
                'lbfgs': {'label': 'limited-memory BFGS'},
                'sag': {'label': 'stochastic average gradient'},
                'saga': {'label': 'stochastic average gradient ameliore'},
                'liblinear': {
                    'label': 'library for large linear classification'}
            },
            'default': 'liblinear'
        },
        'penalty': {
            'label': 'penalty',
            'widget': 'dropdown',
            'options': {
                'l1': {'label': 'l1'},
                'l2': {'label': 'l2'},
                'elasticnet': {'label': 'elastic net'},
                'none': {'label': 'none'}
            },
            'default': 'l2'
        },
        'l1_ratio': {
            'label': 'l1 ratio',
            'widget': 'input',
            'options': {'min': 0,
                        'max': 1,
                        'step': 0.0001,
                        'marks': {0: 'L1', 1: 'L2'}
                        },
            'default': 0
        },
        'dual': {
            'label': 'dual',
            'widget': 'switch',
            'options': (True, False),
            'default': False
        },
        'tol': {
            'label': 'tolerance',
            'widget': 'input',
            'options': {
                'min': 0,
                'max': 100000,
                'step': 0.0001,
                'marks': {0: '0', 100: '100'}
            },
            'default': 0.0001
        },
        'C': {
            'label': 'cost',
            'widget': 'input',
            'options': {
                'min': 0,
                'max': 1000000,
                'step': 0.0001,
                'marks': {0: '0', 1000000: '1000000'}
            },
            'default': 1
        },
        'fit_intercept': {
            'label': 'fit intercept',
            'widget': 'switch',
            'options': (True, False),
            'default': True
        },
        'intercept_scaling': {
            'label': 'intercept scaling',
            'widget': 'input',
            'options': {'min': 0,
                        'max': 1000000,
                        'step': 0.0001,
                        'marks': {0: '0', 1000000: '1000000'}
                        },
            'default': 1
        },
        'max_iter': {
            'label': 'max iterations',
            'widget': 'input',
            'options': {'min': 1,
                        'max': 1000000,
                        'step': 1,
                        'marks': {0: '1', 1000000: '1000000'}
                        },
            'default': 500
        }
    },
    'support vector classification': {
        'kernel': {
            'label': 'kernel',
            'widget': 'dropdown',
            'options': {
                'linear': {'label': 'linear'},
                'poly': {'label': 'polynomial'},
                'rbf': {'label': 'radial basis function'},
                'sigmoid': {'label': 'sigmoid'}
            },
            'default': 'rbf'
        },
        'C': {
            'label': 'cost',
            'widget': 'input',
            'options': {
                'min': 0,
                'max': 1000000,
                'step': 0.0001,
                'marks': {0: '0', 1000000: '1000000'}
            },
            'default': 1
        },
        'degree': {
            'label': 'degree',
            'widget': 'input',
            'options': {
                'min': 0,
                'max': 100,
                'step': 1,
                'marks': {0: '0', 100: '100'}
            },
            'default': 3
        },
        'gamma': {
            'label': 'gamma',
            'widget': 'input',
            'options': {
                'min': 0,
                'max': 1000000,
                'step': 0.0001,
                'marks': {0: '0', 1000000: '1000000'}
            },
            'default': 50  # 'scale'
        },
        'coef0': {
            'label': 'constant coefficient',
            'widget': 'input',
            'options': {
                'min': 0,
                'max': 1000000,
                'step': 0.0001,
                'marks': {0: '0', 1000000: '1000000'}
            },
            'default': 0
        },
        'shrinking': {
            'label': 'shrinking',
            'widget': 'switch',
            'options': (True, False),
            'default': True,
        },
        'tol': {
            'label': 'tolerance',
            'widget': 'input',
            'options': {
                'min': 0,
                'max': 1000000,
                'step': 0.001,
                'marks': {0: '0', 1000000: '1000000'}
            },
            'default': 0.001
        },
        'max_iter': {
            'label': 'max iterations',
            'widget': 'input',
            'options': {
                'min': 1,
                'max': 1000000,
                'step': 1,
                'marks': {0: '1', 1000000: '1000000'}},
            'default': 100,
        }
    },
    'k nearest neighbors': {
        'algorithm': {
            'label': 'algorithm',
            'widget': 'dropdown',
            'options': {
                'auto': {'label': 'auto'},
                'ball_tree': {'label': 'ball tree'},
                'kd_tree': {'label': 'kd tree'},
                'brute': {'label': 'brute force'}
            },
            'default': 'auto'
        },
        'weights': {
            'label': 'weights',
            'widget': 'dropdown',
            'options': {
                'uniform': {'label': 'uniform'},
                'distance': {'label': 'distance'}
            },
            'default': 'uniform',
        },
        'metric': {
            'label': 'distance metric',
            'widget': 'dropdown',
            'options': {
                'euclidian': {'label': 'euclidian'},
                'manhattan': {'label': 'manhattan'},
                'chebyshev': {'label': 'chebyshev'},
                'minkowski': {'label': 'minkowski'}
            },
            'default': 'euclidian'
        },
        'p': {
            'label': 'minkowski power',
            'widget': 'input',
            'options': {
                'min': 0,
                'max': None,
                'step': 0.0001,
            },
            'default': 0
        },
        'n_neighbors': {
            'label': 'number of neighbors',
            'widget': 'input',
            'options': {
                'min': 1,
                'max': 1000000,
                'step': 1,
                'marks': {1: '1', 1000000: '1000000'}
            },
            'default': 5,
        },
        'leaf_size': {
            'label': 'leaf size',
            'widget': 'input',
            'options': {
                'min': 1,
                'max': 1000000,
                'step': 1,
                'marks': {1: '1', 1000000: '1000000'}
            },
            'default': 30
        },
    },
    'decision tree classification': {
        'criterion': {
            'label': 'split criterion',
            'widget': 'dropdown',
            'options': {
                'gini': {'label': 'gini'},
                'entropy': {'label': 'entropy'}
            },
            'default': 'gini'
        },
        'splitter': {
            'label': 'split strategy',
            'widget': 'dropdown',
            'options': {
                'best': {'label': 'best'},
                'random': {'label': 'random'}
            },
            'default': 'best'
        },
        'max_features': {
            'label': 'max features for split',
            'widget': 'dropdown',
            'options': {
                'sqrt': {'label': 'square root'},
                'log2': {'label': 'log (base 2)'},
                'num_features': {'label': 'number of features'},
            },
            'default': 'sqrt'
        },
        'max_depth': {
            'label': 'max depth (0 = no limit)',
            'widget': 'input',
            'options': {
                'min': 0,
                'max': 1000000,
                'step': 1,
                'marks': {0: '0', 1000000: '1000000'}
            },
            'default': 50
        },
        'min_samples_split': {
            'label': 'min samples to split',
            'widget': 'input',
            'options': {
                'min': 1,
                'max': 100,
                'step': 1,
                'marks': {1: '1', 1000000: '1000000'}
            },
            'default': 2
        },
        'min_samples_leaf': {
            'label': 'min samples per leaf',
            'widget': 'input',
            'options': {
                'min': 1,
                'max': 1000000,
                'step': 1,
                'marks': {1: '1', 1000000: '1000000'}
            },
            'default': 5
        },
        'min_weight_fraction_leaf': {
            'label': 'min weight fraction per leaf',
            'widget': 'input',
            'options': {
                'min': 0,
                'max': 1,
                'step': 0.0001,
                'marks': {0: '0', 1: '1'}
            },
            'default': 0.5
        },
        'max_leaf_nodes': {
            'label': 'max leaf nodes (0 = no limit)',
            'widget': 'input',
            'options': {
                'min': -1,
                'max': 1000000,
                'step': 1,
                'marks': {0: '0', 1000000: '1000000'}
            },
            'default': 5
        },
        'min_impurity_decrease': {
            'label': 'min impurity decrease',
            'widget': 'input',
            'options': {
                'min': 0,
                'max': 1000000,
                'step': 0.0001,
                'marks': {0: '0', 1000000: '1000000'}
            },
            'default': 0
        }
    },
    'linear discriminant analysis': {
        'solver': {
            'label': 'solver',
            'widget': 'dropdown',
            'options': {
                'svd': {'label': 'singular value decomposition'},
                'lsqr': {'label': 'least squares solution'},
                'eigen': {'label': 'eigenvalue decomposition'}
            },
            'default': 'svd'
        },
        'shrinkage': {
            'label': 'shrinkage',
            'widget': 'dropdown',
            'options': {
                'fixed': {'label': 'fixed'},
                'auto': {'label': 'Ledoit-Wolf (auto)'}
            },
            'default': 'fixed'
        },
        'n_components': {
            'label': 'number of components',
            'widget': 'input',
            'options': {
                'min': 1,
                'max': 1000000,
                'step': 1,
                'marks': {1: '1', 1000000: '1000000'}
            },
            'default': 5
        },
        'tol': {
            'label': 'tolerance',
            'widget': 'input',
            'options': {
                'min': 0,
                'max': 1000000,
                'step': 0.0001,
                'marks': {0: '1', 1000000: '1000000'}
            },
            'default': 0.0001
        },
    }
}

"""Code for the main server containing login, create account, modify account, delete account, and links to dash"""

# User can login to their account
@server.route('/', methods=['GET', 'POST'])
def start():
    if request.method == "POST":
        db = client['aiML']
        collection = db['users']
        if collection.count_documents({"username":f"{request.form['username']}","password":f"{request.form['password']}"}) == 1:
            user_info = collection.find_one({"username":f"{request.form['username']}"})
            session['id'] = str(user_info['_id'])
            session['email'] = user_info['email']
            session['username'] = user_info['username']
            session['password'] = user_info['password']
            client.close()
            return redirect(url_for('main'))
        else:
            return render_template('start.html', template_error="Could not login: incorrect username or password")
    return render_template('start.html', template_error="")

# User can create an account
@server.route('/createaccount', methods=['GET', 'POST'])
def createaccount():
    db = client['aiML']
    collection = db['users']
    if "email" in request.form and request.method == "POST":
        if request.form['password'] == request.form['retype-password']:
            account_info = {"email":request.form['email'], "username":request.form['username'], "password":request.form['password']}
            for item in account_info:
                session[item] = account_info[item]
                if collection.count_documents({f"{item}":f"{session[item]}"}) > 0:
                    session.pop(item)
                    client.close()
                    return render_template('createaccount.html', template_error = f"Could not create account: {item} is part of another account")
            user_info = {"email":f"{request.form['email']}",
                        "username":f"{request.form['username']}",
                        "password":f"{request.form['password']}"}
            user_id = collection.insert_one(user_info).inserted_id
            session['id'] = str(user_id)
            client.close()
            return redirect(url_for('main'))
        else:
            return render_template('createaccount.html', template_error = "Could not create account: password fields do not match")
    return render_template('createaccount.html', template_error = "")

# Main page containing ai.ML functionality
@server.route('/main', methods=['GET', 'POST'])
def main():
    if not 'id' in session:
        return redirect(url_for('start'))
    return render_template('main.html')

@server.route('/exploredatasets', methods=['GET', 'POST'])
def exploredatasets():
    db = client['aiML']
    data_description = "description_1"
    selected_dataset = ""
    global df
    if not 'id' in session:
        return redirect(url_for('start'))
    if request.method == "POST":
        if "preview-btn" in request.form:
            if request.form.get('selected_dataset', '') == "border_crossing":
                data_description = """The Bureau of Transportation Statistics (BTS) Border Crossing Data provide summary statistics
                                        for inbound crossings at the U.S.-Canada and the U.S.-Mexico border at the port level.
                                        Data are available for trucks, trains, containers, buses, personal vehicles, passengers,
                                        and pedestrians. Border crossing data are collected at ports of entry by U.S. Customs and
                                        Border Protection (CBP). The data reflect the number of vehicles, containers, passengers or
                                        pedestrians entering the United States. CBP does not collect comparable data on outbound crossings.
                                        Users seeking data on outbound counts may therefore want to review data from individual bridge operators,
                                        border state governments, or the Mexican and Canadian governments. (https://www.kaggle.com/akhilv11/border-crossing-entry-data)
                                        Note: Only the first 10 rows and first 10 columns are previewed below
                                    """
            elif request.form.get('selected_dataset', '') == "crime_population":
                data_description = """This data set was extracted from FBI-UCR website for the year 2012 on US cities with population less
                                        than 250,000 people. The following statistics are provided: Population, Violent Crime Total, Murder/Manslaughter,
                                        Forcible Rape, Robbery, Aggravated Assault, Property Crime Total, Burglary, Larceny Theft, Motor Vehicle Theft,
                                        latitude and longitude. (https://www.kaggle.com/mascotinme/population-against-crime)
                                        Note: Only the first 10 rows and first 10 columns are previewed below
                                    """
            elif request.form.get('selected_dataset', '') == "movies":
                data_description = """This data on nearly 7000 films from over the last three decades contains general information on each film (i.e.
                                        director, production company, rating, etc) as well as financial figures for the budget and revenue. All of this data
                                        was scraped from IMBb. (https://www.kaggle.com/danielgrijalvas/movies)
                                        Note: Only the first 10 rows and first 10 columns are previewed below
                                    """
        selected_dataset = request.form.get('selected_dataset', '')
        collection = db[f'{selected_dataset}']
        selected_data = json_normalize(collection.find({}))
        df = selected_data[selected_data.columns[0:9]].head(10)
        client.close()
        if "use-dataset-btn" in request.form:
            return redirect(url_for('build'))
    return render_template('exploredatasets.html', selected_dataset=selected_dataset, description=data_description, tables=[df.to_html(classes='data', header="true", index="false")])

# User can build their model from their chosen dataset
@server.route('/build', methods=['GET', 'POST'])
def build():
    if not 'id' in session:
        return redirect(url_for('start'))
    global df
    return render_template('build.html')

# User can logout from their account
@server.route('/logout', methods=['GET', 'POST'])
def logout():
    if not 'id' in session:
        return redirect(url_for('start'))
    if "returnhome" in request.form:
        if request.form["returnhome"] == "Yes":
            session.pop("username", None)
            session.pop("email", None)
            session.pop("password", None)
            session.pop("id", None)
            return redirect(url_for('start'))
        if request.form["returnhome"] == "No":
            return redirect(url_for('main'))
    return render_template('logout.html')

# User can view basic profile information, update email, username or password, or delete account
@server.route('/profile', methods=['GET', 'POST'])
def profile():
    if not 'id' in session:
        return redirect(url_for('start'))
    return render_template('profile.html', profile = session)

# User can update their email
@server.route('/updateemail', methods=['GET', 'POST'])
def update_email():
    db = client['aiML']
    collection = db['users']
    if not 'id' in session:
        return redirect(url_for('start'))
    if request.method == "GET":
        user_info = collection.find_one({"email":f"{session['email']}"})
        email = user_info['email']
    if request.method == "POST":
        new_email = request.form['new-email']
        if collection.count_documents({"email":f"{request.form['new-email']}"}) > 0:
            return render_template('updateemail.html', template_error = "Could not update email: email is already a part of another account", profile = session)
        collection.update_one({"_id":ObjectId(f"{session['id']}")}, {"$set":{"email":f"{new_email}"}})
        session['email'] = new_email
        client.close()
        return redirect(url_for('profile'))
    return render_template('updateemail.html', template_error = "", profile = session)

# User can update their username
@server.route('/updateusername', methods=['GET', 'POST'])
def update_username():
    db = client['aiML']
    collection = db['users']
    if not 'id' in session:
        return redirect(url_for('start'))
    if request.method == "GET":
        user_info = collection.find_one({"username":f"{session['username']}"})
        username = user_info['username']
    if request.method == "POST":
        new_username = request.form['new-username']
        if collection.count_documents({"username":f"{request.form['new-username']}"}) > 0:
            return render_template('updateusername.html', template_error = "Could not update username: username is already a part of another account", profile = session)
        collection.update_one({"_id":ObjectId(f"{session['id']}")}, {"$set":{"username":f"{new_username}"}})
        session['username'] = new_username
        client.close()
        return redirect(url_for('profile'))
    return render_template('updateusername.html', template_error = "", profile = session)

# User can update their password
@server.route('/updatepassword', methods=['GET', 'POST'])
def update_password():
    db = client['aiML']
    collection = db['users']
    if not 'id' in session:
        return redirect(url_for('start'))
    if request.method == "POST":
        if request.form['new-password'] == request.form['retype-new-password']:
            if collection.count_documents({"password":f"{request.form['old-password']}"}) == 1:
                new_password = request.form['new-password']
                collection.update_one({"_id":ObjectId(f"{session['id']}")}, {"$set":{"password":f"{new_password}"}})
                session['password'] = new_password
                client.close()
                return redirect(url_for('profile'))
            else:
                return render_template('updatepassword.html', template_error = "Could not change password: Incorrect old password")
        else:
            return render_template('updatepassword.html', template_error = "Could not change password: New password fields do not match")
    return render_template('updatepassword.html', template_error = "")

# User can delete an account
@server.route('/deleteaccount', methods=['GET', 'POST'])
def delete_account():
    db = client['aiML']
    collection = db['users']
    if not 'id' in session:
        return redirect(url_for('start'))
    if request.method == "POST":
        if "delete-btn" in request.form:
            collection.delete_one({"_id":ObjectId(f"{session['id']}")})
            client.close()
            return redirect(url_for('start'))
        if "returnhome" in request.form:
            return redirect(url_for('main'))
    return render_template('deleteaccount.html')

"""Utils for Dash"""
def format_dataset_name(filename: str):
    name = str.split(filename, '.')[0]
    specials = ['_', '-', '~']
    for s in specials:
        if s in name:
            name = name.replace(s, ' ')
    return name.title()


def parse_contents(file, filename):
    content_type, content_string = file.split(',')
    decoded = base64.b64decode(content_string)
    db = client['aiML']
    try:
        if 'csv' in filename:
            df = pd.read_csv(io.StringIO(decoded.decode('utf-8')))
            stored_data = df.to_dict(orient='records')
            collection_name = os.path.splitext(filename)[0]
            collection = db[f'{collection_name}']
            collection.insert_many(stored_data)
            client.close()
    except Exception as e:
        print(e)
        return html.Div(['There was an error processing this file.'])
    return html.Div([
        html.H3(format_dataset_name(filename), style={'fontWeight': 'bold'}),
        html.H4('Descriptive Statistics'),
        generate_dtable(
            df.describe(),
            'descriptive',
            virtual=False,
            editable=False
        ),
        html.Br(),
        html.H4('Dataset'),
        generate_dtable(df, table_id='dataset'),
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
             'renamable': rename_cols} for col in sorted(df.columns)
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
        style_table={'overflowX': 'scroll'},
        style_data_conditional=[
            {
                'if': {'row_index': 'odd'},
                'backgroundColor': 'rgb(248, 248, 248)'
            }
        ],
        style_data={
            'whiteSpace': 'normal',
            'height': 'auto'
        },
        style_header={
            'textAlign': 'center',
            'padding': '2px',
            'backgroundColor': 'rgb(230, 230, 230)',
            'height': 'auto',
            'whiteSpace': 'normal',
            'fontWeight': 'bold',
            'fontSize': '12pt',
        },
        style_cell={
            'padding': '2px',
            'height': 'auto',
            'whiteSpace': 'normal',
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

"""Callback functionality for dash"""

@app.callback(
    Output('logistic regression-penalty-dropdown', 'options'),
    [Input('logistic regression-solver-dropdown', 'value')]
)
def filter_available_logistic_regression_penality(value):
    penalties = PARAMETERS['logistic regression']['penalty']['options']
    items = penalties.items()
    solvers = {
        'sag': {k: v for k, v in items if k in {'l2', 'none'}},
        'saga': penalties,
        'newton-cg': {k: v for k, v in items if k in {'l2', 'none'}},
        'lbfgs': {k: v for k, v in items if k == 'l2'},
        'liblinear': {k: v for k, v in items if k != 'none'}
    }
    return generate_options(solvers[value])


@app.callback(
    Output('logistic regression-solver-dropdown', 'options'),
    [Input('logistic regression-penalty-dropdown', 'value')]
)
def filter_available_logistic_regression_solver(value):
    solvers = PARAMETERS['logistic regression']['solver']['options']
    elastic_net = {k: v for k, v in solvers.items() if k == 'saga'}
    if value == 'elasticnet':
        return generate_options(elastic_net)
    else:
        return generate_options(solvers)


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
    return [html.H4('Hyperparameters', style={'fontWeight': 'bold'})] + \
           generate_widget(value)


@app.callback(
    Output('output-data-upload', 'children'),
    [Input('upload-data', 'contents')],
    [State('upload-data', 'filename')]
)
def update_output(content, name):
    if content:
        return [parse_contents(content, name)]

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
    Output('logistic regression', 'children'),
    ALGO_CALLBACK_INPUTS['logistic regression'] + [
        Input('model_name-input', 'value')]

)
def train_logistic_regression(
        solver, penalty, l1_ratio, dual, tol, C, fit_intercept,
        intercept_scaling, max_iter, model_name
):
    params = {'solver': solver, 'penalty': penalty, 'l1_ratio': l1_ratio,
              'dual': dual, 'tol': tol, 'C': C,
              'fit_intercept': fit_intercept,
              'intercept_scaling': intercept_scaling, 'max_iter': max_iter}
    model_id = '1'
    dataset_id = '1'
    X = []
    y = []
    model = Model(model_name=model_name, model_type='LGR', params=params,
                  model_id=model_id, dataset_id=dataset_id,
                  X=X, y=y)
    return model.picklize()


@app.callback(
    Output('support vector classification', 'children'),
    ALGO_CALLBACK_INPUTS['support vector classification'] + [
        Input('model_name-input', 'value')]
)
def train_support_vector_classification(
        kernel, C, degree, gamma, coef0, shrinking, tol, max_iter, model_name
):
    params = {'kernel': kernel, 'C': C, 'degree': degree, 'gamma': gamma,
              'coef0': coef0, 'shrinking': shrinking,
              'tol': tol, 'max_iter': max_iter}
    model_id = '1'
    dataset_id = '1'
    X = []
    y = []
    model = Model(model_name=model_name, model_type='SVC', params=params,
                  model_id=model_id, dataset_id=dataset_id,
                  X=X, y=y)
    return model.picklize()


@app.callback(
    Output('k nearest neighbors', 'children'),
    ALGO_CALLBACK_INPUTS['k nearest neighbors'] + [
        Input('model_name-input', 'value')]
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
    return model.picklize()

@app.callback(
    Output('decision tree classification', 'children'),
    ALGO_CALLBACK_INPUTS['decision tree classification'] + [
        Input('model_name-input', 'value')]
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
    return model.picklize()


@app.callback(
    Output('linear discriminant analysis', 'children'),
    ALGO_CALLBACK_INPUTS['linear discriminant analysis'] + [
        Input('model_name-input', 'value')]
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
    return model.picklize()


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


"""Layouts for each section of the dash pages"""

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
    style=generate_flex_style(grow='1', padding='1%'),
    children=[
        html.H4('Algorithm Selection', style={'fontWeight': 'bold'}),
        generate_dropdown(
            'algorithm_selection-dropdown',
            list(PARAMETERS.keys()),
            width='100%'
        )
    ])

model_name = html.Div(
    id='model_name-container',
    style=generate_flex_style(grow='1', padding='1%'),
    children=[
        html.H4('Model Name', style={'fontWeight': 'bold'}),
        dcc.Input(
            id='model_name-input',
            value=f'Unnamed Model ({NOW})',
            maxLength=50,
            style={'width': '100%'}
        )
    ])

selection_and_name = html.Div(
    id='algorithm_selection_model_name-container',
    style=generate_flex_style(),
    children=[algorithm_selection, model_name]
)

hyperparameters = html.Div(
    id='hyperparameters-container',
    style=generate_flex_style(
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
    style=generate_flex_style(grow='1'),
    children=[
        html.H6('Center'),
        generate_dropdown('center_feature-dropdown', ['a', 'b', 'c'],
                                multi=True, width='100%')
    ]
)

center_value = html.Div(
    id='center_value-container',
    style=generate_flex_style(grow='1'),
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
    style=generate_flex_style(),
    children=[center_feature, center_value]
)

scale_feature = html.Div(
    id='scale_feature-container',
    style=generate_flex_style(grow='1'),
    children=[
        html.H6('Scale'),
        generate_dropdown('scale_feature-dropdown', ['a', 'b', 'c'],
                                multi=True, width='100%')
    ]
)

scale_method = html.Div(
    id='scale_method-container',
    style=generate_flex_style(grow='1'),
    children=[
        html.H6('Method'),
        generate_dropdown(
            'scale_method-dropdown',
            ['a', 'b', 'c'],
            width='100%'
        )
    ]
)

add_scale = html.Div(
    id='add_scale-container',
    style=generate_flex_style(),
    children=[
        html.Button(id='add_scale-button',
                    children='Add',
                    n_clicks=0,
                    style={'fontSize': '100%'}
                    )
    ])

scale = html.Div(
    id='scale-container',
    style=generate_flex_style(),
    children=[scale_feature, scale_method]
)

preprocessing = html.Div(
    id='preprocessing-container',
    style=generate_flex_style(
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
    style=generate_flex_style(grow='1'),
    children=[
        html.H6('Cross Validation'),
        generate_dropdown(
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
    style=generate_flex_style(shrink='2'),
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
    style=generate_flex_style(shrink='2'),
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
    style=generate_flex_style(),
    children=[cv_method, cv_folds, cv_repeats]
)

scoring_metric = html.Div(
    id='scoring_metric-container',
    style=generate_flex_style(),
    children=[
        html.H6('Scoring Metrics'),
        generate_dropdown(
            'scoring_metrics-dropdown',
            SCORING_METRICS['classification'],
            multi=True,
            width='100%'
        )
    ])

tuning_strategy = html.Div(
    id='_tuning_strategy-container',
    style=generate_flex_style(),
    children=[
        html.H6('Hyperparameter Tuning Strategy'),
        generate_dropdown(
            'hyperparameter_tuning_strategy-dropdown',
            ['none', 'grid search', 'random'],
            width='100%'
        )
    ])

train_model = html.Div(style={'textAlign': 'left'}, children=[
    dcc.ConfirmDialogProvider(
        children=html.Button(id='train_model-button',
                             children='Train Model',
                             n_clicks=0,
                             style={'fontSize': '100%'}),
        message='Confirm that you want to train the model')
])

model_selection = html.Div(
    id='model_selection-container',
    style=generate_flex_style(
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
    style=generate_flex_style(alignment='flex-start'),
    children=[hyperparameters, preprocessing, model_selection]
)

build_layout = html.Div([
    html.Div(id='logistic regression-output',
             style={'display': 'none'}
             ),
    html.Div(id='support vector classification-output',
             style={'display': 'none'}
             ),
    html.Div(id='linear discriminant analysis-output',
             style={'display': 'none'}
             ),
    html.Div(id='k nearest neighbors-output',
             style={'display': 'none'}
             ),
    html.Div(id='decision tree classification-output',
             style={'display': 'none'}
             ),
    selection_and_name,
    params_preprocess_selection,

])

app.layout = html.Div([
    dcc.Tabs(id='tabs', value='dataset', children=[
        dcc.Tab(label='Dataset', value='dataset', children=dataset_layout,
                style={'fontSize': '14pt', 'fontWeight': 'bold'}),
        dcc.Tab(label='Build', value='build', children=build_layout,
                style={'fontSize': '14pt', 'fontWeight': 'bold'})]),
    html.Div(id='tabs-content')])

"""Main function to start Flask servers"""

if __name__ == '__main__':
    app.run_server(debug=True)

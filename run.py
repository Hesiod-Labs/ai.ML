import base64
import io
import json
import os

import pandas as pd
from bson.objectid import ObjectId
from flask import (Flask, flash, redirect, render_template, request, session,
                    url_for)
from pandas.io.json import json_normalize
from pymongo import MongoClient

import dash
import aiml

# Instantiates the main Flask server, the Mongo instance, and global dataframe for shared use of a dataframe between Flask and Dash servers
server = Flask(__name__)
server.secret_key = os.urandom(24)
client = MongoClient("mongodb+srv://hlabs_1:thinkBox@aiml-thzu0.mongodb.net/test?retryWrites=true&w=majority")
df = pd.DataFrame()

# Instantiate the dash application and the base layout
app = dash.Dash(__name__,
                server=server,
                external_stylesheets=['https://codepen.io/chriddyp/pen/bWLwgP.css'],
                routes_pathname_prefix='/dash/')
app.config.suppress_callback_exceptions = True
aiml.baselayout(app)

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
        df = selected_data[selected_data.columns[1:10]].head(10)
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

if __name__ == '__main__':
    app.run_server(debug=True)
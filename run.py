import os

from flask import (Flask, flash, redirect, render_template, request, session,
                   url_for)
from pymongo import MongoClient

app = Flask(__name__)
app.secret_key = os.urandom(24)
client = MongoClient("mongodb+srv://hlabs_1:thinkBox@aiml-thzu0.mongodb.net/test?retryWrites=true&w=majority")

# Starting page is the login page
@app.route('/', methods=['GET', 'POST'])
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
# Once done, they will be redirected to home page or asked to reenter info
@app.route('/createaccount', methods=['GET', 'POST'])
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
@app.route('/main', methods=['GET', 'POST'])
def main():
    if not 'id' in session:
        return redirect(url_for('start'))
    return render_template('main.html')

# User can update their email
@app.route('/updateemail', methods=['GET', 'POST'])
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
        collection.update_one({"id":f"{session['id']}"}, {"$set":{"email":f"{new_email}"}})
        session['email'] = new_email
        client.close()
        return redirect(url_for('profile'))
    return render_template('updateemail.html', template_error = "", profile = session)

# User can update their username
@app.route('/updateusername', methods=['GET', 'POST'])
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
        collection.update_one({"id":f"{session['id']}"}, {"$set":{"username":f"{new_username}"}})
        session['username'] = new_username
        client.close()
        return redirect(url_for('profile'))
    return render_template('updateusername.html', template_error = "", profile = session)

# User can update their password
@app.route('/updatepassword', methods=['GET', 'POST'])
def update_password():
    db = client['aiML']
    collection = db['users']
    if not 'id' in session:
        return redirect(url_for('start'))
    if request.method == "POST":
        if request.form['new-password'] == request.form['retype-new-password']:
            if collection.count_documents({"password":f"{request.form['old-password']}"}) == 1:
                new_password = request.form['new-password']
                collection.update_one({"id":f"{session['id']}"}, {"$set":{"password":f"{new_password}"}})
                session['password'] = new_password
                client.close()
                return redirect(url_for('profile'))
            else:
                return render_template('updatepassword.html', template_error = "Could not change password: Incorrect old password")
        else:
            return render_template('updatepassword.html', template_error = "Could not change password: New password fields do not match")
    return render_template('updatepassword.html', template_error = "")
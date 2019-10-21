import os

from bson.objectid import ObjectId
from flask import (Flask, flash, redirect, render_template, request, session,
                   url_for)
from pymongo import MongoClient

app = Flask(__name__)
app.secret_key = os.urandom(24)
client = MongoClient("mongodb+srv://hlabs_1:thinkBox@aiml-thzu0.mongodb.net/test?retryWrites=true&w=majority")

# User can login to their account
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

# Main page containing ai.ML functionality TODO
@app.route('/main', methods=['GET', 'POST'])
def main():
    if not 'id' in session:
        return redirect(url_for('start'))
    return render_template('main.html')

# User can logout from their account
@app.route('/logout', methods=['GET', 'POST'])
def logout():
    if not 'id' in session:
        return redirect(url_for('start'))
    if "returnhome" in request.form:
        if request.form["returnhome"] == "Yes":
            session.pop("username", None)
            session.pop("email", None)
            session.pop("id", None)
            return redirect(url_for('start'))
        if request.form["returnhome"] == "No":
            return redirect(url_for('main'))
    return render_template('logout.html')

# User can view basic profile information, update email, username or password, or delete account
@app.route('/profile', methods=['GET', 'POST'])
def profile():
    if not 'id' in session:
        return redirect(url_for('start'))
    return render_template('profile.html', profile = session)

# User can update their email
@app.route('/updateemail', methods=['GET', 'POST'])
def update_email():
    db = client['aiML']
    collection = db['users']
    if not 'id' in session:
        return redirect(url_for('start'))
    if request.method == "GET":
        user_info = collection.find_one({"email":f"{session['email']}"})
       # email = user_info['email']
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
        collection.update_one({"_id":ObjectId(f"{session['id']}")}, {"$set":{"username":f"{new_username}"}})
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
@app.route('/deleteaccount', methods=['GET', 'POST'])
def delete_account():
    db = client['aiML']
    collection = db['users']
    if not 'id' in session:
        return redirect(url_for('start'))
    if request.method == "POST":
        if "delete-btn" in request.form:
            collection.delete_one({"_id":ObjectId(f"{session['id']}")})
            return redirect(url_for('start'))
        if "returnhome" in request.form:
            return redirect(url_for('main'))
    return render_template('deleteaccount.html')
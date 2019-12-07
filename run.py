"""The primary Flask web application framework for ai.ML that seamlessly
    connect the main web pages with Dash.

    Each function represents a different web page within ai.ML. 
    They make use of flask redirects, template rendering, requests 
    and sessions to relay user input between the frontend and backend. 
    The Dash application is initiated on the same server as the 
    main flask application, allowing for users to go straight to Dash from the
    main page.
"""
import os

from bson.objectid import ObjectId
from flask import Flask, redirect, render_template, request, session, url_for
from pymongo import MongoClient

import dash
import aiml

# Instantiates the main Flask server, the Mongo instance, and global
# dataframe for shared use of a dataframe between Flask and Dash servers
server = Flask(__name__)
server.secret_key = os.urandom(24)
client = MongoClient(
    "mongodb+srv://hlabs_1:thinkBox@aiml-thzu0.mongodb.net/test?retryWrites"
    "=true&w=majority")  # Connection String to MongoDB Atlas

# Instantiate the dash application and the base layout
app = dash.Dash(__name__,
                server=server,
                # Server is the same one defined above for the main flask
                # application
                external_stylesheets=[
                    'https://codepen.io/chriddyp/pen/bWLwgP.css'],
                # CSS styling is same as main html pages
                routes_pathname_prefix='/dash/')
app.config.suppress_callback_exceptions = True

aiml.baselayout(app)  # Layouts for Dash application defined in 'aiml' module


# User can login to their account
@server.route('/', methods=['GET', 'POST'])
def start():
    """User can login to their account

    Returns:
        The 'start' template if invalid login information is provided OR
        The 'main' template if valid login information is provided 
    """
    if request.method == "POST":
        # Connects to ai.ML database
        db = client['aiML']
        # Connects to 'users' collection (this occurs every time program
        # needs to access user information)
        collection = db['users']
        if collection.count_documents({
            "username": f"{request.form['username']}",
            "password": f"{request.form['password']}"}
        ) == 1:
            user_info = collection.find_one({
                "username": f"{request.form['username']}"}
            )
            session['id'] = str(user_info['_id'])
            session['email'] = user_info['email']
            session['username'] = user_info['username']
            session['password'] = user_info['password']
            client.close()
            return redirect(url_for('main'))
        else:
            return render_template(
                'start.html',
                template_error="Could not login: incorrect username or password"
            )
    return render_template('start.html', template_error="")


@server.route('/createaccount', methods=['GET', 'POST'])
def create_account():
    """User can create an account

    Returns:
        The 'create_account' template if invalid new user information is
        provided OR The 'main' template if valid user information is provided
    """
    db = client['aiML']
    collection = db['users']
    if "email" in request.form and request.method == "POST":
        if request.form['password'] == request.form['retype-password']:
            account_info = {"email": request.form['email'],
                            "username": request.form['username'],
                            "password": request.form['password']}
            # Checks username, email, and password
            # Will successfully create the account if all provided information
            # is not already taken by another user
            # in which case a template error will be thrown 
            for item in account_info:
                session[item] = account_info[item]
                if collection.count_documents(
                        {f"{item}": f"{session[item]}"}) > 0:
                    session.pop(item)
                    client.close()
                    return render_template(
                        'createaccount.html',
                        template_error=f"Could not create account: {item} is "
                        f"part of another account")
            user_info = {"email": f"{request.form['email']}",
                         "username": f"{request.form['username']}",
                         "password": f"{request.form['password']}"}
            user_id = collection.insert_one(user_info).inserted_id
            session['id'] = str(user_id)
            client.close()
            return redirect(url_for('main'))
        else:
            return render_template(
                'createaccount.html',
                template_error="Could not create account: password fields do "
                               "not match")
    return render_template('createaccount.html', template_error="")


@server.route('/main', methods=['GET', 'POST'])
def main():
    """Main page containing ai.ML functionality
    if not 'id' in session:
        return redirect(url_for('start'))
    return render_template('main.html')

    Returns:
        One of the following:
            - The 'start' template if the user's ID is not in a session
            - The 'main' template
    """
    if 'id' not in session:
        return redirect(url_for('start'))
    return render_template('main.html')


@server.route('/logout', methods=['GET', 'POST'])
def logout():
    """User can logout from their account

    Returns:
        One of the following:
            - The 'main' template if the user decides that they do not want to
                log out
            - The 'logout' template which will redirect the user to the login
                page once they log out
            - The 'start' template if the user's ID is not in a session
    """
    if 'id' not in session:
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


@server.route('/profile', methods=['GET', 'POST'])
def profile():
    """User can view basic profile information, update email, username or
        password, or delete account

    Returns:
        One of the following:
            - The 'profile' template that showcases user information and has
                links for updating user information and deleting an account
            - The 'start' template if the user's ID is not in a session
    """
    if 'id' not in session:
        return redirect(url_for('start'))
    return render_template('profile.html', profile=session)


@server.route('/updateemail', methods=['GET', 'POST'])
def update_email():
    """User can update their email

    Returns:
        One of the following:
            - The 'updateemail' template if the new email is already taken (
                i.e. in the database)
            - The 'profile' template once the user is finished updating their
                email
    """
    db = client['aiML']
    collection = db['users']
    if 'id' not in session:
        return redirect(url_for('start'))
    if request.method == "GET":
        user_info = collection.find_one({"email": f"{session['email']}"})
        email = user_info['email']
    if request.method == "POST":
        new_email = request.form['new-email']
        if collection.count_documents(
                {"email": f"{request.form['new-email']}"}) > 0:
            return render_template(
                'updateemail.html',
                template_error="Could not update email: email is already a "
                               "part of another account",
                profile=session
            )
        collection.update_one({"_id": ObjectId(f"{session['id']}")},
                              {"$set": {"email": f"{new_email}"}})
        session['email'] = new_email
        client.close()
        return redirect(url_for('profile'))
    return render_template('updateemail.html', template_error="",
                           profile=session)


@server.route('/updateusername', methods=['GET', 'POST'])
def update_username():
    """User can update their username

    Returns:
        One of the following:
            - The 'updateusername' template if the new username is already
                taken (i.e. in the database)
            - The 'profile' template once the user is finished updating their
                email
    """
    db = client['aiML']
    collection = db['users']
    if 'id' not in session:
        return redirect(url_for('start'))
    if request.method == "GET":
        user_info = collection.find_one({"username": f"{session['username']}"})
        username = user_info['username']
    if request.method == "POST":
        new_username = request.form['new-username']
        if collection.count_documents(
                {"username": f"{request.form['new-username']}"}) > 0:
            return render_template(
                'updateusername.html',
                template_error="Could not update username: username is "
                               "already a part of another account",
                profile=session
            )
        collection.update_one({"_id": ObjectId(f"{session['id']}")},
                              {"$set": {"username": f"{new_username}"}})
        session['username'] = new_username
        client.close()
        return redirect(url_for('profile'))
    return render_template('updateusername.html', template_error="",
                           profile=session)


@server.route('/updatepassword', methods=['GET', 'POST'])
def update_password():
    """User can update their password

    Returns:
        One of the following:
            - The 'updatepassword' template if the user incorrectly typed
                their old password
            - The 'updatepassword' template if the new password fields do not
                match eachother OR
            - The 'profile' template once the user is finished updating their
                email
    """
    db = client['aiML']
    collection = db['users']
    if 'id' not in session:
        return redirect(url_for('start'))
    if request.method == "POST":
        if request.form['new-password'] == request.form['retype-new-password']:
            if collection.count_documents(
                    {"password": f"{request.form['old-password']}"}) == 1:
                new_password = request.form['new-password']
                collection.update_one({"_id": ObjectId(f"{session['id']}")},
                                      {"$set": {"password": f"{new_password}"}})
                session['password'] = new_password
                client.close()
                return redirect(url_for('profile'))
            else:
                return render_template(
                    'updatepassword.html',
                    template_error="Could not change password: Incorrect old "
                                   "password")
        else:
            return render_template(
                'updatepassword.html',
                template_error="Could not change password: New password "
                               "fields do not match")
    return render_template('updatepassword.html', template_error="")


@server.route('/deleteaccount', methods=['GET', 'POST'])
def delete_account():
    """User can delete their account

    Returns:
        One of the following:
            - The 'start' template if the user confirms to delete their
                account
            - The 'main' template if the user decides to not delete their
                account
    """
    db = client['aiML']
    collection = db['users']
    if 'id' not in session:
        return redirect(url_for('start'))
    if request.method == "POST":
        if "delete-btn" in request.form:
            collection.delete_one({"_id": ObjectId(f"{session['id']}")})
            client.close()
            return redirect(url_for('start'))
        if "returnhome" in request.form:
            return redirect(url_for('main'))
    return render_template('deleteaccount.html')


if __name__ == '__main__':
    app.run_server(debug=True)

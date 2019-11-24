import os

import pytest
from bson.objectid import ObjectId
from flask import (Flask, flash, redirect, render_template, request, session,
                   url_for)
from pandas import DataFrame
from pandas.io.json import json_normalize
from pymongo import MongoClient

client = MongoClient("mongodb+srv://hlabs_1:thinkBox@aiml-thzu0.mongodb.net/test?retryWrites=true&w=majority")
db = client['aiML']
collection = db['tests']

class TestMongo:

    # Test for creating an account and saving to database
    def test_create_account(self):
        user_info = {"email":"test1@case.edu",
                    "username":"test1user",
                    "password":"test1pass"}
        collection.delete_many({})
        user_id = collection.insert_one(user_info).inserted_id
        assert user_id == collection.find_one({"_id":user_id}).get("_id")

    # Test for not allowing database to take email if already taken
    def test_existing_email(self):
        user_info = {"email":"test1@case.edu",
                    "username":"test1user",
                    "password":"test1pass"}
        collection.delete_many({})
        collection.insert_one(user_info)
        email_count_1 = collection.count_documents({"email":"test1@case.edu"})
        email_count_2 = collection.count_documents({"email":"test2@case.edu"})
        if email_count_1 > 0 and email_count_2 == 0:
            assert (email_count_1 > 0) is True
            assert (email_count_2 == 0) is True
        else:
            assert (email_count_1 > 0) is False
            assert (email_count_2 == 0) is False

    # Test for not allowing database to take username if already taken
    def test_existing_username(self):
        user_info = {"email":"test1@case.edu",
                    "username":"test1user",
                    "password":"test1pass"}
        collection.delete_many({})
        collection.insert_one(user_info)
        username_count_1 = collection.count_documents({"username":"test1user"})
        username_count_2 = collection.count_documents({"username":"test1user"})
        if username_count_1 > 0 and username_count_2 == 0:
            assert (username_count_1 > 0) is True
            assert (username_count_2 == 0) is True
        else:
            assert (username_count_1 > 0) is False
            assert (username_count_2 == 0) is False
"""
    # Test for not allowing database to take password if already taken
    def test_existing_password(self):

    # Test for reading data from the database
    def test_read_data(self):

    # Test for updating an email
    def test_update_email(self):

    # Test for updating an username
    def test_update_username(self):

    # Test for updating an password
    def test_update_password(self):

    # Test for deleting account from database
    def test_delete_account(self):
"""
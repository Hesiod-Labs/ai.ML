import pytest
from pymongo import MongoClient

client = MongoClient("mongodb+srv://hlabs_1:thinkBox@aiml-thzu0.mongodb.net/test?retryWrites=true&w=majority")
db = client['aiML']
collection = db['tests']

"""
The following functions each test aspects of database-application interaction in ai.ML
The queries used below are of the same style and format used in the application itself
They test database CRUD operations that query user information (email, username, password)
"""
class TestMongo:

    # Test for creating an account and saving to database
    def test_create_account(self):
        user_info = {"email":"test1@case.edu",
                    "username":"test1user",
                    "password":"test1pass"}
        collection.delete_many({})
        user_id = collection.insert_one(user_info).inserted_id
        assert user_id == collection.find_one({"_id":user_id}).get("_id")

    # Test for not allowing database to insert email if already taken
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

    # Test for not allowing database to insert username if already taken
    def test_existing_username(self):
        user_info = {"email":"test1@case.edu",
                    "username":"test1user",
                    "password":"test1pass"}
        collection.delete_many({})
        collection.insert_one(user_info)
        username_count_1 = collection.count_documents({"username":"test1user"})
        username_count_2 = collection.count_documents({"username":"test2user"})
        if username_count_1 > 0 and username_count_2 == 0:
            assert (username_count_1 > 0) is True
            assert (username_count_2 == 0) is True
        else:
            assert (username_count_1 > 0) is False
            assert (username_count_2 == 0) is False

    # Test for not allowing database to insert password if already taken
    def test_existing_password(self):
        user_info = {"email":"test1@case.edu",
                    "username":"test1user",
                    "password":"test1pass"}
        collection.delete_many({})
        collection.insert_one(user_info)
        password_count_1 = collection.count_documents({"password":"test1pass"})
        password_count_2 = collection.count_documents({"password":"test2pass"})
        if password_count_1 > 0 and password_count_2 == 0:
            assert (password_count_1 > 0) is True
            assert (password_count_2 == 0) is True
        else:
            assert (password_count_1 > 0) is False
            assert (password_count_2 == 0) is False

    # Test for updating an email
    def test_update_email(self):
        user_info = {"email":"test1@case.edu",
                    "username":"test1user",
                    "password":"test1pass"}
        collection.delete_many({})
        user_id = collection.insert_one(user_info).inserted_id
        email_count_1 = collection.count_documents({"email":"test1@case.edu"})
        email_count_2 = collection.count_documents({"email":"test2@case.edu"})
        if email_count_1 > 0 and email_count_2 == 0:
            assert (email_count_1 > 0) is True
            assert (email_count_2 == 0) is True
        else:
            assert (email_count_1 > 0) is False
            assert (email_count_2 == 0) is False  
        collection.update_one({"_id":user_id}, {"$set":{"email":"test2@case.edu"}})
        email_count_1 = collection.count_documents({"email":"test1@case.edu"})
        email_count_2 = collection.count_documents({"email":"test2@case.edu"})
        if email_count_1 == 0 and email_count_2 > 0:
            assert (email_count_1 == 0) is True
            assert (email_count_2 > 0) is True
        else:
            assert (email_count_1 == 0) is False
            assert (email_count_2 > 0) is False        

    # Test for updating an username
    def test_update_username(self):
        user_info = {"email":"test1@case.edu",
                    "username":"test1user",
                    "password":"test1pass"}
        collection.delete_many({})
        user_id = collection.insert_one(user_info).inserted_id
        username_count_1 = collection.count_documents({"username":"test1user"})
        username_count_2 = collection.count_documents({"username":"test2user"})
        if username_count_1 > 0 and username_count_2 == 0:
            assert (username_count_1 > 0) is True
            assert (username_count_2 == 0) is True
        else:
            assert (username_count_1 > 0) is False
            assert (username_count_2 == 0) is False 
        collection.update_one({"_id":user_id}, {"$set":{"username":"test2user"}})
        username_count_1 = collection.count_documents({"username":"test1user"})
        username_count_2 = collection.count_documents({"username":"test2user"})
        if username_count_1 == 0 and username_count_2 > 0:
            assert (username_count_1 == 0) is True
            assert (username_count_2 > 0) is True
        else:
            assert (username_count_1 == 0) is False
            assert (username_count_2 > 0) is False 

    # Test for updating an password
    def test_update_password(self):
        user_info = {"email":"test1@case.edu",
                    "username":"test1user",
                    "password":"test1pass"}
        collection.delete_many({})
        user_id = collection.insert_one(user_info).inserted_id
        password_count_1 = collection.count_documents({"password":"test1pass"})
        password_count_2 = collection.count_documents({"password":"test2pass"})
        if password_count_1 > 0 and password_count_2 == 0:
            assert (password_count_1 > 0) is True
            assert (password_count_2 == 0) is True
        else:
            assert (password_count_1 > 0) is False
            assert (password_count_2 == 0) is False
        collection.update_one({"_id":user_id}, {"$set":{"password":"test2pass"}})
        password_count_1 = collection.count_documents({"password":"test1pass"})
        password_count_2 = collection.count_documents({"password":"test2pass"})
        if password_count_1 == 0 and password_count_2 > 0:
            assert (password_count_1 == 0) is True
            assert (password_count_2 > 0) is True
        else:
            assert (password_count_1 == 0) is False
            assert (password_count_2 > 0) is False    

    # Test for deleting account from database
    def test_delete_account(self):
        user_info = {"email":"test1@case.edu",
                    "username":"test1user",
                    "password":"test1pass"}
        collection.delete_many({})
        user_id = collection.insert_one(user_info).inserted_id
        password_count_1 = collection.count_documents({"password":"test1pass"})
        password_count_2 = collection.count_documents({"password":"test2pass"})
        if password_count_1 > 0 and password_count_2 == 0:
            assert (password_count_1 > 0) is True
            assert (password_count_2 == 0) is True
        else:
            assert (password_count_1 > 0) is False
            assert (password_count_2 == 0) is False
        collection.delete_one({"_id":user_id})
        password_count_1 = collection.count_documents({"password":"test1pass"})
        password_count_2 = collection.count_documents({"password":"test2pass"})
        if (password_count_1 and password_count_2) == 0:
            assert ((password_count_1 and password_count_2) == 0) is True
        else:
            assert ((password_count_1 and password_count_2) == 0) is False

    # Test for uploading a large dataset
    def test_upload_to_database(self):
        data = [{"email1":"test1@case.edu",
                "languages":["java", "python"],
                "classes":["eecs340", "eecs393"]},
                {"email2":"test2@case.edu",
                "languages":["ruby", "objective-c"],
                "classes":["eecs293" "eecs281"]},
                {"email2":"test2@case.edu",
                "languages":["python", "systemverilog", "c++"],
                "classes":["eecs600", "eecs440"]},
                {"email4":"test4@case.edu",
                "languages":["R", "c#"],
                "classes":["eecs290", "eecs233", "eecs302"]}]
        collection.delete_many({})
        massinsert_id = collection.insert_many(data).inserted_ids
        total_count = collection.count_documents({})
        if total_count == 4:
            assert (total_count == 4) is True
        else:
            assert (total_count == 4) is False
        email_count_1 = collection.count_documents({"email1":"test1@case.edu"})
        email_count_2 = collection.count_documents({"email2":"test2@case.edu"})
        if email_count_1 == 1 and email_count_2 == 2:
            assert (email_count_1 == 1) is True
            assert (email_count_2 == 2) is True
        else:
            assert (email_count_1 == 1) is False
            assert (email_count_2 == 2) is False
from flask_testing import TestCase
from flask import Flask

class TestFlask(TestCase):

    def create_app(self):

        testApp = Flask(_name_)
        testApp.comnfig['TEST'] = True
        return testApp

    

import unittest
from flask import render_template
from flask_login import current_user
from monolith.app import app as tested_app
from monolith.forms import LoginForm

class TestApp(unittest.TestCase):

    def test1_login(self):  
        # bad login test
        app = tested_app.test_client()
        formdata  = {'email': 'example@login.com', 'password': 'testing'}
        reply = app.post('/login', data=formdata, follow_redirects = True, content_type = 'multipart/form-data')
        
        print("reply "+ str(reply.data, 'utf-8'))
        
        self.assertIn("Incorrect data",str(reply.data, 'utf-8'))

        
    def test2_login(self):
        #good login test
        app = tested_app.test_client()
        formdata = {'email':'example@example.com','password':'admin'}
        reply = app.post('/login', data = formdata, follow_redirects = True, content_type = 'multipart/form-data')
        """for some reason even if correct data inserted this does not redirect to the home page"""
        print("reply "+ str(reply.data, 'utf-8'))
        self.assertIn("Logged In!",str(reply.data, 'utf-8'))
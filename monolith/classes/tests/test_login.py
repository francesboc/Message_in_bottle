import unittest
from flask import render_template
from flask_login import current_user
from monolith.app import app as tested_app
from monolith.forms import LoginForm

class TestApp(unittest.TestCase):

    tested_app.config['WTF_CSRF_ENABLED'] = False

    def test1_login(self):  
        # bad login test
        app = tested_app.test_client()
        formdata  = dict(email="a", password="a")
        reply = app.post('/login', data=formdata, follow_redirects = True)
        
        self.assertEqual(reply.status_code, 401)
    
    def test2_login(self):
        #good login test
        app = tested_app.test_client()
        formdata = dict(email="example@example.com", password="admin")
        reply = app.post('/login', data = formdata, follow_redirects = True)
    
        self.assertIn("Hi Admin !",str(reply.data, 'utf-8'))
    
    def test_myaccount(self):
        app = tested_app.test_client()

        #Creating a user
        formdata = dict(email="test@test.com",
                    firstname="test",
                    lastname="test",
                    password="test",
                    date_of_birth="11/11/1111")
        reply = app.post("/create_user", data = formdata, follow_redirects = True)
        self.assertEqual(reply.status_code, 200)

        formdata = dict(email="test@test.com", password="test")
        reply = app.post('/login', data = formdata, follow_redirects = True)
        self.assertIn("Hi test !",str(reply.data, 'utf-8'))

        reply = app.get("/myaccount")
        self.assertEqual(reply.status_code, 200)

        reply = app.delete("/myaccount")
        self.assertEqual(reply.status_code, 303)
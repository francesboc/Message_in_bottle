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
    

    #test: creation of usr, myaccount functionality, message list of usr, delete of account
    def test_myaccount(self):
        app = tested_app.test_client()

        #Creating a user
        email_test = "test@test.com"

        formdata = dict(email="test@test.com",
                    firstname="test",
                    lastname="test",
                    password="test",
                    date_of_birth="11/11/1111")
        reply = app.post("/create_user", data = formdata, follow_redirects = True)
        #self.assertEqual(reply.status_code, 200) #Instead of checking only reply code, i suggest to check if in the list of user 
                                                 #is present the email just registered
        self.assertIn(email_test, str(reply.data, 'utf-8'))

        formdata = dict(email="test@test.com", password="test")
        reply = app.post('/login', data = formdata, follow_redirects = True)
        self.assertIn("Hi test !",str(reply.data, 'utf-8'))

        reply = app.get("/myaccount")
        self.assertEqual(reply.status_code, 200)
        self.assertIn(email_test, str(reply.data, 'utf-8')) #Also added this to check that the page returned is really the correct one (the page realtive to the actual user)

        reply = app.get("/messages")
        self.assertEqual(reply.status_code, 200)
        self.assertIn("Message List", str(reply.data, 'utf-8'))

        reply = app.delete("/myaccount")
        self.assertEqual(reply.status_code, 303)
        reply2 = app.post("/users") # Also added this and next line to ensure the user is no more in the system: 
        self.assertNotIn(email_test, str(reply.data, 'utf-8')) # check if the email of user just deletet is not in the user list


import unittest
from flask import render_template
from flask_login import current_user
from monolith.app import app as tested_app
from monolith.forms import LoginForm

class TestApp(unittest.TestCase):
    tested_app.config['WTF_CSRF_ENABLED'] = False
    
    def test_user(self):
        app = tested_app.test_client()

        # register new user A
        emailA = "Axmpl@xmpl.com"
        emailB = "Bxmpl@xmpl.com"
        formdatA = dict(email="Axmpl@xmpl.com",
                    firstname="userA",
                    lastname="userA",
                    password="userA",
                    date_of_birth="11/11/1111")
        reply = app.post("/create_user", data = formdatA, follow_redirects = True)
        
        # register new user B
        formdatB = dict(email="Bxmpl@xmpl.com",
                    firstname="userB",
                    lastname="userB",
                    password="userB",
                    date_of_birth="11/11/1111")
        reply = app.post("/create_user", data = formdatB, follow_redirects = True)
        #TODO should we test that the password is hashed and salted?

        #trying to register an already used email
        reply = app.post("/create_user", data = formdatB, follow_redirects = True)
        self.assertIn("Email already used",str(reply.data,'utf-8'))
        # show users list and look for user inserted
        reply = app.get("/users")
        
        self.assertIn("First name: userA",str(reply.data,'utf-8'))
        self.assertIn("First name: userB",str(reply.data,'utf-8'))
        self.assertIn("Last name: userA",str(reply.data,'utf-8'))
        self.assertIn("Last name: userB",str(reply.data,'utf-8'))
        self.assertIn("e-mail: "+emailA,str(reply.data,'utf-8'))
        self.assertIn("e-mail: "+emailB,str(reply.data,'utf-8'))
        self.assertIn("User's blacklist:",str(reply.data,'utf-8'))

        #TODO login user A
        logFormA = dict(email = emailA,password = "userA")
        reply = app.get("/login")
        #check get on /login route returns exactly the page expected
        #htmlLogin = open("monolith/templates/login.html","r")
        #reply2 = render_template("monolith/templates/login.html")
        #self.assertEqual(str(reply2.data,'utf-8'), str(reply.data,'utf-8'))     #not working cause of jinja. Is there a way
        
        reply = app.post("/login",data=logFormA,follow_redirects=True)
        self.assertIn("Hi userA",str(reply.data,'utf-8'))
        #check empty mailbox for userA
        reply = app.get("/messages")
        self.assertIn("Your mailbox is empty!",str(reply.data,'utf-8'))
        #TODO send a message A->B

        #TODO switch user B
        reply = app.get("/logout")
        #Check if /logout redirects to the correct page(?)
        logFormB = dict(email = emailB,password = "userB")
        reply = app.post("/login",form=logFormA,follow_redirects=True)
        self.assertIn("Hi userB",str(reply.data,'utf-8'))
        #TODO check B's mailbox and look for the message inserted

        #TODO look the content of the message
import unittest
from flask import render_template
from flask_login import current_user
from monolith.database import User
from monolith.app import app as tested_app
from monolith.forms import LoginForm
from monolith.app import db
import bcrypt

class TestApp(unittest.TestCase):
    tested_app.config['WTF_CSRF_ENABLED'] = False
    #need to clear the database before this test
    def setUp(self):
        """
        Creates a new database for the unit test to use
        """
        tested_app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
        db.init_app(tested_app)
        with tested_app.app_context():
            db.create_all()
            db.session.commit()
            
            
    
    def test_user(self):
        app = tested_app.test_client()

        # register new user A
        emailA = "Axmpl@xmpl.com"
        emailB = "Bxmpl@xmpl.com"
        emailC = "Cxmpl@xmpl.com"
        formdatA = dict(email="Axmpl@xmpl.com",
                    firstname="userA",
                    lastname="userA",
                    password="userA",
                    date_of_birth="11/11/1911")
        reply = app.post("/create_user", data = formdatA, follow_redirects = True)
        
        # register new user B
        formdatB = dict(email="Bxmpl@xmpl.com",
                    firstname="userB",
                    lastname="userB",
                    password="userB",
                    date_of_birth="11/11/1911")
        reply = app.post("/create_user", data = formdatB, follow_redirects = True)
        #register new user C
        formdatC = dict(email="Cxmpl@xmpl.com",
                    firstname="userC",
                    lastname="userC",
                    password="userC",
                    date_of_birth="11/11/1911")
        reply = app.post("/create_user", data = formdatC, follow_redirects = True)

        # try to register a user with wrong date format
        wrong1 = "1911/11/12"
        wrong2 = "11/11/1111"
        formWrongData = dict(email="Xxmpl@xmpl.com",
                    firstname="userX",
                    lastname="userX",
                    password="userX",
                    date_of_birth= wrong1)
        reply = app.post("/create_user", data = formWrongData, follow_redirects = True)
        self.assertIn("Please enter a valid date of birth in the format dd/mm/yyyy!",str(reply.data,'utf-8'))

        formWrongData = dict(email="Xxmpl@xmpl.com",
                    firstname="userX",
                    lastname="userX",
                    password="userX",
                    date_of_birth= wrong2)
        reply = app.post("/create_user", data = formWrongData, follow_redirects = True)
        self.assertIn("Please enter a valid date of birth!",str(reply.data,'utf-8'))

        #trying to register an already used email
        reply = app.post("/create_user", data = formdatB, follow_redirects = True)
        self.assertIn("Email already used",str(reply.data,'utf-8'))
        # show users list and look for user inserted
        reply = app.get("/users")
        
        self.assertIn("First name: userA",str(reply.data,'utf-8'))
        self.assertIn("First name: userB",str(reply.data,'utf-8'))
        self.assertIn("First name: userC",str(reply.data,'utf-8'))
        self.assertIn("Last name: userA",str(reply.data,'utf-8'))
        self.assertIn("Last name: userB",str(reply.data,'utf-8'))
        self.assertIn("Last name: userC",str(reply.data,'utf-8'))
        self.assertIn("e-mail: "+emailA,str(reply.data,'utf-8'))
        self.assertIn("e-mail: "+emailB,str(reply.data,'utf-8'))
        self.assertIn("e-mail: "+emailC,str(reply.data,'utf-8'))
        
        #search for userA in /users
        #When the user is not logged can see also himself into the list of users
        reply = app.get("/users", follow_redirects = True)
        self.assertIn("userA",str(reply.data,'utf-8'))
        # login user A
        logFormA = dict(email = emailA,password = "userA")
        reply = app.post("/login",data=logFormA,follow_redirects=True)
        self.assertIn("Hi userA",str(reply.data,'utf-8'))

        reply = app.get("/users", follow_redirects = True)
        self.assertNotIn("userA",str(reply.data,'utf-8'))

        reply = app.get("/logout",follow_redirects = True)

        
        #test blacklist with no user logged in
        reply = app.get('/blacklist', follow_redirects = True)
        self.assertIn("Your are not login to the website",str(reply.data,'utf-8'))
        
        #test blaclist/<target> with no user logged in
        reply = app.post('blacklist/3', follow_redirects = True)
        self.assertIn("Your are not login to the website",str(reply.data,'utf-8'))

        #test login userA
        reply = app.post("/login",data=logFormA,follow_redirects=True)
        self.assertIn("Hi userA",str(reply.data,'utf-8'))
        
        #test check userA empty blacklist
        reply = app.get("/blacklist", follow_redirects = True)
        self.assertIn("Your blacklist is empty",str(reply.data,'utf-8'))
        
        #Clear the empty blacklist
        reply = app.delete("/blacklist", follow_redirects = True)
        self.assertIn("Your blacklist is already empty",str(reply.data,'utf-8'))
        
        # insert C into the blacklist of A
        reply = app.post("/blacklist/3",follow_redirects = True)
        self.assertIn("User 3 added to the black list.",str(reply.data,'utf-8'))
        
        #check C really into bl A
        reply = app.get("/blacklist",follow_redirects = True)
        self.assertIn(emailC,str(reply.data,'utf-8'))

        #insert X with non existing id 
        reply = app.post("/blacklist/100",follow_redirects = True)
        self.assertIn("Please check that you select a correct user",str(reply.data,'utf-8'))
        
        #inser again C 
        reply = app.post("/blacklist/3",follow_redirects = True)
        self.assertIn("This user is already in your blacklist!",str(reply.data,'utf-8'))
        
        #Clear the blacklist after C insertion
        reply = app.delete("/blacklist", follow_redirects = True)
        self.assertIn("Your blacklist is now empty",str(reply.data,'utf-8'))

        #test check userA empty blacklist
        reply = app.get("/blacklist", follow_redirects = True)
        self.assertIn("Your blacklist is empty",str(reply.data,'utf-8'))
                
        #insert C into A's blacklist
        reply = app.post("/blacklist/3",follow_redirects = True)
        self.assertIn("User 3 added to the black list.",str(reply.data,'utf-8'))

        #remove C from A's blacklist
        reply = app.delete("/blacklist/3",follow_redirects = True)
        self.assertIn("User 3 removed from your black list.",str(reply.data,'utf-8'))

        # try to delete a user from blacklist that is not in blacklist
        reply = app.delete("/blacklist/2", follow_redirects = True)
        self.assertIn("This user is not in your blacklist",str(reply.data,'utf-8'))

        # try to add a user with non valid id into the blacklist
        reply = app.delete("/blacklist/100", follow_redirects = True)
        self.assertIn("Please check that you select a correct user",str(reply.data,'utf-8'))

        #insert C into A's blacklist
        reply = app.post("/blacklist/3",follow_redirects = True)
        self.assertIn("User 3 added to the black list.",str(reply.data,'utf-8'))
        
        #insert B into the blacklist of A
        reply = app.post("/blacklist/2",follow_redirects = True)
        self.assertIn("User 2 added to the black list.",str(reply.data,'utf-8'))
        
        
        
    
        """Test myaccount"""
        app.get("/logout",follow_redirects = True)

        #test delete account
        #create a user
        formdatA = dict(email="delete@xmpl.com",
                    firstname="delete",
                    lastname="delete",
                    password="delete",
                    date_of_birth="11/11/1911")
        reply = app.post("/create_user", data = formdatA, follow_redirects = True)
        app.post("/login", data = dict(email="delete@xmpl.com", password = "delete"), follow_redirects = True)
        reply = app.delete("/myaccount")
        self.assertEqual(303,reply.status_code)
        

        
        
        logFormA = dict(email = emailA,password = "userA")
        reply = app.post("/login",data=logFormA,follow_redirects=True)
        self.assertIn("Hi userA",str(reply.data,'utf-8'))

        real_psw = "userA"
        fake_psw = "user_A"
        
        #test get method
        reply = app.get("/myaccount/modify", follow_redirects = True)
        self.assertIn("Modify your data", str(reply.data,'utf-8'))

        #try change data with wrong psw
        changeuserA = dict(email="Axmpl@xmpl.com",
                    firstname="NewUserA",
                    lastname="userA",
                    password=fake_psw,
                    newpassword = "",
                    repeatnewpassword = "",
                    date_of_birth="11/11/1911")
        reply = app.post("/myaccount/modify", data = changeuserA, follow_redirects = True)
        self.assertIn("Insert your password to apply changes",str(reply.data,'utf-8'))
        
        #change A firstname 
        changeuserA = dict(email="Axmpl@xmpl.com",
                    firstname="NewUserA",
                    lastname="userA",
                    password=real_psw,
                    newpassword = "",
                    repeatnewpassword = "",
                    date_of_birth="11/11/1911")
        reply = app.post("/myaccount/modify", data = changeuserA, follow_redirects = True)
        self.assertIn("NewUserA",str(reply.data,'utf-8'))

        #change A email with B email

        changeuserA = dict(email="Bxmpl@xmpl.com",
                    firstname="NewUserA",
                    lastname="userA",
                    password="userA",
                    newpassword = "",
                    repeatnewpassword = "",
                    date_of_birth="11/11/1911")
        reply = app.post("/myaccount/modify", data = changeuserA, follow_redirects = True)
        with tested_app.app_context():
            bmail = db.session.query(User).filter(User.email == "Bxmpl@xmpl.com").first()
        self.assertIn("This email is already used! Try with another one.",str(reply.data,'utf-8'))

        #change A password
        changepswA = dict(email="Axmpl@xmpl.com",
                    firstname="NewUserA",
                    lastname="userA",
                    password="userA",
                    newpassword = "newuserA",
                    repeatnewpassword = "newuserA",
                    date_of_birth="11/11/1911")
        app.post("/myaccount/modify", data = changepswA, follow_redirects = True)
        with tested_app.app_context():
            usr = db.session.query(User).filter(User.email == "Axmpl@xmpl.com").first()
            psw = "newuserA".encode('utf-8')
            self.assertEqual(True,bcrypt.checkpw(psw, usr.password))
        
        app.post("/logout")
        reply = app.get("/create_user")
        self.assertIn("Create a account",str(reply.data,'utf-8'))
        
    def tearDown(self):
           
        #Ensures that the database is emptied for next unit test
        
        with tested_app.app_context():
            db.session.remove()
            db.drop_all()

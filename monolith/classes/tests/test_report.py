import unittest
from flask import render_template
from flask_login import current_user
from monolith.app import app as tested_app
from monolith.forms import LoginForm
from freezegun import freeze_time
from monolith.app import db
from monolith.database import Images, Messages, User, msglist
import datetime

class TestReport(unittest.TestCase):
    tested_app.config['WTF_CSRF_ENABLED'] = False


    def setUp(self):
        """
        Creates a new database for the unit test to use
        """
        tested_app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
        db.init_app(tested_app)
        with tested_app.app_context():
            db.create_all()
            db.session.commit()


    @freeze_time("2021-11-13 15:00:00")
   # Register some users in the app 
    def test_send_and_report(self):

        A = 2
        B = 3
        C = 4

        app = tested_app.test_client()

        # Register new user A
        emailA = "Axmpl@xmpl.com"
        emailB = "Bxmpl@xmpl.com"
        emailC = "Cxmpl@xmpl.com"
        formdatA = dict(email="Axmpl@xmpl.com",
                    firstname="userA",
                    lastname="userA",
                    password="userA",
                    date_of_birth="11/11/1111")
        reply = app.post("/create_user", data = formdatA, follow_redirects = True)
        
        # Register new user B
        formdatB = dict(email="Bxmpl@xmpl.com",
                    firstname="userB",
                    lastname="userB",
                    password="userB",
                    date_of_birth="11/11/1111")
        reply = app.post("/create_user", data = formdatB, follow_redirects = True)

        # Register new user C
        formdatC = dict(email="Cxmpl@xmpl.com",
                    firstname="userC",
                    lastname="userC",
                    password="userC",
                    date_of_birth="11/11/1111")
        reply = app.post("/create_user", data = formdatC, follow_redirects = True)

        # Check that in the returned HTML page (that is the user list), the string contains the users "userA", "userB", "userC"
        self.assertIn("First name: userA",str(reply.data,'utf-8'))
        self.assertIn("First name: userB",str(reply.data,'utf-8'))
        self.assertIn("First name: userC",str(reply.data,'utf-8'))
        self.assertIn("Last name: userA",str(reply.data,'utf-8'))
        self.assertIn("Last name: userB",str(reply.data,'utf-8'))
        self.assertIn("Last name: userC",str(reply.data,'utf-8'))
        self.assertIn("e-mail: "+emailA,str(reply.data,'utf-8'))
        self.assertIn("e-mail: "+emailB,str(reply.data,'utf-8'))
        self.assertIn("e-mail: "+emailC,str(reply.data,'utf-8'))


        # Test login userA
        logFormA = dict(email = emailA,password = "userA")
        reply = app.post("/login",data=logFormA,follow_redirects=True)
        self.assertIn("Hi userA",str(reply.data,'utf-8'))
        
        # Test a new message sent from A to B
        my_title = "title_from_A_to_B"
        my_content = "content_from_A_to_B"
        msg = str({"destinator": [B],"title":my_title,"date_of_delivery":"2021-11-13","time_of_delivery":"15:10","content":my_content, "font":"Times New Roman"})
        msg = msg.replace("\'","\"")
        data = dict(payload=msg)
        reply = app.post("/message/new" ,data = data, follow_redirects = True)
        print(reply.data)

        #Check presence of message in db
        with tested_app.app_context():
            _messages = db.session.query(Messages).all()
            _alternativeMSG = db.session.query(Messages).filter(Messages.title == my_title).first()
        self.assertEqual(len(_messages),1)
        self.assertEqual(_alternativeMSG.title,my_title)



        # Logout userA
        reply = app.get("/logout",follow_redirects=True)



    def tearDown(self):
        """
        Ensures that the database is emptied for next unit test
        """
        with tested_app.app_context():
            db.session.remove()
            db.drop_all()

'''
        # Send a msg from UserA to UserB
        sendMsgForm = dict(destinator = "Bxmpl@xmpl.com", title = my_title, content = my_content, date_of_delivery = my_date, time = my_time)
        #TODO: how to insert date in the message ??
        reply = app.post("/message/new",data=sendMsgForm,follow_redirects=True)
        self.assertIn("Your message have been send",str(reply.data,'utf-8'))
'''
        

#TODO--> CHECK IF THE USER B HAS RECEIVED THE MESSAGE --> IF THE MESSAGE IS CORRECTLY RECEIVED, THEN USE A MESSAGE WITH BAD WORDS AND TRY THE REPORT FUNCTIONALITY

'''
# Check the delivery of the message
@freeze_time("2021-11-13 15:10:00")
    def test_deliver_msg(self):
        app = tested_app.test_client()

        # Login userB
        emailB = "Bxmpl@xmpl.com"
        logFormA = dict(email = emailB,password = "userB")
        reply = app.post("/login",data=logFormA,follow_redirects=True)
        self.assertIn("Hi userB",str(reply.data,'utf-8'))


        # Check that the message is in the mailbox
'''
import unittest
from flask import render_template
from flask_login import current_user
from monolith.app import app as tested_app
from monolith.forms import LoginForm
import datetime

class TestReport(unittest.TestCase):
    tested_app.config['WTF_CSRF_ENABLED'] = False
    

   # Register some users in the app 
    def register_usrs(self):
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



    # User A sends a msg to UserB
    @freeze_time("2021-11-13 15:00:00")
    def test_send(self):
        # Test login userA
        logFormA = dict(email = emailA,password = "userA")
        reply = app.post("/login",data=logFormA,follow_redirects=True)
        self.assertIn("Hi userA",str(reply.data,'utf-8'))

        # Check empty mailbox at the beginning for userA
        reply = app.get("/messages",follow_redirects = True)
        self.assertIn("Your mailbox is empty!",str(reply.data,'utf-8'))


        # Some useful variables (remember the time is freezed at the beginning of the test)
        today_ = datetime.datetime.now
        _5min_from_now = today_ + datetime.timedelta(minutes=5) #the message has to be delivered 5 minutes from now
        
        my_title = "My title"
        my_content = "My content"
        my_date = _5min_from_now_strftime("%d/%m/%Y")
        my_time = _5min_from_now_strftime("%H:%M")


        # Send a msg from UserA to UserB
        sendMsgForm = dict(destinator = "Bxmpl@xmpl.com", title = my_title, content = my_content, date_of_delivery = my_date, time = my_time)
        #TODO: how to insert date in the message ??
        reply = app.post("/message/new",data=sendMsgForm,follow_redirects=True)
        self.assertIn("Your message have been send",str(reply.data,'utf-8'))

        # Logout userA
        reply = app.get("/logout",follow_redirects=True)



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
import unittest
from flask import render_template
from flask_login import current_user
from monolith.app import app as tested_app
from monolith.forms import LoginForm
from freezegun import freeze_time
from monolith.app import db
from monolith.database import Images, Messages, User, msglist
from sqlalchemy import and_, or_, not_
from datetime import datetime,date

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
            self.populate_db()


    def populate_db(self):
    
        #insert user 1 && 2
        u1 = User()
        u1.email="u1"
        u1.id = 1
        u1.firstname="u1"
        u1.date_of_birth=date.fromisoformat('2021-12-04')
        u1.lastname ="u1"
        u1.ban_expired_date = None
        u1.set_password("u1")
        db.session.add(u1)

        
        u2 = User()
        u2.email="u2"
        u2.id = 2
        u2.firstname="u2"
        u2.date_of_birth=date.fromisoformat('2021-12-04')
        u2.lastname ="u2"
        u2.black_list.append(u1)
        u2.set_password("u2")
        u2.ban_expired_date = None
        db.session.add(u2)

        #Insert a message from u1 to u2

        #first message
        m1 = Messages()
        m1.id = 1
        m1.title="myTitle_from_u1_to_u2"
        m1.content="myContent_fuck_you fuck fuck"
        m1.date_of_delivery=date.fromisoformat('2021-11-14')
        m1.format="Times New Roman"
        m1.sender=u1.get_id()
        m1.bad_content = True
        m1.number_bad = 3
        m1.receivers.append(u2)
        db.session.add(m1)
        db.session.commit()

        #second message         
        m2 = Messages()
        m2.id = 2
        m2.title="myTitle_from_u1_to_u2"
        m2.content="myContent_fuck_you fuck fuck"
        m2.date_of_delivery=date.fromisoformat('2021-11-14')
        m2.format="Times New Roman"
        m2.sender=u1.get_id()
        m2.bad_content = True
        m2.number_bad = 3
        m2.receivers.append(u2)
        db.session.add(m2)
        db.session.commit()

        #third message
        m3 = Messages()
        m3.id = 3
        m3.title="myTitle_from_u1_to_u2"
        m3.content="myContent_fuck_you fuck fuck"
        m3.date_of_delivery=date.fromisoformat('2021-11-14')
        m3.format="Times New Roman"
        m3.sender=u1.get_id()
        m3.bad_content = True
        m3.number_bad = 3
        m3.receivers.append(u2)
        db.session.add(m3)
        db.session.commit()

        #fourth message
        m4 = Messages()
        m4.id = 4
        m4.title="myTitle_from_u1_to_u2"
        m4.content="myContent_fuck_you fuck fuck"
        m4.date_of_delivery=date.fromisoformat('2021-11-14')
        m4.format="Times New Roman"
        m4.sender=u1.get_id()
        m4.bad_content = True
        m4.number_bad = 3
        m4.receivers.append(u2)
        db.session.add(m4)
        db.session.commit()


    @freeze_time("2021-11-15 10:00:00")
    def test_report(self):

        u1 = 1
        u2 = 2

        app = tested_app.test_client()

        # Test login user u2 (the receiver of message)
        logFormA = dict(email = "u2",password = "u2")
        reply = app.post("/login",data=logFormA,follow_redirects=True)
        self.assertIn("Hi u2",str(reply.data,'utf-8'))

                
        #Check received msg for u2
        with tested_app.app_context():
            MSG = db.session.query(msglist,Messages).filter(msglist.c.user_id == u2).filter(msglist.c.msg_id == Messages.id).first()
            #MSG is a value formed by the fields of msgList table and the fields of Messages table
            #from MSG[0] to MSG[4] are fields of msgList
            #MSG[5] are fields of Messages, accessed by referring the by name (example MSG[5].title)
        my_msg = MSG[5]
        self.assertEqual(my_msg.title, "myTitle_from_u1_to_u2")
        

        msg_to_report_ID = my_msg.id

        # Check if the user 1 has zero report against him
        with tested_app.app_context():
            user1 = db.session.query(User).filter(User.id == 1).first()
        self.assertEqual(user1.n_report, 0)

        #Now report the msg because of "bad words"
        reply = app.post("/report_user/"+str(msg_to_report_ID),follow_redirects=True)
        
        # Check that the message exists in the database
        with tested_app.app_context():
            MSG = db.session.query(msglist,Messages).filter(msglist.c.user_id == u2).filter(msglist.c.msg_id == Messages.id).first()
        self.assertEqual(MSG[5].title, "myTitle_from_u1_to_u2")

        #Check the flag 'hasReported' of message and the response of report operation
        self.assertIn("The user has its reported counter incremented",str(reply.data,'utf-8'))
        self.assertEqual(MSG[4], True) #hasReported has to be true now

        # Check if the user 1 has one report against him
        with tested_app.app_context():
            user1 = db.session.query(User).filter(User.id == 1).first()
        self.assertEqual(user1.n_report, 1)

        #Check that if the same user report the same message, the counter is not incremented
        reply = app.post("/report_user/"+str(msg_to_report_ID),follow_redirects=True)
        self.assertIn("You have already reported this message!",str(reply.data,'utf-8'))
        

        #Report other 2 message to have a ban on user1
        reply = app.post("/report_user/2",follow_redirects=True)
        self.assertIn("The user has its reported counter incremented",str(reply.data,'utf-8'))

        reply = app.post("/report_user/3",follow_redirects=True)
        self.assertIn("The user has its reported counter incremented",str(reply.data,'utf-8'))

        reply = app.post("/report_user/4",follow_redirects=True)
        self.assertIn("The user reported has been banned",str(reply.data,'utf-8'))



        #Check the ban date on the user
        with tested_app.app_context():
            user1 = db.session.query(User).filter(User.id == 1).first()
        self.assertIsNotNone(user1.ban_expired_date)
        self.assertEqual("2021-11-18 00:00:00",str(user1.ban_expired_date))


        # Logout
        reply = app.get("/logout",follow_redirects=True)
        
        
        #Check that user 2 can login, because he has not been banned
        logForm_2 = dict(email = "u2",password = "u2")
        reply = app.post("/login",data=logForm_2,follow_redirects=True)
        self.assertIn("Hi u2",str(reply.data,'utf-8'))
        
        # Logout
        reply = app.get("/logout",follow_redirects=True)
        
        #Check that the user 1 is under ban, so he can't login
        logForm_1 = dict(email = "u1",password = "u1")
        reply = app.post("/login",data=logForm_1,follow_redirects=True)
        self.assertIn("Account under ban",str(reply.data,'utf-8'))

        
    #Check that after two day the account u1 is still banned and can't login
    @freeze_time("2021-11-17 10:00:00")
    def still_banned(self):
        app = tested_app.test_client()
        logForm_1 = dict(email = "u1",password = "u1")
        reply = app.post("/login",data=logForm_1,follow_redirects=True)
        self.assertIn("Account under ban",str(reply.data,'utf-8'))
        
        
    #Check that after the ban_expired_date the account u1 is no more banned and can normally login
    @freeze_time("2021-11-20 10:00:00")
    def no_more_banned(self):
        app = tested_app.test_client()
        
        #Check that before login the ban date is not None
        with tested_app.app_context():
            user1 = db.session.query(User).filter(User.id == 1).first()
        self.assertIsNotNone(user1.ban_expired_date)
        
        #Check login
        logForm_1 = dict(email = "u1",password = "u1")
        reply = app.post("/login",data=logForm_1,follow_redirects=True)
        self.assertIn("Hi u1",str(reply.data,'utf-8'))
        
        # Logout
        reply = app.get("/logout",follow_redirects=True)
        
        #Check on DB
        with tested_app.app_context():
            user1 = db.session.query(User).filter(User.id == 1).first()
        self.assertIsNone(user1.ban_expired_date)
        
        
    def tearDown(self):
           
        #Ensures that the database is emptied for next unit test
        
        with tested_app.app_context():
            db.session.remove()
            db.drop_all()

        

"""      
    @freeze_time("2021-11-13 15:15:00")
    def test_received_messages(self):

        app = tested_app.test_client()

        A = 2
        B = 3
        C = 4

        emailA = "Axmpl@xmpl.com"
        emailB = "Bxmpl@xmpl.com"
        emailC = "Cxmpl@xmpl.com"

        # Test login userB
        logFormB = dict(email = emailB,password = "userB")
        reply = app.post("/login",data=logFormB,follow_redirects=True)
        self.assertIn("Hi userB",str(reply.data,'utf-8'))

        # Test if the message has been delivered
        with tested_app.app_context():
            msgs_toB = db.session.query(Messages).filter(Messages.c.receivers == [B]).first()
        self.assertEqual(len(msgs_toB),1)
        self.assertEqual(msgs_toB.title,"title_from_A_to_B")
        print("-->")
        print(msgs_toB.content)
        

        #logout B
        reply = app.get("/logout",follow_redirects=True)


    
    def tearDown(self):
           
        #Ensures that the database is emptied for next unit test
        
        with tested_app.app_context():
            db.session.remove()
            db.drop_all()


        # Send a msg from UserA to UserB
        sendMsgForm = dict(destinator = "Bxmpl@xmpl.com", title = my_title, content = my_content, date_of_delivery = my_date, time = my_time)
        #TODO: how to insert date in the message ??
        reply = app.post("/message/new",data=sendMsgForm,follow_redirects=True)
        self.assertIn("Your message have been send",str(reply.data,'utf-8'))

        

#TODO--> CHECK IF THE USER B HAS RECEIVED THE MESSAGE --> IF THE MESSAGE IS CORRECTLY RECEIVED, THEN USE A MESSAGE WITH BAD WORDS AND TRY THE REPORT FUNCTIONALITY


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
"""
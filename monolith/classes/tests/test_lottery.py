import unittest
from flask import render_template
from flask_login import current_user
from monolith.app import app as tested_app, db

from monolith.background import lottery
from freezegun import freeze_time
from datetime import datetime

class TestLottery(unittest.TestCase):
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

    """ 
    def populate_db():

    """
        
    @freeze_time("2021-11-12")      #test with simulated date before the lottery deadline
    def test_lottery_intime(self):
        app = tested_app.test_client()

        #create users
        # register new user A
        emailA = "Axmpl@xmpl.com"
       
        formdatA = dict(email="Axmpl@xmpl.com",
                    firstname="userA",
                    lastname="userA",
                    password="userA",
                    date_of_birth="11/11/1911")
        reply = app.post("/create_user", data = formdatA, follow_redirects = True)
        
        

        logDatA = dict(email = emailA, password = "userA")
        
        
        #testing lottery with no current user --> should give a 304 status code
        reply = app.get("/lottery",follow_redirects = True)
        self.assertIn("Your are not login to the website", str(reply.data, 'utf-8'))


        #testing lottery/number (select number) with no current user 
        #--> should give a 304 status code
        reply = app.post("/lottery/17",follow_redirects = True)
        self.assertEqual(304, reply.status_code)

        reply = app.get("/lottery/17",follow_redirects = True)
        self.assertRaises(RuntimeError)

        #login with A
        reply = app.post("/login", data = logDatA, follow_redirects = True)
        self.assertIn("Hi userA", str(reply.data, 'utf-8'))


        #Use the logged account A to test lottery 
        #--> should give a page where there is the string "You have selected no number yet, ..."
        reply = app.get("/lottery",follow_redirects = True)
        #self.assertEqual(304, reply)
        self.assertIn("You have selected no number yet, hurry up! Luck is not waiting for you!",str(reply.data,'utf-8'))
        

        #Use the logged account A to test lottery, pick number out of range 
        #--> should give a page where there is the string "You choose an invalid number for the lottery! ..."
        reply = app.post("/lottery/201",follow_redirects = True)
        #self.assertEqual(304,reply.status_code)
        self.assertIn("You choose an invalid number for the lottery! You can choose only number from 1 to 99 !", str(reply.data,'utf-8'))

        reply = app.post("/lottery/-201",follow_redirects = True)
        #self.assertEqual(304,reply.status_code)
        self.assertIn("You choose an invalid number for the lottery! You can choose only number from 1 to 99 !", str(reply.data,'utf-8'))

        #Use the logged account A to test lottery, pick valid number
        #--> should give a page where there is the string "You select the number 18 Good Luck!"
        reply = app.post("/lottery/18",follow_redirects = True)
        self.assertIn("You select the number 18! Good Luck!", str(reply.data,'utf-8'))

        reply = app.get("/lottery",follow_redirects = True)
        self.assertIn("You already select the number. This is your number: 18", str(reply.data,'utf-8'))
        #pick again a valid number

        reply = app.post("/lottery/15",follow_redirects = True)
        self.assertIn("You already select the number 18! Good Luck!", str(reply.data,'utf-8'))

        reply = app.post("/lottery/199",follow_redirects = True)
        self.assertIn("You choose an invalid number for the lottery! You can choose only number from 1 to 99 !", str(reply.data,'utf-8'))
        #self.assertEqual(304, reply.status_code)

        app.get("/logout",follow_redirects = True)

        #to test the lottery we can create 100 accounts and play a different number with each one
        for account in range(1,99):
            this_create = dict(email ="account"+str(account)+"@account.com",
                    firstname="account"+str(account),
                    lastname = "account"+str(account),
                    password="account"+str(account),
                    date_of_birth="11/11/1911"
                    )
            this_login = dict(
                email ="account"+str(account)+"@account.com",
                password="account"+str(account),
            )
            #create nth user
            reply = app.post("/create_user", data = this_create, follow_redirects = True)
            #log nth user
            reply = app.post("/login", data = this_login, follow_redirects = True)
            self.assertIn("Hi account"+str(account), str(reply.data, 'utf-8'))
            #guess 'account' number
            reply = app.post("/lottery/"+str(account),follow_redirects = True)
            self.assertIn("You select the number "+str(account)+"! Good Luck!", str(reply.data,'utf-8'))
            reply = app.get("/logout")
            print(this_create)
            print(this_login)
        #test winning condition
        reply = lottery.apply()
        self.assertEqual([],reply.result)           #maybe this test work but something is wrong in sending the email to the winner
        
    


    @freeze_time("2021-11-27")      #testing lottery after the deadline
    def test_lottery_outoftime(self):
        app = tested_app.test_client()

        # register new user A
        emailA = "Axmpl@xmpl.com"
        formdatA = dict(email="Axmpl@xmpl.com",
                    firstname="userA",
                    lastname="userA",
                    password="userA",
                    date_of_birth="11/11/1911")
        reply = app.post("/create_user", data = formdatA, follow_redirects = True)

        #login with A and play
        logDatA = dict(email = emailA, password = "userA")
        reply = app.post("/login", data = logDatA, follow_redirects = True)
        self.assertIn("Hi userA", str(reply.data, 'utf-8'))

        reply = app.post("/lottery/17", follow_redirects = True)
        #self.assertEqual(304, reply.status_code)
        self.assertIn("You cannot choose any more a number, the time to partecipate to lottery is expired! Try next month!", str(reply.data,'utf-8'))


        
    def tearDown(self):
        """
        Ensures that the database is emptied for next unit test
        """
        with tested_app.app_context():
            db.session.remove()
            db.drop_all()

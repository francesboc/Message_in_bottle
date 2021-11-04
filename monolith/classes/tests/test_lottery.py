import unittest
from flask import render_template
from flask_login import current_user
from monolith.app import app as tested_app
#from background import lottery
from freezegun import freeze_time
from datetime import datetime

class TestLottery(unittest.TestCase):
    tested_app.config['WTF_CSRF_ENABLED'] = False

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
                    date_of_birth="11/11/1111")
        reply = app.post("/create_user", data = formdatA, follow_redirects = True)
        
        

        logDatA = dict(email = emailA, password = "userA")
        
        
        #testing lotter with no current user
        reply = app.get("/play")
        self.assertEqual(403, reply.status_code)

        reply = app.post("/play/17")
        self.assertEqual(403, reply.status_code)

        #login with A and play
        reply = app.post("/login", data = logDatA, follow_redirects = True)
        #get no number
        reply = app.get("/play")
        self.assertEqual(403, reply.status_code)
        self.assertIn("You have selected no number yet, hurry up! Luck is not waiting for you!",str(reply.data,'utf-8'))

        #pick a number out of range

        reply = app.post("/play/201")
        self.assertEqual(304,reply.status_code)
        self.assertIn("You choose an invalid number for the lottery! You can choose only number from 1 to 99 !", str(reply.data,'utf-8'))

        reply = app.post("/play/-201")
        self.assertEqual(304,reply.status_code)
        self.assertIn("You choose an invalid number for the lottery! You can choose only number from 1 to 99 !", str(reply.data,'utf-8'))

        #pick a valid number

        reply = app.post("/play/18")
        self.assertIn("You select the number 18 Good Luck!", str(reply.data,'utf-8'))

        #pick again a valid number

        reply = app.post("/play/99")
        self.assertIn("You already select the number: 18!", str(reply.data,'utf-8'))
        self.assertEqual(304, reply.status_code)

        #test winning condition

    @freeze_time("2021-11-27")      #testing lottery after the deadline
    def test_lottery_outoftime(self):
        app = tested_app.test_client()

        emailA = "Axmpl@xmpl.com"
        logDatA = dict(email = emailA, password = "userA")
        #login with A and play
        #reply = app.post("/login", data = logDatA, follow_redirects = True)

        reply = app.post("/play/17")
        self.assertEqual(304, reply.status_code)
        self.assertIn("You can't choose any more a number, the time to partecipate to lottery is expired! Try next month!", str(reply.data,'utf-8'))



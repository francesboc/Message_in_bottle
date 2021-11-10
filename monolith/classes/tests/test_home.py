import unittest
from flask import render_template
from flask_login import current_user
from monolith.app import app as tested_app
from monolith.forms import LoginForm
from freezegun import freeze_time
from monolith.app import db
from monolith.database import Images, Messages, User, msglist
from sqlalchemy import and_, or_, not_
from datetime import datetime,date, timedelta
import wget

class TestHome(unittest.TestCase):
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
            
    @freeze_time("2021-11-10")
    def populate_db(self):
    
        #insert user 2
        u1 = User()
        u1.email="u1"
        u1.id = 1
        u1.firstname="u1"
        u1.date_of_birth=date.fromisoformat('2000-12-04')
        u1.lastname ="u1"
        u1.lottery_points = 20
        u1.ban_expired_date = None
        u1.set_password("u1")
        db.session.add(u1)

        #insert user 2
        u2 = User()
        u2.email="u2"
        u2.id = 2
        u2.firstname="u2"
        u2.date_of_birth=date.fromisoformat('2000-12-04')
        u2.lastname ="u2"
        u2.lottery_points = 5
        u2.set_password("u2")
        u2.ban_expired_date = None
        db.session.add(u2)
        db.session.commit()
        
    
    
    def test_home_page(self):
        
        app = tested_app.test_client()
        
        # Get the home page with no user logged in
        reply = app.get('/', follow_redirects = True)
        self.assertNotIn("Logged In!", str(reply.data, 'utf-8'))
        
        # Get the home page with user logged in
        formdata = dict(email = "u1", password = "u1")
        reply = app.post('/login', data = formdata, follow_redirects = True)
        self.assertIn("Hi u1 !",str(reply.data, 'utf-8'))
        reply = app.get('/', follow_redirects = True)
        self.assertNotIn("Your are not login to the website", str(reply.data, 'utf-8'))
      
    
    def test_home_images(self):
        
        app = tested_app.test_client()
        
        today = str(datetime.now().strftime('%Y-%m-%d'))
        tomorrow = str((datetime.now()+timedelta(days=1)).strftime('%Y-%m-%d'))
        in5minutes = str((datetime.now()+timedelta(minutes=5)).strftime('%H:%M'))
        
        # Login a user
        formdata = dict(email = "u1", password = "u1")
        reply = app.post('/login', data = formdata, follow_redirects = True)
        self.assertIn("Hi u1 !",str(reply.data, 'utf-8'))
        
        # Send a message that contains an image
        payload = str({"destinator": "2","title":"CtoU2","date_of_delivery":tomorrow,"time_of_delivery":in5minutes,"content":"CtoU2","font":"Serif"})
        payload = payload.replace("\'","\"")

        wget.download("https://github.com/fluidicon.png","/tmp",bar=None) # downloading an image
        image = "/tmp/fluidicon.png"
        data = dict(payload=payload, file=(open(image, 'rb'), image))
        reply = app.post("/message/new" ,data = data, follow_redirects = True)
        print(reply.data)
        # checking the presence of the image in db
        with tested_app.app_context():
            _images = db.session.query(Images.id).all()
        self.assertEqual(len(_images),1)
        
        
        # Try to download the image
        reply = app.get("/image/1", follow_redirects = True)
        downloaded_img = (open(image, 'rb'))
        self.assertEqual(reply.data, downloaded_img.read()) #Confronting the downloaded image with the real one
    
    
    def test_home_messages_and_draft(self):
        
        app = tested_app.test_client()
        
        today = str(datetime.now().strftime('%Y-%m-%d'))
        tomorrow = str((datetime.now()+timedelta(days=1)).strftime('%Y-%m-%d'))
        in5minutes = str((datetime.now()+timedelta(minutes=5)).strftime('%H:%M'))
        
        # Login a user
        formdata = dict(email = "u1", password = "u1")
        reply = app.post('/login', data = formdata, follow_redirects = True)
        self.assertIn("Hi u1 !",str(reply.data, 'utf-8'))
        
        # Send a message without images
        payload = str({"destinator": "2","title":"AtoB","date_of_delivery":today,"time_of_delivery":in5minutes,"content":"AtoB","font":"Serif"})
        payload = payload.replace("\'","\"")
        data = dict(payload=payload)
        reply = app.post("/message/new" ,data = data, follow_redirects = True)
        
        #Check presence of message in db
        with tested_app.app_context():
            _messages = db.session.query(Messages).all()
        self.assertEqual(len(_messages),1)
        
        # Test the home route for message sent
        reply = app.get('/message/send', follow_redirects = True)
        self.assertIn("Your message have been send", str(reply.data, "utf-8"))
        
        # Test the home route for message draft
        reply = app.get('/message/draft', follow_redirects = True)
        self.assertIn("Your message is saved in your draft folder", str(reply.data, "utf-8"))
        
        # Logout the user
        app.get('/logout', follow_redirects=True)
        
        # Test the home route for message with no user logged in
        reply = app.get('/message/send', follow_redirects = True)
        self.assertIn("Your are not login to the website", str(reply.data, "utf-8"))
        
        # Test the home route for message draft
        reply = app.get('/message/draft', follow_redirects = True)
        self.assertIn("Your are not login to the website", str(reply.data, "utf-8"))
        
        
    
    def tearDown(self):
        """
        Ensures that the database is emptied for next unit test
        """
        with tested_app.app_context():
            db.session.remove()
            db.drop_all()
        

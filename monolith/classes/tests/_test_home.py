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
            
    
    def populate_db(self):
    
        #insert user 2
        u1 = User()
        u1.email="u1"
        u1.id = 1
        u1.firstname="u1"
        u1.date_of_birth=date.fromisoformat('2021-12-04')
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
        u2.date_of_birth=date.fromisoformat('2021-12-04')
        u2.lastname ="u2"
        u2.lottery_points = 5
        u2.black_list.append(u1)
        u2.set_password("u2")
        u2.ban_expired_date = None
        db.session.add(u2)
        db.session.commit()
        
        # Insert a message in DB
        m1 = Messages()
        m1.id = 1
        m1.title="myMessage with image"
        m1.content="myContent_1"
        m1.date_of_delivery=date.fromisoformat('2021-11-14')
        m1.format="Times New Roman"
        m1.sender=u1.get_id()
        m1.bad_content = True
        m1.number_bad = 3
        m1.receivers.append(u2)
        db.session.add(m1)
        db.session.commit()
        
        
        #inser an image in DB
        wget.download("https://github.com/fluidicon.png","/tmp",bar=None) # downloading an image
        tmp_image = "/tmp/fluidicon.png"
        
        imm = Images()
        imm.id = 1
        imm.image = open(tmp_image, 'rb')
        imm.message = db.Column(db.Integer, db.ForeignKey('messages.id'))
        imm.mimetype = ""
    
    
    def test_home_page(self):
        
        app = tested_app.test_client()
        
        # Get the home page with no user logged in
        reply = app.get('/', data = formdata, follow_redirects = True)
        self.assertNotIn("Logged In!", reply.data)
        
        # Get the home page with user logged in
        formdata = dict(email = "u1", password = "u1")
        reply = app.post('/login', data = formdata, follow_redirects = True)
        self.assertIn("Hi u1 !",str(reply.data, 'utf-8'))
        reply = app.get('/', follow_redirects = True)
        self.assertIn("Logged In!", reply.data)
      
        
    def test_home_images(self):
        
        
        
        

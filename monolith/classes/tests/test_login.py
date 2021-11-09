import unittest
from flask import render_template
from datetime import date, timedelta, datetime
from flask_login import current_user
from sqlalchemy.sql.expression import true
from monolith.app import app as tested_app
from monolith.app import db
from monolith.database import User
from monolith.forms import LoginForm
from freezegun import freeze_time


class TestApp(unittest.TestCase):

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
        u1.lottery_points = 20
        u1.ban_expired_date = None
        u1.set_password("u1")
        db.session.add(u1)

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
    
    @freeze_time('2021-10-10')
    def test_login(self):
        app = tested_app.test_client()
        with tested_app.app_context():
            #access with user u1
        
            formdata = dict(email = "u1", password = "u1")
            reply = app.post('/login', data = formdata, follow_redirects = True)
            self.assertIn("Hi u1 !",str(reply.data, 'utf-8'))
            
            #test logout
            reply = app.get('/logout', follow_redirects=true)
            self.assertIn("Your are not login to the website",str(reply.data,'utf-8'))

            #login wrong password again
            formdata = dict(email="u1", password="uxxxxxxxxxx")
            reply = app.post('/login', data = formdata, follow_redirects = True)
            self.assertIn("Login failed",str(reply.data, 'utf-8'))
            
            #login with wrong email
            formdata = dict(email="ux", password="u1")
            reply = app.post('/login', data = formdata, follow_redirects = True)
            self.assertIn("Login failed",str(reply.data, 'utf-8'))

            
            # test on user banned trying to log in
            u2 = db.session.query(User).filter(User.id == 2).first()
            u2.ban_expired_date = datetime.fromisoformat('2021-11-10')
            db.session.commit()

            formdata = dict(email = "u2", password = "u2")
            reply = app.post('/login', data = formdata, follow_redirects = True)
            self.assertIn("Account under ban",str(reply.data,'utf-8'))
            
            
            #test on user banned with expired ban date 
            u2.ban_expired_date = datetime.fromisoformat('2021-09-10')
            db.session.commit()

            formdata = dict(email = "u2", password = "u2")
            reply = app.post('/login', data = formdata, follow_redirects = True)
            self.assertIn("Hi u2 !",str(reply.data,'utf-8'))
   
   
    def tearDown(self):
        """
        Ensures that the database is emptied for next nit test
        """
        with tested_app.app_context():
            db.session.remove()
            db.drop_all()
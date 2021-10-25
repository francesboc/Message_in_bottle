
import pytest
import unittest

from monolith.database import User,Message
from datetime import date

from flask import Flask
from monolith.app import db



class TestDB(unittest.TestCase):

    def setUp(self):
        """
        Creates a new database for the unit test to use
        """
        self.app = Flask(__name__)
        db.init_app(self.app)
        with self.app.app_context():
            db.create_all()
            self.populate_db() # Your function that adds test data.
        

    
    
    def populate_db(self):

        #insert user 1 && 2
        u1 = User()
        u1.email="ale"
        u1.firstname="q"
        u1.date_of_birth=date.fromisoformat('2021-12-04')
        u1.lastname ="q"
        u1.set_password("123")
        db.session.add(u1)
       

        u2 = User()
        u2.email="fra"
        u2.firstname="f"
        u2.date_of_birth=date.fromisoformat('2021-12-04')
        u2.lastname ="b"
        u2.set_password("123")
        db.session.add(u2)
        db.session.commit()
        

        #insert a message from u1 to u1 and u2
        m1 = Message()
        m1.title="Title"
        m1.content="Content"
        m1.date=date.fromisoformat('2021-12-04')
        m1.sender=u1.get_id()
        m1.receivers.append(u1)
        m1.receivers.append(u2)
        db.session.add(m1)
        db.session.commit()
        q = db.session.query(Message)
        for row in q:
            print(row.sender,row.title)

        
    
    def test_1(self):
        #Query message
        with self.app.app_context():
            self.populate_db()
            q = db.session.query(Message)
            for row in q:
                print(row.sender)
        self.tearDown()
        
        
    
    
    def tearDown(self):
        """
        Ensures that the database is emptied for next unit test
        """
        self.app = Flask(__name__)
        db.init_app(self.app)
        with self.app.app_context():
            db.drop_all()









       

        

       
            
        
    
  

       

       
        







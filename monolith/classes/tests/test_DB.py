import pytest
import unittest

from monolith.database import User,Messages, msglist, blacklist
from sqlalchemy.exc import IntegrityError
from datetime import date, datetime, timedelta
from sqlalchemy.sql import text
from sqlalchemy import update
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
            
            db.session.commit()
    

    def test_db(self):

        with self.app.app_context():
        
            #insert user 1 && 2
            u1 = User()
            u1.id = 1
            u1.email="u1"
            u1.firstname="u1"
            u1.date_of_birth=date.fromisoformat('2021-12-04')
            u1.lastname ="u1"
            u1.set_password("u1")
            u1.set_lottery_number(10)
            u1.set_points(5)
            db.session.add(u1)
        
            self.assertEqual(10,u1.lottery_ticket_number)
            self.assertEqual(5,u1.lottery_points)


            u2 = User()
            u2.id = 2
            u2.email="u2"
            u2.firstname="u2"
            u2.date_of_birth=date.fromisoformat('2021-12-04')
            u2.lastname ="u2"
            u2.set_password("u2")
            u2.set_lottery_number(10)
            u2.set_points(5)
            db.session.add(u2)
            
            self.assertEqual(u2.lottery_points, 5) # test to increase coverage
        
       

        
            #insert a message from u1 to u1 and u2 and u3
            # date >= today
            m1 = Messages()
            m1.id = 1
            m1.title="Title"
            m1.set_delivery_date(date.fromisoformat('2021-09-04'))
            #m1.date_of_delivery=date.fromisoformat('2021-09-04')
            m1.set_sender(2)
            m1.set_content("Prova")
            db.session.add(m1)
            db.session.commit()
            self.assertEqual(2,m1.sender)
            self.assertEqual("Prova",m1.content)
            self.assertEqual(datetime.fromisoformat('2021-09-04'),m1.date_of_delivery)
            self.assertEqual(1,m1.get_id())


       

           
    def tearDown(self):
        """
        Ensures that the database is emptied for next unit test
        """
        self.app = Flask(__name__)
        db.init_app(self.app)
        with self.app.app_context():
            db.drop_all()









       

        

       
            
        
    
  

       

       
        







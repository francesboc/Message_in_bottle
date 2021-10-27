import pytest
import unittest

from monolith.database import User,Messages, msglist
from datetime import date
from sqlalchemy.sql import text

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
            self.populate_db() # Your function that adds test data.
    

    def populate_db(self):

        
        
         #insert user 1 && 2
        u1 = User()
        u1.email="q"
        u1.firstname="q"
        u1.date_of_birth=date.fromisoformat('2021-12-04')
        u1.lastname ="q"
        u1.set_password("123")
        db.session.add(u1)
        
       
        u2 = User()
        u2.email="bip"
        u2.firstname="y"
        u2.date_of_birth=date.fromisoformat('2021-12-04')
        u2.lastname ="b"
        u2.black_list.append(u1)
        u2.set_password("123")
        db.session.add(u2)
        db.session.commit()
        
        #insert a message from u1 to u1 and u2
        # date >= today
        m1 = Messages()
        m1.title="Title"
        m1.content="Content"
        m1.date_of_delivery=date.fromisoformat('2021-12-04')
        m1.sender=u1.get_id()
        m1.receivers.append(u1)
        m1.receivers.append(u2)
        db.session.add(m1)
        db.session.commit()


        #insert a message from u1 to u1 and u2
        # date >= today
        m2 = Messages()
        m2.title="Title2"
        m2.content="Content2"
        m2.date_of_delivery=date.fromisoformat('2019-12-04')
        m2.sender=u1.get_id()
        m2.receivers.append(u1)
        m2.receivers.append(u2)
        db.session.add(m2)
        db.session.commit()
       
       
       

    def test_1(self):
       
        #Query message
        with self.app.app_context():
            # All Message that a user <k> sended, with title, content, (list)
            k = "q"
            q1 = db.session.query(Messages.content,Messages.title, Messages.date_of_delivery,User.firstname).filter(Messages.sender==User.id).filter(User.firstname==k)

            #All the message received until now
            q2 = db.session.query(Messages.content,Messages.title, Messages.date_of_delivery,User.firstname).filter(Messages.date_of_delivery<=date.today()).filter(Messages.receivers.any())

            #All the message of user K minor of today
            q3 = db.session.query(Messages.title,Messages.content,User.firstname).filter(Messages.date_of_delivery<=date.today()).filter(User.firstname==k).join(User,Messages.receivers)


            print(q3)

            for row in q3:
                print(row)
          
            
           
    def tearDown(self):
        """
        Ensures that the database is emptied for next unit test
        """
        self.app = Flask(__name__)
        db.init_app(self.app)
        with self.app.app_context():
            db.drop_all()









       

        

       
            
        
    
  

       

       
        







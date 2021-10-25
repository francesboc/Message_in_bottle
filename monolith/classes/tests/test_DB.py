import pytest
import unittest

from monolith.database import User,Message, msglist
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
<<<<<<< HEAD

        
=======
>>>>>>> e820ab4f383ca8c09647f5a09fcf741809343a1e
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
        u2.set_password("123")
        db.session.add(u2)
        db.session.commit()
        
<<<<<<< HEAD
        

=======
>>>>>>> e820ab4f383ca8c09647f5a09fcf741809343a1e
        #insert a message from u1 to u1 and u2
        # date >= today
        m1 = Message()
        m1.title="Title"
        m1.content="Content"
        m1.date=date.fromisoformat('2021-12-04')
        m1.sender=u1.get_id()
        m1.receivers.append(u1)
        m1.receivers.append(u2)
      


        #insert a message from u1 to u1 and u2
        # date >= today
        m2 = Message()
        m2.title="Title2"
        m2.content="Content2"
        m2.date=date.fromisoformat('2019-12-04')
        m2.sender=u1.get_id()
        m2.receivers.append(u1)
        m2.receivers.append(u2)
        db.session.add(m2)
        db.session.commit()
       
       
       

    def test_1(self):
       
        #Query message
        with self.app.app_context():
<<<<<<< HEAD
            
            # All Message that a user <k> sended, with title, content, (list)
            k = "q"
            q1 = db.session.query(Message.content,Message.title, Message.date,User.firstname).filter(Message.sender==User.id).filter(User.firstname==k)

            #All the message received until now
            q2 = db.session.query(Message.content,Message.title, Message.date,User.firstname).filter(Message.date<=date.today()).filter(Message.receivers.any())


           
            print(q3)

            for row in q3:
                print(row)
          
            
           
=======
            self.populate_db()
            q = db.session.query(Message)
            for row in q:
                print(row.sender)
        self.tearDown()
        
>>>>>>> e820ab4f383ca8c09647f5a09fcf741809343a1e
    def tearDown(self):
        """
        Ensures that the database is emptied for next unit test
        """
        self.app = Flask(__name__)
        db.init_app(self.app)
        with self.app.app_context():
            db.drop_all()









       

        

       
            
        
    
  

       

       
        







import pytest
import unittest

from monolith.database import User,Messages, msglist, blacklist
from sqlalchemy.exc import IntegrityError
from datetime import date, datetime, timedelta
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
        u1.email="u1"
        u1.firstname="u1"
        u1.date_of_birth=date.fromisoformat('2021-12-04')
        u1.lastname ="u1"
        u1.set_password("u1")
        db.session.add(u1)
        
       
        u2 = User()
        u2.email="u2"
        u2.firstname="u2"
        u2.date_of_birth=date.fromisoformat('2021-12-04')
        u2.lastname ="u2"
        u2.black_list.append(u1)

        # try:
            #u2.black_list.append(u1)
        u2.set_password("u2")
        db.session.add(u2)
        db.session.commit()
        # except IntegrityError as e:
        #     print("Erore")


        
        
        #insert a message from u1 to u1 and u2
        # date >= today
        m1 = Messages()
        m1.title="Title"
        m1.content="Content"
        m1.date_of_delivery=date.fromisoformat('2021-09-04')
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
        m2.date_of_delivery=date.fromisoformat('2021-09-30')
        m2.sender=u1.get_id()
        m2.receivers.append(u1)
        m2.receivers.append(u2)
        db.session.add(m2)
        db.session.commit()
       
       
       

    def test_1(self):
       
        #Query message
        with self.app.app_context():
            # All Message that a user <k> sended, with title, content, (list)
            k = ""
            q1 = db.session.query(Messages.content,Messages.title, Messages.date_of_delivery,User.firstname).filter(Messages.sender==User.id).filter(User.firstname==k)

            #All the message received until now
            q2 = db.session.query(Messages.content,Messages.title, Messages.date_of_delivery,User.firstname).filter(Messages.date_of_delivery<=date.today()).filter(Messages.receivers.any())

            #All the message of user K minor of today
            q3 = db.session.query(Messages.title,Messages.content,User.firstname).filter(Messages.date_of_delivery<=date.today()).filter(User.firstname==k).join(User,Messages.receivers)

            q = db.session.query(Messages.sender,User.id,Messages.title,Messages.date_of_delivery).join(User,Messages.receivers)#.filter(Messages.date_of_delivery==date.today())

            #Blacklist of User K
            q4 = db.session.query(User.firstname,blacklist.c.black_id).filter(User.id==blacklist.c.user_id).filter(User.firstname==k)

            #List of messages of User K without the messages that the blocked users sended to me
            q5 = db.session.query(Messages.sender,Messages.title,Messages.content,Messages.date_of_delivery,User.id).filter(Messages.sender!=(q4)).filter(User.firstname==k).join(User,Messages.receivers)

            message = db.session.query(Messages.date_of_delivery).filter(Messages.date_of_delivery<= date.today())

            #time = str(datetime.datetime.today().minute + 200)
            
            messages = db.session.query(Messages.id, Messages.sender, Messages.title, Messages.content, User.id,msglist.c.notified).filter(Messages.date_of_delivery<(datetime.now()-timedelta(minutes=10))).filter(Messages.id==msglist.c.msg_id,User.id == msglist.c.user_id)



          

            # for row in message:
            #     print(row)

            for row in messages:
                print(row)


           

           
          
            
           
    def tearDown(self):
        """
        Ensures that the database is emptied for next unit test
        """
        self.app = Flask(__name__)
        db.init_app(self.app)
        with self.app.app_context():
            db.drop_all()









       

        

       
            
        
    
  

       

       
        







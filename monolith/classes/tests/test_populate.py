import pytest
import unittest

from monolith.database import User,Messages, msglist, blacklist
from sqlalchemy.exc import IntegrityError
from datetime import date, datetime, timedelta
from sqlalchemy.sql import text
from sqlalchemy import update
from flask import Flask
from monolith.app import db

from monolith.app import create_app
from monolith.database import User,db,Messages, msglist
from random import randrange


#This Script is really useful if you want to populate database
# User are defined ui where i goes from 1 to n User[email : ui (*you can insert yours*),firstname : ui, lastname : ui , blacklist : empty, password : ui ]

#Messages are defined mi where i goes from 1 to n 
# Date of delivery are generated from (now - k*10(minutes)) where k is generated randomly(9)

#KEEEP ATTENTION : REMEBER TO DELETE THE DATABASE BEFORE LAUNCH THIS SCRIPT COULD BE INTEGRITY ERROR OTHERWISE

class TestPopulate(unittest.TestCase):


    def setup (self):
        app = create_app()
        db.init_app(app)
      
        with app.app_context():
            db.create_all()
            db.session.commit()
            #self.populate_db() # Your function that adds test data.
            g = db.session.query(User.id,User.firstname,User.filter_isactive)
            for row in g:
                print(row)


    def populate_db (self):
        
        for i in range(10):
            ui = User()
            ui.email="u"+str(i)    #Insert your mail
            ui.firstname="u"+str(i)
            ui.date_of_birth=date.fromisoformat('2021-12-04')
            ui.lastname ="u"+str(i)
            ui.set_password("u"+str(i))
            db.session.add(ui)
            db.session.commit()
        
        for i in range(10):
            mi = Messages()
            
            mi.title="Title"+str(i)
            mi.content="Content"+str(i)
            k = randrange(9)+1
            mi.date_of_delivery=datetime.now()-timedelta(minutes=k*10)
            mi.sender = i
            mi.receivers.append(db.session.query(User).filter(User.id==k).first())
            db.session.add(mi)
            db.session.commit()

    
    def test_1(self):
        self.setup()


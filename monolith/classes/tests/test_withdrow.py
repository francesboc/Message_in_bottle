from datetime import date, timedelta
import unittest
from sqlalchemy import insert
from monolith.app import app as tested_app
from monolith.app import db
from monolith.database import Images, Messages, User, msglist
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

        #Insert a message from u1 to u2

        #draft message
        md = Messages()
        md.id = 3
        md.title="myDraft_from_u1_to_u2"
        md.content="myContent_is_draft"
        md.date_of_delivery=date.fromisoformat('2021-12-25')
        md.format="Times New Roman"
        md.sender=u1.get_id()
        md.receivers.append(u2)
        md.bad_content = True
        md.number_bad = 0
        md.is_draft = True     
        db.session.add(md)
        db.session.commit()

        #Sent messages
        m1 = Messages()
        m1.id = 4
        m1.title="myTitle_from_u1_to_u2"
        m1.content="myContent_fuck_you fuck fuck"
        m1.date_of_delivery=date.fromisoformat('2021-11-14')
        m1.format="Times New Roman"
        m1.sender=u1.get_id()
        m1.bad_content = True
        m1.is_draft = False
        m1.number_bad = 3
        m1.receivers.append(u2)
        db.session.add(m1)
        db.session.commit()
        
        m2 = Messages()
        m2.id = 5
        m2.title="myTitle_from_u2_to_u1"
        m2.content="myContent_fuck_you fuck fuck"
        m2.date_of_delivery=date.fromisoformat('2021-11-14')
        m2.format="Times New Roman"
        m2.sender=u2.get_id()
        m2.bad_content = True
        m2.is_draft = False
        m2.number_bad = 3
        m2.receivers.append(u1)
        db.session.add(m2)
        db.session.commit()


    def test_msgWithdrow(self):
        app = tested_app.test_client()
        #TODO for non draft check enough points
        #TODO test withdrow with non existing msg
        with tested_app.app_context():
            logA = dict(email = 'u1', password = 'u1')
            reply = app.post('/login', data = logA, follow_redirects = True)

            #withdrow a draft message
            reply = app.delete('/message_withdrow/3')
            #search msg_id into the db
            msg = db.session.query(Messages).filter(Messages.id == 3).first()
            self.assertEqual(None,msg)

            #u1 has enough point to withdrow the message he sent
            reply = app.delete('/message_withdrow/4')
            #search msg_id into the db
            msg = db.session.query(Messages).filter(Messages.id == 4).first()
            self.assertEqual(None,msg)
            #check user have spent his points
            points = db.session.query(User).filter(User.id == 1).first()
            self.assertEqual(10,points.lottery_points)
            app.post('/logout')  

            #withdrow a draft
            reply = app.delete('/message_withdrow/3')
            msg = db.session.query(Messages).filter(Messages.id == 3).first()
            self.assertEqual(None,msg)

            #u2 has no enough point to withdrow his message
            logB = dict(email = 'u2', password = 'u2')
            reply = app.post('/login', data = logB, follow_redirects = True)

            reply = app.delete('/message_withdrow/5')
            msg = db.session.query(Messages).filter(Messages.id == 5).first()
            print(msg)
            self.assertNotEqual(None,msg)



        
        
    def tearDown(self):
        """
        Ensures that the database is emptied for next unit test
        """
        with tested_app.app_context():
            db.session.remove()
            db.drop_all()
            
from datetime import date, timedelta
import unittest
from monolith.app import app as tested_app
from monolith.app import db
from monolith.database import Images, Messages, User, msglist
from freezegun import freeze_time
import wget

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

    @freeze_time(date.today())
    def test1_message(self):
        """Function used to test send of different messages"""
        app = tested_app.test_client()

        # Useful constant
        # corresponding recipient index in message form
        A = 2
        B = 3
        C = 4
        emailA = "usera@example.com"
        emailB = "userb@example.com"
        emailC = "userc@example.com"
        loginA = dict(email = emailA,password = "userA")
        loginB = dict(email = emailB,password = "userB")
        loginC = dict(email = emailC,password = "userC")

        # register new user A
        data = dict(email=emailA,
                    firstname="userA",
                    lastname="userA",
                    password="userA",
                    date_of_birth="11/11/1111")
        reply = app.post("/create_user", data = data, follow_redirects = True)

        # register new user B
        data = dict(email=emailB,
                    firstname="userB",
                    lastname="userB",
                    password="userB",
                    date_of_birth="11/11/1111")
        reply = app.post("/create_user", data = data, follow_redirects = True)

        # register new user C
        data = dict(email=emailC,
                    firstname="userC",
                    lastname="userC",
                    password="userC",
                    date_of_birth="11/11/1111")
        reply = app.post("/create_user", data = data, follow_redirects = True)
        
        reply = app.post("/login",data=loginA,follow_redirects=True)
        
        # Send a message from User A to User B without images
        payload = str({"destinator": [B],"title":"AtoB","date_of_delivery":str(date.today()),"time_of_delivery":"12:42","content":"AtoB"})
        payload = payload.replace("\'","\"")
        data = dict(payload=payload)
        
        reply = app.post("/message/new" ,data = data, follow_redirects = True)
        #Check presence of message in db
        with tested_app.app_context():
            _messages = db.session.query(Messages).all()
        self.assertEqual(len(_messages),1)

        # Send a message from User C to User B and A without images
        app.get('/logout', follow_redirects=True)
        app.post("/login",data=loginC,follow_redirects=True)
        payload = str({"destinator": [A,B],"title":"CtoAB","date_of_delivery":str(date.today()),"time_of_delivery":"12:42","content":"CtoAB"})
        payload = payload.replace("\'","\"")
        data = dict(payload=payload)
        
        reply = app.post("/message/new" ,data = data, follow_redirects = True)
        #Check presence of message in db
        with tested_app.app_context():
            recipient_count = db.session.query(msglist.c.user_id).filter(msglist.c.msg_id == 2).group_by(msglist.c.user_id).count()
        self.assertEqual(recipient_count,2)
        
        # Send a message that contains an image
        payload = str({"destinator": [A],"title":"CtoA","date_of_delivery":str(date.today()),"time_of_delivery":"12:42","content":"CtoA"})
        payload = payload.replace("\'","\"")

        wget.download("https://github.com/fluidicon.png","/tmp",bar=None) # downloading an image
        image = "/tmp/fluidicon.png"
        data = dict(payload=payload, file=(open(image, 'rb'), image))
        reply = app.post("/message/new" ,data = data, follow_redirects = True)
        # checking the presence of the image in db
        with tested_app.app_context():
            _images = db.session.query(Images.id).all()
        self.assertEqual(len(_images),1)
        
        with tested_app.app_context():
            _users = db.session.query(User.email, User.firstname, User.lastname).all()
            _messages = db.session.query(Messages.id, Messages.title, Messages.content, Messages.date_of_delivery, Messages.sender).all()
        
        for row in _users:
            print(row)
        
        for row in _messages:
            print(row)

    @freeze_time(date.today()+timedelta(days=2))
    def test2_message(self):
        return

    def tearDown(self):
        """
        Ensures that the database is emptied for next unit test
        """
        with tested_app.app_context():
            db.session.remove()
            db.drop_all()
            
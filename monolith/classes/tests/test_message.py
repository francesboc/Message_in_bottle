from datetime import date, datetime, timedelta
from re import T
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

    @freeze_time(datetime.now())
    def test1_message_new(self):
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

        today = str(datetime.now().strftime('%Y-%m-%d'))
        tomorrow = str((datetime.now()+timedelta(days=1)).strftime('%Y-%m-%d'))
        in1minute = str((datetime.now()+timedelta(minutes=1)).strftime('%H:%M'))
        in2minute = str((datetime.now()+timedelta(minutes=2)).strftime('%H:%M'))
        in3minute = str((datetime.now()+timedelta(minutes=3)).strftime('%H:%M'))
        in5minutes = str((datetime.now()+timedelta(minutes=5)).strftime('%H:%M'))
        in10minutes = str((datetime.now()+timedelta(minutes=10)).strftime('%H:%M'))

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
        
        # Try to get /message/new
        reply = app.get("/message/new")
        self.assertEqual(reply.status_code,200)

        # Send a message from User A to User B without images
        payload = str({"destinator": [B],"title":"AtoB","date_of_delivery":today,"time_of_delivery":in5minutes,"content":"AtoB","font":"Serif"})
        payload = payload.replace("\'","\"")
        data = dict(payload=payload)
        
        reply = app.post("/message/new" ,data = data, follow_redirects = True)
        #Check presence of message in db
        with tested_app.app_context():
            _messages = db.session.query(Messages).all()
        self.assertEqual(len(_messages),1)

        # Try to send a message with empty title
        payload = str({"destinator": [B],"title":"","date_of_delivery":today,"time_of_delivery":in5minutes,"content":"AtoB","font":"Serif"})
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
        payload = str({"destinator": [A,B],"title":"CtoAB","date_of_delivery":today,"time_of_delivery":in5minutes,"content":"CtoAB","font":"Serif"})
        payload = payload.replace("\'","\"")
        data = dict(payload=payload)
        
        reply = app.post("/message/new" ,data = data, follow_redirects = True)
        #Check presence of message in db with two users
        with tested_app.app_context():
            recipient_count = db.session.query(msglist.c.user_id).filter(msglist.c.msg_id == 2).group_by(msglist.c.user_id).count()
        self.assertEqual(recipient_count,2)
        
        # Send a message that contains an image
        payload = str({"destinator": [A],"title":"CtoA","date_of_delivery":tomorrow,"time_of_delivery":in5minutes,"content":"CtoA","font":"Serif"})
        payload = payload.replace("\'","\"")

        wget.download("https://github.com/fluidicon.png","/tmp",bar=None) # downloading an image
        image = "/tmp/fluidicon.png"
        data = dict(payload=payload, file=(open(image, 'rb'), image))
        reply = app.post("/message/new" ,data = data, follow_redirects = True)
        # checking the presence of the image in db
        with tested_app.app_context():
            _images = db.session.query(Images.id).all()
        self.assertEqual(len(_images),1)

        # Save a drafted message with only one recipient and an image in drafted of C
        payload = str({"destinator": [A],"title":"","date_of_delivery":"","time_of_delivery":"","content":"","font":""})
        payload = payload.replace("\'","\"")
        data = dict(payload=payload, file=(open(image, 'rb'), image))
        
        reply = app.post("/message/draft" ,data = data, follow_redirects = True)
        #Check presence of draft message in db
        with tested_app.app_context():
            _messages = db.session.query(Messages.id, Messages.is_draft).filter(Messages.is_draft == True).all()
            message_id = _messages[0].id
            image_id = db.session.query(Images.id, Images.message).filter(Images.message == message_id).first().id
        self.assertEqual(len(_messages),1)

        # Getting message to edit to refresh updates
        reply = app.get('/edit/'+str(message_id))

        ### DOESN T WORK SINCE HERE ######
        # Let C modify the drafted message by delete and add a different recipient and include an new image and delete the old one
        payload = str({"destinator": [B],"title":"","date_of_delivery":"","time_of_delivery":"","content":"","font":""})
        payload = payload.replace("\'","\"")
        userToDelete = [A]
        imageToDelete = [image_id]
        data = dict(payload=payload,file=(open(image, 'rb'), image),delete_image_ids=imageToDelete,delete_user_ids=userToDelete,message_id=message_id)
        
        reply = app.post("/message/draft" ,data = data, follow_redirects = True)
        #Check the recipients of the drafted message, there should be only B
        with tested_app.app_context():
            _receivers = db.session.query(User.id, Messages.id).join(User, Messages.receivers).filter(Messages.id ==message_id).all()
        self.assertEqual(len(_receivers),1)
        self.assertEqual(_receivers[0].id, B)

        with tested_app.app_context():
            _users = db.session.query(User.email, User.firstname, User.lastname).all()
            _messages = db.session.query(Messages.id, Messages.title, Messages.content, Messages.date_of_delivery, Messages.sender).all()
        
        #for row in _users:
        #    print(row)
        #
        #for row in _messages:
        #    print(row)

    def tearDown(self):
        """
        Ensures that the database is emptied for next unit test
        """
        with tested_app.app_context():
            db.session.remove()
            db.drop_all()
            
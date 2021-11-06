from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship
from sqlalchemy import update
from werkzeug.security import check_password_hash, generate_password_hash
from sqlalchemy.orm import relationship
import bcrypt

db = SQLAlchemy()


msglist = db.Table('msglist',
   
    db.Column('msg_id', db.Integer, db.ForeignKey('messages.id'), primary_key=True),
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('read',db.Boolean, default=False),
    db.Column('notified',db.Boolean, default=False),
    db.Column('hasReported', db.Boolean, default=False) #this is to know if a user has already reported a specific message

)

blacklist = db.Table('blacklist',
    
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('black_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
)

class User(db.Model):

    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.Unicode(128), nullable=False)
    firstname = db.Column(db.Unicode(128))
    lastname = db.Column(db.Unicode(128))
    password = db.Column(db.Unicode(128))
    date_of_birth = db.Column(db.DateTime)
    is_active = db.Column(db.Boolean, default=True)
    is_admin = db.Column(db.Boolean, default=False)
    is_anonymous = False
    filter_isactive = db.Column(db.Boolean, default=False)
    n_report = db.Column(db.Integer, default = 0) #number of report that the user received 
    ban_expired_date = db.Column(db.DateTime, default = None) #data a cui finisce il ban dell'utente
    lottery_ticket_number = db.Column(db.Integer, default = -1) #lottery ticker number 0-99
    lottery_points = db.Column(db.Integer, default = 0) #points gained with the monthly lottery
    
    black_list = relationship('User',
        secondary=blacklist,
        primaryjoin=id==blacklist.c.user_id,
        secondaryjoin=id==blacklist.c.black_id,
        backref="user_id",
        lazy = 'dynamic')
    
    def __init__(self, *args, **kw):
        super(User, self).__init__(*args, **kw)
        self._authenticated = False

    def set_password(self, password):
        self.password = bcrypt.hashpw(password.encode('utf8'), bcrypt.gensalt())

    @property
    def is_authenticated(self):
        return self._authenticated

    def authenticate(self, password):
        #checked = check_password_hash(self.password, password) OLD
        checked = bcrypt.checkpw(password.encode('utf-8'), self.password) #check password hash and salt
        self._authenticated = checked
        return self._authenticated

    def get_id(self):
        return self.id

    def set_lottery_number(self, val):
        self.lottery_ticket_number = val
    

class Messages(db.Model):
    
    __tablename__ = 'messages'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    sender = db.Column(db.Integer, db.ForeignKey('user.id'))
    receivers = relationship('User', secondary=msglist)
    date_of_delivery = db.Column(db.DateTime)
    content = db.Column(db.Text)
    title = db.Column(db.Text)
    bad_content = db.Column(db.Boolean)
    number_bad = db.Column(db.Integer)
    images = relationship("Images", cascade="all,delete", backref="messages")
    is_draft = db.Column(db.Boolean, default=False)
    
    
    def __init__(self, *args, **kw):
        super(Messages, self).__init__(*args, **kw)

    def set_sender(self, val):
        self.sender = val

    def set_receiver(self, val):
        self.receiver = val

    def set_content(self, txt_):
        self.content = txt_

    def set_delivery_date(self, val):
        self.date_of_delivery = val

    def get_id(self):
        return self.id  

class Images(db.Model):

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    image = db.Column(db.LargeBinary, nullable=False)
    message = db.Column(db.Integer, db.ForeignKey('messages.id'))
    mimetype = db.Column(db.Text, nullable=False)

    def __init__(self, *args, **kw):
        super(Images, self).__init__(*args, **kw)
    
   
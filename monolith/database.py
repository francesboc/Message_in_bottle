from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship
from sqlalchemy import update
from werkzeug.security import check_password_hash, generate_password_hash
from sqlalchemy.orm import relationship


db = SQLAlchemy()

msglist = db.Table('msglist', 
    db.Column('msg_id', db.Integer, db.ForeignKey('message.id'), primary_key=True),
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True)
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

    black_list = db.Column(db.String, default="PROVA") #We assume that thi string will be of the following format: id1-id2-...-idN
                                    #To search if a user is in the blacklist simple do a search in the string.
                                    #To add user in the blacklist simple do an append operation
    
    user = relationship("Messages")
    
    def __init__(self, *args, **kw):
        super(User, self).__init__(*args, **kw)
        self._authenticated = False

    def set_password(self, password):
        self.password = generate_password_hash(password)

    @property
    def is_authenticated(self):
        return self._authenticated

    def authenticate(self, password):
        checked = check_password_hash(self.password, password)
        self._authenticated = checked
        return self._authenticated

    def get_id(self):
        return self.id  
    
    
class Message(db.Model):

    __tablename__='message'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(64))
    content = db.Column(db.String(1024), nullable=False)
    date = db.Column(db.DateTime)
    receivers = relationship('User', secondary=msglist)
    sender = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, *args, **kw):
        super(Message, self).__init__(*args, **kw)

        


    def add_to_black_list(id_to_update, id_to_add_blacklist):
        #check existing id
        exists = db.session.query(User.id).filter_by(id=id_to_add_blacklist).first() is not None
        if exists:
            _user_to_update = db.session.query(User).filter_by(id=id_to_add_blacklist).first() #obtain the user
            blck_list = _user_to_update.black_list
            _user_to_update.black_list = blck_list + "-" + str(id_to_add_blacklist)
            db.session.add(_user_to_update)
            db.session.commit()
            #tmp_s = blvalue#.String.python_type
            #print(type(tmp_s))
            #print('DEBUG: ' + blvalue + '-'+str(id_to_add_blacklist))
            #stmt = db.session.update(User).where(User.id==id_to_update).values(black_list=blvalue + '-'+str(id_to_add_blacklist))
        else:
            #managing error of non existing user
            print('ERRORE utente non esistente')


class Messages(db.Model):
    
    __tablename__ = 'messages'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    sender = db.Column(db.Integer, db.ForeignKey('user.id'))
    receiver = db.Column(db.Integer)
    date_of_delivery = db.Column(db.DateTime)
    content = db.Column(db.Text)

    
    def __init__(self, *args, **kw):
        super(Messages, self).__init__(*args, **kw)

    def set_sender(self, val):
        self.sender = val

    def set_receiver(self, val):
        self.receiver = val

    def set_delivery_date(self, val):
        self.date_of_delivery = val

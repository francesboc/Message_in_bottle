from datetime import date, datetime, timedelta
from celery import Celery
from celery.schedules import crontab
import random 
from smtplib import SMTPRecipientsRefused



BACKEND = BROKER = 'redis://localhost:6379'
celery = Celery(__name__, backend=BACKEND, broker=BROKER)


celery.conf.timezone = 'Europe/Rome'

_APP = None

@celery.on_after_configure.connect
def setup_periodic_task(sender, **kwargs):



    # Calls check_messages() task every 5 minutes to send email for unregisred users
    sender.add_periodic_task(300.0, check_messages.s(), name='checking messages every 5 minutes')
    sender.add_periodic_task(crontab(hour=12, minute = 0, day_of_month=27), lottery.s(), name = 'lottery extraction')

# Task for sending notification mail

@celery.task
def check_messages():
    global _APP
    # lazy init
    if _APP is None:
        from monolith.app import create_app, Message, Mail
        from monolith.database import User,db,Messages, msglist, Images, blacklist
        from sqlalchemy import update
       
        

        app = create_app()
        mail = Mail(app)
        db.init_app(app)
        with app.app_context():
            #Checking all the messages not yet delivered that needs to be notified
            _messages = db.session.query(Messages.id, Messages.title, Messages.content, 
                    Messages.date_of_delivery, User.id, User.is_active,
                    User.email, msglist.c.notified, Messages.sender)\
                .filter(Messages.date_of_delivery<=(datetime.now()))\
                .filter(Messages.is_draft==False, msglist.c.read==False) \
                .filter(Messages.id==msglist.c.msg_id,User.id == msglist.c.user_id,msglist.c.notified==False)
            for result in _messages:
                """Background task to send an email with Flask-Mail."""
                # Generating the email
                subject = result[1]
                body = result[2]
                to_email = result[6]
                receiver_id = result[4]
                msg_id = result[0]
                message_sender = result[8]
                user_is_active = result[5]

                # Check if the sender is in the blacklist of the receiver
                _blacklist = db.session.query(blacklist.c.user_id, blacklist.c.black_id) \
                    .filter(blacklist.c.user_id == receiver_id) \
                    .filter(blacklist.c.black_id == message_sender).first()

                if _blacklist is None: # receivers doesn't block sender
                    
                    if user_is_active:
                        # we need to notify the user for a new message
                        email_data = {
                            'subject': 'You received a new message!',
                            'to': to_email,
                            'body': 'Check the application for new messages'
                        }
                    else:
                        # we need to notify the unregistered user via email
                        email_data = {
                            'subject': subject,
                            'to': to_email,
                            'body': body
                        }
                        
                    msg = Message(email_data['subject'], sender=app.config['MAIL_DEFAULT_SENDER'],recipients=[email_data['to']])
                    msg.body = email_data['body']

                    # Take images to attach it to email
                    _images = db.session.query(Images.id,Images.image, Images.mimetype, Images.message)\
                            .filter(Images.message == msg_id).all()
                        
                    for image in _images:
                        msg.attach(str(image.id), image.mimetype, image.image)

                    try:
                        mail.send(msg)
                    except SMTPRecipientsRefused:
                        print("Error in sending E-mail")

                

                # updating notified status
                stmt = (
                    update(msglist).
                    where(msglist.c.msg_id==msg_id, msglist.c.notified == False, msglist.c.user_id==receiver_id).
                    values(notified=True)
                )
                db.session.execute(stmt)
            db.session.commit()
    else:
        app = _APP
    return []

@celery.task
def notify(sender_id,receiver, message):
    global _APP
    # lazy init
    if _APP is None:
        from monolith.app import create_app, Message, Mail
        from monolith.database import User,db,Messages, msglist
        from sqlalchemy import update
        from datetime import datetime

        #TO FIX
        app = create_app()
        mail = Mail(app)
        db.init_app(app)
        with app.app_context():
        

            sender = db.session.query(User.email).filter(User.id==sender_id).first()
            m = db.session.query(Messages.title, Messages.content).filter(Messages.id==message).first()

            receiver_mail = db.session.query(User.email).filter(User.id==receiver).first()

            subject = "Notification"
            body = "The User "+str(receiver_mail[0])+" has read the message with Title: \n"+str(m[0])+"\n Content: \n"+str(m[1])
            to_email = sender[0]
            

            email_data = {
                    
                 'subject': subject,
                 'to': to_email,
                 'body': body
             }
            msg = Message(email_data['subject'], sender=app.config['MAIL_DEFAULT_SENDER'],recipients=[email_data['to']])
            msg.body = email_data['body']
                
            try:
                mail.send(msg)
            except SMTPRecipientsRefused:
                    print("Error in sending E-mail")
   
    else:
        app = _APP
    return []



#task fo the lottery
#new version
@celery.task
def lottery():
    global _APP
    # lazy init
    if _APP is None:
        from monolith.app import create_app, Message, Mail
        from monolith.database import User,db,Messages, msglist
        from sqlalchemy import update

        app = create_app()
        mail = Mail(app)
        db.init_app(app)
        with app.app_context():
            winner = random.randrange(1,100)#exctract a random number in [1,99]
            players = db.session.query(User).filter(User.lottery_ticket_number != -1)     #users who play the lottery
            for p in players:
                if p.lottery_ticket_number == winner:      # if player's number is the extracted number, then he wins
                    p.set_points(5)                   #winner user gains 5 points
                    
                    """Background task to send an email with Flask-Mail."""
                    
                    subject = "Monthly Lottery Result"
                    body = "you have earned 5 points"
                    to_email = p.email
                    receiver_id = p.id
                    
                    email_data = {
                        'subject': subject,
                        'to': to_email,
                        'body': body
                    }
                    msg = Message(email_data['subject'], sender=app.config['MAIL_DEFAULT_SENDER'],recipients=[email_data['to']])
                    msg.body = email_data['body']
                    mail.send(msg)
                p.set_lottery_number(-1)        #restore default value for every player at the end of lottery extraction
            db.session.commit()  
            return []  
    else:
        app = _APP
    return []
   
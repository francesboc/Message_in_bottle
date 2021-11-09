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

    #Call do_task only one
    #sender.add_periodic_task(10.0,do_task.s())

    # Calls check_messages() task every 5 minutes to send email for unregisred users
    sender.add_periodic_task(300.0, check_messages.s(), name='checking messages every 5 minutes')
    sender.add_periodic_task(crontab(hour=12, minute = 0, day_of_month=27), lottery.s(), name = 'lottery extraction')
    # # Calls do_task() every 30 seconds
    # #sender.add_periodic_task(30.0, test.s('world'), expires=10)
    # sender.add_periodic_task(30.0, test.s('world'), expires=10)

    # # Executes every Monday morning at 7:30 a.m.
    # sender.add_periodic_task(
    #     crontab(hour=7, minute=30, day_of_week=1),
    #     test.s('Happy Mondays!'),
    # )

# Task for sending notification mail
@celery.task
def do_task():
    global _APP
    # lazy init
    if _APP is None:
        from monolith.app import create_app
        from monolith.database import User,db,Messages, msglist

        app = create_app()
        db.init_app(app)
        with app.app_context():
            #Query all messages in the interval dt = (-inf,now-10min) that are not notified
            messages = db.session.query(Messages.id, Messages.sender, Messages.title, Messages.content, User.id,msglist.c.notified) \
                                                .filter(Messages.date_of_delivery<(datetime.now()-timedelta(minutes=10))) \
                                                .filter(msglist.c.notified==False) \
                                                .filter(Messages.id==msglist.c.msg_id,User.id == msglist.c.user_id)
            print("ciao")
            for row in messages:
                print(row)
    else:
        app = _APP
    return []

@celery.task
def check_messages():
    global _APP
    # lazy init
    if _APP is None:
        from monolith.app import create_app, Message, Mail
        from monolith.database import User,db,Messages, msglist, Images
        from sqlalchemy import update
       
        

        app = create_app()
        mail = Mail(app)
        db.init_app(app)
        with app.app_context():
            #Checking all the messages not yet delivered for which the recipient has deregistered from system
            _messages = db.session.query(Messages.id, Messages.title, Messages.content, Messages.date_of_delivery, User.id, User.is_active, User.email, msglist.c.notified, Messages.sender)\
                .filter(User.is_active==False, Messages.date_of_delivery<=(datetime.now()))\
                .filter(Messages.id==msglist.c.msg_id,User.id == msglist.c.user_id,msglist.c.notified==False)
            for result in _messages:
                """Background task to send an email with Flask-Mail."""
                # Generating the email
                subject = result[1]
                body = result[2]
                to_email = result[6]
                receiver_id = result[4]
                msg_id = result[0]

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
def notify(sender_id,receiver):
    global _APP
    # lazy init
    if _APP is None:
        from monolith.app import create_app, Message, Mail
        from monolith.database import User,db,Messages, msglist
        from sqlalchemy import update

        #TO FIX
        app = create_app()
        mail = Mail(app)
        db.init_app(app)
        with app.app_context():
            print(sender_id)
            print(receiver)

            sender = db.session.query(User.email).filter(User.id==sender_id).first()
            receiver_mail = db.session.query(User.email).filter(User.id==receiver)

            subject = "Notification"
            body = "The User "+str(receiver_mail[0])+" has read the message"
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
   
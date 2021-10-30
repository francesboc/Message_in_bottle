from datetime import date, datetime, timedelta
from celery import Celery
##add
from celery.schedules import crontab




BACKEND = BROKER = 'redis://localhost:6379'
celery = Celery(__name__, backend=BACKEND, broker=BROKER)


celery.conf.timezone = 'Europe/Rome'

_APP = None

@celery.on_after_configure.connect
def setup_periodic_task(sender, **kwargs):

    #Call do_task only one
    sender.add_periodic_task(10.0,do_task.s())

    # # Calls do_task() every 10 seconds.
    # sender.add_periodic_task(10.0, test.s("H"), name='add every 10')

    # # Calls do_task() every 30 seconds
    # #sender.add_periodic_task(30.0, test.s('world'), expires=10)
    # sender.add_periodic_task(30.0, test.s('world'), expires=10)

    # # Executes every Monday morning at 7:30 a.m.
    # sender.add_periodic_task(
    #     crontab(hour=7, minute=30, day_of_week=1),
    #     test.s('Happy Mondays!'),
    # )

@celery.task
def test(args):
    print(args)



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



   
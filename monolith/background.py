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

    # Calls do_task() every 10 seconds.
    sender.add_periodic_task(10.0, test.s("H"), name='add every 10')

    # Calls do_task() every 30 seconds
    #sender.add_periodic_task(30.0, test.s('world'), expires=10)
    sender.add_periodic_task(30.0, test.s('world'), expires=10)

    # Executes every Monday morning at 7:30 a.m.
    sender.add_periodic_task(
        crontab(hour=7, minute=30, day_of_week=1),
        test.s('Happy Mondays!'),
    
    


    )

@celery.task
def test(args):
    print(args)



@celery.task
def do_task():
    global _APP
    # lazy init
    if _APP is None:
        from monolith.app import create_app
        from monolith.database import User,db,Messages
        from monolith.auth import login_manager
        
        app = create_app()
        db.init_app(app)
        with app.app_context():
            q1 = db.session.query(User.firstname)
            for row in q1:
                print(row)
        
    
    else:
        app = _APP
    
    

    return []



   
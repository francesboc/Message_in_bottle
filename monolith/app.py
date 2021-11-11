import datetime
import os
from flask import Flask
from flask_mail import Mail, Message 

from monolith.auth import login_manager
from monolith.database import User, db
from monolith.views import blueprints


def create_app():
    app = Flask(__name__)
    app.config['WTF_CSRF_SECRET_KEY'] = 'A SECRET KEY'
    app.config['SECRET_KEY'] = 'ANOTHER ONE'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///../mmiab.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Flask-Mail configuration
    app.config['MAIL_SERVER'] = 'smtp.gmail.com'
    app.config['MAIL_PORT'] = 587
    app.config['MAIL_USE_TLS'] = True
    app.config['MAIL_USERNAME'] = os.environ.get('FLASK_MAIL_USERNAME')
    app.config['MAIL_PASSWORD'] = os.environ.get('FLASK_MAIL_PASSWORD')
    app.config['MAIL_DEFAULT_SENDER'] = 'flaskapp10@gmail.com'

    for bp in blueprints:
        app.register_blueprint(bp)
        bp.app = app

    db.init_app(app)
    login_manager.init_app(app)
    db.create_all(app=app)

    # create a first admin user
    with app.app_context():
        q = db.session.query(User).filter(User.email == 'example@example.com', User.is_admin == True)
        user = q.first()
        if user is None: #creating the admin id it doesn't exist
            example = User()
            example.firstname = 'Admin'
            example.lastname = 'Admin'
            example.email = 'example@example.com'
            example.date_of_birth = datetime.datetime(2020, 10, 5)
            example.is_admin = True
            example.set_password('admin')
            db.session.add(example)
            db.session.commit()

    return app


app = create_app()

if __name__ == '__main__':
    app.run()

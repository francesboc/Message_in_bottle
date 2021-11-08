from flask import Blueprint, redirect, render_template
from flask.globals import request
from flask_login import login_user, logout_user


from datetime import datetime, date
from monolith.database import User, db
from monolith.forms import LoginForm

auth = Blueprint('auth', __name__)

#TODO: check also if the user is still active (isActive), because if not the user can't login
@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    error= ""
    code = 200
    if form.validate_on_submit():
        email, password = form.data['email'], form.data['password']
        q = db.session.query(User).filter(User.email == email)
        user = q.first()
        
        if user is not None and user.authenticate(password):
            if user.ban_expired_date is None:
                login_user(user)
                return redirect('/')
            elif user.ban_expired_date < datetime.today(): #the ban date has expired, need to set the ban_expired_date to None
                stmt = (update(User).where(User.email==email).values(ban_expired_date=None))
                db.session.execute(stmt)
                db.session.commit()
                return redirect('/')
            else: #The account is under ban, so the user can't login
                error="Account under ban"
                code = 401
                return render_template('login.html', form=form, error = error), code   #added error to detect bad login
        error="Login failed"
        code = 401
    return render_template('login.html', form=form, error = error, new_msg=2), code   #added error to detect bad login

@auth.route("/logout")
def logout():
    logout_user()
    return redirect('/')

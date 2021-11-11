from flask import Blueprint, redirect, render_template
from flask.globals import request
from flask_login import login_user, logout_user


from datetime import datetime, date
from monolith.database import User, db
from monolith.forms import LoginForm

auth = Blueprint('auth', __name__)

#route to login a user
@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    error= ""
    code = 200
    if form.validate_on_submit():
        email, password = form.data['email'], form.data['password'] #getting data from form
        q = db.session.query(User).filter(User.email == email)
        user = q.first()
        
        if user is not None and user.authenticate(password): #check that user exists and password is correct
            if user.ban_expired_date is None: #check ban on user
                login_user(user)
                return redirect('/')
            elif user.ban_expired_date < datetime.today(): #the ban date has expired, need to set the ban_expired_date to None
                usr = db.session.query(User).filter(User.email == email).first()
                usr.ban_expired_date = None
                db.session.commit()
                
                login_user(user)
                return redirect('/')
            else: #The account is under ban, so the user can't login
                error="Account under ban"
                code = 401
                return render_template('login.html', form=form, error = error), code   #added error to detect bad login
        error="Login failed"
        code = 401
    return render_template('login.html', form=form, error = error), code   #added error to detect bad login

#route to logout a user
@auth.route("/logout")
def logout():
    logout_user()
    return redirect('/')

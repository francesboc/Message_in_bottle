from flask import Blueprint, redirect, render_template
from flask.globals import request
from flask_login import login_user, logout_user

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
            login_user(user)
            return redirect('/')
        error="Login failed"
        code = 401
    return render_template('login.html', form=form, error = error, new_msg=2), code   #added error to detect bad login

@auth.route("/logout")
def logout():
    logout_user()
    return redirect('/')

from flask import Blueprint, redirect, render_template, request
from monolith.auth import current_user

from json import dumps
from monolith.database import User, db, Messages
from monolith.forms import UserForm
from datetime import date

users = Blueprint('users', __name__)

@users.route('/users')
def _users():
    #Filtering only registered users
    _users = db.session.query(User).filter(User.is_active==True)
    return render_template("users.html", users=_users)

@users.route('/users/start/<s>')
def _users_start(s):
    #Filtering only registered users
    users = db.session.query(User).filter(User.is_active==True).filter(User.firstname.startswith(s)).limit(2).all()
    if (len(users)>0):
        return dumps({'id':users[0].id,'firstname' : users[0].firstname,'lastname':users[0].lastname,'email':users[0].email})
    else:
        return dumps({})

@users.route('/myaccount', methods=['DELETE', 'GET'])
def myaccount():
    if request.method == 'DELETE':
        if current_user is not None and hasattr(current_user, 'id'):
            _user = db.session.query(User).filter(User.id == current_user.id).first()
            _user.is_active=False
            db.session.commit()
            return redirect("/logout",code=303)
    elif request.method == 'GET':
        if current_user is not None and hasattr(current_user, 'id'):
            return render_template("myaccount.html")
        else:
            return redirect("/")
    else:
        raise RuntimeError('This should not happen!')

"""@users.route('/blacklist/<id>')
def add = asdaasdfa"""

@users.route('/create_user', methods=['POST', 'GET'])
def create_user():
    form = UserForm()

    if request.method == 'POST':
        if form.validate_on_submit():
            new_user = User()
            form.populate_obj(new_user)
            """
            Password should be hashed with some salt. For example if you choose a hash function x, 
            where x is in [md5, sha1, bcrypt], the hashed_password should be = x(password + s) where
            s is a secret key.
            """
            new_user.set_password(form.password.data)
            db.session.add(new_user)
            db.session.commit()
            return redirect('/users')
    elif request.method == 'GET':
        return render_template('create_user.html', form=form)
    else:
        raise RuntimeError('This should not happen!')

##TESTING-------

@users.route('/messages')
def _messages():
    _messages = db.session.query(Messages)
    return render_template("get_msg.html", messages = _messages)


@users.route('/test_msg', methods=['GET'])
def test_msg():

    if request.method == 'GET':
        new_msg = Messages()
        new_msg.set_sender(99)
        new_msg.set_receiver(88)
        new_msg.set_delivery_date(date.today())

        db.session.add(new_msg)
        db.session.commit()
        return redirect('/messages')
    else:
        raise RuntimeError('This should not happen!')
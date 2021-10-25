from flask import Blueprint, redirect, render_template, request

from monolith.database import User, db, Messages
from monolith.forms import UserForm
from datetime import date

users = Blueprint('users', __name__)


@users.route('/users')
def _users():
    
    #print('get id ok' + _users.get_id())
    User.add_to_black_list(2, 3)
    _users = db.session.query(User)

    return render_template("users.html", users=_users)

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
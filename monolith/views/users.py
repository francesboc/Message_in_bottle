from flask import Blueprint, redirect, render_template, request
from monolith.auth import current_user


from monolith.database import User, db
from monolith.forms import UserForm

users = Blueprint('users', __name__)


@users.route('/users')
def _users():
    _users = db.session.query(User)
    return render_template("users.html", users=_users)

@users.route('/myaccount', methods=['DELETE', 'GET'])
def myaccount():
    if request.method == 'DELETE':
        if current_user is not None and hasattr(current_user, 'id'):
            _user = db.session.query(User).filter(User.id == getattr(current_user,'id')).first()
            _user.is_active=False
            db.session.commit()
            return redirect("/logout",code=303)
    elif request.method == 'GET':
        return render_template("myaccount.html")
    else:
        raise RuntimeError('This should not happen!')

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

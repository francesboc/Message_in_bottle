from flask import Blueprint, redirect, render_template, request, abort
from monolith.auth import current_user
import bcrypt

from json import dumps
from monolith.database import User, db, Messages, blacklist
from monolith.forms import UserForm

import datetime
from datetime import date, timedelta
from datetime import datetime as dt_

import hashlib
from sqlalchemy.exc import IntegrityError
from sqlalchemy import and_, or_, not_

users = Blueprint('users', __name__)

@users.route('/users')
def _users():
    #Filtering only registered users
    _users = db.session.query(User).filter(User.is_active==True)
    return render_template("users.html", users=_users)

#WHAT IS THIS?????
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
            #delete all messages?
            db.session.commit()
            return redirect("/logout",code=303)
    elif request.method == 'GET':
        if current_user is not None and hasattr(current_user, 'id'):
            return render_template("myaccount.html")
        else:
            return redirect("/")
    else:
        raise RuntimeError('This should not happen!')

@users.route('/blacklist',methods=['GET','DELETE'])
def get_blacklist():
    if current_user is not None and hasattr(current_user, 'id'):
        #check user exist and that is logged in
        if request.method == 'GET':
            #show the black list of the current user
            _user = db.session.query(blacklist.c.user_id).filter(blacklist.c.user_id==current_user.id).first()
            if _user is not None:
                #check user has at least 1 row into the blacklist table
                return render_template('black_list.html',action="This is your blacklist",black_list=_user)
            else:
                return render_template('black_list.html',action="Your blacklist is empty",black_list=[])
        elif request.method == 'DELETE':
            #Clear the blacklist
            st = blacklist.delete().where(blacklist.c.user_id == current_user.id)
            if st is not None:
                db.session.execute(st)   
                st = db.session.query(blacklist).filter(blacklist.c.user_id == current_user.id)
                return render_template('black_list.html',action="Your blacklist is now empty",black_list=st)
            else:
                return render_template('black_list.html',action="Your blacklist is already empty",black_list=[])
    else:
        return redirect("/")
        
@users.route('/blacklist/<target>', methods=['POST', 'DELETE'])
def add_to_black_list(target):
    #route that add target to the blacklist of user.
    if current_user is not None and hasattr(current_user, 'id'):
        #existUser = db.session.query(User.id,blacklist.c.user_id).filter(User.id==blacklist.c.user_id).filter(User.id==current_user.id).first()   # user db obj
        #existTarget = db.session.query(User.id,blacklist.c.black_id).filter(User.id==blacklist.c.user_id).filter(User.id==target).first()
        #check that both users are registered and that 'user' is exactly current user and nobody else
        existUser = db.session.query(User).filter(User.id==current_user.id).first()
        existTarget = db.session.query(User).filter(User.id==target).first()
        #add target into the user's blacklist
        if request.method == 'POST':
            #be sure that name is not into the blacklist already
            if existUser is not None and existTarget is not None: 
                try:
                    #try to add target into blacklist
                    existUser.black_list.append(existTarget)
                    db.session.commit()
                    #TODO: user_bl = db.session.query(User,blacklist).filter(User.id==blacklist.c.user_id).filter(User.id==current_user.id).first() is correct? //query dubbia
                    user_bl = db.session.query(User,blacklist,User).filter(User.id==blacklist.c.user_id).filte(User.id == blacklist.c.black_id).filter(User.id==current_user.id).first()
                    return render_template('black_list.html',action="User "+target+" added to the black list.",black_list = user_bl)
                except IntegrityError:
                    #if target already into the blacklist IntegrityError is raised by sqlAlchemy
                    bl = db.session.query(blacklist.c.user_id).filter()
                    return render_template('black_list.html',action="This user is already in your blacklist!",black_list = user_bl)
            else:
                #User or Target not in db
                return render_template('black_list.html',action="Please check that you select a correct user",black_list=[])    
        elif request.method == 'DELETE':
            #IMPORTANT: to show the user row of both current and black user we can query both and send to html a list [user,target]

            #Delete target from blacklist
            if existUser is not None and existTarget is not None:
                #Delete target from current user's blacklist
                bl_target = db.session.query(blacklist).filter(_and(blacklist.c.user_id == current_user.id, blacklist.c.black_id == target)).first()
                if bl_target is not None:
                    #check that target is already into the black list 
                    bl_ = db.session.query(blacklist).filter(blacklist.c.user_id == current_user.id).first()
                    st = blacklist.delete().where((blacklist.c.user_id == current_user)&(blacklist.c.black_id == target))
                    db.session.execute(st)
                    return render_template('black_list.html',action = "User "+target+" removed from your black list.",black_list= bl_)
                else:
                    bl_user = db.session.query(blacklist).filter(blacklist.c.user_id == current_user.id).first()
                    
                    return render_template('black_list.html', action ="This user is not in your blacklist", black_list= bl_)
            else:
                #User or Target not in db
                return render_template('black_list.html',action="Please check that you select a correct user",black_list=[]) 
    else:
        return redirect("/")

@users.route('/create_user', methods=['POST', 'GET'])
def create_user():
    form = UserForm()

    if request.method == 'POST':
        if form.validate_on_submit():
            new_user = User()
            form.populate_obj(new_user)
            
            if db.session.query(User).filter(User.email == form.email.data).first() is not None:
                #email already used so we have to ask to fill again the fields
                return render_template('create_user.html',form=form,error="Email already used!")
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

#showing all the messages (only for test. DO NOT USE THIS IN REAL APPLICATION)
@users.route('/messages')
def _messages():
    _messages = db.session.query(Messages)
    return render_template("get_msg.html", messages = _messages)


@users.route('/test_msg', methods=['GET'])
def test_msg():

    if request.method == 'GET':
        new_msg = Messages()
        new_msg.set_sender(2) #gianluca
        new_msg.set_receiver(1) #vincenzo

        today = date.today()
        tomorrow = today + datetime.timedelta(days=3)
        new_msg.set_delivery_date(tomorrow)
        

        db.session.add(new_msg)
        db.session.commit()
        return redirect('/messages')
    else:
        raise RuntimeError('This should not happen!')

#show recipient all message that have been delivered
@users.route('/show_messages', methods=['GET'])
def show_messages():
    #TODO check user is logged
    #TODO check sender not in black_list
    today = dt_.now()
    #today_dt = datetime.combine(date.today(), datetime.min.time())
    print(today)
    
    _messages = db.session.query(Messages).filter(and_(Messages.receivers == current_user.id, Messages.date_of_delivery <= today_dt))
    #_messages = db.session.query(Messages).filter(Messages.receiver == current_user.id)

    return render_template('get_msg.html',messages = _messages)


#select message to be read and access the reading panel or delete it from the list
@users.route('/select_message/<_id>', methods=['GET', 'DELETE'])
def select_message(_id):
    if request.method == 'GET':
        if current_user is not None and hasattr(current_user, 'id'):
            _message = db.session.query(Messages).filter(Messages.id == _id).first()
          
            if _message.receiver == current_user.id:
                #check that the actual recipient of the id message is the current user to guarantee Confidentiality   
                return render_template('reading_pane.html',content = _message) 
            else:
                abort(403) #the server is refusing action
        else:
            return redirect("/")
    elif request.method == 'DELETE':
        if current_user is not None and hasattr(current_user, 'id'):
            _message = db.session.query(Messages).filter(and_(Messages.id == _id))
            if _message.receiver == current_user.id:
                #delete
                db.session.delete(_message)
                db.session.commit()
            else:
                abort(403) #the server is refusing action
        else:
            return redirect("/")
    else:
        raise RuntimeError('This should not happen!')
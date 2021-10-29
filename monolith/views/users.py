from flask import Blueprint, redirect, render_template, request, abort
from monolith.auth import current_user
import bcrypt

from json import dumps
from monolith.database import User, db, Messages
from monolith.forms import UserForm

import datetime
from datetime import date, timedelta
from datetime import datetime as dt_

import hashlib

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

@users.route('/blacklist/<_id>', methods=['GET','DELETE', 'POST'])
def add_to_black_list(_id):
    #add _id to the balcklist of current user

    #query _id into the database looking for its existence
    exist = db.session.query(User.id).filter_by(id=_id).first()
    if current_user._authenticated and exist is not None:
        #we can add something to the blacklist only if the user is logged and the target user exist
        
        user_row = db.session.query(User).filter(User.id==current_user.id).first()   # current_user row 
        user_bl = user_row.black_list       #blacklist value
        if request.method == 'POST':
            #TODO form to add a user into the blacklist
            action = 'Adding ' + str(_id, 'utf-8') + 'to blacklist'
            if user_bl == "":           
                #empty black list
                user_row.black_list = str(_id,'utf-8')      #just initialize the blacklist with the target id
                
            else:
                user_bl = user_bl + "-" + _id      #build the string adding the following format id1-id2-...-idn
                user_row.black_list = user_bl   
            #update the db
            db.session.add(user_row)
            db.session.commit()

        elif request.method == 'DELETE':
            action = 'Deleting ' + str(_id, 'utf-8') + 'to blacklist'
            if str(_id) in user_row.black_list:
                user_row.black_list.replace(str(_id),"",1)  #deleting id from the blacklist
            #update the db
            db.session.add(user_row)
            db.session.commit()
        
        elif request.method == 'GET':
            action = 'Getting user blacklist'

            bl_list = []
            if (user_row.black_list ): #stringa non vuota
                tmp_list_of_id = user_row.black_list.split("-")
                print(tmp_list_of_id)
                print(len(tmp_list_of_id))
                for name in tmp_list_of_id:
                    #parsing id list into name list
                    tmp_result = db.session.query(User).filter(User.id==int(name)).first()
                    usr_name = tmp_result.firstname
                    usr_surname = tmp_result.secondname
                    bl_list.append({"name":usr_name,"surname":usr_surname,"id":int(name)})
                    #bl_list.append((usr_name, usr_surname, int(name))
    
               
            
        return render_template('black_list.html',blackList = bl_list, action_ = action)




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
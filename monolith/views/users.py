from flask import Blueprint, redirect, render_template, request, abort
from sqlalchemy.orm.base import PASSIVE_NO_RESULT
from sqlalchemy.sql.expression import update
from monolith.auth import current_user
import bcrypt

from json import dumps
from monolith.database import User, db, Messages, blacklist, msglist
from monolith.forms import UserForm, UserModifyForm

import datetime
from datetime import date, timedelta
from datetime import datetime as dt_

import hashlib
from sqlalchemy.exc import IntegrityError
from sqlalchemy import and_, or_, not_
import json

users = Blueprint('users', __name__)

_new_msg = 2

@users.route('/users')
def _users():
    #Filtering only registered users
    if current_user is not None and hasattr(current_user, 'id'):
        #Show all users except current user and show also the button to add a user into the blacklist
        _users = db.session.query(User).filter(User.is_active==True).filter(User.id != current_user.id)
        return render_template("users.html", users=_users,logged = True)
    else:
        _users = db.session.query(User).filter(User.is_active==True)
        return render_template("users.html", users=_users,logged = False)

@users.route('/users/start/<s>')
def _users_start(s):
    #Select the first user in the db with firstname starting by "s", used in search bar for message sending
    users = db.session.query(User).filter(User.is_active==True).filter(User.firstname.startswith(s)).limit(2).all()
    if (len(users)>0):
        return dumps({'id':users[0].id,'firstname' : users[0].firstname,'lastname':users[0].lastname,'email':users[0].email})
    else:
        return dumps({})

@users.route('/myaccount', methods=['DELETE', 'GET'])
def myaccount():
    if request.method == 'DELETE':
        #delete the account just deactivating the is_active field into the database
        if current_user is not None and hasattr(current_user, 'id'):
            #delete only if the user exist
            _user = db.session.query(User).filter(User.id == current_user.id).first()
            _user.is_active=False
            #delete all messages?
            db.session.commit()
            return redirect("/logout",code=303)
    elif request.method == 'GET':
        #get my account info
        if current_user is not None and hasattr(current_user, 'id'):
            content = db.session.query(User.filter_isactive).filter(User.id==current_user.id).first()
            s = ""
            #get the status of the content filter button to show it into the web page
            if content[0]==True:
                s = "Active"
            else:
                s ="Not Active"
        
            return render_template("myaccount.html", contentactive=s,new_msg=10)
        return redirect("/")


@users.route('/myaccount/modify',methods=['GET','POST'])
def modify_data():
    #modify user data
    form = UserModifyForm()
    if request.method == 'GET':
        if current_user is not None and hasattr(current_user, 'id'):
            #render the form with current values of my account
            form.email.data = current_user.email
            form.firstname.data = current_user.firstname
            form.lastname.data = current_user.lastname
            form.date_of_birth.data = current_user.date_of_birth
            return render_template('modifymyaccount.html', form = form)
    if request.method == 'POST':
        if form.validate_on_submit():
            #get the user row
            usr = db.session.query(User).filter(User.id == current_user.id).first()
            #check current password
            verified = bcrypt.checkpw(form.password.data.encode('utf-8'), usr.password)
            if verified:    #to change data values current user need to insert the password
                #check for new password inserted in the apposit field
                if (form.newpassword.data ) and (form.newpassword.data == form.repeatnewpassword.data):
                    usr.set_password(form.newpassword.data)
                
                #check that users changed this account email with another already used by another
                email_check = db.session.query(User.email).filter(User.email == form.email.data).filter(User.email != current_user.email).first()
                if email_check is None:
                    usr.email = form.email.data
                else:
                    return render_template('modifymyaccount.html', form = form, error = "This email is already used! Try with another one.")
                usr.firstname = form.firstname.data
                usr.lastname = form.lastname.data
                usr.date_of_birth = form.date_of_birth.data
                db.session.commit()
                return redirect("/myaccount")
            else:
                return render_template('modifymyaccount.html', form = form, error = "Insert your password to apply changes")


@users.route('/myaccount/set_content', methods=['POST'])
def set_content():
    #set content filter when button clicked into the GUI
    if current_user is not None and hasattr(current_user, 'id'):
            get_data = json.loads(request.data)
            if(get_data['content']=="Active"):
                #Setting to True the field in DB
                stmt = (
                    update(User).
                    where(User.id==current_user.id).
                    values(filter_isactive=True)
                    )
                db.session.execute(stmt)
                db.session.commit()
            else:
                #Setting to False the field in DB
                stmt = (
                    update(User).
                    where(User.id==current_user.id).
                    values(filter_isactive=False)
                )
                db.session.execute(stmt)
                db.session.commit()
        
            return '{"message":"OK"}'
    else:
        return redirect("/")


@users.route('/blacklist',methods=['GET','DELETE'])
def get_blacklist():
    if current_user is not None and hasattr(current_user, 'id'):
        #check user exist and that is logged in
        if request.method == 'GET':
            #show the black list of the current user
            _user = db.session.query(User.id, User.email,User.firstname,User.lastname,blacklist).filter(blacklist.c.user_id == current_user.id).filter(blacklist.c.black_id == User.id)
            
            if _user.first() is not None:
                #check user has at least 1 row into the blacklist table
                return render_template('black_list.html',action="This is your blacklist",black_list=_user,new_msg=_new_msg)
            else:
                return render_template('black_list.html',action="Your blacklist is empty",black_list=[],new_msg=_new_msg)
        elif request.method == 'DELETE':
            
            #Clear the whole blacklist
            black_list = db.session.query(blacklist.c.user_id).filter(blacklist.c.user_id==current_user.id).first()
            if black_list is not None:
                #clear only if the blacklist is not empty
                st = blacklist.delete().where(blacklist.c.user_id == current_user.id)
                db.session.execute(st)   
                db.session.commit()
                black_list = db.session.query(blacklist).filter(blacklist.c.user_id == current_user.id)
            
                return render_template('black_list.html',action="Your blacklist is now empty",black_list=black_list,new_msg=_new_msg)
            else:
                return render_template('black_list.html',action="Your blacklist is already empty",black_list=[],new_msg=_new_msg)
    else:
        return redirect("/")
        
@users.route('/blacklist/<target>', methods=['POST', 'DELETE'])
def add_to_black_list(target):
    #route that add target to the blacklist of user.
    if current_user is not None and hasattr(current_user, 'id'):
        #current can not add himself into the blacklist
        #check that both users are registered and that 'user' is exactly current user and nobody else
        existUser = db.session.query(User).filter(User.id==current_user.id).first()
        existTarget = db.session.query(User).filter(User.id==target).first()
        #add target into the user's blacklist
        if request.method == 'POST':
            #be sure that name is not into the blacklist already
            if existUser is not None and existTarget is not None and current_user.id != target: 
                inside = db.session.query(blacklist).filter(blacklist.c.user_id == current_user.id).filter(blacklist.c.black_id == target).first()
                if inside is None: #the user is NOT already in the blacklist
                    existUser.black_list.append(existTarget)
                    db.session.commit()
                    user_bl = db.session.query(User.email,User.firstname,User.lastname,blacklist).filter(blacklist.c.user_id == current_user.id).filter(blacklist.c.black_id == User.id)
                    return render_template('black_list.html',action="User "+target+" added to the black list.",black_list = user_bl)
                else: #target already in the blacklist
                    user_bl = db.session.query(User.email,User.firstname,User.lastname,blacklist).filter(blacklist.c.user_id == current_user.id).filter(blacklist.c.black_id == User.id)
                    return render_template('black_list.html',action="This user is already in your blacklist!",black_list = user_bl)
            else:
                #User or Target not in db
                return render_template('black_list.html',action="Please check that you select a correct user",black_list=[])    
        elif request.method == 'DELETE':
            #Delete target from blacklist
            if existUser is not None and existTarget is not None:
                #Delete target from current user's blacklist
                bl_target = db.session.query(blacklist).filter((blacklist.c.user_id == current_user.id)&(blacklist.c.black_id == target)).first()
                if bl_target is not None:
                    #check that target is already into the black list 
                    st = blacklist.delete().where((blacklist.c.user_id == current_user.id)&(blacklist.c.black_id == target))
                    db.session.execute(st)
                    db.session.commit()
                    bl_ = db.session.query(User.email,User.firstname,User.lastname,blacklist).filter(blacklist.c.user_id == current_user.id).filter(blacklist.c.black_id == User.id)
                    return render_template('black_list.html',action = "User "+target+" removed from your black list.",black_list= bl_)
                else:
                    bl_ = db.session.query(User.email,User.firstname,User.lastname,blacklist).filter(blacklist.c.user_id == current_user.id).filter(blacklist.c.black_id == User.id)
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
        if form.validate_on_submit() == True:
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
            
            #Check the correct fromat for date of birth
            date_string = form.date_of_birth.data
            format = '%d/%m/%Y'
            try:
                dt_.strptime(date_string, format)
            except ValueError: #the format of date inserted is not correct
                return render_template('create_user.html',form=form,error="Please enter a valid date of birth in the format dd/mm/yyyy!")
            #Check the validity of date of birth (no dates less than 1900, no dates higher than last year
            datetime_object = dt_.strptime(form.date_of_birth.data, '%d/%m/%Y')
            my_1_year_ago = dt_.now() - timedelta(days=365)
            if datetime_object > my_1_year_ago or datetime_object < dt_(1900,1,1):
                return render_template('create_user.html',form=form,error="Please enter a valid date of birth!")
            
            # Setting the user fields and add user to DB
            new_user.set_password(form.password.data)
            new_user.set_dateOfBirth(datetime_object) #setting the date correctly
            db.session.add(new_user)
            db.session.commit()
            return redirect('/')
    elif request.method == 'GET':
        return render_template('create_user.html', form=form)




#report a user: a user can report an other user based on a message that the target user send to him.
@users.route('/report_user/<msg_target_id>', methods = ['POST'])
def report_user(msg_target_id):
    threshold_ban = 3 #the threshold of reports to ban the user
    days_of_ban = 3 #the number of days of ban

    if current_user is not None and hasattr(current_user, 'id'):
        
        if request.method == 'POST': #GET IS ONLY FOR TESTING, THE METHOD SHOULD ALLOWS ONLY POST
            #0. check the existence of usr and usr_to_report
            existTarget = db.session.query(Messages).filter(Messages.id==msg_target_id).first() #check i fthe msg exist

            if existTarget is not None: 
                #1. Create the report against the user of msg_target_id:
                    my_row = db.session.query(Messages.number_bad,msglist.c.hasReported,Messages.sender).filter(and_(Messages.id == msg_target_id, msglist.c.user_id == current_user.id, Messages.id == msglist.c.msg_id)).first()  

                    if my_row.hasReported == False: #check that user has not already reported the msg
                        if my_row.number_bad > 0: #check if the message has really bad words
                            #In this case the report has to be effective -->> the report count on user "sender"        
                            my_row2 = db.session.query(User.n_report, User.ban_expired_date).filter(User.id == my_row[2]).first()
                            if my_row2[1] is None: #check if user is already banned (my_row2[1] is the field ban_expired_date)
                                target_user = db.session.query(User).filter(User.id == my_row.sender).one()
                                if (my_row2[0] + 1) > threshold_ban: #The user has to be ban from app (my_row2[0] is the field n_report)
                                    today = date.today()
                                    ban_date = today + datetime.timedelta(days=3)
                                    target_user.ban_expired_date = ban_date
                                    target_user.n_report = 0
                                    target_user.n_report = 0 #The user is banned, so we reset the report count
                                    db.session.commit()
                                    return render_template('report_user.html', action = "The user reported has been banned")
                                else:
                                    #increment the report count for user, and setting the hasReported field to True
                                    target_user.n_report += 1
                                    stm = msglist.update().where(msglist.c.msg_id == msg_target_id).values(hasReported = True)
                                    db.session.execute(stm)
                                    db.session.commit()
                                    return render_template('report_user.html', action = "The user has its reported counter incremented")
                                    
                            else:
                                #already banned
                                return render_template('report_user.html', action = "The user is already banned", code = 304)

                        else:
                            #sender is not guilty
                            return render_template('report_user.html', action = "This user does not violate our policies, so we cannot handle your report.", code = 304)

                    else:
                        #the actual user has already reported this message (max one report for message for user)
                        return render_template('report_user.html', action = "You have already reported this message!", code = 304)
            else:
                return render_template('report_user.html', action = "Invalid message to report!", code = 404)
    else:
        return redirect("/")







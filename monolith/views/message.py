import base64
from flask import Blueprint, render_template, request,abort
from monolith.forms import NewMessageForm
from monolith.database import Messages, User, msglist, blacklist, db, Images
from monolith.forms import NewMessageForm
from werkzeug.utils import redirect 
from monolith.auth import current_user
from datetime import date, datetime, timedelta
from monolith.background import notify
from sqlalchemy import update

import json

import json

message = Blueprint('message', __name__)



# Check if the message data are correct
def verif_data(data):
    if len(data["destinator"])>=1: # At least one receiver
        if data["date_of_delivery"] != "" and data["time_of_delivery"] != "":
            new_date = data["date_of_delivery"] +" "+data["time_of_delivery"]
            delivery = datetime.strptime(new_date,'%Y-%m-%d %H:%M')
            if delivery>datetime.today(): 
                return "OK"
        return "Date not valid"
    else:
        return "No destinator"


@message.route('/message_withdrow/<msg_id>',methods = ['DELETE'])
def withdrow(msg_id):
    #route of regrets. Withdrow a message only if you selected a real message and you have enough points to do so
    if current_user is not None and hasattr(current_user, 'id'):
        msg_exist = db.session.query(Messages.id, Messages.sender,Messages.is_draft , User.lottery_points).filter(Messages.id == msg_id).filter(Messages.sender == current_user.id).filter(User.id == Messages.sender).first()
        _send = db.session.query(Messages.id,Messages.title,Messages.date_of_delivery).filter(Messages.sender==current_user.id,Messages.is_draft==False).all()
        _draft = db.session.query(Messages.id,Messages.title,Messages.date_of_delivery).filter(Messages.sender==current_user.id,Messages.is_draft==True).all()
        
        print(msg_exist)
        if msg_exist is not None and msg_exist.is_draft == False:
            
            if msg_exist.lottery_points >= 10:
                #this ensure that current_user is the owner of the message and that the message exist
                #10 points needed to withdrow a message
                msg_row = db.session.query(Messages).filter(Messages.id == msg_id).first()
                usr_row = db.session.query(User).filter(User.id == msg_exist.sender).first()
                usr_row.lottery_points -= 10
                db.session.delete(msg_row)          #delete the whole message from the db 
                db.session.commit()
                return render_template('get_msg_send_draft.html', draft=_draft, send=_send, action = "Your message has been deleted")

            else:
                #no enough points to withdrow
                return render_template('get_msg_send_draft.html', draft=_draft, send=_send, action = "You need 10 points to withdrow a message. To gain points, try to play lottery!")
        elif msg_exist.is_draft == True:
            #just delete the draft WORKS
            delete_ = db.session.query(Messages).filter(Messages.id == msg_id).first()
            db.session.delete(delete_)
            db.session.commit()
            return render_template('get_msg_send_draft.html', draft=_draft, send=_send)
        else:
            return render_template('get_msg_send_draft.html', draft=_draft, send=_send, action = "Something went wrong...")

    else:
        return redirect('/')


@message.route('/message/new',methods = ['GET','POST'])
def message_new():
    if current_user is not None and hasattr(current_user, 'id'):
        if request.method == 'GET':
            return render_template("newmessage.html")
        elif request.method =='POST':
            get_data = json.loads(request.form['payload'])
            r = verif_data(get_data)
            if r=='OK':
                list_of_receiver = set(get_data["destinator"])
                date_of_delivery = get_data["date_of_delivery"]
                time_of_delivery = get_data["time_of_delivery"]
                content = get_data["content"]
                # Check if fields are valid before send the message
                title = get_data["title"]
                if title == "":
                    return '{"message":"Message with empty title"}'
                list_of_images = request.files

                #REQUEST TO API
                import urllib.request,urllib.parse, urllib.error
                #content = content+" "+content
                
                url = 'https://neutrinoapi.net/bad-word-filter'
                params = {
                'user-id': 'flaskapp10',
                'api-key': '6OEjKKMDzj3mwfwLJfRbmiOAXamekju4dQloU95eCAjPYjO1',
                'content': content
                }


                try:
                    postdata = urllib.parse.urlencode(params).encode()
                    req = urllib.request.Request(url, data=postdata)
                    response = urllib.request.urlopen(req)
                    result = json.loads(response.read().decode("utf-8"))
                except urllib.error.HTTPError as exception:
                    return '{"message":"KO"}'

                # Check if message was drafted and then sended
                try: 
                    msg_id = request.form["message_id"]
                except KeyError:
                    msg_id = 0

                if msg_id != 0:
                    # message was drafted and then sent
                    try: 
                        # Get images previously uploaded that needs to be deleted
                        image_id_to_delete = json.loads(request.form['delete_image_ids'])
                    except KeyError:
                        image_id_to_delete = []
                    try:
                        # Get users previously uploaded that needs to be deleted
                        user_id_to_delete = json.loads(request.form['delete_user_ids'])
                    except KeyError:
                        user_id_to_delete = []
                    message = db.session.query(Messages).filter(Messages.id == msg_id).first()
                    for id in user_id_to_delete:
                        db.session.query(msglist).filter(msglist.c.msg_id == msg_id).filter(msglist.c.user_id == id).delete()
                    for id in list_of_receiver:
                        rec= db.session.query(User).filter(User.id==id).first()
                        if rec != None:
                            message.receivers.append(rec)
                    db.session.commit()
                    new_date = date_of_delivery +" "+time_of_delivery
                    new_date = datetime.strptime(new_date,'%Y-%m-%d %H:%M')
                    for image in image_id_to_delete:
                        db.session.query(Images).filter(Images.id==image).delete()
                        db.session.commit()
                    for image in list_of_images:
                        # adding new images
                        img = Images()
                        img.image = list_of_images[image].read()
                        img.mimetype = list_of_images[image].mimetype
                        img.message = msg_id
                        db.session.add(img)

                    stmt = (
                        update(Messages).
                        where(Messages.id==int(msg_id)).
                        values(title=title, content=content,date_of_delivery=new_date,is_draft=False)
                    )
                    db.session.execute(stmt)
                    db.session.commit()
                    return '{"message":"OK"}'

                #Creating new Message
                msg = Messages()
                msg.sender= current_user.id
                msg.title = title
                msg.content = content
                new_date = date_of_delivery +" "+time_of_delivery
                msg.date_of_delivery = datetime.strptime(new_date,'%Y-%m-%d %H:%M')
                msg.font = get_data["font"]
                #Setting the message (bad content filter) in database
                #if(result['is-bad']==True):
                #    msg.bad_content=True
                #    msg.number_bad = len(result["bad-words-list"])
                #else:
                #    msg.bad_content=False
                #    msg.number_bad = 0

                for id in list_of_receiver:
                    rec= db.session.query(User).filter(User.id==id).first()
                    print(rec)
                    if rec != None:
                        msg.receivers.append(rec)
                #add message
                db.session.add(msg)
                db.session.commit()

                for image in list_of_images:
                    img = Images()
                    img.image = list_of_images[image].read()
                    img.mimetype = list_of_images[image].mimetype
                    img.message = msg.get_id()
                    db.session.add(img)
                print(msg)
                db.session.commit()
            return '{"message":"'+r+'"}'
              
    else:
        return redirect('/')



@message.route('/message/draft',methods = ['POST'])
def message_draft():
    if current_user is not None and hasattr(current_user, 'id'):
        if request.method == 'GET':
            return render_template("newmessage.html")
        elif request.method =='POST':
            get_data = json.loads(request.form['payload'])
            try: 
                # Get images previously uploaded that needs to be deleted
                image_id_to_delete = json.loads(request.form['delete_image_ids'])
            except KeyError:
                image_id_to_delete = []
            try:
                # Get users previously uploaded that needs to be deleted
                user_id_to_delete = json.loads(request.form['delete_user_ids'])
            except KeyError:
                user_id_to_delete = []

            list_of_receiver = set(get_data["destinator"])
            # allowing draft with at least one destinator specified
            if len(list_of_receiver) == 0:
                return '{"message":"Draft with no recipients"}'
            date_of_delivery = get_data["date_of_delivery"]
            time_of_delivery = get_data["time_of_delivery"]
            content = get_data["content"]
            title = get_data["title"]
            font = get_data["font"]
            list_of_images = request.files
            try: 
                msg_id = request.form["message_id"]
            except KeyError:
                msg_id = 0

            if msg_id != 0:
                # this message was already drafted, need to update it
                message = db.session.query(Messages).filter(Messages.id == msg_id).first()
                for id in user_id_to_delete:
                    db.session.query(msglist).filter(msglist.c.msg_id == msg_id).filter(msglist.c.user_id == id).delete()
                for id in list_of_receiver:
                    rec= db.session.query(User).filter(User.id==id).first()
                    if rec != None:
                        message.receivers.append(rec)
                db.session.commit()
                new_date = date_of_delivery +" "+time_of_delivery
                try:
                    new_date = datetime.strptime(new_date,'%Y-%m-%d %H:%M')
                except ValueError:
                    new_date = date.today()
                for image in image_id_to_delete:
                    print(image)
                    db.session.query(Images).filter(Images.id==image).delete()
                    db.session.commit()
                for image in list_of_images:
                    # adding new images
                    img = Images()
                    img.image = list_of_images[image].read()
                    img.mimetype = list_of_images[image].mimetype
                    img.message = msg_id
                    db.session.add(img)

                stmt = (
                    update(Messages).
                    where(Messages.id==int(msg_id)).
                    values(title=title, content=content,date_of_delivery=new_date,font=font)
                )
                db.session.execute(stmt)
                db.session.commit()
                return '{"message":"OK"}'

            #Creating new Message
            msg = Messages()
            msg.sender= current_user.id
            msg.title = title
            msg.content = content
            msg.font = font
            new_date = date_of_delivery +" "+time_of_delivery
            try:
                msg.date_of_delivery = datetime.strptime(new_date,'%Y-%m-%d %H:%M')
            except ValueError:
                msg.date_of_delivery = date.today()
            msg.is_draft=True

            for id in list_of_receiver:
                rec= db.session.query(User).filter(User.id==id).first()
                print(rec)
                if rec != None:
                    msg.receivers.append(rec)
            #add message
            db.session.add(msg)
            db.session.commit()

            for image in list_of_images:
                img = Images()
                img.image = list_of_images[image].read()
                img.mimetype = list_of_images[image].mimetype
                img.message = msg.get_id()
                db.session.add(img)
            db.session.commit()
        return '{"message":"OK"}'
              
    else:
        return redirect('/')




#select message to be read and access the reading panel or delete it from the list
@message.route('/message/<_id>', methods=['GET', 'DELETE'])
def select_message(_id):
    if request.method == 'GET':
        if current_user is not None and hasattr(current_user, 'id'):

            _message = db.session.query(Messages.title, Messages.content,Messages.id,Messages.font).filter(Messages.id==_id).first()
            _picture = db.session.query(Images).filter(Images.message==_id).all()
            user = db.session.query(msglist.c.user_id).filter(msglist.c.msg_id==_id,msglist.c.user_id==current_user.id).first()

           
                 
            #check that the actual recipient of the id message is the current user to guarantee Confidentiality 
             
            if current_user.id == user[0]:
                #Convert Binary Large Object in Base64
                l = []
                
                for row in _picture:
                   
                    image = base64.b64encode(row.image).decode('ascii')
                    l.append(image)
                
                #If it is the first time that the message is read, then notify the sender and update the state
                read = db.session.query(msglist.c.read).filter(msglist.c.user_id==current_user.id, msglist.c.msg_id==_id).first()
                print(read)

                if(read[0]==False):
                    #notify with celery update read status
                   
                   #Try to notify the sender
                   #QoS  TCP/IP one if the redis-queue, is down the notification is sent iff the user reopen the message after  and the service it's ok
                    try:
                        sender_id = db.session.query(Messages.sender).filter(Messages.id==_id).first()
                        notify.delay(sender_id[0], current_user.id)
                        stmt = (
                        update(msglist).where(msglist.c.msg_id==_id, msglist.c.user_id==current_user.id).values(read=True))

                        db.session.execute(stmt)
                        db.session.commit()
                    except Exception as e:
                        abort(404, description="Celery not available")
                       
                    

                return render_template('message_view.html',message = _message, pictures=json.dumps(l),new_msg=2) 
            else:
                abort(403) #the server is refusing action
        else:
            return redirect("/")

    elif request.method == 'DELETE':
        if current_user is not None and hasattr(current_user, 'id'):
            
            _message = db.session.query(msglist.c.msg_id).filter(msglist.c.id == _id).all()
            for row in _message:
                print(row)

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


# Reply to one message
@message.route('/message/reply/<_id>', methods=['GET', 'DELETE'])
def reply(_id):
    _reply = db.session.query(Messages.sender,Messages.title,User.firstname,User.lastname).filter(Messages.id==_id).filter(User.id==Messages.sender).first()
    print(_reply)
    return render_template('replymessage.html',new_msg=2,reply=_reply)


@message.route('/message/view_send/<_id>',methods=['GET'])
def message_view_send(_id):
    if current_user is not None and hasattr(current_user, 'id'):
        _message = db.session.query(Messages.title, Messages.content,Messages.id,Messages.sender,Messages.font).filter(Messages.id==_id).first()
        _receivers = db.session.query(User.id, User.email, User.firstname, User.lastname , Messages.id).join(User, Messages.receivers).filter(Messages.id == _message.id).all()
        _picture = db.session.query(Images).filter(Images.message==_id).all()
        if _message.sender ==current_user.id:
            l = []
            if len(_picture) > 0:
                for row in _picture:
                    image = base64.b64encode(row.image).decode('ascii')
                    l.append(image)
            
            return render_template('message_view_send.html',message = _message,receivers=_receivers, pictures=json.dumps(l)) 
        else:
            return redirect('/')
    else:
        return redirect('/')


@message.route('/edit/<_id>',methods=['GET'])
def message_view_draft(_id):
    if current_user is not None and hasattr(current_user, 'id'):
        _message = db.session.query(Messages.title, Messages.content,Messages.id,Messages.sender, Messages.date_of_delivery, Messages.font).filter(Messages.id==_id).first()
        _receivers = db.session.query(User.id, User.email, User.firstname, User.lastname , Messages.id).join(User, Messages.receivers).filter(Messages.id == _message.id).all()
        _picture = db.session.query(Images).filter(Images.message==_id).all()
        if _message.sender ==current_user.id:
            l = []
            image_ids = []
            if len(_picture) > 0:
                for row in _picture:
                    image = base64.b64encode(row.image).decode('ascii')
                    l.append(image)
                    image_ids.append(row.id)
            return render_template('message_view_edit_draft.html',message = _message, pictures=json.dumps(l),image_ids=image_ids,receivers=_receivers) 
        else:
            return redirect('/')
    else:
        return redirect('/')


                                             
@message.route('/messages/send',methods=['GET'])
def message_send():
    if current_user is not None and hasattr(current_user, 'id'):
    
        _send = db.session.query(Messages.id,Messages.title,Messages.date_of_delivery, Messages.font).filter(Messages.sender==current_user.id,Messages.is_draft==False).all()
        _draft = db.session.query(Messages.id,Messages.title,Messages.date_of_delivery, Messages.font).filter(Messages.sender==current_user.id,Messages.is_draft==True).all()

        
        return render_template('get_msg_send_draft.html',draft=_draft,send=_send)
    else:
        return redirect('/')

@message.route('/messages', methods=['GET'])
def messages():
    #check user exist and that is logged in
    if current_user is not None and hasattr(current_user, 'id'):

        #checking the content
        filter = db.session.query(User.filter_isactive).filter(User.id==current_user.id).first()
        _messages = ""
        print(filter)
        if filter[0]==False:

            _messages = db.session.query(Messages.id,Messages.title,Messages.date_of_delivery,Messages.sender,User.firstname,msglist.c.user_id,User.filter_isactive,Messages.bad_content) \
            .filter(msglist.c.user_id==User.id,msglist.c.msg_id==Messages.id) \
            .filter(User.id==current_user.id) \
            .filter(Messages.date_of_delivery <= datetime.now(),Messages.is_draft==False) \
            .all()
        else:
            _messages = db.session.query(Messages.id,Messages.title,Messages.date_of_delivery,Messages.sender,User.firstname,msglist.c.user_id,User.filter_isactive,Messages.bad_content) \
            .filter(msglist.c.user_id==User.id,msglist.c.msg_id==Messages.id) \
            .filter(User.id==current_user.id) \
            .filter(Messages.date_of_delivery <= datetime.now(),Messages.is_draft==False) \
            .filter(Messages.bad_content==False) \
            .all()

        for row in _messages:
            print(row)

        
        return render_template("get_msg.html", messages = _messages)
    else:
        return redirect("/")


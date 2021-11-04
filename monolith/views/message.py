from flask import Blueprint, render_template, request
from monolith.forms import NewMessageForm


from monolith.database import Messages, User, msglist, blacklist, db, Images


from werkzeug.utils import redirect 
from monolith.auth import current_user
from datetime import date, datetime, timedelta
import json

import json

message = Blueprint('message', __name__)

#showing all the messages (only for test. DO NOT USE THIS IN REAL APPLICATION)
@message.route('/messages', methods=['GET'])
def _messages():
    #check user exist and that is logged in
    if current_user is not None and hasattr(current_user, 'id'):
        _messages = db.session.query(Messages.id,Messages.title,Messages.date_of_delivery,Messages.sender,User.firstname,msglist.c.user_id) \
        .filter(msglist.c.user_id==current_user.id,msglist.c.user_id==User.id).all()
        print(_messages)
        return render_template("get_msg.html", messages = _messages,new_msg=2)
    else:
        return redirect("/")

def verif_data(data):
    if len(data["destinator"])>=1:
        delivery=datetime.strptime(data["date_of_delivery"],'%Y-%m-%d')
        if delivery>datetime.today():
            return "OK"
        else :
            return "Date is inferior"
    else:
        return "No destinator"


#THIS IS NOT GOOD: not all the messages have to be checked for bad words. 
#ON the new messages there ARE NO LIMITATION of bad words. 
#it's only for content filter, and it's something on the receiver
@message.route('/message/new',methods = ['GET','POST'])
def message_new():
    if current_user is not None and hasattr(current_user, 'id'):
        if request.method == 'GET':
            return render_template("newmessage.html", new_msg=2)
        elif request.method =='POST':
            get_data = json.loads(request.form['payload'])
            r = verif_data(get_data)
            if r=='OK':
                
                #REQUEST TO API
                import urllib.request,urllib.parse, urllib.error
                content = get_data["content"]+" "+get_data["content"]
                
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

              
               
                list_of_receiver = set( get_data["destinator"] ) # remove the duplicate receivers
                list_of_images = request.files
                #Creating new Message
                msg = Messages()
                msg.sender= current_user.id
                msg.title = get_data["title"]
                msg.content = get_data["content"]
                new_date = get_data["date_of_delivery"] +" "+get_data["time_of_delivery"]
                msg.date_of_delivery = datetime.strptime(new_date,'%Y-%m-%d %H:%M')
                #Setting the message (bad content filter) in database
                if(result['is-bad']==True):
                    msg.bad_content=True
                    msg.number_bad = len(result["bad-words-list"])
                else:
                    msg.bad_content=False
                    msg.number_bad = 0

                for id in list_of_receiver:
                            rec= db.session.query(User).filter(User.id==id).first()
                            print(rec)
                            if rec != None:
                                msg.receivers.append(rec)
                for image in list_of_images:
                    img = Images()
                    img.image = list_of_images[image].read()
                    img.mimetype = list_of_images[image].mimetype
                    img.message = msg.id
                    db.session.add(img)
                print(msg)
                db.session.add(msg)
                db.session.commit()
            return '{"message":"'+r+'"}'
              
    else:
        return redirect('/')



#show recipient all message that have been delivered
@message.route('/show_messages', methods=['GET'])
def show_messages():
    #TODO check user is logged
    #TODO check sender not in black_list

    #today_dt = datetime.combine(date.today(), datetime.min.time())
    
    
    _messages = db.session.query(Messages.id,Messages.title,Messages.content).filter(Messages.date_of_delivery <= datetime.now())

    

    return render_template('get_msg.html',messages = _messages)



#select message to be read and access the reading panel or delete it from the list
@message.route('/select_message/<_id>', methods=['GET', 'DELETE'])
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

from flask import Blueprint, render_template, request
from monolith.forms import NewMessageForm
from monolith.database import Messages, User, msglist, blacklist, db
from werkzeug.utils import redirect 
from monolith.auth import current_user
from datetime import date, datetime, timedelta

message = Blueprint('message', __name__)

@message.route('/message/new',methods=['GET'])
def message_new():
    form = NewMessageForm()
    return render_template("newmessage.html", form=form)

#showing all the messages (only for test. DO NOT USE THIS IN REAL APPLICATION)
@message.route('/messages', methods=['GET'])
def _messages():
    #check user exist and that is logged in
    print("ciao")
    return redirect('./')
    # if current_user is not None and hasattr(current_user, 'id'):
        
    #     messages = db.session.query(Messages.title,Messages.date_of_delivery,Messages.sender,msglist.c.user_id).filter(msglist.c.user_id==current_user.id)
    #     print(messages)

    #     return render_template("get_msg.html", messages = _messages,new_msg=2)
    # else:
    #      return redirect("/")




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

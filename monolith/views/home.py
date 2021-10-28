from datetime import date, datetime
from flask import Blueprint, render_template, request
from werkzeug.utils import redirect 
from monolith.forms import NewMessageForm

from monolith.auth import current_user
import json
home = Blueprint('home', __name__)


@home.route('/')
def index():
    if current_user is not None and hasattr(current_user, 'id'):
        welcome = "Logged In!"
    else:
        welcome = None
    return render_template("index.html", welcome=welcome,new_msg=6)



def verif_data(data):
    if len(data["destinator"])>=1:
        delivery=datetime.strptime(data["date_of_delivery"],'%Y-%m-%d')
        if delivery>datetime.today():
            return "OK"
        else :
            return "Date is inferior"
    else:
        return "No destinator"


@home.route('/message/new',methods = ['GET','POST'])
def message_new():
    if current_user is not None and hasattr(current_user, 'id'):
        if request.method == 'GET':
            return render_template("newmessage.html", new_msg=2)
        elif request.method =='POST':
            get_data = json.loads(request.data)
            r = verif_data(get_data)
            if r=='OK':
                print(get_data)
                list_of_receiver = set( get_data["destinator"] ) # remove the duplicate receivers
                #TODO : add the message in the database
            return '{"message":"'+r+'"}'
    else:
        return redirect('/')

@home.route('/message/send')
def message_send():
    if current_user is not None and hasattr(current_user, 'id'):
        return render_template("message_send.html",new_msg=6)
    else:
        return redirect('/')
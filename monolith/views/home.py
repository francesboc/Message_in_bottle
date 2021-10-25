from flask import Blueprint, render_template, request
from werkzeug.utils import redirect 
from monolith.forms import NewMessageForm

from monolith.auth import current_user

home = Blueprint('home', __name__)


@home.route('/')
def index():
    if current_user is not None and hasattr(current_user, 'id'):
        welcome = "Logged In!"
    else:
        welcome = None
    return render_template("index.html", welcome=welcome,new_msg=12)

@home.route('/message/new',methods = ['GET','POST'])
def message_new():
    form = NewMessageForm()
    if request.method == 'GET':
        return render_template("newmessage.html", form=form, new_msg=2)
    elif request.method =='POST':
        #TODO : add the message in the database
        return redirect('/')


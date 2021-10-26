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
    return render_template("index.html", welcome=welcome,new_msg=6)

@home.route('/message/new',methods = ['GET','POST'])
def message_new():
    form = NewMessageForm()
    if request.method == 'GET':
        return render_template("newmessage.html", form=form, new_msg=2)
    elif request.method =='POST':
        if form.validate_on_submit(): 
            #create new message obj 
            new_message = Messages()
            form.populate_obj(new_message)
            new_message.set_sender(current_user.id) #sender is the actual user
            new_message.set_receiver(form.destinator)
            new_message.set_content(form.content)
            new_message.set_delivery_date(form.delivery_date)

            db.session.add(new_message)
            db.session.commit()
    return redirect('/')


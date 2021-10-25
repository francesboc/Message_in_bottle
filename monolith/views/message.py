from flask import Blueprint, render_template
from monolith.forms import NewMessageForm

from monolith.auth import current_user

message = Blueprint('message', __name__)

@message.route('/message/new',methods=['GET'])
def message_new():
    form = NewMessageForm()
    return render_template("newmessage.html", form=form)

from flask import Blueprint, render_template
from monolith.forms import NewMessageForm

from monolith.auth import current_user

home = Blueprint('home', __name__)


@home.route('/')
def index():
    if current_user is not None and hasattr(current_user, 'id'):
        welcome = "Logged In!"
    else:
        welcome = None
    return render_template("index.html", welcome=welcome)

@home.route('/message/new')
def message_new():
    form = NewMessageForm()
    return render_template("newmessage.html", form=form)

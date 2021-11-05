from datetime import date, datetime
from flask import Blueprint, render_template, request
from flask.wrappers import Response
from werkzeug.utils import redirect 
from monolith.forms import NewMessageForm
from monolith.database import Images, Messages, User, db, blacklist


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




# Testing images      
@home.route('/image/<int:id>')
def download_images(id):
    _image = db.session.query(Images).filter(Images.id == id).first()
    return Response(_image.image, mimetype=_image.mimetype)


@home.route('/message/send')
def message_send():
    if current_user is not None and hasattr(current_user, 'id'):
        return render_template("message_send.html",new_msg=6)
    else:
        return redirect('/')


@home.route('/message/reject')
def message_reject():
    if current_user is not None and hasattr(current_user, 'id'):
        return render_template("message_bad_content.html",new_msg=6)
    else:
        return redirect('/')

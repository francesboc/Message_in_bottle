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

                #HANDLEERRORS
                print(result)
                print(result["is-bad"])
                print(result["bad-words-list"])
               
                if(result['is-bad']==True):
                    return '{"message":"CONTENT FILTER"}'
                    
                list_of_receiver = set( get_data["destinator"] ) # remove the duplicate receivers
                list_of_images = request.files
                msg = Messages()
                msg.sender= current_user.id
                msg.title = get_data["title"]
                msg.content = get_data["content"]
                new_date = get_data["date_of_delivery"] +" "+get_data["time_of_delivery"]
                msg.date_of_delivery = datetime.strptime(new_date,'%Y-%m-%d %H:%M')
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

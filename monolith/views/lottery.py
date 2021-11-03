from flask import Blueprint, render_template, request, abort
from monolith.forms import NewMessageForm
from monolith.database import Messages, User, Images, msglist, blacklist, db
from werkzeug.utils import redirect 
from monolith.auth import current_user
from datetime import date, datetime, timedelta
import json


lottery = Blueprint('lottery', __name__)

"""
Every user can guess just 1 number a month. 
Lottery extract randomly 1 number from 1 to 99, if your guess is lucky you won half of the point needed to withdrow a message of your choice.
"""
@lottery.route('/play',method=['GET'])
def lucky_number():
    if current_user is not None and hasattr(current_user, 'id'):
        guess = db.session.query(User.lottery_ticket_number).filter(User.id == current_user.id).first()
        if guess != -1:
            return render_template('lottery_board.html',action = "You already select the number: "+guess+"!")
        else:
            return render_template('lottery_board.html',action = "You have selected no number yet, hurry up! Luck is not waiting for you!")
    else:
        return redirect("/")

@lottery.route('/play/<number>',method = ['POST'])
def play(number):
    #guess a number for lottery
    if current_user is not None and hasattr(current_user, 'id'):
        if request.method == 'POST' and number in range(1,99):
            guess = db.session.query(User.lottery_ticket_number).filter(User.id == current_user.id).first()
            print("This is user guess")
            print(guess)
            if guess is -1:
                guess = number
                db.session.commit()
                return render_template('lottery_board.html',action = "You select the number "+number+"! Good Luck!")
            else:
                #already played
                return render_template('lottery_board.html',action = "You already select the number: "+ guess+"!", code = 304)
        else:
            raise RuntimeError('This should not happen!')
    else:
        return redirect("/")
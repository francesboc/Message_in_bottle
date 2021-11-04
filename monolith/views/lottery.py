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
# This is useful for the user to know what number he choosed or to know if he had not already choose a number
@lottery.route('/play',method=['GET'])
def lucky_number():
    if current_user is not None and hasattr(current_user, 'id'):
        guess = db.session.query(User.lottery_ticket_number).filter(User.id == current_user.id).first()
        if guess != -1:
            return render_template('lottery_board.html',action = "You already select the number. That's your number: "+guess+"!")
        else:
            return render_template('lottery_board.html',action = "You have selected no number yet, hurry up! Luck is not waiting for you!",code = 403)
    else:
        return redirect("/", code = 403)


# This route is necessary to allow user to select a number for the next lottery extraction.
# There is a time limit to choose the number: user can choose number in the first half of the month (from 1st to 15th)
@lottery.route('/play/<number>',method = ['POST'])
def play(number):
    #guess a number for lottery
    last_day = 15
    if current_user is not None and hasattr(current_user, 'id'):
        if request.method == 'POST': #FROM GIALLU: this isd not so correct, because if the user insert a number out of [1,99], it raise an exception. Maybe it's better so separate the checks and give a specific error message for the user in the case of bad number out of range
            if number in range(1,99):
                #now we check for the day of month (user can choose only in the first half of month)
                today = date.today()
                day_of_month = today.day
                if day_of_month <= last_day:
                    guess = db.session.query(User.lottery_ticket_number).filter(User.id == current_user.id).first()
                    print("This is user guess")
                    print('new version')
                    print(guess)
                    if guess == -1:
                        guess = number
                        db.session.commit()
                        return render_template('lottery_board.html',action = "You select the number "+number+"! Good Luck!")
                    else:
                        #already played
                        return render_template('lottery_board.html',action = "You already select the number: "+ guess+"!", code = 304)
                else:
                    return render_template('lottery_board.html', action = "You can't choose any more a number, the time to partecipate to lottery is expired! Try next month!", code = 304)
            else:
                return render_template('lottery_board.html',action = "You choose an invalid number for the lottery! You can choose only number from 1 to 99 !", code = 304)
        else:
            raise RuntimeError('This should not happen!')
    else:
        return redirect("/", code = 403)
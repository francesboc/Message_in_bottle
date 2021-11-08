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
@lottery.route('/lottery',methods = ['GET'])
def lucky_number():
    if current_user is not None and hasattr(current_user, 'id'):
        guess = db.session.query(User.lottery_ticket_number).filter(User.id == current_user.id).first()
        if guess.lottery_ticket_number != -1:
            
            return render_template('lottery_board.html',action = "You already select the number. This is your number: "+ str(guess.lottery_ticket_number)+"!") 
        else:
            return render_template('lottery_board.html',action = "You have selected no number yet, hurry up! Luck is not waiting for you!")
    else:
        return redirect("/")


# This route is necessary to allow user to select a number for the next lottery extraction.
# There is a time limit to choose the number: user can choose number in the first half of the month (from 1st to 15th)
@lottery.route('/lottery/<number_>',methods = ['POST'])
def play(number_):
    #guess a number for lottery
    last_day = 15 #last day of the month useful to select a number
    if current_user is not None and hasattr(current_user, 'id'):
        if request.method == 'POST': 
            number = int(number_)
            if number in range(1,100):
                #now we check for the day of month (user can choose only in the first half of month)
                today = date.today()
                day_of_month = today.day
                if day_of_month <= last_day:
                    usr = db.session.query(User).filter(User.id == current_user.id).first() #retrieve the User element to access after at its fields
                    
                    if usr.lottery_ticket_number == -1: #user doesn't already choose a number, so now he can. We save in the DB the number selected
                        usr.set_lottery_number(number)
                        db.session.commit()
                        return render_template('lottery_board.html',action = "You select the number "+str(number)+"! Good Luck!")
                    else:
                        #already choosed a number
                       return render_template('lottery_board.html',action = "You already select the number "+ str(usr.lottery_ticket_number)+"! Good Luck!")
                else:
                    #can't choose a number because it's expired the usefuk time (useful time: from 1st to 15th of month)
                   return render_template('lottery_board.html', action = "You cannot choose any more a number, the time to partecipate to lottery is expired! Try next month!")
            else:
                return render_template('lottery_board.html', action = "You choose an invalid number for the lottery! You can choose only number from 1 to 99 !")
        else:
            raise RuntimeError('This should not happen!')
    else:
        return redirect("/", code = 304)

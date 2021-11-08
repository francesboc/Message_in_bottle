import wtforms as f
from flask_wtf import FlaskForm
from flask_login import current_user
from wtforms.validators import DataRequired


class LoginForm(FlaskForm):
    email = f.StringField('email', validators=[DataRequired()])
    password = f.PasswordField('password', validators=[DataRequired()])
    display = ['email', 'password']


class UserForm(FlaskForm):
    email = f.StringField('email', validators=[DataRequired()])
    firstname = f.StringField('firstname', validators=[DataRequired()])
    lastname = f.StringField('lastname', validators=[DataRequired()])
    password = f.PasswordField('password', validators=[DataRequired()])
    date_of_birth = f.StringField('dateofbirth', validators=[DataRequired()])
    display = ['email', 'firstname', 'lastname', 'password', 'date_of_birth']

class UserModifyForm(FlaskForm):
    email = f.StringField('email', validators=[DataRequired()])
    firstname = f.StringField('firstname', validators=[DataRequired()])
    lastname = f.StringField('lastname', validators=[DataRequired()])
    password = f.PasswordField('password', validators=[DataRequired()])
    newpassword = f.PasswordField('new password')
    repeatnewpassword = f.PasswordField('repeat new password')
    date_of_birth = f.DateField('dateofbirth', format='%d/%m/%Y')
    display = ['email', 'firstname', 'lastname', 'password','newpassword','repeatnewpassword', 'date_of_birth']

class NewMessageForm(FlaskForm):
    destinator = f.StringField('Destinator', validators=[DataRequired()])
    title = f.StringField('Title', validators=[DataRequired()])    
    content = f.TextAreaField('Content')
    display = ['destinator', 'title','content']

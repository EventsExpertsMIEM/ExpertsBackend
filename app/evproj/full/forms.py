from flask_wtf import FlaskForm
from wtforms import (BooleanField, StringField, PasswordField, validators,
                     TextAreaField, RadioField, IntegerField)


class AuthForm(FlaskForm):
    mail = StringField('Mail', [validators.DataRequired()])
    password = PasswordField('Password', [validators.DataRequired()])


class RegisterForm(FlaskForm):
    mail = StringField('Email', [validators.DataRequired()])
    name = StringField('Name', [validators.DataRequired()])
    surname = StringField('Surname', [validators.DataRequired()])
    password = PasswordField('Password', [validators.DataRequired()])
    password_repeat = PasswordField('Password', [validators.DataRequired()])


class CreateEvent(FlaskForm):
    name = StringField('Name', [validators.DataRequired()])
    sm_description = StringField('Sm_description', [validators.DataRequired()])
    description = StringField('Description', [validators.DataRequired()])
    date_time = StringField('Date_time', [validators.DataRequired()])
    phone = StringField('Phone', [validators.DataRequired()])
    mail = StringField('Mail', [validators.DataRequired()])
    presenters = StringField('Presenters')

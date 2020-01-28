from flask_wtf import FlaskForm
from wtforms import (BooleanField, StringField, PasswordField, validators,
                     TextAreaField, RadioField, IntegerField)


# todo
class NewQuestion(FlaskForm):
    question = StringField('Name', [validators.DataRequired()])
    desc = StringField('Description', [validators.DataRequired()])

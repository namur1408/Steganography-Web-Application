from flask_wtf import FlaskForm
from wtforms.validators import DataRequired
from wtforms import FileField, SubmitField, TextAreaField
from models import Message

class MessageForm(FlaskForm):
    text = TextAreaField('Text', validators=[DataRequired()])
    photo = FileField('Photo', validators=[DataRequired()])

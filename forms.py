from flask_wtf import FlaskForm
from wtforms.validators import DataRequired
from wtforms import TextAreaField, FileField
from models import Message

class MessageForm(FlaskForm):
    text = TextAreaField(validators=[DataRequired()])
    photo = FileField(validators=[DataRequired()])
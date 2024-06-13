import re

from flask_wtf import FlaskForm
from wtforms import FileField, StringField
from wtforms.validators import DataRequired, Length, ValidationError

from audio_mode import AudioMode, TOGGLE_MODE_DIALLING_NUMBER
from utils import get_tracks

phone_regex = re.compile("[0-9-+()]*")


def is_numeric_phone_number(_form, field):
    match = phone_regex.fullmatch(field.data)
    if match is None:
        raise ValidationError("Provided number is not a valid number.")


def is_not_already_existing(_form, field):
    tracks = get_tracks()
    if field.data in tracks[AudioMode.POEMS] or field.data == str(TOGGLE_MODE_DIALLING_NUMBER):
        raise ValidationError("Number is already assigned.")


class Form(FlaskForm):
    number = StringField(
        "Desired number",
        validators=[DataRequired(), Length(min=1, max=25), is_numeric_phone_number, is_not_already_existing],
    )
    file = FileField("MP3", validators=[DataRequired()])

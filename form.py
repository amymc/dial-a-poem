import re

from flask_wtf import FlaskForm
from wtforms import FileField, StringField
from wtforms.validators import DataRequired, Length, Optional, URL, ValidationError

from audio_mode import AudioMode
from utils import get_tracks

phone_regex = re.compile("[0-9-+()]*")


def is_numeric_phone_number(_form, field):
    match = phone_regex.fullmatch(field.data)
    if match is None:
        raise ValidationError("Provided number is not a valid number.")


def is_not_already_existing(_form, field):
    tracks = get_tracks()
    if field.data in tracks[AudioMode.POEMS]:
        raise ValidationError("Number is already assigned.")


class Form(FlaskForm):
    number = StringField(
        "Desired number",
        validators=[DataRequired(), Length(min=1, max=25), is_numeric_phone_number, is_not_already_existing],
    )
    file = FileField("MP3", validators=[Optional()])
    url = StringField("URL", validators=[Optional(), URL()])

    def validate(self, extra_validators=None):
        valid = super(Form, self).validate(extra_validators)
        print(valid)

        if not self.file.data and not self.url.data:
            self.file.errors.append("Either file or URL is required.")
            valid = False

        return valid

import os

from flask import flash, Flask, redirect, render_template, url_for
from flask_wtf import CSRFProtect

from audio_mode import AudioMode
from form import Form
from utils import get_tracks, write_to_file

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("FLASK_SECRET_KEY")

csrf = CSRFProtect(app)


@app.route("/", methods=["GET", "POST"])
def index():
    tracks = get_tracks()
    form = Form()

    # POST + valid
    if form.validate_on_submit():
        file = form.file.data
        number = form.number.data
        # Remove symbols
        number = number.replace("-", "").replace("+", "").replace("(", "").replace(")", "")
        write_to_file(AudioMode.POEMS, file, number)

        # Add the newest track without re-reading file
        # TODO: allow interfacing with jokes?
        tracks[AudioMode.POEMS][number] = file.filename
        flash("Successfully uploaded!")
        return redirect(url_for("index"))

    return render_template("index.html", tracks=tracks[AudioMode.POEMS], form=form)

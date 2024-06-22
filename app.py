import os

from flask import flash, Flask, redirect, render_template, url_for
from flask_wtf import CSRFProtect
from werkzeug.utils import secure_filename

from audio_mode import AudioMode
from form import Form
from utils import get_tracks, UPLOAD_FOLDER, write_to_file

app = Flask(__name__)
app.config.from_pyfile("config.cfg")

csrf = CSRFProtect(app)


@app.route("/", methods=["GET", "POST"])
def index():
    tracks = get_tracks()
    form = Form()

    # POST + valid
    if form.validate_on_submit():
        file = form.file.data
        url = form.url.data

        number = form.number.data
        # Remove symbols
        number = number.replace("-", "").replace("+", "").replace("(", "").replace(")", "")

        if file:
            filename_or_url = file.filename
            filename = secure_filename(file.filename)
            file.save(os.path.join(UPLOAD_FOLDER, filename))
        else:
            filename_or_url = url

        write_to_file(AudioMode.POEMS, filename_or_url, number)

        # Add the newest track without re-reading file
        # TODO: allow interfacing with jokes?
        tracks[AudioMode.POEMS][number] = filename_or_url
        flash("Successfully uploaded!")
        return redirect(url_for("index"))

    return render_template("index.html", tracks=tracks[AudioMode.POEMS], form=form)

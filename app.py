import os

from flask import flash, Flask, render_template
from flask_wtf import CSRFProtect

from form import Form
from utils import get_tracks, write_to_file

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY")

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
        write_to_file(file, number)

        # Add the newest track without re-reading file
        tracks[number] = file.filename
        flash("Successfully uploaded!")

    return render_template("index.html", tracks=tracks, form=form)

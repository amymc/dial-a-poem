import os
from pathlib import Path

from werkzeug.utils import secure_filename

parent = Path(__file__).resolve().parent
UPLOAD_FOLDER = parent / "tracks"
CSV_FILE = UPLOAD_FOLDER / "track-list.csv"


def get_tracks():
    """Reads the CSV track file and returns a dictionary of tracks with keys as the dial number."""
    tracks = {}

    with open(CSV_FILE, "r", encoding="UTF-8") as file:
        for line in file:
            if not line.strip():
                continue
            number, filename = line.strip().split(",")
            tracks[number] = filename.strip()

    return tracks


def write_to_file(file, number: str):
    filename = secure_filename(file.filename)
    file.save(os.path.join(UPLOAD_FOLDER, filename))
    with open(CSV_FILE, "a", encoding="UTF-8") as file:
        file.write(f"{number}, {filename}\n")

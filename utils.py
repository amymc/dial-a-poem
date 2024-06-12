import os
from pathlib import Path

from werkzeug.utils import secure_filename

from audio_mode import AudioMode

parent = Path(__file__).resolve().parent
AUDIO_DIR = Path(__file__).resolve().parent / "audio"
UPLOAD_FOLDER = AUDIO_DIR / "poems"
CSV_FILE = UPLOAD_FOLDER / "track-list.csv"


def get_tracks():
    """Reads the CSV track file and returns a dictionary of audio with keys as the dial number."""
    tracks = {}

    with open(CSV_FILE, "r", encoding="UTF-8") as file:
        for line in file:
            if not line.strip():
                continue
            audio_mode, number, filename = line.strip().split(",")
            audio_mode = AudioMode(audio_mode)
            tracks[audio_mode][number] = filename.strip()

    return tracks


def write_to_file(audio_mode: AudioMode, file, number: str):
    filename = secure_filename(file.filename)
    file.save(os.path.join(UPLOAD_FOLDER, filename))
    with open(CSV_FILE, "a", encoding="UTF-8") as file:
        file.write(f"{audio_mode}, {number}, {filename}\n")

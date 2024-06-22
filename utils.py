from pathlib import Path

from audio_mode import AudioMode

AUDIO_DIR = Path(__file__).resolve().parent / "audio"
CSV_FILE = AUDIO_DIR / "track-list.csv"
UPLOAD_FOLDER = AUDIO_DIR / "poems"


def get_tracks():
    """Reads the CSV into a dictionary with keys for the audio modes.
    Each value is another dictionary of dial number -> filename."""
    tracks = {}

    with open(CSV_FILE, "r", encoding="UTF-8") as file:
        for line in file:
            if not line.strip():
                continue

            audio_mode, number, filename = [piece.strip() for piece in line.strip().split(",")]
            audio_mode = AudioMode(audio_mode)

            if audio_mode.value not in tracks:
                tracks[audio_mode.value] = {}

            tracks[audio_mode.value][number] = filename.strip()

    return tracks


def write_to_file(audio_mode: AudioMode, filename_or_url: str, number: str):
    with open(CSV_FILE, "a", encoding="UTF-8") as file:
        file.write(f"{audio_mode}, {number}, {filename_or_url}\n")

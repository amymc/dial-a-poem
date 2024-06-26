from enum import StrEnum


class AudioMode(StrEnum):
    POEMS = "poems"
    JOKES = "jokes"


def toggle_audio_mode(audio_mode: AudioMode) -> AudioMode:
    if audio_mode == AudioMode.POEMS:
        audio_mode = AudioMode.JOKES
    else:
        audio_mode = AudioMode.POEMS

    return audio_mode

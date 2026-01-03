import librosa
import soundfile as sf
import tempfile
import os
import numpy as np

TARGET_SR = 16000  # Whisper works well with 16kHz, tiny/base variants also okay


def ensure_wav_16k(path: str) -> str:
    """
    Loads audio file, converts to mono 16kHz WAV, writes to temp file, and returns path.
    Does not modify the original file.
    """
    # librosa handles many formats
    y, sr = librosa.load(path, sr=TARGET_SR, mono=True)
    # normalize to float32 in [-1,1]
    if y.dtype != np.float32:
        y = y.astype(np.float32)
    # Write temp WAV
    fd, tmp_path = tempfile.mkstemp(suffix=".wav")
    os.close(fd)
    sf.write(tmp_path, y, TARGET_SR, subtype="PCM_16")
    return tmp_path

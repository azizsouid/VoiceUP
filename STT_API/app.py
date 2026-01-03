from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
import os
import tempfile
import logging
from faster_whisper import WhisperModel
from utils.audio import ensure_wav_16k

# Configuration
# "tiny", "small", "medium", "large-v3"...
MODEL_NAME = os.environ.get("WHISPER_MODEL", "tiny")
DEVICE = os.environ.get("WHISPER_DEVICE", "cpu")      # "cpu" or "cuda"
# e.g., "float16" if using cuda; None for default
COMPUTE_TYPE = os.environ.get("WHISPER_COMPUTE", None)

ALLOWED_EXT = {".wav", ".mp3", ".m4a", ".flac", ".ogg", ".webm"}
MAX_CONTENT_LENGTH = 50 * 1024 * 1024  # 50 MB limit

# Flask app
app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = MAX_CONTENT_LENGTH

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("stt_api")

# Load model once
logger.info(
    f"Loading Whisper model '{MODEL_NAME}' on device={DEVICE} compute_type={COMPUTE_TYPE}")
model_kwargs = {"device": DEVICE}
if COMPUTE_TYPE:
    model_kwargs["compute_type"] = COMPUTE_TYPE

model = WhisperModel(MODEL_NAME, **model_kwargs)


def allowed_file(filename: str) -> bool:
    _, ext = os.path.splitext(filename.lower())
    return ext in ALLOWED_EXT


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "model": MODEL_NAME, "device": DEVICE})


@app.route("/transcribe", methods=["POST"])
def transcribe():
    """
    Expects multipart/form-data with key 'file' as the audio file.
    Returns JSON: { transcription: str, confidence: float|null, segments: [ {start,end,text} ], info: {...} }
    """
    if "file" not in request.files:
        return jsonify({"error": "no file part"}), 400

    f = request.files["file"]
    filename = secure_filename(f.filename or "upload.wav")
    if not allowed_file(filename):
        return jsonify({"error": "unsupported file extension"}), 400

    # Save to temporary file
    with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(filename)[1]) as tmp:
        tmp_path = tmp.name
        f.save(tmp_path)
    logger.info(f"Saved uploaded file to {tmp_path}")

    try:
        # Ensure 16kHz mono WAV for best compatibility
        proc_path = ensure_wav_16k(tmp_path)
        logger.info(f"Preprocessed audio saved to {proc_path}")

        # Model transcription
        # faster-whisper returns (segments, info)
        segments, info = model.transcribe(proc_path, beam_size=5)

        # Build text and segments list
        text = "".join([s.text for s in segments])
        segs = [{"start": float(s.start), "end": float(
            s.end), "text": s.text} for s in segments]

        # Compute confidence heuristic
        avg_logprobs = [getattr(s, "avg_logprob", None) for s in segments]
        avg_logprobs = [v for v in avg_logprobs if v is not None]
        if len(avg_logprobs) > 0:
            avg_lp = sum(avg_logprobs) / len(avg_logprobs)
            # Heuristic: map typical negative logprob to 0-1 range: clamp
            confidence = max(0.0, min(1.0, 1.0 - (abs(avg_lp) / 10.0)))
        else:
            # Fallback: try info fields (if present)
            # info may have 'avg_logprob' or 'no_speech_prob'
            avg_lp = info.get("avg_logprob") if isinstance(
                info, dict) else None
            if avg_lp is not None:
                confidence = max(0.0, min(1.0, 1.0 - (abs(avg_lp) / 10.0)))
            else:
                confidence = None

        result = {
            "transcription": text.strip(),
            "confidence": confidence,
            "segments": segs,
            "info": info if isinstance(info, dict) else {}
        }
        return jsonify(result)

    except Exception as e:
        logger.exception("Error during transcription")
        return jsonify({"error": str(e)}), 500

    finally:
        # clean temporary files
        try:
            os.remove(tmp_path)
        except Exception:
            pass
        try:
            if 'proc_path' in locals() and os.path.exists(proc_path):
                os.remove(proc_path)
        except Exception:
            pass


if __name__ == "__main__":
    # Production: run behind gunicorn. For local dev:
    app.run(host="0.0.0.0", port=5000, debug=False, threaded=True)

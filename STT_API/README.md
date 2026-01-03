STT_API - Flask Whisper transcription service

Quick start (already inside your venv with libraries installed):

1) Set environment (optional)
   export WHISPER_MODEL=tiny
   export WHISPER_DEVICE=cpu
   export WHISPER_COMPUTE=float16  # optional for cuda

2) Run Flask app (dev)
   python app.py
   # for production use: gunicorn -w 4 -b 0.0.0.0:5000 app:app

3) Test with local file
   python client_post.py ../audio_files/file.wav

Notes:
- The service resamples uploaded audio to 16kHz mono before sending to Whisper.
- Confidence is a heuristic derived from segment logprobs (if available).
- To support hybrid client fallback, have your Flutter app attempt local ONNX inference first and call this endpoint when local confidence is low or ONNX fails.

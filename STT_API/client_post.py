import requests
import sys
import json


def post_file(url, file_path):
    with open(file_path, "rb") as f:
        files = {"file": (file_path, f, "audio/wav")}
        resp = requests.post(url, files=files, timeout=120)
    try:
        return resp.json()
    except Exception:
        return {"status_code": resp.status_code, "text": resp.text}


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python client_post.py /path/to/file.wav")
        sys.exit(1)
    audio = sys.argv[1]
    url = "http://127.0.0.1:5000/transcribe"
    print("Posting", audio, "to", url)
    out = post_file(url, audio)
    print(json.dumps(out, indent=2, ensure_ascii=False))

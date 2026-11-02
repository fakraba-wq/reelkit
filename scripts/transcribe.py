#!/usr/bin/env python3
"""Transcribe a video/audio file to word-level timestamps with Groq Whisper.

Usage: python transcribe.py input.mp4 [-o words.json] [--lang ar]
Needs: ffmpeg on PATH, GROQ_API_KEY in the environment. Stdlib only.
"""
import argparse, json, os, subprocess, sys, tempfile, uuid
from urllib import request

URL = "https://api.groq.com/openai/v1/audio/transcriptions"


def to_mp3(src, dst):
    subprocess.run(["ffmpeg", "-y", "-i", src, "-vn", "-ac", "1", "-ar", "16000",
                    "-b:a", "48k", dst], check=True, capture_output=True)


def multipart(fields, file_field, path):
    boundary = uuid.uuid4().hex
    body = bytearray()
    for k, v in fields:
        body += ('--%s\r\nContent-Disposition: form-data; name="%s"\r\n\r\n%s\r\n'
                 % (boundary, k, v)).encode()
    body += ('--%s\r\nContent-Disposition: form-data; name="%s"; filename="%s"\r\n'
             'Content-Type: audio/mpeg\r\n\r\n'
             % (boundary, file_field, os.path.basename(path))).encode()
    with open(path, "rb") as f:
        body += f.read()
    body += ("\r\n--%s--\r\n" % boundary).encode()
    return bytes(body), "multipart/form-data; boundary=" + boundary


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("input")
    ap.add_argument("-o", "--out", default="words.json")
    ap.add_argument("--lang", default=None, help="ISO code, e.g. ar, en, fr (auto if omitted)")
    ap.add_argument("--model", default="whisper-large-v3")
    a = ap.parse_args()

    key = os.environ.get("GROQ_API_KEY")
    if not key:
        sys.exit("Set GROQ_API_KEY first.")

    with tempfile.TemporaryDirectory() as tmp:
        mp3 = os.path.join(tmp, "audio.mp3")
        to_mp3(a.input, mp3)
        fields = [("model", a.model), ("response_format", "verbose_json"),
                  ("timestamp_granularities[]", "word")]
        if a.lang:
            fields.append(("language", a.lang))
        body, ctype = multipart(fields, "file", mp3)
        req = request.Request(URL, data=body, headers={
            "Authorization": "Bearer " + key, "Content-Type": ctype,
            "User-Agent": "reelkit/0.1"})
        with request.urlopen(req) as r:
            data = json.load(r)

    words = [{"word": w["word"].strip(), "start": w["start"], "end": w["end"]}
             for w in data.get("words", [])]
    with open(a.out, "w", encoding="utf-8") as f:
        json.dump({"text": data.get("text", ""), "words": words}, f, ensure_ascii=False, indent=2)
    print("%d words -> %s" % (len(words), a.out))


if __name__ == "__main__":
    main()

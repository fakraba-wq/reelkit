#!/usr/bin/env python3
"""Turn words.json (from transcribe.py) into short caption chunks.

Usage: python captions.py words.json [--max-words 3] [--srt out.srt] [--json out.json]
Chunks break on punctuation or a pause > 0.4 s. Works with RTL text (Arabic).
"""
import argparse, json


def chunk(words, max_words, gap=0.4):
    out, cur = [], []
    for i, w in enumerate(words):
        cur.append(w)
        nxt = words[i + 1] if i + 1 < len(words) else None
        end_punct = w["word"].rstrip()[-1:] in ".?!,؟،"
        if (len(cur) >= max_words or end_punct or nxt is None
                or nxt["start"] - w["end"] > gap):
            out.append({"text": " ".join(x["word"] for x in cur),
                        "start": cur[0]["start"], "end": cur[-1]["end"]})
            cur = []
    return out


def ts(t):
    h, r = divmod(t, 3600)
    m, s = divmod(r, 60)
    return "%02d:%02d:%02d,%03d" % (h, m, int(s), int((s % 1) * 1000))


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("words")
    ap.add_argument("--max-words", type=int, default=3)
    ap.add_argument("--srt", default="captions.srt")
    ap.add_argument("--json", default="captions.json")
    a = ap.parse_args()

    with open(a.words, encoding="utf-8") as f:
        words = json.load(f)["words"]
    caps = chunk(words, a.max_words)
    with open(a.json, "w", encoding="utf-8") as f:
        json.dump(caps, f, ensure_ascii=False, indent=2)
    with open(a.srt, "w", encoding="utf-8") as f:
        for i, c in enumerate(caps, 1):
            f.write("%d\n%s --> %s\n%s\n\n" % (i, ts(c["start"]), ts(c["end"]), c["text"]))
    print("%d captions -> %s, %s" % (len(caps), a.srt, a.json))


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Remove dead air from a clip with ffmpeg.

Usage: python cut_silence.py input.mp4 -o tight.mp4 [--noise -32] [--min 0.35] [--pad 0.08]
Prints the kept segments as JSON on stderr.
"""
import argparse, json, re, subprocess, sys


def duration(path):
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                          "-of", "csv=p=0", path], capture_output=True, text=True, check=True)
    return float(out.stdout.strip())


def silences(path, noise, min_len):
    p = subprocess.run(["ffmpeg", "-i", path, "-af",
                        "silencedetect=noise=%sdB:d=%s" % (noise, min_len),
                        "-f", "null", "-"], capture_output=True, text=True)
    starts = [float(x) for x in re.findall(r"silence_start: ([\d.]+)", p.stderr)]
    ends = [float(x) for x in re.findall(r"silence_end: ([\d.]+)", p.stderr)]
    return list(zip(starts, ends))


def keep_segments(total, sil, pad):
    segs, cur = [], 0.0
    for s, e in sil:
        if s - cur > 0.05:
            segs.append([max(cur - pad, 0.0), min(s + pad, total)])
        cur = e
    if total - cur > 0.05:
        segs.append([max(cur - pad, 0.0), total])
    return segs


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("input")
    ap.add_argument("-o", "--out", default="tight.mp4")
    ap.add_argument("--noise", type=float, default=-32)
    ap.add_argument("--min", type=float, default=0.35)
    ap.add_argument("--pad", type=float, default=0.08)
    a = ap.parse_args()

    total = duration(a.input)
    segs = keep_segments(total, silences(a.input, a.noise, a.min), a.pad)
    if not segs:
        sys.exit("Nothing to keep - lower --noise.")
    parts = []
    for i, (s, e) in enumerate(segs):
        parts.append("[0:v]trim=%.3f:%.3f,setpts=PTS-STARTPTS[v%d];"
                     "[0:a]atrim=%.3f:%.3f,asetpts=PTS-STARTPTS[a%d]" % (s, e, i, s, e, i))
    inputs = "".join("[v%d][a%d]" % (i, i) for i in range(len(segs)))
    graph = ";".join(parts) + ";%sconcat=n=%d:v=1:a=1[v][a]" % (inputs, len(segs))
    subprocess.run(["ffmpeg", "-y", "-i", a.input, "-filter_complex", graph,
                    "-map", "[v]", "-map", "[a]", "-c:v", "libx264", "-crf", "18",
                    "-c:a", "aac", a.out], check=True, capture_output=True)
    kept = sum(e - s for s, e in segs)
    print("%.1fs -> %.1fs (%d segments) -> %s" % (total, kept, len(segs), a.out))
    print(json.dumps(segs), file=sys.stderr)


if __name__ == "__main__":
    main()

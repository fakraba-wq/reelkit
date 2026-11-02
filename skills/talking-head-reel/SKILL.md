---
name: talking-head-reel
description: Edit a raw 9:16 talking-head clip into a finished reel - cut dead air, transcribe, build short captions, then compose in Remotion. Use when the user drops a raw clip and asks for a reel, captions, or a tighter cut.
---

# Talking-head reel

Edit the WHOLE clip, never a demo. Use real footage and real images from the web for anything the speaker mentions.

## Pipeline
1. **Tighten**: `python scripts/cut_silence.py raw.mp4 -o tight.mp4`
2. **Transcribe** the tightened file (never the raw one, so timings match):
   `python scripts/transcribe.py tight.mp4 -o words.json [--lang ar]`
3. **Caption chunks**: `python scripts/captions.py words.json --max-words 3`
4. **Plan** one visual per spoken idea (screenshot, logo, clip). Write the plan to `plan.md` before building.
5. **Compose** in Remotion with `captions.json` as props; keep captions inside the Reels safe zone (top 14% and bottom 22% free).
6. **QA**: export frames at each cut and check captions, faces and safe zone before declaring done.

## Rules
- Open on the speaker within 2-3 seconds.
- Captions: 1-3 words, one highlighted payload word per line. RTL languages stay RTL.
- Do not invent logos or stats; source them or leave them out.
- Never commit API keys; read `GROQ_API_KEY` from the environment.

# 🔬 How to reverse-engineer any video edit

Goal: take a reel you admire and turn its editing style into numbers, rules and a repeatable Claude Code skill. Always use reference videos for study only. Copy the *technique*, never the footage, logos or music.

```
reference video ──► measure ──► study frames ──► write style bible ──► build skill ──► test on your clip
```

## Step 1 · Get the reference 📥
Download a copy you are allowed to study (your own posts, or a public video for analysis):
```bash
yt-dlp -f "bv*[height<=1080]+ba/b" -o ref.mp4 "<video-url>"
```

## Step 2 · Measure the pacing ⏱️
Detect scene cuts and compute shot lengths.
```bash
ffmpeg -i ref.mp4 -vf "select='gt(scene,0.30)',showinfo" -an -f null - 2>&1 | grep pts_time
```
Write down:
- number of cuts and **average shot length** (reels are often 1.2-2.5 s)
- shortest and longest shot
- where the hook ends (usually the first 2-3 s)

## Step 3 · Contact sheets 🖼️
Pull one frame per second into a grid so you can *see* the structure.
```bash
ffmpeg -i ref.mp4 -vf "fps=1,scale=240:-1,tile=8x6" -frames:v 1 sheet.png
```
For every shot note: layout (full-bleed, split, card), what the visual is (screenshot, logo, footage), and how it relates to the spoken line.

## Step 4 · Audio and speech 🔊
```bash
ffmpeg -i ref.mp4 -af ebur128 -f null - 2>&1 | tail -n 12     # loudness (LUFS)
python scripts/transcribe.py ref.mp4 -o ref_words.json           # words per second
```
Record loudness, words per second, where sound effects land (usually on cuts and big words) and whether music is present.

## Step 5 · Captions 💬
From `ref_words.json` plus the frames, note: font style, size, position, how many words per chunk, which word is highlighted, animation (pop, slide, typewriter). Run `python scripts/captions.py ref_words.json --max-words 3` to compare your chunking with theirs.

## Step 6 · Colour and motion 🎨
Sample 3-5 dominant colours from several frames and note camera motion (punch-in, drift, whip), easing (fast out, slow in) and transition type (hard cut, flash, glitch).

## Step 7 · Write the style bible 📖
One page, three sections:
1. **Measured numbers**: shot length, words per caption, loudness, cuts per minute.
2. **Rules**: "open on the speaker in 2 s", "one visual per spoken idea", "captions in the safe zone".
3. **Do-nots**: things that would break the look (dark bands, stock footage clichés, invented logos).

## Step 8 · Turn it into a skill 🧩
Create `skills/<style-name>/SKILL.md` with frontmatter (`name`, `description` saying when to trigger) followed by the pipeline and the style bible. Reuse the three scripts for the mechanical parts and let Claude Code handle the creative decisions.

## Step 9 · Test and iterate ✅
Render the full video (never a demo), export a frame at every cut, and compare against the reference contact sheet. Fix the largest difference first, then re-render. Stop when the pacing, caption behaviour and layout match within a small margin.

## Checklist
- [ ] Shot-length numbers recorded
- [ ] Contact sheet reviewed shot by shot
- [ ] Loudness and speech pace noted
- [ ] Caption behaviour described
- [ ] Style bible written
- [ ] Skill tested on a full clip

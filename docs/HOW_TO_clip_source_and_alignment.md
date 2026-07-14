# How to Find a Clearer Clip Source and Re-cut It

The site's policy is to look for a clearer source before upscaling anything (see the [Topaz upscaling guide](HOW_TO_topaz_upscaling.md)). This guide covers what to do once you go looking: how to tell whether a candidate source is genuinely better, and how to re-cut a clip from it so the existing subtitles and audio description still line up.

Replacing a clip that already has subtitles and audio description is the delicate part. Those files are timed to the clip's timeline. If the new cut starts even slightly off, every caption and every AD cue drifts with it — so most of this guide is about getting the timing right.

---

## The Workflow

```
Check what the source     →   Compare the        →   Find where the      →   Cut, align,
really offers                 picture                clip starts             and verify
──────────────────────        ────────────────       ─────────────────       ──────────────
yt-dlp -F                     Frames side by side    Match the audio         Same duration,
Is the ceiling high           Does it actually       against the full        same R2 key,
enough to be worth it?        look better?           film's audio track      offset < 1 frame
```

---

## When to Use This

- An existing clip looks soft, blocky, or washed out
- You have found another upload of the same film that might be better
- A clip's framing looks cropped or zoomed compared to the original film

---

## A Resolution Number Can Lie

This is the single most important thing in this guide.

A clip stored as `1920x1080` is not necessarily a 1080p clip. It may be an **upscale** of a low-resolution source — the pixel count is high, but the real detail is not there. Upscaling cannot invent detail; it only enlarges what already exists, compression artifacts included.

Feiyimeng clips 3 and 4 were exactly this. Both were stored at `1920x1080`, and both turned out to be upscales: dark areas broke into visible blocks, edges were soft, and the film's wide scope frame had been cropped to fill 16:9, losing picture at the sides. A clean **native 480p** source replaced both. It has fewer pixels, but it looks better — and the files came out roughly ten times smaller.

> **Judge a source by looking at it, not by its label.** A clean 480p can beat a bad 1080p upscale.

---

## Step 1 — Find out what the source really offers

```
yt-dlp -F "https://www.youtube.com/watch?v=VIDEO_ID"
```

This lists every resolution the video actually has. If its ceiling is lower than what is already on the site, the source is only worth using if it wins on something else — cleaner encoding, uncropped framing, or no burned-in watermark.

> **Watch for this warning:** if yt-dlp says `No supported JavaScript runtime could be found`, some formats may be hidden and the list cannot be trusted. Install one (`brew install deno` on Mac), then run the command again before drawing any conclusion. Otherwise you may reject a source that actually does have a higher resolution.

---

## Step 2 — Compare the picture, not the numbers

Pull one frame from the live clip and one from the candidate source at the same moment, and look at them side by side. Ask Claude Code:

```
Extract a frame from the live clip at <R2 URL> and from <YouTube URL> at
<timestamp>, and show them side by side so I can compare the real detail.
```

Look for compression blocks in the dark areas, soft edges, and whether one version is cropped. Only continue if the new source genuinely looks better.

---

## Step 3 — Find where the clip starts in the new source

If you already know the timestamp, use it.

If you don't, Claude Code can find it automatically by matching the existing clip's audio against the full film's audio track — the same scene has the same waveform, so the match points straight at it.

> **The automatic match is systematically about 35 ms late.** It searches a short clip against a feature-length track, and that costs precision. Treat the result as a starting point, never as final. Step 4 corrects it.

---

## Step 4 — Cut, then measure the offset and correct it

After cutting, measure the alignment **directly**: the old clip against the new one, same length, compared head to head. This is far more precise than the search in Step 3, because it compares two short clips instead of hunting through a whole film.

Then re-cut with the start shifted by whatever offset comes back, and measure again.

Ask Claude Code:

```
Measure the offset between the old clip and my new cut by correlating their
audio, then re-cut with the start corrected so the offset is near zero.
```

**Aim for an offset well under one frame** — at 25 fps, one frame is 40 ms. For reference, the corrected Feiyimeng clips landed at 0.4 ms and 1 ms.

Then confirm it with your eyes: pull matching frames from both versions at several timestamps and check that they show the same shots — including one near the very end, where any drift shows up worst.

---

## Step 5 — Keep the timeline and the filename

Two rules that save you a great deal of work:

1. **Cut the new clip to the same duration as the old one.**
2. **Upload it under the same R2 key.**

Do both, and nothing else has to change. The subtitle files, the audio-description cues, and the `<source src=...>` line on the play page all keep working untouched.

> If the new cut is even slightly shorter than the old one, check the **last** subtitle cue. A clip that ends before its final caption does will cut that caption off.

---

## Step 6 — Back up, upload, and verify

**Overwriting a file on R2 is irreversible.** Download the current one first:

```
curl -o backup_of_old_clip.mp4 "https://pub-41c640610b8146e0a2c6dc8915ac1f9d.r2.dev/PATH/TO/CLIP.mp4"
```

Keep the backup until you have played the new clip on the live page and confirmed everything still lines up. Restoring is then just a matter of uploading the backup over the new file.

After uploading, open the play page and **hard-refresh** (**Cmd+Shift+R** on Mac, **Ctrl+Shift+R** on Windows) — R2 is served through a CDN cache, so without this you may still see the old video. Then:

- Play the clip and check the picture
- Switch between the Chinese and English subtitles and confirm they land on the right lines
- Play the audio description and confirm the cues still fall in the silent gaps, not over dialogue

---

## The Script

`clip_from_youtube.sh` in the project root does the download, transcode, and upload in one command:

```
./clip_from_youtube.sh \
  --url   "https://www.youtube.com/watch?v=VIDEO_ID" \
  --start 01:09:23.601 --end 01:11:31 \
  --key   guan-hanqing/feiyimeng-1964-opera-film/Feiyimeng_1964_OperaFilm_Clip_3_2x.mp4
```

Useful options:

| Option | What it does |
|---|---|
| `--no-upload` | Make the file locally and stop. **Use this first, every time.** |
| `--height N` | Cap the resolution (default 1080) |
| `--crop W:H:X:Y` | Crop the picture, e.g. to remove black bars |
| `--webm` | Also produce and upload a `.webm` |

The script needs `CLOUDFLARE_API_TOKEN` for the upload step; it lives in `.env` in the project root. It appends the source URL and segment of every clip it uploads to `video_sources.tsv`, so the provenance of each clip stays recorded.

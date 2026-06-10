# How to Upscale Videos with Topaz Video AI

Topaz Video AI is a tool that improves the quality of older or low-resolution video clips before they are uploaded to the CTC website. This guide covers the basic workflow for upscaling video clips for web use.

---

## When to Use Topaz

Use Topaz when a video clip:
- Looks blurry or pixelated
- Was recorded in a low resolution (e.g. old film transfers, VHS recordings)
- Has visible noise or grain that distracts from the content

You do **not** need to upscale clips that are already clear and high-resolution.

---

## The Workflow

```
Teams / Source/      →   Topaz Video AI   →   Teams / Processed/   →   Cloudflare R2
────────────────         ───────────────       ──────────────────       ─────────────
Original raw clip    →   Upscale & export  →   Save processed clip  →   Upload for web
```

---

## Step 1 — Get the source clip from Teams

1. Open Microsoft Teams and go to the **CTC project channel**
2. Click **Files** and open **Source / [play-name] / [year]-[type] /**
3. Download the original video file to your computer

> Always work from **Source/** — never upscale a file that is already in Processed/.

---

## Step 2 — Open Topaz Video AI

Open **Topaz Video AI** from your Applications folder (Mac) or Start menu (Windows).

---

## Step 3 — Import the video

1. Click **Add Media** or drag your video file into the Topaz window
2. The clip will appear in the preview panel

---

## Step 4 — Choose the right model

Topaz offers several AI models. Choose based on your clip type:

| Model | Best for |
|---|---|
| **Proteus** | General upscaling — good default choice |
| **Artemis** | Old or heavily degraded footage (VHS, film grain) |
| **Iris** | Close-up faces and fine detail |
| **Nyx** | Very noisy or dark footage |

For most CTC clips (opera films, recorded performances), start with **Proteus**.

---

## Step 5 — Set the output resolution

Under **Output Settings**, set the resolution based on the original:

| Original resolution | Recommended output |
|---|---|
| 240p / 360p | 1080p |
| 480p (SD) | 1080p |
| 720p (HD) | 1080p or keep as-is |
| 1080p or higher | No upscaling needed |

---

## Step 6 — Set the output format

Under **Export Settings**:

- **Format:** MP4
- **Codec:** H.264
- **Quality:** CRF 23 (good balance of quality and file size for web)

Avoid very high bitrates — large files slow down the website for visitors.

---

## Step 7 — Set the output file name and location

Save the exported file using the CTC naming convention:

```
[PlayName]_[Year]_Clip_[N].mp4
```

Examples:
- `Mulan_1956_Clip_1.mp4`
- `Mudanting_1986_Clip_2.mp4`

Save it to a folder on your computer that you will then copy to Teams.

---

## Step 8 — Export the video

Click **Export** and wait for Topaz to process the clip. Processing time depends on the clip length and your computer speed — a 1-minute clip may take 5–20 minutes.

---

## Step 9 — Check the result

Before saving to Teams, watch the exported clip and check:
- The image is noticeably clearer than the original
- There are no visual glitches or artifacts (smearing, flickering, strange edges)
- The audio is intact and in sync with the video

If the result looks wrong, try a different model or adjust the settings and export again.

---

## Step 10 — Save to Teams and upload to R2

1. Copy the exported file to **Teams / Processed / [play-name] / [year]-[type] /**
2. Copy it to `ctc-jekyll/assets/plays/[play-name]/[year]-[type]/` on your computer
3. Upload it to Cloudflare R2 following the steps in **HOW_TO.md, Section 7, Step 6**

---

## Tips

- **Keep the original** — never delete or overwrite the source file in Teams / Source/
- **Clip first, then upscale** — if you only need a short section of a longer video, trim it first before running Topaz (upscaling a shorter clip is much faster)
- **Compare before and after** — Topaz has a split-screen preview; use it to check the improvement before exporting
- **File size** — upscaled files are larger than the originals; aim to keep clips under 100MB for smooth web playback

---

## Need Help?

Contact the project manager if you get stuck at any step.

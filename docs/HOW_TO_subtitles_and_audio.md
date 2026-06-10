# How to Make Subtitles, Sound Labels, and Audio Descriptions

This guide explains the full workflow for creating accessibility files for video clips on the CTC website.

---

## Overview: Three Types of Accessibility Files

| Type | What it does | Tool used |
|---|---|---|
| **Subtitles** | Displays spoken words as on-screen text | Arctime (for timestamping) |
| **Sound labels** | Labels significant non-speech sounds (music, applause) | Gemini API or manual editing |
| **Audio descriptions** | Describes what is happening visually, read aloud for blind viewers | Gemini API (text) + OpenAI API (audio) |

---

## Before You Start — Install Required Tools

You only need to do this once.

### Install Arctime Pro

Download and install Arctime Pro from https://arctime.org

### Install Python and the Python extension in VS Code

1. Download and install Python from https://www.python.org (click "Latest Release")
   - **🪟 Windows only:** during installation, check the box **"Add Python to PATH"**
2. Open VS Code
3. Click the **Extensions** icon ( `⊞` ) in the left sidebar
4. Search for **Python** (published by Microsoft)
5. Click **Install**

Once installed, VS Code can run Python scripts directly and highlight errors in your code.

### Install Python packages for Gemini and OpenAI APIs

Open the VS Code terminal and run:

**🍎 Mac**
```
pip3 install google-generativeai openai
```

**🪟 Windows**
```
pip install google-generativeai openai
```

> If `pip` is not found, make sure you completed the Python installation step above and restarted VS Code.

### Set your API keys

You need two API keys — one for Gemini and one for OpenAI. Set them in the VS Code terminal before running any scripts:

**🍎 Mac**
```
export GEMINI_API_KEY=your_gemini_key_here
export OPENAI_API_KEY=your_openai_key_here
```

**🪟 Windows (Git Bash)**
```
export GEMINI_API_KEY=your_gemini_key_here
export OPENAI_API_KEY=your_openai_key_here
```

> API keys are stored in the project's `api-keys.env` file — ask the project manager for access. Never share or commit API keys to GitHub.

---

## Part 1 — Subtitles with Arctime

Subtitles are created in two stages: first write the dialogue text, then use Arctime to assign timestamps.

### Step 1 — Prepare the subtitle text

Write out the spoken dialogue from the video clip as plain text — one line per spoken segment, no timestamps needed yet.

Example:
```
Father, I will go in your place.
I have already trained with the spear.
Mother, please do not worry.
```

Save this to **Teams / Processed / [play-name] / [year]-[type] /**.

### Step 2 — Open Arctime and import the video

1. Open **Arctime Pro** on your computer
2. Import the video clip: **File → Open** and select your clip
3. The video will appear in the preview panel and the waveform on the timeline

### Step 3 — Paste your subtitle text into the Content Panel

1. Find the **Content Panel** on the right side of the screen
2. Paste your prepared subtitle text directly into the panel
3. Configure options as needed:
   - **Ignore Blank Lines** — skips empty rows when creating blocks
4. Click the button to **create subtitle blocks** from the text — Arctime will generate one block per line

### Step 4 — Assign timestamps on the timeline

For each subtitle block on the timeline:
1. Play the video (press **Spacebar**)
2. Drag each subtitle block to align it with the correct moment in the audio waveform
3. Drag the **left edge** to set the start time
4. Drag the **right edge** to set the end time
5. Double-click a block to edit the text if needed; press **Enter** to confirm
6. Press **Ctrl+Z** (Windows) / **⌘Z** (Mac) to undo any mistakes

### Step 5 — Export as VTT

Once all blocks are timestamped:
1. Go to **File → Export**
2. Choose **WebVTT (.vtt)** as the format
3. Name the file using the CTC convention: `[PlayName]_[Year]_Clip_[N].vtt`
   (e.g. `Mulan_1956_Clip_1.vtt`)
4. Save to your computer, then copy to **Teams / Processed / [play-name] / [year]-[type] /**

---

## Part 2 — Sound Labels

Sound labels describe significant non-speech sounds — music, applause, silence, sound effects. They are added to the same `.vtt` subtitle file as the spoken dialogue.

### Option A — Generate with Gemini API

Gemini can analyze the video and generate sound labels automatically. Use the following Python script, replacing the file path and prompt as needed:

```python
import google.generativeai as genai
import os

genai.configure(api_key=os.environ["GEMINI_API_KEY"])

# Upload the video clip
video_file = genai.upload_file("assets/plays/mulan/1956-opera-film/Mulan_1956_Clip_1.mp4")

model = genai.GenerativeModel("gemini-1.5-pro")

response = model.generate_content([
    video_file,
    """Watch this video clip and identify all significant non-speech sounds
(music, applause, ambient noise, sound effects, silence).

For each sound, provide:
- The timestamp when it starts and ends (in HH:MM:SS.mmm format)
- A short label in square brackets (e.g. [Orchestral music plays], [Applause])

Format the output as VTT subtitle blocks I can insert into an existing .vtt file.
Only include sounds — do not transcribe any dialogue."""
])

print(response.text)
```

Copy the output into your `.vtt` file at the correct positions alongside the dialogue lines.

> **Set your API key first:** In the VS Code terminal, run:
> `export GEMINI_API_KEY=your_key_here`

### Option B — Add manually

Open your `.vtt` file in VS Code and insert sound label blocks by hand. Sound labels go in square brackets:

```
WEBVTT

00:00:03.000 --> 00:00:07.000
[Orchestral music plays]

00:00:08.500 --> 00:00:12.000
Father, I will go in your place.

00:00:17.500 --> 00:00:19.000
[Audience applause]
```

---

## Part 3 — Audio Descriptions with Gemini API

Audio descriptions are a separate file that describes the visual content of the video for blind viewers. Gemini can generate these by analyzing the video.

### Step 1 — Generate the audio description text using Gemini

Use the following Python script, passing in your subtitle timestamps so Gemini knows where the gaps are:

```python
import google.generativeai as genai
import os

genai.configure(api_key=os.environ["GEMINI_API_KEY"])

# Upload the video clip
video_file = genai.upload_file("assets/plays/mulan/1956-opera-film/Mulan_1956_Clip_1.mp4")

# Paste your subtitle timestamps here so Gemini avoids those windows
subtitle_times = """
00:00:08.500 --> 00:00:12.000  (dialogue)
00:00:14.000 --> 00:00:17.500  (dialogue)
"""

model = genai.GenerativeModel("gemini-1.5-pro")

response = model.generate_content([
    video_file,
    f"""Watch this video clip and write an audio description for blind viewers.

Describe what is happening visually — costumes, movements, setting, 
expressions, on-screen text — only in the gaps between the dialogue times below.

Dialogue runs at:
{subtitle_times}

Format the output as VTT subtitle blocks with timestamps.
Do not describe what characters are saying — only describe what is seen.
Keep each description to 1–2 sentences."""
])

print(response.text)
```

> **Set your API key first:** `export GEMINI_API_KEY=your_key_here`

### Step 2 — Review and edit the output

Read through Gemini's output carefully and check:
- Descriptions are accurate and objective
- They fit in the gaps between dialogue (no overlap with subtitle timestamps)
- Language is clear and concise
- Nothing important is missing

Edit the text as needed in VS Code.

### Step 3 — Save the VTT file

Name it using the CTC convention: `[PlayName]_[Year]_Clip_[N]_desc.vtt`
(e.g. `Mulan_1956_Clip_1_desc.vtt`)

Save to **Teams / Processed / [play-name] / [year]-[type] /** and to `ctc-jekyll/assets/subtitles/`.

---

## Part 4 — Convert Audio Description Text to Audio with OpenAI API

For full audio description support, the text descriptions are converted into a spoken audio track using OpenAI's text-to-speech API.

### Step 1 — Extract the description text

From your `_desc.vtt` file, copy out the description text (without the VTT timestamps) — just the spoken descriptions in order.

### Step 2 — Generate the audio file using OpenAI API

Use your OpenAI API interface with a prompt or API call like:

```
Convert the following audio description text to speech.

Use a calm, clear, neutral voice at a moderate pace suitable for 
accompanying a Chinese opera film.

Text:
[paste your description text here]
```

Or using the OpenAI API directly:

```python
from openai import OpenAI
client = OpenAI()

response = client.audio.speech.create(
    model="tts-1",
    voice="alloy",        # options: alloy, echo, fable, onyx, nova, shimmer
    input="[your description text here]"
)

response.stream_to_file("Mulan_1956_Clip_1_desc.mp3")
```

### Step 3 — Review the audio

Listen to the generated audio and check:
- The pace is appropriate (not too fast for viewers to follow)
- Pronunciation of Chinese names and terms is acceptable
- The audio fits naturally in the gaps between dialogue

If the pronunciation of Chinese terms is wrong, manually adjust the spelling in the input text to approximate the correct sound (e.g. "Moo-lan" instead of "Mulan") and regenerate.

### Step 4 — Save the audio file

Name it: `[PlayName]_[Year]_Clip_[N]_desc.mp3`
(e.g. `Mulan_1956_Clip_1_desc.mp3`)

Save to **Teams / Processed / [play-name] / [year]-[type] /** and to `ctc-jekyll/assets/subtitles/`.

---

## Part 5 — Add Accessibility Files to the Website

Once all files are ready, ask Claude Code to add them to the video in the website:

```
In plays/mulan/1956-opera-film.md, find the video clip for 
Mulan_1956_Clip_1.mp4 and add:

1. A subtitle track using /assets/subtitles/Mulan_1956_Clip_1.vtt 
   with label "English"
2. An audio description track using /assets/subtitles/Mulan_1956_Clip_1_desc.vtt 
   with label "Audio Description"
```

The resulting video code will look like:

```html
<div class="clip-section">
  <div class="video-wrap">
    <video controls>
      <source src="https://pub-41c640610b8146e0a2c6dc8915ac1f9d.r2.dev/assets/plays/mulan/1956-opera-film/Mulan_1956_Clip_1.mp4" type="video/mp4">
      <track src="/assets/subtitles/Mulan_1956_Clip_1.vtt" kind="subtitles" srclang="en" label="English" default>
      <track src="/assets/subtitles/Mulan_1956_Clip_1_desc.vtt" kind="descriptions" srclang="en" label="Audio Description">
    </video>
  </div>
</div>
```

---

## File Naming Convention

| File type | Pattern | Example |
|---|---|---|
| Subtitle + sound labels | `[PlayName]_[Year]_Clip_[N].vtt` | `Mulan_1956_Clip_1.vtt` |
| Audio description (text) | `[PlayName]_[Year]_Clip_[N]_desc.vtt` | `Mulan_1956_Clip_1_desc.vtt` |
| Audio description (audio) | `[PlayName]_[Year]_Clip_[N]_desc.mp3` | `Mulan_1956_Clip_1_desc.mp3` |

---

## Need Help?

Contact the project manager if you get stuck at any step.

# CTC Teams Folder Structure

This is the canonical layout for the **Microsoft Teams** storage that backs the CTC website. It is where all source documents and media live before they are processed, uploaded to Cloudflare R2, and turned into pages. Follow it so every contributor finds files in the same place and names them the same way.

> **Teams stores files; it is not the website.** The website's text lives in GitHub (`.md` pages) and its web-ready media is served from Cloudflare R2. Teams is the working archive that feeds both.

---

## The top level

```
CTC Project Files/
│
├── About/            ← site-level documents (About, Contribute, Organization, Permissions, How-to-teach…)
├── Accessibility/    ← the accessibility checklist and testing tools
│
├── Source/           ← the authored inputs: the docs + images + the original clips
└── Processed/        ← the video-processing outputs: better clips + subtitles + audio descriptions
```

- **About/** and **Accessibility/** are documents and tools, not adaptation media, so they are **not** split into Source/Processed — they sit on their own at the top.
- **Source/** and **Processed/** mirror each other's internal shape (`Plays/…`, `Media Types/…`); the difference is only what stage the files are at. (Media-type pages have no clips, so they live only under Source/.)

### Why the split

| Folder | What it holds | Who touches it |
|---|---|---|
| **Source/** | The originally authored inputs: the Word documents (essay, `_Figures`, `_TransCharts`, `_ClipNotes`), the images, and the **original** video clips as first sourced. | Authors — this is where the writing and the first-pass media live. |
| **Processed/** | The **video-processing outputs only**: the better-sourced / upscaled clips, plus each clip's **subtitle** files (`_captions_ch.vtt`, `_captions_en.vtt`) and **audio-description** files (`_audiodesc.vtt` + `cue_*.mp3`). | Whoever re-sources, upscales, subtitles, and audio-describes the clips. |

The workflow always runs one direction:

```
Source/                         →  Processed/                        →  Cloudflare R2  →  Reclaim Hosting
docs + images + original clips     re-sourced/upscaled clips             upload for web    live website
                                   + subtitles + audio descriptions      (GitHub for .md pages)
```

> The subtitle and audio-description text files are **generated in the GitHub repo** (`assets/subtitles/…`) as part of the clip workflow; Processed/ is their archived master copy on Teams. Both stay in sync.

---

## Inside Source/ and Processed/ — Plays and Media Types

Both trees use the same two content areas, renamed for clarity from the old `Resource_for_plays` / `Modules, Media Types and Opera Styles`:

```
Plays/          ← one folder per play, then one folder per adaptation module
Media Types/    ← one folder per opera style / format (Opera Film, Kun Opera, Lianhuanhua…)
```

### Source/Plays/ — the authored inputs

```
Source/
└── Plays/
    └── mulan/                              ← play slug: lowercase, hyphens (matches the repo)
        ├── _General-Intro/
        │   ├── Mulan_Intro.docx
        │   └── Mulan_Intro_Figures.docx
        │
        └── Mulan_1956_OperaFilm/           ← one folder per module (the module base name)
            ├── Mulan_1956_OperaFilm.docx            ← essay (module prose)
            ├── Mulan_1956_OperaFilm_Figures.docx    ← figures: caption, Source, Credit, Alt per figure
            ├── Mulan_1956_OperaFilm_TransCharts.docx ← clip translations: one Chinese/English table per clip
            ├── Mulan_1956_OperaFilm_ClipNotes.docx   ← clip notes: per-clip caption (description, Source, Credit)
            ├── Mulan_1956_OperaFilm_1.jpg           ← images (numbered)
            ├── Mulan_1956_OperaFilm_2.jpg
            └── Mulan_1956_OperaFilm_Clip_1_original.mp4  ← the original clip, as first sourced
```

The **`.docx` files travel together** in the module folder: the essay (prose), `_Figures.docx` (images + captions/alt), `_TransCharts.docx` (clip subtitles/translations), and `_ClipNotes.docx` (the caption under each clip). A module with no clips omits the `_TransCharts` and `_ClipNotes` docs; one with no images omits the `_Figures` doc.

### Processed/Plays/ — the video-processing outputs, same path

```
Processed/
└── Plays/
    └── mulan/
        └── Mulan_1956_OperaFilm/
            ├── Mulan_1956_OperaFilm_Clip_1_2x.mp4              ← better-sourced / upscaled clip (goes to R2)
            ├── Mulan_1956_OperaFilm_Clip_1_captions_ch.vtt     ← Chinese subtitles
            ├── Mulan_1956_OperaFilm_Clip_1_captions_en.vtt     ← English subtitles
            ├── Mulan_1956_OperaFilm_Clip_1_audiodesc.vtt       ← audio-description cues
            └── Mulan_1956_OperaFilm_Clip_1_audiodesc/          ← the cue_*.mp3 audio-description audio
```

Same `Plays/mulan/Mulan_1956_OperaFilm/` path as in Source/ — so a clip's original and its processed version (plus that clip's subtitle and audio-description files) are one folder-swap apart (`Source/…` ↔ `Processed/…`).

### Media Types/ — format-level pages

Media-type pages are text and images only (no clips), so everything for them lives on the **Source** side:

```
Source/
└── Media Types/
    └── Kun Opera/
        ├── OperaType_Kun.docx
        ├── OperaType_Kun_Figures.docx
        └── OperaType_Kun_1.jpg …
```

They have nothing in `Processed/` unless a media-type page ever gains a video clip.

---

## Naming conventions

| Thing | Rule | Example | Lives in |
|---|---|---|---|
| Play folder | Lowercase, hyphens — same slug as the GitHub repo | `mulan`, `guan-hanqing` | both |
| Module folder & file base | `[PlayName]_[Year]_[Type]`, PascalCase | `Mulan_1956_OperaFilm` | both |
| `[Type]` values | `OperaFilm`, `Film`, `TV`, `RecordedPerf`, `Comic`, `ModernTheater`, `Print`, `Card` | — | — |
| Essay doc | `[Base].docx` | `Mulan_1956_OperaFilm.docx` | Source |
| Figures doc | `[Base]_Figures.docx` | `Mulan_1956_OperaFilm_Figures.docx` | Source |
| TransCharts doc | `[Base]_TransCharts.docx` | `Mulan_1956_OperaFilm_TransCharts.docx` | Source |
| Clip-notes doc | `[Base]_ClipNotes.docx` | `Mulan_1956_OperaFilm_ClipNotes.docx` | Source |
| Images | `[Base]_N.jpg`/`.png` | `Mulan_1956_OperaFilm_1.jpg` | Source |
| Original clip | `[Base]_Clip_N_original.mp4` | `Mulan_1956_OperaFilm_Clip_1_original.mp4` | Source |
| Processed clip | `[Base]_Clip_N_[suffix].mp4` (Topaz suffix, e.g. `_2x`) | `Mulan_1956_OperaFilm_Clip_1_2x.mp4` | Processed |
| Subtitles | `[Base]_Clip_N_captions_ch.vtt` / `_captions_en.vtt` | `..._Clip_1_captions_en.vtt` | Processed |
| Audio description | `[Base]_Clip_N_audiodesc.vtt` (+ `_audiodesc/cue_*.mp3`) | `..._Clip_1_audiodesc.vtt` | Processed |
| General intro | `_General-Intro/[Play]_Intro.docx` (+ `_Figures`) | `_General-Intro/Mulan_Intro.docx` | Source |
| Media-type doc | `MediaType_[X].docx` / `OperaType_[X].docx` (+ `_Figures`) | `OperaType_Kun.docx` | Source |

Every file for a module shares the same `[Base]` — so a clip, its subtitles, and its audio description sort together, and the Source and Processed copies sit at the same path in each tree.

---

## What is NOT on Teams

- **No source PDFs.** The original page content now lives on the site; there is no rendered `.pdf` to keep or match. (Older module folders may still contain a legacy `[Base].pdf` — leave it if archived, but do not create new ones.)
- **No `.md` pages** — those live in GitHub.

> The subtitle and audio-description files (`_captions_ch.vtt`, `_captions_en.vtt`, `_audiodesc.vtt`, `cue_*.mp3`) **do** live on Teams now, in **Processed/** — they are the video-processing outputs. They are also placed in the GitHub repo under `assets/subtitles/…` so the site can serve them; keep the two in sync.

---

## Migrating the current folders to this layout

The materials today sit in `Resource_for_plays/Modules, [Play] Materials/[Module]/` and `Modules, Media Types and Opera Styles/[Type]/`, with docs and media mixed together. To adopt this structure:

1. Create the top level: `About/`, `Accessibility/`, `Source/`, `Processed/`.
2. Move each current per-module folder into `Source/Plays/[play-slug]/[Module]/` (rename `Resource_for_plays` → `Plays`, drop the `Modules, … Materials` wrapper, lowercase the play slug). The docs, images, and original clips all belong here.
3. Move `Modules, Media Types and Opera Styles/[Type]/` into `Source/Media Types/[Type]/`.
4. As each clip is re-sourced/upscaled and given subtitles and an audio description, put those outputs in the mirror path under `Processed/Plays/[play-slug]/[Module]/`.
5. Leave `About/` documents under the new top-level `About/`.

---

## Need help?

Contact the project manager if you are unsure where a file belongs.

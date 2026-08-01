# Next Steps — Handoff

This is a handoff for whoever picks up the CTC site next. It lists what's left to do and points to the guide for each task. Work through the sections roughly in order (add pages → check accessibility → upload media → publish), and check items off as you go.

_Handoff prepared: 2026-08-01_

---

## Start here (first time on this machine)

1. Read [docs/HOW_TO.md](docs/HOW_TO.md) top to bottom once — it's the master guide. The other `docs/HOW_TO_*.md` files go deeper on specific tasks.
2. Do the one-time setup in HOW_TO.md Section 2 (VS Code, Ruby/Jekyll, Wrangler, and — if you'll touch video — yt-dlp/ffmpeg/deno).
3. Learn the local preview (HOW_TO.md Section 3): from the `ctc-jekyll` folder, serve the site and open it in the browser to check your work before publishing.
4. Get access you'll need: the **GitHub CTC2026 org** (to push), the **Cloudflare** account (R2 media uploads, `CLOUDFLARE_API_TOKEN`), and **Microsoft Teams** (source files + the accessibility checklist).

**Key idea:** every page is just a `.md` text file. You create the file, copy frontmatter from an existing page of the same kind, fill the body (usually converted from a Word doc), add it to the right sidebar menu, preview, and publish. Media (images/video) is **served from Cloudflare R2 and never committed to git**.

---

## 1. Finish the current in-progress work (do this first)

The pages listed below already exist, but their **videos are not done**. For each one you need to: source a **better-quality version** of the clip, upscale it for **clarity**, create **subtitles** and an **audio description**, and then upload the finished media to R2. Only two pages are already complete — the **Feiyimeng (1964 opera film)** page and the **landing page** — skip those; every other video page still needs the full treatment.

For every video page below:

- [ ] **Better source & clarity** — replace the current clip with a higher-quality source, then upscale with Topaz — [clip sourcing & alignment guide](docs/HOW_TO_clip_source_and_alignment.md), [Topaz upscaling guide](docs/HOW_TO_topaz_upscaling.md)
- [ ] **Subtitles** — Chinese + English `.vtt` captions, aligned to the clip — [subtitles & audio guide](docs/HOW_TO_subtitles_and_audio.md)
- [ ] **Audio description** — AD cues in the silence windows only (never overlapping dialogue), rendered to MP3 — [subtitles & audio guide](docs/HOW_TO_subtitles_and_audio.md)
- [ ] **Upload** the finished video + AD MP3s to R2 (see Section 4 below) and confirm they play on the local preview

Pages to finish (check off when the clip, subtitles, and AD are all done and uploaded):

**guan-hanqing** _(Feiyimeng 1964 is done — skip it)_
- [ ] [doue-1959-opera-film1](plays/guan-hanqing/doue-1959-opera-film1.md)
- [ ] [doue-1959-opera-film2](plays/guan-hanqing/doue-1959-opera-film2.md)
- [ ] [jiufengchen-2021-modern-theater](plays/guan-hanqing/jiufengchen-2021-modern-theater.md)
- [ ] [jiufengchen-2022-tv](plays/guan-hanqing/jiufengchen-2022-tv.md)
- [ ] [zhanizi-2016-recorded-perf](plays/guan-hanqing/zhanizi-2016-recorded-perf.md)

**mudanting**
- [ ] [1986-opera-film](plays/mudanting/1986-opera-film.md)
- [ ] [2007-recorded-perf](plays/mudanting/2007-recorded-perf.md)
- [ ] [2009-tv](plays/mudanting/2009-tv.md)

**mulan**
- [ ] [1939-film](plays/mulan/1939-film.md)
- [ ] [1956-opera-film](plays/mulan/1956-opera-film.md)
- [ ] [1964-opera-film](plays/mulan/1964-opera-film.md)
- [ ] [1998-film](plays/mulan/1998-film.md)

**orphan-of-zhao**
- [ ] [2003-performance](plays/orphan-of-zhao/2003-performance.md)
- [ ] [2005-performance](plays/orphan-of-zhao/2005-performance.md)
- [ ] [2011-tv](plays/orphan-of-zhao/2011-tv.md)

**pipaji**
- [ ] [2012-recorded-perf](plays/pipaji/2012-recorded-perf.md)

**xixiangji**
- [ ] [1940-film](plays/xixiangji/1940-film.md)
- [ ] [1965-opera-film](plays/xixiangji/1965-opera-film.md)
- [ ] [1976-opera-film1](plays/xixiangji/1976-opera-film1.md)
- [ ] [1976-opera-film2](plays/xixiangji/1976-opera-film2.md)
- [ ] [1999-film](plays/xixiangji/1999-film.md)
- [ ] [2011-recorded-perf](plays/xixiangji/2011-recorded-perf.md)

**zhangxie**
- [ ] [2017-recorded-perf](plays/zhangxie/2017-recorded-perf.md)

---

## 2. Add the new pages

- [ ] Draft each new page from its source Word doc in `~/Downloads/CTC-source-materials-TEAMS/`, matching the source exactly (wording, italics, line breaks)
- [ ] Wrap all Chinese in `<span lang="zh">…</span>`
- [ ] Use the right guide for the page type:
  - Adaptation module (one film/TV/comic/recording) → [HOW_TO.md Section 7](docs/HOW_TO.md)
  - Media type / opera style overview → [docs/HOW_TO_media.md](docs/HOW_TO_media.md)
- [ ] Add each page to the correct sidebar nav (`_data/play_nav.yml` or `_data/media_nav.yml`)
- [ ] Add figures from the page's **figures document** (`..._Figures.docx`): place each where the essay marks it, put the caption/Source/Credit in the `<figcaption>` verbatim, and use each figure's `Alt:` line as the image alt text — [HOW_TO.md Section 7, Step 5](docs/HOW_TO.md), [figure layout guide](docs/HOW_TO_figures.md), [alt text guide](docs/HOW_TO_alt_text.md)
- [ ] Preview locally and confirm layout, sidebar highlight, and Chinese rendering

> **📣 Update for new authors — figure captions and alt text now live in a `_Figures.docx`.** If you are writing source material for a page, this changes what you hand off. Each module/media page has a separate **figures document** beside its essay doc, and you are responsible for filling it in. Every figure entry gives the image's base name (which also marks the figure's spot in the essay), its `Fig. N` caption, a `Source:` line, a `Credit:` line, and — new — an `Alt:` line:
>
> ```
> Fig. 1: Panel 23, Du Liniang eyes the reader.
> Source: Liu Changhua … Jiangsu Fine Arts Press, 1986.
> Credit: Scan by CTC Project Team …
> Alt: A woman in Ming-dynasty robes turns to gaze directly out at the reader.
> ```
>
> The caption/Source/Credit go into the `<figcaption>` verbatim; the `Alt:` line becomes the image's alt text. You can write the alt text yourself **or** have Claude draft it (per the [alt text guide](docs/HOW_TO_alt_text.md)) — but the final version must go back into that figure's `Alt:` line so the page build picks it up and nothing is left blank. Older figures docs won't have `Alt:` lines yet; add them when you next touch that page. Full details: [HOW_TO.md Section 7, Step 5](docs/HOW_TO.md) and [HOW_TO_alt_text.md Part 1.5](docs/HOW_TO_alt_text.md).

_Pages still to add (fill in specifics):_
- [ ] _(play / media / module page name — source doc location)_

---

## 3. Upload processed videos (and audio) to Cloudflare R2

Do this **before** the accessibility test — the test checks that clips actually play and have captions, so the media has to be live on R2 first. Web-ready video clips and audio-description MP3s are served from the **ctc-media** R2 bucket — they are not in git. See [HOW_TO.md Section 6](docs/HOW_TO.md).

- [ ] Confirm each clip is the **upscaled** export (Topaz `_2x` / `_4k` suffix), not the raw source — [Topaz upscaling guide](docs/HOW_TO_topaz_upscaling.md)
- [ ] Place each file under `assets/plays/[play]/[year]-[type]/` locally
- [ ] Export `CLOUDFLARE_API_TOKEN`, then upload: `wrangler r2 object put ctc-media/<path> --file <path> --content-type video/mp4 --remote`
- [ ] Upload any audio-description MP3s the same way (see `upload_ad_to_r2.sh` as a template, and the [subtitles & audio guide](docs/HOW_TO_subtitles_and_audio.md))
- [ ] Spot-check each clip actually plays from R2 on the local preview

> Keep `.mp4/.mov/.jpg/.png/.gif` etc. out of every commit — media lives in R2 only.

---

## 4. Complete the accessibility test

Do this on every new or edited page (after its media is uploaded) and before publishing. Target conformance is **WCAG 2.1 AA**. See [HOW_TO.md Section 9](docs/HOW_TO.md) and the [OSU compliance doc](docs/OSU_AI_compliance_and_tool_alternatives.md).

- [ ] Run the axe check (`node a11y-axe.mjs`) against each page
- [ ] Every image has descriptive `alt` text, under 120 chars, not a copy of the figcaption — [alt text guide](docs/HOW_TO_alt_text.md)
- [ ] Headings in logical order (no skipped levels); links have meaningful text (not "click here")
- [ ] Every video clip has captions (`.vtt`) and, where applicable, sound labels + audio description — [subtitles & audio guide](docs/HOW_TO_subtitles_and_audio.md)
- [ ] Color contrast passes
- [ ] Fix everything flagged, then re-run to confirm it's clean

---

## 5. Publish on Reclaim Hosting

Two stages: push to GitHub, then deploy to the live site.

- [ ] Per page: build → verify locally → `git add` → `git commit -m "…"` → `git push` (see [HOW_TO.md Section 10](docs/HOW_TO.md))
- [ ] After pushing, **notify the project manager** — they deploy the updated site to **Reclaim Hosting** (the public site). Contributors do not have direct Reclaim access.
- [ ] Confirm the change is live on the public URL

---

## Ongoing

- Keep this file current — add new tasks as they come up so nothing is lost between sessions.
- When a workflow or tool changes, update the matching guide in [docs/](docs/) so it stays accurate.
- Questions or blockers: contact the project manager.

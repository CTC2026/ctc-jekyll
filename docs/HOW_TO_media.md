# How to Add or Edit a Media Types (Opera Styles) Page

The **Media Types** section (also called **Opera Styles**) explains a whole *format* of adaptation — Opera Film, Lianhuanhua, Television, Kun Opera, and so on — rather than one specific production. These pages live in the `media/` folder and share their own sidebar and layout, separate from the play pages.

If you are adding a page about a single film, TV show, comic, or recording, that is an **adaptation module** — use HOW_TO.md Section 7 instead. This guide is only for the format-level overview pages.

---

## How the Media section is put together

| Piece | What it is |
|---|---|
| `media/*.md` | One page per media type (e.g. `media/kun-opera.md`) |
| `media.md` | The section landing page ("Overview") — no sidebar |
| `_data/media_nav.yml` | The list that builds the left sidebar on every media page |
| `_layouts/media.html` | The layout all media pages use — draws the banner, the sidebar, and the content column |

A media page is a plain `.md` file, exactly like a play page. The only differences are the frontmatter (below) and that its sidebar comes from `media_nav.yml` rather than `play_nav.yml`.

---

## Step 1 — Create the page file

Create a new file in the `media/` folder, named with the media type's slug — lowercase, hyphens, no spaces (e.g. `media/kun-opera.md`).

Give it this frontmatter (the four lines between the `---` markers at the very top):

```yaml
---
layout: media
title: Kun Opera
permalink: /media/kun-opera/
page_class: media-kun-opera
---
```

- **layout** — always `media`.
- **title** — the section heading shown at the top of the page and in the sidebar.
- **permalink** — the page's URL, `/media/[slug]/`.
- **page_class** — optional. Add it only if the page needs its own CSS tweaks (for example, `media-kun-opera` enlarges that page's floated figures to match its source layout). If you don't need special styling, leave this line out.

Below the second `---`, write the page content in Markdown and HTML, the same way you would a play page. Wrap all Chinese characters in `<span lang="zh">…</span>`, and add figures with the standard figure classes — see the [figure layout guide](HOW_TO_figures.md).

> **Using Claude Code:** paste a prompt like —
> *"Create a new Media Types page at `media/kun-opera.md` for the media type 'Kun Opera'. Use `layout: media`, `title: Kun Opera`, `permalink: /media/kun-opera/`. Here is the text from my Word document: [paste]. Wrap Chinese in `<span lang=\"zh\">` and keep every citation, italic, and paragraph break from the source."*

---

## Step 2 — Add the page to the Media sidebar

Open `_data/media_nav.yml` and add an entry. The file is a simple flat list of title/URL pairs, in the order they appear in the sidebar:

```yaml
- title: Kunqu/Kun Opera
  url: /media/kun-opera/
```

Place it where you want it to appear in the sidebar. `Overview` (the `/media/` landing page) stays first. The `title` here can differ from the page's own `title` if you want a longer sidebar label (e.g. `Kunqu/Kun Opera`).

> **Using Claude Code:**
> *"In `_data/media_nav.yml`, add an entry titled 'Kunqu/Kun Opera' linking to `/media/kun-opera/`, after the 'Crowdsourced Productions' entry."*

The layout highlights whichever sidebar link matches the current page automatically — you don't add anything for that.

---

## Step 3 — Images and banners

- **Body figures** are added exactly as on play pages. Media images live under `assets/media/` (for example `assets/media/OperaType_Kun_1.jpeg`) and are served from Cloudflare R2, so upload them the same way as any other image (HOW_TO.md Section 7, Step 4). Write alt text and figcaptions per the [alt text guide](HOW_TO_alt_text.md), and place figures per the [figure layout guide](HOW_TO_figures.md).
- **A page banner is optional.** Media pages show a banner only if you set `banner_image` in the frontmatter; most don't, and simply open with the `title` as a heading. If you do add one, give it `banner_alt` too (or add the image to `_data/banner_alt.yml`) — see the [alt text guide](HOW_TO_alt_text.md).

---

## Step 4 — Link the modules that belong to this media type

At the bottom of a media page, list the adaptation modules that use this format, using the standard `module-list` definition list:

```html
## Modules on Lianhuanhua

<dl class="module-list">
<dt><a href="{{ '/plays/pipaji/1958-comic/' | relative_url }}">New Year's Print of <em>The Lute</em> (1958)</a></dt>
<dd markdown="span">One-line description of the module.</dd>
</dl>
```

> A single-line `<dd>` must use `markdown="span"`, **not** `markdown="1"` — otherwise the closing `</dd></dl>` tags leak onto the page as visible text.

---

## Step 5 — Preview and check

Run the local preview (HOW_TO.md Section 3) and open `http://localhost:4000/ctc-jekyll/media/[slug]/`. Confirm:

- The page appears in the Media Types sidebar, and its own entry is highlighted
- Figures sit where you expect them (no empty column beside a floated figure — see the [figure layout guide](HOW_TO_figures.md))
- Chinese text renders correctly and every citation and italic carried over from the source
- The module list at the bottom links to the right pages

Then publish following HOW_TO.md Section 9.

---

## Need Help?

Contact the project manager if you get stuck at any step.

# How to Place and Size Figures on a Page

This guide covers where an image sits on the page — floated left or right, or centered full width — and how to avoid the most common layout problem: an empty column of blank space beside a floated figure. It is about **placement**; for the words inside the image tag (alt text) and under it (figcaption), see the [alt text guide](HOW_TO_alt_text.md).

Pages are built from **text content** (the essay lives on this site now; there is no source PDF or laid-out original to copy a figure arrangement from). So placement follows the **house conventions** in this guide, using the essay text as your guide to *which* paragraph a figure belongs beside. Two rules anchor it:

- On a **play adaptation module** (film/TV/opera-film/recorded-performance), the first figure floats **right, beside the Information box** (next section).
- Every other figure sits **next to the paragraph that discusses it** — where the essay names it (e.g. "(Fig. 2)") or describes that image — floated right/left down the page, or centered full width when it's a wide or lead image.

---

## The first figure on a play module: float it right beside the Information box

On a play adaptation module, the **first figure** — almost always the film **poster** (Fig. 1) — is placed **immediately before the `<div class="module-info">` box** and given `class="module-figure-right"`. Because it floats right while the Information box stays in normal flow, the poster sits in the top-right corner **beside the Information section**, and the details list fills the column to its left. This is the standard opening layout on every play module page.

```html
## Links to the Film

- …links…

<figure class="module-figure-right">
  <img src="https://…/Feiyimeng_1964_OperaFilm_1.jpg"
       alt="Film poster: characters before a dark gate with crimson handprints; title in large red characters.">
  <figcaption><strong>Fig. 1.</strong> Film poster of <em>The Crimson Palm</em>. Source: … Credit: …</figcaption>
</figure>

<div class="module-info">
<h2>Information</h2>
<dl> … </dl>
</div>

## Introduction
```

Put the `<figure>` **above** the `module-info` div in the source, exactly as shown — that ordering is what makes the poster land to the right of the Information box rather than below it.

---

## The figure classes

Every figure is a `<figure>` with one of these classes. The class decides the placement; the image and figcaption inside are always the same shape.

| Class | Placement | Use it for |
|---|---|---|
| `module-figure-right` | Floats to the **right**; text wraps down its left side. ~300px wide (wider on the Kun Opera page). | The default for most figures — a portrait or a figure the text discusses as it flows past. |
| `module-figure-left` | Floats to the **left**; text wraps down its right side. ~300px wide. | Alternating with right-floated figures down a long article, so the page doesn't lean all to one side. |
| `module-figure` | **Centered, full width** (up to 560px), clears the text above and below. | A lead/hero image you want shown large and prominently, or a wide image that would be too small floated. |
| `figure-stack-right` | Floats **right** and stacks several `<figure>`s in one column. | Two or three related small images that belong together beside one block of text. |

The markup is identical across all of them — only the class on the `<figure>` changes:

```html
<figure class="module-figure-right">
  <img src="https://pub-41c640610b8146e0a2c6dc8915ac1f9d.r2.dev/assets/plays/mulan/1956-opera-film/Mulan_1956_OperaFilm_1.jpg"
       alt="Short visual description, under 120 characters.">
  <figcaption><strong>Fig. 1.</strong> Full caption with source and credit.</figcaption>
</figure>
```

> On phones and at high zoom (below the 56.25em breakpoint) **all** floated figures automatically stack full width and center themselves. You don't do anything for that — but it's why the layout you set only matters on a wide desktop screen.

---

## Enlarge and center a lead figure

This is **not** for the first figure on a play module — that one floats right beside the Information box (see above). But elsewhere — a media-type page, a comic/print module, or any spot where one image should open a section large and prominently — give it `class="module-figure"` rather than floating it small. It reads as the opening image of the article instead of a small aside.

```html
<figure class="module-figure">
  <img src="…" alt="…">
  <figcaption><strong>Fig. 1.</strong> …</figcaption>
</figure>
```

---

## Never leave an empty column beside a floated figure

This is the single most common figure problem, and most figure-layout commits on this project are fixing it.

A floated figure (`module-figure-right`/`-left`) is only as tall as its image. If the text meant to wrap alongside it is too short — or the next thing after the figure is a **heading** — the browser drops that content *below* the figure and leaves a tall blank column of empty space beside the photo. It looks broken.

There are three fixes. Pick whichever suits the spot:

**1. Let a heading sit beside the figure.** By default headings clear below a floated figure. To keep a heading *next to* the figure instead, tag it with `{: .beside-figure }` on the line directly under it (kramdown attribute syntax):

```markdown
### Designation as UNESCO Intangible Cultural Heritage
{: .beside-figure }

In 2001, UNESCO released its first Representative List…
```

The heading and the paragraphs after it then wrap up the right (or left) side of the figure, filling the gap. This works on any page.

**2. Intersperse the figures among the paragraphs.** If several floated figures are stacked in one short section, they pile up and overrun the text. Spread them out — move each figure down to sit beside the paragraph it actually relates to, so every figure has enough text beside it to wrap.

**3. Use a full-width figure instead.** If there simply isn't enough text in that section to wrap beside a float, don't float it — give it `class="module-figure"` so it centers full width and the text continues cleanly below.

> **How to spot it:** in the local preview (HOW_TO.md Section 3) on a wide desktop window, scroll past each figure. If you see a heading or paragraph pushed down below an image with blank space beside the image, apply one of the three fixes above.

---

## Alternate figures left and right down the page

When a page has several floated figures, alternate `module-figure-right` and `module-figure-left` so the page doesn't lean all to one side. Keep sizes consistent within a page unless one image genuinely needs to be larger (the Kun Opera page, for example, sizes its floated photos larger — at ~46% of the text column; that enlargement is enabled by its `page_class: media-kun-opera`).

---

## Check the size and position in the preview, then adjust

There is no original layout to match, so **you are the judge of how the visuals look.** After the figures are on the page, open the local preview (HOW_TO.md Section 3) on a wide desktop window and **look at every image and video**: is it on the side you want, the right size, and beside the paragraph it belongs to — with no blank column next to it? If anything looks off, don't hand-edit the HTML — describe the change to **Claude Code** and let it make the adjustment. Paste one of these prompts (edit the file path and figure name to match yours):

**Move a figure to the other side**
```
In plays/[play]/[module].md, change Fig. 3 from floating right to floating
left (module-figure-right → module-figure-left) so it alternates with the
figure above it.
```

**Make a figure bigger, smaller, or full-width**
```
In plays/[play]/[module].md, Fig. 2 looks too small floated. Make it a
centered, full-width figure instead (use class="module-figure").
```

**Move a figure next to a different paragraph**
```
In plays/[play]/[module].md, move Fig. 4 down so it sits beside the
paragraph that begins "When he arrives at the residence…", instead of
where it is now.
```

**Fix a blank column of empty space beside a figure**
```
In plays/[play]/[module].md, there is a tall blank space beside the image
before the "Theme" heading. Fix the empty column beside that floated
figure using one of the three fixes in the figure layout guide (let the
heading sit beside it with {: .beside-figure }, move the figure next to
more text, or make it full-width).
```

**Adjust a video clip's placement**
```
In plays/[play]/[module].md, move the Clip 2 video so it comes right after
its scene heading and context paragraph, and keep its translation-notes
table directly below the clip.
```

Preview again after each change to confirm it looks right. Repeat until every visual sits where you want it.

---

## Checklist before publishing

On a wide desktop preview window, confirm:

- **Play module:** the first figure (poster) floats **right, beside the Information box** — placed before the `module-info` div, with `class="module-figure-right"`
- Each figure sits beside the paragraph that discusses it, floated figures alternate left/right, and sizes are consistent within the page
- No empty column of blank space beside any floated figure
- Figures still stack cleanly when you narrow the window (mobile view)
- Every figure has alt text and a figcaption — see the [alt text guide](HOW_TO_alt_text.md)

---

## Need Help?

Contact the project manager if you get stuck at any step.

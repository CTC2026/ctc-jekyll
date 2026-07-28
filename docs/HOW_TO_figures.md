# How to Place and Size Figures on a Page

This guide covers where an image sits on the page — floated left or right, or centered full width — and how to avoid the most common layout problem: an empty column of blank space beside a floated figure. It is about **placement**; for the words inside the image tag (alt text) and under it (figcaption), see the [alt text guide](HOW_TO_alt_text.md).

The guiding rule for every module and media page: **match the source PDF.** If the author's source document floats a figure on the right at roughly half the text width, do the same. Don't impose a house layout the source didn't use.

---

## The figure classes

Every figure is a `<figure>` with one of these classes. The class decides the placement; the image and figcaption inside are always the same shape.

| Class | Placement | Use it for |
|---|---|---|
| `module-figure-right` | Floats to the **right**; text wraps down its left side. ~300px wide (wider on the Kun Opera page). | The default for most figures — a portrait or a figure the text discusses as it flows past. |
| `module-figure-left` | Floats to the **left**; text wraps down its right side. ~300px wide. | Alternating with right-floated figures down a long article, to match a source that does the same. |
| `module-figure` | **Centered, full width** (up to 560px), clears the text above and below. | A lead/hero figure (often Fig. 1) that the source presents large and prominently, or a wide image that would be too small floated. |
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

## Enlarge and center the lead figure

When the source PDF opens with one figure shown large and centered — commonly Fig. 1 — give it `class="module-figure"` rather than floating it small. This is the "center/enlarge Fig. 1" pattern used across the media and play pages. It reads as the opening image of the article instead of a small aside.

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

## Match the source's left/right rhythm

When a source article alternates figures left and right down the page, reproduce that: alternate `module-figure-left` and `module-figure-right` so the layout tracks the original. Keep sizes consistent within a page unless the source deliberately varies them (the Kun Opera page, for example, sizes its floated photos larger — at ~46% of the text column — to match its source; that enlargement is enabled by its `page_class: media-kun-opera`).

---

## Checklist before publishing

On a wide desktop preview window, confirm:

- Each figure is on the same side (left/right/centered) and roughly the same relative size as in the source PDF
- No empty column of blank space beside any floated figure
- The lead figure is centered and enlarged if the source shows it that way
- Figures still stack cleanly when you narrow the window (mobile view)
- Every figure has alt text and a figcaption — see the [alt text guide](HOW_TO_alt_text.md)

---

## Need Help?

Contact the project manager if you get stuck at any step.

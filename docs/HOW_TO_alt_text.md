# How to Write Alt Text and Add It to the Website

Alt text (alternative text) is a short written description of an image. It is read aloud by screen readers for blind and low-vision users, and displayed if an image fails to load. Good alt text is required for every image on the CTC website.

---

## What Makes Good Alt Text

| Rule | Example |
|---|---|
| Describe what is **in** the image | "A woman in military armor stands on a stage" |
| Include **context** relevant to the module | "Chen Yunshang as Hua Mulan in the 1939 film" |
| Keep it **concise** — one or two sentences maximum | ✓ |
| Do **not** start with "Image of..." or "Photo of..." | Screen readers already announce it is an image |
| Do **not** repeat the caption word for word | The caption is for everyone; alt text is for those who cannot see the image |
| If the image is **decorative** and adds no information, use `alt=""` | Leave the alt attribute empty — do not skip it entirely |

### Examples

| Image | Poor alt text | Good alt text |
|---|---|---|
| A film still of an actress in costume | "image001.jpg" | "Chen Yunshang as Hua Mulan in military armor, 1939 film" |
| A woodblock print of the Western Wing | "old print" | "Woodblock illustration showing the garden scene from The Story of the Western Wing, 1640 edition" |
| A decorative divider line | "line.png" | *(leave blank: `alt=""`)* |

---

## Accessibility Rules (from the CTC Review Checklist)

These rules are drawn from the accessibility criteria used in the CTC image review spreadsheet and are based on standard P.1.1: *Meaningful images must have equivalent text descriptions.*

### When is an image "meaningful"?

An image is meaningful — and requires alt text — if it:
- Illustrates the main content of the module
- Suggests mood or tone
- Conveys a specific visual or sensory experience

Purely decorative images (borders, dividers, background patterns) use `alt=""`.

### Rules for writing alt text

| Rule | Notes |
|---|---|
| **Under 120 characters** | A brief visual summary — what you see in the image; long alt text is hard to follow when read aloud |
| **Do not duplicate the figcaption** | The alt text and figcaption serve different purposes: alt text = quick visual description; figcaption = full context, source, and credits. Write the alt text to add something the figcaption does not say, not to shorten it. If the figcaption already fully describes the image, use `alt=""` |
| **Do not include source or credit information** | Publication titles, dates, and credits belong in the figcaption, not the alt text |
| **Avoid parentheses** | Parentheses can be read awkwardly by screen readers; rewrite as a full sentence instead |
| **Write a complete sentence or phrase** | Incomplete descriptions leave blind users without enough context |
| **Describe what can be seen** | Describe the specific visual content — gestures, poses, setting, text visible in the image — rather than repeating the narrative context already in the figcaption |

### Rules for writing figcaptions

The figcaption and the alt text serve different roles. The figcaption is read by everyone and has no word limit — use it to carry context, interpretation, and purpose that go beyond what is visible in the image.

| Rule | Notes |
|---|---|
| **State why the image is here** | Explain what the image illustrates in relation to the module's argument — do not just describe what is visible |
| **Include source and credit** | Publication title, author, date, page number, or URL; photographer or scan credit |
| **No word limit** | The figcaption can be as long as needed to give the image full context |
| **Do not repeat the alt text** | The alt text describes the scene; the figcaption interprets and contextualizes it |

### Common issues flagged in review

| Issue | What it means |
|---|---|
| **Too long** | Alt text exceeds 120 characters — shorten it |
| **Duplicates caption** | Alt text repeats or paraphrases the figcaption — write a distinct visual description instead, or use `alt=""` if the figcaption fully covers it |
| **Missing context** | Alt text describes the image but not its significance — add relevant context |
| **Same captions** | Two images share identical alt text — each image needs a distinct description |
| **Parentheses** | Alt text contains parentheses — rewrite as a plain sentence |
| **Incomplete** | Alt text is a fragment — write a complete sentence or phrase |
| **Source info in alt text** | Credits or publication details are in the alt text — move them to the figcaption |

---

## Part 1 — Writing Alt Text for New Images

### Step 1 — Look at the image carefully

Ask yourself:
- Who or what is in the image?
- What is happening?
- What details are important for understanding this module?
- Is there any text visible in the image?

### Step 2 — Use Claude Code to draft alt text and figcaption together

You can provide the image in two ways — choose whichever is easiest:

**Option A — paste the image URL**

If the image is already on the CTC website or on Cloudflare R2, paste the link and tell Claude which figure it is:

```
Please draft both the alt text and the figcaption for this image on the CTC website.

Image URL: [paste the full image URL here]
Page it appears on: [e.g. https://ctc2026.github.io/ctc-jekyll/plays/guan-hanqing/]
Figure number: [e.g. Fig. 1]
Source: [publication title, author, year, page — or "Wikimedia Commons"]
Credit: [e.g. "Scan by author" or photographer name, if any]
Why it matters for this module: [one sentence on its relevance to the content]

Rules to follow:
- Alt text: 25 words or fewer, no source or credit info, no parentheses,
  do not duplicate the figcaption, describe what is visible and why it matters
- If the figcaption already fully describes the image, use alt=""
- Figcaption: include figure number, full description, source, and credit;
  avoid parentheses — rewrite as plain sentences instead
- Do not put source or credit info in the alt text

Please give me one draft of each, ready to paste into the .md file.
```

---

**Option B — upload the image directly**

If the image is on your computer and not yet on the website, attach it to your message in Claude Code and use this prompt:

```
I have attached an image for the CTC website. Please draft both the alt text 
and the figcaption for it.

Figure number: [e.g. Fig. 1]
Source: [publication title, author, year, page — or "Wikimedia Commons"]
Credit: [e.g. "Scan by author" or photographer name, if any]
Why it matters for this module: [one sentence on its relevance to the content]

Rules to follow:
- Alt text: 25 words or fewer, no source or credit info, no parentheses,
  do not duplicate the figcaption, describe what is visible and why it matters
- If the figcaption already fully describes the image, use alt=""
- Figcaption: include figure number, full description, source, and credit;
  avoid parentheses — rewrite as plain sentences instead
- Do not put source or credit info in the alt text

Please give me one draft of each, ready to paste into the .md file.
```

### Step 3 — Review and edit the draft

Read the output and check:
- Alt text is 25 words or fewer and does not repeat the figcaption
- Figcaption contains all source and credit information
- Neither contains parentheses
- Chinese names and titles are wrapped in `<span lang="zh">...</span>`

Adjust the wording as needed before adding it to the file.

---

## Part 2 — Adding Alt Text to the Website Code

### Option A — When adding a new image (via Claude Code)

When you ask Claude Code to add an image to a page (as described in HOW_TO.md Sections 6 and 7), include the alt text in your prompt:

```
In plays/mulan/1956-opera-film.md, after the Introduction heading, 
add this image:

File: Mulan_1956_OperaFilm_1.jpg
Alt text: Actress playing Hua Mulan in traditional opera costume, 
          holding a spear, 1956 Yue opera film
Caption: Fig. 1. The actress in the role of Hua Mulan.
Position: float right
```

### Option B — When updating alt text on an existing image

Ask Claude Code to find and update the alt text:

```
In plays/mulan/1939-film.md, find the image Mulan_1939_Film_1.jpg 
and update its alt text to:
"Chen Yunshang as Hua Mulan in the 1939 film, dressed in Tang dynasty military costume"
```

### Option C — Check and fix all alt text on a page

```
Read plays/mudanting/1986-opera-film.md and list every image on the page. 
For each one, tell me:
1. The current alt text
2. Whether it is adequate or needs improvement
3. A suggested improvement if needed

Then make all the changes.
```

---

## Part 3 — What the Code Looks Like

When alt text is correctly added, the image code in the `.md` file looks like this:

```html
<figure class="module-figure-right">
  <img src="https://pub-41c640610b8146e0a2c6dc8915ac1f9d.r2.dev/assets/plays/mulan/1956-opera-film/Mulan_1956_OperaFilm_1.jpg" 
       alt="Actress playing Hua Mulan in traditional opera costume, holding a spear, 1956 Yue opera film">
  <figcaption><strong>Fig. 1.</strong> The actress in the role of Hua Mulan.</figcaption>
</figure>
```

Key points:
- The `alt="..."` attribute goes inside the `<img>` tag
- The alt text and the caption serve different purposes — do not copy one from the other
- Never leave `alt` completely missing from the tag — use `alt=""` for decorative images

---

## Part 4 — Running an Alt Text Check Before Publishing

Before publishing any new or updated page, run an accessibility check to catch missing or poor alt text. See **HOW_TO.md, Section 8** for the full accessibility check process.

You can also ask Claude Code to do a quick check:

```
Read plays/xixiangji/1965-opera-film.md and check every image tag.
List any images where the alt text is blank, too short, or just a filename.
Suggest better alt text for each one.
```

---

## Need Help?

Contact the project manager if you get stuck at any step.

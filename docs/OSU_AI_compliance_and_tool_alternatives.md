# CTC Tools: OSU Compliance, Rationale, Alternatives, and Migration Plan

This document records (1) why each tool in the CTC workflow is used and what could
substitute for it, and (2) a migration note for moving our AI tools onto OSU-approved
channels. Reference: [OSU Approved AI Tools](https://ai.osu.edu/resources-buckeyes/approved-ai-tools).

OSU approval legend: ✅ approved (OSU-contracted) · ⚠️ product/use is conditional or
out-of-channel · ❌ not on the approved list · — not an AI tool (policy doesn't apply).

---

## Part 1 — Why Each Tool Is Used + Substitutes

### AI tools

#### Claude Code (Anthropic)
**Why use it**
- Lets non-coders edit a code-based static site in plain English — central to this
  project, since contributors are theater/literature scholars, not developers.
- Reads the whole project context (file structure, existing pages) so it can match
  house style and run terminal commands (wrangler uploads, Jekyll setup) on the user's behalf.
- Handles the project's most repetitive, error-prone tasks: faithful `.docx`→Markdown
  conversion preserving italics/citations, VTT subtitle generation, alt-text drafting
  against a 120-char rule.
- One tool spans setup, content authoring, accessibility, and media upload.

**Substitutes**

| Substitute | Trade-off |
|---|---|
| **GitHub Copilot** (in VS Code) | Strong code completion, weaker at long-form document conversion and multi-step terminal workflows. ⚠️ Not on OSU list. |
| **Cursor / Windsurf** | Similar agentic editing; ⚠️ not OSU-approved, same personal-account problem. |
| **Microsoft 365 Copilot** | ✅ OSU-approved (S4). Good for drafting prose, but **cannot edit the repo or run commands** — loses the automation. |
| **Manual editing** (no AI) | Zero cost/compliance risk, but slow and raises formatting-error rate for non-coders. |

#### Google Gemini API
**Why use it**
- One of the few models that accepts **direct video input**, exactly what sound-label
  and audio-description generation needs (timestamps from the actual footage).
- Native Chinese + English handling fits the bilingual subtitle workflow.
- Generous free tier and low per-call cost keep accessibility work nearly free.

**Substitutes**

| Substitute | Trade-off |
|---|---|
| **OpenAI GPT-4o (vision/video frames)** | Comparable quality; ⚠️ same personal-key compliance gap, slightly higher cost. |
| **Claude (Bedrock)** | Good vision; ✅ Bedrock path is OSU-approved, but less mature video ingestion than Gemini. |
| **OSU Vertex AI Gemini** | ✅ **Same model, approved channel** — the recommended swap. |
| **Manual labeling** | Free, fully accurate, but labor-intensive per clip. |

#### OpenAI API (TTS)
**Why use it**
- High-quality, natural neural voices suitable for audio descriptions read aloud to
  blind users — pacing matters at ~2.2 words/sec.
- Per-cue MP3 output fits the project's existing `cue_01.mp3` file convention.
- Cheap (<$1/clip) and scriptable.

**Substitutes**

| Substitute | Trade-off |
|---|---|
| **Azure OpenAI TTS (via OSU)** | ✅ **Same voices, OSU-approved channel** — recommended swap. |
| **Google Cloud / ElevenLabs TTS** | ElevenLabs more natural but pricier; ⚠️ neither on OSU list (Google TTS via Vertex would be). |
| **Amazon Polly (via OSU AWS)** | ✅ Approved channel; voices slightly less natural. |
| **macOS/Windows built-in TTS** | Free, offline, no compliance issue; robotic quality. |

#### Topaz Video AI
**Why use it**
- Purpose-built for the project's hardest footage: 1950s–60s opera films, VHS,
  degraded transfers (Artemis/Proteus/Nyx models target grain, noise, low resolution).
- Stackable enhancement passes and per-source presets give fine control older clips need.
- One-time license — no recurring cost.

**Substitutes**

| Substitute | Trade-off |
|---|---|
| **FFmpeg + Real-ESRGAN** | Free, open-source, scriptable; ⚠️ steep learning curve, no GUI/preview. |
| **DaVinci Resolve (Super Scale)** | Free tier exists; less specialized for heavy restoration. |
| **Adobe Premiere / After Effects** | ✅ Adobe is OSU-approved; upscaling weaker than Topaz's dedicated models. |
| **No upscaling** | Free; clearly worse viewing quality for old films. |

### Supporting infrastructure

| Tool | Why it's used | Substitutes |
|---|---|---|
| **Microsoft Teams** | OSU-licensed; shared Source/Processed media storage, accessibility checklists, channel collaboration. | Google Drive (✅ OSU-approved), OneDrive/SharePoint (✅ same M365 license), Dropbox (⚠️ not OSU-standard). |
| **GitHub** | Industry-standard version control; free public repo; integrates with VS Code + Reclaim; full edit history. | GitLab, Bitbucket, OSU institutional GitHub Enterprise. |
| **Cloudflare R2** | **Zero egress fees** (decisive for heavy video); cheap storage; works with Wrangler; public bucket URLs serve the site. | Backblaze B2, AWS S3 (✅ OSU AWS, but egress costs), GitHub LFS (quota-limited). |
| **Reclaim Hosting** | Built for academic/DH projects; affordable; manager-controlled publishing. | GitHub Pages (free, natural Jekyll fit), Netlify/Cloudflare Pages, OSU web hosting. |
| **VS Code** | Free; Mac/Windows parity; built-in terminal; hosts Claude Code + Python extensions. | Cursor (⚠️ not OSU-approved), Sublime/Atom, editor + separate terminal. |
| **Ruby / Jekyll / Bundler** | Mature static-site generator; native on GitHub Pages; fast, secure, database-free. | Hugo, Eleventy, Astro (all require a rebuild). |
| **Python** | De facto language for the AI/media scripts; rich libraries; readable for non-specialists. | Node.js, shell scripts (limited for API work). |
| **Node.js / Wrangler** | Cloudflare's official CLI — required for authenticated R2 uploads with correct content-types and `--remote`. | Cloudflare dashboard upload, `rclone` / `aws s3` CLI against R2. |
| **Arctime Pro** | Purpose-built subtitle timestamping with waveform alignment; exports WebVTT directly. | Subtitle Edit (free), Aegisub (free), Whisper for a first-pass transcript. |

**Pattern across the AI substitutes:** the highest-value swap isn't a *different product* —
it's the **same model through OSU's approved channel** (Claude→Bedrock, Gemini→Vertex,
OpenAI→Azure). Identical quality, fixes compliance, often shifts cost off the project.

---

## Part 2 — Migration Note for the Project Manager

**Re: Moving our AI tools onto OSU-approved channels**

**Why this matters:** We currently run Claude, Gemini, and OpenAI through personal
accounts and API keys. OSU's Approved AI Tools policy approves all three models — but
**only through OSU's contracted cloud channels**, not personal keys. Migrating keeps the
same tools and quality, fixes the compliance gap, and likely shifts cost off the project
onto OSU cloud accounts. Our content is public scholarly material (low sensitivity), so
this is about the *account channel*, not the data.

**The migrations — in priority order:**

1. **Gemini → OSU Google Cloud (Vertex AI)**
   - Request access to OSU's Google Cloud Platform / Vertex AI through OCIO.
   - Swap the scripts (`generate_sound_labels.py`, `generate_audio_desc.py`) from the
     `google-genai` AI Studio key to the **Vertex AI endpoint** (project ID + region +
     service-account auth instead of `GEMINI_API_KEY`).
   - Same Gemini models, same video-input capability.

2. **OpenAI → OSU Azure (Azure OpenAI Service)**
   - Request an Azure OpenAI deployment via OSU Azure.
   - Update `audiodesc_to_tts.py` to call the **Azure OpenAI endpoint** (deployment name
     + `AZURE_OPENAI_ENDPOINT`/key) instead of `platform.openai.com`.
   - Confirm a TTS voice model is enabled on the deployment; voices are equivalent.

3. **Claude → OSU AWS (Amazon Bedrock)**
   - Request Bedrock access through the OSU AWS agreement and enable the latest Claude model.
   - For scripted use, point the Anthropic SDK at Bedrock (AWS credentials + region).
   - Note: the **Claude Code VS Code extension** is what contributors use interactively —
     confirm with OCIO whether Bedrock-backed Claude Code is acceptable, or whether
     contributors should use M365 Copilot (already approved) for prose drafting while
     reserving repo automation for a sanctioned setup.

4. **Topaz Video AI** — not on the approved list at all. Lower urgency (no data sent to a
   hosted model), but flag it to OCIO; if disallowed, the fallback is Adobe (OSU-approved)
   or open-source Real-ESRGAN.

**What I need from you:**
- Approval to open the OCIO/OSU cloud access requests (AWS Bedrock, Azure OpenAI, Vertex AI).
- Confirmation of which department/grant account these should bill to.
- A decision on the Claude Code question above.

Once access is granted, the script changes are small — mostly swapping endpoints and
credentials, no logic changes. New credentials go in the project's secrets file (never committed).

**To verify before acting:**
- **Exact OCIO request process** — confirm OSU's actual intake form/path.
- **Bedrock + Claude Code** — whether the extension can be pointed at Bedrock is the one
  genuinely open question; confirm rather than assume.

---

## Part 3 — Estimated Monthly Budget (All Tools Combined)

Usage-dependent estimates — actual cost varies with how many pages/clips are processed
and which subscription tiers are chosen. Recurring monthly costs are separated from
one-time license purchases. Where an OSU institutional account is used, the cost may be
**$0 to the project** (billed centrally or to a grant).

### Recurring monthly costs

| Tool | Cost basis | Est. monthly (typical) | Notes / assumptions |
|---|---|---|---|
| **Claude Code** (Anthropic) | Subscription | **$20–100** | Claude Pro $20/mo for light editing; heavy use → Max $100/mo. *Via OSU AWS Bedrock = pay-per-token instead.* |
| **Google Gemini API** | Pay-as-you-go | **$2–5** | Cheap Flash models + video upload; free tier available. *Via OSU Vertex AI = likely $0 to project.* |
| **OpenAI API** (TTS) | Pay-as-you-go | **$2–5** | "<$1 per clip"; a few clips/month. *Via OSU Azure OpenAI = likely $0 to project.* |
| **Cloudflare R2** | Storage + ops | **$0–2** | First 10 GB storage free; egress free. A few dozen GB → ~$0.30–1/mo. |
| **Reclaim Hosting** | Hosting plan | **$3–15** | Personal plan ~$30/yr (~$2.50/mo); institutional plans more. |
| **Microsoft Teams / M365** | OSU license | **$0** | Provided by OSU institutional license. |
| **GitHub** (CTC2026 org) | Free tier | **$0** | Public repo; no Copilot in use. |
| **VS Code, Ruby/Jekyll, Python, Node/Wrangler** | Open source | **$0** | All free. |
| **Recurring subtotal** | | **≈ $27–127/mo** | Typical realistic case ≈ **$30/mo** (Claude Pro + light API use). |

### One-time / license purchases (not monthly)

| Tool | Cost basis | One-time cost | Notes |
|---|---|---|---|
| **Topaz Video AI** | Perpetual license | **~$299** | Includes 1 yr of updates; renewals optional. Amortizes to ~$25/mo over a year. |
| **Arctime Pro** | License | **Free–one-time** | A free version exists; "Pro" features are a paid license. Confirm which the team uses. |

### Bottom line

- **Typical recurring spend: ~$30/month** (Claude Pro $20 + Gemini ~$3 + OpenAI ~$3 + R2 ~$1 + Reclaim ~$3).
- **Upper end: ~$125/month** if running Claude Max ($100) and processing many clips.
- **Plus a one-time ~$300** for Topaz (and possibly Arctime Pro).
- **OSU-channel routing cuts cost:** moving Claude (Bedrock), Gemini (Vertex), and OpenAI
  (Azure) onto OSU cloud accounts may push direct project spend toward **~$5/month**
  (just Reclaim + R2), with AI usage billed centrally or to a grant.

> These are estimates, not quotes. The biggest swing factors are the Claude tier and clip
> volume. A per-clip / per-module cost model can tighten these into real forecasts once
> production volume is known.

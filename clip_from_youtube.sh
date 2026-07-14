#!/bin/bash
# Download a time-segment from YouTube, transcode to a web-friendly clip,
# and upload it to Cloudflare R2 (ctc-media bucket) at the given key.
#
# Requires: yt-dlp, ffmpeg, wrangler.  Export CLOUDFLARE_API_TOKEN first (for upload).
#
# Example:
#   export CLOUDFLARE_API_TOKEN=...            # only needed for the upload step
#   ./clip_from_youtube.sh \
#     --url   "https://youtu.be/XXXXXXXX" \
#     --start 00:03:10 --end 00:04:25 \
#     --key   assets/plays/mulan/1956-opera-film/Mulan_1956_OperaFilm_Clip_5.mp4
#
# Options:
#   --url URL          YouTube (or other yt-dlp-supported) video URL   [required]
#   --start HH:MM:SS    segment start                                  [required]
#   --end   HH:MM:SS    segment end                                    [required]
#   --key PATH          R2 key = local path under project, ends .mp4   [required]
#   --height N          cap resolution (default 1080)
#   --crop W:H:X:Y      crop the picture (e.g. remove black bars/watermark)
#   --webm             also produce + upload a .webm (VP9) alongside the mp4
#   --no-upload        stop after making the local file (skip R2)
#
set -euo pipefail

BUCKET="ctc-media"
CDN="https://pub-41c640610b8146e0a2c6dc8915ac1f9d.r2.dev"
PROJ="/Users/sophiali/Downloads/ctc-jekyll"
OUTDIR="$PROJ/clips_out"          # local working copies (NOT committed to git)
PROV="$PROJ/video_sources.tsv"    # provenance log: keep every clip's original URL

HEIGHT=1080
CROP=""
WEBM=0
UPLOAD=1
URL="" START="" END="" KEY=""

while [ $# -gt 0 ]; do
  case "$1" in
    --url)    URL="$2";    shift 2 ;;
    --start)  START="$2";  shift 2 ;;
    --end)    END="$2";    shift 2 ;;
    --key)    KEY="$2";    shift 2 ;;
    --height) HEIGHT="$2"; shift 2 ;;
    --crop)   CROP="$2";   shift 2 ;;
    --webm)   WEBM=1;      shift ;;
    --no-upload) UPLOAD=0; shift ;;
    *) echo "Unknown option: $1" >&2; exit 2 ;;
  esac
done

for v in URL START END KEY; do
  [ -n "${!v}" ] || { echo "ERROR: --${v,,} is required" >&2; exit 2; }
done
case "$KEY" in *.mp4) ;; *) echo "ERROR: --key must end in .mp4" >&2; exit 2 ;; esac

mkdir -p "$OUTDIR"
NAME="$(basename "$KEY" .mp4)"
RAW="$OUTDIR/${NAME}.src.mp4"     # the downloaded segment, before transcode
MP4="$OUTDIR/${NAME}.mp4"         # final web-ready mp4

# ---- video filter: cap height (even dims) + optional crop -------------------
VF="scale=-2:'min(${HEIGHT},ih)'"
[ -n "$CROP" ] && VF="crop=${CROP},${VF}"

echo "==> 1/3  Downloading segment ${START}–${END}"
# Always re-fetch: yt-dlp skips the download if the file exists, which would
# silently reuse a stale segment when --start/--end change between runs.
rm -f "$RAW"
yt-dlp --force-overwrites \
  --download-sections "*${START}-${END}" --force-keyframes-at-cuts \
  -f "bestvideo[height<=${HEIGHT}]+bestaudio/best[height<=${HEIGHT}]/best" \
  --merge-output-format mp4 \
  -o "$RAW" "$URL"

echo "==> 2/3  Transcoding to web-ready mp4 (H.264/AAC, faststart)"
ffmpeg -y -i "$RAW" \
  -vf "$VF" \
  -c:v libx264 -profile:v high -pix_fmt yuv420p -crf 20 -preset slow \
  -c:a aac -b:a 160k -movflags +faststart \
  "$MP4"

if [ "$WEBM" = 1 ]; then
  WEBMF="$OUTDIR/${NAME}.webm"
  echo "==> 2b   Also making .webm (VP9/Opus)"
  ffmpeg -y -i "$RAW" -vf "$VF" \
    -c:v libvpx-vp9 -b:v 0 -crf 32 -row-mt 1 \
    -c:a libopus -b:a 128k "$WEBMF"
fi

echo "==> 3/3  Upload"
if [ "$UPLOAD" = 0 ]; then
  echo "  (skipped --no-upload)  local file: $MP4"
  exit 0
fi

put() {  # $1 local file, $2 r2 key, $3 content-type
  echo "  → $2"
  wrangler r2 object put "$BUCKET/$2" --file "$1" --content-type "$3" --remote \
    2>&1 | grep -E "ERROR|complete|✘|Upload" || true
}
put "$MP4" "$KEY" "video/mp4"
[ "$WEBM" = 1 ] && put "$OUTDIR/${NAME}.webm" "${KEY%.mp4}.webm" "video/webm"

# record where this clip came from (append-only provenance log)
[ -f "$PROV" ] || printf "key\tsource_url\tsegment\n" > "$PROV"
printf "%s\t%s\t%s-%s\n" "$KEY" "$URL" "$START" "$END" >> "$PROV"

echo ""
echo "Done. Live at:"
echo "  $CDN/$KEY"
[ "$WEBM" = 1 ] && echo "  $CDN/${KEY%.mp4}.webm"
echo "Source logged in: $PROV"

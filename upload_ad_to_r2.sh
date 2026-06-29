#!/bin/bash
# Upload audio-description MP3s to Cloudflare R2 (ctc-media bucket).
# Run in a terminal where CLOUDFLARE_API_TOKEN is already exported.
#
# Local  : assets/subtitles/<play>/<module>/clip_N/audio_desc/cue_NN.mp3
# R2 key : <play>/<module>/audiodesc_clipN/cue_NN.mp3   (matches data-ad-mp3-base)

BUCKET="ctc-media"
BASE="/Users/sophiali/Downloads/ctc-jekyll/assets/subtitles/guan-hanqing/feiyimeng-1964-opera-film"
R2="guan-hanqing/feiyimeng-1964-opera-film"

put() {  # $1 local file, $2 r2 key
  echo "  → $2"
  wrangler r2 object put "$BUCKET/$2" --file "$1" --content-type "audio/mpeg" --remote \
    2>&1 | grep -E "ERROR|complete|✘|Upload" || true
}
del() {  # $1 r2 key (orphan cleanup; ok if it doesn't exist)
  echo "  ✗ $1"
  wrangler r2 object delete "$BUCKET/$1" --remote 2>&1 | grep -E "ERROR|complete|✘|Delete" || true
}

echo "clip 3 (7 cues):"
for n in 01 02 03 04 05 06 07; do
  put "$BASE/clip_3/audio_desc/cue_${n}.mp3" "$R2/audiodesc_clip3/cue_${n}.mp3"
done
del "$R2/audiodesc_clip3/cue_08.mp3"      # orphan from old 8-cue version

echo "clip 4 (10 cues):"
for n in 01 02 03 04 05 06 07 08 09 10; do
  put "$BASE/clip_4/audio_desc/cue_${n}.mp3" "$R2/audiodesc_clip4/cue_${n}.mp3"
done
for n in 11 12 13; do del "$R2/audiodesc_clip4/cue_${n}.mp3"; done   # orphans from old versions

echo "Done."

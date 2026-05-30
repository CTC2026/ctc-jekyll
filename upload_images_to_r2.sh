#!/bin/bash
# Upload all site images to Cloudflare R2 (ctc-media bucket)
# Run this in a terminal where CLOUDFLARE_API_TOKEN is already exported.

BUCKET="ctc-media"
BASE="/Users/sophiali/Downloads/ctc-jekyll"
CDN="https://pub-41c640610b8146e0a2c6dc8915ac1f9d.r2.dev"

echo "Uploading images to R2 bucket: $BUCKET"
echo ""

find "$BASE/assets" -type f \( \
  -name "*.jpg" -o -name "*.jpeg" -o \
  -name "*.png" -o -name "*.gif"  -o -name "*.webp" \
\) | while read -r filepath; do
  relpath="${filepath#$BASE/}"

  case "${filepath##*.}" in
    jpg|jpeg) ctype="image/jpeg" ;;
    png)      ctype="image/png" ;;
    gif)      ctype="image/gif" ;;
    webp)     ctype="image/webp" ;;
    *)        ctype="application/octet-stream" ;;
  esac

  echo "  → $relpath"
  wrangler r2 object put "$BUCKET/$relpath" \
    --file "$filepath" \
    --content-type "$ctype" \
    --remote 2>&1 | grep -E "ERROR|complete|✘" || true
done

echo ""
echo "Done. Images are live at $CDN/assets/..."

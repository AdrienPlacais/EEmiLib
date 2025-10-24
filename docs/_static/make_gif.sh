#!/usr/bin/env bash
# Convert an MP4 video into an optimized GIF for GitHub README usage
# Optional cropping: ./make_gif.sh input.mp4 output.gif 640 360 100 50

# ./make_gif.sh animation.mp4 animation.gif 650 890 20 50
set -euo pipefail

if [[ $# -lt 1 ]]; then
  echo "Usage: $0 <input_video> [output_gif] [crop_w crop_h x y]"
  exit 1
fi

INPUT="$1"
BASENAME="${INPUT%.*}"
OUTPUT="${2:-${BASENAME}.gif}"
PALETTE="${BASENAME}_palette.png"
FPS=2
WIDTH=350

# Optional cropping
if [[ $# -ge 5 ]]; then
  CROP="crop=${3}:${4}:${5}:${6},"
  echo "✂️  Cropping to ${3}x${4} from (${5},${6})"
else
  CROP=""
fi

echo "🎬 Generating palette..."
ffmpeg -y -i "$INPUT" -vf "${CROP}fps=$FPS,scale=$WIDTH:-1:flags=lanczos,palettegen=max_colors=64" "$PALETTE"

echo "🎨 Creating GIF..."
ffmpeg -y -i "$INPUT" -i "$PALETTE" \
  -filter_complex "${CROP}fps=$FPS,scale=$WIDTH:-1:flags=lanczos[x];[x][1:v]paletteuse" \
  -loop 0 "$OUTPUT"

if command -v gifsicle >/dev/null 2>&1; then
  echo "💡 Optimizing with gifsicle..."
  gifsicle --delay=10 -O3 "$OUTPUT" -o "$OUTPUT"
fi

echo "✅ Done! Output: $OUTPUT"

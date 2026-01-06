# handbrake-metadata-recovery

Filename rule:
  video.mp4
  video_handbrake.mp4

What it does:
1) Restore metadata
   Copy metadata from original -> handbrake file
   (date, gps, camera stuff if mp4 allows)

2) Isolate missing
   Move originals without handbrake output to:
   not-hanbraked/

3) Isolate present
   Move originals with handbrake output to:
   handbraked/

Requirements:
- Python 3
- exiftool

Install exiftool (macOS):
  brew install exiftool

Run:
  python tool.py /path/to/videos

Pick a number. Done.

Notes:
- No re-encode
- Originals untouched
- Matching is strict:
  filename.mp4 <-> filename_handbrake.mp4

**Note:** This project was made with help from AI. Its mainly for my private use, but feel free to use it if you find it useful. No guarantees though.

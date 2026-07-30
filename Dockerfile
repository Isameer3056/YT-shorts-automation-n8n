# n8n's official image (v2.x+) is a minimal/distroless-style base with no
# package manager (no apt, no apk). Rather than trying to install ffmpeg,
# we copy in an already-compiled static binary via a multi-stage COPY.
FROM n8nio/n8n:latest

COPY --from=mwader/static-ffmpeg:8.1 /ffmpeg /usr/local/bin/ffmpeg
COPY --from=mwader/static-ffmpeg:8.1 /ffprobe /usr/local/bin/ffprobe

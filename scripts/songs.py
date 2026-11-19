"""Build the "Favorite songs" cards from Spotify track IDs.

Run locally when the song list changes:  python scripts/songs.py
Covers are embedded as base64 because GitHub blocks external images inside SVGs.
"""
import base64
import re
import urllib.request
from html import escape, unescape
from pathlib import Path

TRACKS = [
    "1BLOVHYYlH4JUHQGcpt75R",
    "269XSeQhDrWEotMALJaACW",
    "3Eb5sztvEMa0Mqnb8DUAlU",
]
OUT = Path(__file__).resolve().parent.parent / "assets" / "songs"
FONT = "-apple-system,'Segoe UI',Helvetica,Arial,sans-serif"
WIDTH = 440


def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req) as r:
        return r.read()


def track_info(track_id):
    html = fetch(f"https://open.spotify.com/track/{track_id}").decode("utf-8")
    meta = dict(re.findall(r'<meta property="og:(\w+)" content="([^"]*)"', html))
    artist = unescape(meta["description"]).split(" · ")[0]
    # 300px cover instead of 640px keeps the SVG small
    cover = fetch(meta["image"].replace("ab67616d0000b273", "ab67616d00001e02"))
    return unescape(meta["title"]), artist, base64.b64encode(cover).decode()


def header_svg():
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="44" viewBox="0 0 {WIDTH} 44">
<style>.t{{font:600 14px {FONT};fill:#58a6ff}}.s{{font:12px {FONT};fill:#8b949e}}</style>
<circle cx="10" cy="12" r="7" fill="none" stroke="#8b949e" stroke-width="1.5"/>
<path d="M8 8.8 L13 12 L8 15.2 Z" fill="#8b949e"/>
<text x="26" y="17" class="t">Favorite songs</text>
<path d="M4 30a8 8 0 0 1 8 8M4 34.5a3.5 3.5 0 0 1 3.5 3.5" fill="none" stroke="#8b949e" stroke-width="1.5" stroke-linecap="round"/>
<circle cx="4.6" cy="37.4" r="1" fill="#8b949e"/>
<text x="26" y="38" class="s">From Spotify</text>
</svg>"""


def song_svg(title, artist, cover_b64):
    return f"""<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="{WIDTH}" height="40" viewBox="0 0 {WIDTH} 40">
<style>.n{{font:600 12px {FONT};fill:#8b949e}}.a{{font:10px {FONT};fill:#8b949e;opacity:.8}}</style>
<clipPath id="r"><rect x="26" y="4" width="32" height="32" rx="5"/></clipPath>
<image x="26" y="4" width="32" height="32" clip-path="url(#r)" xlink:href="data:image/jpeg;base64,{cover_b64}"/>
<text x="68" y="18" class="n">{escape(title)}</text>
<text x="68" y="32" class="a">{escape(artist)}</text>
</svg>"""


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "header.svg").write_text(header_svg(), encoding="utf-8")
    for i, track_id in enumerate(TRACKS, 1):
        title, artist, cover = track_info(track_id)
        (OUT / f"{i}.svg").write_text(song_svg(title, artist, cover), encoding="utf-8")
        print(i, title, "-", artist)

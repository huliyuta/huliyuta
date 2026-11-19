"""Generate metrics.languages.svg from the user's public, non-fork repositories.

Runs in GitHub Actions with the built-in GITHUB_TOKEN (no personal token needed).
"""
import json
import os
import sys
import urllib.request
from html import escape

USER = os.environ.get("PROFILE_USER", "huliyuta")
TOKEN = os.environ.get("GITHUB_TOKEN", "")
OUT = sys.argv[1] if len(sys.argv) > 1 else "metrics.languages.svg"
LIMIT = 6
IGNORED = {s.strip().lower() for s in os.environ.get("IGNORED_LANGUAGES", "").split(",") if s.strip()}

COLORS = {
    "Python": "#3572A5", "JavaScript": "#f1e05a", "TypeScript": "#3178c6", "HTML": "#e34c26",
    "CSS": "#663399", "SCSS": "#c6538c", "Jupyter Notebook": "#DA5B0B", "Rust": "#dea584",
    "Java": "#b07219", "C": "#555555", "C++": "#f34b7d", "C#": "#178600", "Go": "#00ADD8",
    "Shell": "#89e051", "PowerShell": "#012456", "PLpgSQL": "#336790", "TSQL": "#e38c00",
    "Vue": "#41b883", "Dockerfile": "#384d54", "R": "#198CE7", "Kotlin": "#A97BFF",
    "PHP": "#4F5D95", "Ruby": "#701516", "Svelte": "#ff3e00", "Dart": "#00B4AB",
    "Batchfile": "#C1F12E", "Makefile": "#427819", "Lua": "#000080", "Astro": "#ff5a03",
}


def api(url):
    req = urllib.request.Request(url, headers={"Accept": "application/vnd.github+json"})
    if TOKEN:
        req.add_header("Authorization", f"Bearer {TOKEN}")
    with urllib.request.urlopen(req) as r:
        return json.load(r)


def collect():
    totals, page = {}, 1
    while True:
        repos = api(f"https://api.github.com/users/{USER}/repos?per_page=100&type=owner&page={page}")
        if not repos:
            break
        for repo in repos:
            if repo["fork"] or repo["archived"]:
                continue
            for lang, size in api(repo["languages_url"]).items():
                if lang.lower() not in IGNORED:
                    totals[lang] = totals.get(lang, 0) + size
        page += 1
    return totals


def human(n):
    for unit in ("B", "kB", "MB"):
        if n < 1000:
            return f"{n:.0f} {unit}" if unit == "B" else f"{n:.1f} {unit}"
        n /= 1000
    return f"{n:.1f} GB"


def render(totals):
    top = sorted(totals.items(), key=lambda kv: kv[1], reverse=True)[:LIMIT]
    total = sum(v for _, v in top) or 1
    width, bar_x, bar_w = 480, 20, 440
    rows = (len(top) + 1) // 2
    height = 70 + rows * 20 + 10

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        "<style>"
        ".t{font:600 14px -apple-system,'Segoe UI',Helvetica,Arial,sans-serif;fill:#58a6ff}"
        ".l{font:12px -apple-system,'Segoe UI',Helvetica,Arial,sans-serif;fill:#8b949e}"
        ".n{font:10px -apple-system,'Segoe UI',Helvetica,Arial,sans-serif;fill:#8b949e}"
        "</style>",
        f'<text x="{width / 2}" y="22" text-anchor="middle" class="t">Most used languages</text>',
        f'<clipPath id="c"><rect x="{bar_x}" y="34" width="{bar_w}" height="8" rx="4"/></clipPath>',
        '<g clip-path="url(#c)">',
    ]
    x = bar_x
    for lang, size in top:
        w = bar_w * size / total
        parts.append(f'<rect x="{x:.2f}" y="34" width="{w + 0.5:.2f}" height="8" fill="{COLORS.get(lang, "#8b949e")}"/>')
        x += w
    parts.append("</g>")

    for i, (lang, size) in enumerate(top):
        col, row = i % 2, i // 2
        cx = bar_x + col * 225
        y = 66 + row * 20
        pct = 100 * size / total
        parts += [
            f'<circle cx="{cx + 6}" cy="{y - 4}" r="4.5" fill="{COLORS.get(lang, "#8b949e")}"/>',
            f'<text x="{cx + 18}" y="{y}" class="l">{escape(lang)}</text>',
            f'<text x="{cx + 160}" y="{y}" text-anchor="end" class="n">{human(size)}</text>',
            f'<text x="{cx + 210}" y="{y}" text-anchor="end" class="n">{pct:.2f}%</text>',
        ]
    parts.append("</svg>")
    return "\n".join(parts)


if __name__ == "__main__":
    data = collect()
    with open(OUT, "w", encoding="utf-8") as f:
        f.write(render(data))
    print(f"wrote {OUT}:", sorted(data.items(), key=lambda kv: -kv[1])[:LIMIT])

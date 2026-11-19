"""Regenerate assets/pulse.svg: language mix and latest pushes across public repos."""
import json
import os
import sys
import urllib.request
from datetime import datetime, timezone

USER = os.environ.get("GH_USER", "omar-mahmoud-java-developer")
COLORS = ["#58a6ff", "#a78bfa", "#f472b6", "#3fb950", "#f0883e", "#8b949e"]


def api(path):
    req = urllib.request.Request(f"https://api.github.com{path}")
    req.add_header("Accept", "application/vnd.github+json")
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        req.add_header("Authorization", f"Bearer {token}")
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.load(resp)


def esc(text):
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def build(repos, langs):
    total = sum(langs.values()) or 1
    top = sorted(langs.items(), key=lambda kv: -kv[1])[:5]
    rest = total - sum(b for _, b in top)
    if rest > 0:
        top.append(("Other", rest))
    out = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="900" height="250" viewBox="0 0 900 250" role="img" aria-label="Live GitHub pulse">',
        '<rect width="900" height="250" rx="16" fill="#0d1117"/>',
        '<g font-family="Segoe UI,Helvetica,Arial,sans-serif">',
        '<text x="30" y="38" font-size="16" font-weight="600" fill="#c9d1d9">Live pulse</text>',
        f'<text x="870" y="38" font-size="12" fill="#8b949e" text-anchor="end">auto-updated {datetime.now(timezone.utc):%Y-%m-%d} by GitHub Actions</text>',
    ]
    x = 30.0
    for i, (name, b) in enumerate(top):
        w = 840 * b / total
        out.append(f'<rect x="{x:.1f}" y="56" width="{w:.1f}" height="12" fill="{COLORS[i]}"><animate attributeName="opacity" values="0;1" dur="{0.4 + i * 0.2:.1f}s" fill="freeze"/></rect>')
        x += w
    for i, (name, b) in enumerate(top):
        cx = 30 + (i % 3) * 290
        cy = 94 + (i // 3) * 22
        out.append(f'<circle cx="{cx + 5}" cy="{cy - 4}" r="5" fill="{COLORS[i]}"/><text x="{cx + 16}" y="{cy}" font-size="13" fill="#c9d1d9">{esc(name)} {100 * b / total:.0f}%</text>')
    out.append('<text x="30" y="160" font-size="13" fill="#8b949e">Latest pushes</text>')
    for i, r in enumerate(repos[:3]):
        y = 184 + i * 22
        when = r["pushed_at"][:10]
        out.append(f'<text x="30" y="{y}" font-size="14" fill="#58a6ff">{esc(r["name"][:46])}</text><text x="870" y="{y}" font-size="13" fill="#8b949e" text-anchor="end">{when}</text>')
    out.append('</g></svg>')
    return "\n".join(out)


def main():
    repos = [r for r in api(f"/users/{USER}/repos?per_page=100&sort=pushed") if not r["fork"] and r["name"] != USER]
    langs = {}
    for r in repos:
        for lang, b in api(f"/repos/{USER}/{r['name']}/languages").items():
            langs[lang] = langs.get(lang, 0) + b
    path = os.path.join(os.path.dirname(__file__), "..", "assets", "pulse.svg")
    with open(path, "w", encoding="utf-8") as f:
        f.write(build(repos, langs))
    print("wrote", os.path.normpath(path))


if __name__ == "__main__":
    sys.exit(main())

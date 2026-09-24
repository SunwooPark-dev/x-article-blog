#!/usr/bin/env python3
"""Build the X-article canonical static blog. Regenerable: python3 build.py"""
import hashlib
import html
import os
import re

BASE = os.path.dirname(os.path.abspath(__file__))
FILES = os.path.expanduser("~/workspace/goals/neon-oracle-fortune-app/files")
SITE_URL = "https://x-article-blog-sunwoopark0512-4225s-projects.vercel.app"

ARTICLES = [
    {
        "slug": "write-50-posts-before-your-first-follower",
        "src": "X-아티클-초안-2026-09-19-50-posts.md",
        "title_line_prefix": "# Write 50 Posts",
        "title_occurrence": 0,  # first
        "date_label": "September 19, 2026",
        "status": "published",
        "image": "write-50-posts.webp",
        "blurb": "Your first 50 posts aren't for an audience \u2014 they\u2019re for you. Voice, detachment, proof, and editing instinct are excavated one post at a time.",
        "meta_desc": "Stop waiting for followers to start. Your first 50 posts aren\u2019t for an audience \u2014 they\u2019re for you. Voice, detachment from the scoreboard, a body of proof, and editing instincts are all earned through reps.",
    },
    {
        "slug": "the-7-round-rule",
        "src": "X-아티클-초안-2026-09-19-7-round-rule.md",
        "title_line_prefix": "# The 7-Round Rule",
        "title_occurrence": 0,
        "date_label": "September 19, 2026",
        "status": "draft",
        "image": "7-round-rule.webp",
        "blurb": "I red-team everything I build, but red-teaming has no natural stopping point. The 7-round rule: argue seven different ways, then freeze the design and go touch real data.",
        "meta_desc": "Red-teaming has a failure mode nobody warns you about: no natural stopping point. Seven rounds max, each attacking a different failure mode. Then freeze the design, write down the reversal condition, and go touch real data.",
    },
    {
        "slug": "daily-compounding",
        "src": "X-아티클-초안-2026-09-20-daily-compounding.md",
        "title_line_prefix": "# Daily Compounding",
        "title_occurrence": 1,  # second (after the DRAFT meta block)
        "date_label": "September 20, 2026",
        "status": "draft",
        "image": "daily-compounding.webp",
        "blurb": "Twenty minutes a day turned me from an AI consumer into a builder. Compounding isn\u2019t magic \u2014 it\u2019s attendance.",
        "meta_desc": "For my first year or two with AI tools, I was a world-class consumer. The shift came from a smaller decision: twenty minutes a day, touching the thing. Compounding only works if you deposit \u2014 every day, small amounts, boring amounts.",
    },
    {
        "slug": "content-needs-release-gates",
        "src": "x-article-release-gates/article.md",
        "src_kind": "release_gates",  # custom extractor (원고 section)
        "title_line_prefix": "# Content Needs Release Gates",
        "date_label": "September 23, 2026",
        "status": "published",
        "image": "00-hero-release-gates.webp",
        "no_hero_figure": True,  # hero placed inline via 👉 marker
        "blurb": "Stop publishing on vibes. Run your content like software releases: four gates between every idea and the public \u2014 stockpile, calibrate, deploy, and let the 14-day data decide.",
        "meta_desc": "Content needs release gates, not inspiration. Four gates between an idea and the public: stockpile 12 finished posts, calibrate like a stranger, automate Day 1, and let the 14-day verdict \u2014 keep, change, or kill \u2014 decide.",
    },
    {
        "slug": "dont-convince-the-customer-make-betrayal-impossible",
        "src": "x-article-betrayal-impossible/article.md",
        "title_line_prefix": "# Don't Convince the Customer.",
        "title_occurrence": 0,
        "date_label": "September 23, 2026",
        "status": "published",
        "image": "betrayal-impossible.webp",
        "blurb": "Stop optimizing the win-back email. Three mechanics of unbetrayable trust: tell the costly truth, keep one small promise daily, and let customers co-own the ritual.",
        "meta_desc": "Don't convince the customer \u2014 become the one they can't betray. Three mechanics of unbetrayable trust: costly truth, one small daily promise, co-owned rituals.",
    },
    {
        "slug": "your-ai-doesnt-need-more-context-it-needs-a-librarian",
        "src": "x-article-ai-librarian/article.md",
        "title_line_prefix": "# Your AI Doesn't Need More Context.",
        "title_occurrence": 0,
        "date_label": "September 23, 2026",
        "status": "published",
        "image": "ai-librarian.webp",
        "blurb": "Longer context didn't fix my AI's memory. What worked: summary notes, daily logs, per-person cards. Retrieval is curation, not storage.",
        "meta_desc": "Your AI doesn't need more context. It needs a librarian. Summary notes, daily logs, per-person cards \u2014 feed it less, curate what you keep.",
    },
]


def extract_body_release_gates(src_path):
    """Bank #24: body is the 원고 section of article.md — from its title
    line up to (not including) the '## 숏포스트 3개' section line.
    No byte is altered."""
    with open(src_path, "r", encoding="utf-8") as f:
        raw = f.read()
    lines = raw.split("\n")
    meta_idx = next(i for i, ln in enumerate(lines)
                    if ln.strip() == "## 원고 (영어 전문)")
    start = next(i for i in range(meta_idx, len(lines))
                 if lines[i].startswith("# Content Needs Release Gates"))
    end = next(i for i in range(start + 1, len(lines))
               if lines[i].strip().startswith("## 숏포스트 3개"))
    start_byte = sum(len(l) + 1 for l in lines[:start])
    end_byte = sum(len(l) + 1 for l in lines[:end])
    return raw[start_byte:end_byte]


IMG_MARKER = re.compile(r"👉\s*\[여기에 이미지 첨부:\s*([^\]]+)\]")


def extract_body(src_path, title_prefix, occurrence):
    """Extract the English body verbatim: from the Nth title heading line
    up to (not including) the first subsequent line that is exactly '---'.
    No byte is altered."""
    with open(src_path, "r", encoding="utf-8") as f:
        raw = f.read()
    lines = raw.split("\n")
    hits = [i for i, ln in enumerate(lines) if ln.startswith(title_prefix)]
    start = hits[occurrence]
    end = next(i for i in range(start + 1, len(lines)) if lines[i] == "---")
    start_byte = sum(len(l) + 1 for l in lines[:start])
    end_byte = sum(len(l) + 1 for l in lines[:end])
    return raw[start_byte:end_byte]


def renderable_body(body):
    """Title line + leading '>' meta-quote blocks removed for page rendering.
    The raw body bytes are untouched (hash uses extract_body output)."""
    title_line = body.split("\n", 1)[0]
    rest = body.split("\n", 1)[1] if "\n" in body else ""
    blocks = re.split(r"\n\s*\n", rest)
    while blocks and all(
        ln.strip().startswith(">") for ln in blocks[0].split("\n") if ln.strip()
    ):
        blocks.pop(0)
    return title_line, "\n\n".join(blocks)


def inline_md(text):
    text = html.escape(text)
    text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)", r"<em>\1</em>", text)
    return text


def body_to_html(body, title=""):
    # Inline image markers (👉 [여기에 이미지 첨부: file]) become <figure> blocks.
    body = IMG_MARKER.sub(lambda m: f"\n\n@@FIG:{m.group(1).strip()}@@\n\n", body)
    blocks = re.split(r"\n\s*\n", body.strip("\n"))
    out = []
    i = 0
    while i < len(blocks):
        b = blocks[i].strip("\n")
        if not b:
            i += 1
            continue
        fig = re.fullmatch(r"@@FIG:(.+?)@@", b)
        if fig:
            fname = fig.group(1)
            out.append(f'<figure><img src="../images/{html.escape(fname)}"'
                       f' alt="{html.escape(title)}"></figure>')
        elif b.startswith("# "):
            pass  # title rendered separately
        elif b.startswith("## "):
            out.append(f"<h2>{inline_md(b[3:].strip())}</h2>")
        elif re.match(r"^(- |\* )", b):
            items = [inline_md(re.sub(r"^(- |\* )", "", ln).strip())
                     for ln in b.split("\n") if ln.strip()]
            out.append("<ul>" + "".join(f"<li>{it}</li>" for it in items) + "</ul>")
        elif re.match(r"^\d+\. ", b):
            items = [inline_md(re.sub(r"^\d+\. ", "", ln).strip())
                     for ln in b.split("\n") if ln.strip()]
            out.append("<ol>" + "".join(f"<li>{it}</li>" for it in items) + "</ol>")
        else:
            out.append(f"<p>{inline_md(' '.join(b.split()))}</p>")
        i += 1
    return "\n".join(out)


CSS = """
:root{
  --bg:#141210; --bg2:#1c1917; --ink:#ece7de; --muted:#a8a094;
  --blue:#3f8cff; --amber:#e8a33d; --line:#2c2823;
}
*{margin:0;padding:0;box-sizing:border-box}
html{-webkit-text-size-adjust:100%}
body{background:var(--bg);color:var(--ink);
  font-family:Georgia,'Times New Roman',Charter,serif;line-height:1.75;
  font-size:18px}
.wrap{max-width:700px;margin:0 auto;padding:0 24px}
header.site{border-bottom:1px solid var(--line);padding:28px 0}
header.site .brand{font-family:-apple-system,'Helvetica Neue',Arial,sans-serif;
  font-weight:800;letter-spacing:3px;font-size:14px;color:var(--ink);
  text-decoration:none}
header.site .brand .dot{display:inline-block;width:9px;height:9px;border-radius:50%;
  background:var(--amber);margin-right:10px}
header.site .tag{color:var(--muted);font-size:14px;margin-top:6px;
  font-family:-apple-system,'Helvetica Neue',Arial,sans-serif}
.hero{padding:56px 0 40px}
.hero h1{font-size:clamp(34px,6vw,52px);line-height:1.15;letter-spacing:-.5px}
.hero h1 .acc{color:var(--amber)}
.hero p{color:var(--muted);margin-top:14px;font-size:17px}
.post-card{display:block;text-decoration:none;color:inherit;border:1px solid var(--line);
  border-radius:14px;overflow:hidden;margin-bottom:28px;background:var(--bg2);
  transition:border-color .2s}
.post-card:hover{border-color:var(--blue)}
.post-card img{width:100%;height:220px;object-fit:cover;display:block}
.post-card .body{padding:22px 24px}
.post-card h2{font-size:24px;line-height:1.3;margin-bottom:8px}
.post-card h2 a{color:var(--ink);text-decoration:none}
.post-card .meta{font-family:-apple-system,'Helvetica Neue',Arial,sans-serif;
  font-size:12px;letter-spacing:2px;color:var(--amber);text-transform:uppercase;
  margin-bottom:10px}
.post-card p{color:var(--muted);font-size:16px}
article.post{padding:48px 0 64px}
article.post .meta{font-family:-apple-system,'Helvetica Neue',Arial,sans-serif;
  font-size:12px;letter-spacing:2px;color:var(--amber);text-transform:uppercase;
  margin-bottom:14px}
article.post h1{font-size:clamp(30px,5.5vw,44px);line-height:1.2;
  letter-spacing:-.5px;margin-bottom:8px}
article.post time{color:var(--muted);font-size:15px;
  font-family:-apple-system,'Helvetica Neue',Arial,sans-serif}
article.post figure{margin:28px 0}
article.post figure img{width:100%;border-radius:12px;display:block}
article.post h2{font-size:24px;margin:44px 0 12px;color:var(--ink)}
article.post p{margin:0 0 20px}
article.post ul,article.post ol{margin:0 0 20px 24px}
article.post li{margin-bottom:10px}
article.post strong{color:#fff}
article.post em{color:var(--blue)}
.back{display:inline-block;margin:32px 0 0;color:var(--blue);text-decoration:none;
  font-family:-apple-system,'Helvetica Neue',Arial,sans-serif;font-size:15px}
footer.site{border-top:1px solid var(--line);padding:32px 0;color:var(--muted);
  font-size:14px;font-family:-apple-system,'Helvetica Neue',Arial,sans-serif}
@media(max-width:560px){body{font-size:16px}.post-card img{height:170px}}
"""

BASE_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<meta name="description" content="{desc}">
<link rel="canonical" href="{canonical}">
<style>{css}</style>
</head>
<body>
<header class="site"><div class="wrap">
<a class="brand" href="/"><span class="dot"></span>SUNWOO PARK</a>
<div class="tag">Notes on building, in public.</div>
</div></header>
<div class="wrap">
{content}
</div>
<footer class="site"><div class="wrap">
&copy; 2026 Sunwoo Park. Also on <a href="https://x.com/sunwoopark" style="color:#3f8cff">X</a>.
</div></footer>
</body>
</html>
"""


def main():
    pages = []
    extracted = {}
    for a in ARTICLES:
        src = os.path.join(FILES, a["src"])
        if a.get("src_kind") == "release_gates":
            body = extract_body_release_gates(src)
        else:
            body = extract_body(src, a["title_line_prefix"], a["title_occurrence"])
        extracted[a["slug"]] = body
        title, render_body = renderable_body(body)
        title = title.lstrip("# ").strip()
        post_html = body_to_html(render_body, title)
        status_label = ("Published" if a["status"] == "published"
                        else "Draft \u2014 unpublished")
        hero_figure = "" if a.get("no_hero_figure") else (
            f'<figure><img src="../images/{a["image"]}"'
            f' alt="{html.escape(title)}"></figure>')
        content = f"""
<article class="post">
<div class="meta">{status_label}</div>
<h1>{html.escape(title)}</h1>
<time datetime="{a['date_label']}">{a['date_label']}</time>
{hero_figure}
{post_html}
<a class="back" href="/">&larr; All posts</a>
</article>"""
        page = BASE_HTML.format(title=f"{title} \u2014 Sunwoo Park",
                                desc=html.escape(a["meta_desc"]),
                                canonical=f"{SITE_URL}/posts/{a['slug']}",
                                css=CSS, content=content)
        out = os.path.join(BASE, "posts", f"{a['slug']}.html")
        with open(out, "w", encoding="utf-8") as f:
            f.write(page)
        pages.append(f"posts/{a['slug']}.html")

    cards = []
    for a in ARTICLES:
        title = extracted[a["slug"]].split("\n", 1)[0].lstrip("# ").strip()
        cards.append(f"""
<a class="post-card" href="/posts/{a['slug']}">
<img src="/images/{a['image']}" alt="{html.escape(title)}">
<div class="body">
<div class="meta">{a['date_label']}{' \u00b7 Draft' if a['status']=='draft' else ''}</div>
<h2>{html.escape(title)}</h2>
<p>{html.escape(a['blurb'])}</p>
</div></a>""")
    index_content = f"""
<div class="hero">
<h1>Building in public,<br><span class="acc">twenty minutes</span> at a time.</h1>
<p>Long-form notes behind the X threads \u2014 English essays on craft, systems, and showing up.</p>
</div>
{''.join(cards)}"""
    index = BASE_HTML.format(title="Sunwoo Park \u2014 Notes on building",
                             desc="Long-form essays behind the X threads: craft, systems, and showing up daily.",
                             canonical=SITE_URL,
                             css=CSS, content=index_content)
    with open(os.path.join(BASE, "index.html"), "w", encoding="utf-8") as f:
        f.write(index)

    with open(os.path.join(BASE, "vercel.json"), "w", encoding="utf-8") as f:
        f.write('{\n  "cleanUrls": true\n}\n')

    dc = extracted["daily-compounding"]
    sha = hashlib.sha256(dc.encode("utf-8")).hexdigest()
    rg = extracted["content-needs-release-gates"]
    rg_sha = hashlib.sha256(rg.encode("utf-8")).hexdigest()
    bi = extracted["dont-convince-the-customer-make-betrayal-impossible"]
    bi_sha = hashlib.sha256(bi.encode("utf-8")).hexdigest()
    with open(os.path.join(BASE, "BUILD_NOTES.md"), "w", encoding="utf-8") as f:
        f.write(f"""# Build notes
- Bodies extracted verbatim from the draft .md files (no byte altered).
  content-needs-release-gates: 원고 section of x-article-release-gates/article.md
  (title line to just before '## 숏포스트 3개').
- DRAFT meta blocks and short-post sections excluded from pages.
- canonical <link> auto-added per page: {SITE_URL}/posts/<slug> (index: {SITE_URL}).
- Image mapping: images/write-50-posts.webp / 7-round-rule.webp / daily-compounding.webp
  <- media-generation-x-article-2026-09-19-50-posts-*.webp,
     media-generation-x-article-2026-09-19-7-round-r-*.webp,
     media-generation-daily-compounding-cover-*.webp
- content-needs-release-gates images: 00-hero-release-gates.webp,
  01-gate-stockpile.webp, 02-gate-calibration.webp, 03-gate-day1.webp,
  04-gate-verdict.webp, 05-closing-pipeline.webp (inline at 👉 markers)
- daily-compounding body sha256: {sha}
  (bytes = from second '# Daily Compounding...' heading line start
   to just before the line that is exactly '---')
- content-needs-release-gates body sha256: {rg_sha}
  (bytes = from '# Content Needs Release Gates...' title line under
   '## 원고 (영어 전문)' to just before the line '## 숏포스트 3개')
- betrayal-impossible image: images/betrayal-impossible.webp
  <- x-article-betrayal-impossible/assets/media-generation-hero-knot-*.webp
- dont-convince-the-customer-make-betrayal-impossible body sha256: {bi_sha}
  (bytes = from '# Don't Convince the Customer...' title line
   to just before the line that is exactly '---')
""")
    print("PAGES:", pages)
    print("DAILY_COMPOUNDING_SHA256:", sha)
    print("RELEASE_GATES_SHA256:", rg_sha)
    print("BETRAYAL_SHA256:", bi_sha)
    print("RG_BODY_BYTES:", len(rg.encode("utf-8")))


if __name__ == "__main__":
    main()

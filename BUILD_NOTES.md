# Build notes
- Bodies extracted verbatim from the draft .md files (no byte altered).
  content-needs-release-gates: 원고 section of x-article-release-gates/article.md
  (title line to just before '## 숏포스트 3개').
- DRAFT meta blocks and short-post sections excluded from pages.
- canonical <link> NOT added: domain not finalized. Add after deploy:
  <link rel="canonical" href="https://DOMAIN/posts/<slug>"> per article page.
- Image mapping: images/write-50-posts.webp / 7-round-rule.webp / daily-compounding.webp
  <- media-generation-x-article-2026-09-19-50-posts-*.webp,
     media-generation-x-article-2026-09-19-7-round-r-*.webp,
     media-generation-daily-compounding-cover-*.webp
- content-needs-release-gates images: 00-hero-release-gates.webp,
  01-gate-stockpile.webp, 02-gate-calibration.webp, 03-gate-day1.webp,
  04-gate-verdict.webp, 05-closing-pipeline.webp (inline at 👉 markers)
- daily-compounding body sha256: d33c2af49bb400ac5d42a6c4aefc3fdd3f119e3e78fc06989851585f5ea81ec3
  (bytes = from second '# Daily Compounding...' heading line start
   to just before the line that is exactly '---')
- content-needs-release-gates body sha256: 07b325d63994d8431dbfe1611b810254bd2e89c478d07c314e953d12bf521479
  (bytes = from '# Content Needs Release Gates...' title line under
   '## 원고 (영어 전문)' to just before the line '## 숏포스트 3개')

# Technical SEO and Search Access

Load for crawlability, indexability, rendering, sitemap, canonical, internal-link, structured-data, migration, local/ecommerce, or search-discovery changes.

## Evidence-bearing checks

For each representative public route, inspect the response and rendered page where feasible:

| Check | What to verify |
| --- | --- |
| URL/status | Intended public URL resolves to appropriate content and status |
| Rendering | Essential content and meaningful links survive rendering/hydration |
| Crawl/indexing controls | robots.txt, meta/X-Robots-Tag, auth, CDN/WAF match intent |
| Canonical | Intended equivalent URL without contradictory signals |
| Sitemap | Intended canonical/indexable URLs; truthful update data |
| Links | Important routes reachable through normal links; moved links resolve |
| Not found | Missing routes are genuine not-found responses |
| Page identity | Title, main heading, language, content, and intent align |
| Variants | Pagination/filter/search/locale strategy is deliberate |
| Structured data | Truthful, visible, eligible, and validated for the actual page |
| Favicon and app icons | Resolve correctly across browser tab, bookmark, home-screen, and OS surfaces — see below |
| Private routes | Account/checkout/admin data is protected, not merely hidden |

Record TESTED scope; do not claim site-wide results from a sample. Choose rendering patterns appropriate to the stack and test the result instead of treating any rendering mode as universally required.

## Favicon and app icons

A missing or broken favicon is verifiable from public evidence alone — check it during the [public scan](public-scan.md), before any account access is needed, and fix it as a small, reversible, high-confidence change.

Check, per representative site (this is origin-level, not per-page):

| Check | What to verify |
| --- | --- |
| Root fallback | `<origin>/favicon.ico` returns a successful image response; browsers request it even when a `<link>` tag is present |
| Declared icon | `<head>` includes a working `<link rel="icon" href="...">` (and `sizes`/`type` when multiple formats are offered) pointing at a URL that resolves |
| Apple touch icon | `<link rel="apple-touch-icon" href="...">` resolves, for iOS home-screen/bookmark use |
| Web app manifest | If a `<link rel="manifest">` is present, its `icons` array entries resolve at the declared `sizes` |
| Consistency | The icon is recognizable, on-brand, and not a placeholder/default framework icon left over from scaffolding |

Use a public checker such as realfavicongenerator.net's favicon checker, or fetch the URLs directly, to confirm this without any account. Classify the finding:

- **Missing** — no `/favicon.ico` and no working `<link rel="icon">`: browsers fall back to a blank/generic icon. Treat as a real, low-effort, high-visibility defect, not cosmetic noise, since it appears in every browser tab, bookmark, and history entry.
- **Broken** — a `<link>` tag exists but its `href` 404s or the referenced file is not a valid image: worse than missing, because it signals neglect and can be flagged by validators.
- **Incomplete** — the root favicon works but touch-icon/manifest icons are missing, so the site looks unfinished when added to a home screen.

Propose the smallest fix that closes the gap: add or correct the `<link>` tags, ensure `/favicon.ico` exists at the root, and generate the missing sizes from the existing logo/mark rather than inventing new brand assets. Treat any resulting visual/brand choice (which mark, what background, live-area cropping for maskable icons) as needing the same sign-off as other on-site brand decisions.

## Internal linking and architecture

Map pages to distinct customer jobs, not keyword variations. Use concise descriptive navigation and contextual links. Investigate orphan pages before adding every route to global navigation. Avoid arbitrary click-depth quotas. Preserve valuable routes and incoming links unless evidence supports a change.

## Migration and recovery

Separate URL/domain/framework/design changes where practical. For material moves, capture protected assets, write old-to-new mappings, redirect only to genuinely equivalent destinations, update internal links/canonicals/sitemaps/language signals, test chains/loops, prepare rollback, and obtain production approval. Never use robots.txt as privacy protection or a canonical as a deletion substitute.

## Conditional branches

- **Local:** verify real identity, service area, hours, eligibility, routing, and local substance. Do not invent addresses or interchangeable location pages.
- **Ecommerce:** align price, currency, availability, variants, delivery/returns, feeds, and visible product facts; test inventory/cart/checkout/refund paths.
- **Multilingual:** localize the actual offer and support, define URLs and language alternates deliberately, test switching/fallbacks, and obtain review for consequential translations.
- **High stakes:** require qualified review for consequential health, legal, financial, or safety claims. A disclaimer does not repair an unsupported claim.

Consult current official platform documentation for mutable rules and eligibility; valid markup or correct technical implementation does not guarantee indexing, snippets, or rich results.

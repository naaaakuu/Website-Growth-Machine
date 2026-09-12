# Public, No-Login Baseline Scan

Load first, before any account-access request, for a new engagement, a first look at an unfamiliar site, or when the user has not yet granted analytics/Search Console/behavior-tool access. Every check here uses only the public URL: a public web tool, an unauthenticated API, or a direct HTTP fetch. None require the user to sign in, connect an account, or share a password.

## Why this comes first

A working site, a readable robots.txt, a valid TLS certificate, a real favicon, and a crawlable sitemap are true or false regardless of who owns the analytics account. Diagnosing and fixing what public evidence already proves broken does not need to wait on [the growth-data and access checklist](../templates/growth-access-intake.template.md). Run this scan, report findings, and propose fixes before asking the user to connect anything. Only after this pass is exhausted does connected-account access become the next bottleneck — present it then as a follow-up checklist, not an upfront blocker.

## What this cannot replace

A public scan cannot see real user sessions, query-level search performance, conversion outcomes, or field Core Web Vitals for low-traffic pages. Label every finding from this pass with the correct [evidence label](../SKILL.md); most are OBSERVED (the tool result itself) or ESTIMATED (a lab/synthetic score standing in for a real-user outcome), never OBSERVED business impact. State plainly which questions remain UNKNOWN until the user connects a source.

## No-login toolkit

| Area | Tool | URL pattern | What it proves without an account |
| --- | --- | --- | --- |
| Lab performance + Core Web Vitals estimate | PageSpeed Insights (web report and unauthenticated API) | `https://pagespeed.web.dev/report?url=<url>` | Lab score, opportunities, and CrUX field data when the origin/page has enough real-user traffic to be published |
| Synthetic speed + waterfall | Pingdom Website Speed Test | `https://tools.pingdom.com/#<url>` | Load waterfall, response times by resource, performance grade from a chosen test region |
| Alternate synthetic speed | GTmetrix (unauthenticated test) | `https://gtmetrix.com/` | Second lab data point and waterfall to corroborate Pingdom/PSI |
| TLS/certificate configuration | Qualys SSL Labs | `https://www.ssllabs.com/ssltest/analyze.html?d=<host>` | Certificate validity/chain/expiry, protocol/cipher grade, common misconfguration |
| HTTP security headers | securityheaders.com | `https://securityheaders.com/?q=<url>` | Presence/grade of HSTS, CSP, X-Content-Type-Options, X-Frame-Options, Referrer-Policy |
| Structured data validity | Schema Markup Validator | `https://validator.schema.org/#url=<url>` | Whether JSON-LD/microdata parses and matches a recognized type |
| Markup validity | W3C Markup Validator | `https://validator.w3.org/nu/?doc=<url>` | HTML parsing errors that can affect rendering/accessibility |
| Crawl/indexing controls | Direct fetch | `<origin>/robots.txt`, `<origin>/sitemap.xml` | Whether crawl rules and sitemap exist, parse, and list live URLs |
| Broken links, redirects, duplicate titles/descriptions, missing alt text | `scripts/audit_site.py` (bundled, offline-testable) | run against the public origin | A bounded, same-origin, script-free crawl report — see [technical-seo](technical-seo.md) |
| Favicon and app icons | Direct fetch + realfavicongenerator.net checker | `<origin>/favicon.ico`, `https://realfavicongenerator.net/favicon_checker` | Whether a favicon resolves, whether `<link rel="icon">`/`apple-touch-icon`/manifest icons are present and correctly sized — see [technical-seo](technical-seo.md#favicon-and-app-icons) |
| Historical change/decline evidence | Wayback Machine | `https://web.archive.org/web/*/<url>` | Prior page states useful for RECOVER-mode comparisons |
| DNS/domain health | A public DNS/WHOIS lookup tool | e.g. `https://dnschecker.org/`, registrar WHOIS | Nameservers, propagation, MX presence, registration/expiry status |
| Technology footprint | A public tech-detection tool | e.g. `https://www.wappalyzer.com/lookup/` | CMS/framework/tag-manager footprint, useful context for feasibility, not a security or quality verdict |
| Coarse indexing sanity check | Search engine `site:` operator | `site:<domain>` in a search engine | A rough, non-authoritative signal of what a search engine has indexed |

Every URL above is mutable third-party behavior: confirm the tool is still free/unauthenticated at the time of use and record the access date, following [source-policy](source-policy.md). A free tier can change; do not hardcode a claim about a vendor's pricing or scope into a finding.

## Sequencing inside a session

1. Confirm the public URL, and fetch `robots.txt` and `sitemap.xml` directly — they gate whether anything else below is trustworthy.
2. Run `scripts/audit_site.py` against the public origin for a bounded structural crawl (broken links, redirects, duplicate titles/descriptions, missing alt text, favicon signals).
3. Run PageSpeed Insights and one synthetic tool (Pingdom or GTmetrix) against the representative templates identified by the crawl, per [performance](performance.md).
4. Run the SSL Labs and securityheaders.com checks once per origin.
5. Run the Schema Markup Validator and W3C validator on representative templates where structured data or markup issues are suspected.
6. Check the favicon and app icons per [technical-seo](technical-seo.md#favicon-and-app-icons).
7. Compile findings into the audit report, labeled with the correct evidence tier, and propose the smallest safe fixes per the [default-to-action rule](../SKILL.md).
8. Only then present [the growth-data and access checklist](../templates/growth-access-intake.template.md) — framed as what would sharpen or unlock the *next* layer of diagnosis (real user behavior, query-level search performance, conversion data, paid/social channels), not as a precondition for the work already done.

## When public evidence is enough to act

Treat a public-scan finding as sufficient to propose a fix, without waiting on account access, when it is independently verifiable from the response itself: a missing/expired TLS certificate, a broken favicon, a robots/sitemap error, a 4xx/5xx on a linked route, a failing security header, invalid structured data, or a clear synthetic-performance regression against a recorded baseline. Still route any production change through the [authority tiers](../SKILL.md) and the approved [repair budget](../SKILL.md).

# Changelog

## 2.5.0

- **Public evidence before account access.** Added [references/public-scan.md](references/public-scan.md): a free, no-login toolkit (PageSpeed Insights, Pingdom/GTmetrix, SSL Labs, securityheaders.com, the Schema Markup Validator, the W3C validator, direct robots.txt/sitemap fetches, `scripts/audit_site.py`) that now runs and gets diagnosed/fixed before [the growth-data and access checklist](templates/growth-access-intake.template.md) is presented. The checklist is reframed as a follow-up for real user behavior, query-level search performance, conversions, and paid/social data — never a precondition for the work public evidence can already prove.
- **Favicon and app icons are now a named check**, in [references/technical-seo.md](references/technical-seo.md#favicon-and-app-icons): root `/favicon.ico`, `<link rel="icon">`, apple-touch-icon, and manifest icons, classified as missing/broken/incomplete, with a smallest-safe-fix recommendation.
- **macOS installation.** Added `install.sh` / `install.command` (double-click on macOS, no folder navigation needed) alongside the existing manual copy-the-folder path, plus [INSTALL.md](INSTALL.md) with platform-specific steps and a `package_release.sh` script that produces a single distributable `.tar.gz` (chosen over `.zip` because it keeps the installer's executable permission intact).

## 2.4.0 and earlier

See [MIGRATION.md](MIGRATION.md) for the transition from the single-file v1.0.0 master to the modular package.

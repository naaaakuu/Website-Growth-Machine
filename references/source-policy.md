# Source and Freshness Policy

Load before implementing or asserting mutable platform-specific behavior, including crawler rules, structured-data eligibility, APIs, analytics behavior, browser/tool features, framework versions, or skill installation paths.

## Rules

1. Prefer current primary documentation, the installed project's documented version, and first-party business data.
2. Record publisher, URL or approved export, access date, scope, relevant excerpt/claim, affected decision, and limitations in the source register.
3. Distinguish a platform requirement, platform recommendation, independent observation, vendor estimate, and internal convention.
4. Do not rely on remembered SEO folklore, tool scores, leaked interpretations, or AI answers where current authoritative documentation is accessible.
5. If primary documentation cannot be reached, mark the behavior UNKNOWN or unverified; do not silently hardcode it.
6. Never assert knowledge of proprietary ranking weights, ranking algorithms, AI-citation systems, or provider-internal metrics.

## Recommended source families

Use current official sources for search/crawler/indexing behavior; schema or search-engine feature eligibility; web performance and browser standards; accessibility standards; analytics/payment/CRM integrations; hosting/framework runtime behavior; and platform-specific skill/tool installation. Keep source links in the project record rather than duplicating volatile rules across modules.

## Refresh triggers

Refresh a source when a platform change is likely, a tool reports changed behavior, a dependency/runtime is upgraded, a policy decision depends on it, or evidence conflicts with prior guidance. Update the affected instruction/test rather than preserving an obsolete rule for consistency.

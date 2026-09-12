# Existing-Site Protection and Recovery

Load for existing sites, traffic/ranking decline, outages, migrations, suspected regressions, or valuable-asset changes.

## Protect before changing

Begin with a read-only baseline: representative pages/templates, working journeys, production commit/build if known, URL/status/redirect/canonical samples, sitemap/crawl controls, analytics definitions, structured-data samples, acquisition/conversion evidence, and customer/support signals. Mark assets PROTECTED when evidence suggests revenue, leads, qualified demand, relevant links, repeat use, assisted journeys, navigation, compliance, or seasonal value.

Classify pages as KEEP, FIX, EXPAND, MERGE, RETIRE, or INVESTIGATE. Low visible traffic alone is not enough to delete or merge a page. Require review for irreversible changes.

## Branching diagnosis

| Observation | Investigate before changing |
| --- | --- |
| Sales fall; visits stable | Offer, stock/capacity, checkout, payment, lead handling, tracking |
| Analytics falls; Search data stable | Tags, consent, filters, reporting/time alignment |
| Impressions fall; positions stable | Demand, seasonality, query mix, indexing, result-layout changes |
| Pages disappear after release | robots/noindex, canonicals, status/auth/WAF, rendering, redirects |
| One template slows | Shared assets, API/server, cache, third parties, media |
| Clicks fall; impressions similar | Query/position mix, titles/snippets, result layout, intent |

These are investigation paths, not automatic explanations. Stabilize availability, data integrity, and core customer journeys first. Preserve evidence and use approved rollback paths; do not disable security, consent, or authentication as a shortcut.

## Recovery loop

Capture before state → reproduce → form a root-cause HYPOTHESIS → predict an observable change → make the minimal authorized fix → rerun targeted and regression tests → compare → accept/revert/inconclusive → record. Limit attempts by approved budget and stop with a specific blocker when evidence or permission is missing.

# Performance and Core Web Vitals

Load for speed regressions, Core Web Vitals, Lighthouse, PageSpeed/CrUX, synthetic monitoring, performance budgets, or rendering diagnostics.

## Separate evidence types

Label lab and field measurements separately. A Lighthouse navigation run is a lab diagnostic; it does not establish field Core Web Vitals or customer experience across a population. Field data needs its source, cohort/origin/page scope, device, percentile/window, and data sufficiency. New sites may have no field data: record NOT_TESTED and create an observation plan.

Compare only like with like: URL/template, production-like build, device, network/throttling, runner/location, cache, consent/auth state, browser/tool version, and run count. Keep all comparable runs; report median and spread, not only the best result.

## Diagnose by mechanism

Use waterfalls, traces, and user context to identify server/API delay, cache/CDN behavior, request discovery, image priority, transfer/compression, CSS/font blocking, third-party work, JavaScript/hydration, main-thread tasks, rendering delay, interaction latency, or layout shifts. Choose a remedy based on the mechanism and retest the journey.

## Safe budgets

Set project-specific budgets before optimization. Check raw metrics alongside scores. Do not remove useful functionality, consent/privacy controls, analytics, accessibility, or hard pages merely to improve a score. Do not lower a budget silently.

Use saved-report evaluation for reproducible lab gates and an authorized browser/synthetic/RUM tool for the rest. These tools do not certify SEO, security, accessibility, or business outcomes.

Use a current field-data source such as PageSpeed/CrUX where available, and an authorized synthetic/waterfall tool such as Pingdom or an equivalent where useful. Record the provider, collection conditions, and access date rather than treating tool behavior as permanent.

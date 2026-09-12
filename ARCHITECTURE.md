# Package Architecture

This is one canonical, model-neutral Website Growth Operating System. The old flattened master is preserved in archive/WEBSITE_GROWTH_MASTER.v1.0.0.md; it is not executed or overwritten.

~~~
website-growth-engine/
├── SKILL.md                    # control plane and progressive-loading router
├── references/                 # conditional specialist decision guidance
├── scripts/                    # portable deterministic checks
├── tests/                      # unit tests for scripts
├── templates/                  # per-project .growth records
├── evaluations/                # adversarial agent-behavior evaluations
├── assets/                     # thin adapters and use examples
├── archive/                    # preserved source version
├── INSTALL.md                   # platform install steps, incl. one-click macOS installer
├── CHANGELOG.md                 # what changed between versions
├── AUTOMATION.md                # helper contracts, exit codes, and limitations
├── WEAKNESS_AUDIT.md           # v1 assessment and treatment decisions
├── MIGRATION.md                # material differences from v1
├── LIMITATIONS.md               # explicit capability boundaries
├── SELF_AUDIT.md                # requested quality-standard review
└── VALIDATION.md                # completed validation passes and scope
~~~

## Loading contract

SKILL.md is deliberately a control plane: it establishes evidence vocabulary, authority boundaries, modes, triage, prioritization, repair loops, records, gates, and exact module-routing conditions. An agent reads only the references demanded by the work it is actually doing.

| Need | Module |
| --- | --- |
| Free, no-login checks before requesting account access | public-scan |
| Business goal, bottleneck, investment | strategy |
| Demand/customer/query opportunity | opportunity-research |
| Actual search-result opportunity | serp-intelligence |
| Competitive alternatives/gaps | competitor-intelligence |
| Existing asset or decline protection | existing-site-recovery |
| Crawl/indexing/migration/schema | technical-seo |
| Page architecture and responsible answer discovery | content-discovery |
| Defensible original assets | content-moats |
| Ethical PR/partnerships/referrals | authority-distribution |
| Brand demand/repeat use | brand-demand |
| UX, forms, checkout, booking | cro-ux |
| Events, systems of record, attribution | analytics-attribution |
| Causal testing | experiments |
| Downstream value and retention | retention-ltv |
| Lab/field performance | performance |
| Inclusive journey verification | accessibility |
| Privacy, resilience, security boundaries | reliability-security |
| Acceptance, release, observation | verification-release |
| Handoff, installation, CI | agent-portability |
| Mutable external facts | source-policy |

The scripts are intentionally narrow. They automate deterministic collection/validation and produce inputs to judgment; they do not replace browser journey tests, a real accessibility review, specialist review, customer research, experimentation, production permission, or observed business outcomes.

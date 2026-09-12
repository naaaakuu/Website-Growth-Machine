# Migration from Website Growth Master v1.0.0

## Preservation

The original standalone master is retained unchanged in archive/WEBSITE_GROWTH_MASTER.v1.0.0.md. This package does not overwrite a repository’s AGENTS.md, CLAUDE.md, deployment configuration, .growth records, or live website.

## What materially changed

1. **From a monolith to progressive loading.** The 1,130-line master becomes a concise control plane and 21 targeted modules. Agents load only what their current mode and diagnosis need.
2. **From recommendations to executable support.** The unavailable referenced helpers are replaced with portable scripts and tests for bounded crawling, saved Lighthouse evidence, state initialization, and record validation.
3. **From four evidence labels to six.** IMPLEMENTED, TESTED, and OBSERVED prevent implementation, test, and outcome claims from being conflated.
4. **From a broad checklist to a prioritization engine.** Candidates now include value, reach, confidence, compounding, reversibility, effort, risk, maintenance, and time-to-learning, with critical failures overriding scoring.
5. **From SEO-centric content to defensible assets.** Content-moat, brand-demand, retention/LTV, SERP click-opportunity, and domain-portfolio systems make the business case explicit.
6. **From generic safety to adversarial validation.** Scenarios test prompt injection, false certainty, missing permissions, measurement breaks, traffic-quality tradeoffs, and harmful growth requests.
7. **From handoff prose to state schemas.** .growth templates make decisions, evidence, tests, experiments, releases, and learnings recoverable across agents.

## Installation and adaptation

1. Put the whole folder in the repository’s chosen skill location or retain it as a referenced canonical directory.
2. Merge only the relevant thin section from assets/AGENTS.fragment.md and/or assets/CLAUDE.fragment.md; do not replace existing project instructions.
3. From the target project root, initialize .growth non-destructively with scripts/init_growth_state.py if desired.
4. Fill templates with actual facts and evidence. Do not commit secrets, raw personal data, or restricted exports.
5. Run Python unit tests after changing scripts. Validate release claims against acceptance gates, not a script exit code alone.

## Compatibility notes

The package deliberately avoids assuming an AI model, framework, analytics vendor, paid SEO suite, browser tool, hosting provider, or deployment mechanism. Any model-specific installation path, crawler policy, platform API, structured-data eligibility, or tool behavior must be checked against current official documentation using references/source-policy.md.

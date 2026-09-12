# Weakness Audit of v1.0.0

Audited artifact: WEBSITE_GROWTH_MASTER.md, preserved under archive/. The supplied 1,130-line document is a useful operating manual, but it is flattened and references a missing skill.zip plus helper scripts that were not supplied as a cohesive package. The adjacent independent skills are complementary sources, not a canonical dependency set. Their automation contains conflicting arbitrary SEO rules and outdated assumptions, so this revision does not import it verbatim.

Treatment labels mean: **KEEP** retains a sound principle; **IMPROVE** adds precision; **REFACTOR** relocates or normalizes it; **AUTOMATE** makes a deterministic subset executable; **REMOVE** deletes unsafe or misleading behavior; **ADD** introduces an absent capability.

| Component | v1 assessment | Treatment and concrete change |
| --- | --- | --- |
| Governing business outcome | Strong focus on qualified outcomes and guardrails | **KEEP + IMPROVE**: add metric tree, system of record, bottleneck choice, and downstream-value checks. |
| Evidence vocabulary | Useful measured/estimated/hypothesis/unknown distinction | **IMPROVE**: add IMPLEMENTED, TESTED, and OBSERVED; prevent test, implementation, and business-result conflation. |
| Skill architecture | Flattened master forces irrelevant context loading | **REFACTOR**: concise SKILL.md control plane plus selectively loaded references. |
| Source delivery | Refers to unavailable helper paths | **REFACTOR + ADD**: package real scripts/templates/tests and preserve v1 source. |
| Strategy | Sound objective-first logic but spread through modules | **REFACTOR** into strategy.md; add explicit investment/no-build record. |
| Objective selection | Good primary-outcome principle | **IMPROVE**: require denominator, window, system of record, guardrails, and capacity. |
| Audience research | Credible protocol but weak stopping/decision rule | **IMPROVE**: add customer-job map, contrary evidence, and decision threshold. |
| Keyword research | Correctly rejects invented numbers | **KEEP + IMPROVE**: label provider estimates and tie clusters to opportunity records. |
| SERP intelligence | Mentions features but lacks a reusable record or click decision | **ADD** dedicated SERP module and record. |
| Competitor intelligence | Strong anti-copying language, less structured comparison | **IMPROVE**: compare task completion, proof, distribution, and defensible gaps. |
| Existing-site protection | Strong baseline/protected-assets concept | **KEEP + AUTOMATE**: records plus bounded crawl evidence. |
| Decline diagnosis | Helpful branches, largely prose | **IMPROVE**: use diagnosis hypotheses across measurement, demand, technical, offer, and operations. |
| Technical SEO | Good principles but no usable delivered validator | **KEEP + AUTOMATE**: crawler reports status, redirects, canonical, robots, metadata, links, and images. |
| Crawl/indexing architecture | Comprehensive checks but dispersed | **REFACTOR** into a single scoped evidence checklist. |
| Internal linking | Good anti-arbitrary guidance | **KEEP + AUTOMATE**: flag broken links/orphan candidates; leave remediation to judgment. |
| Structured data | Correctly rejects universal markup | **KEEP + IMPROVE**: require visible-fact rationale and current eligibility source. |
| Content strategy | Useful but articles remain an implied default | **IMPROVE**: make page/tool/no-build selection explicit. |
| Content quality | Strong anti-fabrication guidance | **KEEP + IMPROVE**: formalize source/originality/claims/task/maintenance checks. |
| Content moat | Examples, not a decision system | **ADD** an asset scorecard and maintainability requirements. |
| AI/answer discovery | Sensible caveats mixed with architecture | **REFACTOR** into content-discovery; require sampling metadata and no citation claims. |
| Local/ecommerce SEO | Useful guardrails without routing trigger | **IMPROVE**: make conditional technical/content branches with real-world facts and journey tests. |
| Migration | Strong principles | **KEEP + IMPROVE**: protected-asset diff, map, approval, rollback, and observation. |
| Owned domains | Good anti-network rules | **REFACTOR** into BUILD/CONSOLIDATE/REDIRECT/HOLD/SELL/RETIRE/DEFER model. |
| Digital PR/backlinks | Safeguards exist; operating model thin | **IMPROVE**: define audience value, disclosure, cost, and downstream referral outcome. |
| Brand demand | Mentioned but not operated as a system | **ADD** a repeat-use, reputation, owned-audience, and review/referral module. |
| CRO/UX | Strong anti-dark-pattern posture, broad checklist | **REFACTOR + IMPROVE**: require a verified mechanism and downstream guardrails per intervention. |
| Funnels/lead handling | Present but attenuated after form submission | **IMPROVE**: map response, qualification, attendance, fulfillment, and capacity. |
| Analytics/attribution | Strong concepts, no reusable QA schema | **AUTOMATE + ADD** templates and record validation. |
| Cross-domain measurement | Good warnings, not a full decision path | **IMPROVE**: require unified/referral choice, consent boundary, and source preservation. |
| Experiments | Sound safeguards, no rigorous reusable schema | **REFACTOR + ADD** experiment template and adversarial evaluation. |
| Performance/CWV | Lab/field distinction is correct; numerical defaults too prominent | **IMPROVE**: mechanism diagnosis and project-approved budgets. |
| Lighthouse | v1 proposes a missing helper | **AUTOMATE** saved-report evaluator with coverage/duplicate checks and tests. |
| Synthetic/field tools | Names sources without clean evidence separation | **REFACTOR** field/lab/synthetic requirements. |
| Accessibility | Good automated/manual distinction | **KEEP + IMPROVE**: route/state/journey coverage and acceptance tests. |
| Security/reliability | Sensible boundary but thin incident scaffolding | **IMPROVE**: authorized scope, idempotency, monitoring/rollback owner, privacy minimization. |
| Browser/mobile testing | Mentioned, not tied to customer outcomes | **IMPROVE**: test success, error, retry, and interruption states. |
| Retention/LTV | Present late and briefly | **ADD** dedicated downstream-value and cohort module. |
| Automation | Intended scripts missing; companion scripts use arbitrary rules | **REFACTOR + AUTOMATE** portable, tested standard-library tools. |
| CI/CD/reporting | Proposed, without record validation | **IMPROVE** handoff/CI boundaries and release/report templates. |
| Prioritization | Qualitative score misses reversibility/time-to-learning | **IMPROVE** transparent qualitative decision model plus critical override. |
| Agent portability | One-source principle is sound; fixed discovery paths are volatile | **REFACTOR** thin adapters and current-documentation source policy. |
| Persistent state | Useful .growth proposal but incomplete schemas | **ADD** state, evidence, audit, experiment, release, and learning templates. |
| Prompt/token efficiency | Flat document is costly for narrow work | **REFACTOR** with exact module-routing table. |
| Failure recovery | Repair loop is good but predictions/records are not enforced | **IMPROVE** expected observable, repair budget, and accept/revert/inconclusive status. |
| Anti-hallucination | Strong prose safeguards | **KEEP + IMPROVE** adversarial scenarios for access gaps and prompt injection. |
| Release safety | Strong deployment boundary | **KEEP + IMPROVE** preview/production distinction and release record. |
| Post-launch learning | Present but not structured | **ADD** learning record and invalidation/resume rule. |

## Specific removal/refactor decisions

- **REMOVE** fixed SEO assertions from companion automation: mandatory one-H1, fixed word count, universal canonical/JSON-LD requirements, fixed internal-link quotas, or automatic CSS/performance fixes from static HTML.
- **REMOVE** hardcoded Lighthouse scoring curves and unverified provider-specific thresholds. The evaluator reads the project’s declared policy and raw report fields.
- **REMOVE** experiment helpers that silently substitute rounded alpha/power settings or declare success after a sample-ratio mismatch.
- **REFACTOR** repeated safety rules into the control plane and specialist modules so they remain prominent without loading every checklist for every task.

The new package retains v1’s best ideas—outcome-first work, protected assets, ethical behavior, no fabricated certainty, lab/field distinction, and release discipline—while becoming executable, auditable, and economical to load.

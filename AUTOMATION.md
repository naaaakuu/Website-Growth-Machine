# Deterministic Automation

All helpers require Python 3.9+ and only the standard library. They never use credentials, execute crawled scripts, or make an external change. Run tests from the package root with:

~~~
python -B -m unittest discover -s tests -v
~~~

| Script | Inputs | Output | Exit codes | Limits |
| --- | --- | --- | --- | --- |
| scripts/audit_site.py | Start HTTP(S) URL; optional crawl limits/output path | JSON crawl inventory, verified broken links, redirect chains, duplicate metadata groups, passive image-alt observations, and conservative audit issue candidates | 0 clean bounded crawl; 1 verified fetch/link findings; 2 invalid input; 3 local/runtime failure | Same-origin only; does not execute JavaScript, authenticate, submit forms, discover every URL, or certify SEO/accessibility/security. |
| scripts/evaluate_lighthouse.py | Explicit policy JSON and saved Lighthouse JSON reports | JSON coverage, duplicate/malformed report, and policy-rule evaluation | 0 pass; 1 evidence/rule failure; 2 invalid policy/invocation; 3 local/runtime failure | Does not run Lighthouse, prove report provenance, establish field data, or approve a release. |
| scripts/init_growth_state.py | Project root; optional .growth/template/output paths | JSON report of non-destructively created/existing state records | 0 initialized; 2 invalid input; 3 local/runtime failure | Never overwrites, deletes, or infers business facts. The draft quality policy must be completed before Lighthouse evaluation. |
| scripts/validate_growth_records.py | Project root or explicit .growth path | JSON report of record status, IDs, evidence links, and validation errors | 0 valid; 1 validation failures; 2 invalid/missing target; 3 local/runtime failure | Validates record shape/link safety, not factual truth, live access, or business outcomes. |

Use the script help text for exact flags. Treat all JSON reports as evidence inputs to the method, not automatic production or business decisions.

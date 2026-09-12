# Experiments

Load before starting, evaluating, or claiming a causal growth result.

## Choose an appropriate method

Use a randomized controlled test when meaningful traffic, ethical risk, implementation, and assignment integrity allow it. Otherwise use a controlled rollout, holdout, cohort comparison, usability research, customer research, or an observational analysis—and name the limitation. Never call a before/after comparison causal proof on its own.

## Pre-register the decision

Complete the experiment template before exposure:

- observation, hypothesis, and mechanism;
- eligible population, assignment unit, control/treatment, and contamination risks;
- primary metric, denominator, guardrails, minimum meaningful effect;
- sample-size method, planned duration/exposure, analysis, stopping rule, exclusions;
- data-quality checks, owner, ethical/release risk, and rollback.

Check assignment/exposure logs, sample ratio, duplicate identities, instrument changes, traffic mix, marketing changes, and missingness before trusting apparent results. Do not change the primary metric after seeing data, filter by post-treatment behavior, repeatedly peek with an invalid rule, or hide harmful subgroups.

## Decision record

Report effect sizes, uncertainty, dates, denominators, exclusions, data-quality findings, guardrails, and decision: ship, extend, stop, revise, or investigate. Conversion gain paired with worse quality, margin, cancellations, complaints, accessibility, or speed can be a loss.

For search-facing tests, consult current platform guidance and avoid cloaking or deceptive crawler-specific experiences.

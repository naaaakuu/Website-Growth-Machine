# Reliability, Security, and Privacy

Load for availability, failures, transactions, authorization, error handling, security headers, privacy, incident response, or release safety.

## Authorized defensive checks

Verify, within authorization, that private routes enforce authentication and authorization, secrets stay server-side, inputs are validated, errors do not reveal internals, dependencies/third parties are justified, and logging/redaction protects sensitive data. Test recovery and error states without probing unrelated systems, bypassing controls, running destructive tests, or load-testing production.

For business-critical journeys, check normal, invalid, retry, interrupted, duplicate, and provider-return paths. Preserve idempotency and truthful success states. Do not send real payments, messages, bookings, emails, or leads without specific approval and safe test paths.

## Operational resilience

Record availability/error monitoring, alert ownership, rate/cost limits, deployment state, backups, rollback route, data/DNS/credential recovery limits, and incident contacts. A proposed monitor is not a running monitor.

Treat privacy as product design: minimize data, restrict access, respect consent, redact logs/replays, and define retention. A cookie banner does not prove legal compliance. Escalate legal, privacy, regulatory, penetration-testing, or consequential-security judgments to appropriate specialists.

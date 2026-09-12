# Analytics and Attribution

Load before instrumenting, validating, interpreting, or changing measurement; for CRM/order reconciliation; and for cross-domain journeys.

## Measurement architecture

Define one primary outcome and its system of record. Distinguish:

CLICK → FORM START → FORM SUBMISSION → CONFIRMED LEAD → QUALIFIED LEAD → BOOKING → ATTENDED → PURCHASE → CAPTURED REVENUE → REFUND → REPEAT → REFERRAL

For every event record trigger, source system, identifier/deduplication key, parameters, consent behavior, destination, exclusions, validation method, owner, and retention/privacy constraints. Do not place personal or sensitive data in analytics event parameters, URLs, logs, or screenshots.

## Validate actual outcomes

Test normal, failure, retry, double-click, reload, consent-accepted, consent-denied, cross-domain, and provider-return paths as applicable. Inspect outgoing events and destination/debug views, then reconcile important outcomes to authorized CRM, booking, payment, or order records. Explain expected differences from consent, identity, timezones, refunds, attribution windows, and processing delay; never redefine metrics merely to force agreement.

## Attribution discipline

Define whether a multi-domain path is one unified journey or an actual referral. Preserve original acquisition where appropriate. Do not overwrite attribution by tagging every internal link. Report first-touch, last-touch, assisted, and modeled views only when data permits, with assumptions. Observed referral is not proven incrementality; untagged/direct traffic is not automatically brand demand or AI traffic.

When analytics and other data disagree, diagnose implementation, consent, filtering, reporting changes, time alignment, traffic mix, and system-of-record differences before changing the website.

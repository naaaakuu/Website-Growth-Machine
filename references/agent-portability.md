# Agent Portability and Persistent State

Load when installing this system, moving between Codex/Claude/another agent, handing off work, configuring CI, or recovering a previous session.

## One canonical system

Keep one canonical website-growth-engine directory. Agent-specific files are thin routing adapters; they must not fork methodology or override repository/user instructions. Copy or synchronize the whole directory deliberately; do not independently edit divergent copies.

## Session recovery

On each session:

1. Read repository instructions and the canonical skill.
2. Read .growth/state.json, brief, objectives, protected assets, decisions, latest evidence, audits, experiments, releases, and backlog.
3. Inspect working-tree state and deployment evidence when available.
4. Identify the earliest invalidated gate and resume there.
5. Record new evidence, current mode, blocker, owner, next safe action, and timestamp before handoff.

Do not store secrets, raw personal customer data, account tokens, or sensitive exports in project state. Keep large raw artifacts in approved private storage and reference them.

## Automation boundaries

CI or scheduled jobs need explicit configuration, credentials, quotas, cost limits, alert routes, retries, and approval rules. A skill cannot remain active after a chat/session. It can specify a repeatable command but never claim a monitor, deploy, or external workflow is running unless evidence confirms it.

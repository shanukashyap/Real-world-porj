# SOC Tier-1 Triage Runbook

When triaging alerts: (1) **classify** — benign vs suspicious vs malicious using context (user role, asset criticality, business hours). (2) **enrich** — resolve IP/hostname, user, process hash, parent chain, and known IOC matches from threat intel feeds. (3) **contain** — isolate host, disable account, or block IP only with change control for production. (4) **document** — ticket with timeline, evidence hashes, and scope for Tier-2.

Correlate with SIEM rules: same user failing auth across regions; service accounts with interactive logon; new scheduled tasks or services on domain controllers.

For network security: review firewall denies that spike before allows to the same destination — possible C2 staging.

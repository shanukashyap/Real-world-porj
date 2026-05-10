# Threat Intelligence Fusion in the SOC

Threat intelligence combines **strategic** (actor motivation, campaigns), **operational** (TTPs, infrastructure patterns), and **tactical** (IOCs: IPs, domains, hashes). Fusion means linking IOCs to TTPs and to internal telemetry: if a hash matches malware used by a known group, escalate severity even if single-host impact looks small.

Operationalize feeds with confidence scores and source reliability; deduplicate overlapping indicators; expire stale IOCs to reduce false positives.

For RAG-assisted workflows, analysts should still verify machine output against authoritative CTI and environment-specific baselines.

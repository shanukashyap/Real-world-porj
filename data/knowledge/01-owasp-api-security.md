# OWASP API Security Top Practices

APIs are a primary attack surface for modern applications. Key risk areas include **broken object level authorization (BOLA)**, where attackers manipulate IDs to access other users' data; **broken authentication**, including weak JWT validation and missing token expiry; and **unrestricted resource consumption**, where missing rate limits allow brute force or scraping.

Mitigations: enforce authorization on every object access; validate JWTs with strict algorithms and rotating keys; apply rate limiting per IP and per user; log authentication failures for SIEM correlation; and use schema validation to reject unexpected payloads that enable injection or mass assignment.

For SOC playbooks: alert on spikes in 401/403 responses from the same source, anomalous OAuth token grant rates, and geographic anomalies on API clients.

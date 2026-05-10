# MITRE ATT&CK for SOC Detection Engineering

SOC teams map detections to **tactics** (why: initial access, execution, persistence) and **techniques** (how: T1078 valid accounts, T1566 phishing). A strong detection strategy layers network (IDS/IPS, DNS logs), endpoint (EDR), identity (IdP sign-in logs), and application (API audit logs).

Prioritize visibility into PowerShell/script execution, lateral movement (Remote Desktop, WMI, PsExec), credential access (LSASS, keyloggers), and exfiltration channels (HTTPS uploads, DNS tunneling).

Use the MITRE Navigator to identify coverage gaps and feed those gaps into purple-team exercises.

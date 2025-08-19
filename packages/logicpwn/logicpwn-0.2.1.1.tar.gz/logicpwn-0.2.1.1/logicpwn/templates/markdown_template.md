# {{title}}

**Target:** {{target_url}}
**Assessment Date:** {{scan_start_time}} - {{scan_end_time}}
**Total Findings:** {{total_findings}}
**Critical Issues:** {{critical_count}}

---

## Vulnerability Details

{% for finding in findings %}
### {{finding.severity}} - {{finding.title}}
**CVSS Score:** {{finding.cvss_score}}
**Affected Endpoints:** {{finding.affected_endpoints}}

**Description:**
{{finding.description}}

**Proof of Concept:**
```http
{{finding.proof_of_concept}}
```

**Impact:**
{{finding.impact}}

**Remediation:**
{{finding.remediation}}

**References:** {{finding.references}}
**Discovered At:** {{finding.discovered_at}}

---
{% endfor %}

## Appendix
- **Scan Duration:** {{scan_duration}}
- **LogicPwn Version:** {{logicpwn_version}}
- **Authentication:** {{authenticated_user}} 
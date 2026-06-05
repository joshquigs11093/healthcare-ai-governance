# AI Incident Response Playbook

*Adapt this playbook for your organization and attach a system-specific version to
each higher-risk AI system. The goal is that no one has to improvise during a
safety event. Decisions about shutting a system off should be answerable in
advance.*

---

## What counts as an AI incident

Any event where an AI system causes, or risks causing, harm or a governance
breach, including:

- A clinical model producing systematically wrong outputs (false reassurance,
  missed cases).
- A generative system leaking PHI or producing unsafe medical advice.
- Performance or fairness degradation detected by monitoring (drift).
- A security event involving an AI system or its data.
- Use of a system outside its approved scope.

## Severity levels

| Level | Definition | Example |
|---|---|---|
| **SEV-1** | Imminent or actual patient harm | Sepsis model fails silently in the ICU |
| **SEV-2** | Significant risk, no confirmed harm yet | Fairness monitoring shows a new critical disparity |
| **SEV-3** | Limited/contained issue | A generative tool emitted PHI in one logged output |
| **SEV-4** | Minor / informational | Cosmetic error; degraded non-clinical feature |

## Roles during an incident

- **Incident Lead** — coordinates response and decisions. (Default: _________)
- **Clinical Safety Owner** — assesses patient-safety impact. (Default: _________)
- **System Owner** — the accountable owner for the affected system.
- **Technical Responder** — can disable, roll back, or patch the system.
- **Privacy/Compliance** — engaged for any PHI or regulatory exposure.
- **Communications** — internal and, where required, external notification.

## Response steps

1. **Detect & report.** Anyone may raise an incident via: _______________________.
   Record time, system, and what was observed.
2. **Triage.** Incident Lead assigns a severity and convenes the needed roles.
3. **Contain.** For SEV-1/2, decide whether to disable or roll back the system.
   *Pre-authorize who may make this call so it is not delayed.* Default
   authority: _______________________.
4. **Assess clinical impact.** Clinical Safety Owner determines whether any
   patients were affected and what clinical follow-up is required.
5. **Notify.** Inform affected clinicians/users; engage Privacy/Compliance for
   PHI or regulatory exposure; notify the vendor if applicable.
6. **Remediate.** Fix root cause; validate the fix before any restart.
7. **Restore.** Return to service only after the System Owner and Clinical Safety
   Owner sign off.
8. **Review.** Conduct a blameless post-incident review within ____ business days.

## Post-incident review

- What happened, and what was the timeline?
- What was the patient/operational impact?
- What detection worked, and what was missed?
- Root cause(s)?
- Corrective and preventive actions (with owners and dates)?
- Does the system's risk tier, monitoring, or approval need to change?

## Record

- Incident ID / date:
- System and severity:
- Summary, impact, and resolution:
- Actions and owners:
- Reported to governance committee on:

---

*Maintain completed incident records as an audit trail and review trends at the
governance committee on a recurring basis.*

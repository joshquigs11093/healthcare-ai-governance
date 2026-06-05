# Vendor Model Card Request

*Send this questionnaire to any vendor offering an AI/ML product under
evaluation. It mirrors the model-card schema this organization uses (aligned to
the ONC HTI-1 source attributes) so vendor disclosures map directly onto our
governance record. "We don't disclose that" is itself an evaluable answer.*

---

**Vendor / product / version:**
**Vendor contact for this questionnaire:**
**Date requested / date due:**

## 1. Identity and intended use

1. Product name, version, and model type (e.g. gradient boosting, transformer).
2. What is the specific, intended clinical or operational purpose?
3. Who are the intended users, and in what care setting?
4. What inputs does the model use, and what does it output?
5. What uses are explicitly out of scope or cautioned against?

## 2. Development data

6. Describe the development/training dataset: source, size, time period, geography.
7. What are the demographics of the development data (age, sex, race/ethnicity,
   payer mix where relevant)?
8. How representative is the development data of *our* patient population?

## 3. Validation and performance

9. What validation has been performed: internal, external, prospective?
10. Report performance metrics relevant to the use (e.g. AUROC, sensitivity,
    specificity, calibration) with confidence intervals.
11. Report performance broken down by demographic subgroup.
12. Has the model been validated at sites similar to ours? Provide evidence.

## 4. Fairness and safety

13. What fairness evaluation has been conducted, and what disparities were found?
14. What bias mitigation measures are in place?
15. What are the known limitations and failure modes?
16. What safety considerations and contraindications apply?

## 5. Regulatory and lifecycle

17. Is the product FDA-cleared/approved? If so, provide the clearance and risk class.
18. Is there a Predetermined Change Control Plan (PCCP)? How are model updates
    handled, and how are we notified?
19. How is the model monitored in production, and what drift detection exists?
20. What is the retirement/decommission and incident-notification process?

## 6. Transparency and data handling

21. Can you provide a model card or equivalent documentation? Attach it.
22. How is our data handled, stored, and segregated? Is it used to train models
    serving other customers?
23. What audit logging and access controls does the product provide?
24. Who is the named contact for incidents and safety issues?

---

### For evaluator use

- **Completeness of disclosure:** ☐ full ☐ partial ☐ minimal — notes:
- **Gaps requiring follow-up:**
- **Recommendation:** ☐ proceed ☐ proceed with conditions ☐ do not proceed

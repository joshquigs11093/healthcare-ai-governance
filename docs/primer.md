# A Primer on Healthcare AI Governance

*Written for AI governance committee members, clinical and administrative leaders,
and the staff who support them. No machine-learning background is assumed.*

This primer explains why governing artificial intelligence in a healthcare
organization is different from governing it elsewhere, what the current US
regulatory landscape requires (and where it is uncertain), and what a workable
governance program looks like at three sizes of organization. It closes by
showing how the artifacts this toolkit produces fit a governance program — but
the program, not the tool, is the point.

---

## 1. Why healthcare AI governance differs from generic AI governance

Most published AI governance advice is written for technology companies and
generic enterprises. Healthcare inherits all of those concerns and adds several
that change the calculus entirely.

**The stakes are clinical.** A recommendation engine that mis-ranks products
costs a retailer a sale. A sepsis model that fails silently for a subpopulation
can contribute to a death. The asymmetry between a false negative and a false
positive is not a business tradeoff; it is a patient-safety question that
clinicians, not data scientists, are trained to weigh. Governance must put
clinical judgment in the loop, not merely statistical judgment.

**The data is regulated at rest and in motion.** Protected health information
(PHI) is governed by the HIPAA Privacy and Security Rules. Eighteen specific
identifier types (45 C.F.R. § 164.514(b)(2)) must be controlled, and the
"minimum necessary" principle constrains who may see what. An AI system that
ingests clinical notes, or that *emits* text containing PHI, is a privacy
surface that generic AI governance frameworks barely contemplate.

**Bias has a body count, and a history.** Healthcare data encodes decades of
unequal access and unequal treatment. A model trained on historical utilization
can learn that a group which *received* less care *needed* less care — and then
perpetuate the gap. Fairness evaluation in healthcare is therefore not an
optional ethics exercise; it is part of clinical validity. A model that performs
well on average but poorly for a subgroup is not "mostly accurate," it is
unsafe for that subgroup.

**The accountability chain is long and licensed.** When an AI system influences
care, responsibility is shared among the developing vendor, the deploying health
system, the clinician who acts on the output, and the institution that approved
its use. Several of those parties hold professional licenses and carry
malpractice exposure. Governance must make accountability explicit before
deployment, not reconstruct it after an incident.

**Automation bias is a clinical hazard, not a UX detail.** Clinicians are busy,
and a confident on-screen recommendation exerts real pull. Two failure shapes
matter: *over-reliance*, where a wrong output is accepted because the machine
said so, and *under-reliance*, where a useful tool is ignored after it cries wolf
too often (alert fatigue). Both are properties of the human–AI *team*, not the
model alone, and both are invisible to offline accuracy metrics. Governance has to
ask how the output is presented, how easy it is to override, and whether anyone is
watching how clinicians actually use it — questions a generic framework rarely
raises.

**The research-to-deployment gap is where models break.** A model that performed
beautifully in a published study can degrade badly in production because the
population differs, the data pipeline differs, the clinical workflow differs, or
simply because time has passed and practice has drifted. "It was validated"
describes the past tense at one site; it is not a standing guarantee. Healthcare
governance therefore cares as much about *local* validation and *ongoing*
monitoring as about the original evidence — a stance that distinguishes it from
the ship-it-and-iterate norms of consumer software.

**The regulatory picture is genuinely unsettled.** As of 2026, the rules
governing healthcare AI are in flux (Section 2). A governance program cannot wait
for certainty; it has to make decisions now that remain defensible under several
plausible futures. The pragmatic stance this toolkit takes is to treat the
*underlying disclosures* — what data trained the model, how it was validated,
how it performs across groups, where it should not be used — as independently
valuable regardless of which certification regime survives.

---

## 2. The current US regulatory landscape

Three frameworks shape practice. None is a complete rulebook; together they form
the reference points a governance committee should know.

### NIST AI Risk Management Framework (AI RMF 1.0)

Published in January 2023, the NIST AI RMF is the foundational, *voluntary* US
reference for managing AI risk. It is organized around four functions —
**GOVERN, MAP, MEASURE, and MANAGE** — that are meant to operate continuously
rather than as a one-time checklist. GOVERN establishes the culture and
accountability; MAP characterizes context and risk; MEASURE analyzes and tracks
risk quantitatively and qualitatively; MANAGE acts on it and monitors over time.

NIST has not published an "AI RMF 2.0." Instead the framework is extended through
*profiles*. The **Generative AI Profile (NIST AI 600-1, July 2024)** adds a
catalog of generative-AI-specific risks and suggested actions layered onto the
four functions. In April 2026 NIST released a concept note for a profile on
**Trustworthy AI in Critical Infrastructure**, which explicitly names healthcare
— a signal that sector-specific guidance is coming. Because the AI RMF is
voluntary and descriptive, it is most useful to a governance committee as a
*shared vocabulary and a coverage map*: every risk you accept or mitigate can be
tied back to a specific subcategory, which makes your reasoning auditable.

In practice the four functions are easiest to operate as a loop rather than a
sequence. GOVERN is the standing infrastructure — who is accountable, what the
policies are, how decisions get recorded. MAP happens at intake: before building
or buying, characterize the context, the affected people, and the plausible
harms. MEASURE happens at validation and on a schedule thereafter: quantify
performance, calibration, and fairness, with uncertainty. MANAGE is the action
layer: choose mitigations, decide what risk is acceptable, deploy with monitoring,
and respond when something goes wrong. A committee that can point to where each of
its systems sits in that loop — and what evidence supports the current position —
is governing in substance, not just in name. This toolkit's risk-assessment
questionnaire tags every question with the subcategory it supports precisely so
that the loop is traceable.

### ONC HTI-1 Final Rule, and the HTI-5 reversal

The ONC **HTI-1 Final Rule** (published December 2023; effective February 8,
2024; 89 Fed. Reg. 1192) established the first US *algorithmic transparency*
requirements for AI and predictive Decision Support Interventions (DSIs) in
certified health IT, with a compliance date of January 1, 2026. Its core idea is
"source attributes": certified systems must make available a defined set of
disclosures about each predictive DSI — the data used, the intended use, the
validation, the fairness assessment, the cautioned-against uses — so that a
clinician or organization can evaluate whether to trust it.

The direction then reversed. ASTP/ONC subsequently proposed a deregulation rule
(**HTI-5, late 2025**) that would remove certification requirements for clinical
decision support algorithms, including the model-card-style disclosure
requirement. As of this writing the outcome is uncertain. The defensible
position — and the one this toolkit takes — is that the HTI-1 source-attribute
*content* is good practice whether or not it is mandated, because the disclosures
it asks for (data sources, validation methodology, fairness testing, use
limitations) are exactly what a governance committee needs to make a sound
decision.

### FDA AI/ML guidance for Software as a Medical Device

Some healthcare AI is a regulated medical device; much is not. The dividing line
matters for governance because device status brings FDA oversight and a different
evidentiary bar. The key FDA documents are the **Good Machine Learning Practice
(GMLP) Guiding Principles** (October 2021, jointly with Health Canada and the
MHRA); the final **Predetermined Change Control Plan (PCCP)** guidance for
AI-enabled device software (December 2024), which lets a manufacturer pre-specify
how a model may be updated without a new submission; the **Transparency for
Machine Learning-Enabled Medical Devices** guiding principles (June 2024); and
the draft **Total Product Lifecycle (TPLC)** guidance (January 2025). By early
2026, the FDA had authorized over 1,350 AI-enabled devices. Governance programs
increasingly need to track which inventory systems fall under FDA jurisdiction,
their risk class, and whether a PCCP is in place.

### State law and the moving floor

A growing number of states regulate AI in health care directly — disclosure
requirements, rules on AI in utilization-management and coverage decisions
(several states now require that a licensed clinician, not an algorithm, make the
final medical-necessity determination), and consumer-protection statutes that
reach automated decision-making. The specifics vary and change quickly. The
governance takeaway is to assign someone ongoing responsibility for watching the
states in which the organization operates, rather than treating the federal
frameworks as the whole picture.

It is also worth knowing the **EU AI Act** exists, even for US-only
organizations, because it is shaping vendor behavior and international norms. It
takes a risk-tiered approach, places many medical and safety-related AI uses in a
"high-risk" category with conformity obligations, and influences how global
vendors document and build their products. A US health system will increasingly
encounter vendors whose disclosures are structured around it; recognizing that
vocabulary is useful even when the Act does not directly apply.

The honest summary of the 2026 landscape is that there is no single binding
rulebook for most healthcare AI, the one transparency mandate that did arrive
(HTI-1) is under active rollback, and the durable obligations are the general ones
— HIPAA for data, professional and malpractice standards for clinical use, and
anti-discrimination law for inequitable impact. A governance program built on
those durable obligations, using the voluntary frameworks as structure, will
weather whichever way the specific rules settle.

---

## 3. The minimum viable governance program

Governance does not require a large team or expensive software. It requires a few
functions performed reliably. What scales is the formality, not the fundamentals.

**Community hospital.** A single multidisciplinary committee that meets quarterly
can be enough. The non-negotiables: a written inventory of every AI system in
use (including vendor features quietly embedded in the EHR); a lightweight intake
form for any new use case; a named accountable owner per system; and a standing
agenda item to review systems that affect clinical decisions. One person — often
the CMIO — can shepherd the process. The risk here is not over-engineering; it is
*invisibility*: AI arrives through procurement and EHR upgrades without anyone
deciding to govern it.

**Regional health system.** Add structure: a defined intake-to-retirement
lifecycle, risk-tiered review (higher-risk systems get deeper scrutiny and more
frequent re-review), documented fairness evaluation for clinical models, and a
vendor-evaluation process that demands model cards and validation evidence before
purchase. A part-time AI program lead coordinates; the committee sets policy and
adjudicates the hard cases. Inventory and artifacts should live somewhere with
version history so decisions are reconstructable.

**Academic medical center.** Add depth: separation between research and clinical
deployment governance, prospective and external validation expectations,
integration with the IRB where appropriate, formal post-deployment monitoring,
and explicit handling of locally developed models (where the institution *is* the
developer and inherits developer responsibilities). The program is likely staffed
and may use a commercial governance platform; the artifacts in this toolkit then
serve as a reference for *what good looks like* rather than the system of record.

What should trigger a move up in formality is not organizational size per se but
*exposure*: the first time a model directly influences clinical decisions, the
first locally developed model, the first FDA-regulated device, or the first
generative system that can emit free text to clinicians or patients. Each of those
introduces a class of risk the lighter process was not designed to catch, and is a
natural moment to add the corresponding structure (human-oversight requirements,
developer responsibilities, device tracking, output auditing).

Across all three, the same minimum holds: **know what you have, decide before you
deploy, write down why, and look again on a schedule.** A program that does only
those four things, but does them reliably, already outperforms one with elaborate
policy and no follow-through.

---

## 4. Roles

Governance is a team sport. The titles vary; the functions do not.

- **AI Governance Committee.** The deliberative body that sets policy, classifies
  risk, approves or rejects use cases, and reviews systems on a cadence. It must
  be multidisciplinary — clinical, technical, compliance, legal, and patient or
  community perspective — because no single discipline can see the whole risk.
- **AI Program Lead.** The person who runs the process day to day: maintains the
  inventory, drives intake, schedules reviews, and assembles the evidence the
  committee needs. Often the difference between a program that functions and one
  that exists on paper.
- **Chief Data / Analytics Officer.** Accountable for data governance, quality,
  and the platforms on which models run.
- **Chief Medical Information Officer (CMIO).** The clinical voice — translates
  between clinicians and technologists and owns the question of whether a system
  is safe and useful at the point of care.
- **ML Engineering / Data Science.** Produces the technical artifacts — model
  cards, validation results, fairness reports — and implements monitoring.
- **Compliance and Privacy.** Owns HIPAA, the minimum-necessary analysis, and
  regulatory tracking.
- **Legal.** Owns contractual risk with vendors, liability allocation, and
  interpretation of evolving statute.

Two composition details matter more than they first appear. The committee should
include a **patient or community perspective**, because the people most affected by
a model's errors are rarely in the room when it is approved, and their absence
skews which harms feel salient. And the committee needs a way to handle **conflicts
of interest**: the enthusiasm of a system's champion is valuable, but the person
who will benefit from a "yes" should not also be the person who casts the deciding
vote. Naming these norms in advance keeps the hard meetings from turning on
personalities.

The single most important structural choice is to name **one accountable owner
per system**. Diffuse ownership is how systems drift, reviews lapse, and
incidents find no one ready to respond.

---

## 5. The artifact lifecycle

Governance artifacts are not paperwork for its own sake; each one answers a
question someone will eventually ask. The lifecycle runs from proposal to
retirement.

1. **Intake.** A proposed use case is described against a standard form (see
   `templates/ai-use-case-intake.md`): what problem, what data, what decision it
   influences, who is accountable. The committee decides whether to proceed and
   at what risk tier.
2. **Risk assessment.** A structured questionnaire produces a risk tier and a
   risk register mapped to NIST AI RMF subcategories, with recommended
   mitigations. Higher tiers trigger deeper requirements.
3. **Model card.** Before clinical use, the system's disclosures are documented —
   intended use, data, validation, performance by subgroup, limitations — using a
   schema aligned to the HTI-1 source attributes.
4. **Fairness evaluation.** For models affecting patients, performance is measured
   across demographic and clinically relevant subgroups, with disparities flagged
   and addressed. This is repeated, not done once.
5. **Deployment and monitoring.** The system goes live with a monitoring plan, a
   named owner, access controls, and a tested rollback procedure.
6. **Periodic review.** On a tier-dependent cadence, the committee re-examines the
   system: is it still performing, still fair, still needed?
7. **Retirement.** When a system is replaced or decommissioned, that decision and
   its rationale are recorded — an audit trail does not end at go-live.

The inventory ties these together: every artifact links back to a system record,
so at any moment the committee can see what exists, what is missing, and what is
overdue.

Two properties make the lifecycle trustworthy. First, **traceability**: the
reasoning behind each decision is written down and kept, so a reviewer a year
later can reconstruct *why* a system was approved at a given tier — not just that
it was. Storing the inventory in version control gives this almost for free: the
change history is the audit trail. Second, **proportionality**: the depth of each
stage should scale with risk. A low-risk operational tool does not need
prospective external validation; a high-acuity clinical model does. Spending equal
effort on every system either over-burdens the low-risk cases or under-scrutinizes
the dangerous ones. The risk tier assigned at intake is what makes the rest of the
lifecycle proportionate.

---

## 6. Common failure modes

Programs fail in predictable ways. Naming them is the cheapest prevention.

- **No inventory.** The most common and most consequential failure. You cannot
  govern what you cannot list. AI arrives embedded in EHR modules, imaging tools,
  and administrative software; without a deliberate inventory, much of it is
  ungoverned by default.
- **Model cards as one-time documents.** A model card written at launch and never
  updated becomes fiction as the model, the data, and the population drift. The
  card is a living disclosure, not a launch artifact.
- **Fairness evaluated once and never again.** Disparities emerge over time as
  populations and practice change. A single clean fairness report at deployment is
  evidence about the past, not a guarantee about the present.
- **No incident response plan.** When a model misbehaves, the questions —
  who decides to shut it off, who notifies affected clinicians, who investigates —
  must be answered in advance. Improvising during a safety event is how small
  problems become large ones.
- **Risk classification by vibes.** If how a system got its risk tier is opaque,
  the tier carries no authority. Classification should be a short, explicit,
  reviewable procedure (this toolkit makes the questionnaire and scoring rules
  plain data so non-developers can audit them).
- **Shadow AI.** Staff adopt consumer AI tools (general-purpose chatbots,
  transcription apps) for clinical or administrative work without review, often
  pasting PHI into systems that have no Business Associate Agreement. This is an
  inventory failure of a particularly hazardous kind, and it is best addressed
  with a clear, low-friction intake path and education — not just prohibition,
  which drives the usage further underground.
- **Governance theater.** A committee that approves everything it sees is not
  governing; it is rubber-stamping. The ability to say "not yet" or "not this
  way," and to make that stick, is what makes the rest real. A useful health
  check: when did the committee last decline or materially condition a proposal?
  If the answer is "never," the process may be decorative.

---

## 7. This toolkit as one implementation pattern

This repository is a *reference implementation* of the artifacts described above
— not a product, not a substitute for legal and compliance review, and not a
guarantee of regulatory compliance. It exists to make "what good looks like"
concrete and to give a small program working tools without a platform purchase.

It produces: a version-controlled **system inventory** with risk classification;
**model cards** in Markdown, HTML, and PDF aligned to the HTI-1 source
attributes; **risk assessments** with deterministic, auditable scoring mapped to
NIST AI RMF subcategories; **fairness reports** demonstrated on a transparent,
synthetic-data pipeline; and **LLM output audits** for PHI leakage, unsupported
claims, jailbreaks, tone, and citation validity. A dashboard ties the inventory
and artifacts together for the committee, and a board-report generator summarizes
the portfolio for executives.

Three honesty commitments are built in, because credibility is the whole point of
a governance tool. The synthetic-data fairness demo states plainly that it
demonstrates a *methodology* and validates no real model. The content "signature"
on generated PDFs is a tamper-evidence hash, not a cryptographic signature, and
says so. And the PII detection is open-source Presidio, which is credible but not
tuned for clinical narrative — a limitation documented where it matters, with a
pointer to production-grade alternatives.

The mappings in `docs/mappings/` connect each capability to specific sections of
the NIST AI RMF, the ONC HTI-1 source attributes, and the FDA GMLP principles,
and are reviewed against the source documents annually. Use them to see, for any
framework requirement, which artifact addresses it — and, just as importantly,
which requirements this toolkit does *not* address and you must handle by other
means.

It is fair to ask how you would know whether a governance program is *working*,
since the absence of a publicized AI disaster is weak evidence. A few signals are
more telling than activity counts: the share of production AI systems that have a
current model card, risk assessment, and fairness review (the compliance matrix in
this toolkit makes that visible at a glance); the number of systems overdue for
review trending toward zero; the existence of at least one proposal the committee
declined or materially changed; and a non-zero, calmly handled incident log,
because a program that never records an incident is usually not looking. None of
these is a guarantee of safety, but together they distinguish a program that
functions from one that merely exists.

Governance is ultimately a set of decisions made by accountable people who can
explain their reasoning. Tools make those decisions easier to make, record, and
revisit. They do not make the decisions, and they do not absorb the
accountability. Used that way — as scaffolding for human judgment rather than a
replacement for it — this toolkit can help a healthcare organization deploy AI
that is safer, fairer, and more transparent than it would otherwise be.

---

*This document is educational and does not constitute legal or compliance advice.
Regulatory citations are current as of mid-2026; verify against primary sources
before relying on them. See `docs/mappings/` for detailed framework
cross-references.*

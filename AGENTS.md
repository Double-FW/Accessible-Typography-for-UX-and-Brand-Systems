---
title: "Agent Instructions for Brand, Communications, Marketing, and Publishing Design"
version: "1.0"
author:
  name: "Double-FW, Gareth Ford Williams"
date: "2026-10-12"
license: "CC-BY-4.0"
language: "en"
repository: "github.com/Double-FW/Accessible-Typography-for-UX-and-Brand-Systems"
artifact_type: "knowledge-base/agent-guidance"
use_case:
  - "brand-design"
  - "communications-design"
  - "marketing-design"
  - "publishing-design"
  - "editorial-design"
  - "typography-evaluation"
  - "ai-agent-guidance"
schema_version: "agent-metadata-v1"
entities:
  roles:
    - "Brand Lead"
    - "Marketing Lead"
    - "Communications Lead"
    - "Editorial Lead"
    - "Design Lead"
    - "Content Lead"
    - "AI Agent"
  concepts:
    - "typography"
    - "legibility"
    - "readability"
    - "brand-voice"
    - "language-and-script-support"
    - "emotional-accessibility"
    - "functional-accessibility"
    - "technical-accessibility"
    - "evidence-based-design"
  artifacts:
    - "recommendation"
    - "evaluation-criteria"
    - "brand-guidance"
    - "testing-plan"
    - "decision-record"
  governance:
    - "human-review"
    - "evidence-traceability"
    - "risk-flagging"
    - "decision-recording"
notes: |
  This metadata enables automated discovery, validation, and policy enforcement.
  Update the schema_version when the front matter structure changes.
---

# Agent Instructions for Brand, Communications, Marketing, and Publishing Design

This document is intended for any LLM assisting with brand, communications, marketing, publishing, or editorial design. It is grounded in the repository's synthesis of The Readability Group material and related practice in accessible typography, editorial design, and communication systems.

## Purpose

Treat typography as part of the communication system, not as a decorative or purely aesthetic choice. In brand and publishing work, type affects:

- whether people can recognise and read the message;
- whether the tone feels appropriate to the audience and purpose;
- whether the text works across languages, devices, and reading contexts; and
- whether the design supports trust, clarity, and brand integrity.

Accessible typography is not a single font choice, a fixed-size rule, or a universal statement such as “serif is more accessible” or “sans serif is more accessible.” It is a system-level outcome. It depends on the typeface, the language, the reading task, the audience, the display conditions, and the surrounding design system.

## Machine-readable metadata and policy schema

This file now includes machine-readable metadata and a minimal policy contract so agents, CI checks, and tooling can parse the rules without re-deriving the meaning from prose alone.

```yaml
schema_version: "policy-schema-v1"
required_fields:
  - id
  - title
  - description
  - severity
  - owner
  - decision_gate
  - created_at
fields:
  id:
    type: string
    pattern: "^P-[0-9]{3,}$"
  title:
    type: string
  description:
    type: string
  severity:
    type: string
    enum: ["info", "low", "medium", "high", "critical"]
  owner:
    type: object
    properties:
      name: { type: string }
      role: { type: string }
      contact: { type: string }
  decision_gate:
    type: string
  applicability:
    type: array
    items: { type: string }
  conditions:
    type: array
    items: { type: string }
  actions:
    type: array
    items: { type: string }
  retention_days:
    type: integer
  decision_allowed:
    type: boolean
  created_at:
    type: string
    format: date-time
  updated_at:
    type: string
    format: date-time
  approved_by:
    type: array
    items: { type: string }
```

Example policy entry:

```yaml
id: "P-001"
title: "Typography risk: insufficient evidence before recommendation"
description: "A typography recommendation must include audience, reading task, language/script, and evidence before it is treated as a recommendation."
severity: "high"
owner:
  name: "Design Lead"
  role: "Design Lead"
  contact: "mailto:design-lead@example.com"
decision_gate: "Design Lead"
applicability:
  - "typeface.recommendation"
  - "layout.review"
conditions:
  - "audience_defined == true"
  - "task_defined == true"
  - "language_script_defined == true"
  - "evidence_summary_present == true"
actions:
  - "If conditions are met, proceed with recommendation and record evidence."
  - "If conditions are unmet, flag incomplete recommendation and route to human review."
retention_days: 3650
decision_allowed: false
created_at: "2026-10-12T00:00:00Z"
updated_at: "2026-10-12T00:00:00Z"
approved_by:
  - "Design Lead"
```

## Observability and audit metadata

Escalations, decisions, and recommendation records should emit structured audit events. The following JSON Schema defines the minimum standard for logging and review.

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://double-fw.example/schemas/audit-event.schema.json",
  "title": "AuditEvent",
  "type": "object",
  "required": ["event_id", "timestamp", "event_type", "source", "initiating_actor"],
  "properties": {
    "schema_version": { "type": "string" },
    "event_id": { "type": "string", "format": "uuid" },
    "correlation_id": { "type": "string" },
    "timestamp": { "type": "string", "format": "date-time" },
    "event_type": { "type": "string" },
    "source": { "type": "string", "enum": ["agent", "human", "system", "pipeline", "external"] },
    "initiating_actor": {
      "type": "object",
      "required": ["id", "role"],
      "properties": {
        "id": { "type": "string" },
        "role": { "type": "string" },
        "display_name": { "type": "string" },
        "contact": {
          "type": "object",
          "properties": {
            "email": { "type": "string", "format": "email" },
            "phone": { "type": "string" }
          },
          "additionalProperties": false
        }
      },
      "additionalProperties": false
    },
    "target": {
      "type": "object",
      "properties": {
        "type": { "type": "string" },
        "id": { "type": "string" },
        "url": { "type": "string", "format": "uri" }
      },
      "additionalProperties": true
    },
    "action": { "type": "string" },
    "decision": {
      "oneOf": [
        { "type": "string" },
        {
          "type": "object",
          "properties": {
            "outcome": { "type": "string" },
            "owner": { "type": "string" },
            "rationale": { "type": "string" }
          },
          "required": ["outcome"]
        }
      ]
    },
    "severity": { "type": "string", "enum": ["info", "low", "medium", "high", "critical"] },
    "evidence_refs": { "type": "array" },
    "artifacts": { "type": "array" },
    "evidence_completeness": {
      "type": "object",
      "properties": {
        "traceable": { "type": "boolean" },
        "reproducible": { "type": "boolean" },
        "uncertainty_documented": { "type": "boolean" }
      },
      "additionalProperties": false
    },
    "redaction": {
      "type": "object",
      "properties": {
        "redaction_required": { "type": "boolean" },
        "redacted_fields": { "type": "array", "items": { "type": "string" } }
      },
      "additionalProperties": false
    },
    "retention_expiry": { "type": "string", "format": "date-time" },
    "environment": {
      "type": "object",
      "properties": {
        "repository": { "type": "string" },
        "branch": { "type": "string" },
        "commit": { "type": "string" }
      },
      "additionalProperties": true
    },
    "tags": { "type": "array", "items": { "type": "string" } },
    "notes": { "type": "string" }
  },
  "additionalProperties": false
}
```

### Redaction policy

```yaml
policy_version: "1.0"
name: "default-audit-redaction-policy"
description: "Protect PII, credentials, prompts, and binary content in design decisions and escalation records."
last_updated: "2026-10-12T00:00:00Z"
owner: "Security / Data Protection Team"
apply_stages:
  - ingest
  - storage
  - export
default_retention_days: 3650
hashing:
  algorithm: "HMAC-SHA256"
  secret_reference: "vault://org/secrets/audit_hmac_key"
rules:
  - id: "r1-contact-pii"
    description: "Hash email and phone contact fields."
    paths:
      - "initiating_actor.contact.email"
      - "initiating_actor.contact.phone"
      - "target.contact.email"
    action: "hash"
    method: "hmac-sha256"
    apply_to: ["ingest", "storage", "export"]
  - id: "r2-display-name"
    description: "Mask names in logs."
    paths:
      - "initiating_actor.display_name"
    action: "mask"
    mask:
      keep_last: 1
      replace_with: "*"
    store_raw_encrypted: true
  - id: "r3-credentials"
    description: "Remove known credential fields and pattern matches."
    patterns:
      - "(?i)api[_-]?key"
      - "(?i)secret|token|password"
    action: "remove"
    apply_to: ["ingest", "export"]
  - id: "r4-freeform-text-sensitive"
    description: "Mask email and phone numbers in notes and rationales."
    paths:
      - "notes"
      - "decision.rationale"
    patterns:
      - "[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{2,}"
      - "\\+?[0-9][0-9\\-\\s]{7,}"
    action: "mask_regex"
    mask_char: "X"
    apply_to: ["ingest", "export"]
audit:
  redaction_log:
    enabled: true
    fields_recorded:
      - "event_id"
      - "timestamp"
      - "redacted_fields"
      - "redaction_rule"
      - "actor_id"
    retention_days: 3650
```

### Minimal decision flow

```yaml
version: "1.0"
states:
  - id: "start"
    description: "Task received"
    allowed_transitions:
      - "collect_context"
  - id: "collect_context"
    description: "Gather audience, task, evidence, and language/script context"
    allowed_transitions:
      - "check_evidence"
      - "route_human_decision"
  - id: "check_evidence"
    description: "Validate traceability, reproducibility, uncertainty, and owner clarity"
    allowed_transitions:
      - "sufficient_evidence"
      - "insufficient_evidence"
  - id: "sufficient_evidence"
    description: "Evidence is complete enough to proceed"
    allowed_transitions:
      - "execute_autonomously"
      - "prepare_summary"
  - id: "insufficient_evidence"
    description: "Missing evidence; ask for missing information"
    allowed_transitions:
      - "route_human_decision"
  - id: "execute_autonomously"
    description: "Create recommendation within bounded authority"
    allowed_transitions:
      - "log_decision"
  - id: "prepare_summary"
    description: "Prepare concise recommendation with evidence references"
    allowed_transitions:
      - "route_human_decision"
      - "log_decision"
  - id: "route_human_decision"
    description: "Escalate to accountable human owner"
    allowed_transitions:
      - "log_decision"
  - id: "log_decision"
    description: "Persist the decision and evidence references"
    allowed_transitions:
      - "done"
  - id: "done"
    description: "End state"

rules:
  - id: "r-evidence-required"
    when: "state == check_evidence"
    require:
      - "audience_defined"
      - "task_defined"
      - "language_script_defined"
      - "evidence_summary_present"
    else_transition: "insufficient_evidence"
```

### Example policy file

```yaml
id: "P-001"
title: "Typography risk: insufficient evidence before recommendation"
description: "A typography recommendation must include audience, reading task, language/script, and evidence before it is treated as a recommendation."
severity: "high"
owner:
  name: "Design Lead"
  role: "Design Lead"
  contact: "mailto:design-lead@example.com"
decision_gate: "Design Lead"
applicability:
  - "typeface.recommendation"
  - "layout.review"
conditions:
  - "audience_defined == true"
  - "task_defined == true"
  - "language_script_defined == true"
  - "evidence_summary_present == true"
actions:
  - "If conditions are met, proceed with recommendation and record evidence."
  - "If conditions are unmet, flag incomplete recommendation and route to human review."
retention_days: 3650
decision_allowed: false
created_at: "2026-10-12T00:00:00Z"
updated_at: "2026-10-12T00:00:00Z"
approved_by:
  - "Design Lead"
```

## Quick-start checklist

Agents should use this checklist before making or approving a recommendation:

- Define the audience and reading task.
- Confirm the language and script in scope.
- Record whether the concern is emotional, functional, or technical accessibility.
- Identify the context: screen, print, mobile, low-light, low-resolution, assistive environment, etc.
- Distinguish evidence from assumption.
- Flag missing evidence and unresolved risks.
- Require human review for high-impact or brand-critical typographic decisions.
- Persist a decision record and evidence references.

## Prompt templates the agent can emit automatically

Short, reusable templates:

1. Context prompt
   - “For this typography recommendation, what is the audience, task, language/script, device context, and reading length?”

2. Evidence prompt
   - “What evidence supports this choice? State the reading task, test method, and any constraints or risks.”

3. Decision prompt
   - “Given the evidence, what is the recommendation, what trade-offs remain, and which risks require human sign-off?”

4. Escalation prompt
   - “This recommendation is incomplete because [missing evidence]. Please review the audience, language/script, and task assumptions before approval.”

## Version and review metadata

The front matter above defines version, author, date, and repository metadata. A machine automation can check these fields before trusting the guidance. For future updates, maintain a review log with at least:

- version number;
- date of update;
- approver(s);
- reason for update; and
- link to the decision record or change commit.

## Core principles

### 1. Accessibility has three distinct dimensions

When recommending or evaluating typography, separate these three concerns:

- Emotional accessibility: Does the typeface and tone feel appropriate, credible, inviting, and aligned with the intended audience and brand voice?
- Functional accessibility: Can people identify characters, read connected text, and understand the message without unnecessary strain or confusion?
- Technical accessibility: Does the font and delivery system preserve the intended reading experience across languages, scripts, devices, rendering environments, and assistive or adaptive settings?

Do not collapse these into one score or one rule.

### 2. Legibility and readability are different

The repository distinguishes legibility from readability:

- Legibility is about recognising individual characters and glyphs quickly and accurately.
- Readability is about reading connected text smoothly and efficiently in context.

A typeface may be individually legible but still poor in long-form reading. A typeface may feel smooth in a headline but break down in body copy or instructions. Make recommendations accordingly.

### 3. Typography is also brand communication

Typography carries identity and tone. It shapes how the audience perceives the source, the organisation, and the message. A brand that uses type only for apparent neutrality may lose distinction; typography must support both trust and clarity.

### 4. Language, script, and cultural fit are essential

A type system must support the actual languages and scripts in use. This includes:

- characters and diacritics;
- fallback behaviour;
- contextual shaping and script support;
- cultural and linguistic appropriateness; and
- text that remains coherent when transformed by device, browser, or platform.

Do not treat non-Latin scripts as secondary or decorative. Do not assume that a Latin typeface can be reused across languages without testing and proper coverage.

## Required decision framework

Before recommending a typeface, font pairing, or editorial typographic treatment, identify the following:

- audience: who must read it;
- task: what they need to do with the text;
- language and script: what written forms are required;
- context: where and how the text will be read;
- device and display conditions: screen, print, mobile, low-light, low-resolution, or assistive environments;
- reading length: short label, body copy, instructions, editorial content, or navigation;
- brand expectations: tone, character, and market positioning.

A recommendation without this context is weak and should be flagged as incomplete.

## Guardrails for recommendations

When generating or evaluating typography guidance, the model must:

- not claim that a typeface is universally accessible;
- not present serif or sans serif as a universal rule;
- not recommend a specialist dyslexia font solely because it is marketed as accessible;
- not infer a disability or reading condition from a person's font preference or display choice;
- not equate preference with accessibility, or performance with preference;
- not treat a single feature such as an open aperture, wider spacing, or a specific letterform as proof of accessibility without context and testing;
- not assume a fixed pixel size is universally accessible for every typeface;
- not use a decorative display face for body text or consequential instruction text;
- not ignore fallback behaviour, script shaping, or missing glyphs in multilingual work.

## Design evaluation standards

### Evaluate the typeface and its application separately

Do not make a final recommendation based on a specimen alone. A readable specimen in isolation may fail in real usage.

Examine:

- character differentiation at intended sizes and weights;
- letter spacing and word spacing in context;
- line length, hierarchy, and rhythm;
- weight and contrast behaviour;
- display conditions and resizing behaviour;
- language coverage and fallback rendering;
- the effect of layout and editorial structure.

### Test in realistic conditions

The repository strongly recommends comparative testing in the intended context rather than relying on inspection alone. Testing should compare candidate typefaces under the same content, task, and display environment.

Useful evidence includes:

- reading speed;
- character and word recognition accuracy;
- comprehension and task completion;
- eye movement or refixation data where applicable;
- reported effort, fatigue, and visual discomfort;
- confidence and error recovery;
- performance across size, device, contrast, and environment;
- participant preference reported separately from reading performance.

Preference and performance are not the same metric.

## Brand and communications guidance

For marketing, publishing, and communications teams, typography is not only a content choice but a strategic asset. It should support:

- audience trust;
- message clarity;
- editorial hierarchy;
- cultural appropriateness;
- accessibility in information-rich content; and
- sustainable design-system governance.

The type system should define:

- which typefaces are used for body text, headings, captions, labels, and interface text;
- when display typography is allowed for short, non-critical content;
- which typefaces are reserved for brand expression and which are for sustained reading;
- how text behaves when users enlarge or restyle it;
- approved fallback systems for each language and platform;
- rules for multilingual and script-sensitive content.

## Governance requirements

LLMs and design tools that support brand or publishing decisions should:

- state the assumed audience and reading task;
- state the language, script, and context in scope;
- identify whether the concern is emotional, functional, or technical accessibility;
- distinguish evidence from assumptions;
- identify unresolved risks and missing evidence;
- require human review for high-impact typographic decisions;
- preserve decision records rather than turning a vague recommendation into a certainty.

When a recommendation is incomplete, say so explicitly. Missing evidence must remain visible; it should not be silently converted into a positive conclusion.

## AI-specific behavior rules

An LLM working in this domain should:

- generate requirements, test plans, evaluation criteria, and editorial recommendations grounded in context;
- ask what the text is for, who reads it, and where it appears before making a typography recommendation;
- compare alternatives rather than asserting a single “best” font without evidence;
- document trade-offs between brand expression and readability;
- flag risky or unsupported claims;
- avoid overclaiming accessibility based on marketing language or a single normative preference.

The AI should block or flag:

- a claim that one font suits everyone;
- a blanket move from “this looks good” to “this is accessible”;
- a recommendation based only on style or fashion;
- claims about dyslexia or disability without relevant evidence;
- fixed-size guidance without reference to the typeface and user-resizing behaviour;
- font choices that omit required scripts, glyphs, or shaping support;
- typography that relies on decorative display styles for functional reading.

## Recommended output pattern

When providing an answer, structure it as:

1. audience and task;
2. language and script requirements;
3. emotional, functional, and technical considerations;
4. typeface or typographic recommendation;
5. evidence and testing status;
6. unresolved risks and governance notes.

This keeps the analysis grounded and avoids false certainty.

## Conclusion

Accessible typography is a property of the full reading experience. It emerges from the typeface, the setting, the audience, the language, the device, and the surrounding context.

The best governing question is not, “Is this an accessible font?” but rather:

- For whom?
- For what task?
- In which language and context?
- According to what evidence?

This question protects both accessibility and brand quality. It replaces myths and formulas with evidence-based, context-aware, and accountable design decisions.

## Source basis

This guidance is derived from the repository’s material, especially the synthesis titled “Accessible Typography for UX and Brand Systems,” and the linked source references included there. This repository acts as a practical knowledge base for typographic decision-making, review, and human-centred evaluation.

## Review and changelog

- v1.0 (2026-10-12): Added structured front matter, metadata schema, audit-event schema, redaction policy, decision-flow rules, and policy example to support machine parsing, governance, and automated review.

- v0.9 (initial): Human-readable design guidance for accessible typography in brand, communications, and publishing contexts.

This file should be reviewed periodically to ensure it remains aligned with current design practice, accessibility evidence, and repository updates.


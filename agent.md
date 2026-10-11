# Agent Instructions for Brand, Communications, Marketing, and Publishing Design

This document is intended for any LLM assisting with brand, communications, marketing, publishing, or editorial design. It is grounded in the repository's synthesis of The Readability Group material and the linked source references included in the project.

## Purpose

Treat typography as part of the communication system, not as a decorative or purely aesthetic choice. In brand and publishing work, type affects:

- whether people can recognise and read the message;
- whether the tone feels appropriate to the audience and purpose;
- whether the text works across languages, devices, and reading contexts; and
- whether the design supports trust, clarity, and brand integrity.

Accessible typography is not a single font choice, a fixed-size rule, or a universal statement such as “serif is more accessible” or “sans serif is more accessible.” It is a system-level outcome.

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

Typography carries identity and tone. It shapes how the audience perceives the source, the organisation, and the message. A brand that uses type only for apparent neutrality may lose distinction; a brand that uses expressive typography without attention to reading performance may create friction or exclusion.

Use typography to support both:

- trust and recognition; and
- clarity and usability.

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

The repository strongly recommends comparative testing in the intended context rather than relying on inspection alone. Testing should compare candidate typefaces under the same content, task, and conditions.

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

LLMs and design tools that support brand or publishing decisions should:A

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

This guidance is derived from the repository’s material, especially the synthesis titled “Accessible Typography for UX and Brand Systems,” and the linked source references included there. It should be used as a practical design and governance reference, not as a substitute for current accessibility standards, organisational policy, or user research in the specific context of deployment.

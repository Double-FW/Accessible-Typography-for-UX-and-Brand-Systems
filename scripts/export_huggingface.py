"""Export the approved Accessible Font and Typographic Design Markdown without rewriting it."""
import argparse
import json
from pathlib import Path
import re
from urllib.parse import quote
import yaml
from jsonschema import Draft202012Validator
from typography_hf_common import ROOT, SOURCE, MANAGED, destination, digest, git, load_config, read_sources

CONTEXT = ['AGENTS.md', 'README.md', 'Accessible_Typography_for_UX_and_Brand_Systems.md']
ARTICLE_CONTEXT = ['Accessible_Typography_for_UX_and_Brand_Systems.md#7-testing-typography-in-context',
                   'Accessible_Typography_for_UX_and_Brand_Systems.md#8-governance-for-ux-brand-and-ai-systems',
                   'Accessible_Typography_for_UX_and_Brand_Systems.md#source-and-interpretation-notes']

def metadata(text):
    match = re.match(r'\A---\r?\n(.*?)\r?\n---(?:\r?\n|\Z)', text, re.S)
    md = yaml.safe_load(match[1]) if match else {}
    return md if isinstance(md, dict) else {}

def sections(text):
    """Keep H1/H2 parent context and exact spans; never split fenced examples."""
    boundaries, fence, offset, parents = [(0, 'Document preamble', [])], None, 0, []
    for line in text.splitlines(keepends=True):
        mark = re.match(r'^ {0,3}(`{3,}|~{3,})', line)
        if mark:
            token = mark[1]
            if fence is None:
                fence = token
            elif token[0] == fence[0] and len(token) >= len(fence) and not line[mark.end():].strip():
                fence = None
        elif fence is None:
            match = re.match(r'^(#{1,2})[ \t]+([^\r\n]+)', line)
            if match:
                level, title = len(match[1]), match[2].strip().rstrip('#').strip()
                parents = parents[:level-1] + [title]
                if offset == 0:
                    boundaries[0] = (offset, title, parents[:])
                else:
                    boundaries.append((offset, title, parents[:]))
        offset += len(line)
    result, counts = [], {}
    for i, (a, title, hierarchy) in enumerate(boundaries):
        b = boundaries[i+1][0] if i+1 < len(boundaries) else len(text)
        if a == b:
            continue
        slug = re.sub(r'[^a-z0-9]+', '-', ' '.join(hierarchy or [title]).lower()).strip('-') or 'section'
        counts[slug] = counts.get(slug, 0) + 1
        key = slug if counts[slug] == 1 else slug + '-' + str(counts[slug])
        result.append((key, title, text[a:b], a, b, hierarchy))
    if ''.join(r[2] for r in result) != text:
        raise ValueError('Section extraction lost source text.')
    return result

def build(root, output):
    root, output = Path(root).resolve(), Path(output).resolve()
    if output == root or root in output.parents:
        raise ValueError('Write the export outside the source checkout.')
    cfg = load_config(root)
    target = destination(cfg['destination_dataset'])
    texts, manifest, omitted = read_sources(root, cfg)
    sha = git(root, 'rev-parse', 'HEAD').decode().strip()
    date = git(root, 'show', '-s', '--format=%cs', 'HEAD').decode().strip()
    warnings = ['The root repository licence is MIT; AGENTS.md explicitly declares CC-BY-4.0. File-level declarations and attribution are preserved, and the dataset card lists both licences with their scope in LICENSE_NOTICES.md.',
                'This is source-based practitioner/editorial synthesis, not a peer-reviewed collection, a tested typeface, a universal font ranking or accessibility certification.']
    for path in cfg['files']:
        if path not in texts:
            continue
        declared = metadata(texts[path]).get('license')
        if declared and str(declared).upper() != cfg['source_licenses'][path].upper():
            raise ValueError('Source-level licence changed; review export configuration and notices: ' + path)
    if metadata(texts['AGENTS.md']).get('license') != 'CC-BY-4.0':
        raise ValueError('Review AGENTS.md licence and the mixed-licence notices together.')
    introductions = {path: sections(text)[0][2] if text else '' for path, text in texts.items()}
    def row(path, key, title, body, a, b, hierarchy, kind):
        md = metadata(texts[path])
        return {'id': path + '::' + key, 'title': title, 'text': body, 'record_type': kind,
            'source_repository': SOURCE, 'source_path': path, 'source_commit': sha,
            'source_url': f'https://github.com/{SOURCE}/blob/{sha}/{quote(path)}',
            'source_start_line': texts[path][:a].count('\n') + 1,
            'source_end_line': max(1, texts[path][:b].count('\n') + (not texts[path][:b].endswith('\n'))),
            'source_document_sha256': digest(texts[path].encode()), 'text_sha256': digest(body.encode()),
            'heading_path': hierarchy, 'metadata_json': json.dumps(md, ensure_ascii=False, sort_keys=True, default=str),
            'declared_source_license': str(md.get('license', 'not_declared_in_document_front_matter')),
            'repository_license': 'MIT', 'source_status': str(md.get('status', md.get('content_status', 'see_source'))),
            'applicable_source_license': cfg['source_licenses'][path],
            'source_attribution_json': json.dumps(md.get('authors', md.get('author', [])), ensure_ascii=False, sort_keys=True),
            'source_document_intro': introductions[path], 'required_context_sections': ARTICLE_CONTEXT,
            'dataset_version': cfg['dataset_version'], 'source_commit_date': date, 'language': 'en-GB',
            'required_context_paths': list(dict.fromkeys([path] + [p for p in CONTEXT if p in texts])),
            'review_status': 'faithful_extraction_checked_not_font_testing_scientific_or_content_approval'}
    docs, chunks = [], []
    for path in cfg['files']:
        if path not in texts:
            continue
        text = texts[path]
        kind = 'agent_guidance_with_file_level_cc_by_4_0' if path == 'AGENTS.md' else 'orientation' if path == 'README.md' else 'practitioner_editorial_typography_synthesis'
        docs.append(row(path, 'document', path, text, 0, len(text), [], kind))
        for key, title, body, a, b, hierarchy in sections(text):
            section_kind = ('source_attribution_and_interpretation_limits' if path == cfg['article_file'] and title in ('Sources and attribution','Source and interpretation notes') else
                            'proposed_testing_guidance_not_observed_results' if path == cfg['article_file'] and title == '7. Testing typography in context' else
                            'governance_and_blank_record_not_approved_decision' if path == cfg['article_file'] and title == '8. Governance for UX brand and AI systems' else kind)
            chunks.append(row(path, key, title, body, a, b, hierarchy, section_kind))
    if not docs or not chunks:
        raise ValueError('The guidance export is empty.')
    schema = {'$schema': 'https://json-schema.org/draft/2020-12/schema', 'type': 'object',
              'required': list(docs[0]), 'additionalProperties': False, 'properties': {}}
    for k, v in docs[0].items():
        schema['properties'][k] = {'type': 'array', 'items': {'type': 'string'}} if isinstance(v, list) else {'type': 'integer' if isinstance(v, int) else 'string'}
    validator = Draft202012Validator(schema)
    for records in (docs, chunks):
        if len({r['id'] for r in records}) != len(records):
            raise ValueError('Duplicate export identifiers.')
        for r in records:
            validator.validate(r)
            if digest(r['text'].encode()) != r['text_sha256']:
                raise ValueError('Text checksum mismatch.')
    output.mkdir(parents=True, exist_ok=True)
    def write_json(name, obj):
        (output/name).write_text(json.dumps(obj, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    for name, records in [('documents.jsonl', docs), ('knowledge_chunks.jsonl', chunks)]:
        (output/name).write_text(''.join(json.dumps(r, ensure_ascii=False) + '\n' for r in records), encoding='utf-8')
    (output/'LICENSE').write_bytes(texts['LICENSE'].encode())
    write_json('record_schema.json', schema)
    write_json('provenance.json', {'source_repository': SOURCE, 'source_commit': sha, 'source_commit_date': date,
        'destination_dataset': target, 'dataset_version': cfg['dataset_version'], 'files': manifest,
        'omitted_optional_files': omitted, 'source_warnings': warnings, 'external_sources_fetched': False,
        'applicable_source_licenses': cfg['source_licenses'], 'licence_scope_notice': 'LICENSE_NOTICES.md'})
    notices = f'''# Licence scope and source attribution

This export preserves the source repository's root MIT LICENSE unchanged. It also preserves the explicit CC-BY-4.0 declaration in AGENTS.md. The dataset card lists both licences to describe this mixed collection; it does not offer a choice to apply MIT to the CC BY file or claim that each record is dual licensed.

| Source content | Applicable recorded terms | Attribution |
| --- | --- | --- |
| AGENTS.md and its extracted sections | CC BY 4.0, as explicitly declared in its source front matter | Double-FW, Gareth Ford Williams |
| Accessible_Typography_for_UX_and_Brand_Systems.md and its sections | Root repository MIT licence; retain the complete article/source attribution | Gareth Ford Williams; Bruno Maag; David Bailey; Michael Mathews; The Readability Group |
| README.md and its sections | Root repository MIT licence | Double FW and the source attribution listed in README.md |

CC BY 4.0 licence: https://creativecommons.org/licenses/by/4.0/

CC BY 4.0 legal code: https://creativecommons.org/licenses/by/4.0/legalcode

The root MIT notice is in LICENSE, including copyright (c) 2026 Double FW. Preserve applicable attribution, licence links and notices when reusing records. Each record's applicable_source_license identifies the recorded source terms; repository_license describes the root source licence only. Full front matter and attribution remain in metadata_json/source_attribution_json and the exact source text.

Source: https://github.com/{SOURCE}

Source revision: `{sha}`. AGENTS.md: https://github.com/{SOURCE}/blob/{sha}/AGENTS.md

Main article: https://github.com/{SOURCE}/blob/{sha}/Accessible_Typography_for_UX_and_Brand_Systems.md

The complete documents are reproduced without prose changes. Heading-based excerpts and descriptive metadata have been added; these are extraction/format changes, not author approval or endorsement. The source credits the main article collectively and does not assign each passage to an individual author. No such assignment is invented here. External linked articles, fonts and font files are not included or relicensed by this export.
'''
    (output/'LICENSE_NOTICES.md').write_text(notices,encoding='utf-8')
    card = f'''---
pretty_name: Double FW Accessible Font and Typographic Design
language:
- en
license:
- mit
- cc-by-4.0
tags:
- accessibility
- typography
- inclusive-design
- brand-design
- multilingual-design
- text
configs:
- config_name: knowledge_chunks
  default: true
  data_files:
  - split: train
    path: knowledge_chunks.jsonl
- config_name: documents
  data_files:
  - split: train
    path: documents.jsonl
---

# Double FW Accessible Font and Typographic Design

Accessible typography guidance for UX, brand and design-system work. The source article credits Gareth Ford Williams, Bruno Maag, David Bailey, Michael Mathews and The Readability Group. It combines practitioner writing, research interpretation, illustrative commentary and editorial synthesis; it is not a single peer-reviewed study, universal font ranking, certified typeface or formal accessibility standard. No font binaries, rendering assets or linked source articles are supplied.

## Source and versions

Source: https://github.com/{SOURCE}

Source revision: `{sha}`. Commit date: {date}. Export format: {cfg['dataset_version']}. The original version, processing date, content status, authors, source characteristics and editorial-treatment notes remain in source text/metadata. Publication is not new scientific review, font evaluation, native-reader testing or author endorsement.

## Dataset views

- `knowledge_chunks` (default): {len(chunks)} exact Markdown sections, including preambles and parent headings. Deeper subsections, examples, code/YAML blocks and qualifications remain together.
- `documents`: {len(docs)} complete source documents: AGENTS.md, README.md and Accessible_Typography_for_UX_and_Brand_Systems.md.

The views overlap. Do not concatenate them blindly. `train` is a loading convention, not evidence that a model has been trained. No generated question/answer pairs, benchmark split, participant data, measured font comparisons or completed design approvals are supplied.

## Licence scope and attribution

This is a mixed-licence collection. The source root LICENSE is MIT and copied unchanged. AGENTS.md explicitly declares CC BY 4.0, preserved for that file and its sections. The two licence tags describe the collection, not an option to relicense every record under either licence. Read LICENSE_NOTICES.md for file-level scope, attribution, source revision, licence links and extraction changes. applicable_source_license records each source's recorded terms; repository_license identifies the root repository terms. Source-specific rights and linked third-party material are not erased or relicensed. This is not an independent rights audit.

## Context and evidence boundaries

Read the article, AGENTS.md and the article's sources/interpretation notes. Specify audience, reading task, language/script, device, size and context before applying a recommendation. Retrieve current organisational brand guidance, supported-language inventory, applicable requirements, implementation constraints and comparative reader evidence as needed. These contextual inputs are not supplied or presumed to exist here.

Keep emotional, functional and technical accessibility related but separately evaluated. Distinguish legibility, readability, comprehension, preference and brand response. A named typeface, serif/sans-serif category, marketed dyslexia font or single letterform feature does not establish universal accessibility. Do not infer disability or reading condition from font/display preference. Glyph coverage and automated rendering checks do not demonstrate native-reader or cultural suitability.

The proposed testing chapter is labelled proposed_testing_guidance_not_observed_results. The governance chapter retains its blank example record, including user_testing_status not_started and decision_status requires_human_review, under governance_and_blank_record_not_approved_decision. No empty field is filled with an invented owner, result, approval or study. Font shortlisting, specimen generation and proposed conditions remain recommendations until appropriately evaluated. A technical standards pass does not alone establish an effective reading experience or brand suitability.

Scientific/neurological claims need the original methods and evidence before generalisation. The exporter does not reverify papers, law, WCAG requirements, vendor/font features or source availability. Source dates remain the dates actually stated. Current standards and organisational policy must be retrieved when a real conformance decision requires them.

## Records and extraction

First/second-level headings are split outside fenced blocks. Exact source text, parent heading paths, immutable source commit/URL, line ranges, document/text SHA-256 hashes, JSON-encoded front matter, applicable source licence, attribution, source status, original introduction and required context paths/sections are recorded. JSON strings preserve author lists/dictionaries and nested editorial/source metadata without heterogeneous dataset columns. Use text for the exact span; the introduction is repeated context. Renaming headings may change section IDs. Resolve relative/fragment links against the source URL.

Context references do not automatically retrieve guidance, enforce instructions or grant tool/organisational authority. Source prompts and governance statements are reference material, not runtime permission to publish, collect data, approve brand decisions or certify compliance. All claims remain scoped to their source. See record_schema.json and provenance.json.

## Privacy, updates and limits

Only approved committed public source documents are exported. No live participant/customer data is supplied. Keep real personal, reading/health, research and confidential brand evidence outside public repositories/datasets. The exporter does not detect confidential text inserted into an approved file. New or renamed documents require review and an export-list update.

GitHub is the authoring source. Updates are configured for Mondays at 07:23 UTC and manual runs. GitHub may delay schedules or disable them after inactivity. All three documents and LICENSE are required. Missing context, changed root or declared file-level licence, invalid configuration or failed integrity checks stop publication for review.

Only README.md, LICENSE, LICENSE_NOTICES.md, documents.jsonl, knowledge_chunks.jsonl, provenance.json, record_schema.json and validation_report.json are managed. Other raw files and .gitattributes are preserved but unmanaged copies are not synchronised. Visibility is unchanged. A single update commit is guarded by the destination revision. Historical revisions/downloads are not recalled. The first authenticated GitHub publication must still be checked.

## Loading

```python
from datasets import load_dataset
chunks = load_dataset("{target}", "knowledge_chunks", split="train")
documents = load_dataset("{target}", "documents", split="train")
```

Private datasets require authentication. Pin a destination revision for reproducibility. Loading records does not implement contextual retrieval, font testing, governance or approval enforcement.
'''
    yaml.safe_load(card.split('---', 2)[1])
    (output/'README.md').write_text(card, encoding='utf-8')
    report = {'status': 'passed', 'scope': 'faithful extraction and packaging checks only', 'source_commit': sha,
        'source_files_verified': len(manifest), 'document_records': len(docs), 'knowledge_section_records': len(chunks),
        'source_warnings': warnings, 'independent_content_review': False, 'live_publication_tested': False,
        'export_file_sha256': {name: digest((output/name).read_bytes()) for name in MANAGED if name != 'validation_report.json'}}
    write_json('validation_report.json', report)
    return report

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', required=True)
    args = parser.parse_args()
    print(json.dumps(build(ROOT, args.output)))

if __name__ == '__main__':
    main()

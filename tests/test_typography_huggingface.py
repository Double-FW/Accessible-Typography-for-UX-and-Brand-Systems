"""Faithful export and guarded publication tests with no live dataset writes."""
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import Mock, patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'scripts'))
import typography_hf_common as common
import export_huggingface as exporter
import publish_huggingface as publisher

class TypographySyncTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.base = Path(self.tmp.name)
        self.repo = self.base/'repo'
        self.repo.mkdir()
        cfg = common.load_config(ROOT)
        for name in cfg['files'] + ['LICENSE']:
            result = subprocess.run(['git', '-C', str(ROOT), 'show', 'HEAD:' + name], capture_output=True)
            if result.returncode:
                if name in cfg['required_files']: self.fail('Required source absent: ' + name)
                continue
            (self.repo/name).write_bytes(result.stdout)
        shutil.copytree(ROOT/'huggingface', self.repo/'huggingface')
        self.git('init', '-q'); self.git('config', 'user.name', 'Test fixture')
        self.git('config', 'user.email', 'test@example.invalid'); self.commit()
        self.out = self.base/'export'
    def git(self, *args): return common.git(self.repo, *args)
    def commit(self):
        self.git('add', '.'); self.git('commit', '--allow-empty', '-qm', 'Fixture')
    def build(self): return exporter.build(self.repo, self.out)
    def rows(self, name): return [json.loads(x) for x in (self.out/name).read_text().splitlines()]

    def test_documents_and_sections_reproduce_exact_source_bytes(self):
        self.build()
        for row in self.rows('documents.jsonl'):
            self.assertEqual(row['text'].encode(), self.git('show', 'HEAD:' + row['source_path']))
            joined = ''.join(x['text'] for x in self.rows('knowledge_chunks.jsonl') if x['source_path'] == row['source_path'])
            self.assertEqual(joined, row['text'])

    def test_metadata_licence_warnings_and_status_remain_visible(self):
        report = self.build()
        agent = next(x for x in self.rows('documents.jsonl') if x['source_path'] == 'AGENTS.md')
        original = exporter.metadata(self.git('show', 'HEAD:AGENTS.md').decode())
        self.assertEqual(agent['declared_source_license'], str(original.get('license', 'not_declared_in_document_front_matter')))
        self.assertEqual(agent['source_status'], str(original.get('status', 'see_source')))
        if original.get('license') == 'NOASSERTION':
            self.assertTrue(any('NOASSERTION' in w for w in report['source_warnings']))
        self.assertEqual((self.out/'LICENSE').read_bytes(), self.git('show', 'HEAD:LICENSE'))

    def test_headings_fences_and_parent_context(self):
        text = '---\nstatus: draft\n---\n# Parent\n## One\n```md\n## Example only\n```\n# Second parent\n## Two\nBody\n'
        parts = exporter.sections(text)
        self.assertEqual(''.join(x[2] for x in parts), text)
        self.assertEqual(len(parts), 5)
        self.assertEqual(parts[-1][-1], ['Second parent', 'Two'])
        self.assertIn('Example only', parts[2][2])

    def test_output_is_repeatable(self):
        self.build(); before = {p.name:p.read_bytes() for p in self.out.iterdir()}
        self.build(); self.assertEqual(before, {p.name:p.read_bytes() for p in self.out.iterdir()})

    def test_new_unapproved_and_untracked_material_stays_out(self):
        (self.repo/'not-approved.md').write_text('Not approved'); self.commit()
        (self.repo/'private-notes.md').write_text('Untracked private')
        self.build()
        data = (self.out/'documents.jsonl').read_text()
        self.assertNotIn('not-approved.md', data); self.assertNotIn('Untracked private', data)

    def test_changed_file_level_licence_blocks_export(self):
        path=self.repo/'AGENTS.md'
        path.write_text(path.read_text().replace('license: "MIT"','license: "CC-BY-4.0"'))
        self.commit()
        with self.assertRaisesRegex(ValueError,'licence changed'): self.build()

    def test_missing_required_and_changed_licence_block(self):
        (self.repo/'AGENTS.md').unlink(); self.commit()
        with self.assertRaises(ValueError): self.build()
        self.git('reset', '--hard', 'HEAD~1')
        (self.repo/'LICENSE').write_text('Unapproved new terms'); self.commit()
        with self.assertRaises(ValueError): self.build()

    def test_wrong_source_or_destination_and_output_location_block(self):
        for target in ('', 'GarethFW/accessible-chatbots', 'GarethFW/AVMSD_delivery_and_evidence_repository'):
            with self.assertRaises(ValueError): common.destination(target)
        cfg_path = self.repo/'huggingface/export-config.json'
        cfg = json.loads(cfg_path.read_text()); cfg['source_repository'] = 'Someone/Else'; cfg_path.write_text(json.dumps(cfg))
        with self.assertRaises(ValueError): self.build()
        with self.assertRaises(ValueError): exporter.build(self.repo, self.repo/'export')

    def test_private_source_blocked(self):
        response = Mock(); response.read.return_value = json.dumps({'full_name':common.SOURCE, 'private':True, 'visibility':'private'}).encode()
        response.__enter__ = Mock(return_value=response); response.__exit__ = Mock(return_value=False)
        with patch.object(common.urllib.request, 'urlopen', return_value=response):
            with self.assertRaises(ValueError): common.public_source()

    def test_noop_first_publish_and_destination_protection(self):
        self.build(); api=Mock(); api.repo_info.return_value.sha='read-destination-revision'
        def same(**kw): return str(self.out/kw['filename'])
        result=publisher.publish(self.out, 'fake-test-token', api=api, download=same, check_public=lambda:None)
        self.assertIn('No changes', result); api.create_commit.assert_not_called()
        from huggingface_hub.errors import EntryNotFoundError
        def empty(**kw): raise EntryNotFoundError('Missing test file')
        publisher.publish(self.out, 'fake-test-token', api=api, download=empty, check_public=lambda:None)
        args=api.create_commit.call_args.kwargs
        self.assertEqual(args['repo_id'], 'GarethFW/Accessible_Font_And_Typographic_Design')
        self.assertEqual(args['parent_commit'], 'read-destination-revision')
        self.assertEqual({x.path_in_repo for x in args['operations']}, set(common.MANAGED))
        self.assertNotIn('.gitattributes', {x.path_in_repo for x in args['operations']})
        api.create_repo.assert_not_called(); api.update_repo_settings.assert_not_called()

    def test_missing_token_tampering_and_foreign_provenance_block(self):
        self.build(); api=Mock(); api.repo_info.return_value.sha='head'
        with self.assertRaises(ValueError): publisher.publish(self.out, '', check_public=lambda:None)
        foreign=self.base/'foreign.json'; foreign.write_text(json.dumps({'source_repository':'Another/Source'}))
        def wrong(**kw): return str(foreign if kw['filename']=='provenance.json' else self.out/kw['filename'])
        with self.assertRaises(ValueError): publisher.publish(self.out, 'fake', api=api, download=wrong, check_public=lambda:None)
        (self.out/'README.md').write_text('Tampered export')
        with self.assertRaises(ValueError): publisher.publish(self.out, 'fake', api=api, download=wrong, check_public=lambda:None)

    def test_change_report_distinguishes_removals_and_revision_only_changes(self):
        delta=publisher.changes_between([{'id':'removed','text':'x'}, {'id':'same','text':'x','source_commit':'old'}],
                                        [{'id':'added','text':'y'}, {'id':'same','text':'x','source_commit':'new'}])
        self.assertEqual(delta, {'added':['added'], 'removed':['removed'], 'updated':[]})

    def test_workflow_matches_this_repository_and_preset_destination(self):
        import yaml
        workflow=yaml.load((ROOT/'.github/workflows/huggingface-sync.yml').read_text(), Loader=yaml.BaseLoader)
        self.assertIn("github.repository == 'Double-FW/Accessible-Typography-for-UX-and-Brand-Systems'", workflow['jobs']['publish']['if'])
        self.assertIn('workflow_dispatch', workflow['on'])
        self.assertEqual(common.load_config(ROOT)['destination_dataset'], 'GarethFW/Accessible_Font_And_Typographic_Design')

    def test_current_mit_licence_and_source_attribution_are_preserved(self):
        import yaml
        from huggingface_hub import DatasetCardData
        self.build();docs={x['source_path']:x for x in self.rows('documents.jsonl')}
        self.assertEqual(docs['AGENTS.md']['applicable_source_license'],'MIT')
        article=docs['Accessible_Typography_for_UX_and_Brand_Systems.md']
        self.assertEqual(article['applicable_source_license'],'MIT')
        original=exporter.metadata(article['text'])
        self.assertEqual(json.loads(article['source_attribution_json']),original['authors'])
        self.assertEqual(json.loads(article['metadata_json'])['editorial_treatment'],original['editorial_treatment'])
        card=yaml.safe_load((self.out/'README.md').read_text().split('---',2)[1])
        self.assertEqual(card['license'],'mit')
        DatasetCardData(**card)
        notice=(self.out/'LICENSE_NOTICES.md').read_text()
        for author in original['authors']: self.assertIn(author,notice)
        self.assertIn('MIT',notice)
        self.assertNotIn('CC-BY-4.0',notice)
        self.assertTrue(all(x['applicable_source_license']=='MIT' for x in docs.values()))

    def test_blank_governance_record_and_proposed_tests_are_not_results(self):
        import yaml
        self.build();rows=self.rows('knowledge_chunks.jsonl')
        governance=next(x for x in rows if x['record_type']=='governance_and_blank_record_not_approved_decision')
        text=governance['text'];block=text.split('```yaml',1)[1].split('```',1)[0]
        record=yaml.safe_load(block)['typography_decision']
        self.assertEqual(record['user_testing_status'],'not_started')
        self.assertEqual(record['decision_status'],'requires_human_review')
        self.assertEqual(record['approving_roles'],[])
        self.assertTrue(any(x['record_type']=='proposed_testing_guidance_not_observed_results' for x in rows))
        self.assertTrue(any(x['record_type']=='source_attribution_and_interpretation_limits' for x in rows))

    def test_complex_front_matter_context_and_evidence_limits_remain_intact(self):
        self.build();docs={x['source_path']:x for x in self.rows('documents.jsonl')}
        article=docs['Accessible_Typography_for_UX_and_Brand_Systems.md']
        metadata=json.loads(article['metadata_json'])
        self.assertFalse(metadata['source_characteristics']['normative_standard'])
        self.assertFalse(metadata['source_characteristics']['independently_peer_reviewed_as_a_collection'])
        self.assertEqual(article['source_status'],metadata['content_status'])
        self.assertTrue(all('Accessible_Typography_for_UX_and_Brand_Systems.md' in x['required_context_paths'] for x in docs.values()))
        self.assertFalse(json.loads((self.out/'provenance.json').read_text())['external_sources_fetched'])

if __name__ == '__main__': unittest.main()

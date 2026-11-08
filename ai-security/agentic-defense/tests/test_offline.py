import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from agente_triage import build_draft, condition_from_details, uncorrelated_events


class OfflineTests(unittest.TestCase):
    def test_missing_threshold_is_declared_not_invented(self):
        details = dict(entropy_rate_bits=1.2, markov_cross_entropy_bits=0.3)
        out = condition_from_details(details, rule_thresholds=None)
        self.assertEqual(out['A']['status'], 'soglia non ancora compilata')
        self.assertEqual(out['B']['status'], 'soglia non ancora compilata')

    def test_missing_field_is_declared(self):
        out = condition_from_details({}, rule_thresholds=dict(A=1.0, B=1.0))
        self.assertIn('assente', out['A']['status'])

    def test_threshold_comparison_uses_only_given_values(self):
        out = condition_from_details(dict(entropy_rate_bits=0.5, markov_cross_entropy_bits=2.0),
                                      rule_thresholds=dict(A=1.0, B=1.0))
        self.assertEqual(out['A']['status'], 'sotto soglia')
        self.assertEqual(out['B']['status'], 'sopra soglia')

    def test_uncorrelated_events_counts_missing_command_ids(self):
        correlated = dict(events=[dict(command_ids=[1]), dict(command_ids=[]), dict()])
        self.assertEqual(uncorrelated_events(correlated), 2)

    def test_draft_never_invents_a_threshold_value(self):
        draft = build_draft('esempio', dict(entropy_rate_bits=1.0, markov_cross_entropy_bits=1.0),
                             dict(events=[]), rule_thresholds=None)
        self.assertIn('soglia non ancora compilata', draft)
        self.assertNotIn('AI', draft)
        self.assertNotIn('umano', draft.split('Letto dall')[1] if 'Letto dall' in draft else '')


if __name__ == '__main__':
    unittest.main()

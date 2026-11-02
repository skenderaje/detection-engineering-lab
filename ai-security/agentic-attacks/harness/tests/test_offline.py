import base64
import json
import math
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from common import save
from session import execute
from export import correlate
from analyze import cce, entropy, normalize, quantize, model, score


class FakeGuest:
    def __init__(self):
        self.calls = []

    def upload(self, machine, local, remote):
        self.calls.append(('upload', machine))
        compile(Path(local).read_text(), '<guest-wrapper>', 'exec')

    def run_linux(self, machine, command):
        self.calls.append(('run', machine))

    def download(self, machine, remote, local):
        self.calls.append(('download', machine))
        save(local, dict(started_at='2026-01-01T00:00:00+00:00',
             ended_at='2026-01-01T00:00:01+00:00', monotonic_start_ns=1,
             monotonic_end_ns=2, status='complete', exit_code=7,
             stdout_b64=base64.b64encode(b'\xffout').decode(),
             stderr_b64=base64.b64encode(b'err').decode()))


class OfflineTests(unittest.TestCase):
    def test_result_is_guest_exit_not_vmrun(self):
        with tempfile.TemporaryDirectory() as d:
            g = FakeGuest()
            self.assertTrue(execute(g, Path(d), 'echo example; exit 7'))
            r = json.loads(next(Path(d).glob('*.json')).read_text())
            self.assertEqual(r['exit_code'], 7)
            self.assertEqual(base64.b64decode(r['stdout_b64']), b'\xffout')
            self.assertEqual(g.calls, [('upload','TEST01'),('run','TEST01'),('download','TEST01')])

    def test_transport_error_not_command_failure(self):
        class Failed(FakeGuest):
            def run_linux(self, *args):
                raise RuntimeError('secret must not enter log')
        with tempfile.TemporaryDirectory() as d:
            self.assertFalse(execute(Failed(), Path(d), 'example'))
            text = next(Path(d).glob('*.json')).read_text()
            self.assertNotIn('secret', text)
            self.assertEqual(json.loads(text)['status'], 'transport_error')

    def test_temporal_candidates_are_many_to_many(self):
        commands = [dict(id=str(n),started_at='2026-01-01T00:00:00+00:00',
                        ended_at='2026-01-01T00:00:02+00:00') for n in range(2)]
        rows = [dict(event_time='2026-01-01T00:00:01Z'), dict(event_time='2026-01-01T00:00:09Z')]
        result = correlate(rows, commands, 0)
        self.assertEqual(result[0]['candidate_command_ids'], ['0','1'])
        self.assertEqual(result[1]['candidate_command_ids'], [])

    def test_entropy_and_order(self):
        self.assertEqual(entropy([0]*20), 0)
        self.assertAlmostEqual(entropy([0,1]*100), 1)
        rate, curve = cce([0,1]*100, 8)
        self.assertAlmostEqual(rate, 0)
        self.assertTrue(curve)
        self.assertTrue(math.isnan(cce([0], 10)[0]))

    def test_duplicate_quantiles_do_not_split_ties(self):
        symbols, edges = quantize([2]*30, 5)
        self.assertEqual(set(symbols), {0})
        self.assertEqual(edges, [2.0])

    def test_normalization_and_unseen(self):
        self.assertEqual(normalize('cat file1.c'), 'cat <ARG>')
        self.assertEqual(normalize('cat file2.c'), 'cat <ARG>')
        self.assertEqual(normalize('cat a | grep b'), 'cat <ARG> | grep <ARG>')
        baseline = ['a','b']*20
        loss, unseen = score(['x','y'], model(baseline), baseline, 1)
        self.assertTrue(math.isfinite(loss))
        self.assertEqual(unseen, 1)

    def test_three_scripts_offline(self):
        scripts = Path(__file__).resolve().parents[1]
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for name, label in [('train','human'), ('human','human'), ('agent','agent')]:
                folder = root / name
                subprocess.run([sys.executable, str(scripts/'session.py'), 'init', str(folder),
                                '--label', label, '--task', 'synthetic-only'], check=True, capture_output=True)
                for i in range(12):
                    save(folder / f'{i:02}.json', dict(id=str(i), submitted_at=f'2026-01-01T00:00:{i:02}+00:00',
                         started_at=f'2026-01-01T00:00:{i:02}+00:00', ended_at=f'2026-01-01T00:00:{i:02}.500000+00:00',
                         monotonic_start_ns=(i+1)*1000000000, status='complete', command=['cat a','ls b'][i%2]))
                subprocess.run([sys.executable, str(scripts/'session.py'), 'close', str(folder)], check=True, capture_output=True)
            subprocess.run([sys.executable, str(scripts/'analyze.py'), str(root/'human'), str(root/'agent'),
                            '--baseline',str(root/'train'),'--output',str(root/'analysis')], check=True, capture_output=True)
            self.assertTrue((root/'analysis'/'comparison.csv').exists())
            out = root/'export'
            out.mkdir()
            save(out/'sysmon.json', [dict(event_time='2026-01-01T00:00:01Z',event_id=1)])
            save(out/'wazuh.json', dict(hits=[dict(_id='test',_index='synthetic',_source={'data':{'win':{
                'system':dict(systemTime='2026-01-01T00:00:01Z',eventID='1',computer='ws')}}})]))
            subprocess.run([sys.executable,str(scripts/'export.py'),str(root/'human'),str(out),
                            '--clock-offset-seconds','0','--padding-seconds','0'], check=True,capture_output=True)
            result = json.loads((out/'correlated.json').read_text())
            self.assertEqual(len(result), 2)
            self.assertEqual(result[0]['candidate_command_ids'], ['1'])


if __name__ == '__main__':
    unittest.main()

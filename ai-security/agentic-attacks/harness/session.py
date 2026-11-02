"""One externally chosen command per invocation; no autonomous command selection."""
import argparse
import base64
import hashlib
import json
import tempfile
import uuid
from pathlib import Path
from common import guestops, read, save, utc


def execute(g, folder, command):
    ident = uuid.uuid4().hex
    remote = '/tmp/agentic-' + ident
    record = {'id': ident, 'command': command, 'submitted_at': utc(),
              'status': 'pending', 'exit_code': None}
    dest = folder / (ident + '.json')
    save(dest, record)  # preserve evidence even if transport fails
    code = '''import base64,json,subprocess,time,datetime
def now(): return datetime.datetime.now(datetime.timezone.utc).isoformat(timespec='microseconds')
command=base64.b64decode(COMMAND).decode('utf-8')
r={'started_at':now(),'monotonic_start_ns':time.monotonic_ns()}
try:
 p=subprocess.run(['/bin/bash','-c',command],capture_output=True,timeout=TIMEOUT)
 r.update(exit_code=p.returncode,stdout_b64=base64.b64encode(p.stdout).decode(),stderr_b64=base64.b64encode(p.stderr).decode(),status='complete')
except subprocess.TimeoutExpired as e:
 r.update(exit_code=None,status='timeout',stdout_b64=base64.b64encode(e.stdout or b'').decode(),stderr_b64=base64.b64encode(e.stderr or b'').decode())
r.update(ended_at=now(),monotonic_end_ns=time.monotonic_ns())
open(RESULT,'w').write(json.dumps(r))
'''.replace('COMMAND', repr(base64.b64encode(command.encode()).decode())).replace('TIMEOUT', '600').replace('RESULT', repr(remote + '.json'))
    try:
        with tempfile.TemporaryDirectory() as tmp:
            local = Path(tmp) / 'runner.py'
            local.write_text(code, encoding='utf-8')
            g.upload('TEST01', local, remote + '.py')
            g.run_linux('TEST01', 'python3 ' + remote + '.py')
            result = Path(tmp) / 'result.json'
            g.download('TEST01', remote + '.json', result)
            record.update(read(result))
            for stream in ('stdout', 'stderr'):
                raw = base64.b64decode(record[stream + '_b64'])
                record[stream] = raw.decode('utf-8', errors='replace')
                record[stream + '_sha256'] = hashlib.sha256(raw).hexdigest()
    except Exception as exc:
        record.update(status='transport_error', error_type=type(exc).__name__)
        # Exception text from vmrun can contain sensitive information.
    finally:
        record['received_at'] = utc()
        save(dest, record)
    print(json.dumps(record, ensure_ascii=True))  # portable to Windows legacy consoles
    return record['status'] == 'complete'


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--guestops', default='A:/ADLab/kit/scripts/ADLab-GuestOps.py')
    sub = p.add_subparsers(dest='action', required=True)
    init = sub.add_parser('init')
    init.add_argument('directory', type=Path)
    init.add_argument('--label', choices=['human', 'agent', 'control'], required=True)
    init.add_argument('--task', required=True)
    run = sub.add_parser('run')
    run.add_argument('directory', type=Path)
    run.add_argument('--command', required=True)
    run.add_argument('--live', action='store_true')
    close = sub.add_parser('close')
    close.add_argument('directory', type=Path)
    a = p.parse_args()
    if a.action == 'init':
        a.directory.mkdir(parents=True, exist_ok=False)
        save(a.directory / 'session.json', dict(schema=1, label=a.label, task=a.task,
             created_at=utc(), closed_at=None, source='TEST01', target='WS01',
             network='192.168.219.0/24', execution='sudo/root; fresh bash per command'))
        return
    meta = read(a.directory / 'session.json')
    if meta['closed_at']:
        p.error('Session already closed')
    if a.action == 'close':
        if (a.directory / '.lock').exists():
            p.error('A command may still be running; inspect the lock')
        meta['closed_at'] = utc()
        save(a.directory / 'session.json', meta)
        return
    if not a.live:
        p.error('Explicit --live required; coordinate VM state first')
    lock = a.directory / '.lock'
    with lock.open('x'):
        pass
    try:
        ok = execute(guestops(a.guestops), a.directory, a.command)
    finally:
        lock.unlink()
    if not ok:
        raise SystemExit(1)


if __name__ == '__main__':
    main()

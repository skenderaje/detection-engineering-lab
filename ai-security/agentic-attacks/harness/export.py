"""Explicit live export, or offline re-correlation of preserved artifacts."""
import argparse
import json
import tempfile
import uuid
from datetime import datetime, timedelta
from pathlib import Path
from common import guestops, read, save, utc


def records(directory):
    return sorted((read(p) for p in Path(directory).glob('*.json')
                   if p.name != 'session.json'), key=lambda r: r['submitted_at'])


def stamp(value):
    d = datetime.fromisoformat(value.replace('Z', '+00:00'))
    if d.tzinfo is None:
        raise ValueError('Timezone required')
    return d


def correlate(rows, commands, tolerance):
    result = []
    for row in rows:
        t = stamp(row['event_time'])
        candidates = [c['id'] for c in commands if c.get('started_at') and
                      stamp(c['started_at']) - timedelta(seconds=tolerance) <= t <=
                      stamp(c['ended_at']) + timedelta(seconds=tolerance)]
        result.append(dict(row, candidate_command_ids=candidates,
                           attribution='temporal_candidate_only'))
    return result


def live(g, out, start, end, config):
    token = uuid.uuid4().hex
    remote = 'C:\\Windows\\Temp\\agentic-' + token
    ps = r'''$ErrorActionPreference='Stop'
$rows=@(Get-WinEvent -FilterHashtable @{LogName='Microsoft-Windows-Sysmon/Operational';Id=1,3;StartTime=[datetime]'START';EndTime=[datetime]'END'} -ErrorAction SilentlyContinue)
if ($Error.Count -gt 0 -and $Error[0].FullyQualifiedErrorId -notlike 'NoMatchingEventsFound*') { throw $Error[0] }
$result=@($rows | ForEach-Object {
 $x=[xml]$_.ToXml(); $data=@{}
 foreach($d in $x.Event.EventData.Data){$data[$d.Name]=[string]$d.'#text'}
 @{event_time=$_.TimeCreated.ToUniversalTime().ToString('o');event_id=$_.Id;record_id=$_.RecordId;computer=$_.MachineName;data=$data;xml=$_.ToXml()}
})
ConvertTo-Json -InputObject $result -Depth 12 | Set-Content -Encoding UTF8 'REMOTE.json'
'''.replace('START', start).replace('END', end).replace('REMOTE', remote)
    with tempfile.TemporaryDirectory() as tmp:
        script = Path(tmp) / 'export.ps1'
        script.write_text(ps, encoding='utf-8-sig')
        g.upload('WS01', script, remote + '.ps1')
        g.run_ps('WS01', filename=remote + '.ps1')
        g.download('WS01', remote + '.json', out / 'sysmon.json')
        # Credentials remain in an existing root-readable guest config, never downloaded.
        helper = Path(__file__).with_name('wazuh_export_guest.py')
        linux = '/tmp/agentic-' + token
        g.upload('WAZUH', helper, linux + '.py')
        import shlex
        g.run_linux('WAZUH', 'python3 ' + shlex.quote(linux + '.py') + ' ' +
                    ' '.join(shlex.quote(s) for s in [config, start, end, linux + '.json']))
        g.download('WAZUH', linux + '.json', out / 'wazuh.json')


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('session', type=Path)
    p.add_argument('output', type=Path)
    p.add_argument('--live', action='store_true')
    p.add_argument('--guestops', default='A:/ADLab/kit/scripts/ADLab-GuestOps.py')
    p.add_argument('--wazuh-config', default='/root/agentic-indexer.json')
    p.add_argument('--padding-seconds', type=float, required=True)
    p.add_argument('--clock-offset-seconds', type=float, required=True,
                   help='WS01 UTC minus TEST01 UTC, measured externally')
    a = p.parse_args()
    if a.padding_seconds < 0:
        p.error('Padding must be nonnegative')
    meta = read(a.session / 'session.json')
    commands = records(a.session)
    if not meta['closed_at'] or not commands or any(c['status'] != 'complete' for c in commands):
        p.error('Need closed session with complete commands; inspect failures first')
    shifted = [dict(c, started_at=(stamp(c['started_at']) + timedelta(seconds=a.clock_offset_seconds)).isoformat(),
                    ended_at=(stamp(c['ended_at']) + timedelta(seconds=a.clock_offset_seconds)).isoformat()) for c in commands]
    start = (min(stamp(c['started_at']) for c in shifted) - timedelta(seconds=a.padding_seconds)).isoformat()
    end = (max(stamp(c['ended_at']) for c in shifted) + timedelta(seconds=a.padding_seconds)).isoformat()
    if a.live:
        a.output.mkdir(parents=True, exist_ok=False)
        save(a.output / 'manifest.json', dict(start=start, end=end, exported_at=utc(),
             clock_offset_seconds=a.clock_offset_seconds, padding_seconds=a.padding_seconds,
             status='incomplete', session=meta))
        live(guestops(a.guestops), a.output, start, end, a.wazuh_config)
    sysmon = read(a.output / 'sysmon.json')
    wazuh = read(a.output / 'wazuh.json')
    rows = [dict(r, source='sysmon') for r in sysmon]
    for hit in wazuh['hits']:
        source = hit['_source']
        system = source['data']['win']['system']
        rows.append(dict(source='wazuh', event_time=system['systemTime'],
                         event_id=system['eventID'], record_id=system.get('eventRecordID'),
                         computer=system.get('computer'), index=hit['_index'], id=hit['_id'], raw=source))
    save(a.output / 'correlated.json', correlate(rows, shifted, a.padding_seconds))
    save(a.output / 'correlation-parameters.json', dict(start=start, end=end,
         clock_offset_seconds=a.clock_offset_seconds, padding_seconds=a.padding_seconds))
    if a.live:
        manifest = read(a.output / 'manifest.json')
        manifest.update(status='exported_not_proven_complete', completed_at=utc(),
                        sysmon_count=len(sysmon), wazuh_count=len(wazuh['hits']))
        save(a.output / 'manifest.json', manifest)


if __name__ == '__main__':
    main()

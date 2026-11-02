"""Uploaded to WAZUH by export.py. HTTPS read-only indexer search with scroll."""
import base64
import json
import ssl
import sys
import urllib.request
from datetime import datetime, timezone


def main():
    config_path, start, end, output = sys.argv[1:]
    with open(config_path) as f:
        c = json.load(f)
    if not c['url'].startswith('https://'):
        raise ValueError('HTTPS required')
    context = ssl.create_default_context(cafile=c['ca_file'])
    auth = base64.b64encode((c['username'] + ':' + c['password']).encode()).decode()

    def request(path, body, method='POST'):
        req = urllib.request.Request(c['url'].rstrip('/') + path,
              data=json.dumps(body).encode(), method=method,
              headers={'Authorization': 'Basic ' + auth, 'Content-Type': 'application/json'})
        with urllib.request.urlopen(req, context=context, timeout=60) as response:
            result = json.load(response)
        if result.get('timed_out') or result.get('_shards', {}).get('failed', 0):
            raise RuntimeError('Partial indexer search')
        return result

    query = {'size': 500, 'sort': ['_doc'], 'query': {'bool': {'filter': [
        {'term': {'agent.id': c['agent_id']}},
        {'terms': {'data.win.system.eventID': ['1', '3']}},
        {'term': {'data.win.system.providerName': 'Microsoft-Windows-Sysmon'}},
        {'range': {'data.win.system.systemTime': {'gte': start, 'lte': end}}}]}}}
    import urllib.parse
    index = urllib.parse.quote(c['index_pattern'], safe='*-_,')
    hits, scroll = [], None
    try:
        page = request('/' + index + '/_search?scroll=2m', query)
        while True:
            scroll = page.get('_scroll_id', scroll)
            batch = page['hits']['hits']
            if not batch:
                break
            hits.extend(batch)
            if not scroll:
                raise RuntimeError('Missing scroll id; refusing truncated export')
            page = request('/_search/scroll', {'scroll': '2m', 'scroll_id': scroll})
    finally:
        if scroll:
            request('/_search/scroll', {'scroll_id': [scroll]}, method='DELETE')
    with open(output, 'w') as f:
        json.dump(dict(hits=hits, query=query, index_pattern=c['index_pattern'],
             exported_at=datetime.now(timezone.utc).isoformat(),
             completeness='snapshot_only; late indexing and retention not excluded'), f)


if __name__ == '__main__':
    main()

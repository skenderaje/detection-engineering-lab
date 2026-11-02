"""Descriptive comparison; no AI attribution and no fitted detection thresholds."""
import argparse
import math
import shlex
from collections import Counter, defaultdict
from pathlib import Path
import pandas as pd
from common import read, save
from export import records


def entropy(items):
    counts = Counter(items)
    n = sum(counts.values())
    return -sum((v/n) * math.log2(v/n) for v in counts.values()) if n else float('nan')


def quantize(values, q):
    # Duplicate quantiles collapse: never split identical delays arbitrarily by rank.
    s = pd.Series(values, dtype=float)
    if s.empty:
        return [], []
    if s.nunique() == 1:
        return [0] * len(s), [float(s.iloc[0])]
    bins, edges = pd.qcut(s, q=q, labels=False, retbins=True, duplicates='drop')
    return bins.astype(int).tolist(), edges.tolist()


def cce(symbols, max_order):
    h = entropy(symbols)
    curve = []
    for m in range(2, min(max_order, len(symbols)) + 1):
        blocks = [tuple(symbols[i:i+m]) for i in range(len(symbols)-m+1)]
        # Same windows for joint and prefix: empirical conditional entropy >= 0.
        ce = entropy(blocks) - entropy([b[:-1] for b in blocks])
        singleton_fraction = sum(v for v in Counter(blocks).values() if v == 1) / len(blocks)
        curve.append(dict(order=m, windows=len(blocks), conditional_bits=ce,
                          singleton_fraction=singleton_fraction, cce_bits=ce + singleton_fraction*h))
    return (min([h] + [r['cce_bits'] for r in curve]) if curve else float('nan')), curve


def normalize(command):
    lexer = shlex.shlex(command, posix=True, punctuation_chars=';&|()<>')
    lexer.whitespace_split = True
    lexer.commenters = ''
    result, executable = [], True
    for token in lexer:
        if token and all(c in ';&|()<>' for c in token):
            result.append(token)
            executable = token not in ('>', '>>', '<', '<<')
        elif executable:
            result.append(token)
            executable = False
        else:
            result.append('<ARG>')
    return ' '.join(result)


def model(states):
    return Counter(zip(states, states[1:]))


def score(states, transitions, vocabulary, alpha):
    totals = Counter()
    for (a, b), n in transitions.items():
        totals[a] += n
    vocab = set(vocabulary)
    pairs = list(zip(states, states[1:]))
    if not pairs:
        return float('nan'), float('nan')
    losses = []
    for a, b in pairs:
        a = a if a in vocab else '<UNK>'
        b = b if b in vocab else '<UNK>'
        prob = (transitions[a, b] + alpha) / (totals[a] + alpha*(len(vocab)+1))
        losses.append(-math.log2(prob))
    return sum(losses)/len(losses), sum(s not in vocab for s in states)/len(states)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('sessions', nargs='+', type=Path)
    p.add_argument('--baseline', type=Path, required=True, help='Independent human training session; excluded from scoring')
    p.add_argument('--output', type=Path, required=True)
    p.add_argument('--max-order', type=int, default=10)
    p.add_argument('--entropy-bins', type=int, default=256)
    p.add_argument('--rate-bins', type=int, default=5)
    p.add_argument('--alpha', type=float, default=1.0)
    a = p.parse_args()
    if len(a.sessions) < 2 or a.alpha <= 0 or a.max_order < 2 or min(a.entropy_bins, a.rate_bins) < 2:
        p.error('Need >=2 test sessions, positive alpha, order >=2 and bins >=2')
    if len({s.resolve() for s in a.sessions}) != len(a.sessions) or a.baseline.resolve() in {s.resolve() for s in a.sessions}:
        p.error('Training and test sessions must be distinct')

    def load(folder):
        meta = read(folder / 'session.json')
        rows = records(folder)
        if not meta['closed_at'] or not rows or any(r['status'] != 'complete' for r in rows):
            raise ValueError('Closed complete sessions required: ' + str(folder))
        rows.sort(key=lambda r: r['monotonic_start_ns'])
        return meta, rows, [normalize(r['command']) for r in rows]

    baseline_meta, baseline_rows, baseline = load(a.baseline)
    if baseline_meta['label'] != 'human' or len(baseline) < 2:
        p.error('Human training baseline needs >=2 commands')
    training = model(baseline)
    table, details = [], {}
    for folder in a.sessions:
        meta, commands, states = load(folder)
        times = pd.Series([r['monotonic_start_ns'] for r in commands], dtype='int64')
        delays = (times.diff().dropna()/1e9).tolist()
        if any(d <= 0 for d in delays):
            raise ValueError('Non-increasing monotonic timestamps: possible reboot')
        fine, fine_edges = quantize(delays, a.entropy_bins)
        coarse, coarse_edges = quantize(delays, a.rate_bins)
        rate, curve = cce(coarse, a.max_order)
        loss, unknown = score(states, training, baseline, a.alpha)
        row = dict(session=str(folder), label=meta['label'], commands=len(commands),
                   intervals=len(delays), mean_delay_s=pd.Series(delays, dtype=float).mean(),
                   timing_entropy_bits=entropy(fine), timing_rate_cce_bits=rate,
                   markov_baseline_bits_per_transition=loss, unseen_state_fraction=unknown,
                   warning='exploratory; no validated minimum sample size')
        table.append(row)
        counts = model(states)
        totals = defaultdict(int)
        for (x, y), n in counts.items():
            totals[x] += n
        details[str(folder)] = dict(normalized_commands=states, fine_edges=fine_edges,
             coarse_edges=coarse_edges, cce_curve=curve,
             transitions=[dict(previous=x, next=y, count=n, probability=n/totals[x]) for (x,y),n in sorted(counts.items())])
    a.output.mkdir(parents=True, exist_ok=False)
    frame = pd.DataFrame(table)
    frame.to_csv(a.output / 'comparison.csv', index=False)
    rendered = frame.to_string(index=False, float_format=lambda x: f'{x:.4f}')
    (a.output / 'comparison.txt').write_text(rendered + '\n', encoding='utf-8')
    save(a.output / 'details.json', dict(parameters={k: str(v) if isinstance(v, Path) else
         [str(s) for s in v] if k == 'sessions' else v for k,v in vars(a).items()},
         pandas_version=pd.__version__, sessions=details,
         baseline_transitions=[dict(previous=x,next=y,count=n) for (x,y),n in sorted(training.items())]))
    print(rendered)


if __name__ == '__main__':
    main()

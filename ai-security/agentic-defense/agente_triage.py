"""Scheletro offline dell'agente di triage — vedi triage-agent-spec.md.

Importare questo modulo non contatta mai la rete del lab: legge solo file
JSON già prodotti da harness/export.py e harness/analyze.py. La chiamata al
modello (model_call) e' isolata in una funzione sostituibile con un mock,
cosi' da poter testare build_draft senza nessuna chiave API, nello stesso
spirito di common.py/analyze.py nell'harness offensivo.

Nessuna etichetta "AI"/"umano" viene prodotta qui (vedi vincolo 2 della spec):
il modulo riporta solo se le due condizioni della regola sono soddisfatte sui
dati disponibili, con citazione del file/campo di origine.
"""
import argparse
import json
from pathlib import Path


def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8-sig'))


def condition_from_details(details, rule_thresholds):
    """Confronta i valori già calcolati da analyze.py con le soglie già
    compilate in detection-rule-spec.md. Non calcola nulla di nuovo: se un
    valore o una soglia manca, lo dichiara esplicitamente invece di stimarlo.
    """
    out = {}
    for name, field in (('A', 'entropy_rate_bits'), ('B', 'markov_cross_entropy_bits')):
        value = details.get(field)
        threshold = rule_thresholds.get(name) if rule_thresholds else None
        if value is None:
            out[name] = dict(status='campo assente in details.json', value=None, source=f'details.json:{field}')
        elif threshold is None:
            out[name] = dict(status='soglia non ancora compilata', value=value, source=f'details.json:{field}')
        else:
            out[name] = dict(status='sotto soglia' if value < threshold else 'sopra soglia',
                              value=value, threshold=threshold, source=f'details.json:{field}')
    return out


def uncorrelated_events(correlated):
    """Conta gli eventi Sysmon senza alcun command ID associato.
    Un conteggio alto non e' prova di attivita' mancante: e' solo un fatto
    sulla finestra esportata (vedi harness/README.md, sezione export)."""
    events = correlated.get('events', []) if isinstance(correlated, dict) else correlated
    return sum(1 for e in events if not e.get('command_ids'))


def model_call(prompt):
    """Punto di innesto per il modello. Lo scheletro non chiama nessuna API:
    ritorna None, cosi' build_draft produce una bozza con i soli fatti
    deterministici e marca esplicitamente la sezione interpretativa come da
    completare. Sostituire con una chiamata reale resta responsabilita' di
    chi implementa l'esercizio, non di questo scheletro."""
    return None


def build_draft(exercise_name, details, correlated, rule_thresholds=None):
    conditions = condition_from_details(details, rule_thresholds)
    uncorrelated = uncorrelated_events(correlated)
    lines = [
        f"# Bozza di triage — {exercise_name}",
        "",
        "## Letto dall'agente, da verificare a mano",
        "Sezione generata automaticamente. Ogni affermazione cita il file e il",
        "campo da cui proviene. Nessun valore qui e' stato calcolato da questo",
        "script oltre a un confronto diretto valore/soglia.",
        "",
    ]
    for name in ('A', 'B'):
        c = conditions[name]
        lines.append(f"- Condizione {name}: {c['status']} (fonte: {c['source']}"
                      + (f", valore={c['value']}, soglia={c.get('threshold')}" if c.get('threshold') is not None else f", valore={c.get('value')}")
                      + ")")
    lines.append(f"- Eventi Sysmon senza comando candidato nella finestra: {uncorrelated} "
                 "(fonte: correlated.json; assenza di candidato non e' prova di assenza di attivita')")
    lines += [
        "",
        "## Non determinabile dai dati disponibili",
    ]
    missing = [c['status'] for c in conditions.values() if 'non ancora' in c['status'] or 'assente' in c['status']]
    if missing:
        lines.append("- " + "; ".join(sorted(set(missing))))
    else:
        lines.append("- (nessun campo dichiarato mancante dalle fonti lette; verificare comunque a mano)")
    interpretation = model_call(dict(conditions=conditions, uncorrelated=uncorrelated))
    if interpretation is None:
        lines.append("- Interpretazione del modello non generata in questa esecuzione "
                     "(model_call non configurata): completare a mano prima di considerare la bozza finale.")
    return "\n".join(lines) + "\n"


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('exercise_name')
    p.add_argument('details_json')
    p.add_argument('correlated_json')
    p.add_argument('--rule-thresholds-json', default=None,
                   help='JSON opzionale {"A": <soglia>, "B": <soglia>} compilato a mano da detection-rule-spec.md')
    p.add_argument('--out', default=None, help='Percorso del file di bozza; default stdout')
    args = p.parse_args()

    details = read(args.details_json)
    correlated = read(args.correlated_json)
    thresholds = read(args.rule_thresholds_json) if args.rule_thresholds_json else None
    draft = build_draft(args.exercise_name, details, correlated, thresholds)

    if args.out:
        out_path = Path(args.out)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(draft, encoding='utf-8')
    else:
        print(draft)


if __name__ == '__main__':
    main()

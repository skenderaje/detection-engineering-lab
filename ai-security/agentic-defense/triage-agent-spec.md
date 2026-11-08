# Specifica dell'agente di triage

## Input (tutti già prodotti, nessuno generato dall'agente)

| File | Prodotto da | Cosa contiene |
|---|---|---|
| `exports/<run>/correlated.json` | `harness/export.py` | eventi Sysmon nella finestra, con zero/uno/più command ID associati per sovrapposizione temporale |
| `analysis/<comparison>/details.json` | `harness/analyze.py` | entropia, entropy-rate, CCE, cross-entropy Markov per sessione, con bordi dei bin e parametri |
| `agentic-attacks/detection-rule-spec.md` + la regola Sigma compilata | lavoro umano + harness | soglie reali (quando esistono) per Condizione A e Condizione B |
| log prompt/risposta del controller offensivo (se la sessione analizzata è `agent-test`) | estensione di `session.py` richiesta in [`agente-offensivo-spec.md`](../agentic-attacks/agente-offensivo-spec.md) | cosa ha "pensato" il controller a ogni passo |

L'agente non apre altri file, non interroga l'indexer Wazuh in diretta, non legge `runs/` grezzo (già coperto da `export.py`).

## Output

Un file markdown con questa struttura fissa, da salvare come bozza in `writeups/` (mai sovrascrivere un writeup esistente senza revisione umana):

```markdown
# Bozza di triage — <nome esercizio>

## Letto dall'agente, da verificare a mano
Questa sezione è generata automaticamente. Ogni affermazione cita il file e il
campo da cui proviene. Nessun valore qui è stato calcolato dall'agente.

- Condizione A (cadenza): [soddisfatta/non soddisfatta/soglia non ancora compilata],
  valori: entropia=<da details.json>, entropy-rate=<da details.json>
- Condizione B (sequenza): [soddisfatta/non soddisfatta/soglia non ancora compilata],
  valore: cross-entropy=<da details.json>
- Eventi Sysmon senza alcun comando candidato nella finestra: <conteggio da correlated.json>
  (ricorda: assenza di candidato non è prova di assenza di attività — vedi
  harness/README.md, sezione export)
- Tecniche ATT&CK osservate (non assegnate a priori): <solo se derivabili dai
  comandi effettivamente eseguiti nella sessione, con riferimento al comando>

## Non determinabile dai dati disponibili
<elenco esplicito di cosa l'agente non può concludere con questi file>
```

La seconda sezione è obbligatoria anche quando vuota di contenuto concreto: l'agente deve scrivere esplicitamente i limiti (soglie non compilate, campione troppo corto, assenza di baseline indipendente) invece di ometterli, replicando lo stesso standard di onestà richiesto al resto del lab in "Limiti noti" del README principale.

## Vincoli del prompt di sistema

1. **Citazione obbligatoria**: ogni numero o affermazione nell'output deve indicare il file e il campo di provenienza. Un'affermazione senza citazione viene scartata, non inclusa "a memoria".
2. **Divieto di etichettare "AI" o "umano"**: il prompt deve vietare esplicitamente frasi come "questa sessione è stata condotta da un'AI" — `analyze.py` stesso non produce quell'etichetta, e l'agente di triage non può introdurla a un livello di astrazione successivo.
3. **Divieto di inventare soglie**: se `detection-rule-spec.md` non ha ancora soglie compilate, l'agente scrive "soglia non ancora compilata", non una stima propria.
4. **Nessuna azione**: il prompt non espone all'agente nessun tool di scrittura su Wazuh, GuestOps o il repo stesso oltre alla scrittura del file di bozza in una cartella separata (`writeups/bozze-agente/`, non `writeups/` direttamente) in attesa di revisione e spostamento manuale.
5. **Contesto limitato alla finestra dell'esercizio**: l'agente non deve ricevere in input sessioni/esercizi diversi da quello richiesto, per evitare che generalizzi pattern da un compito a un altro senza che sia stato verificato.

## Collegamento con il resto del lab

Se l'agente segnala che la Condizione A o B non separano le due sessioni (umana e agente) nei dati raccolti, il passo successivo è lo stesso già previsto dal metodo in sette passi: tornare al punto 6 (scrivere o correggere la regola) e ripetere — non modificare la soglia dentro l'agente stesso, che non ha e non deve avere accesso in scrittura alla regola.

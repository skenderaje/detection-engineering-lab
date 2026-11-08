# Agentic defense — un agente di triage che chiude il ciclo del lab

Scopo: usare un LLM **solo per leggere e correlare** gli artefatti già prodotti dal resto del lab (`correlated.json` di `export.py`, la regola Sigma/Wazuh compilata, la mappatura ATT&CK) e scrivere una bozza di valutazione dell'incidente nello stesso formato di [`writeups/`](../../writeups/README.md) — non per decidere o eseguire nulla sul bersaglio.

Questo chiude il metodo in sette passi del README principale: i passi 1-6 (definire la tecnica, eseguire, raccogliere evidenze, scrivere la regola) restano quelli già descritti; l'agente di difesa si inserisce **dopo** il passo 6, come lettore di "regola → alert" che propone una bozza di write-up e, se la regola sembra sbagliata (troppi falsi positivi nei dati raccolti, soglia che non separa i due profili), propone una correzione da verificare a mano — non la applica.

## Perché "agentico" e perché i limiti sono la parte importante

Un sistema che si limita a stampare "se campo X > soglia Y allora alert" non ha bisogno di un LLM: è la regola Sigma stessa. Il motivo per cui un agente ha senso qui è diverso: deve leggere **testo non strutturato** che il resto della pipeline non interpreta — l'XML Sysmon integrale, lo stdout/stderr del comando, l'eventuale log del controller offensivo (prompt/risposta, vedi [`agente-offensivo-spec.md`](../agentic-attacks/agente-offensivo-spec.md)) — e produrre una sintesi leggibile da chi deve decidere. Il rischio esatto che questo introduce è che l'agente *inventi* una correlazione che il parser deterministico non ha trovato. Per questo:

- **L'agente non calcola feature nuove.** Non ricalcola entropia, Markov o CCE: legge gli output già prodotti da `analyze.py` e dalla regola compilata, e li riassume in prosa. Se un numero serve, viene preso da quei file, non stimato dal modello.
- **L'agente non ha credenziali né accesso in scrittura.** Legge file locali (gli export già scaricati con `export.py --live`, mai l'indexer live direttamente) e, se la sessione lo richiede, una API in sola lettura — mai lo stesso path usato per installare/configurare telemetria, che l'harness esplicitamente non fa.
- **L'agente non etichetta "umano" o "AI".** `analyze.py` è già esplicito: "non produce etichette predette né soglie". L'agente di triage eredita lo stesso vincolo — scrive "la Condizione A e la Condizione B della regola [sono/non sono] soddisfatte, con questi valori", non "questo è un agente AI".
- **Ogni output è una bozza, non un verdetto.** Il formato di uscita è un file in `writeups/` con gli stessi campi richiesti dal resto del lab (Scopo, Macchina, Prerequisiti, Risultato atteso, Prove raccolte, Condizioni per fermarsi) più una sezione "Letto dall'agente, da verificare a mano" — mai un campo che si sostituisce alla verifica umana.

## Architettura

```
┌───────────────────────────┐
│ Artefatti già prodotti     │
│ (correlated.json, sigma    │
│  compilata, sysmon.json,   │
│  log prompt/risposta       │
│  dell'agente offensivo)    │
└─────────────┬──────────────┘
              │ solo lettura, offline
              ▼
┌───────────────────────────┐
│  Triage agent (LLM)        │
│  - riassume in prosa       │
│  - segnala soglie mancanti │
│  - propone mapping ATT&CK  │
│    SOLO se osservato nei   │
│    dati, non per supposiz. │
└─────────────┬──────────────┘
              │ bozza markdown
              ▼
┌───────────────────────────┐
│ writeups/<esercizio>.md    │
│ (da rivedere a mano prima  │
│  di essere considerato     │
│  definitivo)                │
└───────────────────────────┘
```

Nessuna freccia entra nel bersaglio, nel domain controller o nel SIEM in scrittura: l'agente di difesa, come l'harness offensivo, resta sulla postazione di verifica e opera su file già esportati.

## Contenuti di questa cartella

- [`triage-agent-spec.md`](triage-agent-spec.md) — specifica dei campi di input/output e dei vincoli del prompt (nessuna soglia inventata, nessuna etichetta AI/umano, citazione obbligatoria della fonte per ogni affermazione).
- `agente_triage.py` *(scheletro, da completare insieme all'implementazione di `harness/`)* — legge `analysis/*/details.json` e `exports/*/correlated.json` già presenti su disco, non contatta mai la rete del lab; la chiamata al modello è isolata in una funzione sostituibile con un mock per i test, come `common.py`/`analyze.py` fanno già per il resto dell'harness.

## Stato

**Specifica e scheletro offline, nessun esercizio eseguito.** Dipende dal completamento di `harness/` (sezione "Detection e condizioni per fermarsi" in [`harness/README.md`](../agentic-attacks/harness/README.md)) per avere dati reali da leggere: senza una regola compilata con soglie vere, questo agente non ha nulla da correlare oltre a dati sintetici di test.

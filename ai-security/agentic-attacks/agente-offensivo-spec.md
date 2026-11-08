# Specifica dell'agente offensivo (versione agentica dell'attacco)

Non è un exploit nuovo: è la specifica di **come un controller LLM guida tecniche già note e già citate in questo repo** (enumerazione AD, Kerberoasting) attraverso l'harness esistente in [`harness/`](harness/README.md), così che ogni comando — scelto dal modello o da un umano — passi dalla stessa CLI strumentata (`session.py`) e produca gli stessi artefatti comparabili. Senza questo, non si può rispondere alla domanda del lab: cosa, nei log, distingue l'agente dall'operatore umano.

Stato: **specifica, nulla eseguito**. Vale lo stesso status di [`detection-rule-spec.md`](detection-rule-spec.md) e delle note in [`harness/README.md`](harness/README.md): nessuna soglia, nessun avvio VM, nessuna chiamata GuestOps reale.

## Perché una tecnica concreta, non "un agente generico"

Le ipotesi di lavoro in [questo README](README.md#ipotesi-di-lavoro) (ritmo di esecuzione, enumerazione esaustiva, firma del tool-calling) non si verificano con un agente che "fa quello che vuole": servono due sessioni confrontabili sullo **stesso compito**, una guidata da un umano (baseline già prevista da `session.py init --label human`) e una guidata dal controller. Il compito scelto, perché già inquadrato nel resto del repo (README principale, `casistica-bersagli.md`, menzione di Mimikatz/Empire/Sliver) e perché produce telemetria Sysmon ben definita sul dominio GOAD:

1. **Enumerazione del dominio** (ATT&CK T1087.002 Domain Account, T1018 Remote System Discovery, T1135 Network Share Discovery) — chi sono gli utenti, i computer, le share SMB raggiungibili da WS01.
2. **Kerberoasting** (ATT&CK T1558.003) — richiesta di service ticket per account con SPN registrato, a valle dell'enumerazione, con lo strumento standard già diffuso in letteratura AD (Impacket `GetUserSPNs.py` o equivalente PowerShell); il cracking offline dell'hash **non fa parte di questo esercizio**, perché non genera traffico/eventi sul bersaglio ed è fuori scopo per un lab di detection.

Nessuna tecnica qui è nuova o non pubblica: sono le stesse della guida GOAD e di Atomic Red Team già citate in [`README.md`](../../README.md#metodo-di-emulazione). Quello che manca, e che questa specifica definisce, è **chi decide il prossimo comando** quando il "chi" è un LLM invece di un umano al tavolo.

## Architettura del controller

```
┌─────────────┐   goal + whitelist tool   ┌──────────────┐
│  Operatore   │ ─────────────────────────▶│  Controller  │
│  umano       │                            │  LLM         │
│ (autorizza   │◀─── comando proposto ──────│              │
│  ogni passo) │                            └──────┬───────┘
└──────┬──────┘                                     │ comando approvato
       │ approva/rifiuta                            ▼
       │                                   ┌──────────────────┐
       └──────────────────────────────────▶│ session.py run    │
                                            │ --live --command   │
                                            │ (harness esistente) │
                                            └─────────┬──────────┘
                                                       │ stdout/stderr/exit
                                                       ▼
                                            ┌──────────────────────┐
                                            │ contesto del controller│
                                            │ (storico comandi+esiti)│
                                            └──────────────────────┘
```

Punti non negoziabili, derivati dalle regole già scritte in `harness/README.md`:

- **Il controller propone, non esegue.** Ogni comando passa per `session.py run --live --command`, la stessa CLI della sessione umana. Il controller non ha accesso diretto a GuestOps, a credenziali, né a un canale di esecuzione parallelo.
- **Gate umano per ogni comando**, almeno nella prima iterazione dell'esercizio — coerente con "un comando scelto esternamente alla volta" già richiesto per la sessione umana. Automatizzare il gate (rimuovere l'approvazione passo-passo) è una modifica successiva, da giustificare e documentare separatamente, non lo stato iniziale.
- **Whitelist di comandi**, non libertà di shell arbitraria: il controller riceve l'elenco esatto dei comandi/tool ammessi per il compito (enumerazione + Kerberoasting come sopra) e il prompt di sistema lo vincola a quell'elenco. Un comando fuori whitelist viene rifiutato dal gate umano, non silenziosamente eseguito.
- **Nessuna persistenza, nessun C2 nel loop stesso**: il "ciclo" osserva-pianifica-agisci è nel controller (processo sulla postazione di verifica), non nel bersaglio. Non introduce un impianto nuovo oltre a quanto già previsto per Empire/Sliver nel resto del lab.
- **Log delle decisioni, non solo dei comandi**: oltre a quanto `session.py` già registra per comando (vedi harness README, sezione 1), questo esercizio richiede di salvare anche il prompt e la risposta grezza del controller per ogni passo, come file separato nella stessa cartella `runs/agent-test`. Senza questo, `analyze.py` può confrontare *cosa* è stato eseguito ma non *perché* — e la domanda sulla "firma del tool-calling" (ipotesi 3 del README) richiede proprio quel testo.

## Cosa questa specifica non copre

- Non assegna un modello LLM specifico: qualunque modello usato va dichiarato nella scheda di esperimento (stessa richiesta già fatta per commit/Python/pandas in `harness/README.md`).
- Non definisce il prompt di sistema esatto: va scritto e versionato insieme all'implementazione, non qui, perché cambia il comportamento osservato e deve essere riproducibile come il resto.
- Non implementa il gate di approvazione né l'integrazione col controller: è lavoro di implementazione su `harness/`, da fare dopo aver completato quanto già "in costruzione" lì (vedi [`harness/README.md`](harness/README.md)).
- Non stabilisce se/quando automatizzare il gate umano: è una decisione da prendere con dati della prima run supervisionata in mano, non a priori.

## Condizioni per fermarsi

Le stesse di `harness/README.md` (conflitti RAM/stato VM, isolamento incerto, clock non misurati, telemetria mancante, errori di trasporto, timeout, processo residuo, riavvio guest, schema inatteso, credenziali nei risultati), più: il controller propone un comando fuori whitelist, il controller propone un comando identico a un passo già fallito senza modifiche, o il controller richiede l'ampliamento del proprio accesso (nuovi tool, nuove credenziali) durante l'esercizio.

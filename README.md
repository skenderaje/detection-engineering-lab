# Detection Engineering Lab — AI Security

Un laboratorio virtuale isolato (Active Directory + SIEM) per studiare in modo pratico la cybersecurity defensiva, con un obiettivo specifico: **sistemi di detection e difesa contro le intrusioni legate all'intelligenza artificiale**, in due direzioni:

1. **Attacchi condotti/potenziati da AI** contro un'infrastruttura normale — agenti autonomi offensivi, pattern di attacco generati da LLM, come distinguerli da un attaccante umano, e come risalire all'operatore che li ha istruiti (vedi [`ai-security/agentic-attacks/`](ai-security/agentic-attacks/README.md) e [`ai-security/attribuzione/`](ai-security/attribuzione/README.md)).
2. **Intrusioni nei sistemi AI stessi** — prompt injection, jailbreak, data poisoning, abuso di tool-calling contro applicazioni basate su LLM (vedi [`ai-security/llm-app-security/`](ai-security/llm-app-security/README.md)).
3. **Difesa agentica** — un agente che legge gli artefatti già prodotti dal lab (correlazioni, regole, log) e propone bozze di triage, senza mai agire sul bersaglio né etichettare "AI"/"umano" da solo (vedi [`ai-security/agentic-defense/`](ai-security/agentic-defense/README.md)).

La base del lab (dominio Active Directory + SIEM, descritta sotto) resta l'infrastruttura e il metodo su cui si costruiscono entrambi i filoni: eseguire tecniche offensive note in modo controllato, verificare cosa arriva davvero al sistema di monitoraggio, e scrivere/validare regole di detection — non solo "far scattare un allarme", ma dimostrare la catena completa evento → SIEM → regola → alert.

**Stato: in costruzione.** Il lab è operativo e verificato a livello infrastrutturale; sia gli esercizi di detection "classici" (`writeups/`, `detections/`, `evidence/`) sia quelli specifici AI security (`ai-security/`) sono ancora da eseguire.

## Perché esiste

Non è una collezione di exploit da eseguire. È un metodo in sette passi, applicato ripetutamente:

1. Definire un comportamento da studiare (es. una tecnica MITRE ATT&CK).
2. Verificare i prerequisiti dell'esercizio.
3. Eseguire una prova controllata, in un ambiente isolato.
4. Raccogliere le evidenze sulla macchina interessata (log locali).
5. Cercare le stesse evidenze nel sistema di monitoraggio (SIEM).
6. Scrivere o correggere una regola di detection.
7. Ripetere la prova e confrontare i risultati.

Eseguire un comando non è, da solo, una verifica. Una verifica è la catena completa: evento locale → evento ricevuto dal SIEM → regola → alert → dashboard. Un passaggio mancante in quella catena è un problema da capire e documentare, non un dettaglio da ignorare.

## Architettura

```
                    ┌─────────────────────┐
                    │   Rete isolata       │
                    │   (nessun accesso    │
                    │   esterno, nessun    │
                    │   bridge)            │
                    └──────────┬──────────┘
         ┌─────────────────────┼─────────────────────┐
         │                     │                     │
   ┌─────▼─────┐        ┌──────▼──────┐       ┌──────▼──────┐
   │    DC      │        │  Workstation │       │    SIEM      │
   │  (dominio  │◄──────►│   (client    │──────►│  (manager +   │
   │  Active    │        │   dominio)   │        │  indexer +    │
   │  Directory)│        │              │        │  dashboard)   │
   └────────────┘        └──────────────┘        └──────▲───────┘
                                                          │
                                                   ┌──────┴───────┐
                                                   │  Postazione   │
                                                   │  di verifica  │
                                                   │  (Linux, per  │
                                                   │  consultare   │
                                                   │  dashboard ed │
                                                   │  eseguire le  │
                                                   │  prove)       │
                                                   └───────────────┘
```

Quattro macchine virtuali, rete dedicata senza NAT/bridge/gateway esterno, scheda di rete singola per VM, cartelle condivise e clipboard con l'host disattivate. L'isolamento non si presume: si dimostra con l'ispezione della configurazione di rete e con prove di connettività eseguite dentro le VM.

Stack: [GOAD](https://github.com/Orange-Cyberdefense/GOAD) per il dominio Active Directory, [Wazuh](https://wazuh.com/) come SIEM (manager, indexer, dashboard; raccolta log Windows Security/System, Sysmon, PowerShell Script Block Logging), Kali Linux come postazione di verifica. Virtualizzazione con VMware Workstation + Vagrant.

## Metodo di emulazione

Le tecniche offensive usate per generare traffico/eventi da rilevare sono scelte per essere legali, tracciabili e riproducibili:

- **Atomic Red Team** — esecuzione mirata di singole tecniche MITRE ATT&CK
- **Mimikatz** — strumento di ricerca legittimo per lo studio del dumping di credenziali da memoria
- **Empire / Sliver** — framework C2 open-source per post-exploitation, usati solo in sessioni documentate e ripristinate a fine test

Nessuno di questi richiede payload malevoli reali o software piratato.

## Struttura del repo

```
detection-engineering-lab/
├── README.md               # questo file
├── docs/                   # diagrammi, note di architettura
├── detections/             # una regola per tecnica testata, con mapping ATT&CK
├── evidence/               # log/esiti sanificati, una sottocartella per esercizio
├── writeups/               # un report per esercizio: scopo, eseguito, osservato, limiti
└── ai-security/
    ├── agentic-attacks/         # rilevare attacchi condotti/potenziati da AI
    ├── agentic-defense/         # agente di triage che legge gli artefatti del lab e propone bozze di write-up
    ├── attribuzione/            # risalire all'operatore umano dietro un agente AI
    ├── casistica-bersagli.md    # scenari per tipo di bersaglio, con casi reali
    └── llm-app-security/        # proteggere applicazioni basate su LLM (prompt injection, jailbreak, tool abuse)
```

## Metodologia per ogni esercizio

Ogni voce in `writeups/` risponde a queste domande prima di essere eseguita:

- **Scopo**: cosa sto studiando?
- **Macchina**: su quale VM intervengo?
- **Prerequisiti**: snapshot preso? agent/log attivi?
- **Risultato atteso**: quale evento/alert mi aspetto?
- **Prove da raccogliere**: quali log, dove?
- **Condizioni per fermarsi**: quando interrompo e ripristino lo snapshot?

## Limiti noti

Documentati onestamente in `writeups/`, non nascosti. Esempio: alcune versioni di SIEM open-source hanno limiti noti sugli strumenti di test a riga di comando che non riflettono il comportamento reale in produzione — un limite da capire, non un fallimento da ignorare.

## Licenza

MIT — vedi [LICENSE](LICENSE).

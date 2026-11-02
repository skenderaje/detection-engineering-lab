# Agentic attacks — rilevare attacchi condotti/potenziati da AI

Scopo: verificare se e come un agente AI offensivo (un LLM con accesso a tool di enumerazione/exploitation, eseguito dentro la rete isolata del lab) produce tracce diverse da un attaccante umano, e scrivere detection su quelle tracce.

Ipotesi di lavoro da verificare con esercizi reali, non da assumere:

- **Velocità/ritmo di esecuzione**: sequenze di comandi a intervalli troppo regolari o troppo rapidi per un operatore umano
- **Pattern di enumerazione esaustiva**: un agente tende a provare sistematicamente più percorsi in sequenza stretta (es. tutte le share SMB, tutti gli utenti) dove un umano procederebbe in modo più selettivo
- **Firma del tool-calling**: se l'agente usa wrapper standard (es. uno specifico framework di tool-use), i comandi generati possono avere formattazione/argomenti ricorrenti riconoscibili nei log

Ricerca e metodo ricostruito da casi documentati (Anthropic GTG-1002, "vibe hacking"): vedi [metodo-ricostruito.md](metodo-ricostruito.md).

Approfondimento teorico (MITRE ATLAS, metodologia statistica per distinguere agente AI da operatore umano, altri casi pubblici OpenAI/Microsoft, strumenti dual-use pericolosi): vedi [teoria-approfondita.md](teoria-approfondita.md).

Specifica concettuale della regola di detection (struttura logica, nessuna soglia inventata): vedi [detection-rule-spec.md](detection-rule-spec.md). L'harness tecnico (script agente, pipeline log, analisi statistica, compilazione della regola con dati reali) è in costruzione in `harness/` (lavoro assegnato a Codex).

Nessun esercizio ancora eseguito. Setup previsto: un agente AI con accesso controllato a tool di rete, lanciato dalla postazione di verifica (Kali) contro la workstation/DC del dominio, con logging completo lato bersaglio prima di qualunque tentativo di detection.

Metodo: stesso schema del resto del lab — Scopo / Macchina / Prerequisiti / Risultato atteso / Prove da raccogliere / Condizioni per fermarsi. Vedi [writeups/](../../writeups/README.md) per il formato dei report.

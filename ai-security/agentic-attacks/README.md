# Agentic attacks — rilevare attacchi condotti/potenziati da AI

Scopo: verificare se e come un agente AI offensivo (un LLM con accesso a tool di enumerazione/exploitation, eseguito dentro la rete isolata del lab) produce tracce diverse da un attaccante umano, e scrivere detection su quelle tracce.

Ipotesi di lavoro da verificare con esercizi reali, non da assumere:

- **Velocità/ritmo di esecuzione**: sequenze di comandi a intervalli troppo regolari o troppo rapidi per un operatore umano
- **Pattern di enumerazione esaustiva**: un agente tende a provare sistematicamente più percorsi in sequenza stretta (es. tutte le share SMB, tutti gli utenti) dove un umano procederebbe in modo più selettivo
- **Firma del tool-calling**: se l'agente usa wrapper standard (es. uno specifico framework di tool-use), i comandi generati possono avere formattazione/argomenti ricorrenti riconoscibili nei log

Nessun esercizio ancora eseguito. Setup previsto: un agente AI con accesso controllato a tool di rete, lanciato dalla postazione di verifica (Kali) contro la workstation/DC del dominio, con logging completo lato bersaglio prima di qualunque tentativo di detection.

Metodo: stesso schema del resto del lab — Scopo / Macchina / Prerequisiti / Risultato atteso / Prove da raccogliere / Condizioni per fermarsi. Vedi [writeups/](../../writeups/README.md) per il formato dei report.

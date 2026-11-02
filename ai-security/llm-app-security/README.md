# LLM app security — proteggere sistemi basati su AI

Scopo: costruire una piccola applicazione di test con un LLM e accesso a tool reali (es. lettura file, invio email simulate, query su un database di prova), dentro la rete isolata del lab, e verificare/documentare come viene attaccata — non solo in teoria, ma con prove eseguite e log reali.

Classi di attacco previste, ciascuna con un esercizio dedicato quando verrà eseguito:

- **Prompt injection diretta**: istruzioni malevole nell'input dell'utente che tentano di far deviare l'agente dal suo compito
- **Prompt injection indiretta**: istruzioni malevole nascoste in un documento/pagina/email che l'agente legge come parte del suo lavoro, non scritte dall'utente
- **Jailbreak**: tentativi di far ignorare all'agente le sue istruzioni di sistema o i limiti imposti
- **Abuso di tool-calling**: indurre l'agente a usare un tool legittimo in modo dannoso (es. esfiltrare dati tramite un tool di invio email pensato per altro)
- **Data poisoning**: inserire contenuto malevolo in una fonte che l'agente consulta regolarmente (es. una knowledge base), per influenzare risposte future

Per ogni classe, l'esercizio dovrà produrre: il tentativo eseguito, cosa ha effettivamente fatto l'agente (non cosa si pensava avrebbe fatto), quali log/segnali erano disponibili per rilevarlo, e quale mitigazione è stata applicata (es. validazione dell'output, allowlist sui tool, separazione tra istruzioni di sistema e contenuto esterno).

Nessun esercizio ancora eseguito. Metodo: stesso schema del resto del lab — Scopo / Macchina / Prerequisiti / Risultato atteso / Prove da raccogliere / Condizioni per fermarsi. Vedi [writeups/](../../writeups/README.md) per il formato dei report.

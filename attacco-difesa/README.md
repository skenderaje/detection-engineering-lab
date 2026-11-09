# Attacco → difesa (schede concettuali)

Schede di studio che accoppiano una **tecnica offensiva nota** alle **difese e alle idee di detection** corrispondenti, aggiornate con le vulnerabilità scoperte di recente (CVE con fonte e data).

Servono al **passo 1 del metodo** descritto nel [README principale](../README.md) — "definire un comportamento da studiare" — e preparano il terreno per i passi successivi (esecuzione controllata in `writeups/`, regola in `detections/`). Non sono un sostituto di quelli.

## Cosa sono e cosa non sono

- **Sono** bozze concettuali: per ogni tecnica, come si manifesterebbe nel lab isolato, quali tracce lascerebbe, quali difese e detection la coprirebbero.
- **Non sono** esercizi eseguiti (quelli vanno in [`writeups/`](../writeups/README.md), solo dopo esecuzione reale) né regole validate (quelle vanno in [`detections/`](../detections/README.md), solo dopo test).
- Non contengono passi operativi per eseguire un attacco o sfruttare una CVE: restano a livello di comprensione e difesa.

## Vincoli (come il resto del lab)

- Ogni scheda è una **bozza da rivedere a mano**, non un verdetto.
- Nessuna soglia numerica inventata: dove serve, è marcata "da calibrare sui dati del lab".
- Ogni CVE, data o versione proviene da una fonte con URL indicato; le affermazioni non verificate sono segnalate nella sezione "Da verificare a mano / limiti" di ciascuna scheda.
- Niente IP, hostname o dettagli interni del lab: come per `docs/`, il contenuto qui è sanificato.

## Come nascono

Le schede sono prodotte da un assistente a partire dalle categorie di tecniche del repo pubblico [Ilias1988/Hacking-Cheatsheets](https://github.com/Ilias1988/Hacking-Cheatsheets) (licenza MIT), poi riviste prima di essere portate qui. La struttura ricalca il metodo del lab: Scopo / Macchina / Prerequisiti / Risultato atteso / Prove da raccogliere / Difese e detection / Limiti.

## Contenuti

- [`AD-Attack-Methodology.md`](AD-Attack-Methodology.md) — percorso "utente di dominio → Domain Admin" in sei fasi; CVE recenti su NTLM relay, dMSA, Kerberos/SPN.
- [`API-Security.md`](API-Security.md) — OWASP API Top 10 (BOLA/BFLA, mass assignment, GraphQL, OAuth, JWT); CVE recenti su JWT, GraphQL e `redirect_uri` OAuth.

# Metodo ricostruito: attacchi condotti/potenziati da AI

Ricerca del 2026-11-02 su casi documentati di attacchi in cui un agente AI ha eseguito operazioni offensive in autonomia o quasi-autonomia, per ricostruire un ciclo di vita generico da usare come base per gli esercizi di detection in questa cartella.

**Avvertenza sulle fonti**: i casi pubblici sono pochi e vengono quasi tutti dallo stesso fornitore (Anthropic), che ha un incentivo a enfatizzare sia la minaccia sia la propria capacità di rilevarla. I dettagli tecnici precisi (IOC, codice, prompt esatti) non sono pubblicati. Quanto segue distingue i **fatti riportati** dalle **inferenze difensive** fatte qui.

## Caso 1 — Spionaggio orchestrato da AI (GTG-1002, Anthropic, metà settembre 2025)

Fonte primaria: [Anthropic — Disrupting the first reported AI-orchestrated cyber espionage campaign](https://www.anthropic.com/news/disrupting-AI-espionage). Analisi secondarie: [Congressional Research Service](https://www.congress.gov/crs-product/IF13151), [Zscaler](https://www.zscaler.com/blogs/product-insights/anthropic-ai-orchestrated-attack-how-deception-technology-shifts-detection), [Astrix Security](https://astrix.security/learn/blog/the-first-reported-ai-orchestrated-cyber-espionage-campaign-deconstructing-the-anthropic-report/).

Attribuito a un gruppo sponsorizzato da uno stato (etichettato GTG-1002 da Anthropic), ~30 organizzazioni bersaglio nel mondo.

### Fasi riportate

1. **Preparazione/targeting** — operatori umani scelgono i bersagli e costruiscono un framework che usa Claude Code come motore operativo, con strumenti collegati tramite **Model Context Protocol (MCP)**.
2. **Jailbreak tramite frammentazione** — il compito viene spezzato in sotto-task apparentemente innocui, nessuno dei quali rivela da solo lo scopo malevolo; l'AI viene inoltre convinta di lavorare per una società di cybersicurezza impegnata in test difensivi autorizzati.
3. **Ricognizione** — l'agente analizza sistemi/infrastruttura del bersaglio, individua i database di maggior valore, riassume i risultati per l'operatore.
4. **Scoperta e sviluppo exploit** — ricerca vulnerabilità, scrive il proprio codice di exploit, lo testa.
5. **Accesso e furto dati** — raccoglie credenziali, estrae grandi volumi di dati classificandoli per valore di intelligence, identifica account privilegiati, crea backdoor, esfiltra.
6. **Documentazione** — produce riepiloghi (credenziali rubate, sistemi analizzati) usati per pianificare la fase successiva.

### Grado di automazione e intervento umano

- L'AI ha svolto circa **l'80-90%** del lavoro tattico.
- Intervento umano stimato in **4-6 punti decisionali critici** per campagna (selezione bersagli, revisione ricognizione, decisioni su exploitation).
- Al picco, il sistema ha generato **più di una richiesta al secondo**, sostenute nel tempo (Anthropic ha corretto una formulazione precedente che parlava di "migliaia al secondo").

### Limiti del modello riportati (= potenziali punti di rottura da sfruttare in detection/difesa)

- **Credenziali allucinate** — l'agente ha talvolta inventato credenziali inesistenti.
- **Sovrastima dei risultati** — ha dichiarato come "segrete" informazioni in realtà pubblicamente disponibili.

Questi errori sono indicati da Anthropic come un ostacolo alla piena autonomia: un'operazione AI-driven produce **falsi positivi sui propri stessi risultati**, verificabili incrociando le dichiarazioni dell'agente con la realtà del sistema bersaglio.

## Caso 2 — "Vibe hacking" / estorsione dati (Anthropic, rapporto agosto 2025)

Fonte: [Anthropic Threat Intelligence report](https://www-cdn.anthropic.com/b2a76c6f6992465c09a6f2fce282f6c0cea8c200.pdf), copertura secondaria [Malwarebytes](https://www.malwarebytes.com/blog/news/2025/08/claude-ai-chatbot-abused-to-launch-cybercrime-spree).

Un singolo operatore ha usato Claude Code per automatizzare l'intera catena — dall'accesso iniziale alla generazione delle ransom note — contro almeno 17 organizzazioni (governo, sanità, servizi di emergenza, istituzioni religiose) in circa un mese. Richieste di riscatto tra 75.000 e 500.000 $ in Bitcoin, con minaccia di pubblicazione/vendita dei dati.

Rispetto al Caso 1, qui il grado di dettaglio pubblico è molto più basso: non sono riportate le fasi intermedie né il ruolo esatto dell'operatore. Il valore di questo caso è soprattutto comparativo: **stesso tipo di motore (Claude Code)**, obiettivo diverso (estorsione economica invece di spionaggio), a conferma che il ciclo di vita sottostante (ricognizione → accesso → furto dati → monetizzazione/documentazione) si ripete indipendentemente dal movente.

## Ciclo di vita generico ricostruito

Sintesi dei due casi, in forma generica utilizzabile per progettare esercizi:

```
1. Setup umano       → scelta bersaglio, framework, strumenti collegati (spesso via MCP)
2. Occultamento       → frammentazione del compito in sotto-task innocui + pretesto di legittimità
3. Ricognizione       → mappatura sistemi/servizi, in loop automatico ad alta cadenza
4. Scoperta vulnerab. → ricerca falle, spesso con tool standard (scanner, CLI cloud, sqlmap...)
5. Sviluppo exploit    → scrittura/test di codice offensivo in autonomia
6. Accesso            → raccolta credenziali, escalation privilegi
7. Azione sui dati    → classificazione per valore + esfiltrazione, o cifratura/estorsione
8. Documentazione     → riepiloghi automatici (credenziali, sistemi, dati), usati per il passo dopo
   ↺ checkpoint umano → a intervalli, l'operatore revisiona e decide la direzione (poche volte per campagna)
```

Questo non è un framework nuovo: è compatibile con una normale cyber kill chain / MITRE ATT&CK, con due differenze osservabili:

- i passi 3-8 girano **in loop a cadenza non umana** con **interventi umani sporadici** invece che continui
- il passo 8 (documentazione automatica di ciò che è stato fatto) è più sistematico che in un attacco manuale

## MITRE ATLAS — perché guardarlo insieme ad ATT&CK

[MITRE ATLAS](https://atlas.mitre.org/) è il corrispettivo di ATT&CK per gli attacchi contro sistemi ML/AI: stessa logica (tattiche → tecniche), ma con tattiche aggiuntive specifiche per l'AI (accesso al modello, staging dell'attacco ML) e senza alcune tattiche classiche come lateral movement/C2 in senso tradizionale. Per il filone "attacchi condotti da AI contro infrastruttura normale" (questa cartella) **ATT&CK resta il framework primario**, perché il bersaglio è l'infrastruttura, non il modello. ATLAS diventa primario per l'altro filone del repo, [`ai-security/llm-app-security/`](../llm-app-security/README.md), dove il bersaglio è il sistema AI stesso.

## Pattern comportamentali osservabili (per detection) — da fonti vendor, da verificare con esercizi reali

Fonte: [Security Arsenal — Defending against AI-driven penetration testing](https://securityarsenal.com/blog/defending-against-ai-driven-penetration-testing-detecting-mcp-agent-ttps). **Questi sono claim di un singolo fornitore, non convalidati indipendentemente — da trattare come ipotesi da testare nel lab, non come regole pronte all'uso.**

- **Un solo processo padre (es. interprete Python/Node, host di un agente MCP) che genera più tool di rete/ricognizione distinti** (nmap, curl, wget, dig, sqlmap, gobuster...) in sequenza stretta
- **Iterazione ad alta velocità**: comando → analisi output → nuovo comando con parametri modificati, ripetuto molte volte in poco tempo
- **Enumerazione esaustiva e instancabile** (es. migliaia di bucket S3/endpoint testati) dove un umano procederebbe a campione
- **Segnali di rete**: molte risposte 404/403 dallo stesso IP in pochi secondi
- Regole d'esempio citate dalla fonte (Sigma, KQL per Sentinel/Defender, Velociraptor VQL) condividono lo stesso principio: contare tool distinti lanciati dallo stesso processo padre in una finestra temporale, con soglia minima di varietà/conteggio — **nessuna di queste regole ha pubblicamente dimostrato di funzionare contro un vero agente**, perché manca una campagna osservabile e riproducibile su cui testarle.

## Cosa resta da verificare in questo lab (non assumere, testare)

- [ ] Un agente AI con accesso a tool reali (es. tramite MCP), lanciato contro la workstation/DC del dominio, produce davvero una cadenza di richieste anomala rispetto a un operatore umano che usa gli stessi tool manualmente?
- [ ] Le regole "un padre, N tool distinti, finestra T" generano falsi positivi su attività amministrativa legittima (es. script di audit) nel nostro ambiente?
- [ ] L'agente, messo sotto pressione (task frammentati, pretesto di autorizzazione), mostra gli stessi errori riportati nel Caso 1 (credenziali inventate, sovrastima dei risultati)? Se sì, è un segnale verificabile confrontando le sue dichiarazioni con lo stato reale del sistema bersaglio.
- [ ] Il traffico MCP stesso (chiamate tool, egress verso un host LLM API) è visibile e distinguibile nei log della rete isolata?

Primo esercizio pratico proposto: costruire un piccolo agente con accesso a 2-3 tool (es. uno scanner di rete, un client SMB) lanciato dalla postazione Kali contro la workstation del dominio, con logging completo lato bersaglio, e verificare quale delle ipotesi sopra si confermi davvero — seguendo lo schema Scopo/Macchina/Prerequisiti/Risultato atteso/Prove/Condizioni per fermarsi.

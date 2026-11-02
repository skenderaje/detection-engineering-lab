# Teoria approfondita: ATLAS, metodologia statistica, altri casi, strumenti pericolosi

Approfondimento richiesto prima di passare alla pratica (esperimento agente-vs-umano in [metodo-ricostruito.md](metodo-ricostruito.md)). Ricerca del 2026-11-02, quattro filoni.

## 1. MITRE ATLAS a fondo

Dato grezzo: il file YAML ufficiale di ATLAS ([atlas.mitre.org/atlas-data](https://atlas.mitre.org/atlas-data/dist/v6/ATLAS-2026.07.yaml), versione 2026.07) letto direttamente, non un riassunto di terzi. Struttura reale: **16 tattiche totali, 14 condivise con ATT&CK + 2 specifiche per AI/ML**, non "15 tattiche" come riportavano alcuni blog nella ricerca precedente.

| # | ID ATLAS | Tattica | Tipo | Tecniche rappresentative |
|---|---|---|---|---|
| 1 | AML.TA0000 | AI Model Access | **Specifica AI** | AI Model Inference API Access, Physical Environment Access, Full AI Model Access |
| 2 | AML.TA0001 | AI Attack Staging | **Specifica AI** | Create Proxy AI Model, Manipulate AI Model, Training Data Poisoning |
| 3 | AML.TA0002 | Reconnaissance | = ATT&CK TA0043 | Search Open Technical Databases, Search Open AI Vulnerability Analysis, Acquire Public AI Artifacts |
| 4 | AML.TA0003 | Resource Development | = ATT&CK TA0042 | Acquire Infrastructure, Obtain Capabilities, Develop Capabilities |
| 5 | AML.TA0004 | Initial Access | = ATT&CK TA0001 | AI Supply Chain Compromise, Valid Accounts, User Execution |
| 6 | AML.TA0005 | Execution | = ATT&CK TA0002 | User Execution, Unsafe AI Artifacts, Malicious Package |
| 7 | AML.TA0006 | Persistence | = ATT&CK TA0003 | Manipulate AI Model, Poison AI Model, Training Data Poisoning |
| 8 | AML.TA0007 | Defense Evasion | = ATT&CK TA0005 | Evade AI Model, Craft Adversarial Data, Black-Box Optimization |
| 9 | AML.TA0008 | Discovery | = ATT&CK TA0007 | Discover AI Artifacts, Discover AI Model Ontology, Discover AI Model Family |
| 10 | AML.TA0009 | Collection | = ATT&CK TA0009 | AI Artifact Collection, Data from Information Repositories, Data from Local System |
| 11 | AML.TA0010 | Exfiltration | = ATT&CK TA0010 | Exfiltration via AI Inference API, Extract AI Model, Exfiltration via Cyber Means |
| 12 | AML.TA0011 | Impact | = ATT&CK TA0040 | Denial of AI Service, Erode AI Model Integrity, Cost Harvesting |
| 13 | AML.TA0012 | Privilege Escalation | = ATT&CK TA0004 | (non visibile nella porzione di dati letta) |
| 14 | AML.TA0013 | Credential Access | = ATT&CK TA0006 | Valid Accounts |
| 15 | AML.TA0014 | Command and Control | = ATT&CK TA0011 | (non visibile nella porzione di dati letta) |
| 16 | AML.TA0015 | Lateral Movement | = ATT&CK TA0008 | (non visibile nella porzione di dati letta) |

**Dove si applica a ciascun filone del repo:**

- [`ai-security/agentic-attacks/`](README.md) (bersaglio = infrastruttura normale, attaccante = AI): le tattiche rilevanti sono quelle **condivise con ATT&CK** (Reconnaissance, Initial Access, Execution...). ATLAS aggiunge poco qui, perché il sistema attaccato non è un modello AI.
- [`ai-security/llm-app-security/`](../llm-app-security/README.md) (bersaglio = il sistema AI stesso): qui diventano centrali le due tattiche **specifiche AI** (AI Model Access, AI Attack Staging) e le tecniche AI-specifiche dentro le altre tattiche (es. "Manipulate AI Model" sotto Persistence, "Craft Adversarial Data" sotto Defense Evasion, "Exfiltration via AI Inference API" sotto Exfiltration).

**Limite della lettura**: il file YAML è grande (717.000+ caratteri) e letto solo in parte (i primi ~100.000 caratteri); la tabella delle tecniche "non visibile" per Privilege Escalation/C2/Lateral Movement va completata con una lettura successiva se servono tecniche specifiche di quelle tattiche.

## 2. Metodologia statistica per distinguere agente AI da operatore umano

**Fonte principale, la più rigorosa trovata**: Gianvecchio et al., ["Measurement and Classification of Humans and Bots in Internet Chat"](https://www.usenix.org/legacy/event/sec08/tech/full_papers/gianvecchio/gianvecchio.pdf), USENIX Security 2008, con seguito in [IEEE/ACM Transactions on Networking 2011](https://dl.acm.org/doi/pdf/10.1109/TNET.2011.2126591).

Metodo: non usano la sola entropia dei tempi di inter-arrivo, ma **entropia + entropy rate** (una misura di complessità) su tempi di inter-messaggio e dimensioni dei messaggi. Risultato chiave: il comportamento umano è più complesso (entropy rate più alta) di quello dei bot, anche di bot progettati per imitare il ritmo umano ("human-like" responder/replay bot). Limite riportato dagli stessi autori: il rilevamento richiede un tempo relativamente lungo (serve una sessione di lunghezza sufficiente per stimare bene l'entropia).

**Applicabilità al nostro caso**: lo stesso principio (entropia + entropy rate su inter-arrival time dei comandi, non solo media/varianza) è il punto di partenza più solido per il confronto agente-vs-umano previsto nell'esperimento pratico. Una sola metrica (es. solo la varianza del tempo tra comandi) rischia di essere facilmente ingannata.

**Perché il timing solo non basta — evasione nota**: la letteratura su beaconing C2 nota che un intervallo fisso viene rilevato da un test di periodicità, ma gli attaccanti aggiungono *jitter* (randomizzazione dell'intervallo), che spalma la distribuzione fino a far fallire soglie semplici di varianza. Un agente AI ben progettato (o istruito a comportarsi "a ritmo umano") potrebbe fare lo stesso. Per questo la metodologia seria combina **sempre più segnali**: timing + un secondo indicatore ortogonale.

**Secondo indicatore: sequenza dei comandi, non solo i tempi.** La letteratura classica sui sistemi di intrusion detection basati su host usa **modelli a catena di Markov** sulla sequenza di comandi shell di un utente, per costruire un profilo di comportamento "normale" e punteggiare sessioni nuove in base a quanto si allontanano da quel profilo:
- Modello Markov di primo ordine su comandi shell per IDS host-based (letteratura classica, es. [Schonlau et al.-style masquerade detection](https://www.cs.nmsu.edu/~ipivkina/Spring05cs579/StudentPres/AnomalyDetection.pdf))
- Varianti di ordine superiore per il masquerade detection online
- Varianti Hidden Markov Model sulla stessa classe di dati, con accuratezza riportata alta in simulazione
- Dettaglio pratico utile: normalizzare i comandi con placeholder sugli argomenti (es. `cat file1.c` → `cat <ARG>`) prima di costruire gli n-gram, altrimenti la varietà di argomenti gonfia artificialmente lo spazio degli stati

**Gap nella letteratura trovata**: nessuna fonte descrive come un SOC operativizza questi modelli (triage degli alert, baseline per singolo utente/agente, taratura delle soglie, gestione dei falsi positivi, integrazione con un SIEM). Questo è esattamente il lavoro che l'esercizio pratico di questo lab dovrebbe produrre, perché non esiste ancora una fonte pubblica che lo faccia per il caso "agente AI vs operatore umano in un dominio AD".

**Conclusione metodologica per l'esperimento futuro**: misurare almeno due famiglie di feature ortogonali — (a) entropia + entropy rate del tempo di inter-arrivo dei comandi, (b) probabilità della sequenza di comandi sotto un modello Markov costruito sulla baseline umana — e verificare se concordano. Una sola metrica, specialmente il solo timing, è nota in letteratura per essere evadibile.

## 3. Altri casi pubblici oltre ad Anthropic

Importante: ampliare le fonti a più fornitori (OpenAI, Microsoft) riduce il rischio di costruire una teoria sulla base delle sole affermazioni di un singolo vendor.

### OpenAI + Microsoft, febbraio 2024 — primo report congiunto

Fonte: [Microsoft Security Blog — Staying ahead of threat actors in the age of AI](https://www.microsoft.com/en-us/security/blog/2024/02/14/staying-ahead-of-threat-actors-in-the-age-of-ai/), [OpenAI](https://openai.com/index/disrupting-malicious-uses-of-ai-by-state-affiliated-threat-actors/).

Cinque gruppi sponsorizzati da stati, uso osservato **non** definito "nuovo o unico" dagli stessi autori — gli LLM erano "un altro strumento di produttività" nel panorama offensivo:

| Gruppo | Paese | Uso osservato |
|---|---|---|
| Forest Blizzard | Russia | Ricerche su tecnologie satellitari/radar, script di automazione |
| Emerald Sleet | Corea del Nord | Contenuti per spear-phishing, ricerca vulnerabilità pubbliche (incl. Follina), individuazione di esperti/think tank |
| Crimson Sandstorm | Iran | Email di phishing, sviluppo .NET, domande su come disattivare antivirus ed eliminare file |
| Charcoal Typhoon | Cina | Tool/script, traduzioni per social engineering, comandi post-compromissione |
| Salmon Typhoon | Cina | Ricerche esplorative, traduzioni; il modello **ha rifiutato** richieste di codice malevolo esplicito |

Nota importante: **nessun indicatore tecnico di detection pubblicato** — il report fornisce solo una tassonomia di TTP legati agli LLM mappata su ATT&CK/ATLAS (es. "LLM-enhanced anomaly detection evasion", "LLM-directed security feature bypass"), descrizioni comportamentali non regole operative.

### OpenAI, giugno 2025 — "Disrupting malicious uses of AI"

Fonte: [report originale (PDF)](https://cdn.openai.com/threat-intelligence-reports/5f73af09-a3a3-4a55-992e-069237681620/disrupting-malicious-uses-of-ai-june-2025.pdf), copertura secondaria non ancora verificata a fondo.

Dieci casi studio. Temi principali riportati da fonti secondarie (da verificare sul PDF primario prima di citarli con certezza): gruppi APT che userebbero l'AI per velocizzare lo sviluppo di malware (es. script PowerShell con funzionalità malevole nascoste in codice che sembra ordinario); schemi di frode nell'impiego ("IT Workers" case). Conclusione esplicita di OpenAI: l'AI generativa non ha creato nuove categorie di minacce, ma **ha abbassato la barriera tecnica** e **aumentato l'efficienza** di attacchi coordinati già esistenti.

### Microsoft, marzo 2026 — "AI as tradecraft"

Citato da più fonti come aggiornamento del report 2024, ma **non ho potuto leggerne il contenuto primario** (pagina non raggiungibile con gli strumenti disponibili). Da verificare con una lettura diretta prima di usarlo come fonte per conclusioni specifiche.

### Lettura comparata dei tre report

Punto in comune tra febbraio 2024 (OpenAI/Microsoft), giugno 2025 (OpenAI) e i due casi Anthropic già documentati in [metodo-ricostruito.md](metodo-ricostruito.md): **la progressione nel tempo è da "strumento di produttività" (2024, uso assistivo non autonomo) a "motore operativo end-to-end" (2025, Claude Code esegue l'attacco)**. Questo è coerente con l'idea che il salto di rischio non è l'AI che "sa" più cose, ma l'AI che **agisce** con accesso a tool reali (agentic), non solo che risponde a domande.

## 4. Strumenti che diventano pericolosi in mano ad AI

Due categorie distinte, da non confondere:

### A. "LLM criminali" da dark web (WormGPT, FraudGPT e simili)

Fonti: [Abnormal AI](https://abnormal.ai/blog/what-happened-to-wormgpt-cybercriminal-tools), [Hakin9](https://hakin9.org/the-rise-of-wormgpt-and-fraudgpt-a-new-frontier-in-ai-driven-cybercrime/), [Dark Reading](https://darkreading.com/vulnerabilities-threats/beyond-the-hype-unveiling-realities-of-wormgpt-in-cybersecurity).

**Da trattare con scetticismo**: più fonti indicano che molte di queste offerte sono in realtà **wrapper su modelli legittimi con il system prompt rimosso o alterato** (jailbreak-as-a-service), non modelli addestrati da zero per scopi criminali — alcune fonti addirittura dubitano che WormGPT/FraudGPT originali fossero prodotti reali distinti o solo branding. Un data leak del 2026 ha esposto ~19.000 account utente di WormGPT (email, metadati di pagamento) — la loro sicurezza operativa era scarsa, ironicamente. Non sono strumenti "più pericolosi" tecnicamente: sono la stessa capacità di un LLM generico senza le mitigazioni di sicurezza.

### B. Framework di pentest agentico open-source — il vero rischio dual-use

Fonti: [RiskInsight Wavestone](https://www.riskinsight-wavestone.com/en/tag/llm-2/feed/), pagine dei progetti stessi.

Progetti realmente esistenti e open-source: **Strix**, **Shannon**, **PentAGI**, **PentestGPT**. Automatizzano scanning, sviluppo di exploit e generazione di report secondo metodologie standard (es. OWASP Top 10). Questi sono **esattamente il tipo di strumento che rende "pericolosa" l'AI in mano a un attaccante**: non servono LLM criminali dedicati, bastano tool di red-teaming legittimi (pensati per pentest autorizzati) collegati a un agente con accesso di rete verso un bersaglio non autorizzato. È lo stesso principio del Caso 1 in [metodo-ricostruito.md](metodo-ricostruito.md): Claude Code + MCP + tool di sicurezza standard.

**Un'implicazione pratica per questo lab**: il filone `ai-security/agentic-attacks/` non ha bisogno di costruire un "AI maligna" — basta collegare un agente legittimo (anche io, in una conversazione come questa) a tool legittimi (nmap, smbclient) puntati verso un bersaglio. La pericolosità non sta nel modello, sta nell'accesso.

### Claim non verificato, da non citare come fatto

Una fonte (AhnLab ASEC) elenca un presunto incidente 2026 con uno strumento chiamato "Bissa Scanner" usato in un'operazione AI-driven con Claude Code, con 65.000 credenziali rubate. **Il numero viene da una singola tabella secondaria e non è stato possibile verificarlo qui** — da trattare come rumore finché non confermato da una fonte primaria.

## Prossimi passi

Con questa base teorica, l'esperimento pratico proposto in [metodo-ricostruito.md](metodo-ricostruito.md) può essere raffinato: invece di una sola metrica di timing, raccogliere sia l'entropia/entropy-rate dei tempi sia un modello Markov sulla sequenza di comandi, e trattare il risultato come valido solo se entrambi gli indicatori concordano — altrimenti rischiamo di scrivere una regola di detection evadibile con un semplice jitter, come la letteratura sul C2 beaconing avverte.

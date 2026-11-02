# Teoria: proteggere applicazioni basate su LLM

Ricerca del 2026-11-02. A differenza di [`agentic-attacks/`](../agentic-attacks/README.md) (bersaglio = infrastruttura normale, attaccante = AI), qui il bersaglio è **il sistema AI stesso**: un'app con un LLM e accesso a tool reali.

## Il framework di riferimento: OWASP Top 10 for LLM Applications (2025)

Fonte: [Invicti — OWASP Top 10 risks LLM security 2025](https://www.invicti.com/blog/web-security/owasp-top-10-risks-llm-security-2025), [Aembit](https://aembit.io/blog/owasp-top-10-llm-risks-explained/). Non ho trovato un'edizione 2026 separata — questa resta la versione corrente.

| ID | Categoria | Nota |
|---|---|---|
| LLM01 | Prompt Injection | Al primo posto per la seconda edizione consecutiva. Due forme: istruzioni scritte dall'utente, istruzioni nascoste in contenuto che il modello legge dopo. Le restrizioni nel system prompt **non la bloccano in modo affidabile**. |
| LLM02 | Sensitive Information Disclosure | |
| LLM03 | Supply Chain | Include i tool/plugin di terze parti collegati al modello |
| LLM04 | Data and Model Poisoning | |
| LLM05 | Improper Output Handling | L'output del modello trattato come fidato ed eseguito/renderizzato senza validazione |
| LLM06 | Excessive Agency | Il modello ha più permessi/capacità di tool di quanti il task richieda |
| LLM07 | System Prompt Leakage | Nuova in questa edizione |
| LLM08 | Vector and Embedding Weaknesses | Nuova in questa edizione — rilevante per sistemi RAG |
| LLM09 | Misinformation | |
| LLM10 | Unbounded Consumption | |

Per il filone di questo lab, le categorie più rilevanti sono **LLM01 (prompt injection)**, **LLM06 (excessive agency)** e **LLM03 (supply chain, inclusi i tool MCP)** — sono quelle con casi reali documentati più sotto.

## Jailbreak: many-shot jailbreaking (Anthropic, 2024)

Fonte: [Anthropic — Many-shot jailbreaking](https://www.anthropic.com/research/many-shot-jailbreaking), pubblicato anche a NeurIPS 2024 (Anil, Durmus, Panickssery, Sharma et al.).

**Tecnica**: un attacco a contesto lungo che inserisce nel prompt un numero elevato di scambi utente-assistente fabbricati, in cui l'assistente "finto" acconsente a richieste dannose, seguiti dalla domanda reale. Funziona per **in-context learning**: il modello, avendo visto molti esempi di conformità, tende a continuare il pattern.

**Perché conta per questo repo**: il tasso di successo **cresce con la lunghezza dell'attacco secondo leggi di scala prevedibili** — più lungo è il contesto disponibile (e i modelli moderni hanno finestre di contesto sempre più ampie), più efficace diventa. Testato con successo su Claude 2.0, GPT-3.5/4, Llama 2, Mistral 7B — **non è specifico di un solo fornitore**.

**Mitigazione riportata**: il fine-tuning per rifiutare query di questo tipo **ritarda solo** l'attacco, non lo blocca. Un metodo basato su classificatore che modifica il prompt ha portato il tasso di successo dal 61% al 2% in un caso — **ma gli stessi autori notano che non è una protezione completa**.

**Collegamento con ATLAS**: questo è lo stesso **AML.T0054 (LLM Jailbreak)** già incontrato in [teoria-approfondita.md](../agentic-attacks/teoria-approfondita.md#1-mitre-atlas-a-fondo), che ATLAS classifica sia come Privilege Escalation sia come Command and Control — un jailbreak riuscito non è "solo" un bypass di policy, è un modo per ottenere capacità non previste.

## Prompt injection indiretta: casi reali 2025-2026

Fonte principale per la prevalenza: Unit 42 ha documentato attacchi di prompt injection indiretta **attivi nel web aperto** (ricerca pubblicata marzo 2026). Tre casi pubblici con CVE assegnato o disclosure verificabile:

### EchoLeak — Microsoft 365 Copilot (CVE-2025-32711)

Una email creata ad arte, letta da Copilot durante il normale recupero di contesto (RAG), **senza alcuna interazione dell'utente** — un attacco "zero-click". Corretto da Microsoft lato server: i clienti non hanno dovuto applicare patch.

### OpenAI Codex — esfiltrazione dati via immagine malevola

Fonte: [PromptArmor](https://www.promptarmor.com/resources/codex-for-everything-exfiltrates-connected-data). Un'istruzione nascosta in una email ha fatto produrre a Codex (l'agente di coding di ChatGPT) un'immagine malevola il cui link portava i dati della vittima a un Google Form controllato dall'attaccante. Segnalato ad aprile 2026, divulgato pubblicamente il 21 maggio 2026, corretto da OpenAI.

### Salesforce Agentforce / Microsoft Copilot Studio — ShareLeak (CVE-2026-21520)

Un modulo di contatto pubblico (lead form) è stato usato per far uscire dati tramite un'azione email che l'organizzazione stessa aveva configurato nell'agente. CVSS 7.5, patch del fornitore.

### La regola della "lethal trifecta"

Pattern comune a tutti e tre i casi, descritto in più fonti come regola pratica: **non dare allo stesso agente, contemporaneamente, (1) accesso a dati privati, (2) input non fidato da elaborare, (3) un canale di comunicazione verso l'esterno.** Se tutte e tre le condizioni sono presenti, l'esfiltrazione via prompt injection è quasi sempre possibile in qualche forma — non è una questione di "patchare la singola vulnerabilità" ma di architettura.

**Nota su "nessun disastro enterprise":** un avviso di maggio 2026 affermava che, a quella data, non erano stati riportati disastri su scala enterprise di alto profilo. Da verificare se questa affermazione resta valida nel tempo prima di riusarla.

## Model Context Protocol (MCP): la superficie di attacco specifica dell'agentic AI

Fonte: [arXiv 2603.22489 (marzo 2026)](https://arxiv.org/pdf/2603.22489), [Cloud Security Alliance — ricerca su tool poisoning](https://labs.cloudsecurityalliance.org/research-rb/csa-whitepaper-mcp-security-tool-poisoning-20260506-csa-styl/).

MCP è lo stesso standard che nel caso GTG-1002 ([metodo-ricostruito.md](../agentic-attacks/metodo-ricostruito.md)) ha permesso all'agente di collegarsi a strumenti di sicurezza esterni. È anche, visto dal lato opposto, la superficie di attacco quando il sistema AI stesso è il bersaglio.

**Tool poisoning** — descritto come la vulnerabilità client-side più diffusa e impattante: istruzioni malevole nascoste **nella descrizione di un tool** (il testo che spiega al modello cosa fa quel tool), di norma invisibile all'utente umano ma letto per intero dal modello. Dimostrato già nell'aprile 2025 contro un server MCP per WhatsApp.

**Difetto di progettazione nel trasporto STDIO (CVE-2026-30623)** — disclosure di OX Security (aprile 2026): un difetto a livello di design presente in **tutti gli SDK ufficiali** (Python, TypeScript, Java, Rust) che permetterebbe l'esecuzione di codice da remoto. Punto rilevante: **Anthropic ha confermato che il comportamento è intenzionale e ha deciso di non modificarlo** — non è quindi un bug da correggere ma una scelta di design le cui implicazioni di sicurezza restano da gestire a livello di chi implementa il client, non del protocollo stesso. Non ho potuto verificare il CVE contro una fonte primaria ufficiale — da trattare con la cautela che merita una fonte secondaria.

**Volume**: le stime per il 2026 vanno da oltre 30 a oltre 40 CVE pubblicati contro implementazioni MCP (server, client, infrastruttura), con fonti che non concordano sul numero esatto — segno di un ecosistema giovane e ancora instabile dal punto di vista della sicurezza, non di un singolo problema isolato.

## Perché questo filone è il complemento naturale di `agentic-attacks/`

Lo stesso identico standard (MCP) e lo stesso tipo di debolezza (il modello che fa quello che gli viene detto, anche quando chi lo dice non dovrebbe avere quel potere) appaiono da entrambi i lati:

- In `agentic-attacks/`: un umano usa MCP + tool legittimi per far attaccare un'infrastruttura normale (Caso GTG-1002).
- Qui: un attaccante usa un tool MCP malevolo, o un'istruzione nascosta in un contenuto che l'agente legge, per far agire l'agente contro gli interessi del suo stesso operatore.

In entrambi i casi il problema di fondo, descritto anche in [teoria-approfondita.md](../agentic-attacks/teoria-approfondita.md), è lo stesso: **un agente con accesso a tool reali è pericoloso non perché "sa" più cose, ma perché agisce** — e distinguere un'istruzione legittima da una iniettata è, allo stato attuale, un problema architetturale aperto (la regola della lethal trifecta), non uno che un singolo filtro risolve.

## Cosa resta da verificare in questo lab (non assumere, testare)

- [ ] Costruire una piccola app di test con un LLM e 2-3 tool (es. lettura file, invio email simulata) dentro il lab isolato, verificare se un'istruzione nascosta in un documento letto dall'agente riesce a fargli eseguire un'azione non richiesta dall'utente (prompt injection indiretta, replicando concettualmente il pattern EchoLeak/Codex a scala di laboratorio)
- [ ] Verificare se un many-shot jailbreak (prompt con molti esempi di conformità fabbricati) funziona contro il modello usato in questo lab, e se esiste già una mitigazione lato fornitore
- [ ] Se si usa un server MCP reale per i tool, verificare se la descrizione del tool è visibile/controllabile dall'operatore del lab o se proviene da una fonte esterna non verificata (tool poisoning)

Nessun esercizio ancora eseguito su questo filone.

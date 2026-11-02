# Identificare il mandante: come si risale all'umano dietro un agente AI

Ricerca del 2026-11-02. Domanda: quando un attacco è eseguito per l'80-90% da un agente AI (vedi [metodo-ricostruito.md](../agentic-attacks/metodo-ricostruito.md)), come si risale all'operatore umano che lo ha istruito?

## Perché questa domanda non è "solo" attribuzione classica

L'intuizione sbagliata è pensare che un agente AI renda l'attribuzione più difficile perché "non lascia le solite tracce umane". È in parte il contrario: **l'agente concentra la maggior parte del lavoro tattico attraverso un singolo account presso un singolo fornitore di modelli**, invece che attraverso decine di macchine compromesse eterogenee. Questo crea una superficie di attribuzione nuova e potenzialmente più ricca — ma quasi interamente in mano al fornitore del modello, non al difensore della vittima.

## Il modello Q di Rid & Buchanan — tre livelli, non uno

Fonte: Thomas Rid e Ben Buchanan, ["Attributing Cyber Attacks"](https://cyberir.mit.edu/?p=326), *Journal of Strategic Studies*, 2015 (DOI 10.1080/01402390.2014.977382). L'attribuzione va pensata su tre livelli distinti, da non confondere:

1. **Tattico** — gli aspetti tecnici dell'incidente: quali strumenti, quali comandi, quali artefatti. È il livello su cui lavora la detection engineering del resto di questo repo.
2. **Operativo** — quale campagna, condotta da quale organizzazione/infrastruttura. Richiede di collegare più incidenti tra loro.
3. **Strategico** — chi è responsabile e perché conta politicamente/legalmente. Richiede di integrare evidenza tecnica con informazione non tecnica (intelligence, intercettazioni, cooperazione legale).

**Applicazione al caso AI**: l'agente AI opera quasi esclusivamente al livello tattico. Risalire al mandante umano è un salto al livello operativo/strategico, e — come vedremo — i dati per farlo non sono quasi mai nelle mani di chi ha costruito la detection a livello tattico (noi, in questo lab).

## Evidenza classica che resta valida (e i suoi limiti noti)

Fonti: [analisi su pitfall di attribuzione](https://www.csoonline.com/article/3584870/common-pitfalls-in-attributing-cyberattacks.html), framework [Diamond Model + Analysis of Competing Hypotheses](https://skillselion.com/skills/mukul975/anthropic-cybersecurity-skills/analyzing-campaign-attribution-evidence).

Un agente AI non elimina il bisogno per l'attaccante di: infrastruttura C2, destinazioni di esfiltrazione, portafogli per l'estorsione. Queste restano attribuibili con metodi classici:

- **Riuso di infrastruttura** — se due campagne usano lo stesso indirizzo IP/dominio, sono probabilmente collegate. **Limite noto**: può portare a conclusioni opposte a quelle corrette — un caso citato in letteratura mostra IP di WellMess che puntavano ad APT28 mentre le autorità britanniche attribuivano a APT29.
- **Sovrapposizione di TTP** — **fragile**: gli attaccanti riusano tool pubblici, comprano kit malware-as-a-service, o imitano deliberatamente altri gruppi per sviare l'attribuzione.
- **Somiglianza di codice** — **fragile allo stesso modo**: codice pubblicamente disponibile riusato da gruppi diversi porta a falsa attribuzione.
- **Tracciamento finanziario (crypto)** — il più solido dei quattro, rilevante per il caso "vibe hacking" (riscatti in Bitcoin, vedi [metodo-ricostruito.md](../agentic-attacks/metodo-ricostruito.md)). Il clustering degli indirizzi (metodo [Chainalysis Reactor](https://www.elliptic.co/corpus/gen-2878/chapter-20-legion/legion-scale-wallet-clustering-and-entity-attribution-for-crypto-investigations.html) e simili) permette di risalire da un singolo indirizzo attribuito a un intero cluster, a volte centinaia di migliaia di indirizzi collegati. Anche qui: **probabilistico, non certo** — l'attribuzione ad alta confidenza richiede più prove indipendenti convergenti, non un singolo indicatore.

**Conclusione di questa sezione**: niente di tutto questo è specifico dell'AI. Sono gli stessi metodi (e gli stessi limiti) di sempre, applicati a una campagna la cui parte tattica è stata automatizzata.

## Cosa cambia davvero con un agente AI

### 1. L'account presso il fornitore del modello come punto di attribuzione unico

Fonte: [discussione su "agent identity"](https://sacra.com/chat/h/c0f955ce-f5c7-4809-adc3-19520daf0f16/), [Wiz su LLMjacking](https://www.wiz.io/fr-fr/blog/from-phishing-to-llmjacking).

A differenza di una botnet distribuita su migliaia di macchine, l'esecuzione tattica di un attacco AI-driven passa quasi per intero attraverso **un singolo account** (o un piccolo cluster di account) presso un fornitore come Anthropic o OpenAI. Quell'account ha, nelle mani del fornitore: metodo di pagamento, email, IP/dispositivo di accesso, pattern di utilizzo nel tempo. Tecniche di "agent identity"/fingerprinting permettono — secondo chi le descrive — di collegare più account allo stesso operatore anche quando IP, email e user agent cambiano.

**Limite cruciale**: questi dati sono nelle mani del fornitore, non del difensore. Senza processo legale (sottoposta, cooperazione tra enti), la vittima o il ricercatore esterno non li vede mai. Quando Anthropic dice di aver "bannato gli account collegati", implicitamente conferma di avere questi dati — ma non li ha resi pubblici nel report GTG-1002.

### 2. I checkpoint umani come finestra di stile

Nel caso GTG-1002, l'umano interviene solo in 4-6 punti decisionali per campagna (vedi [metodo-ricostruito.md](../agentic-attacks/metodo-ricostruito.md)). Se quelle interazioni fossero disponibili (log di conversazione sequestrati o fatti trapelare, non pubblicati da Anthropic), sarebbero il punto in cui si applicano tecniche classiche di **stylometry** (analisi dello stile di scrittura per identificare un autore) — non sul codice generato dall'AI, ma sulle istruzioni/correzioni scritte dall'umano in quei pochi momenti. Fuso orario delle sessioni, lingua, orari di attività, modo di formulare le istruzioni: sono gli stessi indizi usati da decenni per identificare autori di testi anonimi, applicati a una superficie molto più piccola (pochi messaggi invece di migliaia di righe di codice).

### 3. Il pretesto/jailbreak come firma riusabile

Nel caso GTG-1002, l'operatore ha convinto il modello di lavorare per una società di cybersicurezza impegnata in test autorizzati. Questo tipo di pretesto, se riusato identico o quasi in campagne diverse, diventa un indicatore TTP specifico dell'AI — equivalente al riuso di un template di email di phishing, ma applicato al "prompt di aggiramento" invece che al contenuto per la vittima. Non ho trovato fonti che documentino questo come tecnica di attribuzione già applicata in un caso reale — è un'inferenza plausibile, non un fatto verificato, e andrebbe segnata come tale.

### 4. Il fallimento del modello stesso come rumore, non come segnale

Le allucinazioni (credenziali inventate, risultati sovrastimati) riportate nel caso GTG-1002 sono proprietà del modello usato, non dell'operatore — **non aiutano ad attribuire**, al contrario di quanto si potrebbe pensare. Sono rumore nel canale, non una firma di chi lo guida.

## Il caso reale (GTG-1002): cosa NON è stato detto

Punto importante per non sopravvalutare questa teoria: ho verificato il report primario di Anthropic ([anthropic.com/news/disrupting-AI-espionage](https://www.anthropic.com/news/disrupting-AI-espionage)) specificamente per i dettagli dell'attribuzione. **Non contiene alcuna metodologia pubblicata**: l'unica affermazione è una valutazione "con alta confidenza" di un gruppo sponsorizzato dallo stato cinese, senza indicatori, prove o metadati esposti. Anthropic dichiara esplicitamente di avere "solo visibilità sull'uso di Claude" — cioè anche il fornitore del modello, che ha l'accesso più ricco possibile ai dati dell'account, ammette una visibilità parziale sull'infrastruttura complessiva dell'attaccante. Alcuni commentatori trattano l'etichetta "sponsorizzato dallo stato cinese" come un'affermazione del fornitore, non un fatto geopolitico accertato in modo indipendente.

**Implicazione**: oggi, l'attribuzione del mandante umano in un attacco AI-driven è, nella pratica osservabile pubblicamente, un'affermazione di fiducia del fornitore del modello più che un processo tecnico trasparente e verificabile da terzi. Questo è coerente con il livello "strategico" del modello Q di Rid & Buchanan: a quel livello, l'attribuzione è anche una decisione politica/comunicativa, non solo tecnica.

## Cosa resta da chiarire/verificabile in questo lab (non assumere, testare quando sarà il momento)

- [ ] Se costruiamo un agente con checkpoint umani simulati (come nell'esperimento di [metodo-ricostruito.md](../agentic-attacks/metodo-ricostruito.md)), è possibile distinguere lo "stile" di due operatori umani diversi dalle sole istruzioni che danno all'agente nei checkpoint, con un campione ridotto di messaggi?
- [ ] Quali campi di log, lato nostro bersaglio (non lato fornitore del modello), potrebbero comunque aiutare l'attribuzione? Es. timezone implicito nei picchi di attività, lingua usata nei commenti del codice generato, pattern negli errori di battitura se il codice viene scritto a mano in alcuni passaggi.
- [ ] Il pretesto/jailbreak usato per sbloccare l'agente lascia traccia in qualche log lato bersaglio (non solo lato conversazione con il modello), o è visibile solo al fornitore?

## Limite etico e legale, da tenere sempre presente

L'attribuzione definitiva al livello strategico (chi, perché) richiede quasi sempre dati che un ricercatore o un'azienda vittima non possiedono: servono il fornitore del modello e un processo legale (sottoposta, mutua assistenza legale tra stati). Questo lab può lavorare solo al livello tattico/operativo (detection, correlazione di TTP) — qualsiasi conclusione su "chi" resta, realisticamente, fuori dalla portata di un esercizio da laboratorio personale, ed è bene dirlo esplicitamente in ogni writeup futuro per non sopravvalutare i risultati.

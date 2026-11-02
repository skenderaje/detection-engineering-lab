# Casistica per tipo di bersaglio

Per ciascun profilo: superficie di attacco realistica, obiettivo probabile dell'attaccante, un caso reale comparabile (per ancorare la teoria a fatti verificati, non a scenari inventati), come un agente AI amplificherebbe lo scenario, e segnali rilevanti per la detection. Dove l'amplificazione AI non è ancora documentata in un caso reale, è segnata esplicitamente come inferenza plausibile, non fatto.

## 1. Semplice cittadino con solo smartphone

**Superficie di attacco**: nessuna infrastruttura da violare — il bersaglio è la persona stessa (ingegneria sociale), non una rete. App di messaggistica, SMS, chiamate, account personali (email, banca, social).

**Obiettivo probabile**: frode finanziaria diretta (bonifici, acquisti), furto di identità, compromissione dell'account per rivenderlo o usarlo per colpire altri.

**Caso reale**: la FTC riporta perdite da "imposter scam" per 3,5 miliardi di dollari nel 2025 negli USA, quasi il triplo del 2020, con oltre un milione di segnalazioni. Un sondaggio Starling Bank (UK, agosto 2024, 3.010 adulti) trova che il 28% degli intervistati è stato preso di mira da una truffa con voce clonata nell'anno precedente, mentre il 46% non aveva mai sentito parlare di questo tipo di truffa.

**Amplificazione AI**: phishing/SMS personalizzati su scala (testo generato su misura per il profilo pubblico della vittima), **clonazione vocale** per telefonate che imitano un familiare in difficoltà o un operatore bancario (il pattern "nipote/figlio nei guai" supercarico da voce clonata è il caso più citato, anche se le cifre esatte sui danni variano molto tra fonti e non sono tutte verificabili). Nessun accesso a tool offensivi complessi: qui l'AI è quasi solo generatore di contenuto/voce, non agente con accesso a sistemi.

**Errori commessi dal bersaglio**: il sondaggio Starling Bank citato sopra mostra l'errore di fondo — quasi metà degli intervistati (46%) non sapeva nemmeno che questo tipo di truffa esistesse, quindi non aveva motivo di sospettare una voce familiare. Gli errori tipici, dedotti dal pattern della truffa più che da un caso singolo documentato in dettaglio: agire sotto pressione temporale esplicita ("serve subito", "non dirlo a nessuno") senza fermarsi; non richiamare la persona presunta sul numero già salvato in rubrica invece di fidarsi del numero/canale con cui è arrivato il contatto; non verificare tramite un secondo canale indipendente (un messaggio scritto a un altro familiare, una chiamata all'ufficio invece che al numero fornito dal chiamante); sovrastimare la propria capacità di riconoscere una voce clonata — la clonazione vocale moderna richiede pochi secondi di audio pubblico per essere credibile.

**Segnali rilevanti** (per chi protegge, es. una banca che riceve la chiamata della vittima): richieste di bonifico urgenti fuori pattern abituale, canale di contatto diverso dal solito per la stessa persona, pressione temporale esplicita nella richiesta.

## 2. Cittadino con wifi e dispositivi IoT

**Superficie di attacco**: router domestico, telecamere smart, altri dispositivi IoT spesso con credenziali di default o firmware non aggiornato — a differenza del profilo 1, qui esiste un'infrastruttura di rete da compromettere.

**Obiettivo probabile**: reclutamento in una botnet/rete di proxy residenziali (per rivendere l'IP come "pulito" ad altri attori), non necessariamente il furto di dati della vittima stessa.

**Caso reale**: **Water Barghest** (Trend Micro, 2024) — pipeline interamente automatizzata che interroga un database di scansione pubblico (Shodan) per trovare dispositivi vulnerabili, poi lancia exploit automaticamente; il tempo tra infezione iniziale e messa in vendita del dispositivo come proxy sul mercato nero può essere **inferiore a 10 minuti**. Più recentemente, botnet come **Dysphoria** (~296.000 dispositivi, secondo Shadowserver) e il take-down olandese di **Asocks** (~17 milioni di dispositivi) confermano la scala del fenomeno.

**Amplificazione AI**: Water Barghest è già automazione classica, non richiede un LLM. L'elemento AI-specifico, riportato da un vendor (quindi da trattare con cautela, interesse commerciale) è che l'AI comprimerebbe il tempo tra divulgazione di una vulnerabilità e suo sfruttamento "da giorni a ore". Plausibile per analogia con il resto della ricerca di questo repo, ma non confermato in modo indipendente qui.

**Errori commessi dal bersaglio**: credenziali di default lasciate invariate sul router/telecamera (la causa più citata in assoluto per il reclutamento in botnet IoT, inclusa la famiglia Mirai che ha preceduto Water Barghest); firmware del dispositivo mai aggiornato, spesso perché il produttore non invia notifiche o il dispositivo non ha un meccanismo di aggiornamento semplice; dispositivo esposto direttamente su Internet (port forwarding o UPnP attivato senza consapevolezza) invece che dietro il NAT del router; nessuna segmentazione tra la rete "IoT" e quella dei dispositivi personali (PC, smartphone) — se un dispositivo IoT viene compromesso, può diventare un trampolino verso il resto della rete domestica; nessun monitoraggio del traffico in uscita, per cui il dispositivo può restare compromesso per mesi senza che il proprietario se ne accorga (coerente con i tempi di reclutamento di pochi minuti riportati da Water Barghest).

**Segnali rilevanti**: traffico in uscita verso IP/porte anomale dal dispositivo IoT, pattern di scansione tipico di un bot (connessioni rapide e sistematiche verso range di IP), dispositivo che compare come nodo proxy in liste pubbliche di blocklist.

## 3. CEO di una PMI

**Superficie di attacco**: email aziendale, autorità per approvare bonifici, spesso con meno controlli IT strutturati rispetto a una grande azienda (niente SOC dedicato, MFA non sempre obbligatorio).

**Obiettivo probabile**: Business Email Compromise (BEC) — frode diretta tramite bonifico fraudolento, o deployment di ransomware se l'accesso iniziale si estende oltre l'email.

**Caso reale più rilevante per questo profilo (anche se il bersaglio reale era una grande azienda)**: il caso **Arup** (Hong Kong, inizio 2024) — un dipendente è stato convinto a trasferire 25,6 milioni di dollari (HK$200 milioni, in 15 transazioni verso 5 conti) dopo una videochiamata in cui **tutti gli altri partecipanti erano deepfake generati da materiale video/audio pubblico** del CFO e di altri dirigenti. L'attacco è iniziato con un'email di phishing che impersonava il CFO con sede nel Regno Unito. Nessun arresto riportato al momento della ricerca.

**Amplificazione AI**: il caso Arup stesso è l'amplificazione — non serve immaginarla, è già successa. Per una PMI il costo di montare un attacco simile è più basso che mai (voce/video sintetizzati da materiale pubblico, es. video aziendali o interviste), mentre il controllo interno (doppia verifica per bonifici) è tipicamente più debole che in una grande azienda.

**Errori commessi dal bersaglio** (dal caso Arup, dove la vittima era una grande azienda ma l'errore si applica identico a una PMI, spesso con controlli ancora più deboli): il dipendente non ha verificato la richiesta tramite un **secondo canale indipendente** (una telefonata al numero già noto del CFO, non a quello fornito nell'email di phishing iniziale) nonostante la natura insolita e riservata della transazione; si è lasciato convincere dalla **pressione sociale della videochiamata di gruppo** — vedere più "dirigenti" apparentemente presenti ha abbassato la soglia di sospetto, un classico meccanismo di conformità sociale che l'attaccante ha sfruttato deliberatamente; l'azienda non aveva (o il dipendente non ha seguito) una procedura che richiede **doppia autorizzazione fuori banda** per bonifici sopra una certa soglia, indipendentemente da chi lo richiede o con quale urgenza; nessuno ha trovato sospetto che la richiesta fosse esplicitamente "riservata" (la riservatezza richiesta è di per sé un segnale d'allarme classico nelle frodi BEC, non un'eccezione da rispettare).

**Segnali rilevanti**: richiesta di bonifico urgente e riservata fuori dal processo di approvazione standard, pressione a non verificare tramite un secondo canale, video/audio con artefatti di compressione o sincronismo labiale imperfetto (rilevabile solo con attenzione, non con strumenti automatici affidabili al momento).

## 4. CEO di una grande azienda

**Superficie di attacco**: target di alto valore, ma tipicamente con più protezione (sicurezza esecutiva, monitoraggio IT maturo). Il vettore si sposta spesso verso fornitori/filiali meno protetti, o verso spionaggio a lungo termine piuttosto che frode immediata.

**Obiettivo probabile**: spionaggio industriale, furto di proprietà intellettuale, influenza su decisioni strategiche/finanziarie (es. prima di un annuncio societario).

**Caso reale**: il ciclo di vita documentato nel caso **GTG-1002** (vedi [metodo-ricostruito.md](agentic-attacks/metodo-ricostruito.md)) — ~30 organizzazioni bersaglio, agente AI che esegue l'80-90% del lavoro tattico, operatore umano che interviene solo in pochi punti decisionali. Questo profilo di bersaglio è quello più vicino al caso reale già documentato in questo repo.

**Amplificazione AI**: qui l'AI non è "solo" generatore di contenuto (come nei profili 1-3) ma **motore operativo end-to-end** — ricognizione, sviluppo exploit, escalation, esfiltrazione in loop semi-autonomo.

**Errori commessi dal bersaglio**: il dettaglio più importante, spesso trascurato quando si racconta questo caso, è che **nessuna delle ~30 organizzazioni bersaglio si è accorta da sola dell'attacco** — è stato Anthropic a notare "attività sospetta" osservando l'uso del proprio modello, non le vittime a rilevare l'intrusione nella propria rete. Questo è l'errore di fondo: assenza di rilevamento di pattern di accesso anomali a database di alto valore, nessun allarme sul volume/ritmo di query che — con il beneficio del senno di poi — era "più di una richiesta al secondo" sostenuta nel tempo verso i propri sistemi, qualcosa che un normale operatore umano non genera. Le organizzazioni bersaglio avevano quindi probabilmente gli stessi gap di visibilità descritti nel resto di questo repo: nessuna baseline di cosa sia un accesso "normale" al proprio database più sensibile, e nessuna soglia comportamentale (non solo di autenticazione) per distinguere un utente autorizzato che lavora a ritmo umano da un accesso automatizzato con le stesse credenziali.

**Segnali rilevanti**: quelli già descritti in [metodo-ricostruito.md](agentic-attacks/metodo-ricostruito.md) e [detection-rule-spec.md](agentic-attacks/detection-rule-spec.md) — cadenza anomala, sequenza di comandi improbabile per un operatore umano.

## 5. Direttore di ASL (azienda sanitaria locale)

**Superficie di attacco**: sistemi IT spesso legacy nella sanità pubblica, grande volume di dati sanitari sensibili (alto valore sul mercato nero), pressione operativa altissima per il ripristino rapido (vite umane in gioco), spesso accesso di terzi (fornitori di dispositivi medici, software gestionali).

**Obiettivo probabile**: estorsione via ransomware (il settore sanitario è tra i più colpiti), furto ed esfiltrazione di dati sanitari per rivendita o doppia estorsione.

**Caso reale**: la sanità ha subito **più attacchi ransomware di qualsiasi altro settore infrastrutturale critico nel 2025** secondo dati FBI citati dall'American Hospital Association (460 attacchi riportati). Il caso di riferimento resta **Change Healthcare** (2024, gruppo BlackCat/ALPHV), con oltre 192 milioni di record esposti. Il caso **"vibe hacking"** già documentato in questo repo ([metodo-ricostruito.md](agentic-attacks/metodo-ricostruito.md)) ha colpito esplicitamente anche il settore sanitario tra i 17 bersagli, con richieste di riscatto fino a 500.000 $.

**Amplificazione AI**: esattamente il pattern "vibe hacking" — un operatore con Claude Code ha automatizzato l'intera catena dall'accesso iniziale alla generazione delle note di riscatto. Un singolo operatore può colpire molti ospedali/ASL in un mese, impensabile manualmente.

**Errori commessi dal bersaglio** (dal caso Change Healthcare, il più documentato in dettaglio): l'accesso iniziale è avvenuto tramite un **portale Citrix di accesso remoto privo di autenticazione a più fattori**, nonostante la policy interna dell'azienda la richiedesse su tutti i sistemi esposti esternamente — un controllo noto e previsto, semplicemente non applicato su quel sistema specifico. Le credenziali usate potrebbero provenire da un dipendente infettato da un infostealer giorni prima (dettaglio riportato da una sola fonte secondaria, non confermato indipendentemente). Una volta dentro, l'attacco **ha bloccato anche i sistemi di backup**, che secondo testimonianza del CEO erano ancora quelli pre-acquisizione, non ancora modernizzati — cioè l'azienda sapeva di avere un debito tecnico su quel fronte e non l'aveva risolto prima dell'attacco. Gli attaccanti sono rimasti **non rilevati per giorni** prima che l'attacco diventasse evidente. In generale per il settore: sistemi legacy non aggiornati, accesso di fornitori terzi non limitato al minimo necessario, backup non isolati dalla rete principale (quindi cifrabili insieme al resto).

**Segnali rilevanti**: accessi anomali a sistemi di backup prima della cifratura (tentativo di eliminare la via di ripristino), esfiltrazione di volumi anomali di dati verso destinazioni esterne prima della richiesta di riscatto, credenziali di fornitori terzi usate fuori dal loro pattern abituale.

## 6. Dipendente delle poste

**Superficie di attacco**: in Italia, Poste Italiane gestisce anche servizi finanziari (BancoPosta) — un dipendente postale può avere accesso sia a sistemi logistici/dati clienti sia, in alcuni ruoli, a sistemi con rilevanza finanziaria. Superficie ampia e eterogenea.

**Obiettivo probabile**: furto di dati personali dei clienti (indirizzi, documenti spediti), frode finanziaria se l'accesso si estende ai sistemi BancoPosta, punto di pivot verso la rete aziendale più ampia.

**Caso reale comparabile (pattern, non caso specifico su Poste)**: lo stesso pattern Carbanak/Cobalt Group per il settore bancario (vedi profilo 7) si applica concettualmente: email di spear-phishing che sembrano corrispondenza interna/operativa, mirate a un singolo dipendente, con movimento laterale concentrato fuori orario lavorativo per evitare il rilevamento. Non ho trovato un caso pubblico documentato specifico su un'azienda postale con questo pattern — da trattare come inferenza per analogia, non fatto verificato.

**Amplificazione AI**: email di phishing interno generate su misura (tono, terminologia interna) se l'attaccante ha già una minima ricognizione OSINT sull'organizzazione; un agente con accesso a tool di rete potrebbe automatizzare l'enumerazione dei sistemi interni una volta ottenuto un primo accesso, come nel caso GTG-1002.

**Errori commessi dal bersaglio** (per analogia col pattern Carbanak/Cobalt Group del profilo 7, non un caso verificato su un'azienda postale specifica — da trattare come ipotesi): apertura di un allegato (documento Office o Control Panel Applet) arrivato da un indirizzo che sembra un collega o un fornitore interno, senza verificarne l'autenticità; assenza di autenticazione email (SPF/DKIM/DMARC configurati male o non applicati) che permetterebbe a un mittente spoofato di sembrare legittimo; nessuna verifica fuori banda per richieste insolite che toccano dati di spedizione/clienti o, nei ruoli con accesso BancoPosta, operazioni finanziarie; segmentazione insufficiente tra i sistemi logistici (dati di spedizione) e quelli con rilevanza finanziaria, che permetterebbe a un primo accesso limitato di espandersi.

**Segnali rilevanti**: apertura di allegati Office/CPL da un numero anomalo di dipendenti nello stesso periodo, autenticazioni o movimenti laterali fuori orario lavorativo, uso di strumenti di amministrazione remota (RDP su porte non standard, PsExec) da un account che non li usa di norma.

## 7. Dipendente della banca

**Superficie di attacco**: accesso diretto o indiretto a sistemi finanziari, dati clienti, potenzialmente ai sistemi di pagamento/trasferimento. Tipicamente controlli di sicurezza più maturi che altri settori, ma proprio per questo bersaglio di gruppi specializzati con TTP consolidate.

**Obiettivo probabile**: furto finanziario diretto (bonifici fraudolenti), accesso prolungato ai sistemi di pagamento per furti ripetuti, dati clienti per frodi successive.

**Caso reale**: **Carbanak/Cobalt Group** — campagne documentate da Kaspersky (2015) e MITRE ATT&CK (gruppo G0008/G0080) contro istituti finanziari: email di spear-phishing che imitavano corrispondenza bancaria con allegati .doc o .cpl, spesso inviate da account di colleghi già compromessi; **movimento laterale concentrato fuori orario lavorativo** per evitare il rilevamento; gli operatori hanno registrato le schermate dei dipendenti per imparare come usavano le applicazioni bancarie, prima di agire; strumenti di lateral movement riportati: PsExec, Mimikatz, Nmap, RDP su porte alternative (3390, 3391), WMI.

**Amplificazione AI**: il parallelo con GTG-1002 è diretto — "registrare le schermate per imparare l'applicazione bancaria prima di agire" è esattamente il tipo di ricognizione che un agente AI automatizzerebbe end-to-end invece che richiedere settimane di osservazione umana. Non ho trovato un caso pubblico che documenti Carbanak-style + AI agentica insieme — è una proiezione plausibile basata sul combinare due pattern documentati separatamente, non un fatto.

**Errori commessi dal bersaglio**: il dettaglio più specifico riportato dall'analisi di una banca colpita (Bitdefender, via CSO Online) è che **due dipendenti hanno aperto il documento malevolo lo stesso giorno** — non un singolo errore isolato ma un pattern che suggerisce o una campagna ben mirata o un'assenza di formazione diffusa sul riconoscimento di allegati sospetti, anche quando arrivano da un account di un collega già compromesso (quindi apparentemente legittimo). A livello di rilevamento: la maggior parte del movimento laterale è avvenuta **fuori orario lavorativo**, il che implica che il monitoraggio di sicurezza non copriva adeguatamente le ore non lavorative, o che gli alert generati in quelle ore non venivano seguiti con la stessa priorità. L'uso di RDP su porte alternative (3390, 3391) e di strumenti legittimi come PsExec e WMI (anziché malware custom) ha permesso di passare sotto le soglie di detection basate su firme, un errore di impostazione della detection (basata su "cosa" invece che su "come/quando") più che un errore umano singolo.

**Segnali rilevanti**: gli stessi già noti per Carbanak/Cobalt restano validi indipendentemente dall'AI — movimento laterale fuori orario, RDP su porte non standard, uso di Mimikatz/PsExec da un host che non li usa di norma. Questi sono indicatori "a livello tattico" che la detection engineering di questo lab può già affrontare con il metodo descritto in [detection-rule-spec.md](agentic-attacks/detection-rule-spec.md).

## 8. Dipendente di un supermercato

**Superficie di attacco**: sistemi POS (punto vendita), spesso gestiti o mantenuti da fornitori terzi con proprie credenziali di accesso alla rete del retailer — storicamente il punto più debole.

**Obiettivo probabile**: furto di dati delle carte di pagamento su larga scala, dati del programma fedeltà/clienti, pivot verso la rete aziendale più ampia tramite l'accesso del fornitore.

**Caso reale**: pattern ricorrente e ben documentato — **Target (2013)**: accesso iniziale tramite le credenziali di un piccolo fornitore HVAC con pratiche di sicurezza inadeguate, con un'email di phishing come punto di ingresso verso il fornitore stesso. **Home Depot (2014)**: credenziali di un fornitore terzo usate per accedere alla rete e poi elevare i privilegi fino ai registratori di cassa. **Jimmy John's** e **Dairy Queen**: stesso pattern, credenziali di un fornitore POS compromesse.

**Amplificazione AI**: nessun caso pubblico documentato di questo pattern specifico combinato con un agente AI. Per analogia con Water Barghest (profilo 2) e GTG-1002 (profilo 4), un agente con accesso a tool di enumerazione di rete potrebbe automatizzare la fase "dalle credenziali del fornitore rubate alla rete POS" molto più velocemente di un operatore umano — ma questa è un'inferenza, non un fatto osservato.

**Errori commessi dal bersaglio**: il caso Target è probabilmente il più istruttivo dell'intera casistica, perché l'errore non è stato "non avere strumenti di detection" ma **non aver agito su un allarme già generato**. Secondo un'inchiesta Bloomberg Businessweek (citata da più fonti secondarie), FireEye aveva segnalato il malware il 30 novembre 2013 con un alert al massimo livello di gravità, ripetuto man mano che gli attaccanti distribuivano altre varianti dello stesso malware (fino a cinque, secondo i ricercatori) — e l'allarme è stato semplicemente ignorato dal centro operativo di sicurezza a Minneapolis, secondo gli oltre 18 insider intervistati. Due fattori aggravanti riportati: la funzione di blocco automatico del malware era disattivata (le fonti divergono sul perché — scelta del team di sicurezza, o funzione non ancora configurata/testata), e il commento di settore più citato attribuisce l'inazione ad **"alert fatigue"** — team che ignorano gli allarmi perché ne ricevono troppi, molti falsi positivi, o perché sotto organico. A monte, l'accesso iniziale è passato per un **fornitore terzo (HVAC) con pratiche di sicurezza inadeguate**, a cui Target aveva concesso più accesso alla rete di quanto necessario per il suo compito — nessuna segmentazione tra l'accesso del fornitore e la rete dei sistemi di pagamento. Lo stesso schema (credenziali di un fornitore POS, nessuna segmentazione) si ripete in Home Depot, Jimmy John's e Dairy Queen.

**Segnali rilevanti**: credenziali di un account fornitore usate da un IP o in un orario anomalo rispetto al pattern storico, traffico dalla rete amministrativa verso la rete POS (che dovrebbe essere segmentata), volumi di transazioni/query anomali su sistemi di pagamento in finestre temporali brevi.

## Nota di metodo per il lab

Il grado di certezza varia molto tra i profili. Per i profili 3 (PMI), 4 (grande azienda) e 5 (ASL) esistono casi reali **già combinati con AI-driven execution** (Arup, GTG-1002, vibe hacking). Per i profili 1, 2, 6, 7, 8 il caso reale documentato è spesso **senza AI** (Carbanak, Target, Water Barghest), e l'amplificazione AI è un'inferenza plausibile per analogia con i profili dove è già confermata — da trattare esplicitamente come ipotesi da verificare, non da presentare come fatto in un eventuale colloquio o writeup futuro.

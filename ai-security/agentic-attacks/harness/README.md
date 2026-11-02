# Harness agente / umano — AD Lab v2

## Scopo e stato

Infrastruttura sperimentale per confrontare sessioni con decisioni esterne al runner.
Non implementa un agente, non sceglie comandi, non attribuisce attività all'AI.
Nessuna soglia di detection è stata stimata. I test inclusi usano guest finti e dati
sintetici; compatibilità live di VMware, schema indexer e telemetria resta da verificare.

**Macchine:** host Windows con Python 3.11+, TEST01 (Kali, Python 3/bash), WS01
(Windows PowerShell, Sysmon), WAZUH (Python 3, accesso HTTPS all'indexer).
Rete prevista: `192.168.219.0/24`. GuestOps è quello esistente in
`A:/ADLab/kit/scripts/ADLab-GuestOps.py`; non viene copiato o modificato.
Nessuno script accende VM. `--help`, init, close, analisi e correlazione offline non
contattano i guest. Le opzioni `--live` eseguono operazioni: usarle **solo dopo il
coordinamento esplicito dello stato delle VM e della RAM**.

## Prerequisiti e riproducibilità

Preparazione host, dalla cartella harness:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

Usare lo stesso interprete e le stesse dipendenze per tutte le sessioni.
`requirements-tested-win-py314.txt` congela anche le dipendenze transitive della
verifica offline su Windows Python 3.14.8; usare quel file per riprodurre tale ambiente.
Per altri Python/piattaforme risolvere `requirements.txt` e conservare il proprio freeze.
Archiviare
commit del repo, versione Python/pandas/GuestOps, hash di GuestOps, snapshot VM,
versioni tool, configurazione Sysmon, configurazione agent/indexer, task e ordine
delle prove. Registrare manualmente questi dati in una scheda di esperimento;
il runner salva soltanto i metadati elencati nel suo JSON.

Prima delle prove live verificare VMware Tools, credenziali GuestOps, macchine già
accese e nomi effettivi WS01/TEST01/WAZUH. Misurare offset e incertezza degli orologi
TEST01/WS01/host/WAZUH, senza correggerli durante una sessione. Non dichiarare il
timestamp «esatto»: il formato conserva microsecondi, l'accuratezza dipende dal clock.
Verificare che Sysmon raccolga davvero ID 1 e 3 e che Wazuh li indicizzi. La sola
presenza di Wazuh non lo garantisce: gli alert possono contenere un sottoinsieme
dei log, gli archivi richiedono configurazione esplicita.

Sul guest WAZUH predisporre **fuori dal repo**, con permessi root-only, un JSON
`/root/agentic-indexer.json` con queste chiavi:

```json
{
  "url": "https://<INDEXER_HOST_MATCHING_CERTIFICATE>:9200",
  "ca_file": "/<PATH_TO_TRUSTED_CA.pem>",
  "username": "<READ_ONLY_INDEXER_USER>",
  "password": "<SECRET>",
  "agent_id": "<VERIFIED_WS01_AGENT_ID>",
  "index_pattern": "<VERIFIED_ALERTS_OR_ARCHIVES_PATTERN>"
}
```

Nessuna disattivazione TLS, nessun recupero automatico di segreti. Il mapping
atteso è `data.win.system.{eventID,providerName,systemTime,eventRecordID,computer}`
e `agent.id`. Verificarlo sui propri indici prima della prova; mapping diversi
richiedono modifica e revisione della query/parser. Non usare `@timestamp` come
tempo dell'azione senza verificarne la semantica. Non installiamo/configuriamo
telemetria con questo harness.

## 1. Sessioni (`session.py`)

```powershell
python session.py init runs/human-train --label human --task "<task concordato>"
# Solo dopo autorizzazione a operare live, un comando scelto esternamente alla volta:
python session.py run runs/human-train --live --command '<comando approvato contro WS01>'
python session.py close runs/human-train
```

Ripetere con directory distinte per `human-test`, `agent-test` e controlli
amministrativi. Il baseline di training umano deve essere indipendente dai test.
L'umano e il controller LLM usano esattamente la stessa CLI; nessun batch, jitter o
ritardo artificiale viene aggiunto. Non passare credenziali sulla command line.
Il runner non interpreta né limita destinazioni o sintassi shell: mantenere i
comandi entro lo scopo approvato e l'isolamento del lab. Non è una sandbox.

**Prove:** `session.json` e un JSON per comando con identificatore, comando integrale,
submitted/received UTC host, started/ended UTC TEST01, clock monotonic ns TEST01,
stdout/stderr leggibili e base64 lossless, hash SHA256 dei due stream, exit code.
L'exit code è quello di bash (nelle pipeline valgono le normali regole bash),
non quello di VMware. Gli errori di trasporto hanno exit code null e stato distinto;
il testo dell'eccezione non viene registrato per evitare fughe di credenziali.
Un exit code nonzero del comando è comunque una misura completata.

Ogni invocazione usa una nuova bash sotto sudo/root, come previsto da GuestOps:
cd, variabili, job e shell interattive non persistono. Questo fattore può alterare
il comportamento rispetto a un terminale umano ordinario. Il timeout è 600 secondi;
non usare comandi con processi persistenti, background o daemon. Un timeout può
lasciare discendenti attivi: fermare la prova e verificarli prima di riprendere.
Output viene bufferizzato in memoria e poi su disco: evitare output illimitato.
Non eseguire due runner nella stessa sessione; il lock esclusivo evita sovrapposizioni
ordinarie. Dopo un crash ispezionare lo stato prima di rimuovere manualmente `.lock`.
Un JSON pending resta disponibile se il processo host muore prima del download.
Il runner non pulisce automaticamente gli artefatti `/tmp/agentic-*` nei guest.
GuestOps stesso usa file temporanei nella propria directory: quella deve essere scrivibile.

Il timing start-to-start monotonic include durata del comando precedente,
trasferimenti VMware, avvio processi, tempo di lettura/decisione e invocazione CLI.
Non misura il solo tempo cognitivo del controller. Il clock monotonic è confrontabile
solo entro lo stesso boot TEST01. Documentare il boot e non sospendere/riavviare VM.

## 2. Esportazione e correlazione (`export.py`)

```powershell
# Sostituire entrambi i valori con offset misurato e tolleranza giustificata:
python export.py runs/human-test exports/human-test-01 --live --clock-offset-seconds <WS01_UTC_meno_TEST01_UTC> --padding-seconds <tolleranza>
```

Sessione chiusa, comandi completi e destinazione nuova sono obbligatori. Il filtro
copre dal primo start all'ultimo end, applica l'offset dichiarato, poi il padding.
Sysmon viene letto dopo la sessione con Get-WinEvent ID 1/3; XML originale e campi
EventData sono conservati in `sysmon.json`. Query e script exporter creano a loro
volta telemetria: sono una possibile contaminazione vicino al bordo della finestra.
Il codice non modifica log o configurazione Sysmon e non esporta un EVTX forense.

WAZUH esegue una ricerca HTTPS sull'indexer usando l'agent ID esplicito e il tempo
originale Sysmon. La paginazione scroll non tronca al primo blocco; timeout e shard
falliti causano errore. Gli hit integrali con indice/ID e query restano in
`wazuh.json`. Non legge semplicemente alerts.json sul manager.

`correlated.json` conserva tutti gli eventi della finestra, inclusi quelli senza
candidati, e assegna zero/uno/più command ID per sovrapposizione con gli intervalli
di esecuzione più tolleranza. È **associazione temporale, non causalità**. Verificare
anche computer/eventRecordID/ProcessGuid, IP/porte e XML; il parser non inventa
un legame univoco tra comando Kali e processo Windows. Una scansione remota può non
generare un Process Create; Network Connect di Sysmon non è un packet capture e
non garantisce visibilità di ogni tentativo inbound. Eventi target-side non
ricostruiscono necessariamente la sequenza dei comandi sul sorgente.

**Indicizzazione tardiva:** export è uno snapshot, non prova di completezza.
Ripetere in una nuova directory dopo un'attesa documentata; confrontare gli ID
deduplicati per indice/ID e computer/record ID. Conteggi stabili non dimostrano
che non arriveranno altri eventi. Retention, log sovrascritti, alert suppression,
drop e mapping errati possono rendere irrecuperabile la copertura. Conservare tutte
le esportazioni e non equiparare «nessun hit» a «nessuna attività». Il manifest
rimane incomplete se una fase fallisce. Confrontare i conteggi local/indexed prima
di trarre conclusioni; non esiste un criterio automatico di completezza.

Ricalcolo offline, stessi parametri e artefatti grezzi già presenti:

```powershell
python export.py runs/human-test exports/human-test-01 --clock-offset-seconds <offset> --padding-seconds <tolleranza>
```

## 3. Analisi (`analyze.py`)

```powershell
python analyze.py runs/human-test runs/agent-test --baseline runs/human-train --output analysis/comparison-01
```

Risultato atteso: tabella leggibile a terminale e `comparison.txt`, `comparison.csv`,
`details.json` con stati normalizzati, transizioni/probabilità, bordi dei bin,
curva CCE, parametri e versione pandas. Non produce etichette predette né soglie.

Metodo timing da [Gianvecchio et al., USENIX Security 2008, §4.1.1 e §5.1](https://www.usenix.org/legacy/event/sec08/tech/full_papers/gianvecchio/gianvecchio.pdf):
entropia empirica in bit su bin approssimativamente equiprobabili (default Q=256),
rate su Q=5 usando `CCE_m = H(blocchi_m) - H(prefissi_m-1) + p_singleton*H1`.
`p_singleton` è la frazione delle finestre che occorrono una sola volta.
Si prende il minimo tra H1 e i CCE per ordini 2..max-order (default 10).
Joint e prefissi usano le stesse finestre, così la conditional entropy empirica
non diventa negativa per semplice disallineamento dei campioni.
I valori Q riprendono il paper, **non sono soglie calibrate per comandi AI**.
L'ordine massimo è una scelta implementativa esplicita. Non è una replica del
classificatore chat: non analizza dimensione dei messaggi e non usa i suoi cutoff.

Quantili calcolati separatamente per sessione; i quantili duplicati collassano,
tempi identici restano nello stesso stato. Questo preserva i pareggi ma riduce Q
effettivo; controllare i bordi salvati. Quantili per-sessione possono rendere H1
simile per distribuzioni molto diverse: confrontare anche i tempi e fare analisi
di sensibilità con Q/ordine diversi. Campioni corti, dipendenze non stazionarie e
finestre sovrapposte producono bias. Per meno di due intervalli il rate è NaN.
Non viene stabilita una lunghezza minima «sufficiente» o una significatività statistica.

Markov: tokenizzazione shlex bash approssimata, eseguibile conservato, ogni argomento
sostituito da `<ARG>` (`cat file1.c` → `cat <ARG>`). Conserva i separatori shell;
uno stato rappresenta l'intero comando normalizzato di una invocazione, bigrammi
tra invocazioni. Flag, percorsi e valori sono intenzionalmente persi. Non è un
parser bash completo: wrapper sudo/env, assegnazioni, redirezioni, script multilinea
e quoting complesso possono ridurre la validità; ispezionare gli stati e mantenere
una grammatica semplice concordata. Non tratta ogni programma in una pipeline
come azione separata.

Il modello è stimato solo sul training umano distinto. Riporta cross-entropy
media in bit/transizione su ogni test, smoothing add-alpha (default 1), stato UNK
esplicito, frazione di stati sconosciuti. Una loss elevata può indicare task/tool
diversi o baseline scarsa; non è evidenza di AI. Perdita di training non viene
confrontata con test sullo stesso campione. Per confronti seri servono più
operatori/agenti, task bilanciati, controlli automatizzati legittimi, ordine
randomizzato documentato, repliche e test separati per calibrazione/validazione.
Questo script descrittivo non calcola intervalli di confidenza né p-value.

## Detection e condizioni per fermarsi

`detection.sigma.yml.template` è intenzionalmente **non distribuibile**, con soglie,
schema e severità da riempire solo dopo osservazioni e validazione. Anche direzioni
dei confronti e combinazione dei segnali sono ipotesi. Sigma/Wazuh non calcolano
queste feature direttamente da singoli eventi Sysmon: servirà un estrattore
target-side validato e un mapping separato. Le feature del log comandi sorgente
non sono automaticamente disponibili in un SOC; questa lacuna va dimostrata/risolta
prima di sostenere che la regola sia implementabile sui log bersaglio.

Fermarsi per conflitti RAM/stato VM, isolamento incerto, clock non misurati,
telemetria mancante, errori di trasporto, timeout, processo residuo, riavvio guest,
schema inatteso o credenziali nei risultati. Non rilanciare automaticamente un
comando fallito: potrebbe avere avuto effetti anche se il risultato non è arrivato.
Artefatti, comandi e output possono essere sensibili; `runs/`, `exports/`, `analysis/`
sono ignorati da Git, ma vanno comunque revisionati prima di ogni pubblicazione.
La sola infrastruttura non prova alcuna firma distintiva AI/umano.

## Verifica eseguita

Sette test offline superati su Windows/Python 3.14.8: exit code guest distinto dal
trasporto, output binario lossless, errori senza testo sensibile, correlazione
molti-a-molti e assenza di candidati, entropia/rate su sequenze note, pareggi nei
quantili, normalizzazione/UNK e flusso CLI init-close-export-analisi su dati sintetici.
Il wrapper Python destinato a Kali viene compilato nel test con guest simulato.
Nessun avvio VM, chiamata GuestOps reale, accesso all'indexer o verifica live è
stato eseguito. Questi test non certificano compatibilità del lab né validità
statistica di una firma agente/umano.

# Specifica concettuale della regola di detection

Non è la regola finale: è la struttura logica che la regola Sigma/Wazuh dovrà avere, derivata dalla metodologia statistica in [teoria-approfondita.md](teoria-approfondita.md#2-metodologia-statistica-per-distinguere-agente-ai-da-operatore-umano). Le soglie numeriche vanno compilate solo dopo aver raccolto dati reali con l'harness (vedi [metodo-ricostruito.md](metodo-ricostruito.md) e la cartella `harness/` che Codex sta costruendo) — qui non ne viene inventata nessuna.

## Perché due condizioni, non una

La letteratura (Gianvecchio et al.) e la nota sul jitter nel C2 beaconing dicono la stessa cosa da due angoli diversi: **una sola metrica di timing è evadibile**. Un attaccante (umano o un agente istruito a farlo) può introdurre pause artificiali per abbassare la metrica di cadenza senza cambiare cosa fa. Per questo la regola deve combinare due segnali ortogonali e scattare solo quando **entrambi** si allontanano dalla baseline, non quando uno solo lo fa — altrimenti il tasso di falsi positivi diventa ingestibile (qualsiasi script di automazione legittima ha cadenza regolare) oppure la regola è troppo facile da evadere.

## Struttura logica

```
CONDIZIONE A (cadenza)
  entropia(inter-arrival-time dei comandi nella sessione) E
  entropy-rate(stessa serie)
  entrambe SOTTO la soglia_bassa calcolata sulla baseline umana
  [bassa entropia/entropy-rate = comportamento troppo regolare per un umano]

CONDIZIONE B (sequenza)
  log-probabilità della sequenza di comandi (normalizzati con placeholder sugli
  argomenti) sotto il modello Markov di primo ordine costruito sulla baseline umana
  SOTTO la soglia_bassa_sequenza
  [sequenza statisticamente improbabile per un operatore umano in quell'ambiente]

ALERT solo se A AND B
  [mai A da solo: troppi falsi positivi su automazione legittima]
  [mai B da solo: la letteratura non lo valida come sufficiente in isolamento]
```

## Campi che la regola dovrà avere (indipendentemente dal motore - Sigma generico o Wazuh nativo)

| Campo | Cosa contiene | Da dove viene |
|---|---|---|
| `logsource` | Sysmon Process Create / Network Connect sul bersaglio (WS01) | già configurato nel lab |
| `window` | finestra temporale su cui calcolare entropia/entropy-rate (es. ultimi N comandi o ultimi T minuti) | da calibrare sui dati, non assunta |
| `baseline_profile` | riferimento al profilo (entropia minima osservata, modello Markov) costruito sulla sessione umana di riferimento | prodotto dall'harness, non dalla regola stessa |
| `soglia_entropia` | valore minimo di entropia/entropy-rate sotto cui la Condizione A è vera | **da compilare con dati reali** |
| `soglia_markov` | valore minimo di log-probabilità sotto cui la Condizione B è vera | **da compilare con dati reali** |
| `mitre_attck` | tecniche T1595/T1589/T1526 (o altre, in base a cosa viene effettivamente osservato — non assegnate a priori) | derivato dal comportamento osservato, non copiato da un vendor |
| `falsi_positivi_noti` | categorie di attività legittima che potrebbero soddisfare A e B insieme (es. script di audit con esecuzione a comandi fissi e ripetitivi) | da popolare testando la regola contro traffico amministrativo reale, non solo contro l'agente |

## Cosa NON deve fare questa regola

- Non deve assumere un intervallo fisso tra comandi come indicatore unico (evadibile con jitter)
- Non deve scattare sulla sola presenza di tool di ricognizione (nmap, sqlmap...) — quelli li usa anche un umano autorizzato
- Non deve mappare tecniche ATT&CK per supposizione: solo quelle confermate dal comportamento osservato nei dati raccolti

## Collegamento con l'harness di Codex

Il punto 4 del lavoro affidato a Codex (`harness/`) produce il file YAML/Sigma compilato con le soglie reali. Questa specifica è il contratto che quel file deve rispettare: se Codex (o chiunque) scrive una regola con una sola condizione, o con soglie scelte senza dati, non segue questa specifica e va rivista.

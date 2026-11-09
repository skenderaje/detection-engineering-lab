---
tipo: attacco-difesa
data: 2026-11-09
aggiornato: 2026-11-09
fonte: Ilias1988/Hacking-Cheatsheets — API-Security (README.it.md)
tecnica: API-Security
tags: [attacco-difesa, lab, bozza]
---

# API-Security — attacco ipotizzato → difese

> [!WARNING] Bozza — scheda concettuale, nessun esercizio eseguito
> Questa scheda è stata generata automaticamente il 2026-11-09 da un task pianificato. È una bozza da rivedere a mano e non è un verdetto. Non è stato eseguito nessun attacco e non è stato toccato nessun sistema.

## Attacco ipotizzato

**Scopo.** Capire come un attaccante metterebbe alla prova un'API (REST o GraphQL) esposta nel lab isolato, seguendo le categorie della fonte: OWASP API Top 10, discovery ed enumerazione, manipolazione di metodi e parametri, mass assignment, GraphQL, autenticazione (API key, OAuth), JWT, rate limiting, BOLA/BFLA e gestione degli asset. Qui serve a sapere quali tracce lascia ogni passo e dove intervenire.

**Macchina/bersaglio tipico.** Un servizio web di laboratorio che espone un'API REST e/o un endpoint `/graphql`, eventualmente con documentazione pubblicata (`/swagger/`, `/openapi.json`, `/api-docs`, secondo i percorsi elencati nella fonte). L'autenticazione avviene tramite API key, token Bearer/JWT o un flusso OAuth2.

**Prerequisiti (dalla fonte).**
- **Discovery:** raggiungibilità HTTP dell'API e una wordlist di endpoint. Le versioni vecchie o non rilasciate (`/api/v1`, `/api/beta`, `/api/internal`, `/api/debug`) diventano un problema di *Improper Assets Management*.
- **BOLA/IDOR:** identificativi di oggetto prevedibili (sequenziali, basati su timestamp, in formati alternativi) e un controllo di autorizzazione per oggetto assente.
- **BFLA:** endpoint amministrativi o metodi HTTP (POST/PUT/DELETE, oppure override via header `X-HTTP-Method-Override`) senza controllo di ruolo.
- **Mass assignment:** il backend accetta campi extra nel body (`role`, `isAdmin`, `balance`, `verified`) e li scrive sull'oggetto.
- **Content-Type:** un parser che accetta XML in modo inatteso apre la strada a XXE (rimando alla scheda XXE, da creare).
- **GraphQL:** introspezione attiva o aggirabile (`__type` al posto di `__schema`, field suggestions), batching e alias senza limiti, query annidate senza limite di profondità, e argomenti passati a SQL/NoSQL senza sanificazione.
- **Autenticazione:** API key trapelate (file JS, app mobile, GitHub), `redirect_uri` OAuth validato male, parametro `state` assente o riusato, token non invalidati al logout.
- **JWT:** `alg: none` accettato, confusione HS256↔RS256, segreto HMAC debole (craccabile offline), claim (`role`, `admin`, `exp`) di cui il server si fida senza verifica.
- **Rate limiting:** il limite si basa su header controllabili dal client (`X-Forwarded-For` e simili) o su un confronto di percorso sensibile a maiuscole e slash finali.

**Risultato atteso.** Lettura o modifica di dati di altri utenti (BOLA), esecuzione di funzioni riservate (BFLA), escalation di privilegi via mass assignment o claim JWT manomessi, furto di token OAuth, ricognizione completa dello schema, brute force non limitato e indisponibilità del servizio (query GraphQL annidate).

**Nuovi vettori emersi dalle vulnerabilità recenti (dettagli e fonti nella sezione sotto).** Si collegano alle sezioni della fonte:
- **Attacchi JWT → confusione dell'algoritmo, ancora attuale nel 2026.** In LibJWT (CVE-2026-44699) una JWK RSA senza `alg` viene accettata come chiave HMAC, e nel backend OpenSSL l'HMAC gira con una chiave di lunghezza zero: un token si può forgiare. È la stessa classe "HS256 → RS256" descritta nella fonte, ma nasce da un difetto della libreria, non da una configurazione sbagliata dell'applicazione.
- **GraphQL → bypass dell'introspezione disabilitata.** In Parse Server (CVE-2026-30854) le query `__type` annidate dentro inline fragment aggirano il blocco dell'introspezione. Conferma in un prodotto reale la tecnica "Introspezione alternativa con `__type`" della fonte.
- **GraphQL → autorizzazione saltata a livello di framework.** In Spring for GraphQL (CVE-2026-41856) le annotazioni di sicurezza sui metodi controller in gerarchie di tipi non vengono rilevate, quindi il controllo di metodo non scatta. Dall'esterno si manifesta come BFLA/BOLA anche se il codice applicativo "sembra" protetto.
- **OAuth → furto del token via `redirect_uri`.** Diversi provider OAuth/OIDC del 2026 hanno avuto bypass della validazione del `redirect_uri`:
  - Pocket ID (CVE-2026-28512): userinfo con `@`, cioè proprio il pattern `target.com%40attacker.com` della fonte;
  - Backstage (CVE-2026-32235): bypass dell'allowlist a pattern;
  - Authorizer (CVE-2026-54072): nessuna validazione, con token restituiti nel redirect e `client_id` ottenibile dall'endpoint GraphQL pubblico, quindi una catena GraphQL → OAuth;
  - Authlib (CVE-2026-41479): open redirect quando il `response_type` non è supportato.

**MITRE ATT&CK (indicativo).** Lo sfruttamento di un'API esposta rientra in Exploit Public-Facing Application (T1190). L'uso di token rubati o forgiati rientra in Use Alternate Authentication Material: Application Access Token (T1550.001). Il furto di token via redirect OAuth rientra in Steal Application Access Token (T1528). Il brute force sulle API rientra in Brute Force (T1110). La mappatura dei singoli casi (BOLA, mass assignment, introspezione) su sotto-tecniche precise è **da verificare**: ATT&CK non ha voci dedicate alle classi OWASP API.

## Vulnerabilità recenti (con fonte)

Le ricerche sono state fatte con WebSearch il 2026-11-09 e le date sono state lette direttamente dalle pagine indicate. Le fonti sono database di advisory (GitLab Advisory Database, Mend) o blog di terze parti, non sempre la pagina del vendor: vanno ricontrollate su NVD o sull'advisory ufficiale.

| ID | Data pubblicazione | Componente | Descrizione (una riga) | Fonte |
| --- | --- | --- | --- | --- |
| CVE-2026-44699 | 2026-05-15 | LibJWT (C), >=3.0.0 <3.3.3 | Una JWK RSA senza `alg` viene accettata come chiave HMAC per HS256/384/512; con il backend OpenSSL l'HMAC usa una chiave vuota, quindi un JWT si può forgiare. Corretta in 3.3.3. | https://mend.io/vulnerability-database/CVE-2026-44699/ |
| CVE-2026-30854 | 2026-03-09 | parse-server (npm), 9.3.1-alpha.3 → <9.5.0-alpha.10 | Con l'introspezione pubblica GraphQL disattivata, `__type` dentro inline fragment la aggira (ricognizione non autenticata). Corretta in 9.5.0-alpha.10. | https://advisories.gitlab.com/npm/parse-server/CVE-2026-30854/ |
| CVE-2026-41856 | 2026-06-11 (post del blog; patch del 2026-06-10 secondo la stessa pagina) | Spring for GraphQL (2.0.0–2.0.3, 1.4.0–1.4.5, 1.3.0–1.3.8, 1.0.0–1.0.6) | Le annotazioni `@PreAuthorize`/`@Secured` su metodi `@Controller` in gerarchie di tipi non vengono rilevate e il controllo di autorizzazione viene saltato. Corretta in 2.0.4 / 1.4.6 (OSS) e 1.3.9 / 1.0.7 (commerciali). | https://researcher.branch.zeropath.com/blog/cve-2026-41856-spring-graphql-authorization-bypass |
| CVE-2026-32235 | 2026-03-12 | @backstage/plugin-auth-backend (npm), <0.27.1 | Bypass dell'allowlist del redirect URI nel provider OIDC sperimentale. Richiede funzioni sperimentali attive e il consenso della vittima. Corretta in 0.27.1. | https://advisories.gitlab.com/npm/@backstage/plugin-auth-backend/CVE-2026-32235/ |
| CVE-2026-28512 | 2026-03-09 | Pocket ID backend (Go) | Un `redirect_uri` con userinfo (`@`) supera la validazione della callback e il codice di autorizzazione finisce all'host dell'attaccante. Corretta nella pseudo-versione 0.0.0-20260228130835-3a339e33191c. | https://advisories.gitlab.com/golang/github.com/pocket-id/pocket-id/backend/CVE-2026-28512/ |
| CVE-2026-54072 | 2026-07-10 | Authorizer (Go) | `/authorize` non valida `redirect_uri` contro AllowedOrigins: con `response_type=token`/`id_token` i token vengono aggiunti al redirect verso l'attaccante, e il `client_id` è leggibile dall'endpoint GraphQL pubblico. Corretta nella pseudo-versione 0.0.0-20260409051328-bd3f5baf6d3d. | https://advisories.gitlab.com/golang/github.com/authorizerdev/authorizer/CVE-2026-54072/ |
| CVE-2026-41479 | 2026-06-08 | authlib (PyPI), <1.6.10 e >=1.7.0 <1.7.1 | L'endpoint di autorizzazione OAuth 2.0 diventa un open redirect non autenticato quando il `response_type` non è supportato, perché il controllo avviene prima della validazione del redirect URI. Corretta in 1.6.10 / 1.7.1. | https://advisories.gitlab.com/pypi/authlib/CVE-2026-41479/ |

**Segnalazioni trovate ma NON incluse** (data o dettagli non confermati in questa run; vedi "Da verificare"): Hono CVE-2026-22817 (la pagina GitLab era vuota al fetch), Directus CVE-2026-35413 (la pagina NVD era vuota al fetch), PyJWT "CVE-2026-102268" e fast-jwt "CVE-2026-107724" (ID dal formato insolito, le pagine trovate sono aggregatori e una dichiara contenuto generato da AI).

## Prove da raccogliere

Solo tipologie di telemetria. Gli ID evento e i campi esatti dipendono dallo stack del lab e **non sono indicati qui**.
- **Access log del web server / reverse proxy / API gateway:** metodo, percorso, status code, dimensione della risposta, user agent, IP sorgente, header usati per l'IP del client. Servono per enumerazione (molti 404 su percorsi da wordlist), richieste a versioni vecchie (`/v1`, `/beta`, `/internal`) e tentativi di override del metodo.
- **Log applicativi di autorizzazione:** decisioni allow/deny con identità del chiamante, risorsa e proprietario della risorsa. Sono indispensabili per vedere un BOLA: senza il proprietario dell'oggetto nel log, il BOLA non si distingue da un accesso legittimo.
- **Log di autenticazione e di validazione dei token:** login riusciti e falliti, errori di verifica della firma JWT, `alg` del token presentato, `kid`/issuer, token usati dopo il logout o dopo la scadenza.
- **Log del server GraphQL:** nome dell'operazione, query o hash della query, profondità e complessità calcolate, numero di alias per richiesta, presenza di `__schema`/`__type`.
- **Log del provider OAuth/OIDC:** richieste a `/authorize` con `client_id`, `redirect_uri`, `response_type` e `state`, consensi concessi, codici scambiati.
- **Log del database:** errori di sintassi SQL/NoSQL generati da argomenti GraphQL o REST, utili per la SQLi descritta nella fonte.
- **Telemetria di rete (pcap / Zeek o simili nel lab):** volume e frequenza delle richieste verso l'API, header `X-Forwarded-For` incoerenti con l'IP reale.
- **Inventario delle dipendenze (SBOM / lockfile):** versioni di LibJWT, parse-server, Spring for GraphQL, Backstage, Pocket ID, Authorizer e authlib, se presenti nel lab, da confrontare con le versioni corrette.

## Difese / Detection corrispondenti

**Preventive (dalla fonte + buone pratiche OWASP API Top 10).**
- **BOLA:** controllo di autorizzazione per oggetto lato server a ogni accesso, basato sull'identità del token e non su ID passati dal client. Gli ID non prevedibili (UUID casuali) riducono l'enumerazione ma **non** sostituiscono il controllo.
- **BFLA:** deny-by-default sugli endpoint amministrativi e verifica di ruolo per ogni metodo HTTP. Gli header di override (`X-HTTP-Method-Override` e simili) vanno ignorati, oppure accettati solo da client fidati.
- **Mass assignment:** allowlist esplicita dei campi scrivibili per ogni endpoint (DTO o schema di input) e rifiuto dei campi sconosciuti.
- **Content-Type:** accettare solo i content type previsti e disabilitare le entità esterne nei parser XML.
- **GraphQL:** introspezione disattivata in produzione, field suggestions disattivate, limiti di profondità, complessità e alias o batching per richiesta (valori: **soglia da calibrare sui dati del lab**), query parametrizzate nei resolver.
- **JWT:** l'algoritmo atteso va fissato lato server e non letto dall'header del token. Vanno rifiutati `none` e qualsiasi algoritmo non previsto, e le chiavi vanno separate per tipo (una chiave RSA non deve mai poter essere usata come segreto HMAC). Serve un segreto HMAC lungo e casuale, perché quelli elencati nella fonte sono craccabili. Infine, verifica di `exp`, `iss` e `aud`.
- **OAuth:** confronto **esatto** del `redirect_uri` con i valori registrati, senza pattern o prefissi e senza parsing permissivo di userinfo `@`. Servono anche `state` obbligatorio e legato alla sessione, PKCE, e la preferenza per il flusso authorization code rispetto a quello implicito (`response_type=token`).
- **Rate limiting:** il limite va legato all'identità autenticata o all'IP reale visto dal proxy fidato, non a `X-Forwarded-For` fornito dal client. I percorsi vanno normalizzati (maiuscole, slash finale) prima di applicare il limite.
- **Gestione degli asset:** inventario delle versioni API esposte e dismissione o blocco di `/v1`, `/beta`, `/internal`, `/debug` in produzione.

**Patch e mitigazioni dalle vulnerabilità recenti (fonti nella tabella sopra).**
- **LibJWT:** aggiornare almeno alla 3.3.3. Finché non è possibile, assicurarsi che il codice imposti esplicitamente l'algoritmo atteso e che le JWK abbiano `alg` valorizzato.
- **parse-server:** almeno 9.5.0-alpha.10. Non affidarsi al solo flag che disattiva l'introspezione: controllare che anche `__type` sia bloccato.
- **Spring for GraphQL:** 2.0.4 / 1.4.6 (OSS) oppure 1.3.9 / 1.0.7 (commerciali). Finché non si aggiorna, non affidarsi alle sole annotazioni su metodi ereditati e scrivere test che verifichino il diniego.
- **Backstage auth backend:** almeno 0.27.1, oppure lasciare disattivate le funzioni sperimentali (Dynamic Client Registration / Client ID Metadata Documents), che non sono attive di default secondo l'advisory.
- **Pocket ID e Authorizer:** aggiornare alle pseudo-versioni indicate negli advisory. Per Authorizer, valutare anche se l'endpoint GraphQL che espone il `client_id` deve restare pubblico.
- **authlib:** 1.6.10 o 1.7.1.

**Idee di detection (logica a parole, nessuna soglia inventata).**
- **Enumerazione / discovery:** molte risposte 404 o 405 dallo stesso client su percorsi API diversi in una finestra breve, oppure richieste a `/swagger`, `/openapi.json`, `/api-docs` e `/graphql` da client non attesi (soglia da calibrare sui dati del lab).
- **BOLA:** lo stesso utente autenticato accede a molti ID di oggetto distinti che appartengono ad altri proprietari, oppure scorre gli ID in sequenza. Serve che il log contenga il proprietario della risorsa.
- **BFLA:** un utente senza ruolo admin riceve 200 su un percorso `/admin/` o su un metodo riservato. Va trattato come alert immediato, non statistico.
- **Mass assignment:** body di richieste di creazione o modifica che contengono campi privilegiati (`role`, `isAdmin`, `verified`, `balance`) da utenti non admin.
- **JWT:** token con `alg` diverso da quello configurato, `alg: none`, firma vuota, oppure un picco di errori di verifica della firma dallo stesso client. È anomalo anche un token valido con claim di ruolo che non corrisponde al ruolo registrato nel backend per quell'utente.
- **GraphQL:** query con `__schema` o `__type` in produzione (in particolare `__type` dentro inline fragment, come in CVE-2026-30854), query che superano i limiti di profondità o di alias, e molte query con nomi di campo inesistenti (brute force dei campi con field suggestions).
- **OAuth:** richieste a `/authorize` con `redirect_uri` che non corrisponde esattamente a nessun valore registrato, che contiene `@`, che punta a un host esterno o che arriva con `response_type` non supportato. Va correlato con eventuali redirect 302 riusciti verso host esterni.
- **Rate-limit bypass:** lo stesso client TCP che invia valori di `X-Forwarded-For` (o header simili) diversi a ogni richiesta, oppure varianti di maiuscole e slash dello stesso percorso di login.
- **Gestione delle vulnerabilità:** una regola o un report periodico che confronta l'inventario delle dipendenze del lab con le versioni corrette elencate sopra.

## Da verificare a mano / limiti

- **Solo 7 CVE confermate con data.** È il risultato di poche ricerche mirate (JWT, GraphQL, OAuth) e non un censimento completo delle vulnerabilità API del periodo. Nessuna ricerca specifica è stata fatta su API gateway commerciali (Kong, Apigee e simili).
- **Fonti secondarie.** Le date e le versioni vengono da GitLab Advisory Database, Mend e un blog di terze parti. La pagina su CVE-2026-41856 si dichiara contenuto sperimentale generato da AI: va ricontrollata su https://spring.io/security/cve-2026-41856, che non è stata letta in questa run. Tutte le CVE vanno confermate su NVD o sull'advisory del vendor.
- **Escluse ma da approfondire:** Hono CVE-2026-22817 (confusione di `alg` con JWK senza algoritmo, secondo fonti secondarie), Directus CVE-2026-35413 (bypass di `GRAPHQL_INTROSPECTION=false`), PyJWT e fast-jwt (ID dal formato insolito). Prima di citarle servono una pagina ufficiale leggibile e una data.
- **MITRE ATT&CK:** la corrispondenza tra le classi OWASP API e le sotto-tecniche ATT&CK è indicativa e da verificare.
- **Valori di soglia:** tutte le soglie (profondità GraphQL, rate limit, numero di 404 o di ID distinti) vanno calibrate sui dati del lab: nessun valore è indicato qui.
- **Copertura dei log:** le detection su BOLA e mass assignment presuppongono log applicativi con identità, proprietario della risorsa e body delle richieste. Bisogna verificare se lo stack del lab li produce davvero, e con quali vincoli di privacy e conservazione.
- **Validazione:** ogni regola va provata nel lab isolato contro un'API vulnerabile di proposito prima di considerarla valida. Questa scheda non contiene, e volutamente non fornisce, passi operativi per sfruttare le CVE.
- **Fonte di partenza:** la README non riporta versioni, date o numeri. Tutti i dati numerici di questa scheda vengono dalle fonti web con URL indicato.

---
Fonte della tecnica: cheatsheet *API-Security* del repo [Ilias1988/Hacking-Cheatsheets](https://github.com/Ilias1988/Hacking-Cheatsheets) (MIT). Difese, detection e CVE sono aggiunte in questa scheda.

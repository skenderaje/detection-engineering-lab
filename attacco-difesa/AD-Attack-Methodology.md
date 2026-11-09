---
tipo: attacco-difesa
data: 2026-11-08
aggiornato: 2026-11-08
fonte: Ilias1988/Hacking-Cheatsheets — AD-Attack-Methodology (README.it.md)
tecnica: AD-Attack-Methodology
tags: [attacco-difesa, lab, bozza]
---

# AD-Attack-Methodology — attacco ipotizzato → difese

> [!WARNING] Bozza — scheda concettuale, nessun esercizio eseguito
> Scheda generata automaticamente il 2026-11-08 da un task pianificato. È una bozza da rivedere a mano, non un verdetto. Nessun attacco è stato eseguito.

## Attacco ipotizzato

**Scopo.** Ripercorrere, nel lab isolato, il percorso "da utente di dominio a Domain Admin" descritto dalla fonte in 6 fasi: Enumeration → Initial Access → Privilege Escalation → Lateral Movement → Persistence → Domain Dominance. In questa scheda serve a capire quali tracce lascia ogni fase e dove intervenire per prevenirla o rilevarla.

**Macchina/bersaglio tipico.** Un dominio AD di laboratorio con almeno un Domain Controller (servizi DNS 53, Kerberos 88, LDAP 389/636, SMB 445, WinRM 5985, secondo la tabella "Porte Chiave" della fonte), workstation membro e account di servizio con SPN.

**Prerequisiti (dalla fonte).**
- Fase 1: accesso di rete al segmento del DC; alcune enumerazioni funzionano senza credenziali (null session RPC, bind LDAP anonimo, enumerazione utenti via Kerberos), altre richiedono un account valido (raccolta BloodHound, ldapdomaindump).
- Fase 2: password deboli/stagionali (password spraying), LLMNR/NBT-NS attivi in rete (poisoning), host senza firma SMB (NTLM relay), account con pre-autenticazione Kerberos disattivata (AS-REP roasting).
- Fase 3: account con SPN (Kerberoasting), ACL mal configurate (GenericAll, GenericWrite, WriteDACL), deleghe Kerberos (unconstrained, constrained, RBCD).
- Fase 4–6: hash o ticket ottenuti in precedenza (Pass-the-Hash, Pass-the-Ticket, Overpass-the-Hash, WinRM); per persistenza e dominio servono l'hash di krbtgt (Golden Ticket), l'hash di un servizio (Silver Ticket) o diritti di replica (DCSync), oppure accesso al file NTDS.dit tramite shadow copy.

**Risultato atteso.** Il controllo completo del dominio: dump degli hash di tutti gli account e persistenza tramite ticket forgiati o diritti DCSync concessi come backdoor.

**Nuovi vettori emersi dalle vulnerabilità recenti (vedi sezione sotto, con fonti).** Si collegano alle fasi della fonte:
- **Fase 2 / NTLM Relay → CVE-2025-33073.** Si tratta di un bypass delle mitigazioni contro la *NTLM reflection* nel client SMB. Con un'autenticazione forzata (coercion) di un host verso un server SMB malevolo, porta a SYSTEM sulle macchine che non impongono la firma SMB. È rilevante perché la fonte indica già "trova target senza firma SMB" come prerequisito del relay.
- **Fase 3 / Abuso ACL → BadSuccessor (CVE-2025-53779).** Si abusa della migrazione degli account dMSA (delegated Managed Service Account) su domini con almeno un DC Windows Server 2025. Bastano permessi su un'OU o su oggetti dMSA, senza diritti amministrativi espliciti. È un'estensione del tema "ACL mal configurate" della fonte.
- **Fase 3 / Abuso ACL → ResetNightmare (CVE-2026-27912).** Un utente che può scrivere l'UPN di un oggetto (o che ha diritti generici di scrittura o creazione su utenti e computer) può indirizzare un cambio password Kerberos (kpasswd) verso un Domain Admin.
- **Fase 3 / Kerberoasting e scrittura SPN → KerberLoss (CVE-2026-25177).** Il controllo di unicità degli SPN si aggira con caratteri Unicode invisibili. L'effetto è un dirottamento del servizio o un downgrade da Kerberos a NTLM. Si lega al passo "GenericWrite → imposta SPN" della fonte.

**MITRE ATT&CK (indicativo).** Le tecniche della fonte corrispondono a codici noti: Kerberoasting T1558.003, AS-REP Roasting T1558.004, Golden Ticket T1558.001, Silver Ticket T1558.002, DCSync T1003.006, NTDS T1003.003, Pass-the-Hash T1550.002, Pass-the-Ticket T1550.003, LLMNR/NBT-NS Poisoning and SMB Relay T1557.001, Password Spraying T1110.003, Domain Account Discovery T1087.002. Per BadSuccessor, ResetNightmare e KerberLoss la mappatura è **da verificare**: verosimilmente rientrano in Exploitation for Privilege Escalation (T1068) o Account Manipulation (T1098), ma non l'ho confermato su una fonte.

## Vulnerabilità recenti (con fonte)

Le ricerche sono state fatte con WebSearch il 2026-11-08. Le fonti sono quasi tutte secondarie (blog, aggregatori): vanno ricontrollate sulla pagina MSRC o NVD ufficiale.

| ID | Data | Descrizione (una riga) | Fonte |
|---|---|---|---|
| CVE-2025-33073 | Pubblicata il 2025-06-10 (Patch Tuesday di giugno 2025); aggiunta al CISA KEV il 2025-10-20 | Client SMB di Windows: bypass delle mitigazioni NTLM reflection che porta a SYSTEM su host senza firma SMB imposta; sfruttata in the wild | https://nvd.nist.gov/vuln/detail/CVE-2025-33073 · https://synacktiv.com/en/publications/ntlm-reflection-is-dead-long-live-ntlm-reflection-an-in-depth-analysis-of-cve-2025 · https://www.theregister.com/2025/10/21/cisa_windows_smb_bug/ |
| CVE-2025-53779 ("BadSuccessor") | Divulgata da Akamai a maggio 2025; corretta il 2025-08-12 | Kerberos e dMSA su DC Windows Server 2025: abuso della migrazione dMSA fino ai privilegi di Domain Admin. Secondo analisi successive alla patch, la tecnica non è del tutto chiusa | https://www.helpnetsecurity.com/2025/08/13/microsoft-fixes-badsuccessor-kerberos-vulnerability-cve-2025-53779/ · https://thehackernews.com/2025/05/critical-windows-server-2025-dmsa.html · https://www.tenable.com/cve/CVE-2025-53779 |
| CVE-2026-25177 ("KerberLoss") | Corretta con gli aggiornamenti di marzo 2026 | AD DS: unicità degli SPN aggirabile con caratteri Unicode invisibili; porta a dirottamento del servizio, downgrade a NTLM o DoS (CVSS 8.8 secondo le fonti) | https://www.semperis.com/blog/identity-crisis-novel-vulnerabilities-leading-to-kerberos-downgrade-dos-and-full-domain-takeover/ · https://0patch.com/blog/micropatches-released-for-kerberloss-active-directory-domain-services-elevation-o · https://startwithidentity.com/cves/cve-2026-25177.md |
| CVE-2026-27912 ("ResetNightmare") | Corretta il 2026-04-14; micropatch 0patch rilasciata il 2026-09-07 secondo le fonti | Kerberos Change Password (kpasswd): chi può scrivere l'UPN può reimpostare la password di un Domain Admin; esiste una PoC pubblica secondo le fonti (CVSS 8.0) | https://www.semperis.com/blog/identity-crisis-novel-vulnerabilities-leading-to-kerberos-downgrade-dos-and-full-domain-takeover/ · https://www.sentinelone.com/vulnerability-database/cve-2026-27912/ · https://0patch.com/blog/micropatches-released-for-resetnightmare-windows-kerberos-elevation-of-privilege |

**Escluse, perché la fonte non era verificabile.** Un riepilogo di ricerca citava **CVE-2026-54121** (AD CS, PoC "Certighost", luglio 2026) e **CVE-2026-20849** (Kerberos EoP). Per la prima non ho trovato un URL diretto, per la seconda solo un post di forum. Non le ho incluse: vanno cercate a mano su MSRC.

## Prove da raccogliere

A livello di tipologia, senza ID evento o valori inventati. La mappatura degli ID va fatta sui log reali del lab.

- **Log di sicurezza del DC (autenticazione Kerberos).** Richieste di TGT e TGS: volumi anomali di ticket di servizio da un solo account (Kerberoasting), richieste di TGT senza pre-autenticazione (AS-REP), tipi di cifratura deboli richiesti (RC4), molti fallimenti di pre-autenticazione su utenti diversi (spraying o enumerazione utenti).
- **Log del DC sui cambi password.** Cambi o reset di password eseguiti via protocollo Kerberos kpasswd su account privilegiati, soprattutto se preceduti da una modifica dell'UPN (ResetNightmare).
- **Audit delle modifiche agli oggetti AD (Directory Service Changes).** Scritture su UPN, servicePrincipalName (con particolare attenzione a SPN che contengono caratteri non stampabili o Unicode invisibili, KerberLoss), msDS-AllowedToActOnBehalfOfOtherIdentity (RBCD), membership di gruppi privilegiati, ACL sulla radice del dominio (diritti DCSync), creazione di oggetti dMSA e scrittura degli attributi di migrazione dMSA (BadSuccessor).
- **Replica di directory.** Richieste di replica (DRSUAPI) provenienti da host che non sono DC (DCSync).
- **Rete.** Traffico LLMNR/NBT-NS e risposte da host non autorevoli (Responder); autenticazioni NTLM verso host insoliti; connessioni SMB in uscita da server verso workstation (coercion e relay, CVE-2025-33073); record DNS anomali registrati da utenti non privilegiati (vettore di coercion descritto nelle analisi di CVE-2025-33073, da verificare sulla fonte Synacktiv).
- **Endpoint (Sysmon/EDR).** Creazione di processi di servizio remoti (PsExec, SMBExec), WMI remoto, sessioni WinRM, accesso alla memoria di LSASS, `vssadmin` con creazione di shadow copy e copia di ntds.dit, esecuzione di strumenti noti (SharpHound, Rubeus, Mimikatz) quando non offuscati.
- **Inventario delle patch.** Livello di patch di ogni DC: le fonti segnalano che un patching misto tra DC lascia aperti ResetNightmare e KerberLoss.

## Difese / Detection corrispondenti

**Prevenzione (dalla fonte e generale)**
- **Fase 1.** Disabilitare null session e bind LDAP anonimo; limitare chi può leggere le ACL sensibili. Si mitiga, non si elimina: qualunque utente autenticato legge gran parte della directory.
- **Fase 2.** Disabilitare LLMNR e NBT-NS; **imporre la firma SMB su tutti gli host**, che è anche la mitigazione principale indicata per CVE-2025-33073 (https://aviatrix.ai/threat-research-center/cve-2025-33073-ntlm-reflection-attack); attivare la protezione EPA e la firma/channel binding LDAP; password policy contro le password stagionali; rimuovere "Do not require Kerberos preauthentication" dove non serve.
- **Fase 3.** Account di servizio con password lunghe o gMSA (contro il Kerberoasting); disabilitare RC4 dove possibile; audit periodico delle ACL con BloodHound, usato in chiave difensiva; MachineAccountQuota a 0 (limita l'RBCD con computer creati dall'attaccante); mettere gli account privilegiati in "Protected Users" o marcarli come sensibili e non delegabili.
- **Fase 4–6.** Tiering degli account amministrativi; LAPS per gli admin locali; rotazione doppia della password di krbtgt dopo un sospetto di compromissione; limitare i diritti di replica ai soli DC.

**Patch e mitigazioni delle vulnerabilità recenti**
- **CVE-2025-33073.** Installare l'aggiornamento di giugno 2025 sui client Windows; imporre la firma SMB. Per la lista precisa delle build corrette, vedi la pagina NVD/MSRC.
- **CVE-2025-53779 (BadSuccessor).** Installare l'aggiornamento di agosto 2025 sui DC Windows Server 2025 (https://www.helpnetsecurity.com/2025/08/13/microsoft-fixes-badsuccessor-kerberos-vulnerability-cve-2025-53779/). Rivedere comunque chi può creare o modificare oggetti dMSA nelle OU, perché secondo le analisi post-patch la tecnica non è del tutto chiusa (fonte secondaria: https://www.trackr.live/?p=1273, da verificare).
- **CVE-2026-25177 (KerberLoss).** Aggiornamenti di marzo 2026 su **tutti** i DC; limitare "Validated write to service principal name" al minimo indispensabile.
- **CVE-2026-27912 (ResetNightmare).** Aggiornamenti di aprile 2026 su **tutti** i DC; togliere il diritto di scrivere l'UPN agli account che non ne hanno bisogno; rivedere le deleghe che permettono reset di password o creazione di oggetti. Le misure di hardening sono riassunte in https://hivesecurity.gitlab.io/blog/kerberloss-resetnightmare-active-directory-defense e vanno confrontate con la guida originale di Semperis.

**Idee di detection (logica di regola a parole)**
- *Kerberoasting.* Un singolo account richiede molti ticket di servizio per SPN diversi in una finestra breve, con cifratura RC4. Soglia da calibrare sui dati del lab.
- *AS-REP / spraying.* Molte richieste di TGT fallite sullo stesso host sorgente verso utenti diversi, oppure richieste di TGT senza pre-autenticazione. Soglia da calibrare sui dati del lab.
- *DCSync.* Una richiesta di replica di directory da un host o account che non è un DC.
- *ResetNightmare.* Modifica dell'UPN di un oggetto seguita a breve da un cambio password via kpasswd che colpisce un account privilegiato. Va correlata la coppia "scrittura UPN → cambio password".
- *KerberLoss.* Scrittura di servicePrincipalName che contiene caratteri Unicode di formato o invisibili; allarme anche su SPN duplicati "visivamente".
- *BadSuccessor.* Creazione di oggetti dMSA o modifica degli attributi di migrazione dMSA da parte di account non amministrativi; nuovi permessi di creazione oggetti su OU.
- *NTLM relay / CVE-2025-33073.* Un host che si autentica via NTLM verso un altro host subito dopo una coercion (chiamate RPC di tipo PrinterBug o PetitPotam); login di rete come account macchina da indirizzi inattesi; registrazioni DNS anomale.
- *Golden/Silver Ticket.* Ticket con durate o campi incoerenti con la policy del dominio, oppure uso di TGS senza un TGT corrispondente. La logica esatta dipende dalla telemetria disponibile: va provata nel lab.
- *NTDS.dit.* Creazione di shadow copy sul DC seguita da accesso o copia di file NTDS/SYSTEM.

## Da verificare a mano / limiti

- **Fonte README.** È una cheatsheet offensiva orientata ai CTF: non contiene difese, ID evento o soglie. Tutta la parte difensiva è ragionamento generale, da validare nel lab.
- **Fonti web.** Quasi tutte secondarie (news, blog, aggregatori). Per ogni CVE vanno confermati su **MSRC/NVD**: data, build corrette, punteggio CVSS (per BadSuccessor le fonti riportano 7.2 e 8.3, in disaccordo) e prerequisiti esatti.
- **CVE-2025-33073.** Le fonti non concordano sul perimetro: alcune la descrivono come escalation solo locale, altre come problema remoto o Kerberos relay. Va letta l'analisi Synacktiv prima di modellare la detection.
- **BadSuccessor.** Riguarda solo domini con almeno un DC Windows Server 2025. Va controllato se il lab ha un DC Windows Server 2025; se non ne ha, il vettore non è riproducibile.
- **Sfruttamento residuo di BadSuccessor dopo la patch.** È affermato da una fonte singola, da verificare.
- **Mappatura ATT&CK** delle tre vulnerabilità del 2025–2026: da verificare.
- **ID evento Windows, campi di log e soglie.** Volutamente omessi: vanno ricavati dai log reali del lab (Security, Directory Service, Sysmon) dopo aver abilitato l'audit avanzato.
- **CVE-2026-54121 e CVE-2026-20849.** Escluse per mancanza di una fonte verificabile: da ricercare a mano.
- **Detection non provate.** Nessuna regola di questa scheda è stata provata: vanno prima eseguite le singole fasi nel lab isolato, poi verificato che i log attesi compaiano davvero.

---
Fonte della tecnica: cheatsheet *AD-Attack-Methodology* del repo [Ilias1988/Hacking-Cheatsheets](https://github.com/Ilias1988/Hacking-Cheatsheets) (MIT). Difese, detection e CVE sono aggiunte in questa scheda.

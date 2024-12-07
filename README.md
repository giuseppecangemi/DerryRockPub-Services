# Documentazione Derry Rock Pub

## Introduzione

Questo progetto è un'applicazione web sviluppata con Flask per la gestione e registrazione dei soci del "Derry Rock Pub" di Roma. I soci possono registrarsi tramite un modulo accessibile tramite link o QRCode. Gli amministratori hanno la possibilità di visualizzare e gestire i dati dei soci sia in tempo reale che offline, approvando l'accesso all'associazione. Una volta autorizzato, l'owner dovrà avviare un programma locale che automatizza l'inserimento del numero progressivo della tessera (con opzione di inserimento manuale) e invia un'email di benvenuto con la tessera allegata al nuovo socio. Tutte le informazioni vengono archiviate in un database PostgreSQL, con una copia dei dati in formato Excel mantenuta localmente.

## Struttura del Progetto

### File Python

- **app.py**: Contiene la logica del server Flask, definisce le rotte e gestisce le operazioni sul database.
- **gen_qrcode.py**: Crea il QRcode utilizzato per collegarsi almodulo di adesione all'associazione.
- **pdf.py**: Crea il PDF inserendo i dati dei soci.
- **mail.py**: Predispone e invia la mail con allegato la tessera associativa.
- **export_DB.py**: Crea una copia in formato excel, disponibile in locale.
- **automazione.py**: Gestisce la creazione della tessera, eseguendo tutti i file Python eccetto ***app.py***.

### File HTML

1. **form.html**: Modulo di registrazione per i soci del pub, in cui gli utenti possono inserire i propri dati.
2. **login.html**: Modulo di accesso per gli amministratori, che richiede l'inserimento di un PIN per autenticarsi.
3. **view_users.html**: Visualizzazione della lista dei soci registrati, dove gli amministratori possono vedere tutti i dettagli dei soci.

## Dettagli del Modulo di Registrazione Soci (form.html)

Il modulo di registrazione consente agli utenti di inserire i propri dati personali. I campi presenti nel modulo includono:

- **Nome**: Un campo di testo per il nome del socio (obbligatorio).
- **Cognome**: Un campo di testo per il cognome del socio (obbligatorio).
- **Email**: Un campo di tipo email per l'indirizzo email del socio (obbligatorio).
- **Città**: Un campo di testo per la città di residenza (obbligatorio).
- **Data di Nascita**: Un campo di tipo data che accetta date tra il 1900-01-01 e la data odierna. Una funzione JavaScript valida se la data inserita è nel formato corretto e rientra nel range consentito.
- **Residenza**: Un campo di testo per l'indirizzo di residenza (obbligatorio).
- **Sesso**: Un campo a discesa (select) che consente di scegliere tra "Maschile", "Femminile" o "Altro" (obbligatorio).
- **Numero Carta d'Identità**: Un campo di testo per inserire il numero della carta d'identità (facoltativo).
- **File**: Un campo per caricare un file immagine (facoltativo), come una foto del socio.

## Checkbox di Accettazione

- **Presa visione dello statuto**: Un checkbox che richiede la presa visione dello statuto dell'associazione. Il link al file PDF dello statuto è incluso e il checkbox è obbligatorio.
- **Dichiarazioni mendaci**: Un checkbox che avverte l'utente delle conseguenze di dichiarazioni mendaci riguardo alla richiesta di ammissione come socio (obbligatorio).
- **Autorizzazione al trattamento dei dati**: Un checkbox che autorizza il trattamento dei dati personali per finalità di registrazione, in conformità con il GDPR (obbligatorio).

## Submit

- Un pulsante di invio per inviare i dati del modulo. Quando il modulo viene inviato, una funzione di validazione esegue il controllo finale.
La validazione della data di nascita include controlli per assicurarsi che l'utente inserisca una data valida compresa tra il 1900 e la data odierna.

## Dettagli dell'automazione (file batch lanciato in locale)
Questo script gestisce la generazione delle tessere per i soci approvati, invia le tessere tramite email e aggiorna il database con i numeri delle tessere generati. Inoltre, esporta i dati in un file Excel. Di seguito sono descritti i vari passaggi e le funzionalità implementate.

1. **Connessione al Database**
   - Il database viene connesso utilizzando SQLAlchemy e il parametro `DATABASE_URL` caricato dal file `.env`.
   
2. **Caricamento dei Dati**
   - Viene eseguita una query per estrarre tutti i dati dalla tabella `users` del database e il risultato viene caricato in un DataFrame Pandas.

3. **Verifica e Aggiornamento del Numero della Tessera**
   - La colonna `numero_tessera` viene convertita in valori numerici.
   - Viene calcolato il numero della tessera da assegnare al prossimo socio non manuale, partendo dal massimo valore già presente nel database.

4. **Controllo del Range del Numero Tessera**
   - Viene verificato che il numero della tessera generato non superi un valore massimo predefinito (ad esempio, 231400).

5. **Assegnazione del Numero Tessera ai Soci Approvati**
   - I soci approvati senza numero di tessera vengono assegnati il prossimo numero disponibile.
   - Per i soci manuali, viene mantenuto il numero di tessera assegnato dall'owner.

6. **Creazione e Invio delle Tessere**
   - Per ogni socio approvato che non ha ancora ricevuto la tessera, viene generato un file PDF contenente la tessera personalizzata con il numero e i dati del socio.
   - Il file PDF viene inviato via email al socio tramite una funzione `send_email`.

7. **Aggiornamento del Database**
   - Dopo che la tessera è stata inviata, i dati del database vengono aggiornati con il nuovo numero della tessera e lo stato "inviato".

8. **Esportazione dei Dati**
   - Infine, i dati aggiornati vengono esportati in un file Excel.


## Conclusione

Il progetto "Derry Rock Pub" ha lo scopo di semplificare e automatizzare la gestione dei soci e delle tessere associative per il pub. Attraverso l'uso di una piattaforma web sviluppata con Flask, i soci possono registrarsi facilmente, mentre gli amministratori possono gestire i dati in modo efficiente. L'automazione locale, attraverso uno script batch, facilita la creazione e l'invio delle tessere personalizzate, riducendo il lavoro manuale e migliorando l'esperienza complessiva per i soci. 

L'uso di tecnologie come Python, Pandas, SQLAlchemy, e ReportLab per la generazione dei PDF, insieme all'integrazione con un database PostgreSQL, garantisce una gestione fluida e sicura delle informazioni. Il sistema è progettato per essere scalabile e sicuro, con tutte le operazioni di invio email e archiviazione dei dati conformi alle normative sulla privacy.

Il progetto si conclude con l'esportazione dei dati in formato Excel, per garantire una copia di backup e la possibilità di monitorare e analizzare i dati in modo semplice. Con queste funzionalità, l'applicazione non solo semplifica la gestione dei soci, ma ottimizza anche i processi amministrativi, permettendo agli amministratori del "Derry Rock Pub" di concentrarsi su altre attività strategiche.

# Sito web squadra ciclistica (Flask)

Sito semplice per una squadra ciclistica con: storia, vittorie più importanti,
elenco atleti, staff tecnico e contatti. Pensato per essere hostato gratuitamente
su **Render**.

## Struttura del progetto

```
team-ciclistico/
├── app.py                 # App Flask + dati della squadra (modifica qui i contenuti)
├── requirements.txt        # Dipendenze Python
├── Procfile                 # Comando di avvio per Render
├── templates/
│   ├── base.html
│   └── index.html
└── static/
    ├── css/style.css
    └── img/logo.jpg
```

## 1. Personalizzare i contenuti

Apri `app.py` e modifica il dizionario `TEAM_DATA` in cima al file:
- `nome_squadra`, `motto` (frase/slogan)
- `storia` → anno di fondazione e testo
- `vittorie` → lista di vittorie (anno, titolo, descrizione)
- `atleti` → lista di corridori (nome, categoria)
- `staff` → direttori sportivi e istruttori
- `contatti` → email, telefono, indirizzo, social

Non serve toccare l'HTML per cambiare i testi.

## 2. Provarlo in locale

```bash
python -m venv venv
source venv/bin/activate      # su Windows: venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

Il sito sarà disponibile su http://localhost:5000

## 3. Pubblicarlo su Render (piano gratuito)

1. Crea un repository su GitHub e carica tutti i file di questa cartella
   (compreso `Procfile` e `requirements.txt`).
2. Vai su https://render.com e crea un account (puoi accedere anche con GitHub).
3. Clicca **New +** → **Web Service**.
4. Collega il repository GitHub appena creato.
5. Nelle impostazioni del servizio:
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app`
   - **Instance Type**: `Free`
6. Clicca **Create Web Service**. Render farà build e deploy automaticamente.
7. Dopo qualche minuto il sito sarà online su un indirizzo tipo
   `https://tuo-nome-progetto.onrender.com`

Nota: con il piano gratuito di Render, il servizio "si addormenta" dopo un
periodo di inattività e il primo caricamento dopo una pausa può richiedere
qualche secondo in più: è normale.

## 4. Nuove funzioni: Galleria foto e Iscrizioni

- **Galleria foto** (`#galleria`): il pulsante "+ Aggiungi foto" apre una finestra
  per caricare una o più immagini (JPG, PNG, GIF, WEBP, max 8MB). Le foto vengono
  salvate in `static/img/galleria/` e i loro dati (nome file, didascalia, data)
  in `data/galleria.json`.
- **Iscrizione squadra** (`#iscrizione`): modulo con nome, cognome, anno di
  nascita, città di provenienza, categoria, email, telefono, ecc. Ogni richiesta
  viene salvata in `data/iscrizioni.json` (puoi aprirlo per leggere le iscrizioni
  ricevute).

⚠️ **Attenzione se pubblichi su Render (piano gratuito):** il file system è
*effimero* — ad ogni riavvio o nuovo deploy del servizio, i file in `data/` e le
foto caricate in `static/img/galleria/` vengono **cancellati**. Per uso reale
(iscrizioni e foto che devono restare nel tempo) serve una delle seguenti
soluzioni:
- attivare un **Persistent Disk** su Render (a pagamento) collegato alle cartelle
  `data/` e `static/img/galleria/`;
- oppure salvare i dati su un servizio esterno (es. un database come
  PostgreSQL/Supabase, o uno storage come Cloudinary/S3 per le foto).

Per test e demo locali (o su hosting con disco persistente) funziona tutto
subito, senza configurazioni aggiuntive.

Il caricamento foto **richiede l'accesso admin** (vedi sezione successiva):
solo chi conosce la password admin vede il pulsante "+ Aggiungi foto" e può
effettivamente caricare immagini — è bloccato anche lato server, quindi non è
aggirabile da chi non conosce la password.

## 5. Accesso admin (per aggiungere foto)

- Link **"Admin"** in fondo al menu del sito → pagina di login con password.
- Password di default: `piesse2026` — **cambiala assolutamente** prima di
  mettere il sito online, impostando una variabile d'ambiente `ADMIN_PASSWORD`
  nelle impostazioni di Render (Environment → Add Environment Variable):
  - Key: `ADMIN_PASSWORD`
  - Value: la password che vuoi usare tu/lo staff
- Consiglio: imposta anche una variabile `SECRET_KEY` (una stringa lunga e
  casuale) per rendere più sicura la sessione di login:
  - Key: `SECRET_KEY`
  - Value: una stringa casuale a piacere (es. generata con `python -c "import secrets; print(secrets.token_hex(32))"`)
- Una volta loggato, l'admin resta autenticato nel browser finché non clicca
  "Esci (admin)" nel menu o non cancella i cookie del sito.
- Non c'è (per ora) un sistema multi-utente: è un'unica password condivisa tra
  chi gestisce le foto. Se in futuro serve un accesso diverso per più persone,
  si può aggiungere un vero sistema di account.

## 6. Prossimi passi (facoltativi)

- Aggiungere foto reali degli atleti e della squadra (cartella `static/img/`)
- Aggiungere una pagina calendario gare
- Collegare un dominio personalizzato da Render (impostazioni → Custom Domain)

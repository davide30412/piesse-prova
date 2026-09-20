"""
Sito web per squadra ciclistica - Flask app
--------------------------------------------
Modifica i dati qui sotto (dizionario TEAM_DATA) per personalizzare
storia, vittorie, atleti, staff e contatti senza toccare l'HTML.
"""

import os
import json
import uuid
from datetime import datetime

from functools import wraps

from flask import Flask, render_template, request, redirect, url_for, flash, session
from werkzeug.utils import secure_filename

app = Flask(__name__)

# Chiave necessaria per i messaggi di conferma/errore (flash).
# In produzione impostala come variabile d'ambiente SECRET_KEY su Render.
app.secret_key = os.environ.get("SECRET_KEY", "cambia-questa-chiave-in-produzione")

# ---------------------------------------------------------------------
# CONFIGURAZIONE GALLERIA FOTO E MODULO ISCRIZIONI
# ---------------------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
GALLERIA_FILE = os.path.join(DATA_DIR, "galleria.json")
ISCRIZIONI_FILE = os.path.join(DATA_DIR, "iscrizioni.json")

UPLOAD_FOLDER = os.path.join(BASE_DIR, "static", "img", "galleria")
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp"}

app.config["MAX_CONTENT_LENGTH"] = 8 * 1024 * 1024  # max 8MB per richiesta


def _assicura_cartelle():
    os.makedirs(DATA_DIR, exist_ok=True)
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)


def _leggi_json(percorso):
    if not os.path.exists(percorso):
        return []
    try:
        with open(percorso, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return []


def _scrivi_json(percorso, dati):
    _assicura_cartelle()
    with open(percorso, "w", encoding="utf-8") as f:
        json.dump(dati, f, ensure_ascii=False, indent=2)


def _estensione_consentita(nome_file):
    return "." in nome_file and nome_file.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


# ---------------------------------------------------------------------
# ACCESSO ADMIN — solo chi ha la password può aggiungere foto
# ---------------------------------------------------------------------
# IMPORTANTE: su Render vai in Environment e imposta una variabile
# ADMIN_PASSWORD con una password tua, diversa da quella di default qui sotto.
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "piesse2026")


def richiede_admin(vista):
    @wraps(vista)
    def controllo(*args, **kwargs):
        if not session.get("is_admin"):
            flash("Devi accedere come admin per farlo.", "errore")
            return redirect(url_for("admin_login"))
        return vista(*args, **kwargs)
    return controllo

# ---------------------------------------------------------------------
# DATI DELLA SQUADRA — modifica qui i contenuti del sito
# ---------------------------------------------------------------------
TEAM_DATA = {
    "nome_squadra": "Piesse Cycling Team",
    "motto": "Ogni salita ha una storia. Noi la scriviamo in sella.",

    "storia": {
        "anno_fondazione": 2010,
        "testo": (
            "Fondata nel 2010 da un gruppo di amici uniti dalla passione per il ciclismo, "
            "la Piesse Cycling Team è cresciuta negli anni fino a diventare una "
            "delle realtà più solide del ciclismo dilettantistico e giovanile della regione. "
            "Nata da una piccola officina di biciclette, la squadra ha saputo costruire un "
            "percorso fatto di sacrifici, allenamenti quotidiani e tanta strada macinata insieme. "
            "Oggi conta atleti di diverse categorie, un settore giovanile in espansione e uno "
            "staff tecnico che segue ogni corridore in ogni fase della stagione."
        ),
    },

    "vittorie": [
        {
            "anno": "2023",
            "titolo": "Campionato Regionale a cronometro",
            "descrizione": "Vittoria nella categoria Elite grazie a una prova cronometrata perfetta.",
        },
        {
            "anno": "2022",
            "titolo": "Giro delle Colline — Tappa Regina",
            "descrizione": "Successo in solitaria sull'ultima salita, con oltre un minuto di vantaggio.",
        },
        {
            "anno": "2021",
            "titolo": "Coppa Primavera",
            "descrizione": "Primo e terzo posto nella classifica generale a squadre.",
        },
        {
            "anno": "2019",
            "titolo": "Trofeo Città di Roma",
            "descrizione": "Vittoria di tappa e maglia di leader per tre giorni consecutivi.",
        },
    ],

    "atleti": [
        {
            "nome": "Ettore Scottoni",
            "categoria": "Allievo 2",
        },
        {
            "nome": "Davide Sellati",
            "categoria": "Allievo 1",
        },
        {
            "nome": "Giovanni Mancini",
            "categoria": "Allievo 2",
        },
        {
            "nome": "Mirko Troiani",
            "categoria": "Esordiente 2",
        },
    ],

    "staff": {
        "direttori_sportivi": ["Luca Petrolati", "Danilo Sellati"],
        "istruttori": ["Carlo Dullizia", "Marco Petrolati"],
    },

    "contatti": {
        "email": "info@piessecyclingteam.it",
        "telefono": "+39 06 1234567",
        "indirizzo": "Via dello Sport 10, 00100 Roma (RM)",
        "instagram": "https://instagram.com/piessecyclingteam",
        "facebook": "https://facebook.com/piessecyclingteam",
    },
}


@app.route("/")
def home():
    foto_galleria = list(reversed(_leggi_json(GALLERIA_FILE)))
    return render_template(
        "index.html",
        team=TEAM_DATA,
        foto_galleria=foto_galleria,
        is_admin=session.get("is_admin", False),
    )


@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    if session.get("is_admin"):
        return redirect(url_for("home", _anchor="galleria"))

    if request.method == "POST":
        password = request.form.get("password", "")
        if password and password == ADMIN_PASSWORD:
            session["is_admin"] = True
            flash("Accesso admin effettuato. Ora puoi aggiungere foto.", "successo")
            return redirect(url_for("home", _anchor="galleria"))
        flash("Password errata.", "errore")
        return redirect(url_for("admin_login"))

    return render_template("admin_login.html", team=TEAM_DATA)


@app.route("/admin/logout")
def admin_logout():
    session.pop("is_admin", None)
    flash("Disconnesso dall'area admin.", "successo")
    return redirect(url_for("home"))


@app.route("/galleria/aggiungi", methods=["POST"])
@richiede_admin
def aggiungi_foto():
    _assicura_cartelle()
    file_caricati = request.files.getlist("foto")
    didascalia = request.form.get("didascalia", "").strip()

    if not file_caricati or all(f.filename == "" for f in file_caricati):
        flash("Seleziona almeno una foto prima di caricare.", "errore")
        return redirect(url_for("home", _anchor="galleria"))

    galleria = _leggi_json(GALLERIA_FILE)
    aggiunte = 0

    for file in file_caricati:
        if file and file.filename and _estensione_consentita(file.filename):
            estensione = file.filename.rsplit(".", 1)[1].lower()
            nome_sicuro = f"{uuid.uuid4().hex}.{estensione}"
            file.save(os.path.join(UPLOAD_FOLDER, nome_sicuro))
            galleria.append({
                "file": nome_sicuro,
                "didascalia": didascalia,
                "caricata_il": datetime.now().strftime("%d/%m/%Y %H:%M"),
            })
            aggiunte += 1

    if aggiunte:
        _scrivi_json(GALLERIA_FILE, galleria)
        flash(f"{aggiunte} foto caricata/e con successo!", "successo")
    else:
        flash("Formato non supportato. Usa JPG, PNG, GIF o WEBP.", "errore")

    return redirect(url_for("home", _anchor="galleria"))


@app.route("/iscrizione/invia", methods=["POST"])
def invia_iscrizione():
    _assicura_cartelle()

    campi_obbligatori = ["nome", "cognome", "anno_nascita", "citta", "email"]
    dati = {campo: request.form.get(campo, "").strip() for campo in [
        "nome", "cognome", "anno_nascita", "citta", "categoria",
        "email", "telefono", "societa_attuale", "messaggio",
    ]}

    mancanti = [c for c in campi_obbligatori if not dati.get(c)]
    if mancanti:
        flash("Compila tutti i campi obbligatori (nome, cognome, anno di nascita, città, email).", "errore")
        return redirect(url_for("home", _anchor="iscrizione"))

    iscrizioni = _leggi_json(ISCRIZIONI_FILE)
    dati["ricevuta_il"] = datetime.now().strftime("%d/%m/%Y %H:%M")
    iscrizioni.append(dati)
    _scrivi_json(ISCRIZIONI_FILE, iscrizioni)

    flash("Richiesta di iscrizione inviata! Ti contatteremo al più presto.", "successo")
    return redirect(url_for("home", _anchor="iscrizione"))


if __name__ == "__main__":
    # In locale usa "python app.py". Su Render viene usato gunicorn (vedi Procfile).
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)

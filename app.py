import os
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

import os
import sqlite3
import csv
import io
import pickle
from flask import Flask, render_template, request, redirect, url_for, flash, session, Response
import subprocess
import signal
from recuperer_emails import (
    analyser_et_enregistrer_emails,
    analyser_et_enregistrer_emails_manuel,
    get_gmail_service,
    get_email_content,
    est_email_important,
    ajouter_email
)
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build

app = Flask(__name__)
app.secret_key = "agent_secret"
DATABASE_NAME = "emails.db"
CLIENT_SECRETS_FILE = "credentials.json"
TOKEN_FOLDER = "tokens"
SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]

os.makedirs(TOKEN_FOLDER, exist_ok=True)

@app.route("/login")
def login():
    flow = Flow.from_client_secrets_file(
        CLIENT_SECRETS_FILE,
        scopes=SCOPES,
        redirect_uri=url_for("oauth2callback", _external=True),
    )
    authorization_url, state = flow.authorization_url(
        access_type="offline",
        include_granted_scopes="true",
        prompt="consent"
    )
    session["state"] = state
    return redirect(authorization_url)

@app.route("/utilisateurs")
def utilisateurs():
    if "user_email" not in session:
        flash("Veuillez vous connecter.")
        return redirect(url_for("login"))

    utilisateurs = []
    for fichier in os.listdir("tokens"):
        if fichier.startswith("token_") and fichier.endswith(".pickle"):
            email = fichier.replace("token_", "").replace(".pickle", "")
            utilisateurs.append(email)

    return render_template("utilisateurs.html", utilisateurs=utilisateurs)

@app.route("/supprimer_utilisateur", methods=["POST"])
def supprimer_utilisateur():
    email = request.form.get("email")
    chemin_token = os.path.join("tokens", f"token_{email}.pickle")
    if os.path.exists(chemin_token):
        os.remove(chemin_token)
        flash(f"Utilisateur {email} supprimé.")
    else:
        flash("Token introuvable.")
    return redirect(url_for("utilisateurs"))

@app.route("/sauvegarde", methods=["POST"])
def sauvegarde():
    try:
        subprocess.run(["python3", "backup.py"])
        flash("💾 Sauvegarde effectuée avec succès.")
    except Exception as e:
        flash(f"Erreur lors de la sauvegarde : {e}")
    return redirect(url_for("index"))



@app.route("/surveiller", methods=["POST"])
def surveiller():
    try:
        subprocess.Popen(["python3", "agent_surveillance.py"])
        flash("Agent IA lancé en arrière-plan.")
    except Exception as e:
        flash(f"Erreur lors du lancement de l'agent : {e}")
    return redirect(url_for("index"))

@app.route("/arreter_surveillance", methods=["POST"])
def arreter_surveillance():
    try:
        result = subprocess.run(["ps", "aux"], stdout=subprocess.PIPE, text=True)
        lines = result.stdout.splitlines()
        count = 0
        for line in lines:
            if "agent_surveillance.py" in line and "python3" in line:
                pid = int(line.split()[1])
                os.kill(pid, signal.SIGKILL)
                count += 1
        if count:
            flash(f"{count} processus de surveillance arrêtés.")
        else:
            flash("Aucun processus agent_surveillance.py actif trouvé.")
    except Exception as e:
        flash(f"Erreur lors de l'arrêt : {e}")
    return redirect(url_for("index"))

@app.route("/oauth2callback")
def oauth2callback():
    state = session["state"]
    flow = Flow.from_client_secrets_file(
        CLIENT_SECRETS_FILE,
        scopes=SCOPES,
        state=state,
        redirect_uri=url_for("oauth2callback", _external=True),
    )
    flow.fetch_token(authorization_response=request.url)

    credentials = flow.credentials
    service = build("gmail", "v1", credentials=credentials)
    profile = service.users().getProfile(userId="me").execute()
    email = profile["emailAddress"]

    token_path = os.path.join(TOKEN_FOLDER, f"token_{email}.pickle")
    with open(token_path, "wb") as token:
        pickle.dump(credentials, token)

    session["user_email"] = email
    flash(f"Connexion réussie pour {email}.")
    return redirect(url_for("index"))

@app.route("/", methods=["GET"])
@app.route("/page/<int:page>", methods=["GET"])
def index(page=1):
    search_query = request.args.get("search", "")
    filter_type = request.args.get("filter", "")
    exp_filter = request.args.get("exp", "")
    date_filter = request.args.get("date", "")

    per_page = 10
    offset = (page - 1) * per_page
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()

    where_clauses = []
    params = []

    if search_query:
        where_clauses.append("(sujet LIKE ? OR contenu LIKE ?)")
        params.extend(['%' + search_query + '%'] * 2)

    if filter_type:
        where_clauses.append("(sujet LIKE ? OR contenu LIKE ?)")
        params.extend(['%' + filter_type + '%'] * 2)

    if exp_filter:
        where_clauses.append("expediteur LIKE ?")
        params.append('%' + exp_filter + '%')

    if date_filter == "today":
        from datetime import datetime
        date_str = datetime.now().strftime("%d %b %Y")
        where_clauses.append("date LIKE ?")
        params.append('%' + date_str + '%')
    elif date_filter == "week":
        from datetime import datetime, timedelta
        one_week_ago = datetime.now() - timedelta(days=7)
        where_clauses.append("date >= ?")
        params.append(one_week_ago.strftime("%a, %d %b %Y"))
    elif date_filter == "month":
        from datetime import datetime, timedelta
        one_month_ago = datetime.now() - timedelta(days=30)
        where_clauses.append("date >= ?")
        params.append(one_month_ago.strftime("%a, %d %b %Y"))

    where_sql = " AND ".join(where_clauses)
    if where_sql:
        where_sql = "WHERE " + where_sql

    query = f"""
        SELECT id, sujet, expediteur, date, contenu 
        FROM emails 
        {where_sql} 
        ORDER BY id DESC LIMIT ? OFFSET ?
    """
    params.extend([per_page, offset])
    cursor.execute(query, params)
    emails = cursor.fetchall()

    count_query = f"SELECT COUNT(*) FROM emails {where_sql}"
    cursor.execute(count_query, params[:-2])
    total_emails = cursor.fetchone()[0]

    conn.close()
    total_pages = (total_emails + per_page - 1) // per_page

    return render_template(
        "index.html",
        emails=emails,
        search_query=search_query,
        filter_type=filter_type,
        exp_filter=exp_filter,
        date_filter=date_filter,
        page=page,
        total_pages=total_pages,
        user_email=session.get("user_email")
    )

@app.route("/email/<int:email_id>")
def view_email(email_id):
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT sujet, expediteur, date, contenu FROM emails WHERE id = ?", (email_id,))
    email = cursor.fetchone()
    conn.close()
    if not email:
        return "E-mail non trouvé", 404
    return render_template("email.html", email=email, email_id=email_id, page=1)

@app.route("/delete/<int:email_id>", methods=["POST"])
def delete_email(email_id):
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM emails WHERE id = ?", (email_id,))
    conn.commit()
    conn.close()
    flash("E-mail supprimé avec succès.")
    return redirect(url_for('index'))

@app.route("/export_csv")
def export_csv():
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT sujet, expediteur, date, contenu FROM emails ORDER BY id DESC")
    emails = cursor.fetchall()
    conn.close()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Sujet", "Expéditeur", "Date", "Contenu"])
    for email in emails:
        writer.writerow(email)

    output.seek(0)
    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment;filename=emails.csv"}
    )

@app.route("/analyser", methods=["POST"])
def analyser():
    if "user_email" in session:
        try:
            analyser_et_enregistrer_emails(session["user_email"])
            flash("Analyse terminée : e-mails analysés avec succès.")
        except Exception as e:
            flash(f"Erreur lors de l'analyse : {e}")
    return redirect(url_for("index"))

@app.route("/choisir_emails")
def choisir_emails():
    try:
        service = get_gmail_service(port=5520)
        results = service.users().messages().list(userId='me', maxResults=15).execute()
        messages = results.get('messages', [])
        emails = []
        for message in messages:
            msg = service.users().messages().get(userId='me', id=message['id']).execute()
            headers = msg.get("payload", {}).get("headers", [])

            sujet = next((h["value"] for h in headers if h["name"] == "Subject"), "Sans sujet")
            expediteur = next((h["value"] for h in headers if h["name"] == "From"), "Inconnu")
            date = next((h["value"] for h in headers if h["name"] == "Date"), "?")
            contenu = get_email_content(msg)

            emails.append({
                "id": message['id'],
                "sujet": sujet,
                "expediteur": expediteur,
                "date": date,
                "contenu": contenu
            })
        return render_template("choisir_email.html", emails=emails)
    except Exception as e:
        flash(f"Erreur lors du chargement des e-mails : {e}")
        return redirect(url_for("index"))

@app.route("/importer_selection", methods=["POST"])
def importer_selection():
    selected_ids = request.form.getlist("selected_emails")
    try:
        service = get_gmail_service(port=5520)
        for msg_id in selected_ids:
            msg = service.users().messages().get(userId='me', id=msg_id).execute()
            headers = msg.get("payload", {}).get("headers", [])

            sujet = next((h["value"] for h in headers if h["name"] == "Subject"), "Sans sujet")
            expediteur = next((h["value"] for h in headers if h["name"] == "From"), "Inconnu")
            date = next((h["value"] for h in headers if h["name"] == "Date"), "?")
            contenu = get_email_content(msg)

            if est_email_important(sujet, contenu):
                ajouter_email(sujet, expediteur, date, contenu)
                flash(f"E-mail important ajouté : {sujet}")
        flash("Importation manuelle terminée.")
    except Exception as e:
        flash(f"Erreur lors de l'importation : {e}")
    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(debug=True, port=5500)
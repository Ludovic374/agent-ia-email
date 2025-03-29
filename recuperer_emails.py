import base64
import sqlite3
import os
import pickle
import pyttsx3
from flask import flash
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

DATABASE_NAME = "emails.db"
MOTS_CLES_IMPORTANTS = ["virement", "facture", "paiement", "reçu", "banque", "note", "résultat", "évaluation"]

moteur_voix = pyttsx3.init()

def lire_alerte_avec_voix(texte):
    moteur_voix.say(texte)
    moteur_voix.runAndWait()

def get_gmail_service(user_email=None, port=None):
    if user_email:
        token_path = f"tokens/token_{user_email}.pickle"
        if not os.path.exists(token_path):
            raise Exception(f"Token non trouvé pour {user_email}. Veuillez vous connecter.")
        with open(token_path, "rb") as token:
            creds = pickle.load(token)
        if not creds.valid:
            raise Exception("Token invalide ou expiré pour l'utilisateur.")
    else:
        flow = InstalledAppFlow.from_client_secrets_file(
            'credentials.json',
            ['https://www.googleapis.com/auth/gmail.readonly']
        )
        creds = flow.run_local_server(port=port or 5520)
    return build('gmail', 'v1', credentials=creds)

def ajouter_email(sujet, expediteur, date, contenu):
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO emails (sujet, expediteur, date, contenu)
        VALUES (?, ?, ?, ?)
    """, (sujet, expediteur, date, contenu))
    conn.commit()
    conn.close()
    print(f"✅ E-mail ajouté : {sujet}")

def est_email_important(sujet, contenu):
    sujet = sujet.lower()
    contenu = contenu.lower()
    return any(mot in sujet or mot in contenu for mot in MOTS_CLES_IMPORTANTS)

def get_email_content(msg):
    try:
        payload = msg.get("payload", {})
        if "parts" in payload:
            for part in payload["parts"]:
                if part.get("mimeType") == "text/plain" and "data" in part.get("body", {}):
                    return base64.urlsafe_b64decode(part["body"]["data"]).decode("utf-8", errors="ignore")
        elif "data" in payload.get("body", {}):
            return base64.urlsafe_b64decode(payload["body"]["data"]).decode("utf-8", errors="ignore")
    except Exception as e:
        print(f"Erreur lecture contenu e-mail : {e}")
    return ""

def analyser_et_enregistrer_emails_manuel():
    service = get_gmail_service(port=5520)
    _analyser_et_enregistrer(service)

def analyser_et_enregistrer_emails(user_email):
    service = get_gmail_service(user_email=user_email)
    _analyser_et_enregistrer(service)

def _analyser_et_enregistrer(service):
    try:
        results = service.users().messages().list(userId='me', maxResults=10).execute()
        messages = results.get('messages', [])
        if not messages:
            print("📭 Aucun e-mail trouvé.")
            return

        for message in messages:
            msg = service.users().messages().get(userId='me', id=message['id']).execute()
            headers = msg.get("payload", {}).get("headers", [])

            sujet = next((h.get("value", "") for h in headers if h.get("name") == "Subject"), "Sans sujet")
            expediteur = next((h.get("value", "") for h in headers if h.get("name") == "From"), "Inconnu")
            date = next((h.get("value", "") for h in headers if h.get("name") == "Date"), "?")
            contenu = get_email_content(msg)

            if est_email_important(sujet, contenu):
                ajouter_email(sujet, expediteur, date, contenu)
                lire_alerte_avec_voix(f"Email important : {sujet}")
                flash("🔔 Nouvel e-mail important détecté")
    except Exception as e:
        print(f"❌ Erreur analyse e-mails : {e}")
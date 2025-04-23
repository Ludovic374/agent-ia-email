from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import os
import pickle

SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']
CREDENTIALS_FILE = 'credentials.json'
TOKEN_FOLDER = "tokens"  # Dossier où stocker les tokens

def authenticate_user():
    # Créer le dossier tokens s'il n'existe pas
    os.makedirs(TOKEN_FOLDER, exist_ok=True)

    # Lancer le flow OAuth
    flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
    creds = flow.run_local_server(port=0)

    # Récupérer l'adresse e-mail
    service = build('gmail', 'v1', credentials=creds)
    profile = service.users().getProfile(userId='me').execute()
    user_email = profile['emailAddress']

    # Chemin complet vers le fichier token
    token_path = os.path.join(TOKEN_FOLDER, f'token_{user_email}.pickle')
    with open(token_path, 'wb') as token:
        pickle.dump(creds, token)

    print(f"✅ Utilisateur connecté : {user_email}")
    print(f"🔐 Token enregistré dans : {token_path}")
    return user_email

if __name__ == "__main__":
    authenticate_user()

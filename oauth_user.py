from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import os
import pickle

SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']
CREDENTIALS_FILE = 'credentials.json'

def authenticate_user():
    flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
    creds = flow.run_local_server(port=0)

    # Obtenir l'adresse e-mail de l'utilisateur
    service = build('gmail', 'v1', credentials=creds)
    profile = service.users().getProfile(userId='me').execute()
    user_email = profile['emailAddress']

    # Enregistrer le token sous forme de token_<email>.pickle
    token_file = f'token_{user_email}.pickle'
    with open(token_file, 'wb') as token:
        pickle.dump(creds, token)

    print(f"✅ Utilisateur connecté : {user_email}")
    return user_email

if __name__ == "__main__":
    authenticate_user()

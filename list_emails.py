from googleapiclient.discovery import build
from google.oauth2 import service_account

# Vérifie que le fichier credentials.json est bien dans ton projet
SERVICE_ACCOUNT_FILE = 'credentials.json'
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

def get_gmail_service():
    """Initialise le service Gmail API."""
    try:
        creds = service_account.Credentials.from_service_account_file(
            SERVICE_ACCOUNT_FILE, scopes=SCOPES
        )
        service = build('gmail', 'v1', credentials=creds)
        return service
    except Exception as e:
        print(f"❌ Erreur lors de l'authentification : {e}")
        return None

def list_emails():
    """Récupère et affiche les 10 derniers e-mails."""
    service = get_gmail_service()
    if not service:
        return

    try:
        results = service.users().messages().list(userId='me', maxResults=10).execute()
        messages = results.get('messages', [])

        if not messages:
            print("📭 Aucun e-mail trouvé.")
        else:
            for message in messages:
                msg = service.users().messages().get(userId='me', id=message['id']).execute()
                print(f"📬 Sujet: {msg.get('snippet', 'Sans sujet')}")
    except Exception as e:
        print(f"❌ Erreur lors de la récupération des e-mails : {e}")

if __name__ == "__main__":
    list_emails()
